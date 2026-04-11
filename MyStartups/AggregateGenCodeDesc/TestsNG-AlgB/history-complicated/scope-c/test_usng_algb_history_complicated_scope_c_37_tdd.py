import subprocess
import tempfile
import unittest
from pathlib import Path

from tests.cli_test_support import PROJECT_ROOT, UTILITY_PATH, build_query_args_cli_args, load_json


FIXTURE_GIT_DIR = Path(__file__).resolve().parents[3] / "TestdataNG-AlgB" / "history-complicated" / "scope-c" / "37" / "git" / "default"


class TestUsngAlgbHistoryComplicatedScopeC37Tdd(unittest.TestCase):
    """USNG-ALGB-HISTORY-COMPLICATED-SCOPE-C-37: Attribution Contract Applies Identically To Documentation Lines Via Replay (Scope C)"""

    maxDiff = None

    def _run_cli(self, fixture_dir: Path) -> dict:
        query = load_json(fixture_dir / "query.json")
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "out.json"
            subprocess.run(
                [
                    "python3", str(UTILITY_PATH),
                    "--vcsType", query["vcsType"],
                    "--repoURL", query["repoURL"],
                    "--repoBranch", query["repoBranch"],
                    "--startTime", query["startTime"],
                    "--endTime", query["endTime"],
                    "--algorithm", "B",
                    "--scope", query["scope"],
                    *build_query_args_cli_args(query, include_replay_selection=True),
                    "--outputFile", str(output_file),
                    "--commitDiffSetDir", str(fixture_dir / "commitDiffSet"),
                    "--genCodeDescSetDir", str(fixture_dir),
                ],
                cwd=PROJECT_ROOT, text=True, capture_output=True, check=True,
            )
            return load_json(output_file)

    def test_attribution_contract_applies_to_scope_c_doc_lines(self) -> None:
        expected_result = load_json(FIXTURE_GIT_DIR / "expected_result.json")
        actual_result = self._run_cli(FIXTURE_GIT_DIR)
        summary = actual_result.get("SUMMARY", {})
        self.assertIn("totalDocLines", summary, "Scope C result must report totalDocLines (not totalCodeLines)")
        self.assertEqual(actual_result, expected_result)


if __name__ == "__main__":
    unittest.main()
