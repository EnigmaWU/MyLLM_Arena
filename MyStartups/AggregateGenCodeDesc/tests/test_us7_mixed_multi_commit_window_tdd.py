import tempfile
import unittest
from pathlib import Path

from tests.cli_test_support import GitRepoHarness, UTILITY_PATH, load_json, run_cli, write_revision_protocol
from tests.log_assertions import assert_live_line_log, assert_log_contains_all, assert_log_contains_none


FIXTURE_DIR = Path(__file__).resolve().parent.parent / "testdata" / "us7_mixed_multi_commit_window"


class TestUs7MixedMultiCommitWindowTdd(unittest.TestCase):
    maxDiff = None

    def test_cli_matches_us7_expected_result_for_mixed_multi_commit_window(self) -> None:
        self.assertTrue(
            UTILITY_PATH.exists(),
            f"Expected CLI utility at {UTILITY_PATH} for US-7 end-to-end execution.",
        )

        query = load_json(FIXTURE_DIR / "query.json")
        expected_result = load_json(FIXTURE_DIR / "expected_result.json")
        revision_protocol_r1 = load_json(FIXTURE_DIR / "01_genCodeDesc.json")
        revision_protocol_r2 = load_json(FIXTURE_DIR / "02_genCodeDesc.json")
        revision_protocol_r3 = load_json(FIXTURE_DIR / "03_genCodeDesc.json")
        revision_protocol_r4 = load_json(FIXTURE_DIR / "04_genCodeDesc.json")

        with tempfile.TemporaryDirectory() as temp_dir:
            root_dir = Path(temp_dir)
            repo_dir = root_dir / "repo"
            protocol_dir = root_dir / "protocols"
            output_file = root_dir / "out.json"

            repo_dir.mkdir()
            protocol_dir.mkdir()

            # WHY: US-7 is about several ownership transitions inside one
            # query window, so the history intentionally mixes full AI lines,
            # later human cleanup, and a newer partial-AI rewrite.
            repo = GitRepoHarness(repo_dir)
            repo.write(
                "src/mixed.py",
                "first = seed\n"
                "second = seed + 1\n"
                "third = seed + 2\n"
                "fourth = seed + 3\n"
                "fifth = seed + 4\n",
            )
            revision_id_r1 = repo.commit_all("us7-r1", "2026-03-03T09:00:00Z")

            repo.write(
                "src/mixed.py",
                "first = seed\n"
                "second = seed + 1\n"
                "third = seed * 2\n"
                "fourth = seed * 3\n"
                "helper = seed * 4\n"
                "fifth = seed + 4\n",
            )
            revision_id_r2 = repo.commit_all("us7-r2", "2026-03-08T09:00:00Z")

            repo.write(
                "src/mixed.py",
                "first = seed\n"
                "second = seed + 1\n"
                "third = seed * 2\n"
                "fourth = normalize(seed)\n"
                "fifth = seed + 4\n",
            )
            revision_id_r3 = repo.commit_all("us7-r3", "2026-03-15T09:00:00Z")

            repo.write(
                "src/mixed.py",
                "first = seed\n"
                "second = seed + 1\n"
                "third = seed * 2\n"
                "fourth = normalize(seed)\n"
                "fifth = seed + helper(seed)\n",
            )
            revision_id_r4 = repo.commit_all("us7-r4", "2026-03-23T09:00:00Z")

            write_revision_protocol(protocol_dir, revision_protocol_r1, repo_dir, revision_id_r1)
            write_revision_protocol(protocol_dir, revision_protocol_r2, repo_dir, revision_id_r2)
            write_revision_protocol(protocol_dir, revision_protocol_r3, repo_dir, revision_id_r3)
            write_revision_protocol(protocol_dir, revision_protocol_r4, repo_dir, revision_id_r4)

            run_cli(repo_dir, output_file, protocol_dir, query)

            actual_result = load_json(output_file)
            expected_result["REPOSITORY"]["repoURL"] = str(repo_dir)
            expected_result["REPOSITORY"]["revisionId"] = revision_id_r4

            self.assertEqual(actual_result, expected_result)

    def test_cli_emits_debug_logs_for_us7_when_enabled(self) -> None:
        query = load_json(FIXTURE_DIR / "query.json")
        revision_protocol_r1 = load_json(FIXTURE_DIR / "01_genCodeDesc.json")
        revision_protocol_r2 = load_json(FIXTURE_DIR / "02_genCodeDesc.json")
        revision_protocol_r3 = load_json(FIXTURE_DIR / "03_genCodeDesc.json")
        revision_protocol_r4 = load_json(FIXTURE_DIR / "04_genCodeDesc.json")

        with tempfile.TemporaryDirectory() as temp_dir:
            root_dir = Path(temp_dir)
            repo_dir = root_dir / "repo"
            protocol_dir = root_dir / "protocols"
            output_file = root_dir / "out.json"

            repo_dir.mkdir()
            protocol_dir.mkdir()

            repo = GitRepoHarness(repo_dir)
            repo.write(
                "src/mixed.py",
                "first = seed\n"
                "second = seed + 1\n"
                "third = seed + 2\n"
                "fourth = seed + 3\n"
                "fifth = seed + 4\n",
            )
            revision_id_r1 = repo.commit_all("us7-r1", "2026-03-03T09:00:00Z")

            repo.write(
                "src/mixed.py",
                "first = seed\n"
                "second = seed + 1\n"
                "third = seed * 2\n"
                "fourth = seed * 3\n"
                "helper = seed * 4\n"
                "fifth = seed + 4\n",
            )
            revision_id_r2 = repo.commit_all("us7-r2", "2026-03-08T09:00:00Z")

            repo.write(
                "src/mixed.py",
                "first = seed\n"
                "second = seed + 1\n"
                "third = seed * 2\n"
                "fourth = normalize(seed)\n"
                "fifth = seed + 4\n",
            )
            revision_id_r3 = repo.commit_all("us7-r3", "2026-03-15T09:00:00Z")

            repo.write(
                "src/mixed.py",
                "first = seed\n"
                "second = seed + 1\n"
                "third = seed * 2\n"
                "fourth = normalize(seed)\n"
                "fifth = seed + helper(seed)\n",
            )
            revision_id_r4 = repo.commit_all("us7-r4", "2026-03-23T09:00:00Z")

            write_revision_protocol(protocol_dir, revision_protocol_r1, repo_dir, revision_id_r1)
            write_revision_protocol(protocol_dir, revision_protocol_r2, repo_dir, revision_id_r2)
            write_revision_protocol(protocol_dir, revision_protocol_r3, repo_dir, revision_id_r3)
            write_revision_protocol(protocol_dir, revision_protocol_r4, repo_dir, revision_id_r4)

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
                relative_path="src/mixed.py",
                final_line=1,
                origin_file="src/mixed.py",
                origin_line=1,
                revision_id=revision_id_r1,
                classification="human/unattributed",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/mixed.py",
                final_line=2,
                origin_file="src/mixed.py",
                origin_line=2,
                revision_id=revision_id_r1,
                classification="human/unattributed",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/mixed.py",
                final_line=3,
                origin_file="src/mixed.py",
                origin_line=3,
                revision_id=revision_id_r2,
                classification="100%-ai",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/mixed.py",
                final_line=4,
                origin_file="src/mixed.py",
                origin_line=4,
                revision_id=revision_id_r3,
                classification="human/unattributed",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/mixed.py",
                final_line=5,
                origin_file="src/mixed.py",
                origin_line=5,
                revision_id=revision_id_r4,
                classification="60%-ai",
            )

    def test_cli_info_logging_focuses_on_live_line_aggregation_progress_for_us7(self) -> None:
        query = load_json(FIXTURE_DIR / "query.json")
        revision_protocol_r1 = load_json(FIXTURE_DIR / "01_genCodeDesc.json")
        revision_protocol_r2 = load_json(FIXTURE_DIR / "02_genCodeDesc.json")
        revision_protocol_r3 = load_json(FIXTURE_DIR / "03_genCodeDesc.json")
        revision_protocol_r4 = load_json(FIXTURE_DIR / "04_genCodeDesc.json")

        with tempfile.TemporaryDirectory() as temp_dir:
            root_dir = Path(temp_dir)
            repo_dir = root_dir / "repo"
            protocol_dir = root_dir / "protocols"
            output_file = root_dir / "out.json"

            repo_dir.mkdir()
            protocol_dir.mkdir()

            repo = GitRepoHarness(repo_dir)
            repo.write(
                "src/mixed.py",
                "first = seed\n"
                "second = seed + 1\n"
                "third = seed + 2\n"
                "fourth = seed + 3\n"
                "fifth = seed + 4\n",
            )
            revision_id_r1 = repo.commit_all("us7-r1", "2026-03-03T09:00:00Z")

            repo.write(
                "src/mixed.py",
                "first = seed\n"
                "second = seed + 1\n"
                "third = seed * 2\n"
                "fourth = seed * 3\n"
                "helper = seed * 4\n"
                "fifth = seed + 4\n",
            )
            repo.commit_all("us7-r2", "2026-03-08T09:00:00Z")

            repo.write(
                "src/mixed.py",
                "first = seed\n"
                "second = seed + 1\n"
                "third = seed * 2\n"
                "fourth = normalize(seed)\n"
                "fifth = seed + 4\n",
            )
            revision_id_r3 = repo.commit_all("us7-r3", "2026-03-15T09:00:00Z")

            revision_id_r4 = repo.commit_all("us7-r4", "2026-03-23T09:00:00Z") if False else None
            repo.write(
                "src/mixed.py",
                "first = seed\n"
                "second = seed + 1\n"
                "third = seed * 2\n"
                "fourth = normalize(seed)\n"
                "fifth = seed + helper(seed)\n",
            )
            revision_id_r4 = repo.commit_all("us7-r4", "2026-03-23T09:00:00Z")

            write_revision_protocol(protocol_dir, revision_protocol_r1, repo_dir, revision_id_r1)
            write_revision_protocol(protocol_dir, revision_protocol_r2, repo_dir, repo.commit_ids["us7-r2"])
            write_revision_protocol(protocol_dir, revision_protocol_r3, repo_dir, revision_id_r3)
            write_revision_protocol(protocol_dir, revision_protocol_r4, repo_dir, revision_id_r4)

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
                    "LiveLine src/mixed.py:1 aggregate",
                    "LiveLine src/mixed.py:2 aggregate",
                    "LiveLine src/mixed.py:3 aggregate",
                    "LiveLine src/mixed.py:4 aggregate",
                    "LiveLine src/mixed.py:5 aggregate",
                ],
            )
            assert_log_contains_none(
                self,
                result.stderr,
                [
                    "Loaded genCodeDesc for revision",
                    "best_effort_transition=",
                ],
            )


if __name__ == "__main__":
    unittest.main()