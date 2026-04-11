import subprocess
import tempfile
import unittest
from pathlib import Path

from tests.cli_test_support import GitRepoHarness, PROJECT_ROOT, UTILITY_PATH


MAX_COST_SECONDS = 30.0


class TestUsngAlgbHistoryComplicatedScopeRuntime29Tdd(unittest.TestCase):
    """USNG-ALGB-HISTORY-COMPLICATED-SCOPE-RUNTIME-29: Info-Level Log Must Show Replay Progress And Final Summary"""

    maxDiff = None

    def _run_cli_with_logging(self, repo_dir: Path, protocol_dir: Path, output_file: Path, log_level: str) -> tuple[int, str]:
        result = subprocess.run(
            [
                "python3",
                str(UTILITY_PATH),
                "--vcsType", "git",
                "--repoURL", str(repo_dir),
                "--repoBranch", "main",
                "--startTime", "2026-03-01",
                "--endTime", "2026-03-31",
                "--algorithm", "B",
                "--scope", "A",
                "--logLevel", log_level,
                "--outputFile", str(output_file),
                "--genCodeDescSetDir", str(protocol_dir),
            ],
            cwd=PROJECT_ROOT,
            text=True,
            capture_output=True,
        )
        return result.returncode, result.stderr

    def _build_repo(self, root: Path) -> tuple[Path, Path]:
        """Build a complicated-history repo: r1 adds file; r2 rewrites one AI line with human code."""
        repo_dir = root / "repo"
        protocol_dir = root / "protocols"
        repo_dir.mkdir()
        protocol_dir.mkdir()

        repo = GitRepoHarness(repo_dir)

        # r1: add src/app.py with 3 lines
        repo.write("src/app.py", "x = 1\ny = 2\nz = 3\n")
        r1 = repo.commit_all("r1", "2026-03-10T09:00:00Z")

        # r2: rewrite line 2 (complicated attribution: new content replaces r1 line)
        repo.write("src/app.py", "x = 1\ny = 999\nz = 3\n")
        _r2 = repo.commit_all("r2", "2026-03-15T09:00:00Z")

        return repo_dir, protocol_dir

    def test_info_log_emits_final_summary_with_algorithm_b_label(self) -> None:
        """AC-OPS-03 partial: Stderr must emit a Finished Algorithm B summary line at info level."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            output_file = root / "out.json"
            repo_dir, protocol_dir = self._build_repo(root)

            returncode, stderr = self._run_cli_with_logging(repo_dir, protocol_dir, output_file, "info")

            self.assertEqual(returncode, 0, f"Expected exit 0; stderr:\n{stderr}")
            self.assertIn("[INFO]", stderr, "Expected [INFO] lines in stderr with --logLevel info")
            self.assertIn("Finished Algorithm B", stderr, "Expected summary header 'Finished Algorithm B' in stderr")
            self.assertIn("totalCodeLines=", stderr, "Expected totalCodeLines in final summary")
            self.assertIn("fullGeneratedCodeLines=", stderr, "Expected fullGeneratedCodeLines in final summary")
            self.assertIn("partialGeneratedCodeLines=", stderr, "Expected partialGeneratedCodeLines in final summary")

    def test_info_log_emits_live_line_per_line_states(self) -> None:
        """AC-OPS-02 per-line: Info log must emit LiveLine entries for each in-scope line with classification."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            output_file = root / "out.json"
            repo_dir, protocol_dir = self._build_repo(root)

            returncode, stderr = self._run_cli_with_logging(repo_dir, protocol_dir, output_file, "info")

            self.assertEqual(returncode, 0, f"Expected exit 0; stderr:\n{stderr}")
            live_lines = [line for line in stderr.splitlines() if "LiveLine" in line]
            self.assertGreater(len(live_lines), 0, f"Expected at least one LiveLine entry in stderr; got:\n{stderr}")
            self.assertTrue(
                all("classification=" in line for line in live_lines),
                f"All LiveLine entries must contain classification=; got:\n{chr(10).join(live_lines)}",
            )

    def test_info_log_emits_start_state_header(self) -> None:
        """AC-OPS-01: Stderr must contain a start-state header with repo=, branch=, window=, patchCount= at info level."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            output_file = root / "out.json"
            repo_dir, protocol_dir = self._build_repo(root)

            returncode, stderr = self._run_cli_with_logging(repo_dir, protocol_dir, output_file, "info")

            self.assertEqual(returncode, 0, f"Expected exit 0; stderr:\n{stderr}")
            self.assertIn("branch=", stderr, "Expected branch= in start-state header")
            self.assertIn("window=", stderr, "Expected window= in start-state header")
            self.assertIn("patchCount=", stderr, "Expected patchCount= in start-state header")

    def test_info_log_emits_cost_seconds_within_budget(self) -> None:
        """AC-OPS-03: The final summary line must include elapsed= and costSeconds= fields."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            output_file = root / "out.json"
            repo_dir, protocol_dir = self._build_repo(root)

            returncode, stderr = self._run_cli_with_logging(repo_dir, protocol_dir, output_file, "info")

            self.assertEqual(returncode, 0, f"Expected exit 0; stderr:\n{stderr}")
            self.assertIn("elapsed=", stderr, "Expected elapsed= in final summary line")
            self.assertIn("costSeconds=", stderr, "Expected costSeconds= in final summary line")

            # Extract the costSeconds value and verify it is within the budget
            import re
            match = re.search(r"costSeconds=([\d.]+)", stderr)
            self.assertIsNotNone(match, "costSeconds value not found in stderr")
            cost = float(match.group(1))  # type: ignore[union-attr]
            self.assertLess(cost, MAX_COST_SECONDS, f"costSeconds={cost} exceeds budget {MAX_COST_SECONDS}")

    def test_quiet_mode_suppresses_all_info_lines(self) -> None:
        """AC-OPS-04: quiet mode must produce no [INFO] lines on stderr."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            output_file = root / "out.json"
            repo_dir, protocol_dir = self._build_repo(root)

            returncode, stderr = self._run_cli_with_logging(repo_dir, protocol_dir, output_file, "quiet")

            self.assertEqual(returncode, 0, f"Expected exit 0; stderr:\n{stderr}")
            info_lines = [line for line in stderr.splitlines() if "[INFO]" in line]
            self.assertEqual(info_lines, [], f"Expected no [INFO] lines in quiet mode; got:\n{chr(10).join(info_lines)}")

    def test_debug_mode_includes_all_info_lines(self) -> None:
        """AC-OPS-05: debug mode must include all info-level lines plus additional debug diagnostics."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            output_file = root / "out.json"
            repo_dir, protocol_dir = self._build_repo(root)

            returncode_info, stderr_info = self._run_cli_with_logging(repo_dir, protocol_dir, output_file, "info")
            returncode_debug, stderr_debug = self._run_cli_with_logging(repo_dir, protocol_dir, output_file, "debug")

            self.assertEqual(returncode_info, 0)
            self.assertEqual(returncode_debug, 0)

            info_lines_count = sum(1 for line in stderr_info.splitlines() if "[INFO]" in line)
            debug_info_lines_count = sum(1 for line in stderr_debug.splitlines() if "[INFO]" in line)
            total_debug_lines = len([line for line in stderr_debug.splitlines() if "[INFO]" in line or "[DEBUG]" in line])

            # debug mode must include at least as many [INFO] lines as info mode
            self.assertGreaterEqual(debug_info_lines_count, info_lines_count,
                                    "debug mode must include all info-level log lines")

            # debug mode must have additional [DEBUG] lines
            self.assertGreater(total_debug_lines, info_lines_count,
                               "debug mode must emit [DEBUG] lines in addition to [INFO] lines")


if __name__ == "__main__":
    unittest.main()
