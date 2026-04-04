"""US-16: Period-added with deletions, resets, and mixed rewrites inside one window.

Scenarios exercised:
  1. Deleted-in-window: a line added by r1 then deleted by r2 — should NOT count
  2. AI→human rewrite: a pre-window human line rewritten to AI in r1, then rewritten
     back to human in r2 — origin becomes r2, counted as human
  3. Human→AI rewrite: a pre-window human line rewritten by AI in r1 — origin becomes
     r1, counted as AI
  4. Surviving additions: lines added in-window that survive to final state

Commit history:
  r0 (before window): src/report.py with 4 code lines (all human)
  r1 (in window): AI rewrites line 2, AI adds line 5
  r2 (in window): human rewrites line 2 back, deletes line 5, adds line 5 (new human)
"""

import tempfile
import unittest
from pathlib import Path

from aggregateGenCodeDesc import PROTOCOL_VERSION
from tests.cli_test_support import GitRepoHarness, load_json, run_cli, write_revision_protocol


class TestUS16PeriodAddedDeletionsAndRewrites(unittest.TestCase):

    def _build_repo(self, root_dir: Path):
        repo_dir = root_dir / "repo"
        protocol_dir = root_dir / "protocols"
        repo_dir.mkdir()
        protocol_dir.mkdir()

        repo = GitRepoHarness(repo_dir)

        # r0: 4 human code lines (before window)
        repo.write(
            "src/report.py",
            "def report(data):\n"
            "    result = process(data)\n"
            "    output = format(result)\n"
            "    return output\n",
        )
        _r0 = repo.commit_all("human-base", "2026-02-20T09:00:00Z")

        # r1: AI rewrites line 2, adds line 4 (AI)
        repo.write(
            "src/report.py",
            "def report(data):\n"
            "    result = ai_process(data)\n"
            "    output = format(result)\n"
            "    ai_extra = enhance(output)\n"
            "    return output\n",
        )
        r1 = repo.commit_all("ai-rewrite-and-add", "2026-03-10T09:00:00Z")

        # r2: human rewrites line 2 back, removes AI extra, adds a human line
        repo.write(
            "src/report.py",
            "def report(data):\n"
            "    result = manual_process(data)\n"
            "    output = format(result)\n"
            "    checked = validate(output)\n"
            "    return output\n",
        )
        r2 = repo.commit_all("human-rewrite-and-fix", "2026-03-20T09:00:00Z")

        # Protocol for r1: line 2 AI rewrite + line 4 AI addition
        write_revision_protocol(
            protocol_dir,
            {
                "protocolName": "generatedTextDesc",
                "protocolVersion": PROTOCOL_VERSION,
                "SUMMARY": {"totalCodeLines": 2, "fullGeneratedCodeLines": 2, "partialGeneratedCodeLines": 0},
                "REPOSITORY": {"vcsType": "git", "repoURL": "", "repoBranch": "main", "revisionId": ""},
                "DETAIL": [
                    {
                        "fileName": "src/report.py",
                        "codeLines": [
                            {"lineLocation": 2, "genRatio": 100},
                            {"lineLocation": 4, "genRatio": 100},
                        ],
                    }
                ],
            },
            repo_dir,
            r1,
        )

        # Protocol for r2: no AI-generated lines
        write_revision_protocol(
            protocol_dir,
            {
                "protocolName": "generatedTextDesc",
                "protocolVersion": PROTOCOL_VERSION,
                "SUMMARY": {"totalCodeLines": 0, "fullGeneratedCodeLines": 0, "partialGeneratedCodeLines": 0},
                "REPOSITORY": {"vcsType": "git", "repoURL": "", "repoBranch": "main", "revisionId": ""},
                "DETAIL": [{"fileName": "src/report.py", "codeLines": []}],
            },
            repo_dir,
            r2,
        )

        query = {
            "vcsType": "git",
            "repoURL": str(repo_dir),
            "repoBranch": "main",
            "scope": "A",
            "startTime": "2026-03-01",
            "endTime": "2026-03-31",
        }
        return repo, protocol_dir, query, r1, r2

    def test_deleted_ai_line_not_counted(self) -> None:
        """AI line added in r1 and deleted/replaced in r2 should not appear."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo, protocol_dir, query, _r1, r2 = self._build_repo(Path(temp_dir))
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

        # r1 added "ai_process" (AI) + "ai_extra" (AI) — 2 AI lines
        # r2 replaced "ai_process" → "manual_process" (human) and "ai_extra" → "checked" (human)
        # So the surviving in-window lines are:
        #   line 2 "manual_process" (from r2, human) and line 4 "checked" (from r2, human)
        # Pre-window lines (def, output=, return) are excluded from count
        self.assertEqual(actual["SUMMARY"]["totalCodeLines"], 2)
        self.assertEqual(actual["SUMMARY"]["fullGeneratedCodeLines"], 0)
        self.assertEqual(actual["SUMMARY"]["partialGeneratedCodeLines"], 0)
        self.assertEqual(actual["REPOSITORY"]["revisionId"], r2)

    def test_rewritten_line_origin_shifts_to_rewriting_commit(self) -> None:
        """A pre-window line rewritten in-window should be counted as in-window."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo, protocol_dir, query, _r1, _r2 = self._build_repo(Path(temp_dir))
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

        # totalCodeLines = 2 means 2 lines have in-window origin
        # (line 2 rewritten by r2, line 4 added by r2)
        self.assertEqual(actual["SUMMARY"]["totalCodeLines"], 2)


if __name__ == "__main__":
    unittest.main()
