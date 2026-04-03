import unittest
import tempfile
from pathlib import Path

from tests.cli_test_support import GitRepoHarness, UTILITY_PATH, load_json, run_cli, write_revision_protocol


FIXTURE_DIR = Path(__file__).resolve().parent.parent / "testdata" / "us23_scope_parity_matrix"


class TestUs23ScopeParityMatrixTdd(unittest.TestCase):
    maxDiff = None

    def _build_repo_and_run(self, scope: str) -> dict:
        """Create a shared repo with source + doc files, run with the given scope."""
        revision_protocol = load_json(FIXTURE_DIR / "01_genCodeDesc.json")

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
                "# AI helper\n"
                "def calc(x):\n"
                "    # boost\n"
                "    return x + 1\n",
            )
            repo.write(
                "docs/spec.md",
                "# Spec\n"
                "Human written.\n",
            )
            revision_id = repo.commit_all("us23-r1", "2026-03-10T09:00:00Z")

            write_revision_protocol(protocol_dir, revision_protocol, repo_dir, revision_id)

            query = {
                "vcsType": "git",
                "repoURL": str(repo_dir),
                "repoBranch": "main",
                "startTime": "2026-03-01",
                "endTime": "2026-03-31",
                "scope": scope,
            }
            run_cli(repo_dir, output_file, protocol_dir, query)
            result = load_json(output_file)
            return result["SUMMARY"]

    def test_scope_a_counts_only_code_lines_excluding_comments(self) -> None:
        summary = self._build_repo_and_run("A")
        self.assertEqual(summary, {
            "totalCodeLines": 2,
            "fullGeneratedCodeLines": 1,
            "partialGeneratedCodeLines": 0,
        })

    def test_scope_b_counts_code_and_comment_lines(self) -> None:
        summary = self._build_repo_and_run("B")
        self.assertEqual(summary, {
            "totalCodeLines": 4,
            "fullGeneratedCodeLines": 2,
            "partialGeneratedCodeLines": 1,
        })

    def test_scope_c_counts_only_doc_file_lines(self) -> None:
        summary = self._build_repo_and_run("C")
        self.assertEqual(summary, {
            "totalDocLines": 2,
            "fullGeneratedDocLines": 1,
            "partialGeneratedDocLines": 0,
        })

    def test_scope_d_counts_all_source_and_doc_lines(self) -> None:
        summary = self._build_repo_and_run("D")
        self.assertEqual(summary, {
            "totalCodeLines": 6,
            "fullGeneratedCodeLines": 3,
            "partialGeneratedCodeLines": 1,
        })

    def test_all_four_scopes_produce_valid_summaries_with_correct_field_names(self) -> None:
        """Cross-scope sanity: each scope produces a summary with the expected
        field name family, and scope C uses Doc fields while others use Code fields."""
        for scope in ("A", "B", "D"):
            summary = self._build_repo_and_run(scope)
            self.assertIn("totalCodeLines", summary, f"Scope {scope} missing totalCodeLines")
            self.assertNotIn("totalDocLines", summary, f"Scope {scope} should not have totalDocLines")

        summary_c = self._build_repo_and_run("C")
        self.assertIn("totalDocLines", summary_c, "Scope C missing totalDocLines")
        self.assertNotIn("totalCodeLines", summary_c, "Scope C should not have totalCodeLines")


if __name__ == "__main__":
    unittest.main()
