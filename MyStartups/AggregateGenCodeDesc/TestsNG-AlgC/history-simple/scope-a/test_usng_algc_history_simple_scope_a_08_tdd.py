import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.cli_test_support import PROJECT_ROOT, UTILITY_PATH, load_json


FIXTURE_GIT_DIR = Path(__file__).resolve().parents[3] / "TestdataNG-AlgC" / "history-simple" / "scope-a" / "08" / "git" / "default"
FIXTURE_SVN_DIR = Path(__file__).resolve().parents[3] / "TestdataNG-AlgC" / "history-simple" / "scope-a" / "08" / "svn" / "default"


class TestUsngAlgcHistorySimpleScopeA08Tdd(unittest.TestCase):
    maxDiff = None

    def _run_cli(self, fixture_dir: Path, env: dict[str, str] | None = None) -> dict:
        query = load_json(fixture_dir / "query.json")

        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "out.json"
            subprocess.run(
                [
                    sys.executable,
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
                    "C",
                    "--scope",
                    query["scope"],
                    "--outputFile",
                    str(output_file),
                    "--genCodeDescSetDir",
                    str(fixture_dir),
                ],
                cwd=PROJECT_ROOT,
                env=env,
                text=True,
                capture_output=True,
                check=True,
            )
            return load_json(output_file)

    def _normalized_contract(self, result: dict) -> dict:
        return {
            "protocolName": result["protocolName"],
            "protocolVersion": result["protocolVersion"],
            "SUMMARY": result["SUMMARY"],
        }

    def test_git_and_svn_share_same_observable_summary_contract(self) -> None:
        expected_git = load_json(FIXTURE_GIT_DIR / "expected_result.json")
        expected_svn = load_json(FIXTURE_SVN_DIR / "expected_result.json")

        self.assertEqual(self._normalized_contract(expected_git), self._normalized_contract(expected_svn))

        actual_git = self._run_cli(FIXTURE_GIT_DIR)
        actual_svn = self._run_cli(FIXTURE_SVN_DIR)
        self.assertEqual(self._normalized_contract(actual_git), self._normalized_contract(expected_git))
        self.assertEqual(self._normalized_contract(actual_svn), self._normalized_contract(expected_svn))

    def test_git_and_svn_inputs_do_not_require_vcs_binaries_at_runtime(self) -> None:
        hermetic_env = dict(os.environ)
        hermetic_env["PATH"] = "/nonexistent"

        actual_git = self._run_cli(FIXTURE_GIT_DIR, env=hermetic_env)
        actual_svn = self._run_cli(FIXTURE_SVN_DIR, env=hermetic_env)

        expected_git = load_json(FIXTURE_GIT_DIR / "expected_result.json")
        expected_svn = load_json(FIXTURE_SVN_DIR / "expected_result.json")
        self.assertEqual(actual_git, expected_git)
        self.assertEqual(actual_svn, expected_svn)


if __name__ == "__main__":
    unittest.main()
