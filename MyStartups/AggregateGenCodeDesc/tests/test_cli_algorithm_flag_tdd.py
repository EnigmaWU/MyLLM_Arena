import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from tests.cli_test_support import GitRepoHarness, PROJECT_ROOT, UTILITY_PATH, run_cli, write_revision_protocol


FIXTURE_DIR = Path(__file__).resolve().parent.parent / "testdata" / "us1_live_changed_source_ratio"


class TestCliAlgorithmFlagTdd(unittest.TestCase):
    def test_cli_accepts_algorithm_flag(self) -> None:
        query = json.loads((FIXTURE_DIR / "query.json").read_text(encoding="utf-8"))
        revision_protocol = json.loads((FIXTURE_DIR / "01_genCodeDesc.json").read_text(encoding="utf-8"))

        with tempfile.TemporaryDirectory() as temp_dir:
            root_dir = Path(temp_dir)
            repo_dir = root_dir / "repo"
            protocol_dir = root_dir / "protocols"
            output_file = root_dir / "out.json"

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

            result = run_cli(
                repo_dir,
                output_file,
                protocol_dir,
                query,
                extra_args=["--algorithm", "A"],
            )

            self.assertEqual(result.returncode, 0)
            self.assertTrue(output_file.exists())

    def test_cli_rejects_legacy_model_flag(self) -> None:
        result = subprocess.run(
            [
                "python3",
                str(UTILITY_PATH),
                "--repoURL",
                "dummy-repo",
                "--repoBranch",
                "main",
                "--startTime",
                "2026-03-01",
                "--endTime",
                "2026-03-31",
                "--model",
                "A",
            ],
            cwd=PROJECT_ROOT,
            text=True,
            capture_output=True,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unrecognized arguments: --model A", result.stderr)


if __name__ == "__main__":
    unittest.main()