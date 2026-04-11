import subprocess
import tempfile
import unittest
from pathlib import Path

from tests.cli_test_support import GitRepoHarness, PROJECT_ROOT, UTILITY_PATH, write_revision_protocol, load_json


# Scenario: 3 feature branches, each adds a distinct file into main via no-ff merge.
# main r1 (in-window, 2026-03-01): adds src/app.py with 2 human lines (genRatio=0)
# feature-a: adds src/feat_a.py with 2 full-AI lines (genRatio=100), merged to main
# feature-b: adds src/feat_b.py with 2 partial-AI lines (genRatio=50), merged to main
# feature-c: adds src/feat_c.py with 2 human lines (genRatio=0), merged to main
#
# All commits in window 2026-03-01..2026-03-31.
# Expected live-snapshot SUMMARY:
#   totalCodeLines = 2 (app.py) + 2 (feat_a) + 2 (feat_b) + 2 (feat_c) = 8
#   fullGeneratedCodeLines = 2 (feat_a)
#   partialGeneratedCodeLines = 2 (feat_b)

EXPECTED_TOTAL = 8
EXPECTED_FULL = 2
EXPECTED_PARTIAL = 2


class TestUsngAlgbHistoryComplexScopeA11Tdd(unittest.TestCase):
    """USNG-ALGB-HISTORY-COMPLEX-SCOPE-A-11: Many Merged Branches Must Preserve Per-Line Attribution Via Replay"""

    maxDiff = None

    def test_many_merged_branches_preserve_per_line_attribution(self) -> None:
        """AC-01 / AC-GIT-01: Lines from 3 merged feature branches are attributed independently."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo_dir = root / "repo"
            protocol_dir = root / "protocols"
            output_file = root / "out.json"
            repo_dir.mkdir()
            protocol_dir.mkdir()

            repo = GitRepoHarness(repo_dir)

            # main r1 (in-window): add src/app.py — 2 human lines
            repo.write("src/app.py", "def main():\n    return 0\n")
            r1 = repo.commit_all("r1", "2026-03-01T09:00:00Z")

            # feature-a: adds src/feat_a.py — 2 full-AI lines
            repo.checkout_new_branch("feature-a")
            repo.write("src/feat_a.py", "def feat_a():\n    return ai_a()\n")
            fa = repo.commit_all("fa", "2026-03-05T09:00:00Z")

            # Merge feature-a into main
            repo.checkout("main")
            repo.merge_no_ff("feature-a", "merge-a", "2026-03-07T09:00:00Z")

            # feature-b: adds src/feat_b.py — 2 partial-AI lines
            repo.checkout_new_branch("feature-b")
            repo.write("src/feat_b.py", "def feat_b():\n    return partial_b()\n")
            fb = repo.commit_all("fb", "2026-03-10T09:00:00Z")

            # Merge feature-b into main
            repo.checkout("main")
            repo.merge_no_ff("feature-b", "merge-b", "2026-03-12T09:00:00Z")

            # feature-c: adds src/feat_c.py — 2 human lines
            repo.checkout_new_branch("feature-c")
            repo.write("src/feat_c.py", "def feat_c():\n    return human_c()\n")
            fc = repo.commit_all("fc", "2026-03-15T09:00:00Z")

            # Merge feature-c into main
            repo.checkout("main")
            repo.merge_no_ff("feature-c", "merge-c", "2026-03-17T09:00:00Z")

            # genCodeDesc for r1: src/app.py — 2 human lines
            write_revision_protocol(protocol_dir, {
                "protocolName": "generatedTextDesc", "protocolVersion": "26.03", "codeAgent": "MergeAgent",
                "SUMMARY": {"totalCodeLines": 2, "fullGeneratedCodeLines": 0, "partialGeneratedCodeLines": 0},
                "REPOSITORY": {"repoURL": str(repo_dir), "repoBranch": "main", "revisionId": r1},
                "DETAIL": [{"fileName": "src/app.py", "codeLines": [
                    {"lineLocation": 1, "genRatio": 0, "genMethod": "Manual"},
                    {"lineLocation": 2, "genRatio": 0, "genMethod": "Manual"},
                ]}],
            }, repo_dir, r1)

            # genCodeDesc for fa: src/feat_a.py — 2 full-AI lines
            write_revision_protocol(protocol_dir, {
                "protocolName": "generatedTextDesc", "protocolVersion": "26.03", "codeAgent": "MergeAgent",
                "SUMMARY": {"totalCodeLines": 2, "fullGeneratedCodeLines": 2, "partialGeneratedCodeLines": 0},
                "REPOSITORY": {"repoURL": str(repo_dir), "repoBranch": "feature-a", "revisionId": fa},
                "DETAIL": [{"fileName": "src/feat_a.py", "codeLines": [
                    {"lineLocation": 1, "genRatio": 100, "genMethod": "codeCompletion"},
                    {"lineLocation": 2, "genRatio": 100, "genMethod": "codeCompletion"},
                ]}],
            }, repo_dir, fa)

            # genCodeDesc for fb: src/feat_b.py — 2 partial-AI lines
            write_revision_protocol(protocol_dir, {
                "protocolName": "generatedTextDesc", "protocolVersion": "26.03", "codeAgent": "MergeAgent",
                "SUMMARY": {"totalCodeLines": 2, "fullGeneratedCodeLines": 0, "partialGeneratedCodeLines": 2},
                "REPOSITORY": {"repoURL": str(repo_dir), "repoBranch": "feature-b", "revisionId": fb},
                "DETAIL": [{"fileName": "src/feat_b.py", "codeLines": [
                    {"lineLocation": 1, "genRatio": 50, "genMethod": "codeCompletion"},
                    {"lineLocation": 2, "genRatio": 50, "genMethod": "codeCompletion"},
                ]}],
            }, repo_dir, fb)

            # genCodeDesc for fc: src/feat_c.py — 2 human lines
            write_revision_protocol(protocol_dir, {
                "protocolName": "generatedTextDesc", "protocolVersion": "26.03", "codeAgent": "MergeAgent",
                "SUMMARY": {"totalCodeLines": 2, "fullGeneratedCodeLines": 0, "partialGeneratedCodeLines": 0},
                "REPOSITORY": {"repoURL": str(repo_dir), "repoBranch": "feature-c", "revisionId": fc},
                "DETAIL": [{"fileName": "src/feat_c.py", "codeLines": [
                    {"lineLocation": 1, "genRatio": 0, "genMethod": "Manual"},
                    {"lineLocation": 2, "genRatio": 0, "genMethod": "Manual"},
                ]}],
            }, repo_dir, fc)

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

            self.assertEqual(summary.get("totalCodeLines"), EXPECTED_TOTAL,
                             f"Expected totalCodeLines={EXPECTED_TOTAL} across 4 files × 2 lines")
            self.assertEqual(summary.get("fullGeneratedCodeLines"), EXPECTED_FULL,
                             f"Only feat_a.py lines (2) are full-AI")
            self.assertEqual(summary.get("partialGeneratedCodeLines"), EXPECTED_PARTIAL,
                             f"Only feat_b.py lines (2) are partial-AI")


if __name__ == "__main__":
    unittest.main()
