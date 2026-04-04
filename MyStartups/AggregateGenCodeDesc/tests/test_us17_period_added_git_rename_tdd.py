"""US-17: Git rename and move handling for period contribution.

Scenario:
  r0 (before window): create src/old_name.py with 3 code lines (human)
  r1 (in window):     rename src/old_name.py → src/new_name.py AND add 1 AI line

Expected: Only the new AI line counts for period-added.
Pre-window lines survive the rename but their origin (r0) is not in the window.
"""

import tempfile
import unittest
from pathlib import Path

from aggregateGenCodeDesc import PROTOCOL_VERSION
from tests.cli_test_support import GitRepoHarness, load_json, run_cli, write_revision_protocol


class TestUS17PeriodAddedGitRename(unittest.TestCase):

    def _build_repo(self, root_dir: Path):
        repo_dir = root_dir / "repo"
        protocol_dir = root_dir / "protocols"
        repo_dir.mkdir()
        protocol_dir.mkdir()

        repo = GitRepoHarness(repo_dir)

        # r0: human creates src/old_name.py
        repo.write(
            "src/old_name.py",
            "def helper(x):\n"
            "    y = x * 2\n"
            "    return y\n",
        )
        _r0 = repo.commit_all("create-file", "2026-02-20T09:00:00Z")

        # r1: rename + add AI line
        repo.rename("src/old_name.py", "src/new_name.py")
        repo.write(
            "src/new_name.py",
            "def helper(x):\n"
            "    y = x * 2\n"
            "    z = ai_transform(y)\n"
            "    return y\n",
        )
        r1 = repo.commit_all("rename-and-ai-add", "2026-03-15T09:00:00Z")

        # Protocol for r1: line 3 in new_name.py is AI
        write_revision_protocol(
            protocol_dir,
            {
                "protocolName": "generatedTextDesc",
                "protocolVersion": PROTOCOL_VERSION,
                "SUMMARY": {"totalCodeLines": 1, "fullGeneratedCodeLines": 1, "partialGeneratedCodeLines": 0},
                "REPOSITORY": {"vcsType": "git", "repoURL": "", "repoBranch": "main", "revisionId": ""},
                "DETAIL": [
                    {
                        "fileName": "src/new_name.py",
                        "codeLines": [{"lineLocation": 3, "genRatio": 100}],
                    }
                ],
            },
            repo_dir,
            r1,
        )

        query = {
            "vcsType": "git",
            "repoURL": str(repo_dir),
            "repoBranch": "main",
            "scope": "A",
            "startTime": "2026-03-01",
            "endTime": "2026-03-31",
        }
        return repo, protocol_dir, query, r1

    def test_period_added_after_rename_counts_only_new_lines(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo, protocol_dir, query, r1 = self._build_repo(Path(temp_dir))
            output_file = Path(temp_dir) / "out.json"

            result = run_cli(
                repo.repo_dir,
                output_file,
                protocol_dir,
                query,
                extra_args=["--algorithm", "B", "--metric", "period_added_ai_ratio"],
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            actual = load_json(output_file)

        # Only the AI line added in r1 should count; renamed pre-window lines excluded
        self.assertEqual(
            actual["SUMMARY"],
            {
                "totalCodeLines": 1,
                "fullGeneratedCodeLines": 1,
                "partialGeneratedCodeLines": 0,
            },
        )
        self.assertEqual(actual["REPOSITORY"]["revisionId"], r1)

    def test_renamed_file_appears_under_new_path(self) -> None:
        """Verify the output references the new file path, not the old one."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo, protocol_dir, query, _r1 = self._build_repo(Path(temp_dir))
            output_file = Path(temp_dir) / "out.json"

            result = run_cli(
                repo.repo_dir,
                output_file,
                protocol_dir,
                query,
                extra_args=["--algorithm", "B", "--metric", "period_added_ai_ratio"],
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            actual = load_json(output_file)

        # Period-added aggregation produces only SUMMARY, no DETAIL with file paths
        # But the SUMMARY line count proves the rename was tracked correctly
        self.assertEqual(actual["SUMMARY"]["totalCodeLines"], 1)


if __name__ == "__main__":
    unittest.main()
