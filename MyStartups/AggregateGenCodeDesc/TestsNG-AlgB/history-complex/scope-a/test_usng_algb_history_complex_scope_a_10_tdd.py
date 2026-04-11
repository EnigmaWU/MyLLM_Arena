import subprocess
import tempfile
import unittest
from pathlib import Path

from tests.cli_test_support import GitRepoHarness, PROJECT_ROOT, UTILITY_PATH, write_revision_protocol, load_json


# Scenario: 5-line file replayed across 6 commits (pre-window r1, then r2-r6 in-window).
# r2 rewrites line 1 (AI), r3 rewrites line 2 (partial), r4 rewrites line 3 (AI),
# r5 rewrites line 1 AGAIN (human, supersedes r2), r6 rewrites line 4 (partial).
# line 5 stays from r1 (pre-window) → excluded from live snapshot.
#
# Final live-snapshot expected result:
# line1: from r5 (in-window), genRatio=0 → total+1
# line2: from r3 (in-window), genRatio=50 → total+1, partial+1
# line3: from r4 (in-window), genRatio=100 → total+1, full+1
# line4: from r6 (in-window), genRatio=50 → total+1, partial+1
# line5: from r1 (pre-window, 2026-02-15) → excluded
# => totalCodeLines=4, full=1, partial=2

EXPECTED_TOTAL = 4
EXPECTED_FULL = 1
EXPECTED_PARTIAL = 2


class TestUsngAlgbHistoryComplexScopeA10Tdd(unittest.TestCase):
    """USNG-ALGB-HISTORY-COMPLEX-SCOPE-A-10: Deep History Must Preserve Latest Effective Attribution Via Replay"""

    maxDiff = None

    def test_deep_history_preserves_latest_effective_attribution(self) -> None:
        """AC-01 / AC-GIT-01: Repeatedly rewritten lines converge to latest effective attribution."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo_dir = root / "repo"
            protocol_dir = root / "protocols"
            output_file = root / "out.json"
            repo_dir.mkdir()
            protocol_dir.mkdir()

            repo = GitRepoHarness(repo_dir)
            file_path = "src/compute.py"

            # r1 (PRE-window): add file with 5 human lines
            repo.write(file_path, "a = 1\nb = 2\nc = 3\nd = 4\ne = 5\n")
            r1 = repo.commit_all("r1-pre", "2026-02-15T09:00:00Z")

            # r2 (in-window): rewrite line 1 → AI (genRatio=100)
            repo.write(file_path, "a = ai_a()\nb = 2\nc = 3\nd = 4\ne = 5\n")
            r2 = repo.commit_all("r2", "2026-03-05T09:00:00Z")

            # r3 (in-window): rewrite line 2 → partial AI (genRatio=50)
            repo.write(file_path, "a = ai_a()\nb = partial_b()\nc = 3\nd = 4\ne = 5\n")
            r3 = repo.commit_all("r3", "2026-03-10T09:00:00Z")

            # r4 (in-window): rewrite line 3 → AI (genRatio=100)
            repo.write(file_path, "a = ai_a()\nb = partial_b()\nc = ai_c()\nd = 4\ne = 5\n")
            r4 = repo.commit_all("r4", "2026-03-15T09:00:00Z")

            # r5 (in-window): rewrite line 1 AGAIN → human (supersedes r2's AI)
            repo.write(file_path, "a = human_a()\nb = partial_b()\nc = ai_c()\nd = 4\ne = 5\n")
            r5 = repo.commit_all("r5", "2026-03-20T09:00:00Z")

            # r6 (in-window): rewrite line 4 → partial AI (genRatio=50)
            repo.write(file_path, "a = human_a()\nb = partial_b()\nc = ai_c()\nd = partial_d()\ne = 5\n")
            r6 = repo.commit_all("r6", "2026-03-25T09:00:00Z")

            # genCodeDesc for r2: line 1 = genRatio 100
            write_revision_protocol(protocol_dir, {
                "protocolName": "generatedTextDesc", "protocolVersion": "26.03", "codeAgent": "DeepAgent",
                "SUMMARY": {"totalCodeLines": 1, "fullGeneratedCodeLines": 1, "partialGeneratedCodeLines": 0},
                "REPOSITORY": {"repoURL": str(repo_dir), "repoBranch": "main", "revisionId": r2},
                "DETAIL": [{"fileName": file_path, "codeLines": [{"lineLocation": 1, "genRatio": 100, "genMethod": "codeCompletion"}]}],
            }, repo_dir, r2)

            # genCodeDesc for r3: line 2 = genRatio 50
            write_revision_protocol(protocol_dir, {
                "protocolName": "generatedTextDesc", "protocolVersion": "26.03", "codeAgent": "DeepAgent",
                "SUMMARY": {"totalCodeLines": 1, "fullGeneratedCodeLines": 0, "partialGeneratedCodeLines": 1},
                "REPOSITORY": {"repoURL": str(repo_dir), "repoBranch": "main", "revisionId": r3},
                "DETAIL": [{"fileName": file_path, "codeLines": [{"lineLocation": 2, "genRatio": 50, "genMethod": "codeCompletion"}]}],
            }, repo_dir, r3)

            # genCodeDesc for r4: line 3 = genRatio 100
            write_revision_protocol(protocol_dir, {
                "protocolName": "generatedTextDesc", "protocolVersion": "26.03", "codeAgent": "DeepAgent",
                "SUMMARY": {"totalCodeLines": 1, "fullGeneratedCodeLines": 1, "partialGeneratedCodeLines": 0},
                "REPOSITORY": {"repoURL": str(repo_dir), "repoBranch": "main", "revisionId": r4},
                "DETAIL": [{"fileName": file_path, "codeLines": [{"lineLocation": 3, "genRatio": 100, "genMethod": "codeCompletion"}]}],
            }, repo_dir, r4)

            # genCodeDesc for r5: line 1 = genRatio 0 (human override — supersedes r2's AI)
            write_revision_protocol(protocol_dir, {
                "protocolName": "generatedTextDesc", "protocolVersion": "26.03", "codeAgent": "DeepAgent",
                "SUMMARY": {"totalCodeLines": 1, "fullGeneratedCodeLines": 0, "partialGeneratedCodeLines": 0},
                "REPOSITORY": {"repoURL": str(repo_dir), "repoBranch": "main", "revisionId": r5},
                "DETAIL": [{"fileName": file_path, "codeLines": [{"lineLocation": 1, "genRatio": 0, "genMethod": "Manual"}]}],
            }, repo_dir, r5)

            # genCodeDesc for r6: line 4 = genRatio 50
            write_revision_protocol(protocol_dir, {
                "protocolName": "generatedTextDesc", "protocolVersion": "26.03", "codeAgent": "DeepAgent",
                "SUMMARY": {"totalCodeLines": 1, "fullGeneratedCodeLines": 0, "partialGeneratedCodeLines": 1},
                "REPOSITORY": {"repoURL": str(repo_dir), "repoBranch": "main", "revisionId": r6},
                "DETAIL": [{"fileName": file_path, "codeLines": [{"lineLocation": 4, "genRatio": 50, "genMethod": "codeCompletion"}]}],
            }, repo_dir, r6)

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

            # Deep history: line1 was touched by r2 (AI gen=100) then r5 (human gen=0).
            # Latest effective: r5 overwrote r2's AI, so line1 is human now.
            self.assertEqual(summary.get("totalCodeLines"), EXPECTED_TOTAL,
                             "Deep history: pre-window line5 must be excluded; in-window lines 1-4 counted")
            self.assertEqual(summary.get("fullGeneratedCodeLines"), EXPECTED_FULL,
                             "Line3 from r4 (gen=100) is the only full-AI line; r2's AI on line1 was superseded by r5")
            self.assertEqual(summary.get("partialGeneratedCodeLines"), EXPECTED_PARTIAL,
                             "Lines 2 and 4 from r3/r6 (gen=50) are partial")


if __name__ == "__main__":
    unittest.main()
