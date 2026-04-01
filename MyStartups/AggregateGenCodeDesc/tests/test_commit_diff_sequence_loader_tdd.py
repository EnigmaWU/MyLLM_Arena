import unittest
from pathlib import Path

from aggregateGenCodeDesc import CommitDiffSetDirProvider, ProtocolValidationError, RuntimeLogger, load_commit_diff_sequence
from tests.cli_test_support import load_json


SCENARIO_DIR = Path(__file__).resolve().parent.parent / "testdata" / "us6_period_added_ratio"
COMMIT_DIFF_DIR = SCENARIO_DIR / "commitDiffSet"


class TestCommitDiffSequenceLoaderTdd(unittest.TestCase):
    def test_loader_builds_ordered_sequence_from_us6_fixture(self) -> None:
        query = load_json(SCENARIO_DIR / "query.json")
        provider = CommitDiffSetDirProvider(COMMIT_DIFF_DIR, RuntimeLogger("quiet"))

        sequence = load_commit_diff_sequence(
            provider,
            query["repoURL"],
            query["repoBranch"],
            query["includedRevisionIds"],
            query["vcsType"],
        )

        self.assertEqual([entry.revision_id for entry in sequence], ["us6-r2", "us6-r3"])
        self.assertEqual(sequence[0].parsed_patch.files[0].new_path, "src/report.py")
        first_added = [line for line in sequence[0].parsed_patch.files[0].hunks[0].lines if line.kind == "add"]
        second_added = [line for line in sequence[1].parsed_patch.files[0].hunks[0].lines if line.kind == "add"]
        self.assertEqual([line.new_line_number for line in first_added], [3, 4])
        self.assertEqual([line.new_line_number for line in second_added], [5, 6, 7])

    def test_loader_fails_when_provider_has_gap_in_sequence(self) -> None:
        query = load_json(SCENARIO_DIR / "query.json")
        provider = CommitDiffSetDirProvider(COMMIT_DIFF_DIR, RuntimeLogger("quiet"))

        with self.assertRaises(ProtocolValidationError) as context:
            load_commit_diff_sequence(
                provider,
                query["repoURL"],
                query["repoBranch"],
                ["us6-r2", "us6-r404", "us6-r3"],
                query["vcsType"],
            )

        self.assertIn("Commit diff patch file not found", str(context.exception))


if __name__ == "__main__":
    unittest.main()
