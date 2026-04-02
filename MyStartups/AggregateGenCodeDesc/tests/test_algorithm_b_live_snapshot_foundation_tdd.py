import unittest
from datetime import datetime, timezone
from pathlib import Path

from aggregateGenCodeDesc import (
    CommitDiffSetDirProvider,
    GenCodeDescSetDirProvider,
    LineState,
    ProtocolValidationError,
    RuntimeLogger,
    build_protocol_index,
    load_commit_diff_sequence,
    reconstruct_final_line_states_from_commit_diff_sequence,
    summarize_live_changed_line_states_by_revision_ids,
    summarize_live_snapshot_line_states,
)
from tests.cli_test_support import load_json


SCENARIO_DIR = Path(__file__).resolve().parent.parent / "testdata" / "us6_period_added_ratio"
COMMIT_DIFF_DIR = SCENARIO_DIR / "commitDiffSet"
US7_SCENARIO_DIR = Path(__file__).resolve().parent.parent / "testdata" / "us7_mixed_multi_commit_window"
US12_SCENARIO_DIR = Path(__file__).resolve().parent.parent / "testdata" / "us12_many_merged_branches_preserve_attribution"


class TestAlgorithmBLiveSnapshotFoundationTdd(unittest.TestCase):
    def test_reconstruct_final_line_states_replays_us6_sequence(self) -> None:
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

        target_file, final_line_states = reconstruct_final_line_states_from_commit_diff_sequence(
            sequence,
            protocol_indexes,
        )

        self.assertEqual(target_file, "src/report.py")
        self.assertEqual(
            [line.content for line in final_line_states],
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
        self.assertEqual(
            [line.origin_revision_id for line in final_line_states],
            [None, None, "us6-r2", "us6-r2", "us6-r3", "us6-r3", "us6-r3"],
        )
        self.assertEqual(
            [line.gen_ratio for line in final_line_states],
            [0, 0, 100, 100, 0, 0, 100],
        )

    def test_summarize_live_snapshot_line_states_filters_by_origin_commit_time(self) -> None:
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
        _, final_line_states = reconstruct_final_line_states_from_commit_diff_sequence(
            sequence,
            protocol_indexes,
        )

        summary = summarize_live_snapshot_line_states(
            final_line_states,
            revision_commit_times={
                "us6-r2": datetime(2026, 3, 11, 9, 0, tzinfo=timezone.utc),
                "us6-r3": datetime(2026, 3, 15, 11, 30, tzinfo=timezone.utc),
            },
            start_bound=datetime(2026, 3, 10, 0, 0, tzinfo=timezone.utc),
            end_bound=datetime(2026, 3, 31, 23, 59, 59, tzinfo=timezone.utc),
        )

        self.assertEqual(
            summary,
            {
                "totalCodeLines": 5,
                "fullGeneratedCodeLines": 3,
                "partialGeneratedCodeLines": 0,
            },
        )

    def test_summarize_live_snapshot_line_states_requires_commit_time_for_replayed_revision(self) -> None:
        with self.assertRaises(ProtocolValidationError) as context:
            summarize_live_snapshot_line_states(
                [LineState(content="print('hello')", origin_revision_id="us6-r2", gen_ratio=100)],
                revision_commit_times={},
                start_bound=datetime(2026, 3, 10, 0, 0, tzinfo=timezone.utc),
                end_bound=datetime(2026, 3, 31, 23, 59, 59, tzinfo=timezone.utc),
            )

        self.assertIn("Missing commit time for replayed live-snapshot revision us6-r2", str(context.exception))

    def test_reconstruct_final_line_states_replays_us7_mixed_history_sequence(self) -> None:
        query = load_json(US7_SCENARIO_DIR / "query.json")
        revision_ids = ["us7-r1", "us7-r2", "us7-r3", "us7-r4"]
        metadata_provider = GenCodeDescSetDirProvider(US7_SCENARIO_DIR, False, RuntimeLogger("quiet"))
        diff_provider = CommitDiffSetDirProvider(US7_SCENARIO_DIR / "commitDiffSet", RuntimeLogger("quiet"))
        sequence = load_commit_diff_sequence(
            diff_provider,
            query["repoURL"],
            query["repoBranch"],
            revision_ids,
            query["vcsType"],
        )
        protocol_indexes = {
            revision_id: build_protocol_index(
                metadata_provider.get_revision_metadata(query["repoURL"], query["repoBranch"], revision_id, query["vcsType"])
            )
            for revision_id in revision_ids
        }

        target_file, final_line_states = reconstruct_final_line_states_from_commit_diff_sequence(
            sequence,
            protocol_indexes,
        )

        self.assertEqual(target_file, "src/mixed.py")
        self.assertEqual(
            [line.content for line in final_line_states],
            [
                "first = seed",
                "second = seed + 1",
                "third = seed * 2",
                "fourth = normalize(seed)",
                "fifth = seed + helper(seed)",
            ],
        )
        self.assertEqual(
            [line.origin_revision_id for line in final_line_states],
            ["us7-r1", "us7-r1", "us7-r2", "us7-r3", "us7-r4"],
        )
        self.assertEqual(
            [line.gen_ratio for line in final_line_states],
            [0, 0, 100, 0, 60],
        )

    def test_summarize_live_changed_line_states_respects_fixture_included_revision_ids(self) -> None:
        query = load_json(US12_SCENARIO_DIR / "query.json")
        revision_ids = [
            "us12-r1",
            "us12-r2",
            "us12-r3",
            "us12-r5",
            "us12-r7",
            "us12-r8",
            "us12-r10",
            "us12-r14",
            "us12-r15",
        ]
        metadata_provider = GenCodeDescSetDirProvider(US12_SCENARIO_DIR, False, RuntimeLogger("quiet"))
        diff_provider = CommitDiffSetDirProvider(US12_SCENARIO_DIR / "commitDiffSet", RuntimeLogger("quiet"))
        sequence = load_commit_diff_sequence(
            diff_provider,
            query["repoURL"],
            query["repoBranch"],
            revision_ids,
            query["vcsType"],
        )
        protocol_indexes = {
            revision_id: build_protocol_index(
                metadata_provider.get_revision_metadata(query["repoURL"], query["repoBranch"], revision_id, query["vcsType"])
            )
            for revision_id in revision_ids
        }

        _, final_line_states = reconstruct_final_line_states_from_commit_diff_sequence(
            sequence,
            protocol_indexes,
        )
        summary = summarize_live_changed_line_states_by_revision_ids(final_line_states, query["includedRevisionIds"])

        self.assertEqual(
            summary,
            {
                "totalCodeLines": 7,
                "fullGeneratedCodeLines": 2,
                "partialGeneratedCodeLines": 2,
            },
        )


if __name__ == "__main__":
    unittest.main()