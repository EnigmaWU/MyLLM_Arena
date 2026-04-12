#!/usr/bin/env python3
"""Render human-readable commit diff views with inline genRatio hints.

This keeps commitDiffSet/ patches executable while producing a sidecar view for
operators who want to inspect added lines together with their matching
genCodeDesc annotations.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


_COMMIT_DIFF_FILE_RE = re.compile(r"^(?:(?P<time_seq>\d+)_)?(?P<revision_id>.+)_commitDiff\.patch$")
_HUNK_HEADER_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render a human-readable commitDiffSetAnnotated/ sidecar from commitDiffSet + genCodeDescSet.",
    )
    parser.add_argument(
        "datasetDir",
        help="Dataset directory containing commitDiffSet/ and one or more *_genCodeDesc.json protocol directories.",
    )
    parser.add_argument(
        "--outputDir",
        help="Optional output directory. Defaults to <datasetDir>/commitDiffSetAnnotated.",
    )
    return parser.parse_args()


def parse_revision_id_from_patch_name(file_name: str) -> str | None:
    match = _COMMIT_DIFF_FILE_RE.match(file_name)
    if match is None:
        return None
    return match.group("revision_id")


def _annotation_label(line_entry: dict) -> str | None:
    ratio = line_entry.get("genRatio")
    if not isinstance(ratio, int):
        return None

    label = f"genRatio={ratio}"
    method = line_entry.get("genMethod")
    if isinstance(method, str) and method:
        label += f", genMethod={method}"
    return label


def _record_line_annotation(file_annotations: dict[str, dict[int, str]], file_name: str, line_no: int, label: str) -> None:
    file_annotations.setdefault(file_name, {})[line_no] = label


def build_revision_annotations(protocol_dir: Path) -> dict[str, dict[str, dict[int, str]]]:
    revision_annotations: dict[str, dict[str, dict[int, str]]] = {}

    for protocol_path in sorted(protocol_dir.glob("*_genCodeDesc.json")):
        document = json.loads(protocol_path.read_text(encoding="utf-8"))
        repository = document.get("REPOSITORY", {})
        revision_id = repository.get("revisionId")
        if not isinstance(revision_id, str) or not revision_id:
            continue

        file_annotations: dict[str, dict[int, str]] = revision_annotations.setdefault(revision_id, {})
        for detail in document.get("DETAIL", []):
            if not isinstance(detail, dict):
                continue
            file_name = detail.get("fileName")
            if not isinstance(file_name, str) or not file_name:
                continue

            for key in ("codeLines", "docLines"):
                line_entries = detail.get(key)
                if not isinstance(line_entries, list):
                    continue
                for line_entry in line_entries:
                    if not isinstance(line_entry, dict):
                        continue
                    label = _annotation_label(line_entry)
                    if label is None:
                        continue

                    line_location = line_entry.get("lineLocation")
                    if isinstance(line_location, int):
                        _record_line_annotation(file_annotations, file_name, line_location, label)
                        continue

                    line_range = line_entry.get("lineRange")
                    if not isinstance(line_range, dict):
                        continue
                    range_start = line_range.get("from")
                    range_end = line_range.get("to")
                    if not isinstance(range_start, int) or not isinstance(range_end, int):
                        continue
                    for line_no in range(range_start, range_end + 1):
                        _record_line_annotation(file_annotations, file_name, line_no, label)

    return revision_annotations


def find_protocol_dirs(dataset_dir: Path) -> list[Path]:
    protocol_dirs = []
    for dir_name in ("genCodeDescSet", "algcGenCodeDescSet"):
        protocol_dir = dataset_dir / dir_name
        if protocol_dir.is_dir():
            protocol_dirs.append(protocol_dir)
    return protocol_dirs


def load_dataset_annotations(dataset_dir: Path) -> dict[str, dict[str, dict[int, str]]]:
    revision_annotations: dict[str, dict[str, dict[int, str]]] = {}
    for protocol_dir in find_protocol_dirs(dataset_dir):
        for revision_id, file_annotations in build_revision_annotations(protocol_dir).items():
            revision_annotations.setdefault(revision_id, {}).update(file_annotations)
    return revision_annotations


def annotate_patch_text(patch_text: str, file_annotations: dict[str, dict[int, str]]) -> str:
    annotated_lines: list[str] = []
    current_old_path = ""
    current_new_path = ""
    old_line_cursor: int | None = None
    new_line_cursor: int | None = None

    for raw_line in patch_text.splitlines():
        if raw_line.startswith("diff --git "):
            header_parts = raw_line.split()
            current_old_path = header_parts[2].removeprefix("a/") if len(header_parts) >= 3 else ""
            current_new_path = header_parts[3].removeprefix("b/") if len(header_parts) >= 4 else ""
            old_line_cursor = None
            new_line_cursor = None
            annotated_lines.append(raw_line)
            continue

        if raw_line.startswith("--- "):
            current_old_path = raw_line.removeprefix("--- ").removeprefix("a/")
            annotated_lines.append(raw_line)
            continue

        if raw_line.startswith("+++ "):
            current_new_path = raw_line.removeprefix("+++ ").removeprefix("b/")
            annotated_lines.append(raw_line)
            continue

        if raw_line.startswith("rename from "):
            current_old_path = raw_line.removeprefix("rename from ")
            annotated_lines.append(raw_line)
            continue

        if raw_line.startswith("rename to "):
            current_new_path = raw_line.removeprefix("rename to ")
            annotated_lines.append(raw_line)
            continue

        if raw_line.startswith("@@ "):
            hunk_match = _HUNK_HEADER_RE.match(raw_line)
            if hunk_match is not None:
                old_line_cursor = int(hunk_match.group(1))
                new_line_cursor = int(hunk_match.group(3))
            annotated_lines.append(raw_line)
            continue

        if raw_line.startswith("\\ No newline at end of file"):
            annotated_lines.append(raw_line)
            continue

        if raw_line.startswith("+") and not raw_line.startswith("+++") and new_line_cursor is not None:
            annotation = file_annotations.get(current_new_path, {}).get(new_line_cursor)
            if annotation is not None:
                annotated_lines.append(f"{raw_line}  # {annotation}")
            else:
                annotated_lines.append(raw_line)
            new_line_cursor += 1
            continue

        if raw_line.startswith("-") and not raw_line.startswith("---") and old_line_cursor is not None:
            annotated_lines.append(raw_line)
            old_line_cursor += 1
            continue

        if raw_line.startswith(" ") and old_line_cursor is not None and new_line_cursor is not None:
            annotated_lines.append(raw_line)
            old_line_cursor += 1
            new_line_cursor += 1
            continue

        annotated_lines.append(raw_line)

    return "\n".join(annotated_lines) + ("\n" if patch_text.endswith("\n") or annotated_lines else "")


def render_annotated_commit_diff_set(dataset_dir: Path, output_dir: Path) -> int:
    commit_diff_dir = dataset_dir / "commitDiffSet"
    if not commit_diff_dir.is_dir():
        raise FileNotFoundError(f"commitDiffSet directory not found under {dataset_dir}")

    revision_annotations = load_dataset_annotations(dataset_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    rendered_count = 0
    for patch_path in sorted(commit_diff_dir.glob("*_commitDiff.patch")):
        revision_id = parse_revision_id_from_patch_name(patch_path.name)
        patch_text = patch_path.read_text(encoding="utf-8")
        annotated_text = annotate_patch_text(patch_text, revision_annotations.get(revision_id or "", {}))
        (output_dir / patch_path.name).write_text(annotated_text, encoding="utf-8")
        rendered_count += 1

    return rendered_count


def main() -> int:
    args = parse_args()
    dataset_dir = Path(args.datasetDir).resolve()
    output_dir = Path(args.outputDir).resolve() if args.outputDir else dataset_dir / "commitDiffSetAnnotated"
    rendered_count = render_annotated_commit_diff_set(dataset_dir, output_dir)
    print(f"Rendered {rendered_count} annotated patch files to {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())