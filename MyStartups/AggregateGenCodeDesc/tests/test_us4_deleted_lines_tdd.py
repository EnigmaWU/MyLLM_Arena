import tempfile
import unittest
from pathlib import Path
import subprocess

from tests.cli_test_support import GitRepoHarness, PROJECT_ROOT, UTILITY_PATH, load_json, run_cli, write_revision_protocol
from tests.log_assertions import assert_live_line_log, assert_log_contains_all, assert_log_contains_none


FIXTURE_DIR = Path(__file__).resolve().parent.parent / "testdata" / "us4_deleted_lines_excluded"


class TestUs4DeletedLinesTdd(unittest.TestCase):
    maxDiff = None

    def test_cli_matches_us4_expected_result_for_narrow_algorithm_b_fixture_path(self) -> None:
        query = load_json(FIXTURE_DIR / "query.json")
        expected_result = load_json(FIXTURE_DIR / "expected_result.json")

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
                    str(FIXTURE_DIR),
                    "--commitDiffSetDir",
                    str(FIXTURE_DIR / "commitDiffSet"),
                ],
                cwd=PROJECT_ROOT,
                text=True,
                capture_output=True,
                check=True,
            )

            actual_result = load_json(output_file)
            self.assertEqual(actual_result, expected_result)

    def test_cli_matches_us4_expected_result_when_ai_lines_are_deleted_before_endtime(self) -> None:
        self.assertTrue(
            UTILITY_PATH.exists(),
            f"Expected CLI utility at {UTILITY_PATH} for US-4 end-to-end execution.",
        )

        query = load_json(FIXTURE_DIR / "query.json")
        expected_result = load_json(FIXTURE_DIR / "expected_result.json")
        revision_protocol_r1 = load_json(FIXTURE_DIR / "01_genCodeDesc.json")
        revision_protocol_r2 = load_json(FIXTURE_DIR / "02_genCodeDesc.json")

        with tempfile.TemporaryDirectory() as temp_dir:
            root_dir = Path(temp_dir)
            repo_dir = root_dir / "repo"
            protocol_dir = root_dir / "protocols"
            output_file = root_dir / "out.json"

            repo_dir.mkdir()
            protocol_dir.mkdir()

            # WHY: US-4 is about the final live snapshot, so the test uses a
            # later commit that deletes previously AI-attributed lines and then
            # checks that only the surviving lines are aggregated.
            repo = GitRepoHarness(repo_dir)
            repo.write(
                "src/temp_rules.py",
                "rule_one = 'allow'\n"
                "rule_two = 'deny'\n"
                "rule_three = 'audit'\n"
                "rule_four = 'notify'\n",
            )
            revision_id_r1 = repo.commit_all("us4-r1", "2026-03-06T09:00:00Z")

            repo.write(
                "src/temp_rules.py",
                "rule_one = 'allow'\n"
                "rule_two = 'deny'\n",
            )
            revision_id_r2 = repo.commit_all("us4-r2", "2026-03-21T09:00:00Z")

            write_revision_protocol(protocol_dir, revision_protocol_r1, repo_dir, revision_id_r1)
            write_revision_protocol(protocol_dir, revision_protocol_r2, repo_dir, revision_id_r2)

            run_cli(repo_dir, output_file, protocol_dir, query)

            actual_result = load_json(output_file)
            expected_result["REPOSITORY"]["repoURL"] = str(repo_dir)
            expected_result["REPOSITORY"]["revisionId"] = revision_id_r2

            self.assertEqual(actual_result, expected_result)

    def test_cli_emits_debug_logs_for_us4_when_enabled(self) -> None:
        query = load_json(FIXTURE_DIR / "query.json")
        revision_protocol_r1 = load_json(FIXTURE_DIR / "01_genCodeDesc.json")
        revision_protocol_r2 = load_json(FIXTURE_DIR / "02_genCodeDesc.json")

        with tempfile.TemporaryDirectory() as temp_dir:
            root_dir = Path(temp_dir)
            repo_dir = root_dir / "repo"
            protocol_dir = root_dir / "protocols"
            output_file = root_dir / "out.json"

            repo_dir.mkdir()
            protocol_dir.mkdir()

            repo = GitRepoHarness(repo_dir)
            repo.write(
                "src/temp_rules.py",
                "rule_one = 'allow'\n"
                "rule_two = 'deny'\n"
                "rule_three = 'audit'\n"
                "rule_four = 'notify'\n",
            )
            revision_id_r1 = repo.commit_all("us4-r1", "2026-03-06T09:00:00Z")

            repo.write(
                "src/temp_rules.py",
                "rule_one = 'allow'\n"
                "rule_two = 'deny'\n",
            )
            revision_id_r2 = repo.commit_all("us4-r2", "2026-03-21T09:00:00Z")

            write_revision_protocol(protocol_dir, revision_protocol_r1, repo_dir, revision_id_r1)
            write_revision_protocol(protocol_dir, revision_protocol_r2, repo_dir, revision_id_r2)

            result = run_cli(
                repo_dir,
                output_file,
                protocol_dir,
                query,
                extra_args=["--logLevel", "debug"],
            )

            assert_log_contains_all(
                self,
                result.stderr,
                [
                    "Starting analysis",
                    "Loaded genCodeDesc for revision",
                    "Finished analysis",
                ],
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/temp_rules.py",
                final_line=1,
                origin_file="src/temp_rules.py",
                origin_line=1,
                revision_id=revision_id_r1,
                classification="100%-ai",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/temp_rules.py",
                final_line=2,
                origin_file="src/temp_rules.py",
                origin_line=2,
                revision_id=revision_id_r1,
                classification="100%-ai",
            )
            self.assertNotIn("LiveLine src/temp_rules.py:3 aggregate", result.stderr)
            self.assertNotIn("LiveLine src/temp_rules.py:4 aggregate", result.stderr)

    def test_cli_info_logging_focuses_on_surviving_live_lines_for_us4(self) -> None:
        query = load_json(FIXTURE_DIR / "query.json")
        revision_protocol_r1 = load_json(FIXTURE_DIR / "01_genCodeDesc.json")
        revision_protocol_r2 = load_json(FIXTURE_DIR / "02_genCodeDesc.json")

        with tempfile.TemporaryDirectory() as temp_dir:
            root_dir = Path(temp_dir)
            repo_dir = root_dir / "repo"
            protocol_dir = root_dir / "protocols"
            output_file = root_dir / "out.json"

            repo_dir.mkdir()
            protocol_dir.mkdir()

            repo = GitRepoHarness(repo_dir)
            repo.write(
                "src/temp_rules.py",
                "rule_one = 'allow'\n"
                "rule_two = 'deny'\n"
                "rule_three = 'audit'\n"
                "rule_four = 'notify'\n",
            )
            revision_id_r1 = repo.commit_all("us4-r1", "2026-03-06T09:00:00Z")

            repo.write(
                "src/temp_rules.py",
                "rule_one = 'allow'\n"
                "rule_two = 'deny'\n",
            )
            revision_id_r2 = repo.commit_all("us4-r2", "2026-03-21T09:00:00Z")

            write_revision_protocol(protocol_dir, revision_protocol_r1, repo_dir, revision_id_r1)
            write_revision_protocol(protocol_dir, revision_protocol_r2, repo_dir, revision_id_r2)

            result = run_cli(
                repo_dir,
                output_file,
                protocol_dir,
                query,
                extra_args=["--logLevel", "info"],
            )

            assert_log_contains_all(
                self,
                result.stderr,
                [
                    "Starting analysis",
                    "LiveLine src/temp_rules.py:1 aggregate",
                    "LiveLine src/temp_rules.py:2 aggregate",
                ],
            )
            assert_log_contains_none(
                self,
                result.stderr,
                [
                    "Loaded genCodeDesc for revision",
                    "best_effort_transition=",
                    "LiveLine src/temp_rules.py:3 aggregate",
                    "LiveLine src/temp_rules.py:4 aggregate",
                ],
            )


if __name__ == "__main__":
    unittest.main()