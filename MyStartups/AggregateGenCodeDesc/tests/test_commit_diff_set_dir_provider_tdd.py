import argparse
import tempfile
import unittest
from pathlib import Path

from aggregateGenCodeDesc import (
    CommitDiffSetDirProvider,
    EmptyCommitDiffProvider,
    ProtocolValidationError,
    RuntimeLogger,
    build_commit_diff_provider,
    list_commit_diff_revision_ids,
)


class TestCommitDiffSetDirProviderTdd(unittest.TestCase):
    def test_commit_diff_set_dir_provider_loads_raw_patch_text(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            patch_path = base_dir / "r42_commitDiff.patch"
            patch_path.write_text(
                "diff --git a/src/demo.py b/src/demo.py\n"
                "--- a/src/demo.py\n"
                "+++ b/src/demo.py\n"
                "@@ -1 +1,2 @@\n"
                "+print('hello')\n",
                encoding="utf-8",
            )

            provider = CommitDiffSetDirProvider(base_dir, RuntimeLogger("quiet"))

            patch_text = provider.get_commit_diff_patch("https://example.local/repo/demo", "main", "r42", "git")

            self.assertIn("diff --git a/src/demo.py b/src/demo.py", patch_text)
            self.assertIn("+print('hello')", patch_text)

    def test_commit_diff_set_dir_provider_loads_time_seq_prefixed_patch_for_revision(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            patch_path = base_dir / "0007_r42_commitDiff.patch"
            patch_path.write_text(
                "diff --git a/src/demo.py b/src/demo.py\n"
                "--- a/src/demo.py\n"
                "+++ b/src/demo.py\n"
                "@@ -1 +1,2 @@\n"
                "+print('hello')\n",
                encoding="utf-8",
            )

            provider = CommitDiffSetDirProvider(base_dir, RuntimeLogger("quiet"))

            patch_text = provider.get_commit_diff_patch("https://example.local/repo/demo", "main", "r42", "git")

            self.assertIn("diff --git a/src/demo.py b/src/demo.py", patch_text)
            self.assertIn("+print('hello')", patch_text)

    def test_commit_diff_set_dir_provider_fails_for_missing_patch(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            provider = CommitDiffSetDirProvider(Path(temp_dir), RuntimeLogger("quiet"))

            with self.assertRaises(ProtocolValidationError) as context:
                provider.get_commit_diff_patch("https://example.local/repo/demo", "main", "r404", "git")

        self.assertIn("Commit diff patch file not found", str(context.exception))

    def test_commit_diff_set_dir_provider_fails_for_empty_patch(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            (base_dir / "r50_commitDiff.patch").write_text("\n", encoding="utf-8")
            provider = CommitDiffSetDirProvider(base_dir, RuntimeLogger("quiet"))

            with self.assertRaises(ProtocolValidationError) as context:
                provider.get_commit_diff_patch("https://example.local/repo/demo", "main", "r50", "git")

        self.assertIn("Commit diff patch file is empty", str(context.exception))

    def test_build_commit_diff_provider_returns_set_dir_provider_when_configured(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            args = argparse.Namespace(commitDiffSetDir=temp_dir)

            provider = build_commit_diff_provider(args, RuntimeLogger("quiet"))

            self.assertIsInstance(provider, CommitDiffSetDirProvider)

    def test_build_commit_diff_provider_returns_empty_provider_without_config(self) -> None:
        args = argparse.Namespace(commitDiffSetDir=None)

        provider = build_commit_diff_provider(args, RuntimeLogger("quiet"))

        self.assertIsInstance(provider, EmptyCommitDiffProvider)
        self.assertIsNone(provider.get_commit_diff_patch("https://example.local/repo/demo", "main", "r1", "git"))

    def test_list_commit_diff_revision_ids_prefers_time_seq_order_when_present(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            for file_name in [
                "0010_r10_commitDiff.patch",
                "0002_r2_commitDiff.patch",
                "0001_r1_commitDiff.patch",
            ]:
                (base_dir / file_name).write_text("diff --git a/a b/a\n--- a/a\n+++ b/a\n", encoding="utf-8")

            self.assertEqual(list_commit_diff_revision_ids(base_dir), ["r1", "r2", "r10"])

    def test_list_commit_diff_revision_ids_keeps_legacy_filename_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            for file_name in [
                "r10_commitDiff.patch",
                "r2_commitDiff.patch",
                "r1_commitDiff.patch",
            ]:
                (base_dir / file_name).write_text("diff --git a/a b/a\n--- a/a\n+++ b/a\n", encoding="utf-8")

            self.assertEqual(list_commit_diff_revision_ids(base_dir), ["r1", "r2", "r10"])


if __name__ == "__main__":
    unittest.main()
