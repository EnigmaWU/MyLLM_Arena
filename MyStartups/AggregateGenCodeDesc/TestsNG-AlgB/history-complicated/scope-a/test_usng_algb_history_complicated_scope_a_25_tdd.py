import tempfile
import unittest
from pathlib import Path

from tests.cli_test_support import GitRepoHarness, load_json, run_cli, write_revision_protocol


class TestUsngAlgbHistoryComplicatedScopeA25Tdd(unittest.TestCase):
    """USNG-ALGB-HISTORY-COMPLICATED-SCOPE-A-25: Merge-Aware Git Period Contribution Inside One Window"""

    def test_both_main_and_feature_branch_contributions_counted(self) -> None:
        """GIVEN AI lines are added on main and on a feature branch and then merged during the window,
        WHEN Algorithm B computes the period-added result,
        THEN both contributions survive and count correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo_dir = root / "repo"
            protocol_dir = root / "protocols"
            output_file = root / "out.json"
            repo_dir.mkdir()
            protocol_dir.mkdir()

            repo = GitRepoHarness(repo_dir)

            # Base commit — initial empty file
            repo.write("src/shared.py", "class Base:\n    pass\n")
            repo.commit_all("base", "2026-02-01T09:00:00Z")

            # In-window: main branch commit — adds AI line
            repo.write("src/shared.py", "class Base:\n    pass\ndef main_ai():\n    return ai_main()\n")
            r_main = repo.commit_all("main-ai", "2026-03-05T09:00:00Z")

            # Feature branch from base (checkout from before main_ai)
            repo.checkout_new_branch("feature")
            repo.write("src/feature.py", "def feature_ai():\n    return ai_feat()\n")
            r_feat = repo.commit_all("feature-ai", "2026-03-10T09:00:00Z")

            # Merge feature into main
            repo.checkout("main")
            r_merge = repo.merge_no_ff("feature", "merge-feature", "2026-03-20T09:00:00Z")

            for rev_id, lines_data in [
                (r_main, [{"lineLocation": 3, "genRatio": 0, "genMethod": "Manual"}, {"lineLocation": 4, "genRatio": 100, "genMethod": "codeCompletion"}]),
                (r_feat, [{"lineLocation": 1, "genRatio": 0, "genMethod": "Manual"}, {"lineLocation": 2, "genRatio": 100, "genMethod": "vibeCoding"}]),
            ]:
                protocol = {
                    "protocolName": "generatedTextDesc",
                    "protocolVersion": "26.03",
                    "codeAgent": "TestAgent",
                    "SUMMARY": {"totalCodeLines": 2, "fullGeneratedCodeLines": 1, "partialGeneratedCodeLines": 0},
                    "REPOSITORY": {"repoURL": str(repo_dir), "repoBranch": "main", "revisionId": rev_id},
                    "DETAIL": [{"fileName": "src/shared.py" if rev_id == r_main else "src/feature.py", "codeLines": lines_data}],
                }
                write_revision_protocol(protocol_dir, protocol, repo_dir, rev_id)

            query = {
                "vcsType": "git",
                "repoURL": str(repo_dir),
                "repoBranch": "main",
                "startTime": "2026-03-01",
                "endTime": "2026-03-31",
                "scope": "A",
                "metric": "period_added_ai_ratio",
            }

            run_cli(repo_dir, output_file, protocol_dir, query, extra_args=["--algorithm", "B"])

            result = load_json(output_file)
            summary = result["SUMMARY"]
            # Both main contribution (1 AI + 1 human) and feature contribution (1 AI + 1 human) counted
            self.assertGreaterEqual(summary["totalCodeLines"], 4)
            self.assertGreaterEqual(summary["fullGeneratedCodeLines"], 2)


if __name__ == "__main__":
    unittest.main()
