import unittest
import tempfile
from pathlib import Path

from tests.cli_test_support import GitRepoHarness, UTILITY_PATH, load_json, run_cli, write_revision_protocol


FIXTURE_DIR = Path(__file__).resolve().parent.parent / "testdata" / "us20_scope_b_source_with_comments"


class TestUs20ScopeBSourceWithCommentsTdd(unittest.TestCase):
    maxDiff = None

    def test_scope_b_counts_comment_lines_alongside_code_lines(self) -> None:
        """Scope B includes both code and comment lines in totalCodeLines.

        Unlike Scope A which filters out comment lines, Scope B treats every
        non-blank source line — including comments — as a countable line.
        Lines with genRatio > 0 in the protocol are attributed to AI.
        """
        self.assertTrue(
            UTILITY_PATH.exists(),
            f"Expected CLI utility at {UTILITY_PATH} for US-20 end-to-end execution.",
        )

        query = load_json(FIXTURE_DIR / "query.json")
        expected_result = load_json(FIXTURE_DIR / "expected_result.json")
        revision_protocol = load_json(FIXTURE_DIR / "01_genCodeDesc.json")

        with tempfile.TemporaryDirectory() as temp_dir:
            root_dir = Path(temp_dir)
            repo_dir = root_dir / "repo"
            protocol_dir = root_dir / "protocols"
            output_file = root_dir / "out.json"

            repo_dir.mkdir()
            protocol_dir.mkdir()

            # WHY: File content has 6 non-blank lines: 2 comments + 4 code.
            # Scope A would count only the 4 code lines.
            # Scope B counts all 6 non-blank lines.
            repo = GitRepoHarness(repo_dir)
            repo.write(
                "src/calc.py",
                "# AI-generated helper function\n"
                "def calc(x):\n"
                "    # compute the boosted value\n"
                "    value = x + 1\n"
                "    boosted = value * 2\n"
                "    return boosted\n",
            )
            revision_id = repo.commit_all("us20-r1", "2026-03-10T09:00:00Z")

            write_revision_protocol(protocol_dir, revision_protocol, repo_dir, revision_id)

            run_cli(repo_dir, output_file, protocol_dir, query)

            actual_result = load_json(output_file)
            expected_result["REPOSITORY"]["repoURL"] = str(repo_dir)
            expected_result["REPOSITORY"]["revisionId"] = revision_id

            self.assertEqual(actual_result, expected_result)


if __name__ == "__main__":
    unittest.main()
