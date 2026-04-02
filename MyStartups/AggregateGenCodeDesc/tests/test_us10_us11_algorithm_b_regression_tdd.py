import subprocess
import tempfile
import unittest
from pathlib import Path

from tests.cli_test_support import PROJECT_ROOT, UTILITY_PATH, load_json


TESTDATA_DIR = Path(__file__).resolve().parent.parent / "testdata"


class TestUs10Us11AlgorithmBRegressionTdd(unittest.TestCase):
    def _run_fixture(self, fixture_name: str) -> dict:
        fixture_dir = TESTDATA_DIR / fixture_name
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

    def test_algorithm_b_scale_and_deep_history_cluster_matches_expected_results(self) -> None:
        for fixture_name in [
            "us10_large_repository_snapshot",
            "us11_deep_history_preserves_attribution",
        ]:
            with self.subTest(fixture=fixture_name):
                fixture_dir = TESTDATA_DIR / fixture_name
                expected_result = load_json(fixture_dir / "expected_result.json")
                actual_result = self._run_fixture(fixture_name)
                self.assertEqual(actual_result, expected_result)