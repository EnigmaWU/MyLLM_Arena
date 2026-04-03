import unittest
import tempfile
from pathlib import Path

from tests.cli_test_support import GitRepoHarness, UTILITY_PATH, load_json, run_cli, write_revision_protocol


FIXTURE_DIR = Path(__file__).resolve().parent.parent / "testdata" / "us22_scope_d_all_text"


class TestUs22ScopeDAllTextTdd(unittest.TestCase):
    maxDiff = None

    def test_scope_d_counts_all_non_blank_lines_from_source_and_doc_files(self) -> None:
        """Scope D is the union of source files and documentation files.

        All non-blank lines from both file types count. Attribution uses
        codeLines for source files and docLines for doc files. Output uses
        the totalCodeLines field family as the combined summary shape.
        """
        self.assertTrue(
            UTILITY_PATH.exists(),
            f"Expected CLI utility at {UTILITY_PATH} for US-22 end-to-end execution.",
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

            # WHY: source file has 3 non-blank lines, doc file has 2.
            # Scope D unifies both → 5 total non-blank lines.
            repo = GitRepoHarness(repo_dir)
            repo.write(
                "src/calc.py",
                "def calc(x):\n"
                "    value = x + 1\n"
                "    return value\n",
            )
            repo.write(
                "docs/spec.md",
                "# Specification\n"
                "The calc function adds one.\n",
            )
            revision_id = repo.commit_all("us22-r1", "2026-03-10T09:00:00Z")

            write_revision_protocol(protocol_dir, revision_protocol, repo_dir, revision_id)

            run_cli(repo_dir, output_file, protocol_dir, query)

            actual_result = load_json(output_file)
            expected_result["REPOSITORY"]["repoURL"] = str(repo_dir)
            expected_result["REPOSITORY"]["revisionId"] = revision_id

            self.assertEqual(actual_result, expected_result)


if __name__ == "__main__":
    unittest.main()
