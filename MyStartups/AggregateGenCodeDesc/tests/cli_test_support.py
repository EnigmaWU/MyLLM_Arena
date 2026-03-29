import json
import os
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
UTILITY_PATH = PROJECT_ROOT / "aggregateGenCodeDesc.py"


class GitRepoHarness:
    def __init__(self, repo_dir: Path):
        self.repo_dir = repo_dir
        self.commit_ids: dict[str, str] = {}
        self._run(["git", "init", "-b", "main"])
        self._run(["git", "config", "user.name", "AggregateGenCodeDesc Tests"])
        self._run(["git", "config", "user.email", "tests@example.local"])

    def _run(self, command: list[str], env: dict[str, str] | None = None) -> str:
        merged_env = os.environ.copy()
        if env:
            merged_env.update(env)
        result = subprocess.run(
            command,
            cwd=self.repo_dir,
            env=merged_env,
            text=True,
            capture_output=True,
            check=True,
        )
        return result.stdout.strip()

    def write(self, relative_path: str, content: str) -> None:
        file_path = self.repo_dir / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")

    def rename(self, old_path: str, new_path: str) -> None:
        self._run(["git", "mv", old_path, new_path])

    def checkout_new_branch(self, branch_name: str) -> None:
        self._run(["git", "checkout", "-b", branch_name])

    def checkout(self, branch_name: str) -> None:
        self._run(["git", "checkout", branch_name])

    def merge_no_ff(self, branch_name: str, label: str, date: str) -> str:
        env = {
            "GIT_AUTHOR_DATE": date,
            "GIT_COMMITTER_DATE": date,
        }
        self._run(["git", "merge", "--no-ff", branch_name, "-m", label], env=env)
        commit_id = self._run(["git", "rev-parse", "HEAD"])
        self.commit_ids[label] = commit_id
        return commit_id

    def commit_all(self, label: str, date: str) -> str:
        env = {
            "GIT_AUTHOR_DATE": date,
            "GIT_COMMITTER_DATE": date,
        }
        self._run(["git", "add", "-A"], env=env)
        self._run(["git", "commit", "-m", label], env=env)
        commit_id = self._run(["git", "rev-parse", "HEAD"])
        self.commit_ids[label] = commit_id
        return commit_id


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_revision_protocol(protocol_dir: Path, protocol: dict, repo_dir: Path, revision_id: str) -> None:
    protocol["REPOSITORY"]["repoURL"] = str(repo_dir)
    protocol["REPOSITORY"]["revisionId"] = revision_id
    (protocol_dir / f"{revision_id}_genCodeDesc.json").write_text(
        json.dumps(protocol, indent=2),
        encoding="utf-8",
    )


def run_cli(
    repo_dir: Path,
    output_file: Path,
    protocol_dir: Path,
    query: dict,
    extra_args: list[str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "python3",
            str(UTILITY_PATH),
            "--vcsType",
            query["vcsType"],
            "--repoURL",
            str(repo_dir),
            "--repoBranch",
            query["repoBranch"],
            "--startTime",
            query["startTime"],
            "--endTime",
            query["endTime"],
            "--outputFile",
            str(output_file),
            "--genCodeDescSetDir",
            str(protocol_dir),
            *(extra_args or []),
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=True,
    )