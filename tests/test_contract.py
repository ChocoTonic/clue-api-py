from __future__ import annotations

import json
import tomllib
from pathlib import Path

from openapi_spec_validator import validate

from clue_api import READ_ENDPOINTS, __version__, build_openapi


def test_openapi_is_valid_and_generated_file_is_current() -> None:
    contract = build_openapi()
    validate(contract)
    generated = json.loads(Path("docs/openapi.json").read_text())
    assert generated == contract


def test_contract_operations_are_unique_and_read_only() -> None:
    operation_ids = [endpoint.operation_id for endpoint in READ_ENDPOINTS]
    assert len(operation_ids) == len(set(operation_ids))
    contract = build_openapi()
    assert all(
        set(path_item) == {"get"} for path_item in contract["paths"].values() if "get" in path_item
    )


def test_every_endpoint_records_evidence() -> None:
    assert {endpoint.evidence for endpoint in READ_ENDPOINTS} == {
        "live",
        "state-dependent",
        "apk-only",
    }


def test_package_and_contract_versions_match() -> None:
    project = tomllib.loads(Path("pyproject.toml").read_text())
    assert project["project"]["version"] == __version__
    assert build_openapi()["info"]["version"] == __version__
