import unittest
import tempfile
from pathlib import Path

from tests.cli_test_support import GitRepoHarness, load_json, run_cli, write_revision_protocol


class TestUs27CrossAlgorithmScopeParityTdd(unittest.TestCase):
    """US-27: Algorithm A and Algorithm B must produce the same SUMMARY
    for every scope (A, B, C, D) on the same repository content."""

    maxDiff = None

    def _build_shared_repo(self, root_dir: Path) -> tuple[Path, Path, str]:
        """Create a repo with source + doc files and matching protocol.
        Returns (repo_dir, protocol_dir, revision_id)."""
        repo_dir = root_dir / "repo"
        protocol_dir = root_dir / "protocols"
        repo_dir.mkdir()
        protocol_dir.mkdir()

        repo = GitRepoHarness(repo_dir)

        # Source file: 4 lines — 2 comments + 2 code
        repo.write(
            "src/calc.py",
            "# AI helper\n"
            "def calc(x):\n"
            "    # boost\n"
            "    return x + 1\n",
        )
        # Doc file: 2 non-blank lines
        repo.write(
            "docs/spec.md",
            "# Spec\n"
            "Human written.\n",
        )
        revision_id = repo.commit_all("us27-r1", "2026-03-10T09:00:00Z")

        # Protocol with both codeLines and docLines
        protocol = {
            "protocolName": "generatedTextDesc",
            "protocolVersion": "26.03",
            "codeAgent": "TestAgent",
            "SUMMARY": {
                "totalCodeLines": 4,
                "fullGeneratedCodeLines": 2,
                "partialGeneratedCodeLines": 1,
                "totalDocLines": 2,
                "fullGeneratedDocLines": 1,
                "partialGeneratedDocLines": 0,
            },
            "DETAIL": [
                {
                    "fileName": "src/calc.py",
                    "codeLines": [
                        {"lineLocation": 1, "genRatio": 100, "genMethod": "codeCompletion"},
                        {"lineLocation": 2, "genRatio": 100, "genMethod": "codeCompletion"},
                        {"lineLocation": 3, "genRatio": 50, "genMethod": "codeCompletion"},
                    ],
                },
                {
                    "fileName": "docs/spec.md",
                    "docLines": [
                        {"lineLocation": 1, "genRatio": 100, "genMethod": "vibeCoding"},
                    ],
                },
            ],
            "REPOSITORY": {
                "repoURL": str(repo_dir),
                "repoBranch": "main",
                "revisionId": revision_id,
            },
        }
        write_revision_protocol(protocol_dir, protocol, repo_dir, revision_id)
        return repo_dir, protocol_dir, revision_id

    def _run_algorithm_a(self, repo_dir: Path, protocol_dir: Path, scope: str) -> dict:
        with tempfile.TemporaryDirectory() as out_dir:
            output_file = Path(out_dir) / "out.json"
            query = {
                "vcsType": "git",
                "repoURL": str(repo_dir),
                "repoBranch": "main",
                "startTime": "2026-03-01",
                "endTime": "2026-03-31",
                "scope": scope,
            }
            run_cli(repo_dir, output_file, protocol_dir, query)
            return load_json(output_file)

    def _run_algorithm_b(self, repo_dir: Path, protocol_dir: Path, scope: str) -> dict:
        with tempfile.TemporaryDirectory() as out_dir:
            output_file = Path(out_dir) / "out.json"
            query = {
                "vcsType": "git",
                "repoURL": str(repo_dir),
                "repoBranch": "main",
                "startTime": "2026-03-01",
                "endTime": "2026-03-31",
                "scope": scope,
            }
            run_cli(
                repo_dir,
                output_file,
                protocol_dir,
                query,
                extra_args=["--algorithm", "B"],
            )
            return load_json(output_file)

    def test_scope_a_algorithm_a_and_b_produce_same_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_dir, protocol_dir, _ = self._build_shared_repo(Path(temp_dir))
            summary_a = self._run_algorithm_a(repo_dir, protocol_dir, "A")["SUMMARY"]
            summary_b = self._run_algorithm_b(repo_dir, protocol_dir, "A")["SUMMARY"]
            self.assertEqual(summary_a, summary_b)
            self.assertIn("totalCodeLines", summary_a)

    def test_scope_b_algorithm_a_and_b_produce_same_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_dir, protocol_dir, _ = self._build_shared_repo(Path(temp_dir))
            summary_a = self._run_algorithm_a(repo_dir, protocol_dir, "B")["SUMMARY"]
            summary_b = self._run_algorithm_b(repo_dir, protocol_dir, "B")["SUMMARY"]
            self.assertEqual(summary_a, summary_b)
            self.assertIn("totalCodeLines", summary_a)

    def test_scope_c_algorithm_a_and_b_produce_same_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_dir, protocol_dir, _ = self._build_shared_repo(Path(temp_dir))
            summary_a = self._run_algorithm_a(repo_dir, protocol_dir, "C")["SUMMARY"]
            summary_b = self._run_algorithm_b(repo_dir, protocol_dir, "C")["SUMMARY"]
            self.assertEqual(summary_a, summary_b)
            self.assertIn("totalDocLines", summary_a)
            self.assertNotIn("totalCodeLines", summary_a)

    def test_scope_d_algorithm_a_and_b_produce_same_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_dir, protocol_dir, _ = self._build_shared_repo(Path(temp_dir))
            summary_a = self._run_algorithm_a(repo_dir, protocol_dir, "D")["SUMMARY"]
            summary_b = self._run_algorithm_b(repo_dir, protocol_dir, "D")["SUMMARY"]
            self.assertEqual(summary_a, summary_b)
            self.assertIn("totalCodeLines", summary_a)

    def test_cross_algorithm_contract_shape_matches_for_all_scopes(self) -> None:
        """Verify protocolName and protocolVersion match across algorithms for every scope."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_dir, protocol_dir, _ = self._build_shared_repo(Path(temp_dir))
            for scope in ("A", "B", "C", "D"):
                with self.subTest(scope=scope):
                    result_a = self._run_algorithm_a(repo_dir, protocol_dir, scope)
                    result_b = self._run_algorithm_b(repo_dir, protocol_dir, scope)
                    self.assertEqual(result_a["protocolName"], result_b["protocolName"])
                    self.assertEqual(result_a["protocolVersion"], result_b["protocolVersion"])
                    self.assertEqual(result_a["SUMMARY"], result_b["SUMMARY"])


if __name__ == "__main__":
    unittest.main()
