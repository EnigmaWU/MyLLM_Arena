import subprocess
import tempfile
import unittest
from pathlib import Path

from tests.cli_test_support import GitRepoHarness, PROJECT_ROOT, UTILITY_PATH, load_json, run_cli, write_revision_protocol
from tests.test_us12_many_merged_branches_preserve_attribution_tdd import TestUs12ManyMergedBranchesPreserveAttributionTdd


TESTDATA_DIR = Path(__file__).resolve().parent.parent / "testdata"


class TestUs8Us12AlgorithmBRegressionTdd(unittest.TestCase):
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

    def test_algorithm_b_merge_cluster_matches_expected_results(self) -> None:
        for fixture_name in [
            "us8_merge_commit_preserves_attribution",
            "us12_many_merged_branches_preserve_attribution",
        ]:
            with self.subTest(fixture=fixture_name):
                fixture_dir = TESTDATA_DIR / fixture_name
                expected_result = load_json(fixture_dir / "expected_result.json")
                actual_result = self._run_fixture(fixture_name)
                self.assertEqual(actual_result, expected_result)

    def test_algorithm_b_merge_cluster_matches_expected_results_on_real_local_git_replay(self) -> None:
        us8_fixture_dir = TESTDATA_DIR / "us8_merge_commit_preserves_attribution"
        us8_query = load_json(us8_fixture_dir / "query.json")
        us8_expected = load_json(us8_fixture_dir / "expected_result.json")
        us8_revision_protocol_r1 = load_json(us8_fixture_dir / "01_genCodeDesc.json")
        us8_revision_protocol_r2 = load_json(us8_fixture_dir / "02_genCodeDesc.json")
        us8_revision_protocol_r3 = load_json(us8_fixture_dir / "03_genCodeDesc.json")
        us8_revision_protocol_r4 = load_json(us8_fixture_dir / "04_genCodeDesc.json")

        with tempfile.TemporaryDirectory() as temp_dir:
            root_dir = Path(temp_dir)
            repo_dir = root_dir / "repo"
            protocol_dir = root_dir / "protocols"
            output_file = root_dir / "out.json"

            repo_dir.mkdir()
            protocol_dir.mkdir()

            repo = GitRepoHarness(repo_dir)
            repo.write(
                "src/merge_case.py",
                "base = x\n"
                "spacer = x\n"
                "value = x + 1\n"
                "return base + value + spacer\n",
            )
            revision_id_r1 = repo.commit_all("us8-r1", "2026-03-01T09:00:00Z")

            repo.checkout_new_branch("feature-ai")
            repo.write(
                "src/merge_case.py",
                "base = x\n"
                "spacer = x\n"
                "value = x * 2\n"
                "return base + value + spacer\n",
            )
            revision_id_r2 = repo.commit_all("us8-r2", "2026-03-10T09:00:00Z")

            repo.checkout("main")
            repo.write(
                "src/merge_case.py",
                "base = max(x, 0)\n"
                "spacer = x\n"
                "value = x + 1\n"
                "return base + value + spacer\n",
            )
            revision_id_r3 = repo.commit_all("us8-r3", "2026-03-12T09:00:00Z")

            revision_id_r4 = repo.merge_no_ff("feature-ai", "us8-r4", "2026-03-20T09:00:00Z")

            write_revision_protocol(protocol_dir, us8_revision_protocol_r1, repo_dir, revision_id_r1)
            write_revision_protocol(protocol_dir, us8_revision_protocol_r2, repo_dir, revision_id_r2)
            write_revision_protocol(protocol_dir, us8_revision_protocol_r3, repo_dir, revision_id_r3)
            write_revision_protocol(protocol_dir, us8_revision_protocol_r4, repo_dir, revision_id_r4)

            run_cli(
                repo_dir,
                output_file,
                protocol_dir,
                us8_query,
                extra_args=["--algorithm", "B", "--metric", "live_changed_source_ratio"],
            )

            actual_result = load_json(output_file)
            us8_expected["REPOSITORY"]["repoURL"] = str(repo_dir)
            us8_expected["REPOSITORY"]["revisionId"] = revision_id_r4
            self.assertEqual(actual_result, us8_expected)

    def test_algorithm_b_us12_branch_heavy_real_local_git_replay_matches_expected_result(self) -> None:
        us12_builder = TestUs12ManyMergedBranchesPreserveAttributionTdd(methodName="runTest")
        us12_query = us12_builder._query()
        expected_result = load_json(TESTDATA_DIR / "us12_many_merged_branches_preserve_attribution" / "expected_result.json")

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_dir, protocol_dir, output_file, revision_ids = us12_builder._build_history(Path(temp_dir))

            run_cli(
                repo_dir,
                output_file,
                protocol_dir,
                us12_query,
                extra_args=["--algorithm", "B", "--metric", "live_changed_source_ratio"],
            )

            actual_result = load_json(output_file)
            expected_result["REPOSITORY"]["repoURL"] = str(repo_dir)
            expected_result["REPOSITORY"]["revisionId"] = revision_ids["r15"]

            self.assertEqual(actual_result, expected_result)