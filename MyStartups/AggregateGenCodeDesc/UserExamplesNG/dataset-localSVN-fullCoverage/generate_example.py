#!/usr/bin/env python3

import argparse
import difflib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


USER_EXAMPLES_NG_DIR = Path(__file__).resolve().parents[1]
if str(USER_EXAMPLES_NG_DIR) not in sys.path:
    sys.path.insert(0, str(USER_EXAMPLES_NG_DIR))

from render_annotated_commit_diff_set import render_annotated_commit_diff_set


START_TIME = "2026-03-01"
END_TIME = "2026-03-31"
TRUNK_CREATED_TIMESTAMP = "2026-02-28T09:00:00Z"
REVISION_TIMESTAMPS = [
    "2026-03-01T09:00:00Z",
    "2026-03-05T09:00:00Z",
    "2026-03-10T09:00:00Z",
    "2026-03-15T09:00:00Z",
    "2026-03-20T09:00:00Z",
]


class GenerationError(RuntimeError):
    pass


def run_command(args: list[str], cwd: Path | None = None, env: dict[str, str] | None = None) -> str:
    completed = subprocess.run(
        args,
        cwd=cwd,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise GenerationError(f"Command failed: {' '.join(args)}\n{completed.stderr.strip()}")
    return completed.stdout.strip()


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def prepare_output_dir(output_dir: Path, force: bool) -> None:
    if output_dir.exists():
        if not force:
            raise GenerationError(f"Output directory already exists: {output_dir}. Use --force to replace it.")
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)


def summary_fields(scope: str) -> dict:
    if scope == "A":
        return {"totalCodeLines": 2, "fullGeneratedCodeLines": 1, "partialGeneratedCodeLines": 1}
    if scope == "B":
        return {"totalCodeLines": 4, "fullGeneratedCodeLines": 2, "partialGeneratedCodeLines": 1}
    if scope == "C":
        return {"totalDocLines": 3, "fullGeneratedDocLines": 1, "partialGeneratedDocLines": 1}
    if scope == "D":
        return {"totalCodeLines": 7, "fullGeneratedCodeLines": 3, "partialGeneratedCodeLines": 2}
    raise GenerationError(f"Unsupported scope: {scope}")


def snapshot_source(revision_id: str) -> str:
    snapshots = {
        "r1": "legacy = 0\n",
        "r2": "# intro comment\nlegacy = 0\n",
        "r3": "# intro comment\nvalue = 1\n",
        "r4": "# intro comment\nvalue = 1\nprint(value)\n",
        "r5": "# intro comment\nvalue = 1\nprint(value)\n# generated note\n",
    }
    return snapshots[revision_id]


def snapshot_doc(revision_id: str) -> str:
    snapshots = {
        "r1": "Legacy guide\n",
        "r2": "User guide intro\n",
        "r3": "User guide intro\n",
        "r4": "User guide intro\nAI summary\n",
        "r5": "User guide intro\nAI summary\nHybrid note\n",
    }
    return snapshots[revision_id]


def code_lines_for_revision(revision_id: str) -> list[dict]:
    rows = {
        "r1": [{"lineLocation": 1, "genRatio": 0, "genMethod": "Manual"}],
        "r2": [
            {"lineLocation": 1, "genRatio": 0, "genMethod": "Manual"},
            {"lineLocation": 2, "genRatio": 0, "genMethod": "Manual"},
        ],
        "r3": [
            {"lineLocation": 1, "genRatio": 0, "genMethod": "Manual"},
            {"lineLocation": 2, "genRatio": 100, "genMethod": "codeCompletion"},
        ],
        "r4": [
            {"lineLocation": 1, "genRatio": 0, "genMethod": "Manual"},
            {"lineLocation": 2, "genRatio": 100, "genMethod": "codeCompletion"},
            {"lineLocation": 3, "genRatio": 50, "genMethod": "vibeCoding"},
        ],
        "r5": [
            {"lineLocation": 1, "genRatio": 0, "genMethod": "Manual"},
            {"lineLocation": 2, "genRatio": 100, "genMethod": "codeCompletion"},
            {"lineLocation": 3, "genRatio": 50, "genMethod": "vibeCoding"},
            {"lineLocation": 4, "genRatio": 100, "genMethod": "vibeCoding"},
        ],
    }
    return rows[revision_id]


def doc_lines_for_revision(revision_id: str) -> list[dict]:
    rows = {
        "r1": [{"lineLocation": 1, "genRatio": 0, "genMethod": "Manual"}],
        "r2": [{"lineLocation": 1, "genRatio": 0, "genMethod": "Manual"}],
        "r3": [{"lineLocation": 1, "genRatio": 0, "genMethod": "Manual"}],
        "r4": [
            {"lineLocation": 1, "genRatio": 0, "genMethod": "Manual"},
            {"lineLocation": 2, "genRatio": 100, "genMethod": "vibeCoding"},
        ],
        "r5": [
            {"lineLocation": 1, "genRatio": 0, "genMethod": "Manual"},
            {"lineLocation": 2, "genRatio": 100, "genMethod": "vibeCoding"},
            {"lineLocation": 3, "genRatio": 50, "genMethod": "codeCompletion"},
        ],
    }
    return rows[revision_id]


def v2603_summary_for_revision(revision_id: str) -> dict:
    summary_by_revision = {
        "r1": {"totalCodeLines": 1, "fullGeneratedCodeLines": 0, "partialGeneratedCodeLines": 0, "totalDocLines": 1, "fullGeneratedDocLines": 0, "partialGeneratedDocLines": 0},
        "r2": {"totalCodeLines": 1, "fullGeneratedCodeLines": 0, "partialGeneratedCodeLines": 0, "totalDocLines": 1, "fullGeneratedDocLines": 0, "partialGeneratedDocLines": 0},
        "r3": {"totalCodeLines": 1, "fullGeneratedCodeLines": 1, "partialGeneratedCodeLines": 0, "totalDocLines": 0, "fullGeneratedDocLines": 0, "partialGeneratedDocLines": 0},
        "r4": {"totalCodeLines": 1, "fullGeneratedCodeLines": 0, "partialGeneratedCodeLines": 1, "totalDocLines": 1, "fullGeneratedDocLines": 1, "partialGeneratedDocLines": 0},
        "r5": {"totalCodeLines": 1, "fullGeneratedCodeLines": 1, "partialGeneratedCodeLines": 0, "totalDocLines": 1, "fullGeneratedDocLines": 0, "partialGeneratedDocLines": 1},
    }
    return summary_by_revision[revision_id]


def v2603_detail_for_revision(revision_id: str) -> list[dict]:
    detail_by_revision = {
        "r1": [],
        "r2": [],
        "r3": [{"fileName": "trunk/src/app.py", "codeLines": [{"lineLocation": 2, "genRatio": 100, "genMethod": "codeCompletion"}]}],
        "r4": [
            {"fileName": "trunk/src/app.py", "codeLines": [{"lineLocation": 3, "genRatio": 50, "genMethod": "vibeCoding"}]},
            {"fileName": "trunk/docs/guide.md", "docLines": [{"lineLocation": 2, "genRatio": 100, "genMethod": "vibeCoding"}]},
        ],
        "r5": [
            {"fileName": "trunk/src/app.py", "codeLines": [{"lineLocation": 4, "genRatio": 100, "genMethod": "vibeCoding"}]},
            {"fileName": "trunk/docs/guide.md", "docLines": [{"lineLocation": 3, "genRatio": 50, "genMethod": "codeCompletion"}]},
        ],
    }
    return detail_by_revision[revision_id]


def build_v2603_protocol(repo_url: str, revision_label: str, revision_id: str) -> dict:
    revision_index = int(revision_label.removeprefix("r")) - 1
    return {
        "protocolName": "generatedTextDesc",
        "protocolVersion": "26.03",
        "codeAgent": "UserExampleMatrixAgent",
        "SUMMARY": v2603_summary_for_revision(revision_label),
        "DETAIL": v2603_detail_for_revision(revision_label),
        "REPOSITORY": {
            "vcsType": "svn",
            "repoURL": repo_url,
            "repoBranch": "trunk",
            "revisionId": revision_id,
            "revisionTimestamp": REVISION_TIMESTAMPS[revision_index],
        },
    }


def build_v2604_protocol(repo_url: str, revision_label: str, revision_id: str, revision_ids_by_label: dict[str, str]) -> dict:
    revision_index = int(revision_label.removeprefix("r")) - 1
    detail_entries_by_revision = {
        "r1": [
            {
                "fileName": "trunk/src/app.py",
                "codeLines": [
                    {
                        "changeType": "add",
                        "lineLocation": 1,
                        "genRatio": 0,
                        "genMethod": "Manual",
                        "blame": {
                            "revisionId": revision_ids_by_label["r1"],
                            "originalFilePath": "trunk/src/app.py",
                            "originalLine": 1,
                            "timestamp": REVISION_TIMESTAMPS[0],
                        },
                    }
                ],
            },
            {
                "fileName": "trunk/docs/guide.md",
                "docLines": [
                    {
                        "changeType": "add",
                        "lineLocation": 1,
                        "genRatio": 0,
                        "genMethod": "Manual",
                        "blame": {
                            "revisionId": revision_ids_by_label["r1"],
                            "originalFilePath": "trunk/docs/guide.md",
                            "originalLine": 1,
                            "timestamp": REVISION_TIMESTAMPS[0],
                        },
                    }
                ],
            },
        ],
        "r2": [
            {
                "fileName": "trunk/src/app.py",
                "codeLines": [
                    {
                        "changeType": "delete",
                        "blame": {"revisionId": revision_ids_by_label["r1"], "originalFilePath": "trunk/src/app.py", "originalLine": 1},
                    },
                    {
                        "changeType": "add",
                        "lineLocation": 1,
                        "genRatio": 0,
                        "genMethod": "Manual",
                        "blame": {
                            "revisionId": revision_ids_by_label["r2"],
                            "originalFilePath": "trunk/src/app.py",
                            "originalLine": 1,
                            "timestamp": REVISION_TIMESTAMPS[1],
                        },
                    },
                    {
                        "changeType": "add",
                        "lineLocation": 2,
                        "genRatio": 0,
                        "genMethod": "Manual",
                        "blame": {
                            "revisionId": revision_ids_by_label["r2"],
                            "originalFilePath": "trunk/src/app.py",
                            "originalLine": 2,
                            "timestamp": REVISION_TIMESTAMPS[1],
                        },
                    },
                ],
            },
            {
                "fileName": "trunk/docs/guide.md",
                "docLines": [
                    {
                        "changeType": "delete",
                        "blame": {"revisionId": revision_ids_by_label["r1"], "originalFilePath": "trunk/docs/guide.md", "originalLine": 1},
                    },
                    {
                        "changeType": "add",
                        "lineLocation": 1,
                        "genRatio": 0,
                        "genMethod": "Manual",
                        "blame": {
                            "revisionId": revision_ids_by_label["r2"],
                            "originalFilePath": "trunk/docs/guide.md",
                            "originalLine": 1,
                            "timestamp": REVISION_TIMESTAMPS[1],
                        },
                    },
                ],
            },
        ],
        "r3": [
            {
                "fileName": "trunk/src/app.py",
                "codeLines": [
                    {
                        "changeType": "delete",
                        "blame": {"revisionId": revision_ids_by_label["r2"], "originalFilePath": "trunk/src/app.py", "originalLine": 2},
                    },
                    {
                        "changeType": "add",
                        "lineLocation": 2,
                        "genRatio": 100,
                        "genMethod": "codeCompletion",
                        "blame": {
                            "revisionId": revision_ids_by_label["r3"],
                            "originalFilePath": "trunk/src/app.py",
                            "originalLine": 2,
                            "timestamp": REVISION_TIMESTAMPS[2],
                        },
                    },
                ],
            },
            {
                "fileName": "trunk/docs/guide.md",
                "docLines": [],
            },
        ],
        "r4": [
            {
                "fileName": "trunk/src/app.py",
                "codeLines": [
                    {
                        "changeType": "add",
                        "lineLocation": 3,
                        "genRatio": 50,
                        "genMethod": "vibeCoding",
                        "blame": {
                            "revisionId": revision_ids_by_label["r4"],
                            "originalFilePath": "trunk/src/app.py",
                            "originalLine": 3,
                            "timestamp": REVISION_TIMESTAMPS[3],
                        },
                    }
                ],
            },
            {
                "fileName": "trunk/docs/guide.md",
                "docLines": [
                    {
                        "changeType": "add",
                        "lineLocation": 2,
                        "genRatio": 100,
                        "genMethod": "vibeCoding",
                        "blame": {
                            "revisionId": revision_ids_by_label["r4"],
                            "originalFilePath": "trunk/docs/guide.md",
                            "originalLine": 2,
                            "timestamp": REVISION_TIMESTAMPS[3],
                        },
                    }
                ],
            },
        ],
        "r5": [
            {
                "fileName": "trunk/src/app.py",
                "codeLines": [
                    {
                        "changeType": "add",
                        "lineLocation": 4,
                        "genRatio": 100,
                        "genMethod": "vibeCoding",
                        "blame": {
                            "revisionId": revision_ids_by_label["r5"],
                            "originalFilePath": "trunk/src/app.py",
                            "originalLine": 4,
                            "timestamp": REVISION_TIMESTAMPS[4],
                        },
                    }
                ],
            },
            {
                "fileName": "trunk/docs/guide.md",
                "docLines": [
                    {
                        "changeType": "add",
                        "lineLocation": 3,
                        "genRatio": 50,
                        "genMethod": "codeCompletion",
                        "blame": {
                            "revisionId": revision_ids_by_label["r5"],
                            "originalFilePath": "trunk/docs/guide.md",
                            "originalLine": 3,
                            "timestamp": REVISION_TIMESTAMPS[4],
                        },
                    }
                ],
            },
        ],
    }

    summary_by_revision = {
        "r1": {"totalCodeLines": 1, "fullGeneratedCodeLines": 0, "partialGeneratedCodeLines": 0, "totalDocLines": 1, "fullGeneratedDocLines": 0, "partialGeneratedDocLines": 0},
        "r2": {"totalCodeLines": 1, "fullGeneratedCodeLines": 0, "partialGeneratedCodeLines": 0, "totalDocLines": 0, "fullGeneratedDocLines": 0, "partialGeneratedDocLines": 0},
        "r3": {"totalCodeLines": 1, "fullGeneratedCodeLines": 1, "partialGeneratedCodeLines": 0, "totalDocLines": 0, "fullGeneratedDocLines": 0, "partialGeneratedDocLines": 0},
        "r4": {"totalCodeLines": 1, "fullGeneratedCodeLines": 0, "partialGeneratedCodeLines": 1, "totalDocLines": 1, "fullGeneratedDocLines": 1, "partialGeneratedDocLines": 0},
        "r5": {"totalCodeLines": 1, "fullGeneratedCodeLines": 1, "partialGeneratedCodeLines": 0, "totalDocLines": 1, "fullGeneratedDocLines": 0, "partialGeneratedDocLines": 1},
    }

    return {
        "protocolName": "generatedTextDesc",
        "protocolVersion": "26.04",
        "codeAgent": "UserExampleMatrixAgent",
        "SUMMARY": summary_by_revision[revision_label],
        "DETAIL": detail_entries_by_revision[revision_label],
        "REPOSITORY": {
            "vcsType": "svn",
            "repoURL": repo_url,
            "repoBranch": "trunk",
            "revisionId": revision_id,
            "revisionTimestamp": REVISION_TIMESTAMPS[revision_index],
        },
    }


def build_expected_output(repo_url: str, scope: str, end_revision_id: str, protocol_version: str) -> dict:
    return {
        "protocolName": "generatedTextDesc",
        "protocolVersion": protocol_version,
        "SUMMARY": summary_fields(scope),
        "REPOSITORY": {
            "vcsType": "svn",
            "repoURL": repo_url,
            "repoBranch": "trunk",
            "revisionId": end_revision_id,
        },
    }


def svn_timestamp(value: str) -> str:
    return value.removesuffix("Z") + ".000000Z"


def set_revision_date(repo_url: str, revision_id: str, timestamp: str) -> None:
    run_command(["svn", "propset", "--revprop", "-r", revision_id, "svn:date", svn_timestamp(timestamp), repo_url])


def parse_committed_revision(output: str) -> str:
    match = re.search(r"Committed revision (\d+)\.", output)
    if match is None:
        raise GenerationError(f"Unable to parse committed revision from output: {output}")
    return match.group(1)


def build_snapshot_map(revision_label: str) -> dict[str, str]:
    return {
        "trunk/src/app.py": snapshot_source(revision_label),
        "trunk/docs/guide.md": snapshot_doc(revision_label),
    }


def build_patch_text(previous_snapshot: dict[str, str], current_snapshot: dict[str, str]) -> str:
    parts: list[str] = []
    for path in sorted(set(previous_snapshot) | set(current_snapshot)):
        old_text = previous_snapshot.get(path)
        new_text = current_snapshot.get(path)
        if old_text == new_text:
            continue
        old_lines = [] if old_text is None else old_text.splitlines()
        new_lines = [] if new_text is None else new_text.splitlines()
        fromfile = f"a/{path}" if old_text is not None else "/dev/null"
        tofile = f"b/{path}" if new_text is not None else "/dev/null"
        diff_lines = list(difflib.unified_diff(old_lines, new_lines, fromfile=fromfile, tofile=tofile, lineterm=""))
        parts.append(f"diff --git a/{path} b/{path}")
        parts.extend(diff_lines)
    return "\n".join(parts) + ("\n" if parts else "")


def create_svn_repo(repo_dir: Path, working_copy_dir: Path, metadata_dir: Path, algc_dir: Path, commit_diff_dir: Path) -> tuple[str, dict[str, str]]:
    repo_dir.mkdir(parents=True, exist_ok=True)
    run_command(["svnadmin", "create", str(repo_dir)])

    hook_path = repo_dir / "hooks" / "pre-revprop-change"
    hook_path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    hook_path.chmod(0o755)

    repo_url = repo_dir.resolve().as_uri()
    run_command(["svn", "mkdir", f"{repo_url}/trunk", "-m", "create trunk"])
    set_revision_date(repo_url, "1", TRUNK_CREATED_TIMESTAMP)

    run_command(["svn", "checkout", f"{repo_url}/trunk", str(working_copy_dir)])

    previous_snapshot: dict[str, str] = {}
    revision_ids_by_label: dict[str, str] = {}
    for index, revision_label in enumerate(["r1", "r2", "r3", "r4", "r5"]):
        (working_copy_dir / "src").mkdir(parents=True, exist_ok=True)
        (working_copy_dir / "docs").mkdir(parents=True, exist_ok=True)
        (working_copy_dir / "src" / "app.py").write_text(snapshot_source(revision_label), encoding="utf-8")
        (working_copy_dir / "docs" / "guide.md").write_text(snapshot_doc(revision_label), encoding="utf-8")

        if revision_label == "r1":
            run_command(["svn", "add", "--force", "src", "docs"], cwd=working_copy_dir)

        commit_output = run_command(["svn", "commit", "-m", revision_label], cwd=working_copy_dir)
        revision_id = parse_committed_revision(commit_output)
        set_revision_date(repo_url, revision_id, REVISION_TIMESTAMPS[index])
        revision_ids_by_label[revision_label] = revision_id

        current_snapshot = build_snapshot_map(revision_label)
        patch_text = build_patch_text(previous_snapshot, current_snapshot)
        (commit_diff_dir / f"{index + 1:04d}_{revision_id}_commitDiff.patch").write_text(patch_text, encoding="utf-8")
        previous_snapshot = current_snapshot

    for revision_label in ["r1", "r2", "r3", "r4", "r5"]:
        revision_id = revision_ids_by_label[revision_label]
        write_json(metadata_dir / f"{revision_id}_genCodeDesc.json", build_v2603_protocol(repo_url, revision_label, revision_id))
        write_json(algc_dir / f"{revision_id}_genCodeDesc.json", build_v2604_protocol(repo_url, revision_label, revision_id, revision_ids_by_label))

    return repo_url, revision_ids_by_label


def write_query_args(base_dir: Path, repo_url: str, end_revision_id: str) -> None:
    write_json(
        base_dir / "queryArgs.json",
        {
            "vcsType": "svn",
            "repoURL": repo_url,
            "repoBranch": "trunk",
            "endRevisionId": end_revision_id,
        },
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the SVN support-matrix coverage user example.")
    parser.add_argument("--outputDir", required=True)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    output_dir = Path(args.outputDir).resolve()
    prepare_output_dir(output_dir, args.force)

    repo_dir = output_dir / "svnrepo"
    working_copy_dir = output_dir / "workingCopy"
    metadata_dir = output_dir / "genCodeDescSet"
    algc_dir = output_dir / "algcGenCodeDescSet"
    commit_diff_dir = output_dir / "commitDiffSet"
    metadata_dir.mkdir(parents=True, exist_ok=True)
    algc_dir.mkdir(parents=True, exist_ok=True)
    commit_diff_dir.mkdir(parents=True, exist_ok=True)

    repo_url, revision_ids_by_label = create_svn_repo(repo_dir, working_copy_dir, metadata_dir, algc_dir, commit_diff_dir)
    end_revision_id = revision_ids_by_label["r5"]
    write_query_args(algc_dir, repo_url, end_revision_id)

    for scope in ["A", "B", "C", "D"]:
        write_json(output_dir / f"expected_alga_{scope}.json", build_expected_output(repo_url, scope, end_revision_id, "26.03"))
        write_json(output_dir / f"expected_algb-svn-workflow_{scope}.json", build_expected_output(repo_url, scope, end_revision_id, "26.03"))
        write_json(output_dir / f"expected_algb-offline_{scope}.json", build_expected_output(repo_url, scope, end_revision_id, "26.03"))
        write_json(output_dir / f"expected_algc_{scope}.json", build_expected_output(repo_url, scope, end_revision_id, "26.04"))

    render_annotated_commit_diff_set(output_dir, output_dir / "commitDiffSetAnnotated")

    write_json(
        output_dir / "manifest.json",
        {
            "scenario": "matrix02-svn-coverage",
            "covers": ["A|svn|A-D", "B local SVN workflow|svn|A-D", "B commit diff set|svn|A-D", "C svn-origin|A-D"],
            "startTime": START_TIME,
            "endTime": END_TIME,
            "endRevisionId": end_revision_id,
            "operatorRunMode": "Use explicit aggregateGenCodeDesc.py aggregate commands from UserExamplesNG/README_UserExamplesNG.md; this generator does not emit run/check shell wrappers.",
            "genRatioLocation": "Inspect genCodeDescSet/*.json or algcGenCodeDescSet/*.json for line attribution; if a patch carries a genRatio tail comment, treat it as a human-readable hint only, not aggregate input.",
            "repoURL": repo_url,
            "revisionIdsByLabel": revision_ids_by_label,
        },
    )
    print(f"Generated SVN matrix coverage example at {output_dir}")


if __name__ == "__main__":
    main()