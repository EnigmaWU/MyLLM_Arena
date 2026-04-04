import tempfile
import unittest
from pathlib import Path
import subprocess

from aggregateGenCodeDesc import PROTOCOL_VERSION
from tests.cli_test_support import GitRepoHarness, PROJECT_ROOT, UTILITY_PATH, load_json, run_cli, write_revision_protocol
from tests.log_assertions import assert_live_line_log, assert_log_contains_all, assert_log_contains_none


FIXTURE_DIR = Path(__file__).resolve().parent.parent / "testdata" / "us8_merge_commit_preserves_attribution"


class TestUs8MergeCommitPreservesAttributionTdd(unittest.TestCase):
    maxDiff = None

    def test_cli_algorithm_b_matches_algorithm_a_when_merge_keeps_feature_duplicate_line_after_main_deletes_original(self) -> None:
        query = {
            "vcsType": "git",
            "repoURL": "https://example.local/repo/us8-duplicate-merge",
            "repoBranch": "main",
            "scope": "A",
            "startTime": "2026-03-01",
            "endTime": "2026-03-31",
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            root_dir = Path(temp_dir)
            repo_dir = root_dir / "repo"
            protocol_dir = root_dir / "protocols"
            output_a = root_dir / "out-a.json"
            output_b = root_dir / "out-b.json"

            repo_dir.mkdir()
            protocol_dir.mkdir()

            repo = GitRepoHarness(repo_dir)
            repo.write(
                "src/duplicate_merge.py",
                "def plan(seed):\n"
                "    start = seed\n"
                "    dup = seed\n"
                "    marker = seed + 1\n"
                "    return marker\n",
            )
            revision_id_r1 = repo.commit_all("dup-r1", "2026-02-20T09:00:00Z")

            repo.checkout_new_branch("feature-ai")
            repo.write(
                "src/duplicate_merge.py",
                "def plan(seed):\n"
                "    start = seed\n"
                "    dup = seed\n"
                "    dup = seed\n"
                "    marker = seed + 1\n"
                "    return marker\n",
            )
            revision_id_r2 = repo.commit_all("dup-r2", "2026-03-10T09:00:00Z")

            repo.checkout("main")
            repo.write(
                "src/duplicate_merge.py",
                "def plan(seed):\n"
                "    start = seed\n"
                "    marker = seed + 1\n"
                "    return marker + 1\n",
            )
            revision_id_r3 = repo.commit_all("dup-r3", "2026-03-12T09:00:00Z")

            revision_id_r4 = repo.merge_with_manual_resolution(
                "feature-ai",
                "dup-r4",
                "2026-03-20T09:00:00Z",
                {
                    "src/duplicate_merge.py":
                        "def plan(seed):\n"
                        "    start = seed\n"
                        "    dup = seed\n"
                        "    marker = seed + 1\n"
                        "    return marker + 1\n"
                },
            )

            write_revision_protocol(
                protocol_dir,
                {
                    "protocolName": "generatedTextDesc",
                    "protocolVersion": PROTOCOL_VERSION,
                    "SUMMARY": {
                        "totalCodeLines": 0,
                        "fullGeneratedCodeLines": 0,
                        "partialGeneratedCodeLines": 0,
                    },
                    "REPOSITORY": {
                        "vcsType": "git",
                        "repoURL": str(repo_dir),
                        "repoBranch": "main",
                        "revisionId": revision_id_r1,
                    },
                    "DETAIL": [{"fileName": "src/duplicate_merge.py", "codeLines": []}],
                },
                repo_dir,
                revision_id_r1,
            )
            write_revision_protocol(
                protocol_dir,
                {
                    "protocolName": "generatedTextDesc",
                    "protocolVersion": PROTOCOL_VERSION,
                    "SUMMARY": {
                        "totalCodeLines": 1,
                        "fullGeneratedCodeLines": 1,
                        "partialGeneratedCodeLines": 0,
                    },
                    "REPOSITORY": {
                        "vcsType": "git",
                        "repoURL": str(repo_dir),
                        "repoBranch": "feature-ai",
                        "revisionId": revision_id_r2,
                    },
                    "DETAIL": [
                        {
                            "fileName": "src/duplicate_merge.py",
                            "codeLines": [{"lineLocation": 3, "genRatio": 100}],
                        }
                    ],
                },
                repo_dir,
                revision_id_r2,
            )
            write_revision_protocol(
                protocol_dir,
                {
                    "protocolName": "generatedTextDesc",
                    "protocolVersion": PROTOCOL_VERSION,
                    "SUMMARY": {
                        "totalCodeLines": 0,
                        "fullGeneratedCodeLines": 0,
                        "partialGeneratedCodeLines": 0,
                    },
                    "REPOSITORY": {
                        "vcsType": "git",
                        "repoURL": str(repo_dir),
                        "repoBranch": "main",
                        "revisionId": revision_id_r3,
                    },
                    "DETAIL": [{"fileName": "src/duplicate_merge.py", "codeLines": []}],
                },
                repo_dir,
                revision_id_r3,
            )
            write_revision_protocol(
                protocol_dir,
                {
                    "protocolName": "generatedTextDesc",
                    "protocolVersion": PROTOCOL_VERSION,
                    "SUMMARY": {
                        "totalCodeLines": 0,
                        "fullGeneratedCodeLines": 0,
                        "partialGeneratedCodeLines": 0,
                    },
                    "REPOSITORY": {
                        "vcsType": "git",
                        "repoURL": str(repo_dir),
                        "repoBranch": "main",
                        "revisionId": revision_id_r4,
                    },
                    "DETAIL": [{"fileName": "src/duplicate_merge.py", "codeLines": []}],
                },
                repo_dir,
                revision_id_r4,
            )

            result_a = run_cli(repo_dir, output_a, protocol_dir, query)
            result_b = run_cli(
                repo_dir,
                output_b,
                protocol_dir,
                query,
                extra_args=["--algorithm", "B"],
            )

            self.assertEqual(result_a.returncode, 0, msg=result_a.stderr)
            self.assertEqual(result_b.returncode, 0, msg=result_b.stderr)

            actual_a = load_json(output_a)
            actual_b = load_json(output_b)

            self.assertEqual(actual_a["REPOSITORY"]["revisionId"], revision_id_r4)
            self.assertEqual(actual_a["REPOSITORY"]["repoURL"], str(repo_dir))
            self.assertEqual(actual_b, actual_a)

    def test_cli_algorithm_b_matches_algorithm_a_when_manual_merge_adds_duplicate_text_matching_pre_window_parent_line(self) -> None:
        query = {
            "vcsType": "git",
            "repoURL": "https://example.local/repo/us8-manual-duplicate-text",
            "repoBranch": "main",
            "scope": "A",
            "startTime": "2026-03-01",
            "endTime": "2026-03-31",
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            root_dir = Path(temp_dir)
            repo_dir = root_dir / "repo"
            protocol_dir = root_dir / "protocols"
            output_a = root_dir / "out-a.json"
            output_b = root_dir / "out-b.json"

            repo_dir.mkdir()
            protocol_dir.mkdir()

            repo = GitRepoHarness(repo_dir)
            repo.write(
                "src/manual_merge_duplicate.py",
                "def plan(seed):\n"
                "    start = seed\n"
                "    dup = seed\n"
                "    marker = seed + 1\n"
                "    return marker\n",
            )
            revision_id_r1 = repo.commit_all("manual-dup-r1", "2026-02-20T09:00:00Z")

            repo.checkout_new_branch("feature-ai")
            repo.write(
                "src/manual_merge_duplicate.py",
                "def plan(seed):\n"
                "    start = seed\n"
                "    dup = seed\n"
                "    marker = helper(seed)\n"
                "    return marker + seed\n",
            )
            revision_id_r2 = repo.commit_all("manual-dup-r2", "2026-03-10T09:00:00Z")

            repo.checkout("main")
            repo.write(
                "src/manual_merge_duplicate.py",
                "def plan(seed):\n"
                "    start = sanitize(seed)\n"
                "    dup = seed\n"
                "    marker = seed + 1\n"
                "    return marker + 1\n",
            )
            revision_id_r3 = repo.commit_all("manual-dup-r3", "2026-03-12T09:00:00Z")

            revision_id_r4 = repo.merge_with_manual_resolution(
                "feature-ai",
                "manual-dup-r4",
                "2026-03-20T09:00:00Z",
                {
                    "src/manual_merge_duplicate.py":
                        "def plan(seed):\n"
                        "    start = sanitize(seed)\n"
                        "    dup = seed\n"
                        "    dup = seed\n"
                        "    marker = helper(seed)\n"
                        "    return marker + 1\n"
                },
            )

            write_revision_protocol(
                protocol_dir,
                {
                    "protocolName": "generatedTextDesc",
                    "protocolVersion": PROTOCOL_VERSION,
                    "SUMMARY": {
                        "totalCodeLines": 0,
                        "fullGeneratedCodeLines": 0,
                        "partialGeneratedCodeLines": 0,
                    },
                    "REPOSITORY": {
                        "vcsType": "git",
                        "repoURL": str(repo_dir),
                        "repoBranch": "main",
                        "revisionId": revision_id_r1,
                    },
                    "DETAIL": [{"fileName": "src/manual_merge_duplicate.py", "codeLines": []}],
                },
                repo_dir,
                revision_id_r1,
            )
            write_revision_protocol(
                protocol_dir,
                {
                    "protocolName": "generatedTextDesc",
                    "protocolVersion": PROTOCOL_VERSION,
                    "SUMMARY": {
                        "totalCodeLines": 1,
                        "fullGeneratedCodeLines": 1,
                        "partialGeneratedCodeLines": 0,
                    },
                    "REPOSITORY": {
                        "vcsType": "git",
                        "repoURL": str(repo_dir),
                        "repoBranch": "feature-ai",
                        "revisionId": revision_id_r2,
                    },
                    "DETAIL": [
                        {
                            "fileName": "src/manual_merge_duplicate.py",
                            "codeLines": [{"lineLocation": 4, "genRatio": 100}],
                        }
                    ],
                },
                repo_dir,
                revision_id_r2,
            )
            write_revision_protocol(
                protocol_dir,
                {
                    "protocolName": "generatedTextDesc",
                    "protocolVersion": PROTOCOL_VERSION,
                    "SUMMARY": {
                        "totalCodeLines": 0,
                        "fullGeneratedCodeLines": 0,
                        "partialGeneratedCodeLines": 0,
                    },
                    "REPOSITORY": {
                        "vcsType": "git",
                        "repoURL": str(repo_dir),
                        "repoBranch": "main",
                        "revisionId": revision_id_r3,
                    },
                    "DETAIL": [{"fileName": "src/manual_merge_duplicate.py", "codeLines": []}],
                },
                repo_dir,
                revision_id_r3,
            )
            write_revision_protocol(
                protocol_dir,
                {
                    "protocolName": "generatedTextDesc",
                    "protocolVersion": PROTOCOL_VERSION,
                    "SUMMARY": {
                        "totalCodeLines": 0,
                        "fullGeneratedCodeLines": 0,
                        "partialGeneratedCodeLines": 0,
                    },
                    "REPOSITORY": {
                        "vcsType": "git",
                        "repoURL": str(repo_dir),
                        "repoBranch": "main",
                        "revisionId": revision_id_r4,
                    },
                    "DETAIL": [{"fileName": "src/manual_merge_duplicate.py", "codeLines": []}],
                },
                repo_dir,
                revision_id_r4,
            )

            result_a = run_cli(repo_dir, output_a, protocol_dir, query)
            result_b = run_cli(
                repo_dir,
                output_b,
                protocol_dir,
                query,
                extra_args=["--algorithm", "B"],
            )

            self.assertEqual(result_a.returncode, 0, msg=result_a.stderr)
            self.assertEqual(result_b.returncode, 0, msg=result_b.stderr)

            actual_a = load_json(output_a)
            actual_b = load_json(output_b)

            self.assertEqual(actual_a["REPOSITORY"]["revisionId"], revision_id_r4)
            self.assertEqual(actual_a["REPOSITORY"]["repoURL"], str(repo_dir))
            self.assertEqual(actual_b, actual_a)

    def test_cli_matches_us8_expected_result_for_narrow_algorithm_b_fixture_path(self) -> None:
        query = load_json(FIXTURE_DIR / "query.json")
        expected_result = load_json(FIXTURE_DIR / "expected_result.json")

        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "out.json"
            subprocess.run(
                [
                    "python3",
                    str(UTILITY_PATH),
                    "--vcsType",
                    query["vcsType"],
                    "--repoURL",
                    query["repoURL"],
                    "--repoBranch",
                    query["repoBranch"],
                    "--startTime",
                    query["startTime"],
                    "--endTime",
                    query["endTime"],
                    "--algorithm",
                    "B",
                    "--scope",
                    query["scope"],
                    "--outputFile",
                    str(output_file),
                    "--genCodeDescSetDir",
                    str(FIXTURE_DIR),
                    "--commitDiffSetDir",
                    str(FIXTURE_DIR / "commitDiffSet"),
                ],
                cwd=PROJECT_ROOT,
                text=True,
                capture_output=True,
                check=True,
            )

            actual_result = load_json(output_file)
            self.assertEqual(actual_result, expected_result)

    def test_cli_matches_us8_expected_result_after_merge_preserves_effective_origin(self) -> None:
        self.assertTrue(
            UTILITY_PATH.exists(),
            f"Expected CLI utility at {UTILITY_PATH} for US-8 end-to-end execution.",
        )

        query = load_json(FIXTURE_DIR / "query.json")
        expected_result = load_json(FIXTURE_DIR / "expected_result.json")
        revision_protocol_r1 = load_json(FIXTURE_DIR / "01_genCodeDesc.json")
        revision_protocol_r2 = load_json(FIXTURE_DIR / "02_genCodeDesc.json")
        revision_protocol_r3 = load_json(FIXTURE_DIR / "03_genCodeDesc.json")
        revision_protocol_r4 = load_json(FIXTURE_DIR / "04_genCodeDesc.json")

        with tempfile.TemporaryDirectory() as temp_dir:
            root_dir = Path(temp_dir)
            repo_dir = root_dir / "repo"
            protocol_dir = root_dir / "protocols"
            output_file = root_dir / "out.json"

            repo_dir.mkdir()
            protocol_dir.mkdir()

            # WHY: US-8 is about the merge commit preserving each live line's
            # effective origin, so the history must contain both a feature-side
            # AI change and a mainline human change before the merge.
            repo = GitRepoHarness(repo_dir)
            repo.write(
                "src/merge_case.py",
                "base = x\n"
                "spacer = x\n"
                "value = x + 1\n"
                "return base + value + spacer\n",
            )
            revision_id_r1 = repo.commit_all("us8-r1", "2026-03-01T09:00:00Z")

            repo.checkout_new_branch("feature-ai")
            repo.write(
                "src/merge_case.py",
                "base = x\n"
                "spacer = x\n"
                "value = x * 2\n"
                "return base + value + spacer\n",
            )
            revision_id_r2 = repo.commit_all("us8-r2", "2026-03-10T09:00:00Z")

            repo.checkout("main")
            repo.write(
                "src/merge_case.py",
                "base = max(x, 0)\n"
                "spacer = x\n"
                "value = x + 1\n"
                "return base + value + spacer\n",
            )
            revision_id_r3 = repo.commit_all("us8-r3", "2026-03-12T09:00:00Z")

            revision_id_r4 = repo.merge_no_ff("feature-ai", "us8-r4", "2026-03-20T09:00:00Z")

            write_revision_protocol(protocol_dir, revision_protocol_r1, repo_dir, revision_id_r1)
            write_revision_protocol(protocol_dir, revision_protocol_r2, repo_dir, revision_id_r2)
            write_revision_protocol(protocol_dir, revision_protocol_r3, repo_dir, revision_id_r3)
            write_revision_protocol(protocol_dir, revision_protocol_r4, repo_dir, revision_id_r4)

            run_cli(repo_dir, output_file, protocol_dir, query)

            actual_result = load_json(output_file)
            expected_result["REPOSITORY"]["repoURL"] = str(repo_dir)
            expected_result["REPOSITORY"]["revisionId"] = revision_id_r4

            self.assertEqual(actual_result, expected_result)

    def test_cli_emits_debug_logs_for_us8_when_enabled(self) -> None:
        query = load_json(FIXTURE_DIR / "query.json")
        revision_protocol_r1 = load_json(FIXTURE_DIR / "01_genCodeDesc.json")
        revision_protocol_r2 = load_json(FIXTURE_DIR / "02_genCodeDesc.json")
        revision_protocol_r3 = load_json(FIXTURE_DIR / "03_genCodeDesc.json")
        revision_protocol_r4 = load_json(FIXTURE_DIR / "04_genCodeDesc.json")

        with tempfile.TemporaryDirectory() as temp_dir:
            root_dir = Path(temp_dir)
            repo_dir = root_dir / "repo"
            protocol_dir = root_dir / "protocols"
            output_file = root_dir / "out.json"

            repo_dir.mkdir()
            protocol_dir.mkdir()

            repo = GitRepoHarness(repo_dir)
            repo.write(
                "src/merge_case.py",
                "base = x\n"
                "spacer = x\n"
                "value = x + 1\n"
                "return base + value + spacer\n",
            )
            revision_id_r1 = repo.commit_all("us8-r1", "2026-03-01T09:00:00Z")

            repo.checkout_new_branch("feature-ai")
            repo.write(
                "src/merge_case.py",
                "base = x\n"
                "spacer = x\n"
                "value = x * 2\n"
                "return base + value + spacer\n",
            )
            revision_id_r2 = repo.commit_all("us8-r2", "2026-03-10T09:00:00Z")

            repo.checkout("main")
            repo.write(
                "src/merge_case.py",
                "base = max(x, 0)\n"
                "spacer = x\n"
                "value = x + 1\n"
                "return base + value + spacer\n",
            )
            revision_id_r3 = repo.commit_all("us8-r3", "2026-03-12T09:00:00Z")

            revision_id_r4 = repo.merge_no_ff("feature-ai", "us8-r4", "2026-03-20T09:00:00Z")

            write_revision_protocol(protocol_dir, revision_protocol_r1, repo_dir, revision_id_r1)
            write_revision_protocol(protocol_dir, revision_protocol_r2, repo_dir, revision_id_r2)
            write_revision_protocol(protocol_dir, revision_protocol_r3, repo_dir, revision_id_r3)
            write_revision_protocol(protocol_dir, revision_protocol_r4, repo_dir, revision_id_r4)

            result = run_cli(
                repo_dir,
                output_file,
                protocol_dir,
                query,
                extra_args=["--logLevel", "debug"],
            )

            assert_log_contains_all(
                self,
                result.stderr,
                [
                    "Starting analysis",
                    "Loaded genCodeDesc for revision",
                    "Finished analysis",
                ],
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/merge_case.py",
                final_line=1,
                origin_file="src/merge_case.py",
                origin_line=1,
                revision_id=revision_id_r3,
                classification="human/unattributed",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/merge_case.py",
                final_line=2,
                origin_file="src/merge_case.py",
                origin_line=2,
                revision_id=revision_id_r1,
                classification="human/unattributed",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/merge_case.py",
                final_line=3,
                origin_file="src/merge_case.py",
                origin_line=3,
                revision_id=revision_id_r2,
                classification="100%-ai",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/merge_case.py",
                final_line=4,
                origin_file="src/merge_case.py",
                origin_line=4,
                revision_id=revision_id_r1,
                classification="human/unattributed",
            )

    def test_cli_info_logging_focuses_on_live_line_aggregation_progress_for_us8(self) -> None:
        query = load_json(FIXTURE_DIR / "query.json")
        revision_protocol_r1 = load_json(FIXTURE_DIR / "01_genCodeDesc.json")
        revision_protocol_r2 = load_json(FIXTURE_DIR / "02_genCodeDesc.json")
        revision_protocol_r3 = load_json(FIXTURE_DIR / "03_genCodeDesc.json")
        revision_protocol_r4 = load_json(FIXTURE_DIR / "04_genCodeDesc.json")

        with tempfile.TemporaryDirectory() as temp_dir:
            root_dir = Path(temp_dir)
            repo_dir = root_dir / "repo"
            protocol_dir = root_dir / "protocols"
            output_file = root_dir / "out.json"

            repo_dir.mkdir()
            protocol_dir.mkdir()

            repo = GitRepoHarness(repo_dir)
            repo.write(
                "src/merge_case.py",
                "base = x\n"
                "spacer = x\n"
                "value = x + 1\n"
                "return base + value + spacer\n",
            )
            revision_id_r1 = repo.commit_all("us8-r1", "2026-03-01T09:00:00Z")

            repo.checkout_new_branch("feature-ai")
            repo.write(
                "src/merge_case.py",
                "base = x\n"
                "spacer = x\n"
                "value = x * 2\n"
                "return base + value + spacer\n",
            )
            repo.commit_all("us8-r2", "2026-03-10T09:00:00Z")

            repo.checkout("main")
            repo.write(
                "src/merge_case.py",
                "base = max(x, 0)\n"
                "spacer = x\n"
                "value = x + 1\n"
                "return base + value + spacer\n",
            )
            revision_id_r3 = repo.commit_all("us8-r3", "2026-03-12T09:00:00Z")

            revision_id_r4 = repo.merge_no_ff("feature-ai", "us8-r4", "2026-03-20T09:00:00Z")

            write_revision_protocol(protocol_dir, revision_protocol_r1, repo_dir, revision_id_r1)
            write_revision_protocol(protocol_dir, revision_protocol_r2, repo_dir, repo.commit_ids["us8-r2"])
            write_revision_protocol(protocol_dir, revision_protocol_r3, repo_dir, revision_id_r3)
            write_revision_protocol(protocol_dir, revision_protocol_r4, repo_dir, revision_id_r4)

            result = run_cli(
                repo_dir,
                output_file,
                protocol_dir,
                query,
                extra_args=["--logLevel", "info"],
            )

            assert_log_contains_all(
                self,
                result.stderr,
                [
                    "Starting analysis",
                    "LiveLine src/merge_case.py:1 aggregate",
                    "LiveLine src/merge_case.py:2 aggregate",
                    "LiveLine src/merge_case.py:3 aggregate",
                    "LiveLine src/merge_case.py:4 aggregate",
                ],
            )
            assert_log_contains_none(
                self,
                result.stderr,
                [
                    "Loaded genCodeDesc for revision",
                    "best_effort_transition=",
                ],
            )


if __name__ == "__main__":
    unittest.main()