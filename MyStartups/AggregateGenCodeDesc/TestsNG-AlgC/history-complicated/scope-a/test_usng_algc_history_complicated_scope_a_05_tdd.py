import subprocess
import tempfile
import unittest
from pathlib import Path

from tests.cli_test_support import PROJECT_ROOT, UTILITY_PATH, load_json


FIXTURE_GIT_DIR = Path(__file__).resolve().parents[3] / "TestdataNG-AlgC" / "history-complicated" / "scope-a" / "05" / "git" / "default"
FIXTURE_SVN_DIR = Path(__file__).resolve().parents[3] / "TestdataNG-AlgC" / "history-complicated" / "scope-a" / "05" / "svn" / "default"


class TestUsngAlgcHistoryComplicatedScopeA05Tdd(unittest.TestCase):
    maxDiff = None

    def _run_cli(self, fixture_dir: Path) -> dict:
        query = load_json(fixture_dir / "query.json")

        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "out.json"
            subprocess.run(
                [
                    "python3",
                    str(UTILITY_PATH),
                    "--startTime",
                    query["startTime"],
                    "--endTime",
                    query["endTime"],
                    "--algorithm",
                    "C",
                    "--scope",
                    query["scope"],
                    "--outputFile",
                    str(output_file),
                    "--genCodeDescSetDir",
                    str(fixture_dir),
                ],
                cwd=PROJECT_ROOT,
                text=True,
                capture_output=True,
                check=True,
            )
            return load_json(output_file)

    def test_cli_matches_git_expected_result_when_rename_preserves_lineage(self) -> None:
        expected_result = load_json(FIXTURE_GIT_DIR / "expected_result.json")
        actual_result = self._run_cli(FIXTURE_GIT_DIR)
        self.assertEqual(actual_result, expected_result)

    def test_cli_matches_svn_expected_result_when_rename_preserves_lineage(self) -> None:
        expected_result = load_json(FIXTURE_SVN_DIR / "expected_result.json")
        actual_result = self._run_cli(FIXTURE_SVN_DIR)
        self.assertEqual(actual_result, expected_result)


if __name__ == "__main__":
    unittest.main()
