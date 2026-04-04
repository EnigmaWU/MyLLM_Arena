import shutil
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from tests.cli_test_support import SvnRepoHarness, UTILITY_PATH, load_json, run_cli, write_revision_protocol
from tests.log_assertions import assert_live_line_log, assert_log_contains_all, assert_log_contains_none, assert_transition_hint


FIXTURE_DIR = Path(__file__).resolve().parent.parent / "testdata" / "us11_deep_history_preserves_attribution"


def _svn_protocol(protocol: dict) -> dict:
    converted = deepcopy(protocol)
    converted["REPOSITORY"]["vcsType"] = "svn"
    converted["REPOSITORY"]["repoBranch"] = "trunk"
    for detail in converted.get("DETAIL", []):
        file_name = detail.get("fileName")
        if file_name and not file_name.startswith("trunk/"):
            detail["fileName"] = f"trunk/{file_name}"
    return converted


@unittest.skipUnless(shutil.which("svn") and shutil.which("svnadmin"), "svn tooling not installed")
class TestUs11DeepHistoryPreservesAttributionSvnTdd(unittest.TestCase):
    maxDiff = None

    def _query(self) -> dict:
        query = load_json(FIXTURE_DIR / "query.json")
        query["vcsType"] = "svn"
        query["repoBranch"] = "trunk"
        return query

    def _build_us11_repo(self, root_dir: Path) -> tuple[SvnRepoHarness, Path, Path, dict[str, str]]:
        repo_dir = root_dir / "repo"
        working_copy_dir = root_dir / "wc"
        protocol_dir = root_dir / "protocols"
        output_file = root_dir / "out.json"

        protocol_dir.mkdir()

        repo = SvnRepoHarness(repo_dir, working_copy_dir)
        repo.write(
            "trunk/src/deep_history.py",
            "carry_pre_window = base\n"
            "bounce_human = base + 1\n"
            "bounce_ai = base + 2\n"
            "steady_partial = base + 3\n"
            "reset_after_ai = base + 4\n",
        )
        repo.add("trunk/src/deep_history.py")
        revision_id_r1 = repo.commit_all("us11-svn-r1", "2026-02-24T09:00:00.000000Z")

        repo.write(
            "trunk/src/deep_history.py",
            "carry_pre_window = base\n"
            "bounce_human = suggest(base + 1)\n"
            "bounce_ai = base + 2\n"
            "steady_partial = base + 3\n"
            "reset_after_ai = synthesize(base + 4)\n",
        )
        revision_id_r2 = repo.commit_all("us11-svn-r2", "2026-03-03T09:00:00.000000Z")

        repo.write(
            "trunk/src/deep_history.py",
            "carry_pre_window = base\n"
            "bounce_human = normalize(base + 1)\n"
            "bounce_ai = draft(base + 2)\n"
            "steady_partial = base + 3\n"
            "reset_after_ai = synthesize(base + 4)\n",
        )
        revision_id_r3 = repo.commit_all("us11-svn-r3", "2026-03-06T09:00:00.000000Z")

        repo.write(
            "trunk/src/deep_history.py",
            "carry_pre_window = base\n"
            "bounce_human = refine(base + 1)\n"
            "bounce_ai = stabilize(base + 2)\n"
            "steady_partial = base + 3\n"
            "reset_after_ai = synthesize(base + 4)\n",
        )
        revision_id_r4 = repo.commit_all("us11-svn-r4", "2026-03-10T09:00:00.000000Z")

        repo.write(
            "trunk/src/deep_history.py",
            "carry_pre_window = base\n"
            "bounce_human = finalize(base + 1)\n"
            "bounce_ai = stabilize(base + 2)\n"
            "steady_partial = base + 3\n"
            "reset_after_ai = synthesize(base + 4)\n",
        )
        revision_id_r5 = repo.commit_all("us11-svn-r5", "2026-03-14T09:00:00.000000Z")

        repo.write(
            "trunk/src/deep_history.py",
            "carry_pre_window = base\n"
            "bounce_human = finalize(base + 1)\n"
            "bounce_ai = stabilize(base + 2)\n"
            "steady_partial = blend(base + 3)\n"
            "reset_after_ai = synthesize(base + 4)\n",
        )
        revision_id_r6 = repo.commit_all("us11-svn-r6", "2026-03-18T09:00:00.000000Z")

        repo.write(
            "trunk/src/deep_history.py",
            "carry_pre_window = base\n"
            "bounce_human = finalize(base + 1)\n"
            "bounce_ai = stabilize(base + 2)\n"
            "steady_partial = blend(base + 3)\n"
            "reset_after_ai = verify(base + 4)\n",
        )
        revision_id_r7 = repo.commit_all("us11-svn-r7", "2026-03-22T09:00:00.000000Z")

        repo.write(
            "trunk/src/deep_history.py",
            "carry_pre_window = base\n"
            "bounce_human = finalize(base + 1)\n"
            "bounce_ai = generate(base + 2)\n"
            "steady_partial = blend(base + 3)\n"
            "reset_after_ai = verify(base + 4)\n",
        )
        revision_id_r8 = repo.commit_all("us11-svn-r8", "2026-03-26T09:00:00.000000Z")

        repo.write("trunk/README.md", "us11 deep history docs update\n")
        repo.add("trunk/README.md")
        revision_id_r9 = repo.commit_all("us11-svn-r9", "2026-03-28T09:00:00.000000Z")

        for index, revision_id in enumerate(
            [
                revision_id_r1,
                revision_id_r2,
                revision_id_r3,
                revision_id_r4,
                revision_id_r5,
                revision_id_r6,
                revision_id_r7,
                revision_id_r8,
            ],
            start=1,
        ):
            write_revision_protocol(
                protocol_dir,
                _svn_protocol(load_json(FIXTURE_DIR / f"{index:02d}_genCodeDesc.json")),
                repo.repo_dir,
                revision_id,
                repo_url_override=repo.repo_url,
            )

        return repo, protocol_dir, output_file, {
            "r1": revision_id_r1,
            "r2": revision_id_r2,
            "r3": revision_id_r3,
            "r4": revision_id_r4,
            "r5": revision_id_r5,
            "r6": revision_id_r6,
            "r7": revision_id_r7,
            "r8": revision_id_r8,
            "r9": revision_id_r9,
        }

    def test_cli_matches_us11_expected_result_for_deep_history(self) -> None:
        self.assertTrue(
            UTILITY_PATH.exists(),
            f"Expected CLI utility at {UTILITY_PATH} for US-11 SVN end-to-end execution.",
        )

        query = self._query()
        expected_result = load_json(FIXTURE_DIR / "expected_result.json")

        with tempfile.TemporaryDirectory() as temp_dir:
            repo, protocol_dir, output_file, revision_ids = self._build_us11_repo(Path(temp_dir))

            run_cli(repo.repo_dir, output_file, protocol_dir, query, repo_url_override=repo.repo_url)

            actual_result = load_json(output_file)
            expected_result["REPOSITORY"]["vcsType"] = "svn"
            expected_result["REPOSITORY"]["repoURL"] = repo.repo_url
            expected_result["REPOSITORY"]["repoBranch"] = "trunk"
            expected_result["REPOSITORY"]["revisionId"] = revision_ids["r9"]

            self.assertEqual(actual_result, expected_result)

    def test_cli_emits_debug_logs_for_us11_when_enabled(self) -> None:
        query = self._query()

        with tempfile.TemporaryDirectory() as temp_dir:
            repo, protocol_dir, output_file, revision_ids = self._build_us11_repo(Path(temp_dir))

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
                    "Skip out-of-window line src/deep_history.py:1",
                ],
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/deep_history.py",
                final_line=2,
                origin_file="trunk/src/deep_history.py",
                origin_line=2,
                revision_id=revision_ids["r5"],
                classification="human/unattributed",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/deep_history.py",
                final_line=3,
                origin_file="trunk/src/deep_history.py",
                origin_line=3,
                revision_id=revision_ids["r8"],
                classification="100%-ai",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/deep_history.py",
                final_line=4,
                origin_file="trunk/src/deep_history.py",
                origin_line=4,
                revision_id=revision_ids["r6"],
                classification="60%-ai",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/deep_history.py",
                final_line=5,
                origin_file="trunk/src/deep_history.py",
                origin_line=5,
                revision_id=revision_ids["r7"],
                classification="human/unattributed",
            )
            assert_transition_hint(self, result.stderr, "50%-ai", "human/unattributed")
            assert_transition_hint(self, result.stderr, "human/unattributed", "60%-ai")
            assert_transition_hint(self, result.stderr, "human/unattributed", "100%-ai")

    def test_cli_info_logging_focuses_on_live_line_aggregation_progress_for_us11(self) -> None:
        query = self._query()

        with tempfile.TemporaryDirectory() as temp_dir:
            repo, protocol_dir, output_file, _revision_ids = self._build_us11_repo(Path(temp_dir))

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
                    "LiveLine src/deep_history.py:2 aggregate",
                    "LiveLine src/deep_history.py:3 aggregate",
                    "LiveLine src/deep_history.py:4 aggregate",
                    "LiveLine src/deep_history.py:5 aggregate",
                    "Finished analysis with totalCodeLines=4 fullGeneratedCodeLines=1 partialGeneratedCodeLines=1",
                ],
            )
            assert_log_contains_none(
                self,
                result.stderr,
                [
                    "Loaded genCodeDesc for revision",
                    "LiveLine src/deep_history.py:1 aggregate",
                ],
            )


if __name__ == "__main__":
    unittest.main()