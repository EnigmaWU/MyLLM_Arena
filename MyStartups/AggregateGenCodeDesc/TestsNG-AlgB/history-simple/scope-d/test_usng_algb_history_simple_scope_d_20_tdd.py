import subprocess
import tempfile
import unittest
from pathlib import Path

from tests.cli_test_support import PROJECT_ROOT, UTILITY_PATH, build_query_args_cli_args, load_json


FIXTURE_GIT_DIR = Path(__file__).resolve().parents[3] / "TestdataNG-AlgB" / "history-simple" / "scope-d" / "20" / "git" / "default"
FIXTURE_SVN_DIR = Path(__file__).resolve().parents[3] / "TestdataNG-AlgB" / "history-simple" / "scope-d" / "20" / "svn" / "default"


class TestUsngAlgbHistorySimpleScopeD20Tdd(unittest.TestCase):
    """USNG-ALGB-HISTORY-SIMPLE-SCOPE-D-20: Algorithm B Must Support Scope D"""

    maxDiff = None

    def _run_cli(self, fixture_dir: Path) -> dict:
        query = load_json(fixture_dir / "query.json")

        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "out.json"
            subprocess.run(
                [
                    "python3",
                    str(UTILITY_PATH),
                    "--vcsType",
                    query["vcsType"],
                    "--repoURL",
                    query["repoURL"],
                    "--repoBranch",
                    query["repoBranch"],
                    "--startTime",
                    query["startTime"],
                    "--endTime",
                    query["endTime"],
                    "--algorithm",
                    "B",
                    "--scope",
                    query["scope"],
                    *build_query_args_cli_args(query, include_replay_selection=True),
                    "--outputFile",
                    str(output_file),
                    "--commitDiffSetDir",
                    str(fixture_dir / "commitDiffSet"),
                    "--genCodeDescSetDir",
                    str(fixture_dir),
                ],
                cwd=PROJECT_ROOT,
                text=True,
                capture_output=True,
                check=True,
            )
            return load_json(output_file)

    def test_cli_matches_git_expected_result_both_file_families_replayed(self) -> None:
        expected_result = load_json(FIXTURE_GIT_DIR / "expected_result.json")
        actual_result = self._run_cli(FIXTURE_GIT_DIR)
        self.assertEqual(actual_result, expected_result)
        # Scope D uses totalCodeLines (not totalDocLines) even for combined result
        self.assertIn("totalCodeLines", actual_result["SUMMARY"])

    def test_cli_matches_svn_expected_result(self) -> None:
        expected_result = load_json(FIXTURE_SVN_DIR / "expected_result.json")
        actual_result = self._run_cli(FIXTURE_SVN_DIR)
        self.assertEqual(actual_result, expected_result)


if __name__ == "__main__":
    unittest.main()
