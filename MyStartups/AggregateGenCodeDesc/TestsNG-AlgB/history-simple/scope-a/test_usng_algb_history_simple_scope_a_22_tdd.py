import tempfile
import unittest
from pathlib import Path

from tests.cli_test_support import GitRepoHarness, load_json, run_cli, write_revision_protocol


class TestUsngAlgbHistorySimpleScopeA22Tdd(unittest.TestCase):
    """USNG-ALGB-HISTORY-SIMPLE-SCOPE-A-22: Single-Branch Period-Added Baseline Without Merges Or Renames"""

    def test_period_added_single_branch_baseline(self) -> None:
        """GIVEN a single-branch Git repo with one pre-window commit and two in-window commits,
        WHEN Algorithm B computes period-added totals,
        THEN only in-window lines with the correct AI attribution are counted."""

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo_dir = root / "repo"
            protocol_dir = root / "protocols"
            output_file = root / "out.json"
            repo_dir.mkdir()
            protocol_dir.mkdir()

            repo = GitRepoHarness(repo_dir)

            # Pre-window commit — human lines, should NOT count in period-added
            repo.write("src/base.py", "def base():\n    return 0\n")
            pre_window_rev = repo.commit_all("pre-window", "2026-02-15T09:00:00Z")

            # In-window commit r1 — 2 AI lines
            repo.write("src/model.py", "class Model:\n    def predict(self):\n        return ai_result()\n")
            r1 = repo.commit_all("r1", "2026-03-10T09:00:00Z")

            # In-window commit r2 — 1 human line
            repo.write("src/model.py", "class Model:\n    def predict(self):\n        return ai_result()\n    def label(self):\n        return human_label()\n")
            r2 = repo.commit_all("r2", "2026-03-20T09:00:00Z")

            # Protocol for r1
            protocol_r1 = {
                "protocolName": "generatedTextDesc",
                "protocolVersion": "26.03",
                "codeAgent": "TestAgent",
                "SUMMARY": {"totalCodeLines": 3, "fullGeneratedCodeLines": 2, "partialGeneratedCodeLines": 0},
                "REPOSITORY": {"repoURL": str(repo_dir), "repoBranch": "main", "revisionId": r1},
                "DETAIL": [
                    {
                        "fileName": "src/model.py",
                        "codeLines": [
                            {"lineLocation": 1, "genRatio": 0, "genMethod": "Manual"},
                            {"lineLocation": 2, "genRatio": 100, "genMethod": "vibeCoding"},
                            {"lineLocation": 3, "genRatio": 100, "genMethod": "vibeCoding"},
                        ],
                    }
                ],
            }
            write_revision_protocol(protocol_dir, protocol_r1, repo_dir, r1)

            # Protocol for r2 (lines added by r2: new lines 4-5)
            protocol_r2 = {
                "protocolName": "generatedTextDesc",
                "protocolVersion": "26.03",
                "codeAgent": "TestAgent",
                "SUMMARY": {"totalCodeLines": 5, "fullGeneratedCodeLines": 2, "partialGeneratedCodeLines": 0},
                "REPOSITORY": {"repoURL": str(repo_dir), "repoBranch": "main", "revisionId": r2},
                "DETAIL": [
                    {
                        "fileName": "src/model.py",
                        "codeLines": [
                            {"lineLocation": 4, "genRatio": 0, "genMethod": "Manual"},
                            {"lineLocation": 5, "genRatio": 0, "genMethod": "Manual"},
                        ],
                    }
                ],
            }
            write_revision_protocol(protocol_dir, protocol_r2, repo_dir, r2)

            query = {
                "vcsType": "git",
                "repoURL": str(repo_dir),
                "repoBranch": "main",
                "startTime": "2026-03-01",
                "endTime": "2026-03-31",
                "scope": "A",
                "metric": "period_added_ai_ratio",
            }

            run_cli(
                repo_dir,
                output_file,
                protocol_dir,
                query,
                extra_args=["--algorithm", "B"],
            )

            result = load_json(output_file)
            # Only in-window lines count (from r1 and r2):
            # r1: "class Model:" (0), "    def predict(self):" (100), "        return ai_result()" (100) → total=3, full=2
            # r2: "    def label(self):" (0), "        return human_label()" (0) → total=2, full=0
            # pre-window "src/base.py" → excluded (out of window)
            # net period-added: totalCodeLines=5, fullGeneratedCodeLines=2, partialGeneratedCodeLines=0
            self.assertEqual(result["SUMMARY"]["totalCodeLines"], 5)
            self.assertEqual(result["SUMMARY"]["fullGeneratedCodeLines"], 2)
            self.assertEqual(result["SUMMARY"]["partialGeneratedCodeLines"], 0)


if __name__ == "__main__":
    unittest.main()
