import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import pytest

from tests.cli_test_support import SvnRepoHarness


@pytest.mark.experimental_svn
@unittest.skipUnless(shutil.which("svn") and shutil.which("svnadmin"), "svn tooling not installed")
class TestRealSvnLineageExperiments(unittest.TestCase):
    def test_branch_owned_file_merge_can_preserve_branch_origin_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = SvnRepoHarness(root / "repo", root / "wc")

            def run(command: list[str]) -> str:
                return subprocess.run(command, check=True, capture_output=True, text=True).stdout.strip()

            (repo.working_copy_dir / "branches").mkdir()
            run(["svn", "add", str(repo.working_copy_dir / "branches")])
            repo.commit_all("create branches", "2026-02-25T09:00:00.000000Z")

            repo.write("trunk/src/alpha.py", "carry = 1\nalpha = base\nstable = 2\n")
            repo.add("trunk/src/alpha.py")
            repo.commit_all("r1", "2026-03-01T09:00:00.000000Z")

            output = subprocess.run(
                ["svn", "copy", repo.trunk_url, f"{repo.repo_url}/branches/feature-alpha", "-m", "copy alpha"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout
            copy_revision = next(line for line in output.splitlines() if line.startswith("Committed revision ")).removeprefix("Committed revision ").removesuffix(".")
            run(["svn", "propset", "--revprop", "-r", copy_revision, "svn:date", "2026-03-02T09:00:00.000000Z", repo.repo_url])

            branch_wc = root / "alpha-branch"
            subprocess.run(["svn", "checkout", f"{repo.repo_url}/branches/feature-alpha", str(branch_wc)], check=True, capture_output=True, text=True)
            (branch_wc / "src" / "alpha.py").write_text("carry = 1\nalpha = ai(base)\nstable = 2\n", encoding="utf-8")
            branch_commit = subprocess.run(["svn", "commit", "-m", "branch rewrite", str(branch_wc)], check=True, capture_output=True, text=True).stdout
            branch_revision = next(line for line in branch_commit.splitlines() if line.startswith("Committed revision ")).removeprefix("Committed revision ").removesuffix(".")
            run(["svn", "propset", "--revprop", "-r", branch_revision, "svn:date", "2026-03-03T09:00:00.000000Z", repo.repo_url])

            run(["svn", "update", str(repo.working_copy_dir)])
            run(["svn", "merge", "-c", branch_revision, f"{repo.repo_url}/branches/feature-alpha", str(repo.working_copy_dir / "trunk")])
            trunk_merge = repo.commit_all("merge alpha", "2026-03-04T09:00:00.000000Z")

            blame_xml = subprocess.run(
                ["svn", "blame", "--xml", "-g", "-r", trunk_merge, f"{repo.trunk_url}/src/alpha.py"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout

            self.assertIn(f'revision="{branch_revision}"', blame_xml)
            self.assertIn('path="/branches/feature-alpha/src/alpha.py"', blame_xml)

    def test_same_file_multi_branch_merge_remains_unsuitable_for_branch_tip_claims(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = SvnRepoHarness(root / "repo", root / "wc")

            def run(command: list[str]) -> str:
                return subprocess.run(command, check=True, capture_output=True, text=True).stdout.strip()

            (repo.working_copy_dir / "branches").mkdir()
            run(["svn", "add", str(repo.working_copy_dir / "branches")])
            repo.commit_all("create branches", "2026-02-25T09:00:00.000000Z")

            repo.write("trunk/src/shared.py", "a = 1\nb = 2\nc = 3\nd = 4\n")
            repo.add("trunk/src/shared.py")
            repo.commit_all("r1", "2026-03-01T09:00:00.000000Z")

            repo.write("trunk/src/shared.py", "a = main(1)\nb = 2\nc = 3\nd = 4\n")
            repo.commit_all("r2", "2026-03-02T09:00:00.000000Z")

            for offset, branch_name in enumerate(["feature-b", "feature-c"], start=3):
                output = subprocess.run(
                    ["svn", "copy", repo.trunk_url, f"{repo.repo_url}/branches/{branch_name}", "-m", f"copy {branch_name}"],
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout
                revision_id = next(line for line in output.splitlines() if line.startswith("Committed revision ")).removeprefix("Committed revision ").removesuffix(".")
                run(["svn", "propset", "--revprop", "-r", revision_id, "svn:date", f"2026-03-0{offset}T09:00:00.000000Z", repo.repo_url])

            run(["svn", "switch", f"{repo.repo_url}/branches/feature-b", str(repo.working_copy_dir / "trunk")])
            repo.write("trunk/src/shared.py", "a = main(1)\nb = ai(2)\nc = 3\nd = 4\n")
            branch_b_revision = repo.commit_all("r3", "2026-03-05T09:00:00.000000Z")

            run(["svn", "switch", f"{repo.repo_url}/branches/feature-c", str(repo.working_copy_dir / "trunk")])
            repo.write("trunk/src/shared.py", "a = main(1)\nb = 2\nc = mixed(3)\nd = 4\n")
            branch_c_revision = repo.commit_all("r4", "2026-03-06T09:00:00.000000Z")

            run(["svn", "switch", repo.trunk_url, str(repo.working_copy_dir / "trunk")])
            run(["svn", "update", str(repo.working_copy_dir)])
            run(["svn", "merge", "-c", branch_b_revision, f"{repo.repo_url}/branches/feature-b", str(repo.working_copy_dir / "trunk")])
            trunk_merge_b_revision = repo.commit_all("merge b", "2026-03-07T09:00:00.000000Z")

            run(["svn", "update", str(repo.working_copy_dir)])
            run(["svn", "merge", "-c", branch_c_revision, f"{repo.repo_url}/branches/feature-c", str(repo.working_copy_dir / "trunk")])
            trunk_merge_c_revision = repo.commit_all("merge c", "2026-03-08T09:00:00.000000Z")

            blame_xml = subprocess.run(
                ["svn", "blame", "--xml", "-g", "-r", trunk_merge_c_revision, f"{repo.trunk_url}/src/shared.py"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout

            self.assertIn(f'revision="{trunk_merge_b_revision}"', blame_xml)
            self.assertIn(f'revision="{trunk_merge_c_revision}"', blame_xml)
            self.assertNotIn(f'path="/branches/feature-b/src/shared.py"', blame_xml)
            self.assertNotIn(f'path="/branches/feature-c/src/shared.py"', blame_xml)


if __name__ == "__main__":
    unittest.main()