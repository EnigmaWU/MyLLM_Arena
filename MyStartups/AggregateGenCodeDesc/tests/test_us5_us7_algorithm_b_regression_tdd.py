import subprocess
import tempfile
import unittest
from pathlib import Path

from tests.cli_test_support import GitRepoHarness, PROJECT_ROOT, UTILITY_PATH, load_json, run_cli, write_revision_protocol


TESTDATA_DIR = Path(__file__).resolve().parent.parent / "testdata"


class TestUs5Us7AlgorithmBRegressionTdd(unittest.TestCase):
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

    def test_algorithm_b_rename_and_mixed_history_cluster_matches_expected_results(self) -> None:
        for fixture_name in [
            "us5_rename_preserves_lineage",
            "us7_mixed_multi_commit_window",
        ]:
            with self.subTest(fixture=fixture_name):
                fixture_dir = TESTDATA_DIR / fixture_name
                expected_result = load_json(fixture_dir / "expected_result.json")
                actual_result = self._run_fixture(fixture_name)
                self.assertEqual(actual_result, expected_result)

    def test_algorithm_b_rename_and_mixed_history_cluster_matches_expected_results_on_real_local_git_replay(self) -> None:
        scenarios = [
            {
                "fixture_name": "us5_rename_preserves_lineage",
                "file_path": "src/legacy_name.py",
                "revisions": [
                    (
                        "01_genCodeDesc.json",
                        "us5-r1",
                        "2026-03-08T09:00:00Z",
                        "write",
                        "src/legacy_name.py",
                        "def calc(x):\n    value = x * 2\n    return value\n",
                    ),
                    (
                        "02_genCodeDesc.json",
                        "us5-r2",
                        "2026-03-12T09:00:00Z",
                        "rename",
                        ("src/legacy_name.py", "src/current_name.py"),
                        None,
                    ),
                ],
                "final_path": "src/current_name.py",
            },
            {
                "fixture_name": "us7_mixed_multi_commit_window",
                "file_path": "src/mixed.py",
                "revisions": [
                    (
                        "01_genCodeDesc.json",
                        "us7-r1",
                        "2026-03-03T09:00:00Z",
                        "write",
                        "src/mixed.py",
                        "first = seed\nsecond = seed + 1\nthird = seed + 2\nfourth = seed + 3\nfifth = seed + 4\n",
                    ),
                    (
                        "02_genCodeDesc.json",
                        "us7-r2",
                        "2026-03-08T09:00:00Z",
                        "write",
                        "src/mixed.py",
                        "first = seed\nsecond = seed + 1\nthird = seed * 2\nfourth = seed * 3\nhelper = seed * 4\nfifth = seed + 4\n",
                    ),
                    (
                        "03_genCodeDesc.json",
                        "us7-r3",
                        "2026-03-15T09:00:00Z",
                        "write",
                        "src/mixed.py",
                        "first = seed\nsecond = seed + 1\nthird = seed * 2\nfourth = normalize(seed)\nfifth = seed + 4\n",
                    ),
                    (
                        "04_genCodeDesc.json",
                        "us7-r4",
                        "2026-03-23T09:00:00Z",
                        "write",
                        "src/mixed.py",
                        "first = seed\nsecond = seed + 1\nthird = seed * 2\nfourth = normalize(seed)\nfifth = seed + helper(seed)\n",
                    ),
                ],
                "final_path": "src/mixed.py",
            },
        ]

        for scenario in scenarios:
            with self.subTest(fixture=scenario["fixture_name"]):
                fixture_dir = TESTDATA_DIR / scenario["fixture_name"]
                query = load_json(fixture_dir / "query.json")
                expected_result = load_json(fixture_dir / "expected_result.json")

                with tempfile.TemporaryDirectory() as temp_dir:
                    root_dir = Path(temp_dir)
                    repo_dir = root_dir / "repo"
                    protocol_dir = root_dir / "protocols"
                    output_file = root_dir / "out.json"

                    repo_dir.mkdir()
                    protocol_dir.mkdir()

                    repo = GitRepoHarness(repo_dir)
                    final_revision_id = ""
                    for protocol_name, commit_label, commit_date, action, action_target, file_content in scenario["revisions"]:
                        if action == "write":
                            repo.write(action_target, file_content)
                        elif action == "rename":
                            old_path, new_path = action_target
                            repo.rename(old_path, new_path)
                        else:
                            raise AssertionError(f"Unsupported scenario action: {action}")

                        revision_id = repo.commit_all(commit_label, commit_date)
                        revision_protocol = load_json(fixture_dir / protocol_name)
                        write_revision_protocol(protocol_dir, revision_protocol, repo_dir, revision_id)
                        final_revision_id = revision_id

                    run_cli(
                        repo_dir,
                        output_file,
                        protocol_dir,
                        query,
                        extra_args=["--algorithm", "B", "--metric", "live_changed_source_ratio"],
                    )

                    actual_result = load_json(output_file)
                    expected_result["REPOSITORY"]["repoURL"] = str(repo_dir)
                    expected_result["REPOSITORY"]["revisionId"] = final_revision_id
                    self.assertEqual(actual_result, expected_result)