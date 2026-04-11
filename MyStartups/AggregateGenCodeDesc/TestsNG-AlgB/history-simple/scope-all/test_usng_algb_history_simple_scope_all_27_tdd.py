import subprocess
import tempfile
import unittest
from pathlib import Path

from tests.cli_test_support import GitRepoHarness, load_json, run_cli, write_revision_protocol, PROJECT_ROOT, UTILITY_PATH


class TestUsngAlgbHistorySimpleScopeAll27Tdd(unittest.TestCase):
    """USNG-ALGB-HISTORY-SIMPLE-SCOPE-ALL-27: Algorithm A And Algorithm B Must Produce Identical SUMMARY For Every Scope"""

    def _build_repo_with_protocol(self) -> tuple:
        """Returns (repo_dir_path, protocol_dir_path, commit_id) in a temp context handled by caller."""
        raise NotImplementedError("Use within test method's tempdir context")

    def test_scope_a_parity_between_algorithm_a_and_b(self) -> None:
        """Algorithm A (blame) and Algorithm B (replay) must produce identical SUMMARY for scope A."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo_dir = root / "repo"
            protocol_dir = root / "protocols"
            output_a = root / "out_a.json"
            output_b = root / "out_b.json"
            repo_dir.mkdir()
            protocol_dir.mkdir()

            repo = GitRepoHarness(repo_dir)
            repo.write("src/core.py", "def core():\n    return ai_val()\n")
            r1 = repo.commit_all("r1", "2026-03-10T09:00:00Z")

            protocol = {
                "protocolName": "generatedTextDesc",
                "protocolVersion": "26.03",
                "codeAgent": "TestAgent",
                "SUMMARY": {"totalCodeLines": 2, "fullGeneratedCodeLines": 1, "partialGeneratedCodeLines": 0},
                "REPOSITORY": {"repoURL": str(repo_dir), "repoBranch": "main", "revisionId": r1},
                "DETAIL": [
                    {
                        "fileName": "src/core.py",
                        "codeLines": [
                            {"lineLocation": 1, "genRatio": 0, "genMethod": "Manual"},
                            {"lineLocation": 2, "genRatio": 100, "genMethod": "codeCompletion"},
                        ],
                    }
                ],
            }
            write_revision_protocol(protocol_dir, protocol, repo_dir, r1)

            query = {
                "vcsType": "git",
                "repoURL": str(repo_dir),
                "repoBranch": "main",
                "startTime": "2026-03-01",
                "endTime": "2026-03-31",
                "scope": "A",
            }

            # Run Algorithm A
            run_cli(repo_dir, output_a, protocol_dir, query, extra_args=["--algorithm", "A"])
            # Run Algorithm B
            run_cli(repo_dir, output_b, protocol_dir, query, extra_args=["--algorithm", "B"])

            result_a = load_json(output_a)
            result_b = load_json(output_b)
            self.assertEqual(result_a["SUMMARY"], result_b["SUMMARY"])


if __name__ == "__main__":
    unittest.main()
