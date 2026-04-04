"""US-18: Merge-aware Git period contribution inside one requested window.

Scenario:
  r0 (before window): human creates src/base.py with 2 code lines
  r1 (in window, main): AI adds 1 line on main
  r2 (in window, feature): AI adds 1 line on feature branch
  r3 (in window, main): merge feature→main (no-ff merge commit)

Expected: Both AI lines survive the merge and count for period-added.
  totalCodeLines = 2, fullGeneratedCodeLines = 2
"""

import tempfile
import unittest
from pathlib import Path

from aggregateGenCodeDesc import PROTOCOL_VERSION
from tests.cli_test_support import GitRepoHarness, load_json, run_cli, write_revision_protocol


class TestUS18PeriodAddedMergeAware(unittest.TestCase):

    def _build_repo(self, root_dir: Path):
        repo_dir = root_dir / "repo"
        protocol_dir = root_dir / "protocols"
        repo_dir.mkdir()
        protocol_dir.mkdir()

        repo = GitRepoHarness(repo_dir)

        # r0: human baseline (before window)
        repo.write(
            "src/base.py",
            "def base():\n"
            "    return 0\n",
        )
        _r0 = repo.commit_all("human-base", "2026-02-20T09:00:00Z")

        # r1: AI adds line on main (in window)
        repo.write(
            "src/base.py",
            "def base():\n"
            "    x = ai_init()\n"
            "    return 0\n",
        )
        r1 = repo.commit_all("ai-on-main", "2026-03-05T09:00:00Z")

        # Create feature branch from r0
        repo.checkout_new_branch("feature")
        # Reset feature to r0 state
        repo._run(["git", "reset", "--hard", "HEAD~1"])
        repo.write(
            "src/base.py",
            "def base():\n"
            "    return 0\n"
            "    y = ai_enhance()\n",
        )
        r2 = repo.commit_all("ai-on-feature", "2026-03-08T09:00:00Z")

        # Back to main and merge
        repo.checkout("main")
        r3 = repo.merge_with_manual_resolution(
            "feature",
            "merge-feature",
            "2026-03-15T09:00:00Z",
            resolved_files={
                "src/base.py": (
                    "def base():\n"
                    "    x = ai_init()\n"
                    "    return 0\n"
                    "    y = ai_enhance()\n"
                ),
            },
        )

        # Protocol for r1: line 2 is AI
        write_revision_protocol(
            protocol_dir,
            {
                "protocolName": "generatedTextDesc",
                "protocolVersion": PROTOCOL_VERSION,
                "SUMMARY": {"totalCodeLines": 1, "fullGeneratedCodeLines": 1, "partialGeneratedCodeLines": 0},
                "REPOSITORY": {"vcsType": "git", "repoURL": "", "repoBranch": "main", "revisionId": ""},
                "DETAIL": [
                    {
                        "fileName": "src/base.py",
                        "codeLines": [{"lineLocation": 2, "genRatio": 100}],
                    }
                ],
            },
            repo_dir,
            r1,
        )

        # Protocol for r2: line 3 is AI
        write_revision_protocol(
            protocol_dir,
            {
                "protocolName": "generatedTextDesc",
                "protocolVersion": PROTOCOL_VERSION,
                "SUMMARY": {"totalCodeLines": 1, "fullGeneratedCodeLines": 1, "partialGeneratedCodeLines": 0},
                "REPOSITORY": {"vcsType": "git", "repoURL": "", "repoBranch": "main", "revisionId": ""},
                "DETAIL": [
                    {
                        "fileName": "src/base.py",
                        "codeLines": [{"lineLocation": 3, "genRatio": 100}],
                    }
                ],
            },
            repo_dir,
            r2,
        )

        # Protocol for merge commit r3: both AI lines present
        write_revision_protocol(
            protocol_dir,
            {
                "protocolName": "generatedTextDesc",
                "protocolVersion": PROTOCOL_VERSION,
                "SUMMARY": {"totalCodeLines": 2, "fullGeneratedCodeLines": 2, "partialGeneratedCodeLines": 0},
                "REPOSITORY": {"vcsType": "git", "repoURL": "", "repoBranch": "main", "revisionId": ""},
                "DETAIL": [
                    {
                        "fileName": "src/base.py",
                        "codeLines": [
                            {"lineLocation": 2, "genRatio": 100},
                            {"lineLocation": 4, "genRatio": 100},
                        ],
                    }
                ],
            },
            repo_dir,
            r3,
        )

        query = {
            "vcsType": "git",
            "repoURL": str(repo_dir),
            "repoBranch": "main",
            "scope": "A",
            "startTime": "2026-03-01",
            "endTime": "2026-03-31",
        }
        return repo, protocol_dir, query, r1, r2, r3

    def test_period_added_merge_counts_both_branch_contributions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo, protocol_dir, query, _r1, _r2, r3 = self._build_repo(Path(temp_dir))
            output_file = Path(temp_dir) / "out.json"

            result = run_cli(
                repo.repo_dir,
                output_file,
                protocol_dir,
                query,
                extra_args=["--algorithm", "B", "--metric", "period_added_ai_ratio"],
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            actual = load_json(output_file)

        # Both AI lines (from main and feature) survive the merge
        self.assertEqual(
            actual["SUMMARY"],
            {
                "totalCodeLines": 2,
                "fullGeneratedCodeLines": 2,
                "partialGeneratedCodeLines": 0,
            },
        )
        self.assertEqual(actual["REPOSITORY"]["revisionId"], r3)


if __name__ == "__main__":
    unittest.main()
