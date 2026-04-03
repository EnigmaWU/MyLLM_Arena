import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import aggregateGenCodeDesc
from tests.cli_test_support import GitRepoHarness, load_json, run_cli, write_revision_protocol


FIXTURE_DIR = Path(__file__).resolve().parent.parent / "testdata" / "us1_live_changed_source_ratio"


class TestRuntimeHardeningTdd(unittest.TestCase):
    def test_cli_fails_cleanly_for_unsupported_algorithm(self) -> None:
        query = load_json(FIXTURE_DIR / "query.json")
        revision_protocol = load_json(FIXTURE_DIR / "01_genCodeDesc.json")

        with tempfile.TemporaryDirectory() as temp_dir:
            root_dir = Path(temp_dir)
            repo_dir = root_dir / "repo"
            protocol_dir = root_dir / "protocols"
            output_file = root_dir / "out.json"

            repo_dir.mkdir()
            protocol_dir.mkdir()

            repo = GitRepoHarness(repo_dir)
            repo.write(
                "src/calc.py",
                "def calc(x):\n"
                "    value = x + 1\n"
                "    boosted = value * 2\n"
                "    return boosted\n",
            )
            revision_id = repo.commit_all("us1-r1", "2026-03-10T09:00:00Z")
            write_revision_protocol(protocol_dir, revision_protocol, repo_dir, revision_id)

            with self.assertRaises(subprocess.CalledProcessError) as context:
                run_cli(repo_dir, output_file, protocol_dir, query, extra_args=["--algorithm", "B"])

            self.assertIn("Current Algorithm B routing requires either --metric or a query.json metric", context.exception.stderr)
            self.assertNotIn("Traceback", context.exception.stderr)

    def test_cli_fails_cleanly_for_missing_file_name_in_protocol_detail(self) -> None:
        query = load_json(FIXTURE_DIR / "query.json")
        revision_protocol = load_json(FIXTURE_DIR / "01_genCodeDesc.json")

        with tempfile.TemporaryDirectory() as temp_dir:
            root_dir = Path(temp_dir)
            repo_dir = root_dir / "repo"
            protocol_dir = root_dir / "protocols"
            output_file = root_dir / "out.json"

            repo_dir.mkdir()
            protocol_dir.mkdir()

            repo = GitRepoHarness(repo_dir)
            repo.write(
                "src/calc.py",
                "def calc(x):\n"
                "    value = x + 1\n"
                "    boosted = value * 2\n"
                "    return boosted\n",
            )
            revision_id = repo.commit_all("us1-r1", "2026-03-10T09:00:00Z")

            revision_protocol["DETAIL"][0].pop("fileName")
            write_revision_protocol(protocol_dir, revision_protocol, repo_dir, revision_id)

            with self.assertRaises(subprocess.CalledProcessError) as context:
                run_cli(repo_dir, output_file, protocol_dir, query)

            self.assertIn("Protocol DETAIL entry missing fileName", context.exception.stderr)
            self.assertNotIn("Traceback", context.exception.stderr)

    def test_cli_fails_cleanly_for_missing_protocol_file_when_required(self) -> None:
        query = load_json(FIXTURE_DIR / "query.json")

        with tempfile.TemporaryDirectory() as temp_dir:
            root_dir = Path(temp_dir)
            repo_dir = root_dir / "repo"
            protocol_dir = root_dir / "protocols"
            output_file = root_dir / "out.json"

            repo_dir.mkdir()
            protocol_dir.mkdir()

            repo = GitRepoHarness(repo_dir)
            repo.write(
                "src/calc.py",
                "def calc(x):\n"
                "    value = x + 1\n"
                "    boosted = value * 2\n"
                "    return boosted\n",
            )
            repo.commit_all("us1-r1", "2026-03-10T09:00:00Z")

            with self.assertRaises(subprocess.CalledProcessError) as context:
                run_cli(repo_dir, output_file, protocol_dir, query, extra_args=["--failOnMissingProtocol"])

            self.assertIn("Protocol file not found", context.exception.stderr)
            self.assertNotIn("Traceback", context.exception.stderr)

    def test_cli_fails_cleanly_for_overlapping_protocol_line_coverage(self) -> None:
        query = load_json(FIXTURE_DIR / "query.json")
        revision_protocol = load_json(FIXTURE_DIR / "01_genCodeDesc.json")

        with tempfile.TemporaryDirectory() as temp_dir:
            root_dir = Path(temp_dir)
            repo_dir = root_dir / "repo"
            protocol_dir = root_dir / "protocols"
            output_file = root_dir / "out.json"

            repo_dir.mkdir()
            protocol_dir.mkdir()

            repo = GitRepoHarness(repo_dir)
            repo.write(
                "src/calc.py",
                "def calc(x):\n"
                "    value = x + 1\n"
                "    boosted = value * 2\n"
                "    return boosted\n",
            )
            revision_id = repo.commit_all("us1-r1", "2026-03-10T09:00:00Z")

            revision_protocol["DETAIL"][0]["codeLines"] = [
                {"lineLocation": 2, "genRatio": 50, "genMethod": "codeCompletion"},
                {"lineRange": {"from": 2, "to": 3}, "genRatio": 100, "genMethod": "vibeCoding"},
            ]
            write_revision_protocol(protocol_dir, revision_protocol, repo_dir, revision_id)

            with self.assertRaises(subprocess.CalledProcessError) as context:
                run_cli(repo_dir, output_file, protocol_dir, query)

            self.assertIn("overlapping line coverage at line 2", context.exception.stderr)
            self.assertNotIn("Traceback", context.exception.stderr)

    def test_cli_fails_cleanly_for_gen_ratio_outside_valid_range(self) -> None:
        query = load_json(FIXTURE_DIR / "query.json")
        revision_protocol = load_json(FIXTURE_DIR / "01_genCodeDesc.json")

        with tempfile.TemporaryDirectory() as temp_dir:
            root_dir = Path(temp_dir)
            repo_dir = root_dir / "repo"
            protocol_dir = root_dir / "protocols"
            output_file = root_dir / "out.json"

            repo_dir.mkdir()
            protocol_dir.mkdir()

            repo = GitRepoHarness(repo_dir)
            repo.write(
                "src/calc.py",
                "def calc(x):\n"
                "    value = x + 1\n"
                "    boosted = value * 2\n"
                "    return boosted\n",
            )
            revision_id = repo.commit_all("us1-r1", "2026-03-10T09:00:00Z")

            revision_protocol["DETAIL"][0]["codeLines"][0]["genRatio"] = 101
            write_revision_protocol(protocol_dir, revision_protocol, repo_dir, revision_id)

            with self.assertRaises(subprocess.CalledProcessError) as context:
                run_cli(repo_dir, output_file, protocol_dir, query)

            self.assertIn("has genRatio outside 0..100", context.exception.stderr)
            self.assertNotIn("Traceback", context.exception.stderr)

    def test_cli_fails_cleanly_when_no_revision_exists_before_end_time(self) -> None:
        query = load_json(FIXTURE_DIR / "query.json")
        revision_protocol = load_json(FIXTURE_DIR / "01_genCodeDesc.json")

        with tempfile.TemporaryDirectory() as temp_dir:
            root_dir = Path(temp_dir)
            repo_dir = root_dir / "repo"
            protocol_dir = root_dir / "protocols"
            output_file = root_dir / "out.json"

            repo_dir.mkdir()
            protocol_dir.mkdir()

            repo = GitRepoHarness(repo_dir)
            repo.write(
                "src/calc.py",
                "def calc(x):\n"
                "    value = x + 1\n"
                "    boosted = value * 2\n"
                "    return boosted\n",
            )
            revision_id = repo.commit_all("us1-r1", "2026-03-10T09:00:00Z")
            write_revision_protocol(protocol_dir, revision_protocol, repo_dir, revision_id)

            query["startTime"] = "2026-03-01"
            query["endTime"] = "2026-03-01"

            with self.assertRaises(subprocess.CalledProcessError) as context:
                run_cli(repo_dir, output_file, protocol_dir, query)

            self.assertIn("No revision found at or before endTime", context.exception.stderr)
            self.assertNotIn("Traceback", context.exception.stderr)

    def test_cli_requires_working_dir_for_git_when_repo_url_is_logical_url(self) -> None:
        result = subprocess.run(
            [
                "python3",
                str(Path(__file__).resolve().parent.parent / "aggregateGenCodeDesc.py"),
                "--repoURL",
                "https://example.local/repo/demo.git",
                "--repoBranch",
                "main",
                "--startTime",
                "2026-03-01",
                "--endTime",
                "2026-03-31",
                "--vcsType",
                "git",
            ],
            cwd=Path(__file__).resolve().parent.parent,
            text=True,
            capture_output=True,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--workingDir is required for git", result.stderr)

    def test_cli_rejects_commit_diff_set_dir_for_algorithm_a(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run(
                [
                    "python3",
                    str(Path(__file__).resolve().parent.parent / "aggregateGenCodeDesc.py"),
                    "--repoURL",
                    "/tmp/local-repo",
                    "--repoBranch",
                    "main",
                    "--startTime",
                    "2026-03-01",
                    "--endTime",
                    "2026-03-31",
                    "--vcsType",
                    "git",
                    "--algorithm",
                    "A",
                    "--commitDiffSetDir",
                    temp_dir,
                ],
                cwd=Path(__file__).resolve().parent.parent,
                text=True,
                capture_output=True,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--commitDiffSetDir is only supported with --algorithm B", result.stderr)

    def test_cli_allows_algorithm_b_commit_diff_set_dir_without_git_working_dir(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run(
                [
                    "python3",
                    str(Path(__file__).resolve().parent.parent / "aggregateGenCodeDesc.py"),
                    "--repoURL",
                    "https://example.local/repo/demo.git",
                    "--repoBranch",
                    "main",
                    "--startTime",
                    "2026-03-01",
                    "--endTime",
                    "2026-03-31",
                    "--vcsType",
                    "git",
                    "--algorithm",
                    "B",
                    "--commitDiffSetDir",
                    temp_dir,
                ],
                cwd=Path(__file__).resolve().parent.parent,
                text=True,
                capture_output=True,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Current Algorithm B routing requires either --metric or a query.json metric", result.stderr)
        self.assertNotIn("--workingDir is required for git", result.stderr)

    def test_cli_rejects_repo_branch_with_path_traversal(self) -> None:
        result = subprocess.run(
            [
                "python3",
                str(Path(__file__).resolve().parent.parent / "aggregateGenCodeDesc.py"),
                "--repoURL",
                "/tmp/local-repo",
                "--repoBranch",
                "../../etc/passwd",
                "--startTime",
                "2026-03-01",
                "--endTime",
                "2026-03-31",
                "--vcsType",
                "git",
            ],
            cwd=Path(__file__).resolve().parent.parent,
            text=True,
            capture_output=True,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--repoBranch must not contain path traversal", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_cli_rejects_empty_repo_branch(self) -> None:
        result = subprocess.run(
            [
                "python3",
                str(Path(__file__).resolve().parent.parent / "aggregateGenCodeDesc.py"),
                "--repoURL",
                "/tmp/local-repo",
                "--repoBranch",
                "",
                "--startTime",
                "2026-03-01",
                "--endTime",
                "2026-03-31",
                "--vcsType",
                "git",
            ],
            cwd=Path(__file__).resolve().parent.parent,
            text=True,
            capture_output=True,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--repoBranch must not be empty", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_cli_rejects_start_time_after_end_time(self) -> None:
        result = subprocess.run(
            [
                "python3",
                str(Path(__file__).resolve().parent.parent / "aggregateGenCodeDesc.py"),
                "--repoURL",
                "/tmp/local-repo",
                "--repoBranch",
                "main",
                "--startTime",
                "2026-04-01",
                "--endTime",
                "2026-03-01",
                "--vcsType",
                "git",
            ],
            cwd=Path(__file__).resolve().parent.parent,
            text=True,
            capture_output=True,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--startTime must not be after --endTime", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_parse_svn_blame_fails_when_blame_entries_and_file_lines_diverge(self) -> None:
        def fake_run_svn(args: list[str]) -> str:
            if args[:3] == ["blame", "--xml", "-g"]:
                return (
                    '<?xml version="1.0" encoding="UTF-8"?>\n'
                    '<blame><target path="file:///repo/trunk/src/demo.py">'
                    '<entry line-number="1"><commit revision="11"/></entry>'
                    '</target></blame>'
                )
            if args[:2] == ["cat", "-r"]:
                return "line one\nline two\n"
            raise AssertionError(f"Unexpected svn invocation: {args}")

        with patch.object(aggregateGenCodeDesc, "run_svn", side_effect=fake_run_svn):
            with self.assertRaises(aggregateGenCodeDesc.RepositoryStateError) as context:
                aggregateGenCodeDesc.parse_svn_blame("file:///repo", "trunk", "11", "src/demo.py")

        self.assertIn("SVN blame/content line count mismatch", str(context.exception))


if __name__ == "__main__":
    unittest.main()