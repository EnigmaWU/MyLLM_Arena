import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from tests.cli_test_support import GitRepoHarness, UTILITY_PATH, load_json, run_cli, write_revision_protocol
from tests.log_assertions import assert_live_line_log, assert_log_contains_all, assert_log_contains_none


FIXTURE_DIR = Path(__file__).resolve().parent.parent / "testdata" / "us1_live_changed_source_ratio"


class TestUs1LiveChangedSourceRatioTdd(unittest.TestCase):
    maxDiff = None

    def test_cli_matches_us1_expected_result_for_real_git_repo(self) -> None:
        self.assertTrue(
            UTILITY_PATH.exists(),
            f"Expected CLI utility at {UTILITY_PATH} for US-1 end-to-end execution.",
        )

        query = load_json(FIXTURE_DIR / "query.json")
        expected_result = load_json(FIXTURE_DIR / "expected_result.json")
        revision_protocol = load_json(FIXTURE_DIR / "01_genCodeDesc.json")

        with tempfile.TemporaryDirectory() as temp_dir:
            root_dir = Path(temp_dir)
            repo_dir = root_dir / "repo"
            protocol_dir = root_dir / "protocols"
            output_file = root_dir / "out.json"

            repo_dir.mkdir()
            protocol_dir.mkdir()

            # WHY: this test intentionally creates a real Git history instead of
            # mocking Git output, because the product contract depends on blame
            # behavior and commit timestamps rather than on an internal adapter.
            repo = GitRepoHarness(repo_dir)
            repo.write(
                "src/calc.py",
                "def calc(x):\n"
                "    value = x + 1\n"
                "    boosted = value * 2\n"
                "    return boosted\n",
            )
            revision_id = repo.commit_all("us1-r1", "2026-03-10T09:00:00Z")

            write_revision_protocol(protocol_dir, revision_protocol, repo_dir, revision_id)

            run_cli(repo_dir, output_file, protocol_dir, query)

            actual_result = load_json(output_file)
            expected_result["REPOSITORY"]["repoURL"] = str(repo_dir)
            expected_result["REPOSITORY"]["revisionId"] = revision_id

            self.assertEqual(actual_result, expected_result)

    def test_cli_fails_when_protocol_repository_identity_mismatches_query(self) -> None:
        query = load_json(FIXTURE_DIR / "query.json")
        revision_protocol = load_json(FIXTURE_DIR / "01_genCodeDesc.json")

        with tempfile.TemporaryDirectory() as temp_dir:
            root_dir = Path(temp_dir)
            repo_dir = root_dir / "repo"
            protocol_dir = root_dir / "protocols"
            output_file = root_dir / "out.json"

            repo_dir.mkdir()
            protocol_dir.mkdir()

            repo = GitRepoHarness(repo_dir)
            repo.write(
                "src/calc.py",
                "def calc(x):\n"
                "    value = x + 1\n"
                "    boosted = value * 2\n"
                "    return boosted\n",
            )
            revision_id = repo.commit_all("us1-r1", "2026-03-10T09:00:00Z")

            revision_protocol["REPOSITORY"]["repoURL"] = "https://wrong.example/repo/demo"
            revision_protocol["REPOSITORY"]["repoBranch"] = query["repoBranch"]
            revision_protocol["REPOSITORY"]["revisionId"] = revision_id
            (protocol_dir / f"{revision_id}_genCodeDesc.json").write_text(
                json.dumps(revision_protocol, indent=2),
                encoding="utf-8",
            )

            # WHY: external metadata can be present but still belong to the
            # wrong repository target. This failure case protects against a
            # silent cross-repository join that would produce believable but
            # invalid aggregate numbers.
            with self.assertRaises(subprocess.CalledProcessError) as context:
                run_cli(repo_dir, output_file, protocol_dir, query)

            self.assertIn("Metadata repoURL mismatch", context.exception.stderr)

    def test_cli_preserves_logical_git_repo_url_when_working_dir_is_separate(self) -> None:
        query = load_json(FIXTURE_DIR / "query.json")
        expected_result = load_json(FIXTURE_DIR / "expected_result.json")
        revision_protocol = load_json(FIXTURE_DIR / "01_genCodeDesc.json")

        with tempfile.TemporaryDirectory() as temp_dir:
            root_dir = Path(temp_dir)
            repo_dir = root_dir / "repo"
            protocol_dir = root_dir / "protocols"
            output_file = root_dir / "out.json"

            repo_dir.mkdir()
            protocol_dir.mkdir()

            repo = GitRepoHarness(repo_dir)
            repo.write(
                "src/calc.py",
                "def calc(x):\n"
                "    value = x + 1\n"
                "    boosted = value * 2\n"
                "    return boosted\n",
            )
            revision_id = repo.commit_all("us1-r1", "2026-03-10T09:00:00Z")

            logical_repo_url = "https://example.local/repo/demo.git"
            write_revision_protocol(
                protocol_dir,
                revision_protocol,
                repo_dir,
                revision_id,
                repo_url_override=logical_repo_url,
            )

            run_cli(
                repo_dir,
                output_file,
                protocol_dir,
                {**query, "repoURL": logical_repo_url},
                repo_url_override=logical_repo_url,
                working_dir_override=repo_dir,
            )

            actual_result = load_json(output_file)
            expected_result["REPOSITORY"]["repoURL"] = logical_repo_url
            expected_result["REPOSITORY"]["revisionId"] = revision_id

            self.assertEqual(actual_result, expected_result)

    def test_cli_emits_debug_logs_for_us1_when_enabled(self) -> None:
        query = load_json(FIXTURE_DIR / "query.json")
        revision_protocol = load_json(FIXTURE_DIR / "01_genCodeDesc.json")

        with tempfile.TemporaryDirectory() as temp_dir:
            root_dir = Path(temp_dir)
            repo_dir = root_dir / "repo"
            protocol_dir = root_dir / "protocols"
            output_file = root_dir / "out.json"

            repo_dir.mkdir()
            protocol_dir.mkdir()

            repo = GitRepoHarness(repo_dir)
            repo.write(
                "src/calc.py",
                "def calc(x):\n"
                "    value = x + 1\n"
                "    boosted = value * 2\n"
                "    return boosted\n",
            )
            revision_id = repo.commit_all("us1-r1", "2026-03-10T09:00:00Z")

            write_revision_protocol(protocol_dir, revision_protocol, repo_dir, revision_id)

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
                relative_path="src/calc.py",
                final_line=1,
                origin_file="src/calc.py",
                origin_line=1,
                revision_id=revision_id,
                classification="100%-ai",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/calc.py",
                final_line=2,
                origin_file="src/calc.py",
                origin_line=2,
                revision_id=revision_id,
                classification="50%-ai",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/calc.py",
                final_line=3,
                origin_file="src/calc.py",
                origin_line=3,
                revision_id=revision_id,
                classification="100%-ai",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/calc.py",
                final_line=4,
                origin_file="src/calc.py",
                origin_line=4,
                revision_id=revision_id,
                classification="human/unattributed",
            )

    def test_cli_info_logging_focuses_on_live_line_aggregation_progress(self) -> None:
        query = load_json(FIXTURE_DIR / "query.json")
        revision_protocol = load_json(FIXTURE_DIR / "01_genCodeDesc.json")

        with tempfile.TemporaryDirectory() as temp_dir:
            root_dir = Path(temp_dir)
            repo_dir = root_dir / "repo"
            protocol_dir = root_dir / "protocols"
            output_file = root_dir / "out.json"

            repo_dir.mkdir()
            protocol_dir.mkdir()

            repo = GitRepoHarness(repo_dir)
            repo.write(
                "src/calc.py",
                "def calc(x):\n"
                "    value = x + 1\n"
                "    boosted = value * 2\n"
                "    return boosted\n",
            )
            revision_id = repo.commit_all("us1-r1", "2026-03-10T09:00:00Z")

            write_revision_protocol(protocol_dir, revision_protocol, repo_dir, revision_id)

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
                    "LiveLine src/calc.py:1 aggregate",
                    "LiveLine src/calc.py:2 aggregate",
                    "LiveLine src/calc.py:3 aggregate",
                    "LiveLine src/calc.py:4 aggregate",
                ],
            )
            assert_log_contains_none(
                self,
                result.stderr,
                [
                    "Loaded genCodeDesc for revision",
                ],
            )


if __name__ == "__main__":
    unittest.main()