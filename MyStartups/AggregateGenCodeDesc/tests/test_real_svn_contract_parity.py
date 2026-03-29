import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


@unittest.skipUnless(shutil.which("svn") and shutil.which("svnadmin"), "svn tooling not installed")
class TestRealSvnContractParity(unittest.TestCase):
    def test_local_svn_repo_can_be_created_for_future_parity_tests(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo_dir = root / "repo"
            wc_dir = root / "wc"

            subprocess.run(["svnadmin", "create", str(repo_dir)], check=True, capture_output=True, text=True)
            subprocess.run(["svn", "checkout", f"file://{repo_dir}", str(wc_dir)], check=True, capture_output=True, text=True)
            (wc_dir / "trunk").mkdir()
            subprocess.run(["svn", "add", str(wc_dir / "trunk")], check=True, capture_output=True, text=True)
            subprocess.run(["svn", "commit", "-m", "create trunk", str(wc_dir)], check=True, capture_output=True, text=True)

            trunk_file = wc_dir / "trunk" / "calc.py"
            trunk_file.write_text("def calc(x):\n    return x + 1\n", encoding="utf-8")
            subprocess.run(["svn", "add", str(trunk_file)], check=True, capture_output=True, text=True)
            subprocess.run(["svn", "commit", "-m", "add calc", str(wc_dir)], check=True, capture_output=True, text=True)

            blame = subprocess.run(
                ["svn", "blame", str(trunk_file)],
                check=True,
                capture_output=True,
                text=True,
            ).stdout
            self.assertIn("def calc(x):", blame)


if __name__ == "__main__":
    unittest.main()
