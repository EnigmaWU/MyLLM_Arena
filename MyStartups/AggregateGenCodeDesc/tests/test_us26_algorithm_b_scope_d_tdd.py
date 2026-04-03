import unittest
import tempfile
from pathlib import Path

from tests.cli_test_support import GitRepoHarness, load_json, run_cli, write_revision_protocol


class TestUs26AlgorithmBScopeD(unittest.TestCase):
    """US-26: Algorithm B + Scope D must count all text lines from both source and doc files."""

    def test_algorithm_b_scope_d_counts_source_and_doc_lines_via_live_changed(self) -> None:
        """Given a repo with a source file and a doc file,
        when Algorithm B (live_changed_source_ratio) runs with --scope D,
        then totalCodeLines includes non-blank lines from both files."""

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo_dir = root / "repo"
            protocol_dir = root / "protocols"
            output_file = root / "out.json"
            repo_dir.mkdir()
            protocol_dir.mkdir()

            repo = GitRepoHarness(repo_dir)

            # Source file: 3 non-blank code lines
            source_content = (
                "value = 1\n"
                "result = value + 1\n"
                "output = result\n"
            )
            repo.write("src/calc.py", source_content)

            # Doc file: 2 non-blank lines
            doc_content = (
                "# Specification\n"
                "\n"
                "Calc produces output.\n"
            )
            repo.write("docs/spec.md", doc_content)
            revision_id = repo.commit_all("r1", "2026-03-15T09:00:00Z")

            # Protocol: codeLines for source, docLines for doc
            protocol = {
                "protocolName": "generatedTextDesc",
                "protocolVersion": "26.03",
                "codeAgent": "TestAgent",
                "SUMMARY": {"totalCodeLines": 5, "fullGeneratedCodeLines": 5, "partialGeneratedCodeLines": 0},
                "REPOSITORY": {"repoURL": str(repo_dir), "repoBranch": "main", "revisionId": revision_id},
                "DETAIL": [
                    {
                        "fileName": "src/calc.py",
                        "codeLines": [
                            {"lineLocation": 1, "genRatio": 100, "genMethod": "vibeCoding"},
                            {"lineLocation": 2, "genRatio": 100, "genMethod": "vibeCoding"},
                            {"lineLocation": 3, "genRatio": 100, "genMethod": "vibeCoding"},
                        ],
                    },
                    {
                        "fileName": "docs/spec.md",
                        "docLines": [
                            {"lineLocation": 1, "genRatio": 100, "genMethod": "vibeCoding"},
                            {"lineLocation": 3, "genRatio": 100, "genMethod": "vibeCoding"},
                        ],
                    },
                ],
            }
            write_revision_protocol(protocol_dir, protocol, repo_dir, revision_id)

            query = {
                "vcsType": "git",
                "repoURL": str(repo_dir),
                "repoBranch": "main",
                "startTime": "2026-03-01",
                "endTime": "2026-03-31",
                "scope": "D",
            }

            run_cli(
                repo_dir,
                output_file,
                protocol_dir,
                query,
                extra_args=["--algorithm", "B", "--metric", "live_changed_source_ratio"],
            )

            result = load_json(output_file)
            # Scope D: 3 source + 2 doc = 5 total, using CodeLines field names
            self.assertEqual(result["SUMMARY"]["totalCodeLines"], 5)
            self.assertEqual(result["SUMMARY"]["fullGeneratedCodeLines"], 5)
            self.assertEqual(result["SUMMARY"]["partialGeneratedCodeLines"], 0)
