import subprocess
import tempfile
import unittest
from pathlib import Path

from tests.cli_test_support import PROJECT_ROOT, UTILITY_PATH, load_json, run_cli
from tests.test_us10_large_repository_snapshot_tdd import TestUs10LargeRepositorySnapshotTdd
from tests.test_us11_deep_history_preserves_attribution_tdd import TestUs11DeepHistoryPreservesAttributionTdd


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

    def test_algorithm_b_scale_and_deep_history_cluster_matches_expected_results_on_real_local_git_replay(self) -> None:
        scenarios = [
            (
                "us10_large_repository_snapshot",
                TestUs10LargeRepositorySnapshotTdd(methodName="runTest"),
                "_build_us10_repo",
            ),
            (
                "us11_deep_history_preserves_attribution",
                TestUs11DeepHistoryPreservesAttributionTdd(methodName="runTest"),
                "_build_us11_repo",
            ),
        ]

        for fixture_name, builder, builder_method_name in scenarios:
            with self.subTest(fixture=fixture_name):
                fixture_dir = TESTDATA_DIR / fixture_name
                query = load_json(fixture_dir / "query.json")
                expected_result = load_json(fixture_dir / "expected_result.json")

                with tempfile.TemporaryDirectory() as temp_dir:
                    build_repo = getattr(builder, builder_method_name)
                    repo_dir, protocol_dir, output_file, revision_ids = build_repo(Path(temp_dir))

                    run_cli(
                        repo_dir,
                        output_file,
                        protocol_dir,
                        query,
                        extra_args=["--algorithm", "B"],
                    )

                    actual_result = load_json(output_file)
                    expected_result["REPOSITORY"]["repoURL"] = str(repo_dir)
                    expected_result["REPOSITORY"]["revisionId"] = revision_ids[sorted(revision_ids.keys())[-1]]
                    self.assertEqual(actual_result, expected_result)