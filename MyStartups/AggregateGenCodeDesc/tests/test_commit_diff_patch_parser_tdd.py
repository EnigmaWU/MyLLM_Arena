import unittest
from pathlib import Path

from aggregateGenCodeDesc import ProtocolValidationError, parse_commit_diff_patch


FIXTURE_DIR = Path(__file__).resolve().parent.parent / "testdata" / "us6_period_added_ratio" / "commitDiffSet"


class TestCommitDiffPatchParserTdd(unittest.TestCase):
    def test_parser_extracts_added_lines_from_us6_r2_patch(self) -> None:
        patch_text = (FIXTURE_DIR / "0001_us6-r2_commitDiff.patch").read_text(encoding="utf-8")

        parsed = parse_commit_diff_patch(patch_text)

        self.assertEqual(len(parsed.files), 1)
        parsed_file = parsed.files[0]
        self.assertEqual(parsed_file.old_path, "src/report.py")
        self.assertEqual(parsed_file.new_path, "src/report.py")
        self.assertEqual(len(parsed_file.hunks), 1)
        added_lines = [line for line in parsed_file.hunks[0].lines if line.kind == "add"]
        self.assertEqual([line.new_line_number for line in added_lines], [3, 4])
        self.assertEqual([line.content for line in added_lines], [
            "    draft = summarize(data)",
            "    publish(draft)",
        ])

    def test_parser_extracts_added_lines_from_us6_r3_patch(self) -> None:
        patch_text = (FIXTURE_DIR / "0002_us6-r3_commitDiff.patch").read_text(encoding="utf-8")

        parsed = parse_commit_diff_patch(patch_text)

        self.assertEqual(len(parsed.files), 1)
        added_lines = [line for line in parsed.files[0].hunks[0].lines if line.kind == "add"]
        self.assertEqual([line.new_line_number for line in added_lines], [5, 6, 7])
        self.assertEqual(added_lines[-1].content, "    return publish_result")

    def test_parser_rejects_patch_without_diff_git_header(self) -> None:
        with self.assertRaises(ProtocolValidationError) as context:
            parse_commit_diff_patch("--- a/src/demo.py\n+++ b/src/demo.py\n")

        self.assertIn("must start with a diff --git file header", str(context.exception))

    def test_parser_rejects_malformed_hunk_header(self) -> None:
        patch_text = (
            "diff --git a/src/demo.py b/src/demo.py\n"
            "--- a/src/demo.py\n"
            "+++ b/src/demo.py\n"
            "@@ malformed @@\n"
        )

        with self.assertRaises(ProtocolValidationError) as context:
            parse_commit_diff_patch(patch_text)

        self.assertIn("Malformed commit diff hunk header", str(context.exception))

    def test_parser_infers_file_paths_from_diff_git_header_when_path_headers_are_absent(self) -> None:
        parsed = parse_commit_diff_patch("diff --git a/src/demo.py b/src/demo.py\n")

        self.assertEqual(len(parsed.files), 1)
        self.assertEqual(parsed.files[0].old_path, "src/demo.py")
        self.assertEqual(parsed.files[0].new_path, "src/demo.py")


if __name__ == "__main__":
    unittest.main()
