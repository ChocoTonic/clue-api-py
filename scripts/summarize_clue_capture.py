#!/usr/bin/env python3
"""Print a metadata-only summary of Clue API flows from a mitmproxy capture."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlsplit

from mitmproxy import http, io

from clue_api.contracts import READ_ENDPOINTS

SAFE_PATH_SEGMENTS = {
    segment
    for endpoint in READ_ENDPOINTS
    for segment in endpoint.path.split("/")
    if segment and not segment.startswith("{")
} | {"access-tokens"}


def sanitized_path(path: str) -> str:
    """Preserve known route words while redacting every dynamic segment."""
    segments = path.strip("/").split("/")
    sanitized = "/".join(
        segment if segment in SAFE_PATH_SEGMENTS else "<redacted>" for segment in segments
    )
    return f"/{sanitized}" if path.startswith("/") else sanitized


def json_shape(value: Any) -> str:
    """Describe JSON structure without printing values."""
    if isinstance(value, dict):
        return "object{" + ", ".join(sorted(map(str, value.keys()))) + "}"
    if isinstance(value, list):
        item_kinds = sorted({type(item).__name__ for item in value})
        return f"array(len={len(value)}, item_types={','.join(item_kinds) or 'empty'})"
    return type(value).__name__


def content_shape(message: http.Message | None) -> str:
    if message is None or not message.raw_content:
        return "empty"
    content_type = message.headers.get("content-type", "").split(";", 1)[0]
    if content_type == "application/json" or content_type.endswith("+json"):
        try:
            return "json:" + json_shape(json.loads(message.content))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return "invalid-json"
    return f"{content_type or 'unknown'} ({len(message.raw_content)} bytes)"


def authorization_scheme(request: http.Request) -> str:
    authorization = request.headers.get("authorization")
    if not authorization:
        return "none"
    return authorization.partition(" ")[0] or "present-without-scheme"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("capture", type=Path)
    parser.add_argument("--host", default="api.helloclue.com")
    args = parser.parse_args()

    with args.capture.open("rb") as capture_file:
        for flow in io.FlowReader(capture_file).stream():
            if not isinstance(flow, http.HTTPFlow) or flow.request.host != args.host:
                continue
            url = urlsplit(flow.request.pretty_url)
            query_keys = sorted({key for key, _ in parse_qsl(url.query, keep_blank_values=True)})
            status = flow.response.status_code if flow.response else "no-response"
            safe_path = sanitized_path(url.path)
            print(f"{flow.request.method} {safe_path} -> {status}")
            print(f"  query keys: {', '.join(query_keys) or 'none'}")
            print(f"  auth scheme: {authorization_scheme(flow.request)}")
            print(f"  request shape: {content_shape(flow.request)}")
            print(f"  response shape: {content_shape(flow.response)}")


if __name__ == "__main__":
    main()
