#!/usr/bin/env python3

import argparse
import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path


START_TIME = "2026-02-20"
END_TIME = "2026-03-31"


class GenerationError(RuntimeError):
    pass


class _DateCursor:
    def __init__(self, start: datetime):
        self.current = start

    def next(self) -> str:
        value = self.current
        self.current += timedelta(minutes=1)
        return value.strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass
class ExampleStats:
    branch_count: int
    commit_count: int
    end_revision_id: str
    feature_commit_count: int
    added_lines: int
    deleted_lines: int


class GitRepoBuilder:
    def __init__(self, repo_dir: Path):
        self.repo_dir = repo_dir
        self.repo_dir.mkdir(parents=True, exist_ok=True)
        self._run(["git", "init"])
        self._run(["git", "config", "user.name", "AggregateGenCodeDesc User Example"])
        self._run(["git", "config", "user.email", "userexamples@example.local"])
        self._run(["git", "checkout", "-b", "main"])

    def _run(self, args: list[str], env: dict[str, str] | None = None) -> str:
        completed = subprocess.run(
            args,
            cwd=self.repo_dir,
            env=env,
            check=False,
            capture_output=True,
            text=True,
        )
        if completed.returncode != 0:
            raise GenerationError(
                f"Command failed in {self.repo_dir}: {' '.join(args)}\n{completed.stderr.strip()}"
            )
        return completed.stdout.strip()

    def write(self, relative_path: str, content: str) -> None:
        target_path = self.repo_dir / relative_path
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(content, encoding="utf-8")

    def commit_all(self, message: str, commit_date: str) -> str:
        self._run(["git", "add", "."])
        env = {
            "GIT_AUTHOR_DATE": commit_date,
            "GIT_COMMITTER_DATE": commit_date,
        }
        self._run(["git", "commit", "-m", message], env={**dict(os.environ), **env})
        return self.head_revision()

    def checkout(self, branch_name: str) -> None:
        self._run(["git", "checkout", branch_name])

    def checkout_new_branch(self, branch_name: str) -> None:
        self._run(["git", "checkout", "-b", branch_name])

    def merge_no_ff(self, branch_name: str, message: str, commit_date: str) -> str:
        env = {
            "GIT_AUTHOR_DATE": commit_date,
            "GIT_COMMITTER_DATE": commit_date,
        }
        self._run(["git", "merge", "--no-ff", branch_name, "-m", message], env={**dict(os.environ), **env})
        return self.head_revision()

    def merge_octopus(self, branch_names: list[str], message: str, commit_date: str) -> str:
        env = {
            "GIT_AUTHOR_DATE": commit_date,
            "GIT_COMMITTER_DATE": commit_date,
        }
        self._run(
            ["git", "merge", "--no-ff", *branch_names, "-m", message],
            env={**dict(os.environ), **env},
        )
        return self.head_revision()

    def head_revision(self) -> str:
        return self._run(["git", "rev-parse", "HEAD"])

    def branch_count(self) -> int:
        return len(self._run(["git", "branch", "--format=%(refname:short)"]).splitlines())

    def commit_count(self) -> int:
        return int(self._run(["git", "rev-list", "--count", "--all"]))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a heavy real Git user example for AggregateGenCodeDesc.")
    parser.add_argument("--outputDir", required=True, help="Directory where the generated example will be written")
    parser.add_argument("--force", action="store_true", help="Replace outputDir if it already exists")
    parser.add_argument("--featureBranches", type=int, default=100, help="Number of feature branches to create")
    parser.add_argument("--commitsPerFeatureBranch", type=int, default=10, help="Number of commits per feature branch")
    parser.add_argument("--fullAiBranches", type=int, default=40, help="How many feature branches have 100 percent AI attribution")
    parser.add_argument("--partialAiBranches", type=int, default=30, help="How many feature branches have partial AI attribution")
    parser.add_argument("--partialAiRatio", type=int, default=60, help="genRatio for partial AI branches")
    parser.add_argument(
        "--linesAddedPerFeatureCommit",
        type=int,
        default=10,
        help="How many new lines each feature commit adds; one carried line is deleted on the next commit",
    )
    return parser.parse_args()


def validate_args(args: argparse.Namespace) -> None:
    if args.featureBranches <= 0:
        raise GenerationError("--featureBranches must be greater than 0")
    if args.commitsPerFeatureBranch <= 0:
        raise GenerationError("--commitsPerFeatureBranch must be greater than 0")
    if args.fullAiBranches < 0 or args.partialAiBranches < 0:
        raise GenerationError("AI branch counts cannot be negative")
    if args.fullAiBranches + args.partialAiBranches > args.featureBranches:
        raise GenerationError("fullAiBranches + partialAiBranches cannot exceed featureBranches")
    if args.linesAddedPerFeatureCommit <= 0:
        raise GenerationError("--linesAddedPerFeatureCommit must be greater than 0")


def prepare_output_dir(output_dir: Path, force: bool) -> None:
    if output_dir.exists():
        if not force:
            raise GenerationError(f"Output directory already exists: {output_dir}. Use --force to replace it.")
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)


def feature_ratio(feature_index: int, full_ai_branches: int, partial_ai_branches: int, partial_ai_ratio: int) -> int:
    if feature_index < full_ai_branches:
        return 100
    if feature_index < full_ai_branches + partial_ai_branches:
        return partial_ai_ratio
    return 0


def feature_file_content(feature_index: int, commit_index: int, lines_added_per_feature_commit: int) -> str:
    stable_lines_per_commit = max(lines_added_per_feature_commit - 1, 0)
    lines = [
        f"# feature {feature_index:03d}",
        f"ai_anchor_full_{feature_index:03d} = {feature_index}",
        f"ai_anchor_partial_{feature_index:03d} = {feature_index} * 2",
    ]
    for prior_commit_index in range(1, commit_index + 1):
        for stable_line_index in range(1, stable_lines_per_commit + 1):
            lines.append(
                f"# feature_{feature_index:03d}_commit_{prior_commit_index:02d}_line_{stable_line_index:02d} = {feature_index} + {prior_commit_index} + {stable_line_index}"
            )
    lines.append(f"# carry_line_{feature_index:03d}_{commit_index:03d} = {feature_index} + {commit_index}")
    return "\n".join(lines) + "\n"


def base_feature_file_content(feature_index: int) -> str:
    return "\n".join(
        [
            f"# feature {feature_index:03d}",
            f"ai_anchor_full_{feature_index:03d} = {feature_index}",
            f"ai_anchor_partial_{feature_index:03d} = {feature_index} * 2",
            f"# carry_line_{feature_index:03d}_000 = {feature_index}",
        ]
    ) + "\n"


def base_revision_protocol(repo_url: str, revision_id: str, args: argparse.Namespace) -> dict:
    detail = []
    total_code_lines = 0
    full_generated_code_lines = 0
    partial_generated_code_lines = 0

    for feature_index in range(args.featureBranches):
        ratio = feature_ratio(
            feature_index,
            args.fullAiBranches,
            args.partialAiBranches,
            args.partialAiRatio,
        )
        file_name = f"src/features/feature_{feature_index:03d}.py"
        code_lines = []
        if ratio > 0:
            code_lines = [
                {"lineLocation": 2, "genRatio": ratio, "genMethod": "codeCompletion"},
                {"lineLocation": 3, "genRatio": ratio, "genMethod": "codeCompletion"},
            ]
            total_code_lines += 2
            if ratio == 100:
                full_generated_code_lines += 2
            else:
                partial_generated_code_lines += 2

        detail.append({"fileName": file_name, "codeLines": code_lines})

    return {
        "protocolName": "generatedTextDesc",
        "protocolVersion": "26.03",
        "codeAgent": "HeavyUserExampleAgent",
        "SUMMARY": {
            "totalCodeLines": total_code_lines,
            "fullGeneratedCodeLines": full_generated_code_lines,
            "partialGeneratedCodeLines": partial_generated_code_lines,
        },
        "DETAIL": detail,
        "REPOSITORY": {
            "vcsType": "git",
            "repoURL": repo_url,
            "repoBranch": "main",
            "revisionId": revision_id,
        },
    }


def revision_protocol(repo_url: str, repo_branch: str, revision_id: str, file_name: str, ratio: int) -> dict:
    code_lines = []
    full_generated_code_lines = 0
    partial_generated_code_lines = 0

    if ratio > 0:
        code_lines = [
            {"lineLocation": 2, "genRatio": ratio, "genMethod": "codeCompletion"},
            {"lineLocation": 3, "genRatio": ratio, "genMethod": "codeCompletion"},
        ]
        if ratio == 100:
            full_generated_code_lines = 2
        else:
            partial_generated_code_lines = 2

    return {
        "protocolName": "generatedTextDesc",
        "protocolVersion": "26.03",
        "codeAgent": "HeavyUserExampleAgent",
        "SUMMARY": {
            "totalCodeLines": len(code_lines),
            "fullGeneratedCodeLines": full_generated_code_lines,
            "partialGeneratedCodeLines": partial_generated_code_lines,
        },
        "DETAIL": [{"fileName": file_name, "codeLines": code_lines}],
        "REPOSITORY": {
            "vcsType": "git",
            "repoURL": repo_url,
            "repoBranch": repo_branch,
            "revisionId": revision_id,
        },
    }


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def write_helper_scripts(project_root: Path, example_dir: Path, end_revision_id: str) -> None:
    run_script = example_dir / "run_aggregate.sh"
    check_script = example_dir / "check_output.sh"

    run_script.write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n\n"
        f"REPO_ROOT={json.dumps(str(project_root))}\n"
        f"EXAMPLE_DIR={json.dumps(str(example_dir))}\n"
        'OUTPUT_FILE="${1:-/tmp/agg-userexample-heavy-01-out.json}"\n\n'
        'python3 "$REPO_ROOT/aggregateGenCodeDesc.py" \\\n'
        '  --vcsType git \\\n'
        '  --repoURL "$EXAMPLE_DIR/repo" \\\n'
        '  --repoBranch main \\\n'
        f'  --startTime {START_TIME} \\\n'
        f'  --endTime {END_TIME} \\\n'
        '  --scope A \\\n'
        '  --outputFile "$OUTPUT_FILE" \\\n'
        '  --genCodeDescSetDir "$EXAMPLE_DIR/genCodeDescSet"\n',
        encoding="utf-8",
    )

    check_script.write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n\n"
        f"EXAMPLE_DIR={json.dumps(str(example_dir))}\n"
        'OUTPUT_FILE="${1:-/tmp/agg-userexample-heavy-01-out.json}"\n\n'
        'python3 - "$OUTPUT_FILE" "$EXAMPLE_DIR/expected_result.json" <<\'PY\'\n'
        'import json\n'
        'import sys\n'
        'from pathlib import Path\n\n'
        'actual = json.loads(Path(sys.argv[1]).read_text())\n'
        'expected = json.loads(Path(sys.argv[2]).read_text())\n\n'
        'if actual != expected:\n'
        '    raise SystemExit("Heavy example mismatch")\n\n'
        'print("Heavy example OK: actual output exactly matches expected_result.json")\n'
        'PY\n',
        encoding="utf-8",
    )


def build_example(output_dir: Path, args: argparse.Namespace) -> ExampleStats:
    repo_dir = output_dir / "repo"
    protocol_dir = output_dir / "genCodeDescSet"
    protocol_dir.mkdir(parents=True, exist_ok=True)

    repo = GitRepoBuilder(repo_dir)
    for feature_index in range(args.featureBranches):
        repo.write(f"src/features/feature_{feature_index:03d}.py", base_feature_file_content(feature_index))
    base_revision_id = repo.commit_all("heavy-userexample-base", "2026-02-20T09:00:00Z")
    write_json(protocol_dir / f"{base_revision_id}_genCodeDesc.json", base_revision_protocol(str(repo_dir), base_revision_id, args))

    date_cursor = _DateCursor(datetime(2026, 3, 1, 0, 0, tzinfo=timezone.utc))
    feature_branch_names = [f"feature-{feature_index:03d}" for feature_index in range(args.featureBranches)]

    for feature_index, branch_name in enumerate(feature_branch_names):
        file_name = f"src/features/feature_{feature_index:03d}.py"
        repo.checkout("main")
        repo.checkout_new_branch(branch_name)

        revision_id = ""
        for commit_index in range(1, args.commitsPerFeatureBranch + 1):
            repo.write(file_name, feature_file_content(feature_index, commit_index, args.linesAddedPerFeatureCommit))
            revision_id = repo.commit_all(
                f"heavy-f{feature_index:03d}-c{commit_index:02d}",
                date_cursor.next(),
            )

    repo.checkout("main")
    repo.checkout_new_branch("release")

    first_phase_count = max(1, args.featureBranches // 2)
    first_phase = feature_branch_names[:first_phase_count]
    second_phase_end = first_phase_count + max(0, (args.featureBranches - first_phase_count) // 2)
    second_phase = feature_branch_names[first_phase_count:second_phase_end]
    third_phase = feature_branch_names[second_phase_end:]

    for group_index, start_index in enumerate(range(0, len(first_phase), 10)):
        integration_branch_name = f"integration-{group_index:02d}"
        repo.checkout("release")
        repo.checkout_new_branch(integration_branch_name)
        for branch_name in first_phase[start_index:start_index + 10]:
            repo.merge_no_ff(branch_name, f"heavy-int-{group_index:02d}-{branch_name}", date_cursor.next())
        repo.checkout("release")
        repo.merge_no_ff(integration_branch_name, f"heavy-release-from-{integration_branch_name}", date_cursor.next())

    for group_index, start_index in enumerate(range(0, len(second_phase), 5)):
        merge_group = second_phase[start_index:start_index + 5]
        if not merge_group:
            continue
        repo.checkout("release")
        if len(merge_group) == 1:
            repo.merge_no_ff(merge_group[0], f"heavy-release-direct-{merge_group[0]}", date_cursor.next())
        else:
            repo.merge_octopus(merge_group, f"heavy-release-octopus-{group_index:02d}", date_cursor.next())

    for branch_name in third_phase:
        repo.checkout("release")
        repo.merge_no_ff(branch_name, f"heavy-release-direct-{branch_name}", date_cursor.next())

    repo.checkout("main")
    end_revision_id = repo.merge_no_ff("release", "heavy-main-final", date_cursor.next())

    return ExampleStats(
        branch_count=repo.branch_count(),
        commit_count=repo.commit_count(),
        end_revision_id=end_revision_id,
        feature_commit_count=args.featureBranches * args.commitsPerFeatureBranch,
        added_lines=args.featureBranches * args.commitsPerFeatureBranch * args.linesAddedPerFeatureCommit,
        deleted_lines=args.featureBranches * args.commitsPerFeatureBranch,
    )


def write_example_metadata(output_dir: Path, args: argparse.Namespace, stats: ExampleStats) -> None:
    repo_dir = output_dir / "repo"
    expected_result = {
        "protocolName": "generatedTextDesc",
        "protocolVersion": "26.03",
        "SUMMARY": {
            "totalCodeLines": args.featureBranches * 2,
            "fullGeneratedCodeLines": args.fullAiBranches * 2,
            "partialGeneratedCodeLines": args.partialAiBranches * 2,
        },
        "REPOSITORY": {
            "vcsType": "git",
            "repoURL": str(repo_dir),
            "repoBranch": "main",
            "revisionId": stats.end_revision_id,
        },
    }
    query = {
        "vcsType": "git",
        "repoURL": str(repo_dir),
        "repoBranch": "main",
        "metric": "live_changed_source_ratio",
        "algorithm": "A",
        "scope": "A",
        "startTime": START_TIME,
        "endTime": END_TIME,
        "endRevisionId": stats.end_revision_id,
    }
    manifest = {
        "scenario": "heavy01-git-production-scale",
        "featureBranches": args.featureBranches,
        "commitsPerFeatureBranch": args.commitsPerFeatureBranch,
        "featureCommitCount": stats.feature_commit_count,
        "linesAddedPerFeatureCommit": args.linesAddedPerFeatureCommit,
        "featureCommitAddedLines": stats.added_lines,
        "featureCommitDeletedLines": stats.deleted_lines,
        "branchCount": stats.branch_count,
        "commitCount": stats.commit_count,
        "repoURL": str(repo_dir),
        "repoBranch": "main",
        "endRevisionId": stats.end_revision_id,
        "startTime": START_TIME,
        "endTime": END_TIME,
    }
    write_json(output_dir / "expected_result.json", expected_result)
    write_json(output_dir / "query.json", query)
    write_json(output_dir / "manifest.json", manifest)


def main() -> None:
    args = parse_args()
    validate_args(args)

    output_dir = Path(args.outputDir).resolve()
    prepare_output_dir(output_dir, args.force)

    project_root = Path(__file__).resolve().parents[2]
    stats = build_example(output_dir, args)
    write_example_metadata(output_dir, args, stats)
    write_helper_scripts(project_root, output_dir, stats.end_revision_id)

    print(f"Generated heavy example at {output_dir}")
    print(f"Branches: {stats.branch_count}")
    print(f"Commits: {stats.commit_count}")
    print(f"Feature commits: {stats.feature_commit_count}")
    print(f"Feature added lines: {stats.added_lines}")
    print(f"Feature deleted lines: {stats.deleted_lines}")
    print(f"End revision: {stats.end_revision_id}")


if __name__ == "__main__":
    main()