import unittest
from pathlib import Path

from aggregateGenCodeDesc import (
    GenCodeDescSetDirProvider,
    CommitDiffSetDirProvider,
    LineState,
    RuntimeLogger,
    apply_commit_diff_file_to_line_states,
    build_protocol_index,
    load_commit_diff_sequence,
    summarize_period_added_line_states,
)
from tests.cli_test_support import load_json


SCENARIO_DIR = Path(__file__).resolve().parent.parent / "testdata" / "us6_period_added_ratio"
COMMIT_DIFF_DIR = SCENARIO_DIR / "commitDiffSet"


class TestCommitDiffLineAttributionTdd(unittest.TestCase):
    def test_replay_assigns_gen_ratios_from_revision_metadata(self) -> None:
        query = load_json(SCENARIO_DIR / "query.json")
        metadata_provider = GenCodeDescSetDirProvider(SCENARIO_DIR, False, RuntimeLogger("quiet"))
        diff_provider = CommitDiffSetDirProvider(COMMIT_DIFF_DIR, RuntimeLogger("quiet"))
        sequence = load_commit_diff_sequence(
            diff_provider,
            query["repoURL"],
            query["repoBranch"],
            query["includedRevisionIds"],
            query["vcsType"],
        )
        protocol_indexes = {
            revision_id: build_protocol_index(
                metadata_provider.get_revision_metadata(query["repoURL"], query["repoBranch"], revision_id, query["vcsType"])
            )
            for revision_id in query["includedRevisionIds"]
        }

        current_lines = [
            LineState(content="def build_report(data):", origin_revision_id="us6-r1", gen_ratio=0),
            LineState(content="    report = []", origin_revision_id="us6-r1", gen_ratio=0),
        ]

        for revision_diff in sequence:
            current_lines = apply_commit_diff_file_to_line_states(
                current_lines,
                revision_diff.parsed_patch.files[0],
                revision_diff.revision_id,
                protocol_indexes[revision_diff.revision_id],
            )

        self.assertEqual(
            [line.gen_ratio for line in current_lines],
            [0, 0, 100, 100, 0, 0, 100],
        )

    def test_us6_period_added_summary_matches_expected_result(self) -> None:
        query = load_json(SCENARIO_DIR / "query.json")
        expected_result = load_json(SCENARIO_DIR / "expected_result.json")
        metadata_provider = GenCodeDescSetDirProvider(SCENARIO_DIR, False, RuntimeLogger("quiet"))
        diff_provider = CommitDiffSetDirProvider(COMMIT_DIFF_DIR, RuntimeLogger("quiet"))
        sequence = load_commit_diff_sequence(
            diff_provider,
            query["repoURL"],
            query["repoBranch"],
            query["includedRevisionIds"],
            query["vcsType"],
        )
        protocol_indexes = {
            revision_id: build_protocol_index(
                metadata_provider.get_revision_metadata(query["repoURL"], query["repoBranch"], revision_id, query["vcsType"])
            )
            for revision_id in query["includedRevisionIds"]
        }

        current_lines = [
            LineState(content="def build_report(data):", origin_revision_id="us6-r1", gen_ratio=0),
            LineState(content="    report = []", origin_revision_id="us6-r1", gen_ratio=0),
        ]
        for revision_diff in sequence:
            current_lines = apply_commit_diff_file_to_line_states(
                current_lines,
                revision_diff.parsed_patch.files[0],
                revision_diff.revision_id,
                protocol_indexes[revision_diff.revision_id],
            )

        summary = summarize_period_added_line_states(current_lines, query["includedRevisionIds"])

        self.assertEqual(summary, expected_result["SUMMARY"])


if __name__ == "__main__":
    unittest.main()
