import shutil
import tempfile
import unittest
from pathlib import Path

from tests.cli_test_support import SvnRepoHarness, UTILITY_PATH, load_json, run_cli, write_revision_protocol
from tests.log_assertions import assert_live_line_log, assert_log_contains_all, assert_log_contains_none


FIXTURE_DIR = Path(__file__).resolve().parent.parent / "testdata" / "us1_live_changed_source_ratio_svn"


@unittest.skipUnless(shutil.which("svn") and shutil.which("svnadmin"), "svn tooling not installed")
class TestUs1LiveChangedSourceRatioSvnTdd(unittest.TestCase):
    maxDiff = None

    def _build_svn_repo(self, root_dir: Path) -> tuple[SvnRepoHarness, Path, Path, str]:
        repo_dir = root_dir / "repo"
        working_copy_dir = root_dir / "wc"
        protocol_dir = root_dir / "protocols"
        output_file = root_dir / "out.json"

        protocol_dir.mkdir()

        repo = SvnRepoHarness(repo_dir, working_copy_dir)
        trunk_file = working_copy_dir / "trunk" / "src" / "demo.py"
        trunk_file.parent.mkdir(parents=True, exist_ok=True)
        trunk_file.write_text(
            "def calc(x):\n"
            "    value = x + 1\n"
            "    boosted = value * 2\n"
            "    return boosted\n",
            encoding="utf-8",
        )
        repo.add("trunk/src/demo.py")
        revision_id = repo.commit_all("us1-svn-r2", "2026-03-10T09:00:00.000000Z")

        return repo, protocol_dir, output_file, revision_id

    def test_cli_matches_us1_expected_result_for_real_svn_repo(self) -> None:
        self.assertTrue(
            UTILITY_PATH.exists(),
            f"Expected CLI utility at {UTILITY_PATH} for US-1 SVN end-to-end execution.",
        )

        query = load_json(FIXTURE_DIR / "query.json")
        expected_result = load_json(FIXTURE_DIR / "expected_result.json")
        revision_protocol = load_json(FIXTURE_DIR / "01_genCodeDesc.json")

        with tempfile.TemporaryDirectory() as temp_dir:
            repo, protocol_dir, output_file, revision_id = self._build_svn_repo(Path(temp_dir))
            write_revision_protocol(
                protocol_dir,
                revision_protocol,
                repo.repo_dir,
                revision_id,
                repo_url_override=repo.repo_url,
            )

            run_cli(
                repo.repo_dir,
                output_file,
                protocol_dir,
                query,
                repo_url_override=repo.repo_url,
            )

            actual_result = load_json(output_file)
            expected_result["REPOSITORY"]["repoURL"] = repo.repo_url
            expected_result["REPOSITORY"]["revisionId"] = revision_id

            self.assertEqual(actual_result, expected_result)

    def test_cli_emits_debug_logs_for_us1_svn_when_enabled(self) -> None:
        query = load_json(FIXTURE_DIR / "query.json")
        revision_protocol = load_json(FIXTURE_DIR / "01_genCodeDesc.json")

        with tempfile.TemporaryDirectory() as temp_dir:
            repo, protocol_dir, output_file, revision_id = self._build_svn_repo(Path(temp_dir))
            write_revision_protocol(
                protocol_dir,
                revision_protocol,
                repo.repo_dir,
                revision_id,
                repo_url_override=repo.repo_url,
            )

            result = run_cli(
                repo.repo_dir,
                output_file,
                protocol_dir,
                query,
                extra_args=["--logLevel", "debug"],
                repo_url_override=repo.repo_url,
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
                relative_path="src/demo.py",
                final_line=1,
                origin_file="trunk/src/demo.py",
                origin_line=1,
                revision_id=revision_id,
                classification="human/unattributed",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/demo.py",
                final_line=2,
                origin_file="trunk/src/demo.py",
                origin_line=2,
                revision_id=revision_id,
                classification="100%-ai",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/demo.py",
                final_line=3,
                origin_file="trunk/src/demo.py",
                origin_line=3,
                revision_id=revision_id,
                classification="100%-ai",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/demo.py",
                final_line=4,
                origin_file="trunk/src/demo.py",
                origin_line=4,
                revision_id=revision_id,
                classification="50%-ai",
            )

    def test_cli_info_logging_focuses_on_live_line_aggregation_progress_for_us1_svn(self) -> None:
        query = load_json(FIXTURE_DIR / "query.json")
        revision_protocol = load_json(FIXTURE_DIR / "01_genCodeDesc.json")

        with tempfile.TemporaryDirectory() as temp_dir:
            repo, protocol_dir, output_file, revision_id = self._build_svn_repo(Path(temp_dir))
            write_revision_protocol(
                protocol_dir,
                revision_protocol,
                repo.repo_dir,
                revision_id,
                repo_url_override=repo.repo_url,
            )

            result = run_cli(
                repo.repo_dir,
                output_file,
                protocol_dir,
                query,
                extra_args=["--logLevel", "info"],
                repo_url_override=repo.repo_url,
            )

            assert_log_contains_all(
                self,
                result.stderr,
                [
                    "Starting analysis",
                    "LiveLine src/demo.py:1 aggregate",
                    "LiveLine src/demo.py:2 aggregate",
                    "LiveLine src/demo.py:3 aggregate",
                    "LiveLine src/demo.py:4 aggregate",
                    "Finished analysis with totalCodeLines=4 fullGeneratedCodeLines=2 partialGeneratedCodeLines=1",
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