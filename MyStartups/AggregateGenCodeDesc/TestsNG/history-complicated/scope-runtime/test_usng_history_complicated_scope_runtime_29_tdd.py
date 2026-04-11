import re
import subprocess
import tempfile
import unittest
from pathlib import Path

from tests.cli_test_support import GitRepoHarness, PROJECT_ROOT, UTILITY_PATH, load_json, write_revision_protocol
from tests.log_assertions import assert_log_contains_all, assert_log_contains_none, assert_transition_hint


SCENARIO_DIR = PROJECT_ROOT / "OperatorScenarioNG" / "history-complicated" / "scope-runtime" / "29"
AI_TO_HUMAN_DIR = SCENARIO_DIR / "ai-to-human"
HUMAN_TO_AI_DIR = SCENARIO_DIR / "human-to-ai"

MAX_COST_SECONDS = 30.0


def _run_alg_a(repo_dir: Path, protocol_dir: Path, output_file: Path, log_level: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "python3", str(UTILITY_PATH),
            "--vcsType", "git",
            "--repoURL", str(repo_dir),
            "--repoBranch", "main",
            "--startTime", "2026-03-01",
            "--endTime", "2026-03-31",
            "--algorithm", "A",
            "--scope", "A",
            "--logLevel", log_level,
            "--outputFile", str(output_file),
            "--genCodeDescSetDir", str(protocol_dir),
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
    )


def _build_ai_to_human_repo(root: Path) -> tuple[Path, Path]:
    """r1: all-AI 3-line src/app.py.  r2: human rewrites line 2.  Returns (repo_dir, protocol_dir)."""
    repo_dir = root / "repo"
    protocol_dir = root / "protocols"
    repo_dir.mkdir()
    protocol_dir.mkdir()

    proto_r1 = load_json(AI_TO_HUMAN_DIR / "r1_genCodeDesc.json")
    proto_r2 = load_json(AI_TO_HUMAN_DIR / "r2_genCodeDesc.json")

    repo = GitRepoHarness(repo_dir)
    repo.write("src/app.py", "x = 1\ny = 2\nz = 3\n")
    r1 = repo.commit_all("r1", "2026-03-10T09:00:00Z")

    repo.write("src/app.py", "x = 1\ny = 999\nz = 3\n")
    r2 = repo.commit_all("r2", "2026-03-20T09:00:00Z")

    write_revision_protocol(protocol_dir, proto_r1, repo_dir, r1)
    write_revision_protocol(protocol_dir, proto_r2, repo_dir, r2)
    return repo_dir, protocol_dir


def _build_human_to_ai_repo(root: Path) -> tuple[Path, Path]:
    """r1: all-human 3-line src/score.py.  r2: AI rewrites lines 2 and 3.  Returns (repo_dir, protocol_dir)."""
    repo_dir = root / "repo"
    protocol_dir = root / "protocols"
    repo_dir.mkdir()
    protocol_dir.mkdir()

    proto_r1 = load_json(HUMAN_TO_AI_DIR / "r1_genCodeDesc.json")
    proto_r2 = load_json(HUMAN_TO_AI_DIR / "r2_genCodeDesc.json")

    repo = GitRepoHarness(repo_dir)
    repo.write("src/score.py", "a = 1\nb = 2\nc = 3\n")
    r1 = repo.commit_all("r1", "2026-03-10T09:00:00Z")

    repo.write("src/score.py", "a = 1\nb = 200\nc = 300\n")
    r2 = repo.commit_all("r2", "2026-03-20T09:00:00Z")

    write_revision_protocol(protocol_dir, proto_r1, repo_dir, r1)
    write_revision_protocol(protocol_dir, proto_r2, repo_dir, r2)
    return repo_dir, protocol_dir


class TestUsngHistoryComplicatedScopeRuntime29Tdd(unittest.TestCase):
    """USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-RUNTIME-29:
    Info-Level Log Must Show Initial Load, Per-Line State Transition, And Final Summary"""

    maxDiff = None

    # -----------------------------------------------------------------------
    # AC-OPS-01: start-state header contains repo=, branch=, window=, endRevision=
    # -----------------------------------------------------------------------

    def test_info_log_emits_start_state_header_with_required_fields(self) -> None:
        """AC-OPS-01: --logLevel info must emit Starting analysis with repo=, branch=, window=, endRevision= fields."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo_dir, protocol_dir = _build_ai_to_human_repo(root)
            result = _run_alg_a(repo_dir, protocol_dir, root / "out.json", "info")

            self.assertEqual(result.returncode, 0, f"CLI failed:\n{result.stderr}")
            assert_log_contains_all(self, result.stderr, [
                "Starting analysis",
                "repo=",
                "branch=",
                "window=",
                "endRevision=",
            ])

    # -----------------------------------------------------------------------
    # AC-OPS-02: per-line TransitionHint on ownership change
    # -----------------------------------------------------------------------

    def test_info_log_emits_transition_hint_on_ownership_change(self) -> None:
        """AC-OPS-02: --logLevel info must emit a TransitionHint line when line ownership changes."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo_dir, protocol_dir = _build_ai_to_human_repo(root)
            result = _run_alg_a(repo_dir, protocol_dir, root / "out.json", "info")

            self.assertEqual(result.returncode, 0, f"CLI failed:\n{result.stderr}")
            self.assertIn("TransitionHint", result.stderr, "Expected TransitionHint in info-level stderr")
            self.assertIn("best_effort_transition=", result.stderr, "Expected best_effort_transition= in TransitionHint")

    # -----------------------------------------------------------------------
    # AC-OPS-03: final summary contains required totals and timing fields
    # -----------------------------------------------------------------------

    def test_info_log_emits_final_summary_with_required_fields(self) -> None:
        """AC-OPS-03: --logLevel info must emit Finished analysis with totals and elapsed/costSeconds."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo_dir, protocol_dir = _build_ai_to_human_repo(root)
            result = _run_alg_a(repo_dir, protocol_dir, root / "out.json", "info")

            self.assertEqual(result.returncode, 0, f"CLI failed:\n{result.stderr}")
            assert_log_contains_all(self, result.stderr, [
                "Finished analysis",
                "totalCodeLines=",
                "fullGeneratedCodeLines=",
                "partialGeneratedCodeLines=",
                "elapsed=",
                "costSeconds=",
            ])

    def test_info_log_cost_seconds_within_budget(self) -> None:
        """AC-OPS-03 (timing gate): costSeconds must be below MAX_COST_SECONDS."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo_dir, protocol_dir = _build_ai_to_human_repo(root)
            result = _run_alg_a(repo_dir, protocol_dir, root / "out.json", "info")

            self.assertEqual(result.returncode, 0, f"CLI failed:\n{result.stderr}")
            match = re.search(r"costSeconds=([\d.]+)", result.stderr)
            self.assertIsNotNone(match, "costSeconds value not found in stderr")
            cost = float(match.group(1))  # type: ignore[union-attr]
            self.assertLess(cost, MAX_COST_SECONDS, f"costSeconds={cost} exceeds budget {MAX_COST_SECONDS}")

    # -----------------------------------------------------------------------
    # AC-OPS-04: quiet mode suppresses TransitionHint and LiveLine lines
    # -----------------------------------------------------------------------

    def test_quiet_mode_suppresses_transition_hint_and_live_line(self) -> None:
        """AC-OPS-04: --logLevel quiet must not emit TransitionHint or LiveLine lines."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo_dir, protocol_dir = _build_ai_to_human_repo(root)
            result = _run_alg_a(repo_dir, protocol_dir, root / "out.json", "quiet")

            self.assertEqual(result.returncode, 0, f"CLI failed:\n{result.stderr}")
            assert_log_contains_none(self, result.stderr, ["TransitionHint", "LiveLine"])

    # -----------------------------------------------------------------------
    # AC-OPS-05: debug mode shows all diagnostic tiers beyond info
    # -----------------------------------------------------------------------

    def test_debug_mode_includes_all_info_lines_plus_debug_diagnostics(self) -> None:
        """AC-OPS-05: --logLevel debug must emit all info-level lines plus [DEBUG] diagnostic lines."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo_dir, protocol_dir = _build_ai_to_human_repo(root)
            result_info = _run_alg_a(repo_dir, protocol_dir, root / "out_info.json", "info")
            result_debug = _run_alg_a(repo_dir, protocol_dir, root / "out_debug.json", "debug")

            self.assertEqual(result_info.returncode, 0)
            self.assertEqual(result_debug.returncode, 0)

            info_count = sum(1 for line in result_info.stderr.splitlines() if "[INFO]" in line)
            debug_info_count = sum(1 for line in result_debug.stderr.splitlines() if "[INFO]" in line)
            self.assertGreaterEqual(debug_info_count, info_count,
                                    "debug mode must include at least as many [INFO] lines as info mode")

            assert_log_contains_all(self, result_debug.stderr, [
                "Loaded genCodeDesc for revision",
                "Scanning file",
            ])

    # -----------------------------------------------------------------------
    # AC-OPS-06: AI-to-human golden narrative
    # -----------------------------------------------------------------------

    def test_ai_to_human_transition_golden_narrative(self) -> None:
        """AC-OPS-06: AI-to-human scenario must emit best_effort_transition=100%-ai->human/unattributed."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo_dir, protocol_dir = _build_ai_to_human_repo(root)
            result = _run_alg_a(repo_dir, protocol_dir, root / "out.json", "info")

            self.assertEqual(result.returncode, 0, f"CLI failed:\n{result.stderr}")
            assert_transition_hint(self, result.stderr, "100%-ai", "human/unattributed")

    # -----------------------------------------------------------------------
    # AC-OPS-07: human-to-AI golden narrative
    # -----------------------------------------------------------------------

    def test_human_to_ai_transition_golden_narrative(self) -> None:
        """AC-OPS-07: Human-to-AI scenario must emit best_effort_transition=human/unattributed->100%-ai."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo_dir, protocol_dir = _build_human_to_ai_repo(root)
            result = _run_alg_a(repo_dir, protocol_dir, root / "out.json", "info")

            self.assertEqual(result.returncode, 0, f"CLI failed:\n{result.stderr}")
            assert_transition_hint(self, result.stderr, "human/unattributed", "100%-ai")


if __name__ == "__main__":
    unittest.main()
