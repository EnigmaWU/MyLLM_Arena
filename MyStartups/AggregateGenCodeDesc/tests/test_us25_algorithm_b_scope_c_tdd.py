import unittest
import tempfile
from pathlib import Path

from tests.cli_test_support import GitRepoHarness, load_json, run_cli, write_revision_protocol


class TestUs25AlgorithmBScopeC(unittest.TestCase):
    """US-25: Algorithm B + Scope C must count documentation file lines using docLines protocol field."""

    def test_algorithm_b_scope_c_counts_doc_lines_via_live_changed(self) -> None:
        """Given a documentation file (.md) with non-blank lines,
        when Algorithm B (live_changed_source_ratio) runs with --scope C,
        then totalDocLines includes all non-blank doc lines."""

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo_dir = root / "repo"
            protocol_dir = root / "protocols"
            output_file = root / "out.json"
            repo_dir.mkdir()
            protocol_dir.mkdir()

            repo = GitRepoHarness(repo_dir)

            # 3 non-blank lines in a documentation file
            file_content = (
                "# Design Overview\n"
                "\n"
                "The system processes events.\n"
                "Each event has a timestamp.\n"
            )
            repo.write("docs/design.md", file_content)
            revision_id = repo.commit_all("r1", "2026-03-15T09:00:00Z")

            # Protocol: docLines covers the 3 non-blank lines
            protocol = {
                "protocolName": "generatedTextDesc",
                "protocolVersion": "26.03",
                "codeAgent": "TestAgent",
                "SUMMARY": {"totalDocLines": 3, "fullGeneratedDocLines": 3, "partialGeneratedDocLines": 0},
                "REPOSITORY": {"repoURL": str(repo_dir), "repoBranch": "main", "revisionId": revision_id},
                "DETAIL": [
                    {
                        "fileName": "docs/design.md",
                        "docLines": [
                            {"lineLocation": 1, "genRatio": 100, "genMethod": "vibeCoding"},
                            {"lineLocation": 3, "genRatio": 100, "genMethod": "vibeCoding"},
                            {"lineLocation": 4, "genRatio": 100, "genMethod": "vibeCoding"},
                        ],
                    }
                ],
            }
            write_revision_protocol(protocol_dir, protocol, repo_dir, revision_id)

            query = {
                "vcsType": "git",
                "repoURL": str(repo_dir),
                "repoBranch": "main",
                "startTime": "2026-03-01",
                "endTime": "2026-03-31",
                "scope": "C",
            }

            run_cli(
                repo_dir,
                output_file,
                protocol_dir,
                query,
                extra_args=["--algorithm", "B", "--metric", "live_changed_source_ratio"],
            )

            result = load_json(output_file)
            # Scope C: Doc field names, 3 non-blank doc lines
            self.assertEqual(result["SUMMARY"]["totalDocLines"], 3)
            self.assertEqual(result["SUMMARY"]["fullGeneratedDocLines"], 3)
            self.assertEqual(result["SUMMARY"]["partialGeneratedDocLines"], 0)
