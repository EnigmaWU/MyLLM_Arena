import subprocess
import tempfile
import unittest
from pathlib import Path

from tests.cli_test_support import PROJECT_ROOT, UTILITY_PATH, load_json


FIXTURE_GIT_DIR = Path(__file__).resolve().parent.parent / "testdata" / "us1_live_changed_source_ratio"
FIXTURE_SVN_DIR = Path(__file__).resolve().parent.parent / "testdata" / "us1_live_changed_source_ratio_svn"


class TestUs9AlgorithmBContractParityTdd(unittest.TestCase):
    maxDiff = None

    def _normalized_contract(self, result: dict) -> dict:
        return {
            "protocolName": result["protocolName"],
            "protocolVersion": result["protocolVersion"],
            "SUMMARY": result["SUMMARY"],
        }

    def _run_algorithm_b_cell(self, fixture_dir: Path) -> dict:
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
                    "--outputFile",
                    str(output_file),
                    "--genCodeDescSetDir",
                    str(fixture_dir),
                    "--commitDiffSetDir",
                    str(fixture_dir / "commitDiffSet"),
                ],
                cwd=PROJECT_ROOT,
                text=True,
                capture_output=True,
                check=True,
            )
            return load_json(output_file)

    def test_algorithm_b_git_and_svn_supported_cells_share_same_observable_contract(self) -> None:
        expected_git = load_json(FIXTURE_GIT_DIR / "expected_result.json")
        expected_svn = load_json(FIXTURE_SVN_DIR / "expected_result.json")
        expected_contract = self._normalized_contract(expected_git)

        self.assertEqual(expected_contract, self._normalized_contract(expected_svn))

        algorithm_b_git = self._run_algorithm_b_cell(FIXTURE_GIT_DIR)
        algorithm_b_svn = self._run_algorithm_b_cell(FIXTURE_SVN_DIR)

        self.assertEqual(self._normalized_contract(algorithm_b_git), expected_contract)
        self.assertEqual(self._normalized_contract(algorithm_b_svn), expected_contract)
        self.assertEqual(self._normalized_contract(algorithm_b_git), self._normalized_contract(algorithm_b_svn))

        self.assertEqual(algorithm_b_git["REPOSITORY"]["vcsType"], "git")
        self.assertEqual(algorithm_b_svn["REPOSITORY"]["vcsType"], "svn")


if __name__ == "__main__":
    unittest.main()