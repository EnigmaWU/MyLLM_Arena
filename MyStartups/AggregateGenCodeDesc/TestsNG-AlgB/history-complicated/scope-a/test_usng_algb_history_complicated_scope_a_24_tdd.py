import tempfile
import unittest
from pathlib import Path

from tests.cli_test_support import GitRepoHarness, load_json, run_cli, write_revision_protocol


class TestUsngAlgbHistoryComplicatedScopeA24Tdd(unittest.TestCase):
    """USNG-ALGB-HISTORY-COMPLICATED-SCOPE-A-24: Git Rename And Move Handling For Period Contribution"""

    def test_rename_does_not_inflate_period_added_count(self) -> None:
        """GIVEN a file is renamed during the period and a new AI line is added,
        WHEN Algorithm B computes the period-added result,
        THEN only the genuinely new line counts; pre-rename surviving lines are excluded."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo_dir = root / "repo"
            protocol_dir = root / "protocols"
            output_file = root / "out.json"
            repo_dir.mkdir()
            protocol_dir.mkdir()

            repo = GitRepoHarness(repo_dir)

            # Pre-window: create the original file
            repo.write("src/old_module.py", "def old():\n    return 0\n")
            repo.commit_all("pre-window", "2026-02-10T09:00:00Z")

            # In-window r1: rename the file and add a new AI line
            repo.rename("src/old_module.py", "src/new_module.py")
            # Add a new AI function to the renamed file
            (repo_dir / "src" / "new_module.py").write_text(
                "def old():\n    return 0\ndef ai_new():\n    return ai_result()\n",
                encoding="utf-8",
            )
            r1 = repo.commit_all("r1-rename-and-add", "2026-03-10T09:00:00Z")

            protocol_r1 = {
                "protocolName": "generatedTextDesc",
                "protocolVersion": "26.03",
                "codeAgent": "TestAgent",
                "SUMMARY": {"totalCodeLines": 2, "fullGeneratedCodeLines": 2, "partialGeneratedCodeLines": 0},
                "REPOSITORY": {"repoURL": str(repo_dir), "repoBranch": "main", "revisionId": r1},
                "DETAIL": [
                    {
                        "fileName": "src/new_module.py",
                        "codeLines": [
                            {"lineLocation": 3, "genRatio": 0, "genMethod": "Manual"},
                            {"lineLocation": 4, "genRatio": 100, "genMethod": "codeCompletion"},
                        ],
                    }
                ],
            }
            write_revision_protocol(protocol_dir, protocol_r1, repo_dir, r1)

            query = {
                "vcsType": "git",
                "repoURL": str(repo_dir),
                "repoBranch": "main",
                "startTime": "2026-03-01",
                "endTime": "2026-03-31",
                "scope": "A",
                "metric": "period_added_ai_ratio",
            }

            run_cli(repo_dir, output_file, protocol_dir, query, extra_args=["--algorithm", "B"])

            result = load_json(output_file)
            summary = result["SUMMARY"]
            # Only in-window added lines count:
            # "def ai_new():" (0) and "    return ai_result()" (100) → added in r1 (in-window)
            # Pre-rename lines "def old():" and "    return 0" → excluded
            self.assertEqual(summary["totalCodeLines"], 2)
            self.assertEqual(summary["fullGeneratedCodeLines"], 1)
            self.assertEqual(summary["partialGeneratedCodeLines"], 0)


if __name__ == "__main__":
    unittest.main()
