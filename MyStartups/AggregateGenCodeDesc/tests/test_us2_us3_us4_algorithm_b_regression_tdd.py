import unittest
from pathlib import Path
import subprocess
import tempfile

from tests.cli_test_support import GitRepoHarness, PROJECT_ROOT, UTILITY_PATH, load_json, run_cli, write_revision_protocol


TESTDATA_DIR = Path(__file__).resolve().parent.parent / "testdata"


class TestUs2Us3Us4AlgorithmBRegressionTdd(unittest.TestCase):
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

    def test_algorithm_b_rewrite_and_deletion_cluster_matches_expected_results(self) -> None:
        for fixture_name in [
            "us2_human_overwrites_ai_live_changed",
            "us3_ai_overwrites_human_live_changed",
            "us4_deleted_lines_excluded",
        ]:
            with self.subTest(fixture=fixture_name):
                fixture_dir = TESTDATA_DIR / fixture_name
                expected_result = load_json(fixture_dir / "expected_result.json")
                actual_result = self._run_fixture(fixture_name)
                self.assertEqual(actual_result, expected_result)

    def test_algorithm_b_rewrite_and_deletion_cluster_matches_expected_results_on_real_local_git_replay(self) -> None:
        scenarios = [
            {
                "fixture_name": "us2_human_overwrites_ai_live_changed",
                "file_path": "src/normalize.py",
                "revisions": [
                    (
                        "01_genCodeDesc.json",
                        "us2-r1",
                        "2026-03-10T09:00:00Z",
                        "value = raw.strip()\nvalue = value.lower()\nresult = value\n",
                    ),
                    (
                        "02_genCodeDesc.json",
                        "us2-r2",
                        "2026-03-20T09:00:00Z",
                        "value = raw.strip()\nvalue = raw.casefold()\nresult = value\n",
                    ),
                ],
            },
            {
                "fixture_name": "us3_ai_overwrites_human_live_changed",
                "file_path": "src/score.py",
                "revisions": [
                    (
                        "01_genCodeDesc.json",
                        "us3-r1",
                        "2026-03-05T09:00:00Z",
                        "score = base\nscore = score + 1\nreturn score\n",
                    ),
                    (
                        "02_genCodeDesc.json",
                        "us3-r2",
                        "2026-03-18T09:00:00Z",
                        "score = base\nscore = score * 2\nreturn max(score, 0)\n",
                    ),
                ],
            },
            {
                "fixture_name": "us4_deleted_lines_excluded",
                "file_path": "src/temp_rules.py",
                "revisions": [
                    (
                        "01_genCodeDesc.json",
                        "us4-r1",
                        "2026-03-06T09:00:00Z",
                        "rule_one = 'allow'\nrule_two = 'deny'\nrule_three = 'audit'\nrule_four = 'notify'\n",
                    ),
                    (
                        "02_genCodeDesc.json",
                        "us4-r2",
                        "2026-03-21T09:00:00Z",
                        "rule_one = 'allow'\nrule_two = 'deny'\n",
                    ),
                ],
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
                    for protocol_name, commit_label, commit_date, file_content in scenario["revisions"]:
                        repo.write(scenario["file_path"], file_content)
                        revision_id = repo.commit_all(commit_label, commit_date)
                        revision_protocol = load_json(fixture_dir / protocol_name)
                        write_revision_protocol(protocol_dir, revision_protocol, repo_dir, revision_id)
                        final_revision_id = revision_id

                    run_cli(
                        repo_dir,
                        output_file,
                        protocol_dir,
                        query,
                        extra_args=["--algorithm", "B"],
                    )

                    actual_result = load_json(output_file)
                    expected_result["REPOSITORY"]["repoURL"] = str(repo_dir)
                    expected_result["REPOSITORY"]["revisionId"] = final_revision_id
                    self.assertEqual(actual_result, expected_result)