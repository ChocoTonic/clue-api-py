"""Minimal command-line interface for read-only Clue API queries."""

from __future__ import annotations

import argparse
import getpass
import json
import os
from collections.abc import Sequence
from typing import Any

from .client import ClueClient
from .contracts import build_openapi


def parser() -> argparse.ArgumentParser:
    command_parser = argparse.ArgumentParser(prog="clue-api")
    command_parser.add_argument(
        "--token",
        default=os.environ.get("CLUE_ACCESS_TOKEN"),
        help="access token; prefer the CLUE_ACCESS_TOKEN environment variable",
    )
    command_parser.add_argument(
        "--email",
        default=os.environ.get("CLUE_EMAIL"),
        help="Clue email; prompts securely for the password when no token is supplied",
    )
    command_parser.add_argument(
        "--time-zone",
        default=os.environ.get("CLUE_TIME_ZONE"),
        help="IANA time zone, for example America/Los_Angeles",
    )
    subcommands = command_parser.add_subparsers(dest="command", required=True)
    subcommands.add_parser("spec")
    subcommands.add_parser("initialize")
    subcommands.add_parser("current-cycle")
    history = subcommands.add_parser("history")
    history.add_argument("--limit", type=int, default=20)
    history.add_argument("--cursor")
    measurements = subcommands.add_parser("measurements")
    measurements.add_argument("--start", required=True)
    measurements.add_argument("--end", required=True)
    measurements.add_argument("--type", dest="measurement_type")
    return command_parser


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.command == "spec":
        print(json.dumps(build_openapi(), indent=2, sort_keys=True))
        return 0
    if args.token:
        client = ClueClient(args.token, time_zone=args.time_zone)
    elif args.email:
        client = ClueClient.from_credentials(
            args.email,
            getpass.getpass("Clue password: "),
            time_zone=args.time_zone,
        )
    else:
        raise SystemExit("Set CLUE_ACCESS_TOKEN or CLUE_EMAIL")
    with client:
        result: dict[str, Any]
        if args.command == "initialize":
            result = client.initialize()
        elif args.command == "current-cycle":
            result = client.current_cycle()
        elif args.command == "history":
            result = client.cycle_history(limit=args.limit, cursor=args.cursor)
        else:
            result = client.measurements(
                start=args.start,
                end=args.end,
                measurement_type=args.measurement_type,
            )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
