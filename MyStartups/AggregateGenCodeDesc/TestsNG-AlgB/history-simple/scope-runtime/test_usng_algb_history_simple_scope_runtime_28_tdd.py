import subprocess
import tempfile
import unittest
from pathlib import Path

from tests.cli_test_support import GitRepoHarness, write_revision_protocol, PROJECT_ROOT, UTILITY_PATH


class TestUsngAlgbHistorySimpleScopeRuntime28Tdd(unittest.TestCase):
    """USNG-ALGB-HISTORY-SIMPLE-SCOPE-RUNTIME-28: Production Hardening — File-Size Guard"""

    def test_oversized_file_raises_repository_state_error(self) -> None:
        """GIVEN a Git repository contains a file whose content exceeds MAX_FILE_SIZE_BYTES,
        WHEN Algorithm B reads the file through local git replay,
        THEN it raises RepositoryStateError with a clear diagnostic."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo_dir = root / "repo"
            protocol_dir = root / "protocols"
            output_file = root / "out.json"
            repo_dir.mkdir()
            protocol_dir.mkdir()

            repo = GitRepoHarness(repo_dir)

            # Create a file that exceeds MAX_FILE_SIZE_BYTES (10 MB)
            # MAX_FILE_SIZE_BYTES is 10 * 1024 * 1024
            oversized_content = "x = 1\n" * (10 * 1024 * 1024 // 6 + 1)
            repo.write("src/huge.py", oversized_content)
            r1 = repo.commit_all("r1", "2026-03-10T09:00:00Z")

            result = subprocess.run(
                [
                    "python3",
                    str(UTILITY_PATH),
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
            )

            # Should exit with non-zero due to RepositoryStateError
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("RepositoryStateError", result.stderr + result.stdout)


if __name__ == "__main__":
    unittest.main()
