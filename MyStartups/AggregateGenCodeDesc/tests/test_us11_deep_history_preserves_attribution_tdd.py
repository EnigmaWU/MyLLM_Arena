import tempfile
import unittest
from pathlib import Path
import subprocess

from tests.cli_test_support import GitRepoHarness, PROJECT_ROOT, UTILITY_PATH, load_json, run_cli, write_revision_protocol
from tests.log_assertions import assert_live_line_log, assert_log_contains_all, assert_log_contains_none, assert_transition_hint


FIXTURE_DIR = Path(__file__).resolve().parent.parent / "testdata" / "us11_deep_history_preserves_attribution"


class TestUs11DeepHistoryPreservesAttributionTdd(unittest.TestCase):
    maxDiff = None

    def test_cli_matches_us11_expected_result_for_narrow_algorithm_b_fixture_path(self) -> None:
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

    def _build_us11_repo(self, root_dir: Path) -> tuple[Path, Path, Path, dict[str, str]]:
        repo_dir = root_dir / "repo"
        protocol_dir = root_dir / "protocols"
        output_file = root_dir / "out.json"

        repo_dir.mkdir()
        protocol_dir.mkdir()

        repo = GitRepoHarness(repo_dir)
        repo.write(
            "src/deep_history.py",
            "carry_pre_window = base\n"
            "bounce_human = base + 1\n"
            "bounce_ai = base + 2\n"
            "steady_partial = base + 3\n"
            "reset_after_ai = base + 4\n",
        )
        revision_id_r1 = repo.commit_all("us11-r1", "2026-02-24T09:00:00Z")

        repo.write(
            "src/deep_history.py",
            "carry_pre_window = base\n"
            "bounce_human = suggest(base + 1)\n"
            "bounce_ai = base + 2\n"
            "steady_partial = base + 3\n"
            "reset_after_ai = synthesize(base + 4)\n",
        )
        revision_id_r2 = repo.commit_all("us11-r2", "2026-03-03T09:00:00Z")

        repo.write(
            "src/deep_history.py",
            "carry_pre_window = base\n"
            "bounce_human = normalize(base + 1)\n"
            "bounce_ai = draft(base + 2)\n"
            "steady_partial = base + 3\n"
            "reset_after_ai = synthesize(base + 4)\n",
        )
        revision_id_r3 = repo.commit_all("us11-r3", "2026-03-06T09:00:00Z")

        repo.write(
            "src/deep_history.py",
            "carry_pre_window = base\n"
            "bounce_human = refine(base + 1)\n"
            "bounce_ai = stabilize(base + 2)\n"
            "steady_partial = base + 3\n"
            "reset_after_ai = synthesize(base + 4)\n",
        )
        revision_id_r4 = repo.commit_all("us11-r4", "2026-03-10T09:00:00Z")

        repo.write(
            "src/deep_history.py",
            "carry_pre_window = base\n"
            "bounce_human = finalize(base + 1)\n"
            "bounce_ai = stabilize(base + 2)\n"
            "steady_partial = base + 3\n"
            "reset_after_ai = synthesize(base + 4)\n",
        )
        revision_id_r5 = repo.commit_all("us11-r5", "2026-03-14T09:00:00Z")

        repo.write(
            "src/deep_history.py",
            "carry_pre_window = base\n"
            "bounce_human = finalize(base + 1)\n"
            "bounce_ai = stabilize(base + 2)\n"
            "steady_partial = blend(base + 3)\n"
            "reset_after_ai = synthesize(base + 4)\n",
        )
        revision_id_r6 = repo.commit_all("us11-r6", "2026-03-18T09:00:00Z")

        repo.write(
            "src/deep_history.py",
            "carry_pre_window = base\n"
            "bounce_human = finalize(base + 1)\n"
            "bounce_ai = stabilize(base + 2)\n"
            "steady_partial = blend(base + 3)\n"
            "reset_after_ai = verify(base + 4)\n",
        )
        revision_id_r7 = repo.commit_all("us11-r7", "2026-03-22T09:00:00Z")

        repo.write(
            "src/deep_history.py",
            "carry_pre_window = base\n"
            "bounce_human = finalize(base + 1)\n"
            "bounce_ai = generate(base + 2)\n"
            "steady_partial = blend(base + 3)\n"
            "reset_after_ai = verify(base + 4)\n",
        )
        revision_id_r8 = repo.commit_all("us11-r8", "2026-03-26T09:00:00Z")

        repo.write("README.md", "us11 deep history docs update\n")
        revision_id_r9 = repo.commit_all("us11-r9", "2026-03-28T09:00:00Z")

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
                load_json(FIXTURE_DIR / f"{index:02d}_genCodeDesc.json"),
                repo_dir,
                revision_id,
            )

        return repo_dir, protocol_dir, output_file, {
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
            f"Expected CLI utility at {UTILITY_PATH} for US-11 end-to-end execution.",
        )

        query = load_json(FIXTURE_DIR / "query.json")
        expected_result = load_json(FIXTURE_DIR / "expected_result.json")

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_dir, protocol_dir, output_file, revision_ids = self._build_us11_repo(Path(temp_dir))

            run_cli(repo_dir, output_file, protocol_dir, query)

            actual_result = load_json(output_file)
            expected_result["REPOSITORY"]["repoURL"] = str(repo_dir)
            expected_result["REPOSITORY"]["revisionId"] = revision_ids["r9"]

            self.assertEqual(actual_result, expected_result)

    def test_cli_emits_debug_logs_for_us11_when_enabled(self) -> None:
        query = load_json(FIXTURE_DIR / "query.json")

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_dir, protocol_dir, output_file, revision_ids = self._build_us11_repo(Path(temp_dir))

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
                    "Skip out-of-window line src/deep_history.py:1",
                ],
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/deep_history.py",
                final_line=2,
                origin_file="src/deep_history.py",
                origin_line=2,
                revision_id=revision_ids["r5"],
                classification="human/unattributed",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/deep_history.py",
                final_line=3,
                origin_file="src/deep_history.py",
                origin_line=3,
                revision_id=revision_ids["r8"],
                classification="100%-ai",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/deep_history.py",
                final_line=4,
                origin_file="src/deep_history.py",
                origin_line=4,
                revision_id=revision_ids["r6"],
                classification="60%-ai",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/deep_history.py",
                final_line=5,
                origin_file="src/deep_history.py",
                origin_line=5,
                revision_id=revision_ids["r7"],
                classification="human/unattributed",
            )
            assert_transition_hint(self, result.stderr, "50%-ai", "human/unattributed")
            assert_transition_hint(self, result.stderr, "human/unattributed", "60%-ai")
            assert_transition_hint(self, result.stderr, "human/unattributed", "100%-ai")

    def test_cli_info_logging_focuses_on_live_line_aggregation_progress_for_us11(self) -> None:
        query = load_json(FIXTURE_DIR / "query.json")

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_dir, protocol_dir, output_file, _revision_ids = self._build_us11_repo(Path(temp_dir))

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