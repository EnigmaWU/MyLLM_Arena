"""US-15: Single-branch period-added baseline without merges or renames.

Scenario:
  r0 (before window): human creates src/calc.py with 3 code lines
  r1 (in window):     AI adds 2 lines to src/calc.py
  r2 (in window):     human adds 1 line to src/calc.py

Period window: 2026-03-01 ~ 2026-03-31  (covers r1 + r2)

Expected SUMMARY (period-added only counts lines originated by in-window commits):
  totalCodeLines = 3  (2 from r1 + 1 from r2)
  fullGeneratedCodeLines = 2  (the 2 AI lines from r1)
  partialGeneratedCodeLines = 0
"""

import json
import tempfile
import unittest
from pathlib import Path

from aggregateGenCodeDesc import PROTOCOL_VERSION
from tests.cli_test_support import GitRepoHarness, load_json, run_cli, write_revision_protocol


class TestUS15PeriodAddedSingleBranchBaseline(unittest.TestCase):

    def _build_repo(self, root_dir: Path):
        repo_dir = root_dir / "repo"
        protocol_dir = root_dir / "protocols"
        repo_dir.mkdir()
        protocol_dir.mkdir()

        repo = GitRepoHarness(repo_dir)

        # r0: human baseline (before window)
        repo.write(
            "src/calc.py",
            "def calc(x):\n"
            "    value = x + 1\n"
            "    return value\n",
        )
        _r0 = repo.commit_all("human-base", "2026-02-20T09:00:00Z")

        # r1: AI adds 2 lines (in window)
        repo.write(
            "src/calc.py",
            "def calc(x):\n"
            "    value = x + 1\n"
            "    norm = normalize(x)\n"
            "    score = compute_score(norm)\n"
            "    return value\n",
        )
        r1 = repo.commit_all("ai-add", "2026-03-10T09:00:00Z")

        # r2: human adds 1 line (in window)
        repo.write(
            "src/calc.py",
            "def calc(x):\n"
            "    value = x + 1\n"
            "    norm = normalize(x)\n"
            "    score = compute_score(norm)\n"
            "    total = value + score\n"
            "    return value\n",
        )
        r2 = repo.commit_all("human-add", "2026-03-20T09:00:00Z")

        # Protocol for r1: lines 3 and 4 are AI-generated
        write_revision_protocol(
            protocol_dir,
            {
                "protocolName": "generatedTextDesc",
                "protocolVersion": PROTOCOL_VERSION,
                "SUMMARY": {"totalCodeLines": 2, "fullGeneratedCodeLines": 2, "partialGeneratedCodeLines": 0},
                "REPOSITORY": {"vcsType": "git", "repoURL": "", "repoBranch": "main", "revisionId": ""},
                "DETAIL": [
                    {
                        "fileName": "src/calc.py",
                        "codeLines": [
                            {"lineLocation": 3, "genRatio": 100},
                            {"lineLocation": 4, "genRatio": 100},
                        ],
                    }
                ],
            },
            repo_dir,
            r1,
        )

        # Protocol for r2: no AI-generated lines in this commit
        write_revision_protocol(
            protocol_dir,
            {
                "protocolName": "generatedTextDesc",
                "protocolVersion": PROTOCOL_VERSION,
                "SUMMARY": {"totalCodeLines": 0, "fullGeneratedCodeLines": 0, "partialGeneratedCodeLines": 0},
                "REPOSITORY": {"vcsType": "git", "repoURL": "", "repoBranch": "main", "revisionId": ""},
                "DETAIL": [{"fileName": "src/calc.py", "codeLines": []}],
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

    def test_period_added_counts_only_in_window_lines(self) -> None:
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

        self.assertEqual(
            actual["SUMMARY"],
            {
                "totalCodeLines": 3,
                "fullGeneratedCodeLines": 2,
                "partialGeneratedCodeLines": 0,
            },
        )
        self.assertEqual(actual["REPOSITORY"]["revisionId"], r2)

    def test_period_added_excludes_pre_window_lines(self) -> None:
        """Pre-window lines (def, value=, return) must NOT be counted even though they survive."""
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

        # 6 total lines in file, but only 3 originated in the window
        self.assertEqual(actual["SUMMARY"]["totalCodeLines"], 3)

    def test_period_added_scope_b_counts_all_source_lines(self) -> None:
        """Scope B includes comments. Here all lines are pure code so result is same as Scope A."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo, protocol_dir, query, _r1, r2 = self._build_repo(Path(temp_dir))
            query["scope"] = "B"
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

        self.assertEqual(actual["SUMMARY"]["totalCodeLines"], 3)
        self.assertEqual(actual["SUMMARY"]["fullGeneratedCodeLines"], 2)


if __name__ == "__main__":
    unittest.main()
