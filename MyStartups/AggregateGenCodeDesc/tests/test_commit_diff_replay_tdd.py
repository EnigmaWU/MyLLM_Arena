import unittest
from pathlib import Path

from aggregateGenCodeDesc import ProtocolValidationError, apply_commit_diff_file_to_lines, load_commit_diff_sequence, CommitDiffSetDirProvider, RuntimeLogger
from tests.cli_test_support import load_json


SCENARIO_DIR = Path(__file__).resolve().parent.parent / "testdata" / "us6_period_added_ratio"
COMMIT_DIFF_DIR = SCENARIO_DIR / "commitDiffSet"


class TestCommitDiffReplayTdd(unittest.TestCase):
    def test_replay_applies_us6_sequence_to_base_file_lines(self) -> None:
        query = load_json(SCENARIO_DIR / "query.json")
        provider = CommitDiffSetDirProvider(COMMIT_DIFF_DIR, RuntimeLogger("quiet"))
        sequence = load_commit_diff_sequence(
            provider,
            query["repoURL"],
            query["repoBranch"],
            query["includedRevisionIds"],
            query["vcsType"],
        )

        current_lines = [
            "def build_report(data):",
            "    report = []",
        ]

        for revision_diff in sequence:
            current_lines = apply_commit_diff_file_to_lines(current_lines, revision_diff.parsed_patch.files[0])

        self.assertEqual(
            current_lines,
            [
                "def build_report(data):",
                "    report = []",
                "    draft = summarize(data)",
                "    publish(draft)",
                "    status = \"done\"",
                "    notify(status)",
                "    return publish_result",
            ],
        )

    def test_replay_fails_when_patch_context_does_not_match_current_lines(self) -> None:
        query = load_json(SCENARIO_DIR / "query.json")
        provider = CommitDiffSetDirProvider(COMMIT_DIFF_DIR, RuntimeLogger("quiet"))
        sequence = load_commit_diff_sequence(
            provider,
            query["repoURL"],
            query["repoBranch"],
            ["us6-r2"],
            query["vcsType"],
        )

        with self.assertRaises(ProtocolValidationError) as context:
            apply_commit_diff_file_to_lines([
                "def build_report(data):",
                "    wrong = []",
            ], sequence[0].parsed_patch.files[0])

        self.assertIn("Commit diff context mismatch", str(context.exception))


if __name__ == "__main__":
    unittest.main()
