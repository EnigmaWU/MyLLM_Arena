import unittest
import tempfile
from pathlib import Path

from tests.cli_test_support import GitRepoHarness, load_json, run_cli, write_revision_protocol


class TestUs24AlgorithmBScopeB(unittest.TestCase):
    """US-24: Algorithm B + Scope B must count all non-blank source lines including comments."""

    def test_algorithm_b_scope_b_counts_comments_via_live_changed(self) -> None:
        """Given a source file with code and comments,
        when Algorithm B (live_changed_source_ratio) runs with --scope B,
        then totalCodeLines includes all non-blank lines (code + comments)."""

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo_dir = root / "repo"
            protocol_dir = root / "protocols"
            output_file = root / "out.json"
            repo_dir.mkdir()
            protocol_dir.mkdir()

            repo = GitRepoHarness(repo_dir)

            # 5 non-blank lines: 2 comments + 3 code
            file_content = (
                "# Initialize module\n"
                "# Author: test\n"
                "value = 1\n"
                "result = value + 1\n"
                "output = result\n"
            )
            repo.write("src/calc.py", file_content)
            revision_id = repo.commit_all("r1", "2026-03-15T09:00:00Z")

            # Protocol: codeLines covers all 5 non-blank lines (scope B style)
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
                            {"lineLocation": 4, "genRatio": 100, "genMethod": "vibeCoding"},
                            {"lineLocation": 5, "genRatio": 100, "genMethod": "vibeCoding"},
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
                "scope": "B",
            }

            run_cli(
                repo_dir,
                output_file,
                protocol_dir,
                query,
                extra_args=["--algorithm", "B"],
            )

            result = load_json(output_file)
            # Scope B: all 5 non-blank lines counted (2 comments + 3 code)
            self.assertEqual(result["SUMMARY"]["totalCodeLines"], 5)
            self.assertEqual(result["SUMMARY"]["fullGeneratedCodeLines"], 5)
            self.assertEqual(result["SUMMARY"]["partialGeneratedCodeLines"], 0)
