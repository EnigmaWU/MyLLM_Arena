import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
UTILITY_PATH = PROJECT_ROOT / "aggregateGenCodeDesc.py"
FIXTURE_DIR = PROJECT_ROOT / "testdata" / "us2_human_overwrites_ai_live_changed"


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


class TestUs2HumanOverwritesAiTdd(unittest.TestCase):
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

    def test_cli_matches_us2_expected_result_when_human_rewrites_one_ai_line(self) -> None:
        self.assertTrue(
            UTILITY_PATH.exists(),
            f"Expected CLI utility at {UTILITY_PATH} for US-2 end-to-end execution.",
        )

        query = json.loads((FIXTURE_DIR / "query.json").read_text(encoding="utf-8"))
        expected_result = json.loads((FIXTURE_DIR / "expected_result.json").read_text(encoding="utf-8"))
        revision_protocol_r1 = json.loads((FIXTURE_DIR / "01_genCodeDesc.json").read_text(encoding="utf-8"))
        revision_protocol_r2 = json.loads((FIXTURE_DIR / "02_genCodeDesc.json").read_text(encoding="utf-8"))

        with tempfile.TemporaryDirectory() as temp_dir:
            root_dir = Path(temp_dir)
            repo_dir = root_dir / "repo"
            protocol_dir = root_dir / "protocols"
            output_file = root_dir / "out.json"

            repo_dir.mkdir()
            protocol_dir.mkdir()

            # WHY: US-2 is about effective ownership after a later rewrite, so
            # the test must use a real two-commit Git history and let blame
            # decide which surviving lines still point to the AI revision.
            repo = GitRepoHarness(repo_dir)
            repo.write(
                "src/normalize.py",
                "value = raw.strip()\n"
                "value = value.lower()\n"
                "result = value\n",
            )
            revision_id_r1 = repo.commit_all("us2-r1", "2026-03-10T09:00:00Z")

            repo.write(
                "src/normalize.py",
                "value = raw.strip()\n"
                "value = raw.casefold()\n"
                "result = value\n",
            )
            revision_id_r2 = repo.commit_all("us2-r2", "2026-03-20T09:00:00Z")

            revision_protocol_r1["REPOSITORY"]["repoURL"] = str(repo_dir)
            revision_protocol_r1["REPOSITORY"]["revisionId"] = revision_id_r1
            protocol_path_r1 = protocol_dir / f"{revision_id_r1}_genCodeDesc.json"
            protocol_path_r1.write_text(json.dumps(revision_protocol_r1, indent=2), encoding="utf-8")

            revision_protocol_r2["REPOSITORY"]["repoURL"] = str(repo_dir)
            revision_protocol_r2["REPOSITORY"]["revisionId"] = revision_id_r2
            protocol_path_r2 = protocol_dir / f"{revision_id_r2}_genCodeDesc.json"
            protocol_path_r2.write_text(json.dumps(revision_protocol_r2, indent=2), encoding="utf-8")

            self.run_cli(repo_dir, output_file, protocol_dir, query)

            actual_result = json.loads(output_file.read_text(encoding="utf-8"))
            expected_result["REPOSITORY"]["repoURL"] = str(repo_dir)
            expected_result["REPOSITORY"]["revisionId"] = revision_id_r2

            self.assertEqual(actual_result, expected_result)


if __name__ == "__main__":
    unittest.main()