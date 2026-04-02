import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from tests.cli_test_support import (
    GitRepoHarness,
    PROJECT_ROOT,
    SvnRepoHarness,
    UTILITY_PATH,
    load_json,
    run_cli,
    write_revision_protocol,
)


FIXTURE_GIT_DIR = Path(__file__).resolve().parent.parent / "testdata" / "us1_live_changed_source_ratio"
FIXTURE_SVN_DIR = Path(__file__).resolve().parent.parent / "testdata" / "us1_live_changed_source_ratio_svn"


@unittest.skipUnless(shutil.which("svn") and shutil.which("svnadmin"), "svn tooling not installed")
class TestUs1MatrixParityTdd(unittest.TestCase):
    maxDiff = None

    def _normalized_contract(self, result: dict) -> dict:
        return {
            "protocolName": result["protocolName"],
            "protocolVersion": result["protocolVersion"],
            "SUMMARY": result["SUMMARY"],
        }

    def _run_algorithm_a_git_cell(self, root_dir: Path) -> dict:
        query = load_json(FIXTURE_GIT_DIR / "query.json")
        revision_protocol = load_json(FIXTURE_GIT_DIR / "01_genCodeDesc.json")

        repo_dir = root_dir / "git-repo"
        protocol_dir = root_dir / "git-protocols"
        output_file = root_dir / "git-out.json"
        repo_dir.mkdir()
        protocol_dir.mkdir()

        repo = GitRepoHarness(repo_dir)
        repo.write(
            "src/calc.py",
            "def calc(x):\n"
            "    value = x + 1\n"
            "    boosted = value * 2\n"
            "    return boosted\n",
        )
        revision_id = repo.commit_all("us1-r1", "2026-03-10T09:00:00Z")
        write_revision_protocol(protocol_dir, revision_protocol, repo_dir, revision_id)

        run_cli(repo_dir, output_file, protocol_dir, query)
        return load_json(output_file)

    def _run_algorithm_a_svn_cell(self, root_dir: Path) -> dict:
        query = load_json(FIXTURE_SVN_DIR / "query.json")
        revision_protocol = load_json(FIXTURE_SVN_DIR / "01_genCodeDesc.json")

        repo_dir = root_dir / "svn-repo"
        working_copy_dir = root_dir / "svn-wc"
        protocol_dir = root_dir / "svn-protocols"
        output_file = root_dir / "svn-out.json"
        protocol_dir.mkdir()

        repo = SvnRepoHarness(repo_dir, working_copy_dir)
        trunk_file = working_copy_dir / "trunk" / "src" / "demo.py"
        trunk_file.parent.mkdir(parents=True, exist_ok=True)
        trunk_file.write_text(
            "def calc(x):\n"
            "    value = x + 1\n"
            "    boosted = value * 2\n"
            "    return boosted\n",
            encoding="utf-8",
        )
        repo.add("trunk/src/demo.py")
        revision_id = repo.commit_all("us1-svn-r2", "2026-03-10T09:00:00.000000Z")

        write_revision_protocol(
            protocol_dir,
            revision_protocol,
            repo.repo_dir,
            revision_id,
            repo_url_override=repo.repo_url,
        )
        run_cli(
            repo.repo_dir,
            output_file,
            protocol_dir,
            query,
            repo_url_override=repo.repo_url,
        )
        return load_json(output_file)

    def _run_algorithm_b_cell(self, fixture_dir: Path) -> dict:
        query = load_json(fixture_dir / "query.json")

        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "out.json"
            subprocess.run(
                [
                    "python3",
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
                    "B",
                    "--scope",
                    query["scope"],
                    "--outputFile",
                    str(output_file),
                    "--genCodeDescSetDir",
                    str(fixture_dir),
                    "--commitDiffSetDir",
                    str(fixture_dir / "commitDiffSet"),
                ],
                cwd=PROJECT_ROOT,
                text=True,
                capture_output=True,
                check=True,
            )
            return load_json(output_file)

    def test_us1_all_four_cells_share_same_observable_contract(self) -> None:
        expected_git = load_json(FIXTURE_GIT_DIR / "expected_result.json")
        expected_svn = load_json(FIXTURE_SVN_DIR / "expected_result.json")
        expected_contract = self._normalized_contract(expected_git)

        self.assertEqual(expected_contract, self._normalized_contract(expected_svn))

        with tempfile.TemporaryDirectory() as temp_dir:
            root_dir = Path(temp_dir)
            algorithm_a_git = self._run_algorithm_a_git_cell(root_dir)
            algorithm_a_svn = self._run_algorithm_a_svn_cell(root_dir)

        algorithm_b_git = self._run_algorithm_b_cell(FIXTURE_GIT_DIR)
        algorithm_b_svn = self._run_algorithm_b_cell(FIXTURE_SVN_DIR)

        self.assertEqual(self._normalized_contract(algorithm_a_git), expected_contract)
        self.assertEqual(self._normalized_contract(algorithm_a_svn), expected_contract)
        self.assertEqual(self._normalized_contract(algorithm_b_git), expected_contract)
        self.assertEqual(self._normalized_contract(algorithm_b_svn), expected_contract)

        self.assertEqual(self._normalized_contract(algorithm_a_git), self._normalized_contract(algorithm_a_svn))
        self.assertEqual(self._normalized_contract(algorithm_a_git), self._normalized_contract(algorithm_b_git))
        self.assertEqual(self._normalized_contract(algorithm_a_git), self._normalized_contract(algorithm_b_svn))

        self.assertEqual(algorithm_a_git["REPOSITORY"]["vcsType"], "git")
        self.assertEqual(algorithm_a_svn["REPOSITORY"]["vcsType"], "svn")
        self.assertEqual(algorithm_b_git["REPOSITORY"]["vcsType"], "git")
        self.assertEqual(algorithm_b_svn["REPOSITORY"]["vcsType"], "svn")


if __name__ == "__main__":
    unittest.main()