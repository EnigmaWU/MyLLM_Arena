import tempfile
import unittest
from pathlib import Path
import subprocess

from tests.cli_test_support import GitRepoHarness, PROJECT_ROOT, UTILITY_PATH, load_json, run_cli, write_revision_protocol
from tests.log_assertions import assert_live_line_log, assert_log_contains_all, assert_log_contains_none, assert_transition_hint


FIXTURE_DIR = Path(__file__).resolve().parent.parent / "testdata" / "us10_large_repository_snapshot"


class TestUs10LargeRepositorySnapshotTdd(unittest.TestCase):
    maxDiff = None

    def test_cli_matches_us10_expected_result_for_narrow_algorithm_b_fixture_path(self) -> None:
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
                    "--endRevisionId",
                    query["endRevisionId"],
                    "--includedRevisionIds",
                    *query["includedRevisionIds"],
                ],
                cwd=PROJECT_ROOT,
                text=True,
                capture_output=True,
                check=True,
            )

            actual_result = load_json(output_file)
            self.assertEqual(actual_result, expected_result)

    def _protocol(self, *, repo_branch: str, details: list[dict]) -> dict:
        return {
            "protocolName": "generatedTextDesc",
            "protocolVersion": "26.03",
            "codeAgent": "ExampleAgent",
            "SUMMARY": {
                "totalCodeLines": 0,
                "fullGeneratedCodeLines": 0,
                "partialGeneratedCodeLines": 0,
            },
            "DETAIL": details,
            "REPOSITORY": {
                "vcsType": "git",
                "repoURL": "https://example.local/repo/us10-demo",
                "repoBranch": repo_branch,
                "revisionId": "placeholder",
            },
        }

    def _build_us10_repo(self, root_dir: Path) -> tuple[Path, Path, Path, dict[str, str]]:
        repo_dir = root_dir / "repo"
        protocol_dir = root_dir / "protocols"
        output_file = root_dir / "out.json"

        repo_dir.mkdir()
        protocol_dir.mkdir()

        repo = GitRepoHarness(repo_dir)
        baseline_files = {
            "src/core/alpha.py": "alpha_line = base + 1",
            "src/core/beta.py": "beta_line = base + 1",
            "src/core/gamma.py": "gamma_line = base + 1",
            "src/services/delta.py": "delta_line = base + 1",
            "src/services/epsilon.py": "epsilon_line = base + 1",
            "src/utils/zeta.py": "zeta_line = base + 1",
            "src/utils/eta.py": "eta_line = base + 1",
            "src/app/theta.py": "theta_line = base + 1",
        }
        for relative_path, middle_line in baseline_files.items():
            repo.write(
                relative_path,
                "carry_pre_window = base\n"
                f"{middle_line}\n"
                "stable_pre_window = base + 2\n",
            )
        revision_id_r1 = repo.commit_all("us10-r1", "2026-02-24T09:00:00Z")

        repo.write(
            "src/core/alpha.py",
            "carry_pre_window = base\n"
            "alpha_line = suggest(base + 1)\n"
            "stable_pre_window = base + 2\n",
        )
        repo.write(
            "src/core/beta.py",
            "carry_pre_window = base\n"
            "beta_line = suggest(base + 1)\n"
            "stable_pre_window = base + 2\n",
        )
        repo.write(
            "src/core/gamma.py",
            "carry_pre_window = base\n"
            "gamma_line = draft(base + 1)\n"
            "stable_pre_window = base + 2\n",
        )
        revision_id_r2 = repo.commit_all("us10-r2", "2026-03-05T09:00:00Z")

        repo.write(
            "src/core/beta.py",
            "carry_pre_window = base\n"
            "beta_line = refine(base + 1)\n"
            "stable_pre_window = base + 2\n",
        )
        repo.write(
            "src/services/delta.py",
            "carry_pre_window = base\n"
            "delta_line = synthesize(base + 1)\n"
            "stable_pre_window = base + 2\n",
        )
        repo.write(
            "src/services/epsilon.py",
            "carry_pre_window = base\n"
            "epsilon_line = blend(base + 1)\n"
            "stable_pre_window = base + 2\n",
        )
        revision_id_r3 = repo.commit_all("us10-r3", "2026-03-12T09:00:00Z")

        repo.write(
            "src/utils/zeta.py",
            "carry_pre_window = base\n"
            "zeta_line = generate(base + 1)\n"
            "stable_pre_window = base + 2\n",
        )
        repo.write(
            "src/utils/eta.py",
            "carry_pre_window = base\n"
            "eta_line = finalize(base + 1)\n"
            "stable_pre_window = base + 2\n",
        )
        repo.write(
            "src/app/theta.py",
            "carry_pre_window = base\n"
            "theta_line = assist(base + 1)\n"
            "stable_pre_window = base + 2\n",
        )
        revision_id_r4 = repo.commit_all("us10-r4", "2026-03-20T09:00:00Z")

        repo.write("README.md", "us10 large snapshot docs update\n")
        revision_id_r5 = repo.commit_all("us10-r5", "2026-03-28T09:00:00Z")

        for index, revision_id in enumerate([revision_id_r1, revision_id_r2, revision_id_r3, revision_id_r4], start=1):
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
        }

    def test_cli_matches_us10_expected_result_for_large_snapshot(self) -> None:
        self.assertTrue(
            UTILITY_PATH.exists(),
            f"Expected CLI utility at {UTILITY_PATH} for US-10 end-to-end execution.",
        )

        query = load_json(FIXTURE_DIR / "query.json")
        expected_result = load_json(FIXTURE_DIR / "expected_result.json")

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_dir, protocol_dir, output_file, revision_ids = self._build_us10_repo(Path(temp_dir))

            run_cli(repo_dir, output_file, protocol_dir, query)

            actual_result = load_json(output_file)
            expected_result["REPOSITORY"]["repoURL"] = str(repo_dir)
            expected_result["REPOSITORY"]["revisionId"] = revision_ids["r5"]

            self.assertEqual(actual_result, expected_result)

    def test_cli_emits_debug_logs_for_us10_when_enabled(self) -> None:
        query = load_json(FIXTURE_DIR / "query.json")

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_dir, protocol_dir, output_file, revision_ids = self._build_us10_repo(Path(temp_dir))

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
                    "Resolved 8 source files in the end snapshot",
                    "Finished analysis",
                    "Reuse cached genCodeDesc for revision",
                    "Skip out-of-window line src/core/alpha.py:1",
                ],
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/core/alpha.py",
                final_line=2,
                origin_file="src/core/alpha.py",
                origin_line=2,
                revision_id=revision_ids["r2"],
                classification="100%-ai",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/core/beta.py",
                final_line=2,
                origin_file="src/core/beta.py",
                origin_line=2,
                revision_id=revision_ids["r3"],
                classification="human/unattributed",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/core/gamma.py",
                final_line=2,
                origin_file="src/core/gamma.py",
                origin_line=2,
                revision_id=revision_ids["r2"],
                classification="50%-ai",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/services/delta.py",
                final_line=2,
                origin_file="src/services/delta.py",
                origin_line=2,
                revision_id=revision_ids["r3"],
                classification="100%-ai",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/services/epsilon.py",
                final_line=2,
                origin_file="src/services/epsilon.py",
                origin_line=2,
                revision_id=revision_ids["r3"],
                classification="60%-ai",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/utils/zeta.py",
                final_line=2,
                origin_file="src/utils/zeta.py",
                origin_line=2,
                revision_id=revision_ids["r4"],
                classification="100%-ai",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/utils/eta.py",
                final_line=2,
                origin_file="src/utils/eta.py",
                origin_line=2,
                revision_id=revision_ids["r4"],
                classification="human/unattributed",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/app/theta.py",
                final_line=2,
                origin_file="src/app/theta.py",
                origin_line=2,
                revision_id=revision_ids["r4"],
                classification="40%-ai",
            )
            assert_transition_hint(self, result.stderr, "100%-ai", "human/unattributed")
            assert_transition_hint(self, result.stderr, "human/unattributed", "50%-ai")
            assert_transition_hint(self, result.stderr, "human/unattributed", "60%-ai")

    def test_cli_info_logging_focuses_on_live_line_aggregation_progress_for_us10(self) -> None:
        query = load_json(FIXTURE_DIR / "query.json")

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_dir, protocol_dir, output_file, _revision_ids = self._build_us10_repo(Path(temp_dir))

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
                    "LiveLine src/core/alpha.py:2 aggregate",
                    "LiveLine src/core/beta.py:2 aggregate",
                    "LiveLine src/core/gamma.py:2 aggregate",
                    "LiveLine src/services/delta.py:2 aggregate",
                    "LiveLine src/services/epsilon.py:2 aggregate",
                    "LiveLine src/utils/zeta.py:2 aggregate",
                    "LiveLine src/utils/eta.py:2 aggregate",
                    "LiveLine src/app/theta.py:2 aggregate",
                    "Finished analysis with totalCodeLines=8 fullGeneratedCodeLines=3 partialGeneratedCodeLines=3",
                ],
            )
            assert_log_contains_none(
                self,
                result.stderr,
                [
                    "Loaded genCodeDesc for revision",
                    "LiveLine src/core/alpha.py:1 aggregate",
                ],
            )

    def test_cli_preserves_dense_multi_line_large_snapshot_variant(self) -> None:
        query = {
            "vcsType": "git",
            "repoURL": "https://example.local/repo/us10-dense-snapshot",
            "repoBranch": "main",
            "metric": "live_changed_source_ratio",
            "algorithm": "A",
            "scope": "A",
            "startTime": "2026-03-01",
            "endTime": "2026-03-31",
            "endRevisionId": "us10-dense-r5",
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            root_dir = Path(temp_dir)
            repo_dir = root_dir / "repo"
            protocol_dir = root_dir / "protocols"
            output_file = root_dir / "out.json"

            repo_dir.mkdir()
            protocol_dir.mkdir()

            repo = GitRepoHarness(repo_dir)
            baseline_files = {
                "src/core/alpha.py": ("alpha_two = base + 1", "alpha_three = base + 2", "alpha_four = base + 3"),
                "src/core/beta.py": ("beta_two = base + 1", "beta_three = base + 2", "beta_four = base + 3"),
                "src/services/gamma.py": ("gamma_two = base + 1", "gamma_three = base + 2", "gamma_four = base + 3"),
                "src/services/delta.py": ("delta_two = base + 1", "delta_three = base + 2", "delta_four = base + 3"),
            }
            for relative_path, (line_two, line_three, line_four) in baseline_files.items():
                repo.write(
                    relative_path,
                    "carry_pre_window = base\n"
                    f"{line_two}\n"
                    f"{line_three}\n"
                    f"{line_four}\n"
                    "stable_pre_window = base + 4\n",
                )
            revision_id_r1 = repo.commit_all("us10-dense-r1", "2026-02-24T09:00:00Z")

            repo.write(
                "src/core/alpha.py",
                "carry_pre_window = base\n"
                "alpha_two = suggest(base + 1)\n"
                "alpha_three = assist(base + 2)\n"
                "alpha_four = base + 3\n"
                "stable_pre_window = base + 4\n",
            )
            repo.write(
                "src/core/beta.py",
                "carry_pre_window = base\n"
                "beta_two = synthesize(base + 1)\n"
                "beta_three = base + 2\n"
                "beta_four = base + 3\n"
                "stable_pre_window = base + 4\n",
            )
            repo.write(
                "src/services/gamma.py",
                "carry_pre_window = base\n"
                "gamma_two = base + 1\n"
                "gamma_three = blend(base + 2)\n"
                "gamma_four = base + 3\n"
                "stable_pre_window = base + 4\n",
            )
            revision_id_r2 = repo.commit_all("us10-dense-r2", "2026-03-05T09:00:00Z")

            repo.write(
                "src/core/beta.py",
                "carry_pre_window = base\n"
                "beta_two = normalize(base + 1)\n"
                "beta_three = generate(base + 2)\n"
                "beta_four = base + 3\n"
                "stable_pre_window = base + 4\n",
            )
            repo.write(
                "src/services/delta.py",
                "carry_pre_window = base\n"
                "delta_two = draft(base + 1)\n"
                "delta_three = generate(base + 2)\n"
                "delta_four = base + 3\n"
                "stable_pre_window = base + 4\n",
            )
            revision_id_r3 = repo.commit_all("us10-dense-r3", "2026-03-12T09:00:00Z")

            repo.write(
                "src/core/alpha.py",
                "carry_pre_window = base\n"
                "alpha_two = suggest(base + 1)\n"
                "alpha_three = assist(base + 2)\n"
                "alpha_four = refine(base + 3)\n"
                "stable_pre_window = base + 4\n",
            )
            repo.write(
                "src/services/gamma.py",
                "carry_pre_window = base\n"
                "gamma_two = verify(base + 1)\n"
                "gamma_three = blend(base + 2)\n"
                "gamma_four = suggest(base + 3)\n"
                "stable_pre_window = base + 4\n",
            )
            revision_id_r4 = repo.commit_all("us10-dense-r4", "2026-03-20T09:00:00Z")

            repo.write("README.md", "us10 dense snapshot docs update\n")
            revision_id_r5 = repo.commit_all("us10-dense-r5", "2026-03-28T09:00:00Z")

            write_revision_protocol(
                protocol_dir,
                self._protocol(
                    repo_branch="main",
                    details=[
                        {"fileName": "src/core/alpha.py", "codeLines": []},
                        {"fileName": "src/core/beta.py", "codeLines": []},
                        {"fileName": "src/services/gamma.py", "codeLines": []},
                        {"fileName": "src/services/delta.py", "codeLines": []},
                    ],
                ),
                repo_dir,
                revision_id_r1,
            )
            write_revision_protocol(
                protocol_dir,
                self._protocol(
                    repo_branch="main",
                    details=[
                        {
                            "fileName": "src/core/alpha.py",
                            "codeLines": [
                                {"lineLocation": 2, "genRatio": 100, "genMethod": "codeCompletion"},
                                {"lineLocation": 3, "genRatio": 50, "genMethod": "codeCompletion"},
                            ],
                        },
                        {
                            "fileName": "src/core/beta.py",
                            "codeLines": [
                                {"lineLocation": 2, "genRatio": 100, "genMethod": "codeCompletion"},
                            ],
                        },
                        {
                            "fileName": "src/services/gamma.py",
                            "codeLines": [
                                {"lineLocation": 3, "genRatio": 60, "genMethod": "codeCompletion"},
                            ],
                        },
                        {"fileName": "src/services/delta.py", "codeLines": []},
                    ],
                ),
                repo_dir,
                revision_id_r2,
            )
            write_revision_protocol(
                protocol_dir,
                self._protocol(
                    repo_branch="main",
                    details=[
                        {"fileName": "src/core/alpha.py", "codeLines": []},
                        {
                            "fileName": "src/core/beta.py",
                            "codeLines": [
                                {"lineLocation": 3, "genRatio": 100, "genMethod": "codeCompletion"},
                            ],
                        },
                        {"fileName": "src/services/gamma.py", "codeLines": []},
                        {
                            "fileName": "src/services/delta.py",
                            "codeLines": [
                                {"lineLocation": 2, "genRatio": 40, "genMethod": "codeCompletion"},
                                {"lineLocation": 3, "genRatio": 100, "genMethod": "codeCompletion"},
                            ],
                        },
                    ],
                ),
                repo_dir,
                revision_id_r3,
            )
            write_revision_protocol(
                protocol_dir,
                self._protocol(
                    repo_branch="main",
                    details=[
                        {
                            "fileName": "src/core/alpha.py",
                            "codeLines": [
                                {"lineLocation": 4, "genRatio": 70, "genMethod": "codeCompletion"},
                            ],
                        },
                        {"fileName": "src/core/beta.py", "codeLines": []},
                        {
                            "fileName": "src/services/gamma.py",
                            "codeLines": [
                                {"lineLocation": 4, "genRatio": 100, "genMethod": "codeCompletion"},
                            ],
                        },
                        {"fileName": "src/services/delta.py", "codeLines": []},
                    ],
                ),
                repo_dir,
                revision_id_r4,
            )

            result = run_cli(
                repo_dir,
                output_file,
                protocol_dir,
                query,
                extra_args=["--logLevel", "debug"],
            )

            self.assertEqual(
                load_json(output_file),
                {
                    "protocolName": "generatedTextDesc",
                    "protocolVersion": "26.03",
                    "SUMMARY": {
                        "totalCodeLines": 10,
                        "fullGeneratedCodeLines": 4,
                        "partialGeneratedCodeLines": 4,
                    },
                    "REPOSITORY": {
                        "vcsType": "git",
                        "repoURL": str(repo_dir),
                        "repoBranch": "main",
                        "revisionId": revision_id_r5,
                    },
                },
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/core/alpha.py",
                final_line=2,
                origin_file="src/core/alpha.py",
                origin_line=2,
                revision_id=revision_id_r2,
                classification="100%-ai",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/core/alpha.py",
                final_line=3,
                origin_file="src/core/alpha.py",
                origin_line=3,
                revision_id=revision_id_r2,
                classification="50%-ai",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/core/alpha.py",
                final_line=4,
                origin_file="src/core/alpha.py",
                origin_line=4,
                revision_id=revision_id_r4,
                classification="70%-ai",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/core/beta.py",
                final_line=2,
                origin_file="src/core/beta.py",
                origin_line=2,
                revision_id=revision_id_r3,
                classification="human/unattributed",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/core/beta.py",
                final_line=3,
                origin_file="src/core/beta.py",
                origin_line=3,
                revision_id=revision_id_r3,
                classification="100%-ai",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/services/gamma.py",
                final_line=2,
                origin_file="src/services/gamma.py",
                origin_line=2,
                revision_id=revision_id_r4,
                classification="human/unattributed",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/services/gamma.py",
                final_line=3,
                origin_file="src/services/gamma.py",
                origin_line=3,
                revision_id=revision_id_r2,
                classification="60%-ai",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/services/gamma.py",
                final_line=4,
                origin_file="src/services/gamma.py",
                origin_line=4,
                revision_id=revision_id_r4,
                classification="100%-ai",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/services/delta.py",
                final_line=2,
                origin_file="src/services/delta.py",
                origin_line=2,
                revision_id=revision_id_r3,
                classification="40%-ai",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/services/delta.py",
                final_line=3,
                origin_file="src/services/delta.py",
                origin_line=3,
                revision_id=revision_id_r3,
                classification="100%-ai",
            )
            assert_transition_hint(self, result.stderr, "100%-ai", "human/unattributed")
            assert_transition_hint(self, result.stderr, "human/unattributed", "70%-ai")
            assert_transition_hint(self, result.stderr, "human/unattributed", "100%-ai")


if __name__ == "__main__":
    unittest.main()