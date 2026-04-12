#!/usr/bin/env python3
"""Check the user-facing info-level log contract for AggregateGenCodeDesc examples."""

from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify begin, per-line, and summary info-level log messages for a UserExamplesNG run.",
    )
    parser.add_argument("--logFile", required=True, help="Path to the stderr log captured from --logLevel info.")
    parser.add_argument(
        "--mode",
        choices=["live", "algorithm-b"],
        required=True,
        help="Use 'live' for Algorithm A/C style logs and 'algorithm-b' for Algorithm B replay logs.",
    )
    parser.add_argument(
        "--scope",
        choices=["A", "B", "C", "D"],
        default="A",
        help="Scope used by the example. Scope C expects Doc summary fields; other scopes expect Code summary fields.",
    )
    parser.add_argument("--label", default="UserExample", help="Short label to print in the success message.")
    return parser.parse_args()


def require_fragments(log_text: str, fragments: list[str], label: str) -> None:
    missing = [fragment for fragment in fragments if fragment not in log_text]
    if missing:
        missing_display = ", ".join(missing)
        raise SystemExit(f"{label}: missing required log fragments: {missing_display}")


def require_live_line_contract(log_text: str, label: str) -> None:
    live_lines = [line for line in log_text.splitlines() if "LiveLine " in line]
    if not live_lines:
        raise SystemExit(f"{label}: missing LiveLine per-line log entries")
    malformed = [line for line in live_lines if "classification=" not in line]
    if malformed:
        raise SystemExit(f"{label}: found LiveLine entries without classification=: {malformed[0]}")


def summary_fragments(mode: str, scope: str) -> list[str]:
    if scope == "C":
        total_key = "totalDocLines="
        full_key = "fullGeneratedDocLines="
        partial_key = "partialGeneratedDocLines="
    else:
        total_key = "totalCodeLines="
        full_key = "fullGeneratedCodeLines="
        partial_key = "partialGeneratedCodeLines="

    if mode == "algorithm-b":
        return ["Finished Algorithm B", total_key, full_key, partial_key, "elapsed=", "costSeconds="]
    return ["Finished analysis", total_key, full_key, partial_key, "elapsed=", "costSeconds="]


def start_fragments(mode: str) -> list[str]:
    if mode == "algorithm-b":
        return ["[INFO]", "Starting Algorithm B", "repo=", "branch=", "window=", "patchCount="]
    return ["[INFO]", "Starting analysis", "repo=", "branch=", "window=", "endRevision="]


def main() -> int:
    args = parse_args()
    log_text = Path(args.logFile).read_text(encoding="utf-8")

    require_fragments(log_text, start_fragments(args.mode), args.label)
    require_live_line_contract(log_text, args.label)
    require_fragments(log_text, summary_fragments(args.mode, args.scope), args.label)

    print(f"{args.label} info-log OK: begin + line-by-line + summary messages are present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())