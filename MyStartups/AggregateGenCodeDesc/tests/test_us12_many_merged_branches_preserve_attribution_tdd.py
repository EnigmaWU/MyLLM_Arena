import json
import tempfile
import unittest
from pathlib import Path

from tests.cli_test_support import GitRepoHarness, load_json, run_cli, write_revision_protocol
from tests.log_assertions import assert_live_line_log, assert_log_contains_all, assert_log_contains_none


FIXTURE_DIR = Path(__file__).resolve().parent.parent / "testdata" / "us12_many_merged_branches_preserve_attribution"


class TestUs12ManyMergedBranchesPreserveAttributionTdd(unittest.TestCase):
    maxDiff = None

    def _query(self) -> dict:
        return load_json(FIXTURE_DIR / "query.json")

    def _inline_protocol(
        self,
        *,
        repo_branch: str,
        file_name: str,
        full_lines: list[int] | None = None,
        partial_lines: dict[int, int] | None = None,
    ) -> dict:
        full_lines = full_lines or []
        partial_lines = partial_lines or {}
        code_lines = [
            {"lineLocation": line_number, "genRatio": 100, "genMethod": "codeCompletion"}
            for line_number in full_lines
        ]
        code_lines.extend(
            {
                "lineLocation": line_number,
                "genRatio": ratio,
                "genMethod": "vibeCoding",
            }
            for line_number, ratio in sorted(partial_lines.items())
        )
        return {
            "protocolName": "generatedTextDesc",
            "protocolVersion": "26.03",
            "codeAgent": "Us12VariantAgent",
            "SUMMARY": {
                "totalCodeLines": len(full_lines) + len(partial_lines),
                "fullGeneratedCodeLines": len(full_lines),
                "partialGeneratedCodeLines": len(partial_lines),
            },
            "DETAIL": [
                {
                    "fileName": file_name,
                    "codeLines": code_lines,
                }
            ],
            "REPOSITORY": {
                "vcsType": "git",
                "repoURL": "https://example.local/repo/us12-variant",
                "repoBranch": repo_branch,
                "revisionId": "placeholder",
            },
        }

    def _build_history(self, root_dir: Path) -> tuple[Path, Path, Path, dict[str, str]]:
        repo_dir = root_dir / "repo"
        protocol_dir = root_dir / "protocols"
        output_file = root_dir / "out.json"
        repo_dir.mkdir()
        protocol_dir.mkdir()

        repo = GitRepoHarness(repo_dir)

        # WHY: US-12 is about preserving independent per-line attribution when
        # many branches merge into the same target window, so the history uses
        # several feature branches that each contribute a different surviving line.
        repo.write(
            "src/branch_matrix.py",
            "carry_pre_window = base\n"
            "main_human = base + 1\n"
            "alpha_branch = base + 2\n"
            "beta_branch = base + 3\n"
            "gamma_branch = base + 4\n"
            "delta_branch = base + 5\n"
            "epsilon_branch = base + 6\n"
            "stable_pre_window = base + 7\n"
            "main_tail = base + 8\n"
            "return carry_pre_window + main_human + alpha_branch + beta_branch + gamma_branch + delta_branch + epsilon_branch + stable_pre_window + main_tail\n",
        )
        revision_id_r1 = repo.commit_all("us12-r1", "2026-02-24T09:00:00Z")

        repo.write(
            "src/branch_matrix.py",
            "carry_pre_window = base\n"
            "main_human = sanitize(base + 1)\n"
            "alpha_branch = base + 2\n"
            "beta_branch = base + 3\n"
            "gamma_branch = base + 4\n"
            "delta_branch = base + 5\n"
            "epsilon_branch = base + 6\n"
            "stable_pre_window = base + 7\n"
            "main_tail = base + 8\n"
            "return carry_pre_window + main_human + alpha_branch + beta_branch + gamma_branch + delta_branch + epsilon_branch + stable_pre_window + main_tail\n",
        )
        revision_id_r2 = repo.commit_all("us12-r2", "2026-03-02T09:00:00Z")

        repo.checkout_new_branch("feature-alpha")
        repo.write(
            "src/branch_matrix.py",
            "carry_pre_window = base\n"
            "main_human = sanitize(base + 1)\n"
            "alpha_branch = helper(base + 2)\n"
            "beta_branch = base + 3\n"
            "gamma_branch = base + 4\n"
            "delta_branch = base + 5\n"
            "epsilon_branch = base + 6\n"
            "stable_pre_window = base + 7\n"
            "main_tail = base + 8\n"
            "return carry_pre_window + main_human + alpha_branch + beta_branch + gamma_branch + delta_branch + epsilon_branch + stable_pre_window + main_tail\n",
        )
        revision_id_r3 = repo.commit_all("us12-r3", "2026-03-05T09:00:00Z")

        repo.checkout("main")
        revision_id_r4 = repo.merge_no_ff("feature-alpha", "us12-r4", "2026-03-07T09:00:00Z")

        repo.checkout_new_branch("feature-beta")
        repo.write(
            "src/branch_matrix.py",
            "carry_pre_window = base\n"
            "main_human = sanitize(base + 1)\n"
            "alpha_branch = helper(base + 2)\n"
            "beta_branch = suggest(base + 3)\n"
            "gamma_branch = base + 4\n"
            "delta_branch = base + 5\n"
            "epsilon_branch = base + 6\n"
            "stable_pre_window = base + 7\n"
            "main_tail = base + 8\n"
            "return carry_pre_window + main_human + alpha_branch + beta_branch + gamma_branch + delta_branch + epsilon_branch + stable_pre_window + main_tail\n",
        )
        revision_id_r5 = repo.commit_all("us12-r5", "2026-03-09T09:00:00Z")

        repo.checkout("main")
        revision_id_r6 = repo.merge_no_ff("feature-beta", "us12-r6", "2026-03-11T09:00:00Z")

        repo.checkout_new_branch("feature-gamma")
        repo.write(
            "src/branch_matrix.py",
            "carry_pre_window = base\n"
            "main_human = sanitize(base + 1)\n"
            "alpha_branch = helper(base + 2)\n"
            "beta_branch = suggest(base + 3)\n"
            "gamma_branch = synthesize(base + 4)\n"
            "delta_branch = base + 5\n"
            "epsilon_branch = base + 6\n"
            "stable_pre_window = base + 7\n"
            "main_tail = base + 8\n"
            "return carry_pre_window + main_human + alpha_branch + beta_branch + gamma_branch + delta_branch + epsilon_branch + stable_pre_window + main_tail\n",
        )
        revision_id_r7 = repo.commit_all("us12-r7", "2026-03-13T09:00:00Z")

        repo.checkout("main")
        repo.write(
            "src/branch_matrix.py",
            "carry_pre_window = base\n"
            "main_human = sanitize(base + 1)\n"
            "alpha_branch = helper(base + 2)\n"
            "beta_branch = suggest(base + 3)\n"
            "gamma_branch = base + 4\n"
            "delta_branch = base + 5\n"
            "epsilon_branch = base + 6\n"
            "stable_pre_window = base + 7\n"
            "main_tail = clamp(base + 8)\n"
            "return carry_pre_window + main_human + alpha_branch + beta_branch + gamma_branch + delta_branch + epsilon_branch + stable_pre_window + main_tail\n",
        )
        revision_id_r8 = repo.commit_all("us12-r8", "2026-03-15T09:00:00Z")

        revision_id_r9 = repo.merge_no_ff("feature-gamma", "us12-r9", "2026-03-17T09:00:00Z")

        repo.checkout_new_branch("feature-delta")
        repo.write(
            "src/branch_matrix.py",
            "carry_pre_window = base\n"
            "main_human = sanitize(base + 1)\n"
            "alpha_branch = helper(base + 2)\n"
            "beta_branch = suggest(base + 3)\n"
            "gamma_branch = synthesize(base + 4)\n"
            "delta_branch = blend(base + 5)\n"
            "epsilon_branch = base + 6\n"
            "stable_pre_window = base + 7\n"
            "main_tail = clamp(base + 8)\n"
            "return carry_pre_window + main_human + alpha_branch + beta_branch + gamma_branch + delta_branch + epsilon_branch + stable_pre_window + main_tail\n",
        )
        revision_id_r10 = repo.commit_all("us12-r10", "2026-03-19T09:00:00Z")

        repo.checkout("main")
        revision_id_r11 = repo.merge_no_ff("feature-delta", "us12-r11", "2026-03-20T09:00:00Z")

        repo.checkout_new_branch("feature-epsilon")
        repo.write(
            "src/branch_matrix.py",
            "carry_pre_window = base\n"
            "main_human = sanitize(base + 1)\n"
            "alpha_branch = helper(base + 2)\n"
            "beta_branch = suggest(base + 3)\n"
            "gamma_branch = synthesize(base + 4)\n"
            "delta_branch = blend(base + 5)\n"
            "epsilon_branch = complete(base + 6)\n"
            "stable_pre_window = base + 7\n"
            "main_tail = clamp(base + 8)\n"
            "return carry_pre_window + main_human + alpha_branch + beta_branch + gamma_branch + delta_branch + epsilon_branch + stable_pre_window + main_tail\n",
        )
        revision_id_r12 = repo.commit_all("us12-r12", "2026-03-21T09:00:00Z")

        repo.checkout("main")
        revision_id_r13 = repo.merge_no_ff("feature-epsilon", "us12-r13", "2026-03-22T09:00:00Z")

        repo.write(
            "src/branch_matrix.py",
            "carry_pre_window = base\n"
            "main_human = sanitize(base + 1)\n"
            "alpha_branch = helper(base + 2)\n"
            "beta_branch = suggest(base + 3)\n"
            "gamma_branch = synthesize(base + 4)\n"
            "delta_branch = blend(base + 5)\n"
            "epsilon_branch = manual_override(base + 6)\n"
            "stable_pre_window = base + 7\n"
            "main_tail = clamp(base + 8)\n"
            "return carry_pre_window + main_human + alpha_branch + beta_branch + gamma_branch + delta_branch + epsilon_branch + stable_pre_window + main_tail\n",
        )
        revision_id_r14 = repo.commit_all("us12-r14", "2026-03-23T09:00:00Z")

        repo.write("README.md", "us12 docs update\n")
        revision_id_r15 = repo.commit_all("us12-r15", "2026-03-25T09:00:00Z")

        revision_protocol_r1 = load_json(FIXTURE_DIR / "01_genCodeDesc.json")
        revision_protocol_r2 = load_json(FIXTURE_DIR / "02_genCodeDesc.json")
        revision_protocol_r3 = load_json(FIXTURE_DIR / "03_genCodeDesc.json")
        revision_protocol_r4 = load_json(FIXTURE_DIR / "04_genCodeDesc.json")
        revision_protocol_r5 = load_json(FIXTURE_DIR / "05_genCodeDesc.json")
        revision_protocol_r6 = load_json(FIXTURE_DIR / "06_genCodeDesc.json")
        revision_protocol_r7 = load_json(FIXTURE_DIR / "07_genCodeDesc.json")
        revision_protocol_r8 = load_json(FIXTURE_DIR / "08_genCodeDesc.json")
        revision_protocol_r9 = load_json(FIXTURE_DIR / "09_genCodeDesc.json")
        revision_protocol_r10 = load_json(FIXTURE_DIR / "10_genCodeDesc.json")
        revision_protocol_r11 = load_json(FIXTURE_DIR / "11_genCodeDesc.json")
        revision_protocol_r12 = load_json(FIXTURE_DIR / "12_genCodeDesc.json")
        revision_protocol_r13 = load_json(FIXTURE_DIR / "13_genCodeDesc.json")
        revision_protocol_r14 = load_json(FIXTURE_DIR / "14_genCodeDesc.json")

        write_revision_protocol(protocol_dir, revision_protocol_r1, repo_dir, revision_id_r1)
        write_revision_protocol(protocol_dir, revision_protocol_r2, repo_dir, revision_id_r2)
        write_revision_protocol(protocol_dir, revision_protocol_r3, repo_dir, revision_id_r3)
        write_revision_protocol(protocol_dir, revision_protocol_r4, repo_dir, revision_id_r4)
        write_revision_protocol(protocol_dir, revision_protocol_r5, repo_dir, revision_id_r5)
        write_revision_protocol(protocol_dir, revision_protocol_r6, repo_dir, revision_id_r6)
        write_revision_protocol(protocol_dir, revision_protocol_r7, repo_dir, revision_id_r7)
        write_revision_protocol(protocol_dir, revision_protocol_r8, repo_dir, revision_id_r8)
        write_revision_protocol(protocol_dir, revision_protocol_r9, repo_dir, revision_id_r9)
        write_revision_protocol(protocol_dir, revision_protocol_r10, repo_dir, revision_id_r10)
        write_revision_protocol(protocol_dir, revision_protocol_r11, repo_dir, revision_id_r11)
        write_revision_protocol(protocol_dir, revision_protocol_r12, repo_dir, revision_id_r12)
        write_revision_protocol(protocol_dir, revision_protocol_r13, repo_dir, revision_id_r13)
        write_revision_protocol(protocol_dir, revision_protocol_r14, repo_dir, revision_id_r14)

        return repo_dir, protocol_dir, output_file, {
            "r2": revision_id_r2,
            "r3": revision_id_r3,
            "r5": revision_id_r5,
            "r7": revision_id_r7,
            "r8": revision_id_r8,
            "r10": revision_id_r10,
            "r14": revision_id_r14,
            "r15": revision_id_r15,
        }

    def test_cli_matches_us12_expected_result_with_many_merged_branches(self) -> None:
        query = self._query()
        expected_result = load_json(FIXTURE_DIR / "expected_result.json")

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_dir, protocol_dir, output_file, revision_ids = self._build_history(Path(temp_dir))

            run_cli(repo_dir, output_file, protocol_dir, query)

            actual_result = json.loads(output_file.read_text(encoding="utf-8"))
            expected_result["REPOSITORY"]["repoURL"] = str(repo_dir)
            expected_result["REPOSITORY"]["revisionId"] = revision_ids["r15"]

            self.assertEqual(actual_result, expected_result)

    def test_cli_emits_debug_logs_for_us12_branch_heavy_history(self) -> None:
        query = self._query()

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_dir, protocol_dir, output_file, revision_ids = self._build_history(Path(temp_dir))

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
                    "Finished analysis with totalCodeLines=7 fullGeneratedCodeLines=2 partialGeneratedCodeLines=2",
                    "Metadata repoBranch differs",
                    "Skip out-of-window line src/branch_matrix.py:1",
                    "Skip out-of-window line src/branch_matrix.py:8",
                    "Skip out-of-window line src/branch_matrix.py:10",
                ],
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/branch_matrix.py",
                final_line=2,
                origin_file="src/branch_matrix.py",
                origin_line=2,
                revision_id=revision_ids["r2"],
                classification="human/unattributed",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/branch_matrix.py",
                final_line=3,
                origin_file="src/branch_matrix.py",
                origin_line=3,
                revision_id=revision_ids["r3"],
                classification="100%-ai",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/branch_matrix.py",
                final_line=4,
                origin_file="src/branch_matrix.py",
                origin_line=4,
                revision_id=revision_ids["r5"],
                classification="70%-ai",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/branch_matrix.py",
                final_line=5,
                origin_file="src/branch_matrix.py",
                origin_line=5,
                revision_id=revision_ids["r7"],
                classification="100%-ai",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/branch_matrix.py",
                final_line=6,
                origin_file="src/branch_matrix.py",
                origin_line=6,
                revision_id=revision_ids["r10"],
                classification="40%-ai",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/branch_matrix.py",
                final_line=7,
                origin_file="src/branch_matrix.py",
                origin_line=7,
                revision_id=revision_ids["r14"],
                classification="human/unattributed",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/branch_matrix.py",
                final_line=9,
                origin_file="src/branch_matrix.py",
                origin_line=9,
                revision_id=revision_ids["r8"],
                classification="human/unattributed",
            )
            assert_log_contains_none(
                self,
                result.stderr,
                [
                    "LiveLine src/branch_matrix.py:1 aggregate",
                    "LiveLine src/branch_matrix.py:8 aggregate",
                    "LiveLine src/branch_matrix.py:10 aggregate",
                ],
            )

    def test_cli_info_logging_focuses_on_live_line_aggregation_progress_for_us12(self) -> None:
        query = self._query()

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_dir, protocol_dir, output_file, _revision_ids = self._build_history(Path(temp_dir))

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
                    "LiveLine src/branch_matrix.py:2 aggregate",
                    "LiveLine src/branch_matrix.py:3 aggregate",
                    "LiveLine src/branch_matrix.py:4 aggregate",
                    "LiveLine src/branch_matrix.py:5 aggregate",
                    "LiveLine src/branch_matrix.py:6 aggregate",
                    "LiveLine src/branch_matrix.py:7 aggregate",
                    "LiveLine src/branch_matrix.py:9 aggregate",
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

    def test_cli_preserves_non_first_parent_origins_under_octopus_merge_variant(self) -> None:
        query = {
            "vcsType": "git",
            "repoURL": "https://example.local/repo/us12-variant",
            "repoBranch": "main",
            "metric": "live_changed_source_ratio",
            "model": "A",
            "scope": "A",
            "startTime": "2026-03-01",
            "endTime": "2026-03-31",
            "endRevisionId": "us12-oct-r7",
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            root_dir = Path(temp_dir)
            repo_dir = root_dir / "repo"
            protocol_dir = root_dir / "protocols"
            output_file = root_dir / "out.json"
            repo_dir.mkdir()
            protocol_dir.mkdir()

            repo = GitRepoHarness(repo_dir)
            repo.write(
                "src/alpha_file.py",
                "carry_pre_window = base\n"
                "alpha_line = base + 1\n"
                "stable_pre_window = base + 2\n",
            )
            repo.write(
                "src/beta_file.py",
                "carry_pre_window = base\n"
                "beta_line = base + 1\n"
                "stable_pre_window = base + 2\n",
            )
            repo.write(
                "src/gamma_file.py",
                "carry_pre_window = base\n"
                "gamma_line = base + 1\n"
                "stable_pre_window = base + 2\n",
            )
            repo.write(
                "src/main_file.py",
                "carry_pre_window = base\n"
                "main_human = base + 1\n"
                "stable_pre_window = base + 2\n",
            )
            revision_id_r1 = repo.commit_all("us12-oct-r1", "2026-02-24T09:00:00Z")

            repo.checkout_new_branch("feature-alpha")
            repo.write(
                "src/alpha_file.py",
                "carry_pre_window = base\n"
                "alpha_line = helper(base + 1)\n"
                "stable_pre_window = base + 2\n",
            )
            revision_id_r2 = repo.commit_all("us12-oct-r2", "2026-03-03T09:00:00Z")

            repo.checkout("main")
            repo.checkout_new_branch("feature-beta")
            repo.write(
                "src/beta_file.py",
                "carry_pre_window = base\n"
                "beta_line = suggest(base + 1)\n"
                "stable_pre_window = base + 2\n",
            )
            revision_id_r3 = repo.commit_all("us12-oct-r3", "2026-03-04T09:00:00Z")

            repo.checkout("main")
            repo.checkout_new_branch("feature-gamma")
            repo.write(
                "src/gamma_file.py",
                "carry_pre_window = base\n"
                "gamma_line = synthesize(base + 1)\n"
                "stable_pre_window = base + 2\n",
            )
            revision_id_r4 = repo.commit_all("us12-oct-r4", "2026-03-05T09:00:00Z")

            repo.checkout("main")
            revision_id_r5 = repo.merge_octopus(
                ["feature-alpha", "feature-beta", "feature-gamma"],
                "us12-oct-r5",
                "2026-03-09T09:00:00Z",
            )

            repo.write(
                "src/main_file.py",
                "carry_pre_window = base\n"
                "main_human = sanitize(base + 1)\n"
                "stable_pre_window = base + 2\n",
            )
            revision_id_r6 = repo.commit_all("us12-oct-r6", "2026-03-10T09:00:00Z")

            repo.write("README.md", "us12 octopus docs update\n")
            revision_id_r7 = repo.commit_all("us12-oct-r7", "2026-03-10T09:00:00Z")

            baseline_protocol = self._inline_protocol(repo_branch="main", file_name="src/alpha_file.py")
            baseline_protocol["DETAIL"] = [
                {"fileName": "src/alpha_file.py", "codeLines": []},
                {"fileName": "src/beta_file.py", "codeLines": []},
                {"fileName": "src/gamma_file.py", "codeLines": []},
                {"fileName": "src/main_file.py", "codeLines": []},
            ]
            write_revision_protocol(protocol_dir, baseline_protocol, repo_dir, revision_id_r1)

            alpha_protocol = self._inline_protocol(repo_branch="feature-alpha", file_name="src/alpha_file.py", full_lines=[2])
            alpha_protocol["DETAIL"].append({"fileName": "src/beta_file.py", "codeLines": []})
            alpha_protocol["DETAIL"].append({"fileName": "src/gamma_file.py", "codeLines": []})
            alpha_protocol["DETAIL"].append({"fileName": "src/main_file.py", "codeLines": []})
            write_revision_protocol(protocol_dir, alpha_protocol, repo_dir, revision_id_r2)

            beta_protocol = self._inline_protocol(repo_branch="feature-beta", file_name="src/beta_file.py", partial_lines={2: 60})
            beta_protocol["DETAIL"].append({"fileName": "src/alpha_file.py", "codeLines": []})
            beta_protocol["DETAIL"].append({"fileName": "src/gamma_file.py", "codeLines": []})
            beta_protocol["DETAIL"].append({"fileName": "src/main_file.py", "codeLines": []})
            write_revision_protocol(protocol_dir, beta_protocol, repo_dir, revision_id_r3)

            gamma_protocol = self._inline_protocol(repo_branch="feature-gamma", file_name="src/gamma_file.py", full_lines=[2])
            gamma_protocol["DETAIL"].append({"fileName": "src/alpha_file.py", "codeLines": []})
            gamma_protocol["DETAIL"].append({"fileName": "src/beta_file.py", "codeLines": []})
            gamma_protocol["DETAIL"].append({"fileName": "src/main_file.py", "codeLines": []})
            write_revision_protocol(protocol_dir, gamma_protocol, repo_dir, revision_id_r4)

            merge_protocol = self._inline_protocol(repo_branch="main", file_name="src/main_file.py")
            merge_protocol["DETAIL"] = [
                {"fileName": "src/alpha_file.py", "codeLines": []},
                {"fileName": "src/beta_file.py", "codeLines": []},
                {"fileName": "src/gamma_file.py", "codeLines": []},
                {"fileName": "src/main_file.py", "codeLines": []},
            ]
            write_revision_protocol(protocol_dir, merge_protocol, repo_dir, revision_id_r5)

            main_protocol = self._inline_protocol(repo_branch="main", file_name="src/main_file.py")
            main_protocol["DETAIL"] = [
                {"fileName": "src/alpha_file.py", "codeLines": []},
                {"fileName": "src/beta_file.py", "codeLines": []},
                {"fileName": "src/gamma_file.py", "codeLines": []},
                {"fileName": "src/main_file.py", "codeLines": []},
            ]
            write_revision_protocol(protocol_dir, main_protocol, repo_dir, revision_id_r6)

            result = run_cli(
                repo_dir,
                output_file,
                protocol_dir,
                query,
                extra_args=["--logLevel", "debug"],
            )

            self.assertEqual(
                json.loads(output_file.read_text(encoding="utf-8")),
                {
                    "protocolName": "generatedTextDesc",
                    "protocolVersion": "26.03",
                    "SUMMARY": {
                        "totalCodeLines": 4,
                        "fullGeneratedCodeLines": 2,
                        "partialGeneratedCodeLines": 1,
                    },
                    "REPOSITORY": {
                        "vcsType": "git",
                        "repoURL": str(repo_dir),
                        "repoBranch": "main",
                        "revisionId": revision_id_r7,
                    },
                },
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/alpha_file.py",
                final_line=2,
                origin_file="src/alpha_file.py",
                origin_line=2,
                revision_id=revision_id_r2,
                classification="100%-ai",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/beta_file.py",
                final_line=2,
                origin_file="src/beta_file.py",
                origin_line=2,
                revision_id=revision_id_r3,
                classification="60%-ai",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/gamma_file.py",
                final_line=2,
                origin_file="src/gamma_file.py",
                origin_line=2,
                revision_id=revision_id_r4,
                classification="100%-ai",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/main_file.py",
                final_line=2,
                origin_file="src/main_file.py",
                origin_line=2,
                revision_id=revision_id_r6,
                classification="human/unattributed",
            )

    def test_cli_preserves_pre_rename_branch_origin_after_rename_and_merge_variant(self) -> None:
        query = {
            "vcsType": "git",
            "repoURL": "https://example.local/repo/us12-rename-merge",
            "repoBranch": "main",
            "metric": "live_changed_source_ratio",
            "model": "A",
            "scope": "A",
            "startTime": "2026-03-01",
            "endTime": "2026-03-31",
            "endRevisionId": "us12-rm-r7",
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            root_dir = Path(temp_dir)
            repo_dir = root_dir / "repo"
            protocol_dir = root_dir / "protocols"
            output_file = root_dir / "out.json"
            repo_dir.mkdir()
            protocol_dir.mkdir()

            repo = GitRepoHarness(repo_dir)
            repo.write(
                "src/legacy_merge_name.py",
                "carry_pre_window = base\n"
                "branch_human = base + 1\n"
                "branch_full = base + 2\n"
                "branch_partial = base + 3\n",
            )
            repo.write(
                "src/main_side.py",
                "carry_pre_window = base\n"
                "main_human = base + 1\n"
                "stable_pre_window = base + 2\n",
            )
            revision_id_r1 = repo.commit_all("us12-rm-r1", "2026-02-24T09:00:00Z")

            repo.checkout_new_branch("feature-rename")
            repo.write(
                "src/legacy_merge_name.py",
                "carry_pre_window = base\n"
                "branch_human = sanitize(base + 1)\n"
                "branch_full = base + 2\n"
                "branch_partial = base + 3\n",
            )
            revision_id_r2 = repo.commit_all("us12-rm-r2", "2026-03-03T09:00:00Z")

            repo.rename("src/legacy_merge_name.py", "src/merged_name.py")
            revision_id_r3 = repo.commit_all("us12-rm-r3", "2026-03-05T09:00:00Z")

            repo.write(
                "src/merged_name.py",
                "carry_pre_window = base\n"
                "branch_human = sanitize(base + 1)\n"
                "branch_full = helper(base + 2)\n"
                "branch_partial = suggest(base + 3)\n",
            )
            revision_id_r4 = repo.commit_all("us12-rm-r4", "2026-03-07T09:00:00Z")

            repo.checkout("main")
            repo.write(
                "src/main_side.py",
                "carry_pre_window = base\n"
                "main_human = normalize(base + 1)\n"
                "stable_pre_window = base + 2\n",
            )
            revision_id_r5 = repo.commit_all("us12-rm-r5", "2026-03-09T09:00:00Z")

            revision_id_r6 = repo.merge_no_ff("feature-rename", "us12-rm-r6", "2026-03-12T09:00:00Z")

            repo.write("README.md", "us12 rename merge docs update\n")
            revision_id_r7 = repo.commit_all("us12-rm-r7", "2026-03-14T09:00:00Z")

            baseline_protocol = self._inline_protocol(repo_branch="main", file_name="src/legacy_merge_name.py")
            baseline_protocol["DETAIL"] = [
                {"fileName": "src/legacy_merge_name.py", "codeLines": []},
                {"fileName": "src/main_side.py", "codeLines": []},
            ]
            write_revision_protocol(protocol_dir, baseline_protocol, repo_dir, revision_id_r1)

            pre_rename_human_protocol = self._inline_protocol(repo_branch="feature-rename", file_name="src/legacy_merge_name.py")
            pre_rename_human_protocol["DETAIL"].append({"fileName": "src/main_side.py", "codeLines": []})
            write_revision_protocol(protocol_dir, pre_rename_human_protocol, repo_dir, revision_id_r2)

            rename_protocol = self._inline_protocol(repo_branch="feature-rename", file_name="src/merged_name.py")
            rename_protocol["DETAIL"].append({"fileName": "src/main_side.py", "codeLines": []})
            write_revision_protocol(protocol_dir, rename_protocol, repo_dir, revision_id_r3)

            branch_ai_protocol = self._inline_protocol(
                repo_branch="feature-rename",
                file_name="src/merged_name.py",
                full_lines=[3],
                partial_lines={4: 60},
            )
            branch_ai_protocol["DETAIL"].append({"fileName": "src/main_side.py", "codeLines": []})
            write_revision_protocol(protocol_dir, branch_ai_protocol, repo_dir, revision_id_r4)

            main_protocol = self._inline_protocol(repo_branch="main", file_name="src/main_side.py")
            main_protocol["DETAIL"] = [
                {"fileName": "src/merged_name.py", "codeLines": []},
                {"fileName": "src/main_side.py", "codeLines": []},
            ]
            write_revision_protocol(protocol_dir, main_protocol, repo_dir, revision_id_r5)

            merge_protocol = self._inline_protocol(repo_branch="main", file_name="src/merged_name.py")
            merge_protocol["DETAIL"] = [
                {"fileName": "src/merged_name.py", "codeLines": []},
                {"fileName": "src/main_side.py", "codeLines": []},
            ]
            write_revision_protocol(protocol_dir, merge_protocol, repo_dir, revision_id_r6)

            result = run_cli(
                repo_dir,
                output_file,
                protocol_dir,
                query,
                extra_args=["--logLevel", "debug"],
            )

            self.assertEqual(
                json.loads(output_file.read_text(encoding="utf-8")),
                {
                    "protocolName": "generatedTextDesc",
                    "protocolVersion": "26.03",
                    "SUMMARY": {
                        "totalCodeLines": 4,
                        "fullGeneratedCodeLines": 1,
                        "partialGeneratedCodeLines": 1,
                    },
                    "REPOSITORY": {
                        "vcsType": "git",
                        "repoURL": str(repo_dir),
                        "repoBranch": "main",
                        "revisionId": revision_id_r7,
                    },
                },
            )
            assert_log_contains_all(
                self,
                result.stderr,
                [
                    "Metadata repoBranch differs",
                    "Skip out-of-window line src/merged_name.py:1",
                    "Skip out-of-window line src/main_side.py:1",
                    "Skip out-of-window line src/main_side.py:3",
                ],
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/merged_name.py",
                final_line=2,
                origin_file="src/legacy_merge_name.py",
                origin_line=2,
                revision_id=revision_id_r2,
                classification="human/unattributed",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/merged_name.py",
                final_line=3,
                origin_file="src/merged_name.py",
                origin_line=3,
                revision_id=revision_id_r4,
                classification="100%-ai",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/merged_name.py",
                final_line=4,
                origin_file="src/merged_name.py",
                origin_line=4,
                revision_id=revision_id_r4,
                classification="60%-ai",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/main_side.py",
                final_line=2,
                origin_file="src/main_side.py",
                origin_line=2,
                revision_id=revision_id_r5,
                classification="human/unattributed",
            )

    def test_cli_preserves_rename_lineage_inside_octopus_merge_variant(self) -> None:
        query = {
            "vcsType": "git",
            "repoURL": "https://example.local/repo/us12-rename-octopus",
            "repoBranch": "main",
            "metric": "live_changed_source_ratio",
            "model": "A",
            "scope": "A",
            "startTime": "2026-03-01",
            "endTime": "2026-03-31",
            "endRevisionId": "us12-ro-r8",
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            root_dir = Path(temp_dir)
            repo_dir = root_dir / "repo"
            protocol_dir = root_dir / "protocols"
            output_file = root_dir / "out.json"
            repo_dir.mkdir()
            protocol_dir.mkdir()

            repo = GitRepoHarness(repo_dir)
            repo.write(
                "src/legacy_alpha.py",
                "carry_pre_window = base\n"
                "rename_human = base + 1\n"
                "rename_ai = base + 2\n"
                "stable_pre_window = base + 3\n",
            )
            repo.write(
                "src/beta_branch.py",
                "carry_pre_window = base\n"
                "beta_ai = base + 1\n"
                "stable_pre_window = base + 2\n",
            )
            repo.write(
                "src/gamma_branch.py",
                "carry_pre_window = base\n"
                "gamma_ai = base + 1\n"
                "stable_pre_window = base + 2\n",
            )
            repo.write(
                "src/main_side.py",
                "carry_pre_window = base\n"
                "main_human = base + 1\n"
                "stable_pre_window = base + 2\n",
            )
            revision_id_r1 = repo.commit_all("us12-ro-r1", "2026-02-24T09:00:00Z")

            repo.checkout_new_branch("feature-rename")
            repo.write(
                "src/legacy_alpha.py",
                "carry_pre_window = base\n"
                "rename_human = sanitize(base + 1)\n"
                "rename_ai = base + 2\n"
                "stable_pre_window = base + 3\n",
            )
            revision_id_r2 = repo.commit_all("us12-ro-r2", "2026-03-03T09:00:00Z")
            repo.rename("src/legacy_alpha.py", "src/merged_alpha.py")
            revision_id_r3 = repo.commit_all("us12-ro-r3", "2026-03-04T09:00:00Z")
            repo.write(
                "src/merged_alpha.py",
                "carry_pre_window = base\n"
                "rename_human = sanitize(base + 1)\n"
                "rename_ai = helper(base + 2)\n"
                "stable_pre_window = base + 3\n",
            )
            revision_id_r4 = repo.commit_all("us12-ro-r4", "2026-03-05T09:00:00Z")

            repo.checkout("main")
            repo.checkout_new_branch("feature-beta")
            repo.write(
                "src/beta_branch.py",
                "carry_pre_window = base\n"
                "beta_ai = suggest(base + 1)\n"
                "stable_pre_window = base + 2\n",
            )
            revision_id_r5 = repo.commit_all("us12-ro-r5", "2026-03-06T09:00:00Z")

            repo.checkout("main")
            repo.checkout_new_branch("feature-gamma")
            repo.write(
                "src/gamma_branch.py",
                "carry_pre_window = base\n"
                "gamma_ai = synthesize(base + 1)\n"
                "stable_pre_window = base + 2\n",
            )
            revision_id_r6 = repo.commit_all("us12-ro-r6", "2026-03-07T09:00:00Z")

            repo.checkout("main")
            revision_id_r7 = repo.merge_octopus(
                ["feature-rename", "feature-beta", "feature-gamma"],
                "us12-ro-r7",
                "2026-03-10T09:00:00Z",
            )
            repo.write(
                "src/main_side.py",
                "carry_pre_window = base\n"
                "main_human = normalize(base + 1)\n"
                "stable_pre_window = base + 2\n",
            )
            repo.commit_all("us12-ro-r7b", "2026-03-11T09:00:00Z")
            repo.write("README.md", "us12 rename octopus docs update\n")
            revision_id_r8 = repo.commit_all("us12-ro-r8", "2026-03-12T09:00:00Z")

            baseline_protocol = self._inline_protocol(repo_branch="main", file_name="src/main_side.py")
            baseline_protocol["DETAIL"] = [
                {"fileName": "src/legacy_alpha.py", "codeLines": []},
                {"fileName": "src/beta_branch.py", "codeLines": []},
                {"fileName": "src/gamma_branch.py", "codeLines": []},
                {"fileName": "src/main_side.py", "codeLines": []},
            ]
            write_revision_protocol(protocol_dir, baseline_protocol, repo_dir, revision_id_r1)

            rename_human_protocol = self._inline_protocol(repo_branch="feature-rename", file_name="src/legacy_alpha.py")
            rename_human_protocol["DETAIL"] = [
                {"fileName": "src/legacy_alpha.py", "codeLines": []},
                {"fileName": "src/beta_branch.py", "codeLines": []},
                {"fileName": "src/gamma_branch.py", "codeLines": []},
                {"fileName": "src/main_side.py", "codeLines": []},
            ]
            write_revision_protocol(protocol_dir, rename_human_protocol, repo_dir, revision_id_r2)

            rename_only_protocol = self._inline_protocol(repo_branch="feature-rename", file_name="src/merged_alpha.py")
            rename_only_protocol["DETAIL"] = [
                {"fileName": "src/merged_alpha.py", "codeLines": []},
                {"fileName": "src/beta_branch.py", "codeLines": []},
                {"fileName": "src/gamma_branch.py", "codeLines": []},
                {"fileName": "src/main_side.py", "codeLines": []},
            ]
            write_revision_protocol(protocol_dir, rename_only_protocol, repo_dir, revision_id_r3)

            rename_ai_protocol = self._inline_protocol(repo_branch="feature-rename", file_name="src/merged_alpha.py", full_lines=[3])
            rename_ai_protocol["DETAIL"].append({"fileName": "src/beta_branch.py", "codeLines": []})
            rename_ai_protocol["DETAIL"].append({"fileName": "src/gamma_branch.py", "codeLines": []})
            rename_ai_protocol["DETAIL"].append({"fileName": "src/main_side.py", "codeLines": []})
            write_revision_protocol(protocol_dir, rename_ai_protocol, repo_dir, revision_id_r4)

            beta_protocol = self._inline_protocol(repo_branch="feature-beta", file_name="src/beta_branch.py", partial_lines={2: 60})
            beta_protocol["DETAIL"].append({"fileName": "src/merged_alpha.py", "codeLines": []})
            beta_protocol["DETAIL"].append({"fileName": "src/gamma_branch.py", "codeLines": []})
            beta_protocol["DETAIL"].append({"fileName": "src/main_side.py", "codeLines": []})
            write_revision_protocol(protocol_dir, beta_protocol, repo_dir, revision_id_r5)

            gamma_protocol = self._inline_protocol(repo_branch="feature-gamma", file_name="src/gamma_branch.py", full_lines=[2])
            gamma_protocol["DETAIL"].append({"fileName": "src/merged_alpha.py", "codeLines": []})
            gamma_protocol["DETAIL"].append({"fileName": "src/beta_branch.py", "codeLines": []})
            gamma_protocol["DETAIL"].append({"fileName": "src/main_side.py", "codeLines": []})
            write_revision_protocol(protocol_dir, gamma_protocol, repo_dir, revision_id_r6)

            octopus_protocol = self._inline_protocol(repo_branch="main", file_name="src/main_side.py")
            octopus_protocol["DETAIL"] = [
                {"fileName": "src/merged_alpha.py", "codeLines": []},
                {"fileName": "src/beta_branch.py", "codeLines": []},
                {"fileName": "src/gamma_branch.py", "codeLines": []},
                {"fileName": "src/main_side.py", "codeLines": []},
            ]
            write_revision_protocol(protocol_dir, octopus_protocol, repo_dir, revision_id_r7)

            main_protocol = self._inline_protocol(repo_branch="main", file_name="src/main_side.py")
            main_protocol["DETAIL"] = [
                {"fileName": "src/merged_alpha.py", "codeLines": []},
                {"fileName": "src/beta_branch.py", "codeLines": []},
                {"fileName": "src/gamma_branch.py", "codeLines": []},
                {"fileName": "src/main_side.py", "codeLines": []},
            ]
            write_revision_protocol(protocol_dir, main_protocol, repo_dir, repo.commit_ids["us12-ro-r7b"])

            result = run_cli(
                repo_dir,
                output_file,
                protocol_dir,
                query,
                extra_args=["--logLevel", "debug"],
            )

            self.assertEqual(
                json.loads(output_file.read_text(encoding="utf-8")),
                {
                    "protocolName": "generatedTextDesc",
                    "protocolVersion": "26.03",
                    "SUMMARY": {
                        "totalCodeLines": 5,
                        "fullGeneratedCodeLines": 2,
                        "partialGeneratedCodeLines": 1,
                    },
                    "REPOSITORY": {
                        "vcsType": "git",
                        "repoURL": str(repo_dir),
                        "repoBranch": "main",
                        "revisionId": revision_id_r8,
                    },
                },
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/merged_alpha.py",
                final_line=2,
                origin_file="src/legacy_alpha.py",
                origin_line=2,
                revision_id=revision_id_r2,
                classification="human/unattributed",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/merged_alpha.py",
                final_line=3,
                origin_file="src/merged_alpha.py",
                origin_line=3,
                revision_id=revision_id_r4,
                classification="100%-ai",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/beta_branch.py",
                final_line=2,
                origin_file="src/beta_branch.py",
                origin_line=2,
                revision_id=revision_id_r5,
                classification="60%-ai",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/gamma_branch.py",
                final_line=2,
                origin_file="src/gamma_branch.py",
                origin_line=2,
                revision_id=revision_id_r6,
                classification="100%-ai",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/main_side.py",
                final_line=2,
                origin_file="src/main_side.py",
                origin_line=2,
                revision_id=repo.commit_ids["us12-ro-r7b"],
                classification="human/unattributed",
            )

    def test_cli_preserves_double_rename_lineage_after_merge_variant(self) -> None:
        query = {
            "vcsType": "git",
            "repoURL": "https://example.local/repo/us12-double-rename",
            "repoBranch": "main",
            "metric": "live_changed_source_ratio",
            "model": "A",
            "scope": "A",
            "startTime": "2026-03-01",
            "endTime": "2026-03-31",
            "endRevisionId": "us12-dr-r9",
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            root_dir = Path(temp_dir)
            repo_dir = root_dir / "repo"
            protocol_dir = root_dir / "protocols"
            output_file = root_dir / "out.json"
            repo_dir.mkdir()
            protocol_dir.mkdir()

            repo = GitRepoHarness(repo_dir)
            repo.write(
                "src/legacy_round1.py",
                "carry_pre_window = base\n"
                "rename_human = base + 1\n"
                "rename_full = base + 2\n"
                "rename_partial = base + 3\n",
            )
            repo.write(
                "src/main_companion.py",
                "carry_pre_window = base\n"
                "main_human = base + 1\n"
                "stable_pre_window = base + 2\n",
            )
            revision_id_r1 = repo.commit_all("us12-dr-r1", "2026-02-24T09:00:00Z")

            repo.checkout_new_branch("feature-double-rename")
            repo.write(
                "src/legacy_round1.py",
                "carry_pre_window = base\n"
                "rename_human = sanitize(base + 1)\n"
                "rename_full = base + 2\n"
                "rename_partial = base + 3\n",
            )
            revision_id_r2 = repo.commit_all("us12-dr-r2", "2026-03-03T09:00:00Z")

            repo.rename("src/legacy_round1.py", "src/intermediate_round2.py")
            revision_id_r3 = repo.commit_all("us12-dr-r3", "2026-03-04T09:00:00Z")

            repo.write(
                "src/intermediate_round2.py",
                "carry_pre_window = base\n"
                "rename_human = sanitize(base + 1)\n"
                "rename_full = helper(base + 2)\n"
                "rename_partial = base + 3\n",
            )
            revision_id_r4 = repo.commit_all("us12-dr-r4", "2026-03-05T09:00:00Z")

            repo.rename("src/intermediate_round2.py", "src/final_round3.py")
            revision_id_r5 = repo.commit_all("us12-dr-r5", "2026-03-06T09:00:00Z")

            repo.write(
                "src/final_round3.py",
                "carry_pre_window = base\n"
                "rename_human = sanitize(base + 1)\n"
                "rename_full = helper(base + 2)\n"
                "rename_partial = suggest(base + 3)\n",
            )
            revision_id_r6 = repo.commit_all("us12-dr-r6", "2026-03-07T09:00:00Z")

            repo.checkout("main")
            repo.write(
                "src/main_companion.py",
                "carry_pre_window = base\n"
                "main_human = normalize(base + 1)\n"
                "stable_pre_window = base + 2\n",
            )
            revision_id_r7 = repo.commit_all("us12-dr-r7", "2026-03-09T09:00:00Z")

            revision_id_r8 = repo.merge_no_ff("feature-double-rename", "us12-dr-r8", "2026-03-11T09:00:00Z")

            repo.write("README.md", "us12 double rename docs update\n")
            revision_id_r9 = repo.commit_all("us12-dr-r9", "2026-03-12T09:00:00Z")

            baseline_protocol = self._inline_protocol(repo_branch="main", file_name="src/legacy_round1.py")
            baseline_protocol["DETAIL"] = [
                {"fileName": "src/legacy_round1.py", "codeLines": []},
                {"fileName": "src/main_companion.py", "codeLines": []},
            ]
            write_revision_protocol(protocol_dir, baseline_protocol, repo_dir, revision_id_r1)

            first_change_protocol = self._inline_protocol(repo_branch="feature-double-rename", file_name="src/legacy_round1.py")
            first_change_protocol["DETAIL"].append({"fileName": "src/main_companion.py", "codeLines": []})
            write_revision_protocol(protocol_dir, first_change_protocol, repo_dir, revision_id_r2)

            first_rename_protocol = self._inline_protocol(repo_branch="feature-double-rename", file_name="src/intermediate_round2.py")
            first_rename_protocol["DETAIL"].append({"fileName": "src/main_companion.py", "codeLines": []})
            write_revision_protocol(protocol_dir, first_rename_protocol, repo_dir, revision_id_r3)

            middle_ai_protocol = self._inline_protocol(repo_branch="feature-double-rename", file_name="src/intermediate_round2.py", full_lines=[3])
            middle_ai_protocol["DETAIL"].append({"fileName": "src/main_companion.py", "codeLines": []})
            write_revision_protocol(protocol_dir, middle_ai_protocol, repo_dir, revision_id_r4)

            second_rename_protocol = self._inline_protocol(repo_branch="feature-double-rename", file_name="src/final_round3.py")
            second_rename_protocol["DETAIL"].append({"fileName": "src/main_companion.py", "codeLines": []})
            write_revision_protocol(protocol_dir, second_rename_protocol, repo_dir, revision_id_r5)

            final_ai_protocol = self._inline_protocol(repo_branch="feature-double-rename", file_name="src/final_round3.py", partial_lines={4: 60})
            final_ai_protocol["DETAIL"].append({"fileName": "src/main_companion.py", "codeLines": []})
            write_revision_protocol(protocol_dir, final_ai_protocol, repo_dir, revision_id_r6)

            main_protocol = self._inline_protocol(repo_branch="main", file_name="src/main_companion.py")
            main_protocol["DETAIL"] = [
                {"fileName": "src/final_round3.py", "codeLines": []},
                {"fileName": "src/main_companion.py", "codeLines": []},
            ]
            write_revision_protocol(protocol_dir, main_protocol, repo_dir, revision_id_r7)

            merge_protocol = self._inline_protocol(repo_branch="main", file_name="src/final_round3.py")
            merge_protocol["DETAIL"] = [
                {"fileName": "src/final_round3.py", "codeLines": []},
                {"fileName": "src/main_companion.py", "codeLines": []},
            ]
            write_revision_protocol(protocol_dir, merge_protocol, repo_dir, revision_id_r8)

            result = run_cli(
                repo_dir,
                output_file,
                protocol_dir,
                query,
                extra_args=["--logLevel", "debug"],
            )

            self.assertEqual(
                json.loads(output_file.read_text(encoding="utf-8")),
                {
                    "protocolName": "generatedTextDesc",
                    "protocolVersion": "26.03",
                    "SUMMARY": {
                        "totalCodeLines": 4,
                        "fullGeneratedCodeLines": 1,
                        "partialGeneratedCodeLines": 1,
                    },
                    "REPOSITORY": {
                        "vcsType": "git",
                        "repoURL": str(repo_dir),
                        "repoBranch": "main",
                        "revisionId": revision_id_r9,
                    },
                },
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/final_round3.py",
                final_line=2,
                origin_file="src/legacy_round1.py",
                origin_line=2,
                revision_id=revision_id_r2,
                classification="human/unattributed",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/final_round3.py",
                final_line=3,
                origin_file="src/intermediate_round2.py",
                origin_line=3,
                revision_id=revision_id_r4,
                classification="100%-ai",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/final_round3.py",
                final_line=4,
                origin_file="src/final_round3.py",
                origin_line=4,
                revision_id=revision_id_r6,
                classification="60%-ai",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/main_companion.py",
                final_line=2,
                origin_file="src/main_companion.py",
                origin_line=2,
                revision_id=revision_id_r7,
                classification="human/unattributed",
            )

    def test_cli_preserves_rename_lineage_across_branch_handoff_merges_variant(self) -> None:
        query = {
            "vcsType": "git",
            "repoURL": "https://example.local/repo/us12-branch-handoff",
            "repoBranch": "main",
            "metric": "live_changed_source_ratio",
            "model": "A",
            "scope": "A",
            "startTime": "2026-03-01",
            "endTime": "2026-03-31",
            "endRevisionId": "us12-bh-r10",
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            root_dir = Path(temp_dir)
            repo_dir = root_dir / "repo"
            protocol_dir = root_dir / "protocols"
            output_file = root_dir / "out.json"
            repo_dir.mkdir()
            protocol_dir.mkdir()

            repo = GitRepoHarness(repo_dir)
            repo.write(
                "src/stage_one_name.py",
                "carry_pre_window = base\n"
                "handoff_human = base + 1\n"
                "handoff_full = base + 2\n"
                "handoff_partial = base + 3\n",
            )
            repo.write(
                "src/main_anchor.py",
                "carry_pre_window = base\n"
                "main_human = base + 1\n"
                "stable_pre_window = base + 2\n",
            )
            revision_id_r1 = repo.commit_all("us12-bh-r1", "2026-02-24T09:00:00Z")

            repo.checkout_new_branch("feature-alpha")
            repo.write(
                "src/stage_one_name.py",
                "carry_pre_window = base\n"
                "handoff_human = sanitize(base + 1)\n"
                "handoff_full = base + 2\n"
                "handoff_partial = base + 3\n",
            )
            revision_id_r2 = repo.commit_all("us12-bh-r2", "2026-03-03T09:00:00Z")

            repo.rename("src/stage_one_name.py", "src/stage_two_name.py")
            revision_id_r3 = repo.commit_all("us12-bh-r3", "2026-03-04T09:00:00Z")

            repo.write(
                "src/stage_two_name.py",
                "carry_pre_window = base\n"
                "handoff_human = sanitize(base + 1)\n"
                "handoff_full = helper(base + 2)\n"
                "handoff_partial = base + 3\n",
            )
            revision_id_r4 = repo.commit_all("us12-bh-r4", "2026-03-05T09:00:00Z")

            repo.checkout("main")
            repo.checkout_new_branch("integration-handoff")
            revision_id_r5 = repo.merge_no_ff("feature-alpha", "us12-bh-r5", "2026-03-07T09:00:00Z")

            repo.rename("src/stage_two_name.py", "src/stage_three_name.py")
            revision_id_r6 = repo.commit_all("us12-bh-r6", "2026-03-08T09:00:00Z")

            repo.write(
                "src/stage_three_name.py",
                "carry_pre_window = base\n"
                "handoff_human = sanitize(base + 1)\n"
                "handoff_full = helper(base + 2)\n"
                "handoff_partial = suggest(base + 3)\n",
            )
            revision_id_r7 = repo.commit_all("us12-bh-r7", "2026-03-09T09:00:00Z")

            repo.checkout("main")
            repo.write(
                "src/main_anchor.py",
                "carry_pre_window = base\n"
                "main_human = normalize(base + 1)\n"
                "stable_pre_window = base + 2\n",
            )
            revision_id_r8 = repo.commit_all("us12-bh-r8", "2026-03-10T09:00:00Z")

            revision_id_r9 = repo.merge_no_ff("integration-handoff", "us12-bh-r9", "2026-03-12T09:00:00Z")

            repo.write("README.md", "us12 branch handoff docs update\n")
            revision_id_r10 = repo.commit_all("us12-bh-r10", "2026-03-13T09:00:00Z")

            baseline_protocol = self._inline_protocol(repo_branch="main", file_name="src/stage_one_name.py")
            baseline_protocol["DETAIL"] = [
                {"fileName": "src/stage_one_name.py", "codeLines": []},
                {"fileName": "src/main_anchor.py", "codeLines": []},
            ]
            write_revision_protocol(protocol_dir, baseline_protocol, repo_dir, revision_id_r1)

            first_change_protocol = self._inline_protocol(repo_branch="feature-alpha", file_name="src/stage_one_name.py")
            first_change_protocol["DETAIL"].append({"fileName": "src/main_anchor.py", "codeLines": []})
            write_revision_protocol(protocol_dir, first_change_protocol, repo_dir, revision_id_r2)

            first_rename_protocol = self._inline_protocol(repo_branch="feature-alpha", file_name="src/stage_two_name.py")
            first_rename_protocol["DETAIL"].append({"fileName": "src/main_anchor.py", "codeLines": []})
            write_revision_protocol(protocol_dir, first_rename_protocol, repo_dir, revision_id_r3)

            first_ai_protocol = self._inline_protocol(repo_branch="feature-alpha", file_name="src/stage_two_name.py", full_lines=[3])
            first_ai_protocol["DETAIL"].append({"fileName": "src/main_anchor.py", "codeLines": []})
            write_revision_protocol(protocol_dir, first_ai_protocol, repo_dir, revision_id_r4)

            handoff_merge_protocol = self._inline_protocol(repo_branch="integration-handoff", file_name="src/stage_two_name.py")
            handoff_merge_protocol["DETAIL"] = [
                {"fileName": "src/stage_two_name.py", "codeLines": []},
                {"fileName": "src/main_anchor.py", "codeLines": []},
            ]
            write_revision_protocol(protocol_dir, handoff_merge_protocol, repo_dir, revision_id_r5)

            second_rename_protocol = self._inline_protocol(repo_branch="integration-handoff", file_name="src/stage_three_name.py")
            second_rename_protocol["DETAIL"].append({"fileName": "src/main_anchor.py", "codeLines": []})
            write_revision_protocol(protocol_dir, second_rename_protocol, repo_dir, revision_id_r6)

            second_ai_protocol = self._inline_protocol(repo_branch="integration-handoff", file_name="src/stage_three_name.py", partial_lines={4: 60})
            second_ai_protocol["DETAIL"].append({"fileName": "src/main_anchor.py", "codeLines": []})
            write_revision_protocol(protocol_dir, second_ai_protocol, repo_dir, revision_id_r7)

            main_protocol = self._inline_protocol(repo_branch="main", file_name="src/main_anchor.py")
            main_protocol["DETAIL"] = [
                {"fileName": "src/stage_three_name.py", "codeLines": []},
                {"fileName": "src/main_anchor.py", "codeLines": []},
            ]
            write_revision_protocol(protocol_dir, main_protocol, repo_dir, revision_id_r8)

            final_merge_protocol = self._inline_protocol(repo_branch="main", file_name="src/stage_three_name.py")
            final_merge_protocol["DETAIL"] = [
                {"fileName": "src/stage_three_name.py", "codeLines": []},
                {"fileName": "src/main_anchor.py", "codeLines": []},
            ]
            write_revision_protocol(protocol_dir, final_merge_protocol, repo_dir, revision_id_r9)

            result = run_cli(
                repo_dir,
                output_file,
                protocol_dir,
                query,
                extra_args=["--logLevel", "debug"],
            )

            self.assertEqual(
                json.loads(output_file.read_text(encoding="utf-8")),
                {
                    "protocolName": "generatedTextDesc",
                    "protocolVersion": "26.03",
                    "SUMMARY": {
                        "totalCodeLines": 4,
                        "fullGeneratedCodeLines": 1,
                        "partialGeneratedCodeLines": 1,
                    },
                    "REPOSITORY": {
                        "vcsType": "git",
                        "repoURL": str(repo_dir),
                        "repoBranch": "main",
                        "revisionId": revision_id_r10,
                    },
                },
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/stage_three_name.py",
                final_line=2,
                origin_file="src/stage_one_name.py",
                origin_line=2,
                revision_id=revision_id_r2,
                classification="human/unattributed",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/stage_three_name.py",
                final_line=3,
                origin_file="src/stage_two_name.py",
                origin_line=3,
                revision_id=revision_id_r4,
                classification="100%-ai",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/stage_three_name.py",
                final_line=4,
                origin_file="src/stage_three_name.py",
                origin_line=4,
                revision_id=revision_id_r7,
                classification="60%-ai",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/main_anchor.py",
                final_line=2,
                origin_file="src/main_anchor.py",
                origin_line=2,
                revision_id=revision_id_r8,
                classification="human/unattributed",
            )

    def test_cli_preserves_parallel_rename_lineages_from_two_merged_branches_variant(self) -> None:
        query = {
            "vcsType": "git",
            "repoURL": "https://example.local/repo/us12-parallel-renames",
            "repoBranch": "main",
            "metric": "live_changed_source_ratio",
            "model": "A",
            "scope": "A",
            "startTime": "2026-03-01",
            "endTime": "2026-03-31",
            "endRevisionId": "us12-pr-r10",
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            root_dir = Path(temp_dir)
            repo_dir = root_dir / "repo"
            protocol_dir = root_dir / "protocols"
            output_file = root_dir / "out.json"
            repo_dir.mkdir()
            protocol_dir.mkdir()

            repo = GitRepoHarness(repo_dir)
            repo.write(
                "src/alpha_legacy.py",
                "carry_pre_window = base\n"
                "alpha_human = base + 1\n"
                "alpha_full = base + 2\n",
            )
            repo.write(
                "src/beta_legacy.py",
                "carry_pre_window = base\n"
                "beta_human = base + 1\n"
                "beta_partial = base + 2\n",
            )
            repo.write(
                "src/main_parallel.py",
                "carry_pre_window = base\n"
                "main_human = base + 1\n"
                "stable_pre_window = base + 2\n",
            )
            revision_id_r1 = repo.commit_all("us12-pr-r1", "2026-02-24T09:00:00Z")

            repo.checkout_new_branch("feature-alpha")
            repo.write(
                "src/alpha_legacy.py",
                "carry_pre_window = base\n"
                "alpha_human = sanitize(base + 1)\n"
                "alpha_full = base + 2\n",
            )
            revision_id_r2 = repo.commit_all("us12-pr-r2", "2026-03-03T09:00:00Z")
            repo.rename("src/alpha_legacy.py", "src/alpha_final.py")
            revision_id_r3 = repo.commit_all("us12-pr-r3", "2026-03-04T09:00:00Z")
            repo.write(
                "src/alpha_final.py",
                "carry_pre_window = base\n"
                "alpha_human = sanitize(base + 1)\n"
                "alpha_full = helper(base + 2)\n",
            )
            revision_id_r4 = repo.commit_all("us12-pr-r4", "2026-03-05T09:00:00Z")

            repo.checkout("main")
            repo.checkout_new_branch("feature-beta")
            repo.write(
                "src/beta_legacy.py",
                "carry_pre_window = base\n"
                "beta_human = normalize(base + 1)\n"
                "beta_partial = base + 2\n",
            )
            revision_id_r5 = repo.commit_all("us12-pr-r5", "2026-03-06T09:00:00Z")
            repo.rename("src/beta_legacy.py", "src/beta_final.py")
            revision_id_r6 = repo.commit_all("us12-pr-r6", "2026-03-07T09:00:00Z")
            repo.write(
                "src/beta_final.py",
                "carry_pre_window = base\n"
                "beta_human = normalize(base + 1)\n"
                "beta_partial = suggest(base + 2)\n",
            )
            revision_id_r7 = repo.commit_all("us12-pr-r7", "2026-03-08T09:00:00Z")

            repo.checkout("main")
            revision_id_r8 = repo.merge_no_ff("feature-alpha", "us12-pr-r8", "2026-03-10T09:00:00Z")
            revision_id_r9 = repo.merge_no_ff("feature-beta", "us12-pr-r9", "2026-03-11T09:00:00Z")
            repo.write(
                "src/main_parallel.py",
                "carry_pre_window = base\n"
                "main_human = verify(base + 1)\n"
                "stable_pre_window = base + 2\n",
            )
            repo.commit_all("us12-pr-r9b", "2026-03-12T09:00:00Z")

            repo.write("README.md", "us12 parallel rename docs update\n")
            revision_id_r10 = repo.commit_all("us12-pr-r10", "2026-03-13T09:00:00Z")

            baseline_protocol = self._inline_protocol(repo_branch="main", file_name="src/alpha_legacy.py")
            baseline_protocol["DETAIL"] = [
                {"fileName": "src/alpha_legacy.py", "codeLines": []},
                {"fileName": "src/beta_legacy.py", "codeLines": []},
                {"fileName": "src/main_parallel.py", "codeLines": []},
            ]
            write_revision_protocol(protocol_dir, baseline_protocol, repo_dir, revision_id_r1)

            alpha_human_protocol = self._inline_protocol(repo_branch="feature-alpha", file_name="src/alpha_legacy.py")
            alpha_human_protocol["DETAIL"].append({"fileName": "src/beta_legacy.py", "codeLines": []})
            alpha_human_protocol["DETAIL"].append({"fileName": "src/main_parallel.py", "codeLines": []})
            write_revision_protocol(protocol_dir, alpha_human_protocol, repo_dir, revision_id_r2)

            alpha_rename_protocol = self._inline_protocol(repo_branch="feature-alpha", file_name="src/alpha_final.py")
            alpha_rename_protocol["DETAIL"].append({"fileName": "src/beta_legacy.py", "codeLines": []})
            alpha_rename_protocol["DETAIL"].append({"fileName": "src/main_parallel.py", "codeLines": []})
            write_revision_protocol(protocol_dir, alpha_rename_protocol, repo_dir, revision_id_r3)

            alpha_ai_protocol = self._inline_protocol(repo_branch="feature-alpha", file_name="src/alpha_final.py", full_lines=[3])
            alpha_ai_protocol["DETAIL"].append({"fileName": "src/beta_legacy.py", "codeLines": []})
            alpha_ai_protocol["DETAIL"].append({"fileName": "src/main_parallel.py", "codeLines": []})
            write_revision_protocol(protocol_dir, alpha_ai_protocol, repo_dir, revision_id_r4)

            beta_human_protocol = self._inline_protocol(repo_branch="feature-beta", file_name="src/beta_legacy.py")
            beta_human_protocol["DETAIL"].append({"fileName": "src/alpha_final.py", "codeLines": []})
            beta_human_protocol["DETAIL"].append({"fileName": "src/main_parallel.py", "codeLines": []})
            write_revision_protocol(protocol_dir, beta_human_protocol, repo_dir, revision_id_r5)

            beta_rename_protocol = self._inline_protocol(repo_branch="feature-beta", file_name="src/beta_final.py")
            beta_rename_protocol["DETAIL"].append({"fileName": "src/alpha_final.py", "codeLines": []})
            beta_rename_protocol["DETAIL"].append({"fileName": "src/main_parallel.py", "codeLines": []})
            write_revision_protocol(protocol_dir, beta_rename_protocol, repo_dir, revision_id_r6)

            beta_ai_protocol = self._inline_protocol(repo_branch="feature-beta", file_name="src/beta_final.py", partial_lines={3: 60})
            beta_ai_protocol["DETAIL"].append({"fileName": "src/alpha_final.py", "codeLines": []})
            beta_ai_protocol["DETAIL"].append({"fileName": "src/main_parallel.py", "codeLines": []})
            write_revision_protocol(protocol_dir, beta_ai_protocol, repo_dir, revision_id_r7)

            alpha_merge_protocol = self._inline_protocol(repo_branch="main", file_name="src/alpha_final.py")
            alpha_merge_protocol["DETAIL"] = [
                {"fileName": "src/alpha_final.py", "codeLines": []},
                {"fileName": "src/beta_legacy.py", "codeLines": []},
                {"fileName": "src/main_parallel.py", "codeLines": []},
            ]
            write_revision_protocol(protocol_dir, alpha_merge_protocol, repo_dir, revision_id_r8)

            beta_merge_protocol = self._inline_protocol(repo_branch="main", file_name="src/beta_final.py")
            beta_merge_protocol["DETAIL"] = [
                {"fileName": "src/alpha_final.py", "codeLines": []},
                {"fileName": "src/beta_final.py", "codeLines": []},
                {"fileName": "src/main_parallel.py", "codeLines": []},
            ]
            write_revision_protocol(protocol_dir, beta_merge_protocol, repo_dir, revision_id_r9)

            main_protocol = self._inline_protocol(repo_branch="main", file_name="src/main_parallel.py")
            main_protocol["DETAIL"] = [
                {"fileName": "src/alpha_final.py", "codeLines": []},
                {"fileName": "src/beta_final.py", "codeLines": []},
                {"fileName": "src/main_parallel.py", "codeLines": []},
            ]
            write_revision_protocol(protocol_dir, main_protocol, repo_dir, repo.commit_ids["us12-pr-r9b"])

            result = run_cli(
                repo_dir,
                output_file,
                protocol_dir,
                query,
                extra_args=["--logLevel", "debug"],
            )

            self.assertEqual(
                json.loads(output_file.read_text(encoding="utf-8")),
                {
                    "protocolName": "generatedTextDesc",
                    "protocolVersion": "26.03",
                    "SUMMARY": {
                        "totalCodeLines": 5,
                        "fullGeneratedCodeLines": 1,
                        "partialGeneratedCodeLines": 1,
                    },
                    "REPOSITORY": {
                        "vcsType": "git",
                        "repoURL": str(repo_dir),
                        "repoBranch": "main",
                        "revisionId": revision_id_r10,
                    },
                },
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/alpha_final.py",
                final_line=2,
                origin_file="src/alpha_legacy.py",
                origin_line=2,
                revision_id=revision_id_r2,
                classification="human/unattributed",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/alpha_final.py",
                final_line=3,
                origin_file="src/alpha_final.py",
                origin_line=3,
                revision_id=revision_id_r4,
                classification="100%-ai",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/beta_final.py",
                final_line=2,
                origin_file="src/beta_legacy.py",
                origin_line=2,
                revision_id=revision_id_r5,
                classification="human/unattributed",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/beta_final.py",
                final_line=3,
                origin_file="src/beta_final.py",
                origin_line=3,
                revision_id=revision_id_r7,
                classification="60%-ai",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/main_parallel.py",
                final_line=2,
                origin_file="src/main_parallel.py",
                origin_line=2,
                revision_id=repo.commit_ids["us12-pr-r9b"],
                classification="human/unattributed",
            )


if __name__ == "__main__":
    unittest.main()