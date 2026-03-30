import subprocess
import tempfile
import unittest
from pathlib import Path

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

            self.assertIn("Only Algorithm A is implemented", context.exception.stderr)
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


if __name__ == "__main__":
    unittest.main()