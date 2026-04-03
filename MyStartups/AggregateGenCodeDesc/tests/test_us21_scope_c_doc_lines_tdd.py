import unittest
import tempfile
from pathlib import Path

from tests.cli_test_support import GitRepoHarness, UTILITY_PATH, load_json, run_cli, write_revision_protocol


FIXTURE_DIR = Path(__file__).resolve().parent.parent / "testdata" / "us21_scope_c_doc_lines"


class TestUs21ScopeCDocLinesTdd(unittest.TestCase):
    maxDiff = None

    def test_scope_c_counts_doc_file_lines_using_doc_lines_protocol(self) -> None:
        """Scope C targets documentation files (like .md) and uses docLines
        from the genCodeDesc protocol to determine AI attribution.

        - File listing includes doc extensions instead of source extensions.
        - All non-blank lines count.
        - Output uses totalDocLines / fullGeneratedDocLines / partialGeneratedDocLines.
        """
        self.assertTrue(
            UTILITY_PATH.exists(),
            f"Expected CLI utility at {UTILITY_PATH} for US-21 end-to-end execution.",
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

            # WHY: File content has 4 non-blank lines.
            # L1: heading (genRatio 100)
            # L2: AI-generated paragraph (genRatio 100)
            # L3: human-edited section header (genRatio 50)
            # L4: human paragraph (genRatio 0, not in docLines)
            repo = GitRepoHarness(repo_dir)
            repo.write(
                "docs/design.md",
                "# Design Document\n"
                "This specification was entirely generated.\n"
                "## Overview\n"
                "The system computes metrics.\n",
            )
            revision_id = repo.commit_all("us21-r1", "2026-03-10T09:00:00Z")

            write_revision_protocol(protocol_dir, revision_protocol, repo_dir, revision_id)

            run_cli(repo_dir, output_file, protocol_dir, query)

            actual_result = load_json(output_file)
            expected_result["REPOSITORY"]["repoURL"] = str(repo_dir)
            expected_result["REPOSITORY"]["revisionId"] = revision_id

            self.assertEqual(actual_result, expected_result)


if __name__ == "__main__":
    unittest.main()
