"""US-28 · Production Hardening — scope validation and file-size guard.

Acceptance criteria:
  AC-1  Invalid --scope values (Z, empty, lowercase a) are rejected with
        EXIT_INPUT_ERROR and a clear diagnostic.
  AC-2  Invalid --scope is rejected for BOTH Algorithm A and Algorithm B.
  AC-3  read_git_file_lines_at_revision raises RepositoryStateError when
        a single file exceeds MAX_FILE_SIZE_BYTES.
  AC-4  parse_blame raises RepositoryStateError when blame output exceeds
        MAX_FILE_SIZE_BYTES.
"""

import argparse
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import aggregateGenCodeDesc
from tests.cli_test_support import GitRepoHarness, load_json, run_cli, write_revision_protocol


FIXTURE_DIR = Path(__file__).resolve().parent.parent / "testdata" / "us1_live_changed_source_ratio"


class TestInvalidScopeRejection(unittest.TestCase):
    """AC-1/AC-2: Invalid --scope values are rejected at input validation."""

    def _run_with_scope(self, scope: str, algorithm: str = "A") -> subprocess.CompletedProcess[str]:
        query = load_json(FIXTURE_DIR / "query.json")
        revision_protocol = load_json(FIXTURE_DIR / "01_genCodeDesc.json")

        with tempfile.TemporaryDirectory() as temp_dir:
            root_dir = Path(temp_dir)
            repo_dir = root_dir / "repo"
            protocol_dir = root_dir / "protocols"
            output_file = root_dir / "out.json"

            repo_dir.mkdir()
            protocol_dir.mkdir()

            repo = GitRepoHarness(repo_dir)
            repo.write("src/calc.py", "def calc(x):\n    return x + 1\n")
            revision_id = repo.commit_all("r1", "2026-03-10T09:00:00Z")
            write_revision_protocol(protocol_dir, revision_protocol, repo_dir, revision_id)

            return subprocess.run(
                [
                    "python3",
                    str(Path(__file__).resolve().parent.parent / "aggregateGenCodeDesc.py"),
                    "--vcsType", "git",
                    "--repoURL", str(repo_dir),
                    "--repoBranch", "main",
                    "--startTime", query["startTime"],
                    "--endTime", query["endTime"],
                    "--outputFile", str(output_file),
                    "--genCodeDescSetDir", str(protocol_dir),
                    "--scope", scope,
                    "--algorithm", algorithm,
                ],
                cwd=repo_dir,
                text=True,
                capture_output=True,
            )

    def test_scope_Z_rejected_algorithm_a(self) -> None:
        result = self._run_with_scope("Z", algorithm="A")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--scope must be one of: A, B, C, D", result.stderr)

    def test_scope_Z_rejected_algorithm_b(self) -> None:
        result = self._run_with_scope("Z", algorithm="B")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--scope must be one of: A, B, C, D", result.stderr)

    def test_scope_lowercase_a_rejected(self) -> None:
        result = self._run_with_scope("a")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--scope must be one of: A, B, C, D", result.stderr)

    def test_scope_empty_rejected(self) -> None:
        result = self._run_with_scope("")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--scope must be one of: A, B, C, D", result.stderr)


class TestFileSizeGuard(unittest.TestCase):
    """AC-3/AC-4: Oversized VCS output raises RepositoryStateError."""

    def test_read_git_file_rejects_oversized_output(self) -> None:
        fake_result = MagicMock()
        fake_result.returncode = 0
        fake_result.stdout = "x" * (aggregateGenCodeDesc.MAX_FILE_SIZE_BYTES + 1)

        with patch.object(aggregateGenCodeDesc, "run_command", return_value=fake_result):
            with self.assertRaises(aggregateGenCodeDesc.RepositoryStateError) as ctx:
                aggregateGenCodeDesc.read_git_file_lines_at_revision(
                    Path("/fake"), "abc123", "large_file.py"
                )
            self.assertIn("exceeds", str(ctx.exception))

    def test_read_git_file_accepts_normal_output(self) -> None:
        fake_result = MagicMock()
        fake_result.returncode = 0
        fake_result.stdout = "line1\nline2\nline3\n"

        with patch.object(aggregateGenCodeDesc, "run_command", return_value=fake_result):
            lines = aggregateGenCodeDesc.read_git_file_lines_at_revision(
                Path("/fake"), "abc123", "normal_file.py"
            )
            self.assertEqual(lines, ["line1", "line2", "line3"])

    def test_parse_blame_rejects_oversized_output(self) -> None:
        oversized = "x" * (aggregateGenCodeDesc.MAX_FILE_SIZE_BYTES + 1)

        with patch.object(aggregateGenCodeDesc, "run_git", return_value=oversized):
            with self.assertRaises(aggregateGenCodeDesc.RepositoryStateError) as ctx:
                aggregateGenCodeDesc.parse_blame(Path("/fake"), "abc123", "large_file.py")
            self.assertIn("exceeds", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
