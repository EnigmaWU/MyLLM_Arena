import unittest
from pathlib import Path

from aggregateGenCodeDesc import CommitDiffSetDirProvider, LineState, RuntimeLogger, apply_commit_diff_file_to_line_states, load_commit_diff_sequence
from tests.cli_test_support import load_json


SCENARIO_DIR = Path(__file__).resolve().parent.parent / "testdata" / "us6_period_added_ratio"
COMMIT_DIFF_DIR = SCENARIO_DIR / "commitDiffSet"


class TestCommitDiffLineStateTdd(unittest.TestCase):
    def test_line_state_replay_preserves_origin_revision_for_added_lines(self) -> None:
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
            LineState(content="def build_report(data):", origin_revision_id=None),
            LineState(content="    report = []", origin_revision_id=None),
        ]

        for revision_diff in sequence:
            current_lines = apply_commit_diff_file_to_line_states(
                current_lines,
                revision_diff.parsed_patch.files[0],
                revision_diff.revision_id,
            )

        self.assertEqual([line.content for line in current_lines], [
            "def build_report(data):",
            "    report = []",
            "    draft = summarize(data)",
            "    publish(draft)",
            "    status = \"done\"",
            "    notify(status)",
            "    return publish_result",
        ])
        self.assertEqual(
            [line.origin_revision_id for line in current_lines],
            [None, None, "us6-r2", "us6-r2", "us6-r3", "us6-r3", "us6-r3"],
        )

    def test_line_state_replay_keeps_existing_origin_through_context_lines(self) -> None:
        query = load_json(SCENARIO_DIR / "query.json")
        provider = CommitDiffSetDirProvider(COMMIT_DIFF_DIR, RuntimeLogger("quiet"))
        sequence = load_commit_diff_sequence(
            provider,
            query["repoURL"],
            query["repoBranch"],
            ["us6-r2"],
            query["vcsType"],
        )

        current_lines = [
            LineState(content="def build_report(data):", origin_revision_id="us6-r1"),
            LineState(content="    report = []", origin_revision_id="us6-r1"),
        ]

        current_lines = apply_commit_diff_file_to_line_states(
            current_lines,
            sequence[0].parsed_patch.files[0],
            sequence[0].revision_id,
        )

        self.assertEqual(
            [line.origin_revision_id for line in current_lines],
            ["us6-r1", "us6-r1", "us6-r2", "us6-r2"],
        )


if __name__ == "__main__":
    unittest.main()
