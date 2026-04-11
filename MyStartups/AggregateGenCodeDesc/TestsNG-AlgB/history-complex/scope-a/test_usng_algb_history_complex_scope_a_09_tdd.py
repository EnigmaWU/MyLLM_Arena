import subprocess
import tempfile
import unittest
from pathlib import Path

from tests.cli_test_support import GitRepoHarness, PROJECT_ROOT, UTILITY_PATH, write_revision_protocol, load_json


NUM_FILES = 10
LINES_PER_FILE = 5
GEN_RATIOS_PER_FILE = [100, 0, 50, 0, 0]  # line1=full, line3=partial, others=human


def _build_file_content(file_index: int) -> str:
    return "\n".join(f"line{line_no}_{file_index:02d} = {line_no}" for line_no in range(1, LINES_PER_FILE + 1)) + "\n"


def _build_file_protocol_detail(file_path: str) -> dict:
    return {
        "fileName": file_path,
        "codeLines": [
            {"lineLocation": line_no, "genRatio": GEN_RATIOS_PER_FILE[line_no - 1], "genMethod": "Manual" if GEN_RATIOS_PER_FILE[line_no - 1] == 0 else "codeCompletion"}
            for line_no in range(1, LINES_PER_FILE + 1)
        ],
    }


class TestUsngAlgbHistoryComplexScopeA09Tdd(unittest.TestCase):
    """USNG-ALGB-HISTORY-COMPLEX-SCOPE-A-09: Large File Set Must Preserve Result Semantics Via Replay"""

    maxDiff = None

    def test_large_file_set_produces_correct_live_snapshot_result(self) -> None:
        """AC-01 / AC-GIT-01: Large file set (10 files × 5 lines) preserves correct SUMMARY via Algorithm B live replay."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo_dir = root / "repo"
            protocol_dir = root / "protocols"
            output_file = root / "out.json"
            repo_dir.mkdir()
            protocol_dir.mkdir()

            repo = GitRepoHarness(repo_dir)

            # r1 (in-window): add NUM_FILES source files, each with LINES_PER_FILE code lines
            file_paths = [f"src/module{i:02d}.py" for i in range(1, NUM_FILES + 1)]
            for i, file_path in enumerate(file_paths, start=1):
                repo.write(file_path, _build_file_content(i))
            r1 = repo.commit_all("r1", "2026-03-10T09:00:00Z")

            # Write genCodeDesc for r1 including all NUM_FILES files
            protocol_r1 = {
                "protocolName": "generatedTextDesc",
                "protocolVersion": "26.03",
                "codeAgent": "LargeFileSetAgent",
                "SUMMARY": {
                    "totalCodeLines": NUM_FILES * LINES_PER_FILE,
                    "fullGeneratedCodeLines": NUM_FILES,
                    "partialGeneratedCodeLines": NUM_FILES,
                },
                "REPOSITORY": {"repoURL": str(repo_dir), "repoBranch": "main", "revisionId": r1},
                "DETAIL": [_build_file_protocol_detail(f"src/module{i:02d}.py") for i in range(1, NUM_FILES + 1)],
            }
            write_revision_protocol(protocol_dir, protocol_r1, repo_dir, r1)

            result = subprocess.run(
                [
                    "python3", str(UTILITY_PATH),
                    "--vcsType", "git",
                    "--repoURL", str(repo_dir),
                    "--repoBranch", "main",
                    "--startTime", "2026-03-01",
                    "--endTime", "2026-03-31",
                    "--algorithm", "B",
                    "--scope", "A",
                    "--outputFile", str(output_file),
                    "--genCodeDescSetDir", str(protocol_dir),
                ],
                cwd=PROJECT_ROOT,
                text=True,
                capture_output=True,
                check=True,
            )

            actual = load_json(output_file)
            summary = actual.get("SUMMARY", {})

            # All NUM_FILES files × LINES_PER_FILE lines are in-window (r1 is in-window)
            # genRatio per file: [100, 0, 50, 0, 0] → full=1, partial=1, human=3 per file
            expected_total = NUM_FILES * LINES_PER_FILE
            expected_full = NUM_FILES * GEN_RATIOS_PER_FILE.count(100)
            expected_partial = NUM_FILES * sum(1 for r in GEN_RATIOS_PER_FILE if 0 < r < 100)
            self.assertEqual(summary.get("totalCodeLines"), expected_total,
                             f"Expected totalCodeLines={expected_total}")
            self.assertEqual(summary.get("fullGeneratedCodeLines"), expected_full,
                             f"Expected fullGeneratedCodeLines={expected_full}")
            self.assertEqual(summary.get("partialGeneratedCodeLines"), expected_partial,
                             f"Expected partialGeneratedCodeLines={expected_partial}")


if __name__ == "__main__":
    unittest.main()
