import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from aggregateGenCodeDesc import PROTOCOL_VERSION
from tests.cli_test_support import GitRepoHarness, PROJECT_ROOT, UTILITY_PATH, load_json, run_cli, write_revision_protocol


FIXTURE_DIR = Path(__file__).resolve().parent.parent / "testdata" / "us1_live_changed_source_ratio"


class TestCliAlgorithmFlagTdd(unittest.TestCase):
    def _build_local_git_algorithm_b_repo(
        self,
        root_dir: Path,
        repo_url_override: str | None = None,
    ) -> tuple[GitRepoHarness, Path, dict, str, str]:
        repo_dir = root_dir / "repo"
        protocol_dir = root_dir / "protocols"
        repo_dir.mkdir()
        protocol_dir.mkdir()

        repo = GitRepoHarness(repo_dir)
        repo.write(
            "src/calc.py",
            "def calc(x):\n"
            "    value = x + 1\n"
            "    return value\n",
        )
        human_revision = repo.commit_all("human-base", "2026-02-20T09:00:00Z")

        repo.write(
            "src/calc.py",
            "def calc(x):\n"
            "    value = normalize(x)\n"
            "    return value\n",
        )
        ai_revision = repo.commit_all("ai-rewrite", "2026-03-15T09:00:00Z")

        protocol = {
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
                "repoBranch": "main",
                "revisionId": ai_revision,
            },
            "DETAIL": [
                {
                    "fileName": "src/calc.py",
                    "codeLines": [
                        {
                            "lineLocation": 2,
                            "genRatio": 100,
                        }
                    ],
                }
            ],
        }
        write_revision_protocol(
            protocol_dir,
            protocol,
            repo_dir,
            ai_revision,
            repo_url_override=repo_url_override,
        )
        query = {
            "vcsType": "git",
            "repoURL": str(repo_dir),
            "repoBranch": "main",
            "scope": "A",
            "startTime": "2026-03-01",
            "endTime": "2026-03-31",
        }
        return repo, protocol_dir, query, human_revision, ai_revision

    def _build_local_git_algorithm_b_period_repo(self, root_dir: Path) -> tuple[GitRepoHarness, Path, dict, str, str]:
        repo_dir = root_dir / "period-repo"
        protocol_dir = root_dir / "period-protocols"
        repo_dir.mkdir()
        protocol_dir.mkdir()

        repo = GitRepoHarness(repo_dir)
        repo.write(
            "src/report.py",
            "def build_report(data):\n"
            "    report = []\n"
            "    return report\n",
        )
        repo.commit_all("human-base", "2026-02-20T09:00:00Z")

        repo.write(
            "src/report.py",
            "def build_report(data):\n"
            "    report = []\n"
            "    draft = summarize(data)\n"
            "    return report\n",
        )
        ai_revision = repo.commit_all("ai-add", "2026-03-10T09:00:00Z")

        repo.write(
            "src/report.py",
            "def build_report(data):\n"
            "    report = []\n"
            "    draft = summarize(data)\n"
            "    publish(draft)\n"
            "    return report\n",
        )
        human_revision = repo.commit_all("human-add", "2026-03-20T09:00:00Z")

        protocol = {
            "protocolName": "generatedTextDesc",
            "protocolVersion": PROTOCOL_VERSION,
            "SUMMARY": {
                "totalCodeLines": 2,
                "fullGeneratedCodeLines": 1,
                "partialGeneratedCodeLines": 0,
            },
            "REPOSITORY": {
                "vcsType": "git",
                "repoURL": str(repo_dir),
                "repoBranch": "main",
                "revisionId": human_revision,
            },
            "DETAIL": [
                {
                    "fileName": "src/report.py",
                    "codeLines": [
                        {
                            "lineLocation": 3,
                            "genRatio": 100,
                        }
                    ],
                }
            ],
        }
        write_revision_protocol(protocol_dir, protocol, repo_dir, ai_revision)
        query = {
            "vcsType": "git",
            "repoURL": str(repo_dir),
            "repoBranch": "main",
            "scope": "A",
            "startTime": "2026-03-01",
            "endTime": "2026-03-31",
        }
        return repo, protocol_dir, query, ai_revision, human_revision

    def _run_algorithm_b_live_snapshot_cli(self, query: dict, protocol_dir: Path, commit_diff_dir: Path, extra_args: list[str] | None = None) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "out.json"
            return subprocess.run(
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
                    str(protocol_dir),
                    "--commitDiffSetDir",
                    str(commit_diff_dir),
                    *(extra_args or []),
                ],
                cwd=PROJECT_ROOT,
                text=True,
                capture_output=True,
            )

    def _run_algorithm_b_offline_cli(self, query: dict, commit_diff_dir: Path, extra_args: list[str] | None = None) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "out.json"
            return subprocess.run(
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
                    "--commitDiffSetDir",
                    str(commit_diff_dir),
                    *(extra_args or []),
                ],
                cwd=PROJECT_ROOT,
                text=True,
                capture_output=True,
            )

    def test_cli_accepts_algorithm_flag(self) -> None:
        query = json.loads((FIXTURE_DIR / "query.json").read_text(encoding="utf-8"))
        revision_protocol = json.loads((FIXTURE_DIR / "01_genCodeDesc.json").read_text(encoding="utf-8"))

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

            result = run_cli(
                repo_dir,
                output_file,
                protocol_dir,
                query,
                extra_args=["--algorithm", "A"],
            )

            self.assertEqual(result.returncode, 0)
            self.assertTrue(output_file.exists())

    def test_cli_rejects_legacy_model_flag(self) -> None:
        result = subprocess.run(
            [
                "python3",
                str(UTILITY_PATH),
                "--repoURL",
                "dummy-repo",
                "--repoBranch",
                "main",
                "--startTime",
                "2026-03-01",
                "--endTime",
                "2026-03-31",
                "--model",
                "A",
            ],
            cwd=PROJECT_ROOT,
            text=True,
            capture_output=True,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unrecognized arguments: --model A", result.stderr)

    def test_cli_executes_narrow_algorithm_b_offline_diff_path_for_us6_fixture(self) -> None:
        fixture_dir = Path(__file__).resolve().parent.parent / "testdata" / "us6_period_added_ratio"
        query = json.loads((fixture_dir / "query.json").read_text(encoding="utf-8"))
        expected_result = json.loads((fixture_dir / "expected_result.json").read_text(encoding="utf-8"))

        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "out.json"

            result = subprocess.run(
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
                    str(fixture_dir),
                    "--commitDiffSetDir",
                    str(fixture_dir / "commitDiffSet"),
                ],
                cwd=PROJECT_ROOT,
                text=True,
                capture_output=True,
                check=True,
            )

            self.assertEqual(result.returncode, 0)
            actual_result = json.loads(output_file.read_text(encoding="utf-8"))
            self.assertEqual(actual_result, expected_result)

    def test_cli_executes_algorithm_b_live_snapshot_path_for_us1_fixture(self) -> None:
        fixture_dir = Path(__file__).resolve().parent.parent / "testdata" / "us1_live_changed_source_ratio"
        query = json.loads((fixture_dir / "query.json").read_text(encoding="utf-8"))
        expected_result = json.loads((fixture_dir / "expected_result.json").read_text(encoding="utf-8"))

        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "out.json"

            result = subprocess.run(
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
                    str(fixture_dir),
                    "--commitDiffSetDir",
                    str(fixture_dir / "commitDiffSet"),
                ],
                cwd=PROJECT_ROOT,
                text=True,
                capture_output=True,
                check=True,
            )

            self.assertEqual(result.returncode, 0)
            actual_result = json.loads(output_file.read_text(encoding="utf-8"))
            self.assertEqual(actual_result, expected_result)

    def test_cli_executes_algorithm_b_live_snapshot_path_for_us1_svn_fixture(self) -> None:
        fixture_dir = Path(__file__).resolve().parent.parent / "testdata" / "us1_live_changed_source_ratio_svn"
        query = json.loads((fixture_dir / "query.json").read_text(encoding="utf-8"))
        expected_result = json.loads((fixture_dir / "expected_result.json").read_text(encoding="utf-8"))

        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "out.json"

            result = subprocess.run(
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
                    str(fixture_dir),
                    "--commitDiffSetDir",
                    str(fixture_dir / "commitDiffSet"),
                ],
                cwd=PROJECT_ROOT,
                text=True,
                capture_output=True,
                check=True,
            )

            self.assertEqual(result.returncode, 0)
            actual_result = json.loads(output_file.read_text(encoding="utf-8"))
            self.assertEqual(actual_result, expected_result)

    def test_cli_executes_algorithm_b_live_snapshot_path_for_local_git_repo_without_commit_diff_fixtures(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo, protocol_dir, query, _human_revision, ai_revision = self._build_local_git_algorithm_b_repo(Path(temp_dir))
            output_file = Path(temp_dir) / "out.json"

            result = run_cli(
                repo.repo_dir,
                output_file,
                protocol_dir,
                query,
                extra_args=["--algorithm", "B", "--metric", "live_changed_source_ratio"],
            )

            self.assertEqual(result.returncode, 0)
            actual_result = load_json(output_file)
            self.assertEqual(
                actual_result,
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
                        "repoURL": str(repo.repo_dir),
                        "repoBranch": "main",
                        "revisionId": ai_revision,
                    },
                },
            )

    def test_cli_executes_algorithm_b_live_snapshot_path_with_logical_repo_url_and_working_dir(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            logical_repo_url = "https://example.local/repo/demo"
            repo, protocol_dir, query, _human_revision, ai_revision = self._build_local_git_algorithm_b_repo(
                Path(temp_dir),
                repo_url_override=logical_repo_url,
            )
            output_file = Path(temp_dir) / "out.json"

            result = run_cli(
                repo.repo_dir,
                output_file,
                protocol_dir,
                query,
                extra_args=["--algorithm", "B", "--metric", "live_changed_source_ratio"],
                repo_url_override=logical_repo_url,
                working_dir_override=repo.repo_dir,
            )

            self.assertEqual(result.returncode, 0)
            actual_result = load_json(output_file)
            self.assertEqual(actual_result["REPOSITORY"]["repoURL"], logical_repo_url)
            self.assertEqual(actual_result["REPOSITORY"]["revisionId"], ai_revision)
            self.assertEqual(
                actual_result["SUMMARY"],
                {
                    "totalCodeLines": 1,
                    "fullGeneratedCodeLines": 1,
                    "partialGeneratedCodeLines": 0,
                },
            )

    def test_cli_executes_algorithm_b_period_added_path_for_local_git_repo_without_commit_diff_fixtures(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo, protocol_dir, query, _ai_revision, human_revision = self._build_local_git_algorithm_b_period_repo(Path(temp_dir))
            output_file = Path(temp_dir) / "period-out.json"

            result = run_cli(
                repo.repo_dir,
                output_file,
                protocol_dir,
                query,
                extra_args=["--algorithm", "B", "--metric", "period_added_ai_ratio"],
            )

            self.assertEqual(result.returncode, 0)
            actual_result = load_json(output_file)
            self.assertEqual(
                actual_result,
                {
                    "protocolName": "generatedTextDesc",
                    "protocolVersion": PROTOCOL_VERSION,
                    "SUMMARY": {
                        "totalCodeLines": 2,
                        "fullGeneratedCodeLines": 1,
                        "partialGeneratedCodeLines": 0,
                    },
                    "REPOSITORY": {
                        "vcsType": "git",
                        "repoURL": str(repo.repo_dir),
                        "repoBranch": "main",
                        "revisionId": human_revision,
                    },
                },
            )

    def test_cli_rejects_algorithm_b_live_snapshot_without_commit_diff_fixtures_or_local_git_checkout(self) -> None:
        query = {
            "vcsType": "git",
            "repoURL": "https://example.local/repo/demo",
            "repoBranch": "main",
            "scope": "A",
            "startTime": "2026-03-01",
            "endTime": "2026-03-31",
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            protocol_dir = Path(temp_dir) / "protocols"
            protocol_dir.mkdir()
            output_file = Path(temp_dir) / "out.json"

            result = subprocess.run(
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
                    "--metric",
                    "live_changed_source_ratio",
                    "--scope",
                    query["scope"],
                    "--outputFile",
                    str(output_file),
                    "--genCodeDescSetDir",
                    str(protocol_dir),
                ],
                cwd=PROJECT_ROOT,
                text=True,
                capture_output=True,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("requires a local repository via --workingDir or an absolute --repoURL", result.stderr)

    def test_cli_rejects_invalid_vcs_type_for_algorithm_b_live_snapshot_path(self) -> None:
        query = {
            "vcsType": "hg",
            "repoURL": "https://example.local/repo/demo",
            "repoBranch": "main",
            "scope": "A",
            "startTime": "2026-03-01",
            "endTime": "2026-03-31",
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            fixture_dir = Path(__file__).resolve().parent.parent / "testdata" / "us1_live_changed_source_ratio"
            result = self._run_algorithm_b_live_snapshot_cli(
                query,
                fixture_dir,
                fixture_dir / "commitDiffSet",
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--vcsType must be one of: git, svn", result.stderr)

    def test_cli_rejects_algorithm_b_offline_first_patch_with_multiple_files(self) -> None:
        query = {
            "vcsType": "git",
            "repoURL": "https://example.local/repo/demo",
            "repoBranch": "main",
            "scope": "A",
            "startTime": "2026-03-10",
            "endTime": "2026-03-31",
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            commit_diff_dir = Path(temp_dir) / "commitDiffSet"
            commit_diff_dir.mkdir()
            (commit_diff_dir / "r1_commitDiff.patch").write_text(
                "diff --git a/src/report.py b/src/report.py\n"
                "--- a/src/report.py\n"
                "+++ b/src/report.py\n"
                "@@ -1 +1,2 @@\n"
                " def build_report(data):\n"
                "+    draft = summarize(data)\n"
                "diff --git a/src/extra.py b/src/extra.py\n"
                "--- a/src/extra.py\n"
                "+++ b/src/extra.py\n"
                "@@ -0,0 +1 @@\n"
                "+print('extra')\n",
                encoding="utf-8",
            )

            result = self._run_algorithm_b_offline_cli(
                query,
                commit_diff_dir,
                extra_args=["--metric", "period_added_ai_ratio"],
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("only supports a single file in the first patch sequence", result.stderr)

    def test_cli_rejects_algorithm_b_offline_first_patch_with_multiple_hunks(self) -> None:
        query = {
            "vcsType": "git",
            "repoURL": "https://example.local/repo/demo",
            "repoBranch": "main",
            "scope": "A",
            "startTime": "2026-03-10",
            "endTime": "2026-03-31",
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            commit_diff_dir = Path(temp_dir) / "commitDiffSet"
            commit_diff_dir.mkdir()
            (commit_diff_dir / "r1_commitDiff.patch").write_text(
                "diff --git a/src/report.py b/src/report.py\n"
                "--- a/src/report.py\n"
                "+++ b/src/report.py\n"
                "@@ -1 +1,2 @@\n"
                " def build_report(data):\n"
                "+    draft = summarize(data)\n"
                "@@ -5 +6,2 @@\n"
                " old_tail\n"
                "+new_tail\n",
                encoding="utf-8",
            )

            result = self._run_algorithm_b_offline_cli(
                query,
                commit_diff_dir,
                extra_args=["--metric", "period_added_ai_ratio"],
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("only supports a single hunk in the first patch", result.stderr)

    def test_cli_rejects_algorithm_b_offline_when_replayed_file_path_jumps_to_unrelated_file(self) -> None:
        query = {
            "vcsType": "git",
            "repoURL": "https://example.local/repo/demo",
            "repoBranch": "main",
            "scope": "A",
            "startTime": "2026-03-10",
            "endTime": "2026-03-31",
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            commit_diff_dir = Path(temp_dir) / "commitDiffSet"
            commit_diff_dir.mkdir()
            (commit_diff_dir / "r1_commitDiff.patch").write_text(
                "diff --git a/src/report.py b/src/report.py\n"
                "--- a/src/report.py\n"
                "+++ b/src/report.py\n"
                "@@ -1,2 +1,3 @@\n"
                " def build_report(data):\n"
                "     report = []\n"
                "+    draft = summarize(data)\n",
                encoding="utf-8",
            )
            (commit_diff_dir / "r2_commitDiff.patch").write_text(
                "diff --git a/src/unrelated.py b/src/report_renamed.py\n"
                "--- a/src/unrelated.py\n"
                "+++ b/src/report_renamed.py\n"
                "@@ -1,3 +1,4 @@\n"
                " def build_report(data):\n"
                "     report = []\n"
                "     draft = summarize(data)\n"
                "+    publish(draft)\n",
                encoding="utf-8",
            )

            result = self._run_algorithm_b_offline_cli(
                query,
                commit_diff_dir,
                extra_args=["--metric", "period_added_ai_ratio"],
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("only supports a single replayed file path across the diff sequence", result.stderr)

    def test_cli_rejects_algorithm_b_when_routing_metric_cannot_be_inferred(self) -> None:
        query = {
            "vcsType": "git",
            "repoURL": "https://example.local/repo/demo",
            "repoBranch": "main",
            "scope": "A",
            "startTime": "2026-03-10",
            "endTime": "2026-03-31",
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            commit_diff_dir = Path(temp_dir) / "commitDiffSet"
            commit_diff_dir.mkdir()
            (commit_diff_dir / "r1_commitDiff.patch").write_text(
                "diff --git a/src/report.py b/src/report.py\n"
                "--- a/src/report.py\n"
                "+++ b/src/report.py\n"
                "@@ -0,0 +1 @@\n"
                "+print('hello')\n",
                encoding="utf-8",
            )

            result = self._run_algorithm_b_offline_cli(query, commit_diff_dir)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("requires either --metric or a query.json metric", result.stderr)


if __name__ == "__main__":
    unittest.main()