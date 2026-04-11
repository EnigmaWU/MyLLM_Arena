import tempfile
import unittest
from pathlib import Path

from tests.cli_test_support import GitRepoHarness, load_json, run_cli, write_revision_protocol


class TestUsngAlgbHistoryComplicatedScopeA23Tdd(unittest.TestCase):
    """USNG-ALGB-HISTORY-COMPLICATED-SCOPE-A-23: Period-Added Accounting With Deletions, Resets, And Mixed Rewrites"""

    def test_deleted_in_window_ai_lines_excluded_from_period_added(self) -> None:
        """GIVEN an AI line is added and then deleted within the same window,
        WHEN Algorithm B computes the period-added result,
        THEN the deleted AI line does not appear in the final period-added total."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo_dir = root / "repo"
            protocol_dir = root / "protocols"
            output_file = root / "out.json"
            repo_dir.mkdir()
            protocol_dir.mkdir()

            repo = GitRepoHarness(repo_dir)

            # r1: adds AI line that will be deleted later
            repo.write("src/work.py", "def work():\n    ai_step = ai_init()\n    return ai_step\n")
            r1 = repo.commit_all("r1", "2026-03-05T09:00:00Z")

            # r2: deletes the AI line and replaces with human
            repo.write("src/work.py", "def work():\n    human_step = manual_init()\n    return human_step\n")
            r2 = repo.commit_all("r2", "2026-03-15T09:00:00Z")

            protocol_r1 = {
                "protocolName": "generatedTextDesc",
                "protocolVersion": "26.03",
                "codeAgent": "TestAgent",
                "SUMMARY": {"totalCodeLines": 3, "fullGeneratedCodeLines": 2, "partialGeneratedCodeLines": 0},
                "REPOSITORY": {"repoURL": str(repo_dir), "repoBranch": "main", "revisionId": r1},
                "DETAIL": [
                    {
                        "fileName": "src/work.py",
                        "codeLines": [
                            {"lineLocation": 1, "genRatio": 0, "genMethod": "Manual"},
                            {"lineLocation": 2, "genRatio": 100, "genMethod": "vibeCoding"},
                            {"lineLocation": 3, "genRatio": 0, "genMethod": "Manual"},
                        ],
                    }
                ],
            }
            write_revision_protocol(protocol_dir, protocol_r1, repo_dir, r1)

            protocol_r2 = {
                "protocolName": "generatedTextDesc",
                "protocolVersion": "26.03",
                "codeAgent": "TestAgent",
                "SUMMARY": {"totalCodeLines": 3, "fullGeneratedCodeLines": 0, "partialGeneratedCodeLines": 0},
                "REPOSITORY": {"repoURL": str(repo_dir), "repoBranch": "main", "revisionId": r2},
                "DETAIL": [
                    {
                        "fileName": "src/work.py",
                        "codeLines": [
                            {"lineLocation": 2, "genRatio": 0, "genMethod": "Manual"},
                            {"lineLocation": 3, "genRatio": 0, "genMethod": "Manual"},
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

            run_cli(repo_dir, output_file, protocol_dir, query, extra_args=["--algorithm", "B"])

            result = load_json(output_file)
            summary = result["SUMMARY"]
            # Surviving lines both from r1 and r2:
            # r1: "def work():" (0) — survives unchanged → origin r1, in window
            # r2: "    human_step = manual_init()" (0) → origin r2, in window
            # r2: "    return human_step" (0) → origin r2, in window
            # The AI line from r1 was deleted in r2 so it does NOT survive
            self.assertEqual(summary["fullGeneratedCodeLines"], 0)
            self.assertEqual(summary["partialGeneratedCodeLines"], 0)

    def test_pre_window_surviving_lines_excluded_from_period_added(self) -> None:
        """GIVEN a file contains pre-window lines that survive unchanged into endTime,
        WHEN Algorithm B computes the period-added result,
        THEN those pre-window surviving lines are excluded from period-added totals."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo_dir = root / "repo"
            protocol_dir = root / "protocols"
            output_file = root / "out.json"
            repo_dir.mkdir()
            protocol_dir.mkdir()

            repo = GitRepoHarness(repo_dir)

            # Pre-window commit
            repo.write("src/base.py", "def base():\n    return old_val()\n")
            repo.commit_all("pre-window", "2026-02-10T09:00:00Z")

            # In-window commit — adds a new AI line
            repo.write("src/base.py", "def base():\n    return old_val()\ndef new_ai():\n    return ai_result()\n")
            r_inwindow = repo.commit_all("in-window", "2026-03-15T09:00:00Z")

            protocol_inwindow = {
                "protocolName": "generatedTextDesc",
                "protocolVersion": "26.03",
                "codeAgent": "TestAgent",
                "SUMMARY": {"totalCodeLines": 2, "fullGeneratedCodeLines": 2, "partialGeneratedCodeLines": 0},
                "REPOSITORY": {"repoURL": str(repo_dir), "repoBranch": "main", "revisionId": r_inwindow},
                "DETAIL": [
                    {
                        "fileName": "src/base.py",
                        "codeLines": [
                            {"lineLocation": 3, "genRatio": 0, "genMethod": "Manual"},
                            {"lineLocation": 4, "genRatio": 100, "genMethod": "codeCompletion"},
                        ],
                    }
                ],
            }
            write_revision_protocol(protocol_dir, protocol_inwindow, repo_dir, r_inwindow)

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
            # Only in-window lines count:
            # "def new_ai():" (0) and "    return ai_result()" (100) → totalCodeLines=2, full=1
            # "def base():" and "    return old_val()" are pre-window → excluded
            self.assertEqual(summary["totalCodeLines"], 2)
            self.assertEqual(summary["fullGeneratedCodeLines"], 1)


if __name__ == "__main__":
    unittest.main()
