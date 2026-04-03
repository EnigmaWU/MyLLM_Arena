import json
import os
import subprocess
from pathlib import Path

from aggregateGenCodeDesc import load_json_document


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

    def merge_with_manual_resolution(
        self,
        branch_name: str,
        label: str,
        date: str,
        resolved_files: dict[str, str],
    ) -> str:
        env = {
            "GIT_AUTHOR_DATE": date,
            "GIT_COMMITTER_DATE": date,
        }
        result = subprocess.run(
            ["git", "merge", "--no-ff", branch_name, "-m", label],
            cwd=self.repo_dir,
            env={**os.environ, **env},
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode == 0:
            commit_id = self._run(["git", "rev-parse", "HEAD"])
            self.commit_ids[label] = commit_id
            return commit_id
        if result.returncode != 1:
            raise subprocess.CalledProcessError(result.returncode, result.args, output=result.stdout, stderr=result.stderr)

        for relative_path, content in resolved_files.items():
            self.write(relative_path, content)
        self._run(["git", "add", "-A"], env=env)
        self._run(["git", "commit", "-m", label], env=env)
        commit_id = self._run(["git", "rev-parse", "HEAD"])
        self.commit_ids[label] = commit_id
        return commit_id

    def merge_octopus(self, branch_names: list[str], label: str, date: str) -> str:
        env = {
            "GIT_AUTHOR_DATE": date,
            "GIT_COMMITTER_DATE": date,
        }
        self._run(["git", "merge", "-m", label, *branch_names], env=env)
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


class SvnRepoHarness:
    def __init__(self, repo_dir: Path, working_copy_dir: Path):
        self.repo_dir = repo_dir
        self.working_copy_dir = working_copy_dir
        self.revision_ids: dict[str, str] = {}
        subprocess.run(["svnadmin", "create", str(self.repo_dir)], check=True, capture_output=True, text=True)
        hook_path = self.repo_dir / "hooks" / "pre-revprop-change"
        hook_path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        hook_path.chmod(0o755)
        subprocess.run(["svn", "checkout", self.repo_url, str(self.working_copy_dir)], check=True, capture_output=True, text=True)
        (self.working_copy_dir / "trunk").mkdir()
        subprocess.run(["svn", "add", str(self.working_copy_dir / "trunk")], check=True, capture_output=True, text=True)
        self.commit_all("create trunk", "2026-02-24T09:00:00.000000Z")

    @property
    def repo_url(self) -> str:
        return f"file://{self.repo_dir}"

    @property
    def trunk_url(self) -> str:
        return f"{self.repo_url}/trunk"

    def write(self, relative_path: str, content: str) -> None:
        file_path = self.working_copy_dir / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")

    def add(self, relative_path: str) -> None:
        subprocess.run(
            ["svn", "add", "--parents", str(self.working_copy_dir / relative_path)],
            check=True,
            capture_output=True,
            text=True,
        )

    def commit_all(self, label: str, date: str | None = None) -> str:
        result = subprocess.run(
            ["svn", "commit", "-m", label, str(self.working_copy_dir)],
            check=True,
            capture_output=True,
            text=True,
        )
        committed_line = next(line for line in result.stdout.splitlines() if line.startswith("Committed revision "))
        revision_id = committed_line.removeprefix("Committed revision ").removesuffix(".")
        if date is not None:
            subprocess.run(
                ["svn", "propset", "--revprop", "-r", revision_id, "svn:date", date, self.repo_url],
                check=True,
                capture_output=True,
                text=True,
            )
        self.revision_ids[label] = revision_id
        return revision_id


def load_json(path: Path) -> dict:
    return load_json_document(path.read_text(encoding="utf-8"))


def write_revision_protocol(
    protocol_dir: Path,
    protocol: dict,
    repo_dir: Path,
    revision_id: str,
    repo_url_override: str | None = None,
) -> None:
    protocol["REPOSITORY"]["repoURL"] = repo_url_override or str(repo_dir)
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
    repo_url_override: str | None = None,
    working_dir_override: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "python3",
            str(UTILITY_PATH),
            "--vcsType",
            query["vcsType"],
            "--repoURL",
            repo_url_override or str(repo_dir),
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
            *( ["--workingDir", str(working_dir_override)] if working_dir_override else [] ),
            *(extra_args or []),
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=True,
    )