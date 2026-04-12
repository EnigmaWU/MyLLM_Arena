#!/usr/bin/env python3

import argparse
import json
import os
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
        "r3": [{"fileName": "src/app.py", "codeLines": [{"lineLocation": 2, "genRatio": 100, "genMethod": "codeCompletion"}]}],
        "r4": [
            {"fileName": "src/app.py", "codeLines": [{"lineLocation": 3, "genRatio": 50, "genMethod": "vibeCoding"}]},
            {"fileName": "docs/guide.md", "docLines": [{"lineLocation": 2, "genRatio": 100, "genMethod": "vibeCoding"}]},
        ],
        "r5": [
            {"fileName": "src/app.py", "codeLines": [{"lineLocation": 4, "genRatio": 100, "genMethod": "vibeCoding"}]},
            {"fileName": "docs/guide.md", "docLines": [{"lineLocation": 3, "genRatio": 50, "genMethod": "codeCompletion"}]},
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
            "vcsType": "git",
            "repoURL": repo_url,
            "repoBranch": "main",
            "revisionId": revision_id,
            "revisionTimestamp": REVISION_TIMESTAMPS[revision_index],
        },
    }


def build_v2604_protocol(repo_url: str, revision_label: str, revision_id: str, revision_ids_by_label: dict[str, str]) -> dict:
    revision_index = int(revision_label.removeprefix("r")) - 1
    detail_entries_by_revision = {
        "r1": [
            {
                "fileName": "src/app.py",
                "codeLines": [
                    {
                        "changeType": "add",
                        "lineLocation": 1,
                        "genRatio": 0,
                        "genMethod": "Manual",
                        "blame": {
                            "revisionId": revision_ids_by_label["r1"],
                            "originalFilePath": "src/app.py",
                            "originalLine": 1,
                            "timestamp": REVISION_TIMESTAMPS[0],
                        },
                    }
                ],
            },
            {
                "fileName": "docs/guide.md",
                "docLines": [
                    {
                        "changeType": "add",
                        "lineLocation": 1,
                        "genRatio": 0,
                        "genMethod": "Manual",
                        "blame": {
                            "revisionId": revision_ids_by_label["r1"],
                            "originalFilePath": "docs/guide.md",
                            "originalLine": 1,
                            "timestamp": REVISION_TIMESTAMPS[0],
                        },
                    }
                ],
            },
        ],
        "r2": [
            {
                "fileName": "src/app.py",
                "codeLines": [
                    {
                        "changeType": "delete",
                        "blame": {"revisionId": revision_ids_by_label["r1"], "originalFilePath": "src/app.py", "originalLine": 1},
                    },
                    {
                        "changeType": "add",
                        "lineLocation": 1,
                        "genRatio": 0,
                        "genMethod": "Manual",
                        "blame": {
                            "revisionId": revision_ids_by_label["r2"],
                            "originalFilePath": "src/app.py",
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
                            "originalFilePath": "src/app.py",
                            "originalLine": 2,
                            "timestamp": REVISION_TIMESTAMPS[1],
                        },
                    },
                ],
            },
            {
                "fileName": "docs/guide.md",
                "docLines": [
                    {
                        "changeType": "delete",
                        "blame": {"revisionId": revision_ids_by_label["r1"], "originalFilePath": "docs/guide.md", "originalLine": 1},
                    },
                    {
                        "changeType": "add",
                        "lineLocation": 1,
                        "genRatio": 0,
                        "genMethod": "Manual",
                        "blame": {
                            "revisionId": revision_ids_by_label["r2"],
                            "originalFilePath": "docs/guide.md",
                            "originalLine": 1,
                            "timestamp": REVISION_TIMESTAMPS[1],
                        },
                    },
                ],
            },
        ],
        "r3": [
            {
                "fileName": "src/app.py",
                "codeLines": [
                    {
                        "changeType": "delete",
                        "blame": {"revisionId": revision_ids_by_label["r2"], "originalFilePath": "src/app.py", "originalLine": 2},
                    },
                    {
                        "changeType": "add",
                        "lineLocation": 2,
                        "genRatio": 100,
                        "genMethod": "codeCompletion",
                        "blame": {
                            "revisionId": revision_ids_by_label["r3"],
                            "originalFilePath": "src/app.py",
                            "originalLine": 2,
                            "timestamp": REVISION_TIMESTAMPS[2],
                        },
                    },
                ],
            }
        ],
        "r4": [
            {
                "fileName": "src/app.py",
                "codeLines": [
                    {
                        "changeType": "add",
                        "lineLocation": 3,
                        "genRatio": 50,
                        "genMethod": "vibeCoding",
                        "blame": {
                            "revisionId": revision_ids_by_label["r4"],
                            "originalFilePath": "src/app.py",
                            "originalLine": 3,
                            "timestamp": REVISION_TIMESTAMPS[3],
                        },
                    }
                ],
            },
            {
                "fileName": "docs/guide.md",
                "docLines": [
                    {
                        "changeType": "add",
                        "lineLocation": 2,
                        "genRatio": 100,
                        "genMethod": "vibeCoding",
                        "blame": {
                            "revisionId": revision_ids_by_label["r4"],
                            "originalFilePath": "docs/guide.md",
                            "originalLine": 2,
                            "timestamp": REVISION_TIMESTAMPS[3],
                        },
                    }
                ],
            },
        ],
        "r5": [
            {
                "fileName": "src/app.py",
                "codeLines": [
                    {
                        "changeType": "add",
                        "lineLocation": 4,
                        "genRatio": 100,
                        "genMethod": "vibeCoding",
                        "blame": {
                            "revisionId": revision_ids_by_label["r5"],
                            "originalFilePath": "src/app.py",
                            "originalLine": 4,
                            "timestamp": REVISION_TIMESTAMPS[4],
                        },
                    }
                ],
            },
            {
                "fileName": "docs/guide.md",
                "docLines": [
                    {
                        "changeType": "add",
                        "lineLocation": 3,
                        "genRatio": 50,
                        "genMethod": "codeCompletion",
                        "blame": {
                            "revisionId": revision_ids_by_label["r5"],
                            "originalFilePath": "docs/guide.md",
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
        "r2": {"totalCodeLines": 2, "fullGeneratedCodeLines": 0, "partialGeneratedCodeLines": 0, "totalDocLines": 1, "fullGeneratedDocLines": 0, "partialGeneratedDocLines": 0},
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
            "vcsType": "git",
            "repoURL": repo_url,
            "repoBranch": "main",
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
            "vcsType": "git",
            "repoURL": repo_url,
            "repoBranch": "main",
            "revisionId": end_revision_id,
        },
    }


def create_git_repo(repo_dir: Path, metadata_dir: Path, algc_dir: Path, commit_diff_dir: Path) -> dict[str, str]:
    repo_dir.mkdir(parents=True, exist_ok=True)
    run_command(["git", "init"], cwd=repo_dir)
    run_command(["git", "config", "user.name", "UserExamples"], cwd=repo_dir)
    run_command(["git", "config", "user.email", "userexamples@example.local"], cwd=repo_dir)
    run_command(["git", "checkout", "-b", "main"], cwd=repo_dir)

    previous_commit = ""
    revision_ids_by_label: dict[str, str] = {}
    for index, revision_id in enumerate(["r1", "r2", "r3", "r4", "r5"]):
        (repo_dir / "src").mkdir(parents=True, exist_ok=True)
        (repo_dir / "docs").mkdir(parents=True, exist_ok=True)
        (repo_dir / "src" / "app.py").write_text(snapshot_source(revision_id), encoding="utf-8")
        (repo_dir / "docs" / "guide.md").write_text(snapshot_doc(revision_id), encoding="utf-8")
        run_command(["git", "add", "."], cwd=repo_dir)
        env = {**dict(os.environ), "GIT_AUTHOR_DATE": REVISION_TIMESTAMPS[index], "GIT_COMMITTER_DATE": REVISION_TIMESTAMPS[index]}
        run_command(["git", "commit", "-m", revision_id], cwd=repo_dir, env=env)
        commit_sha = run_command(["git", "rev-parse", "HEAD"], cwd=repo_dir)
        revision_ids_by_label[revision_id] = commit_sha

        if previous_commit:
            patch_text = run_command(["git", "diff", "--find-renames=25%", previous_commit, commit_sha], cwd=repo_dir)
        else:
            patch_text = run_command(["git", "show", "--format=", "--find-renames=25%", "--root", commit_sha], cwd=repo_dir)
        (commit_diff_dir / f"{index + 1:04d}_{commit_sha}_commitDiff.patch").write_text(patch_text + "\n", encoding="utf-8")
        previous_commit = commit_sha

    for revision_label in ["r1", "r2", "r3", "r4", "r5"]:
        commit_sha = revision_ids_by_label[revision_label]
        write_json(metadata_dir / f"{commit_sha}_genCodeDesc.json", build_v2603_protocol(str(repo_dir), revision_label, commit_sha))
        write_json(
            algc_dir / f"{commit_sha}_genCodeDesc.json",
            build_v2604_protocol(str(repo_dir), revision_label, commit_sha, revision_ids_by_label),
        )

    return revision_ids_by_label


def write_query_args(base_dir: Path, repo_url: str, end_revision_id: str) -> None:
    write_json(
        base_dir / "queryArgs.json",
        {
            "vcsType": "git",
            "repoURL": repo_url,
            "repoBranch": "main",
            "endRevisionId": end_revision_id,
        },
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the Git support-matrix coverage user example.")
    parser.add_argument("--outputDir", required=True)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    output_dir = Path(args.outputDir).resolve()
    prepare_output_dir(output_dir, args.force)

    repo_dir = output_dir / "repo"
    metadata_dir = output_dir / "genCodeDescSet"
    algc_dir = output_dir / "algcGenCodeDescSet"
    commit_diff_dir = output_dir / "commitDiffSet"
    metadata_dir.mkdir(parents=True, exist_ok=True)
    algc_dir.mkdir(parents=True, exist_ok=True)
    commit_diff_dir.mkdir(parents=True, exist_ok=True)

    revision_ids_by_label = create_git_repo(repo_dir, metadata_dir, algc_dir, commit_diff_dir)
    end_revision_id = revision_ids_by_label["r5"]
    write_query_args(algc_dir, str(repo_dir), end_revision_id)

    for scope in ["A", "B", "C", "D"]:
        write_json(output_dir / f"expected_alga_{scope}.json", build_expected_output(str(repo_dir), scope, end_revision_id, "26.03"))
        write_json(output_dir / f"expected_algb-local_{scope}.json", build_expected_output(str(repo_dir), scope, end_revision_id, "26.03"))
        write_json(output_dir / f"expected_algb-offline_{scope}.json", build_expected_output(str(repo_dir), scope, end_revision_id, "26.03"))
        write_json(output_dir / f"expected_algc_{scope}.json", build_expected_output(str(repo_dir), scope, end_revision_id, "26.04"))

    render_annotated_commit_diff_set(output_dir, output_dir / "commitDiffSetAnnotated")

    write_json(
        output_dir / "manifest.json",
        {
            "scenario": "matrix01-git-coverage",
            "covers": ["A|git|A-D", "B local Git|git|A-D", "B commit diff set|git|A-D", "C git-origin|A-D"],
            "startTime": START_TIME,
            "endTime": END_TIME,
            "endRevisionId": end_revision_id,
            "operatorRunMode": "Use explicit aggregateGenCodeDesc.py aggregate commands from UserExamplesNG/README_UserExamplesNG.md; this generator does not emit run/check shell wrappers.",
            "genRatioLocation": "Inspect genCodeDescSet/*.json or algcGenCodeDescSet/*.json for line attribution; if a patch carries a genRatio tail comment, treat it as a human-readable hint only, not aggregate input.",
            "revisionIdsByLabel": revision_ids_by_label,
        },
    )
    print(f"Generated Git matrix coverage example at {output_dir}")


if __name__ == "__main__":
    main()