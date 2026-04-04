"""US-19: SVN-supported subset for Algorithm-B period contribution.

Uses the offline fixtures path (--commitDiffSetDir) with SVN-style revision IDs.
This verifies the period-added metric works for SVN repositories through the
offline replay path.

Scenario:
  r1 patch: creates src/report.py with 2 lines (1 AI, 1 human)
  r2 patch: adds 1 AI line to src/report.py

Expected:
  totalCodeLines = 3, fullGeneratedCodeLines = 2, partialGeneratedCodeLines = 0
"""

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from aggregateGenCodeDesc import PROTOCOL_VERSION
from tests.cli_test_support import PROJECT_ROOT, UTILITY_PATH


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class TestUS19PeriodAddedSvnSubset(unittest.TestCase):

    def _build_svn_fixtures(self, root_dir: Path):
        protocol_dir = root_dir / "protocols"
        commit_diff_dir = root_dir / "commitDiffSet"
        protocol_dir.mkdir()
        commit_diff_dir.mkdir()

        # r1 patch: create file with 2 lines
        (commit_diff_dir / "2_commitDiff.patch").write_text(
            "diff --git a/trunk/src/report.py b/trunk/src/report.py\n"
            "--- /dev/null\n"
            "+++ b/trunk/src/report.py\n"
            "@@ -0,0 +1,2 @@\n"
            "+def report():\n"
            "+    data = ai_fetch()\n",
            encoding="utf-8",
        )

        # r2 patch: add 1 line
        (commit_diff_dir / "3_commitDiff.patch").write_text(
            "diff --git a/trunk/src/report.py b/trunk/src/report.py\n"
            "--- a/trunk/src/report.py\n"
            "+++ b/trunk/src/report.py\n"
            "@@ -1,2 +1,3 @@\n"
            " def report():\n"
            "     data = ai_fetch()\n"
            "+    result = ai_process(data)\n",
            encoding="utf-8",
        )

        # Protocol for r1 (revision 2): line 2 is AI
        (protocol_dir / "2_genCodeDesc.json").write_text(
            json.dumps({
                "protocolName": "generatedTextDesc",
                "protocolVersion": PROTOCOL_VERSION,
                "SUMMARY": {"totalCodeLines": 1, "fullGeneratedCodeLines": 1, "partialGeneratedCodeLines": 0},
                "REPOSITORY": {
                    "vcsType": "svn",
                    "repoURL": "file:///svn/testrepo",
                    "repoBranch": "trunk",
                    "revisionId": "2",
                },
                "DETAIL": [
                    {
                        "fileName": "trunk/src/report.py",
                        "codeLines": [{"lineLocation": 2, "genRatio": 100}],
                    }
                ],
            }, indent=2),
            encoding="utf-8",
        )

        # Protocol for r2 (revision 3): line 3 is AI
        (protocol_dir / "3_genCodeDesc.json").write_text(
            json.dumps({
                "protocolName": "generatedTextDesc",
                "protocolVersion": PROTOCOL_VERSION,
                "SUMMARY": {"totalCodeLines": 1, "fullGeneratedCodeLines": 1, "partialGeneratedCodeLines": 0},
                "REPOSITORY": {
                    "vcsType": "svn",
                    "repoURL": "file:///svn/testrepo",
                    "repoBranch": "trunk",
                    "revisionId": "3",
                },
                "DETAIL": [
                    {
                        "fileName": "trunk/src/report.py",
                        "codeLines": [{"lineLocation": 3, "genRatio": 100}],
                    }
                ],
            }, indent=2),
            encoding="utf-8",
        )

        # query.json with explicit includedRevisionIds
        query_json = {
            "includedRevisionIds": ["2", "3"],
            "endRevisionId": "3",
        }
        (protocol_dir / "query.json").write_text(
            json.dumps(query_json, indent=2),
            encoding="utf-8",
        )

        return protocol_dir, commit_diff_dir

    def test_svn_period_added_via_offline_fixtures(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            protocol_dir, commit_diff_dir = self._build_svn_fixtures(Path(temp_dir))
            output_file = Path(temp_dir) / "out.json"

            result = subprocess.run(
                [
                    "python3",
                    str(UTILITY_PATH),
                    "--vcsType", "svn",
                    "--repoURL", "file:///svn/testrepo",
                    "--repoBranch", "trunk",
                    "--startTime", "2026-03-01",
                    "--endTime", "2026-03-31",
                    "--algorithm", "B",
                    "--metric", "period_added_ai_ratio",
                    "--scope", "A",
                    "--outputFile", str(output_file),
                    "--genCodeDescSetDir", str(protocol_dir),
                    "--commitDiffSetDir", str(commit_diff_dir),
                ],
                cwd=PROJECT_ROOT,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            actual = _load_json(output_file)

        self.assertEqual(
            actual["SUMMARY"],
            {
                "totalCodeLines": 3,
                "fullGeneratedCodeLines": 2,
                "partialGeneratedCodeLines": 0,
            },
        )
        self.assertEqual(actual["REPOSITORY"]["vcsType"], "svn")
        self.assertEqual(actual["REPOSITORY"]["revisionId"], "3")

    def test_svn_period_added_works_without_repoURL_and_repoBranch(self) -> None:
        """When --commitDiffSetDir is provided, --repoURL and --repoBranch are optional."""
        with tempfile.TemporaryDirectory() as temp_dir:
            protocol_dir, commit_diff_dir = self._build_svn_fixtures(Path(temp_dir))
            output_file = Path(temp_dir) / "out.json"

            result = subprocess.run(
                [
                    "python3",
                    str(UTILITY_PATH),
                    "--vcsType", "svn",
                    "--startTime", "2026-03-01",
                    "--endTime", "2026-03-31",
                    "--algorithm", "B",
                    "--metric", "period_added_ai_ratio",
                    "--scope", "A",
                    "--outputFile", str(output_file),
                    "--genCodeDescSetDir", str(protocol_dir),
                    "--commitDiffSetDir", str(commit_diff_dir),
                ],
                cwd=PROJECT_ROOT,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            actual = _load_json(output_file)

        self.assertEqual(actual["SUMMARY"]["totalCodeLines"], 3)
        self.assertEqual(actual["SUMMARY"]["fullGeneratedCodeLines"], 2)
        self.assertEqual(actual["REPOSITORY"]["revisionId"], "3")


if __name__ == "__main__":
    unittest.main()
