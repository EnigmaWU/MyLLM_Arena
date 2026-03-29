import tempfile
import unittest
from pathlib import Path

from tests.cli_test_support import GitRepoHarness, run_cli
from tests.log_assertions import assert_live_line_log, assert_log_contains_all, assert_log_contains_none


class TestStressMixedHistoryTenPlusCommits(unittest.TestCase):
    maxDiff = None

    def _query(self) -> dict:
        return {
            "vcsType": "git",
            "repoURL": "https://example.local/repo/stress",
            "repoBranch": "main",
            "metric": "live_changed_source_ratio",
            "model": "A",
            "scope": "A",
            "startTime": "2026-03-01",
            "endTime": "2026-03-31",
            "endRevisionId": "stress-r11",
        }

    def _protocol(self, *, repo_branch: str, full_lines: list[int] | None = None, partial_lines: dict[int, int] | None = None, file_name: str) -> dict:
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
            "codeAgent": "StressScenarioAgent",
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
                "repoURL": "https://example.local/repo/stress",
                "repoBranch": repo_branch,
                "revisionId": "placeholder",
            },
        }

    def _write_protocol(self, protocol_dir: Path, protocol: dict, repo_dir: Path, revision_id: str) -> None:
        protocol = {
            **protocol,
            "REPOSITORY": {
                **protocol["REPOSITORY"],
                "repoURL": str(repo_dir),
                "revisionId": revision_id,
            },
        }
        (protocol_dir / f"{revision_id}_genCodeDesc.json").write_text(__import__("json").dumps(protocol, indent=2), encoding="utf-8")

    def _build_stress_history(self, root_dir: Path) -> tuple[Path, Path, Path, dict[str, str]]:
        repo_dir = root_dir / "repo"
        protocol_dir = root_dir / "protocols"
        output_file = root_dir / "out.json"
        repo_dir.mkdir()
        protocol_dir.mkdir()

        repo = GitRepoHarness(repo_dir)

        # WHY: this scenario intentionally mixes the already-proven behaviors
        # into one longer history so the current blame-based implementation is
        # exercised under realistic churn rather than only isolated stories.
        repo.write(
            "src/legacy_mix.py",
            "carry_pre_window = seed\n"
            "human_window = seed + 1\n"
            "rename_ai = seed + 2\n"
            "ai_then_human = seed + 3\n"
            "human_then_ai = seed + 4\n"
            "deleted_ai = seed + 5\n"
            "partial_future = seed + 6\n"
            "stable_tail = seed + 7\n",
        )
        revision_id_r0 = repo.commit_all("stress-r0", "2026-02-20T09:00:00Z")

        repo.write(
            "src/legacy_mix.py",
            "carry_pre_window = seed\n"
            "human_window = seed + 10\n"
            "rename_ai = seed + 2\n"
            "ai_then_human = seed + 3\n"
            "human_then_ai = seed + 4\n"
            "deleted_ai = seed + 5\n"
            "partial_future = seed + 6\n"
            "stable_tail = seed + 7\n",
        )
        revision_id_r1 = repo.commit_all("stress-r1", "2026-03-02T09:00:00Z")

        repo.write(
            "src/legacy_mix.py",
            "carry_pre_window = seed\n"
            "human_window = seed + 10\n"
            "rename_ai = helper(seed)\n"
            "ai_then_human = helper(seed + 1)\n"
            "human_then_ai = seed + 4\n"
            "deleted_ai = helper(seed + 2)\n"
            "partial_future = seed + 6\n"
            "stable_tail = seed + 7\n",
        )
        revision_id_r2 = repo.commit_all("stress-r2", "2026-03-05T09:00:00Z")

        repo.rename("src/legacy_mix.py", "src/current_mix.py")
        revision_id_r3 = repo.commit_all("stress-r3", "2026-03-07T09:00:00Z")

        repo.write(
            "src/current_mix.py",
            "carry_pre_window = seed\n"
            "human_window = seed + 10\n"
            "rename_ai = helper(seed)\n"
            "ai_then_human = sanitize(seed)\n"
            "human_then_ai = seed + 4\n"
            "deleted_ai = helper(seed + 2)\n"
            "partial_future = seed + 6\n"
            "stable_tail = seed + 7\n",
        )
        revision_id_r4 = repo.commit_all("stress-r4", "2026-03-10T09:00:00Z")

        repo.write(
            "src/current_mix.py",
            "carry_pre_window = seed\n"
            "human_window = seed + 10\n"
            "rename_ai = helper(seed)\n"
            "ai_then_human = sanitize(seed)\n"
            "human_then_ai = seed + 4\n"
            "deleted_ai = helper(seed + 2)\n"
            "partial_future = seed + suggest(seed)\n"
            "stable_tail = seed + 7\n",
        )
        revision_id_r5 = repo.commit_all("stress-r5", "2026-03-12T09:00:00Z")

        repo.write(
            "src/current_mix.py",
            "carry_pre_window = seed\n"
            "human_window = seed + 10\n"
            "rename_ai = helper(seed)\n"
            "ai_then_human = sanitize(seed)\n"
            "human_then_ai = seed + 4\n"
            "partial_future = seed + suggest(seed)\n"
            "stable_tail = seed + 7\n",
        )
        revision_id_r6 = repo.commit_all("stress-r6", "2026-03-14T09:00:00Z")

        repo.checkout_new_branch("feature-ai")
        repo.write(
            "src/current_mix.py",
            "carry_pre_window = seed\n"
            "human_window = seed + 10\n"
            "rename_ai = helper(seed)\n"
            "ai_then_human = sanitize(seed)\n"
            "human_then_ai = helper(seed * 2)\n"
            "partial_future = seed + suggest(seed)\n"
            "stable_tail = seed + 7\n",
        )
        revision_id_r7 = repo.commit_all("stress-r7", "2026-03-16T09:00:00Z")

        repo.checkout("main")
        repo.write(
            "src/current_mix.py",
            "carry_pre_window = seed\n"
            "human_window = max(seed, 0) + 10\n"
            "rename_ai = helper(seed)\n"
            "ai_then_human = sanitize(seed)\n"
            "human_then_ai = seed + 4\n"
            "partial_future = seed + suggest(seed)\n"
            "stable_tail = seed + 7\n",
        )
        revision_id_r8 = repo.commit_all("stress-r8", "2026-03-18T09:00:00Z")

        revision_id_r9 = repo.merge_no_ff("feature-ai", "stress-r9", "2026-03-20T09:00:00Z")

        repo.write("README.md", "stress docs update\n")
        revision_id_r10 = repo.commit_all("stress-r10", "2026-03-24T09:00:00Z")

        protocols = {
            revision_id_r0: self._protocol(repo_branch="main", file_name="src/legacy_mix.py"),
            revision_id_r1: self._protocol(repo_branch="main", file_name="src/legacy_mix.py"),
            revision_id_r2: self._protocol(repo_branch="main", full_lines=[3, 4, 6], file_name="src/legacy_mix.py"),
            revision_id_r3: self._protocol(repo_branch="main", file_name="src/current_mix.py"),
            revision_id_r4: self._protocol(repo_branch="main", file_name="src/current_mix.py"),
            revision_id_r5: self._protocol(repo_branch="main", partial_lines={7: 60}, file_name="src/current_mix.py"),
            revision_id_r6: self._protocol(repo_branch="main", file_name="src/current_mix.py"),
            revision_id_r7: self._protocol(repo_branch="feature-ai", full_lines=[5], file_name="src/current_mix.py"),
            revision_id_r8: self._protocol(repo_branch="main", file_name="src/current_mix.py"),
            revision_id_r9: self._protocol(repo_branch="main", file_name="src/current_mix.py"),
        }
        for revision_id, protocol in protocols.items():
            self._write_protocol(protocol_dir, protocol, repo_dir, revision_id)

        return repo_dir, protocol_dir, output_file, {
            "r0": revision_id_r0,
            "r2": revision_id_r2,
            "r4": revision_id_r4,
            "r5": revision_id_r5,
            "r7": revision_id_r7,
            "r8": revision_id_r8,
            "r10": revision_id_r10,
        }

    def test_cli_handles_realistic_mixed_history_with_eleven_commits(self) -> None:
        query = self._query()

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_dir, protocol_dir, output_file, revision_ids = self._build_stress_history(Path(temp_dir))

            run_cli(repo_dir, output_file, protocol_dir, query)

            self.assertEqual(
                __import__("json").loads(output_file.read_text(encoding="utf-8")),
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
                        "revisionId": revision_ids["r10"],
                    },
                },
            )

    def test_cli_debug_logs_show_mixed_realistic_origins(self) -> None:
        query = self._query()

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_dir, protocol_dir, output_file, revision_ids = self._build_stress_history(Path(temp_dir))

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
                    "Finished analysis with totalCodeLines=5 fullGeneratedCodeLines=2 partialGeneratedCodeLines=1",
                    "Metadata repoBranch differs",
                    "Skip out-of-window line src/current_mix.py:1",
                    "Skip out-of-window line src/current_mix.py:7",
                ],
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/current_mix.py",
                final_line=2,
                origin_file="src/current_mix.py",
                origin_line=2,
                revision_id=revision_ids["r8"],
                classification="human/unattributed",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/current_mix.py",
                final_line=3,
                origin_file="src/legacy_mix.py",
                origin_line=3,
                revision_id=revision_ids["r2"],
                classification="100%-ai",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/current_mix.py",
                final_line=4,
                origin_file="src/current_mix.py",
                origin_line=4,
                revision_id=revision_ids["r4"],
                classification="human/unattributed",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/current_mix.py",
                final_line=5,
                origin_file="src/current_mix.py",
                origin_line=5,
                revision_id=revision_ids["r7"],
                classification="100%-ai",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/current_mix.py",
                final_line=6,
                origin_file="src/current_mix.py",
                origin_line=7,
                revision_id=revision_ids["r5"],
                classification="60%-ai",
            )
            assert_log_contains_none(
                self,
                result.stderr,
                [
                    "LiveLine src/current_mix.py:1 aggregate",
                    "LiveLine src/current_mix.py:7 aggregate",
                ],
            )


if __name__ == "__main__":
    unittest.main()