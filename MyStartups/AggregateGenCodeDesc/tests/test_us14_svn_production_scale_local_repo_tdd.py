import shutil
import subprocess
import tempfile
import unittest
from argparse import Namespace
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import aggregateGenCodeDesc
import pytest
from tests.cli_test_support import SvnRepoHarness, load_json, write_revision_protocol


FIXTURE_DIR = Path(__file__).resolve().parent.parent / "testdata" / "us14_svn_production_scale_local_repo"
FEATURE_BRANCH_COUNT = 100
COMMITS_PER_FEATURE_BRANCH = 10
FULL_AI_BRANCH_COUNT = 40
PARTIAL_AI_BRANCH_COUNT = 30
PARTIAL_AI_RATIO = 60
INTEGRATION_BATCH_SIZE = 10


class _DateCursor:
    def __init__(self, start: datetime):
        self.current = start

    def next(self) -> str:
        value = self.current
        self.current += timedelta(minutes=1)
        return value.strftime("%Y-%m-%dT%H:%M:%S.000000Z")


class _CountingProvider(aggregateGenCodeDesc.GenCodeDescProvider):
    def __init__(self, inner: aggregateGenCodeDesc.GenCodeDescProvider):
        self.inner = inner
        self.calls: list[str] = []

    def get_revision_metadata(self, repo_url: str, repo_branch: str, revision_id: str, vcs_type: str) -> dict:
        self.calls.append(revision_id)
        return self.inner.get_revision_metadata(repo_url, repo_branch, revision_id, vcs_type)


@pytest.mark.production_scale
@pytest.mark.long_running
@unittest.skipUnless(shutil.which("svn") and shutil.which("svnadmin"), "svn tooling not installed")
class TestUs14SvnProductionScaleLocalRepoTdd(unittest.TestCase):
    maxDiff = None

    def _query(self) -> dict:
        return load_json(FIXTURE_DIR / "query.json")

    def _expected_result(self) -> dict:
        return load_json(FIXTURE_DIR / "expected_result.json")

    def _run(self, command: list[str]) -> str:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        return result.stdout.strip()

    def _commit_path(self, path: Path, label: str, date: str, repo_url: str) -> str:
        result = subprocess.run(["svn", "commit", "-m", label, str(path)], check=True, capture_output=True, text=True)
        committed_line = next(line for line in result.stdout.splitlines() if line.startswith("Committed revision "))
        revision_id = committed_line.removeprefix("Committed revision ").removesuffix(".")
        self._run(["svn", "propset", "--revprop", "-r", revision_id, "svn:date", date, repo_url])
        return revision_id

    def _checkout(self, repo_url: str, target_url: str, target_path: Path) -> None:
        subprocess.run(["svn", "checkout", target_url, str(target_path)], check=True, capture_output=True, text=True)

    def _feature_ratio(self, feature_index: int) -> int:
        if feature_index < FULL_AI_BRANCH_COUNT:
            return 100
        if feature_index < FULL_AI_BRANCH_COUNT + PARTIAL_AI_BRANCH_COUNT:
            return PARTIAL_AI_RATIO
        return 0

    def _protocol_detail(self, file_name: str, ratio: int) -> dict:
        code_lines = []
        if ratio > 0:
            code_lines = [
                {"lineLocation": 2, "genRatio": ratio, "genMethod": "codeCompletion"},
                {"lineLocation": 3, "genRatio": ratio, "genMethod": "codeCompletion"},
            ]
        return {
            "fileName": file_name,
            "codeLines": code_lines,
        }

    def _protocol(self, *, details: list[dict]) -> dict:
        full_generated_code_lines = 0
        partial_generated_code_lines = 0
        for detail in details:
            for code_line in detail.get("codeLines", []):
                if code_line["genRatio"] == 100:
                    full_generated_code_lines += 1
                elif code_line["genRatio"] > 0:
                    partial_generated_code_lines += 1
        return {
            "protocolName": "generatedTextDesc",
            "protocolVersion": "26.03",
            "codeAgent": "US14ScaleAgent",
            "SUMMARY": {
                "totalCodeLines": full_generated_code_lines + partial_generated_code_lines,
                "fullGeneratedCodeLines": full_generated_code_lines,
                "partialGeneratedCodeLines": partial_generated_code_lines,
            },
            "DETAIL": details,
            "REPOSITORY": {
                "vcsType": "svn",
                "repoURL": "placeholder",
                "repoBranch": "trunk",
                "revisionId": "placeholder",
            },
        }

    def _feature_file_content(self, feature_index: int, commit_index: int) -> str:
        return (
            f"# feature {feature_index:03d}\n"
            f"feature_value_a = {feature_index} + {commit_index}\n"
            f"feature_value_b = {feature_index} + {commit_index} * 2\n"
        )

    def _build_repo(self, root_dir: Path) -> tuple[SvnRepoHarness, Path, str, list[str], int, int]:
        repo_dir = root_dir / "repo"
        working_copy_dir = root_dir / "wc"
        branches_root = root_dir / "branch_wcs"
        protocol_dir = root_dir / "protocols"
        protocol_dir.mkdir()
        branches_root.mkdir()

        repo = SvnRepoHarness(repo_dir, working_copy_dir)
        (repo.working_copy_dir / "branches").mkdir()
        self._run(["svn", "add", str(repo.working_copy_dir / "branches")])
        repo.commit_all("create branches", "2026-02-25T09:00:00.000000Z")

        (repo.working_copy_dir / "trunk" / "src").mkdir(parents=True, exist_ok=True)
        self._run(["svn", "add", str(repo.working_copy_dir / "trunk" / "src")])
        for feature_index in range(FEATURE_BRANCH_COUNT):
            repo.write(
                f"trunk/src/feature_{feature_index:03d}.py",
                f"# feature {feature_index:03d}\n"
                f"feature_value_a = {feature_index} + 0\n"
                f"feature_value_b = {feature_index} + 0\n",
            )
            repo.add(f"trunk/src/feature_{feature_index:03d}.py")
        repo.commit_all("us14-base", "2026-02-26T09:00:00.000000Z")

        date_cursor = _DateCursor(datetime(2026, 3, 1, 0, 0, tzinfo=timezone.utc))
        integration_revision_ids: list[str] = []
        integration_batches: list[list[tuple[int, str]]] = []

        current_batch: list[tuple[int, str]] = []
        for feature_index in range(FEATURE_BRANCH_COUNT):
            branch_name = f"feature-{feature_index:03d}"
            copy_result = subprocess.run(
                ["svn", "copy", repo.trunk_url, f"{repo.repo_url}/branches/{branch_name}", "-m", f"copy {branch_name}"],
                check=True,
                capture_output=True,
                text=True,
            )
            copy_revision = next(
                line for line in copy_result.stdout.splitlines() if line.startswith("Committed revision ")
            ).removeprefix("Committed revision ").removesuffix(".")
            self._run(["svn", "propset", "--revprop", "-r", copy_revision, "svn:date", date_cursor.next(), repo.repo_url])

            branch_wc = branches_root / branch_name
            self._checkout(repo.repo_url, f"{repo.repo_url}/branches/{branch_name}", branch_wc)
            branch_file = branch_wc / "src" / f"feature_{feature_index:03d}.py"

            for commit_index in range(1, COMMITS_PER_FEATURE_BRANCH + 1):
                branch_file.write_text(self._feature_file_content(feature_index, commit_index), encoding="utf-8")
                branch_revision_id = self._commit_path(
                    branch_wc,
                    f"us14-f{feature_index:03d}-c{commit_index:02d}",
                    date_cursor.next(),
                    repo.repo_url,
                )

            current_batch.append((feature_index, branch_revision_id))
            if len(current_batch) == INTEGRATION_BATCH_SIZE:
                integration_batches.append(current_batch)
                current_batch = []

        if current_batch:
            integration_batches.append(current_batch)

        for batch_index, batch in enumerate(integration_batches):
            protocol_details: list[dict] = []
            for feature_index, _branch_revision_id in batch:
                trunk_file = repo.working_copy_dir / "trunk" / "src" / f"feature_{feature_index:03d}.py"
                branch_file_url = f"{repo.repo_url}/branches/feature-{feature_index:03d}/src/feature_{feature_index:03d}.py"
                trunk_file.write_text(self._run(["svn", "cat", branch_file_url]), encoding="utf-8")
                protocol_details.append(
                    self._protocol_detail(
                        f"trunk/src/feature_{feature_index:03d}.py",
                        self._feature_ratio(feature_index),
                    )
                )

            integration_revision_id = repo.commit_all(
                f"us14-integrate-{batch_index:02d}",
                date_cursor.next(),
            )
            integration_revision_ids.append(integration_revision_id)
            write_revision_protocol(
                protocol_dir,
                self._protocol(details=protocol_details),
                repo.repo_dir,
                integration_revision_id,
                repo_url_override=repo.repo_url,
            )

        repo.write("trunk/README.md", "us14 docs update\n")
        repo.add("trunk/README.md")
        end_revision_id = repo.commit_all("us14-final-docs", date_cursor.next())

        branch_entries = [line for line in self._run(["svn", "ls", f"{repo.repo_url}/branches"]).splitlines() if line.endswith("/")]
        branch_count = len(branch_entries)
        commit_count = int(end_revision_id)
        return repo, protocol_dir, end_revision_id, integration_revision_ids, branch_count, commit_count

    def test_build_result_matches_expected_result_for_production_scale_svn_repo(self) -> None:
        query = self._query()
        expected_result = self._expected_result()

        with tempfile.TemporaryDirectory() as temp_dir:
            repo, protocol_dir, end_revision_id, integration_revision_ids, branch_count, commit_count = self._build_repo(Path(temp_dir))

            self.assertGreaterEqual(branch_count, 100)
            self.assertGreaterEqual(commit_count, 1000)

            counting_provider = _CountingProvider(
                aggregateGenCodeDesc.GenCodeDescSetDirProvider(
                    protocol_dir,
                    False,
                    aggregateGenCodeDesc.RuntimeLogger("quiet"),
                )
            )
            args = Namespace(
                repoURL=repo.repo_url,
                repoBranch=query["repoBranch"],
                startTime=query["startTime"],
                endTime=query["endTime"],
                vcsType=query["vcsType"],
                algorithm=query["algorithm"],
                scope=query["scope"],
                outputFile=None,
                outputFormat="json",
                metadataSource="genCodeDesc",
                genCodeDescSetDir=str(protocol_dir),
                workingDir=None,
                failOnMissingProtocol=False,
                includeBreakdown="none",
                logLevel="quiet",
            )

            with patch.object(aggregateGenCodeDesc, "build_gen_code_desc_provider", return_value=counting_provider):
                actual_result = aggregateGenCodeDesc.build_result(args)

            expected_result["REPOSITORY"]["repoURL"] = repo.repo_url
            expected_result["REPOSITORY"]["revisionId"] = end_revision_id
            self.assertEqual(actual_result, expected_result)

            call_counts = Counter(counting_provider.calls)
            self.assertEqual(set(call_counts), set(integration_revision_ids))
            self.assertEqual(len(call_counts), len(integration_revision_ids))
            self.assertTrue(all(count == 1 for count in call_counts.values()))


if __name__ == "__main__":
    unittest.main()