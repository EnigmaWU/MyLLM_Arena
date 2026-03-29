import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
UTILITY_PATH = PROJECT_ROOT / "aggregateGenCodeDesc.py"
FIXTURE_DIR = PROJECT_ROOT / "testdata" / "us1_live_changed_source_ratio"


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


class TestUs1LiveChangedSourceRatioTdd(unittest.TestCase):
    maxDiff = None

    def run_cli(self, repo_dir: Path, output_file: Path, protocol_dir: Path, query: dict) -> subprocess.CompletedProcess[str]:
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
            ],
            cwd=PROJECT_ROOT,
            text=True,
            capture_output=True,
            check=True,
        )

    def test_cli_matches_us1_expected_result_for_real_git_repo(self) -> None:
        self.assertTrue(
            UTILITY_PATH.exists(),
            f"Expected CLI utility at {UTILITY_PATH} for US-1 end-to-end execution.",
        )

        query = json.loads((FIXTURE_DIR / "query.json").read_text(encoding="utf-8"))
        expected_result = json.loads((FIXTURE_DIR / "expected_result.json").read_text(encoding="utf-8"))
        revision_protocol = json.loads((FIXTURE_DIR / "01_genCodeDesc.json").read_text(encoding="utf-8"))

        with tempfile.TemporaryDirectory() as temp_dir:
            root_dir = Path(temp_dir)
            repo_dir = root_dir / "repo"
            protocol_dir = root_dir / "protocols"
            output_file = root_dir / "out.json"

            repo_dir.mkdir()
            protocol_dir.mkdir()

            repo = GitRepoHarness(repo_dir)
            repo.write(
                "src/calc.py",
                "def calc(x):\n"
                "    value = x + 1\n"
                "    boosted = value * 2\n"
                "    return boosted\n",
            )
            revision_id = repo.commit_all("us1-r1", "2026-03-10T09:00:00Z")

            revision_protocol["REPOSITORY"]["repoURL"] = str(repo_dir)
            revision_protocol["REPOSITORY"]["revisionId"] = revision_id
            protocol_path = protocol_dir / f"{revision_id}_genCodeDesc.json"
            protocol_path.write_text(json.dumps(revision_protocol, indent=2), encoding="utf-8")

            self.run_cli(repo_dir, output_file, protocol_dir, query)

            actual_result = json.loads(output_file.read_text(encoding="utf-8"))
            expected_result["REPOSITORY"]["repoURL"] = str(repo_dir)
            expected_result["REPOSITORY"]["revisionId"] = revision_id

            self.assertEqual(actual_result, expected_result)

    def test_cli_fails_when_protocol_repository_identity_mismatches_query(self) -> None:
        query = json.loads((FIXTURE_DIR / "query.json").read_text(encoding="utf-8"))
        revision_protocol = json.loads((FIXTURE_DIR / "01_genCodeDesc.json").read_text(encoding="utf-8"))

        with tempfile.TemporaryDirectory() as temp_dir:
            root_dir = Path(temp_dir)
            repo_dir = root_dir / "repo"
            protocol_dir = root_dir / "protocols"
            output_file = root_dir / "out.json"

            repo_dir.mkdir()
            protocol_dir.mkdir()

            repo = GitRepoHarness(repo_dir)
            repo.write(
                "src/calc.py",
                "def calc(x):\n"
                "    value = x + 1\n"
                "    boosted = value * 2\n"
                "    return boosted\n",
            )
            revision_id = repo.commit_all("us1-r1", "2026-03-10T09:00:00Z")

            revision_protocol["REPOSITORY"]["repoURL"] = str(repo_dir)
            revision_protocol["REPOSITORY"]["repoBranch"] = "wrong-branch"
            revision_protocol["REPOSITORY"]["revisionId"] = revision_id
            protocol_path = protocol_dir / f"{revision_id}_genCodeDesc.json"
            protocol_path.write_text(json.dumps(revision_protocol, indent=2), encoding="utf-8")

            with self.assertRaises(subprocess.CalledProcessError) as context:
                self.run_cli(repo_dir, output_file, protocol_dir, query)

            self.assertIn("Metadata repoBranch mismatch", context.exception.stderr)


if __name__ == "__main__":
    unittest.main()