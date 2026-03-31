import tempfile
import unittest
from argparse import Namespace
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import aggregateGenCodeDesc
import pytest
from tests.cli_test_support import GitRepoHarness, load_json, write_revision_protocol


FIXTURE_DIR = Path(__file__).resolve().parent.parent / "testdata" / "us13_git_production_scale_local_repo"
FEATURE_BRANCH_COUNT = 100
COMMITS_PER_FEATURE_BRANCH = 10
FULL_AI_BRANCH_COUNT = 40
PARTIAL_AI_BRANCH_COUNT = 30
PARTIAL_AI_RATIO = 60


class _DateCursor:
    def __init__(self, start: datetime):
        self.current = start

    def next(self) -> str:
        value = self.current
        self.current += timedelta(minutes=1)
        return value.strftime("%Y-%m-%dT%H:%M:%SZ")


class _CountingProvider(aggregateGenCodeDesc.GenCodeDescProvider):
    def __init__(self, inner: aggregateGenCodeDesc.GenCodeDescProvider):
        self.inner = inner
        self.calls: list[str] = []

    def get_revision_metadata(self, repo_url: str, repo_branch: str, revision_id: str, vcs_type: str) -> dict:
        self.calls.append(revision_id)
        return self.inner.get_revision_metadata(repo_url, repo_branch, revision_id, vcs_type)


@pytest.mark.production_scale
@pytest.mark.long_running
class TestUs13GitProductionScaleLocalRepoTdd(unittest.TestCase):
    maxDiff = None

    def _query(self) -> dict:
        return load_json(FIXTURE_DIR / "query.json")

    def _expected_result(self) -> dict:
        return load_json(FIXTURE_DIR / "expected_result.json")

    def _feature_ratio(self, feature_index: int) -> int:
        if feature_index < FULL_AI_BRANCH_COUNT:
            return 100
        if feature_index < FULL_AI_BRANCH_COUNT + PARTIAL_AI_BRANCH_COUNT:
            return PARTIAL_AI_RATIO
        return 0

    def _protocol(self, *, repo_branch: str, file_name: str, ratio: int) -> dict:
        code_lines = []
        full_generated_code_lines = 0
        partial_generated_code_lines = 0

        if ratio > 0:
            code_lines = [
                {"lineLocation": 2, "genRatio": ratio, "genMethod": "codeCompletion"},
                {"lineLocation": 3, "genRatio": ratio, "genMethod": "codeCompletion"},
            ]
            if ratio == 100:
                full_generated_code_lines = 2
            else:
                partial_generated_code_lines = 2

        return {
            "protocolName": "generatedTextDesc",
            "protocolVersion": "26.03",
            "codeAgent": "US13ScaleAgent",
            "SUMMARY": {
                "totalCodeLines": len(code_lines),
                "fullGeneratedCodeLines": full_generated_code_lines,
                "partialGeneratedCodeLines": partial_generated_code_lines,
            },
            "DETAIL": [
                {
                    "fileName": file_name,
                    "codeLines": code_lines,
                }
            ],
            "REPOSITORY": {
                "vcsType": "git",
                "repoURL": "placeholder",
                "repoBranch": repo_branch,
                "revisionId": "placeholder",
            },
        }

    def _feature_file_content(self, feature_index: int, commit_index: int) -> str:
        return (
            f"# feature {feature_index:03d}\n"
            f"feature_value_a = {feature_index} + {commit_index}\n"
            f"feature_value_b = {feature_index} + {commit_index} * 2\n"
        )

    def _build_repo(self, root_dir: Path) -> tuple[Path, Path, str, list[str], int, int]:
        repo_dir = root_dir / "repo"
        protocol_dir = root_dir / "protocols"
        repo_dir.mkdir()
        protocol_dir.mkdir()

        repo = GitRepoHarness(repo_dir)
        for feature_index in range(FEATURE_BRANCH_COUNT):
            repo.write(
                f"src/features/feature_{feature_index:03d}.py",
                f"# feature {feature_index:03d}\n"
                f"feature_value_a = {feature_index} + 0\n"
                f"feature_value_b = {feature_index} + 0\n",
            )
        repo.commit_all("us13-base", "2026-02-20T09:00:00Z")

        date_cursor = _DateCursor(datetime(2026, 3, 1, 0, 0, tzinfo=timezone.utc))
        feature_tip_ids: list[str] = []

        for feature_index in range(FEATURE_BRANCH_COUNT):
            branch_name = f"feature-{feature_index:03d}"
            file_name = f"src/features/feature_{feature_index:03d}.py"
            repo.checkout("main")
            repo.checkout_new_branch(branch_name)

            revision_id = ""
            for commit_index in range(1, COMMITS_PER_FEATURE_BRANCH + 1):
                repo.write(file_name, self._feature_file_content(feature_index, commit_index))
                revision_id = repo.commit_all(
                    f"us13-f{feature_index:03d}-c{commit_index:02d}",
                    date_cursor.next(),
                )

            feature_tip_ids.append(revision_id)
            write_revision_protocol(
                protocol_dir,
                self._protocol(
                    repo_branch=branch_name,
                    file_name=file_name,
                    ratio=self._feature_ratio(feature_index),
                ),
                repo_dir,
                revision_id,
            )

        repo.checkout("main")
        repo.checkout_new_branch("release")

        for group_index in range(5):
            integration_branch_name = f"integration-{group_index:02d}"
            repo.checkout("release")
            repo.checkout_new_branch(integration_branch_name)
            start_index = group_index * 10
            for feature_index in range(start_index, start_index + 10):
                repo.merge_no_ff(
                    f"feature-{feature_index:03d}",
                    f"us13-int-{group_index:02d}-merge-{feature_index:03d}",
                    date_cursor.next(),
                )
            repo.checkout("release")
            repo.merge_no_ff(
                integration_branch_name,
                f"us13-release-from-int-{group_index:02d}",
                date_cursor.next(),
            )

        for octopus_group_index in range(5):
            start_index = 50 + (octopus_group_index * 5)
            repo.checkout("release")
            repo.merge_octopus(
                [f"feature-{feature_index:03d}" for feature_index in range(start_index, start_index + 5)],
                f"us13-release-octopus-{octopus_group_index:02d}",
                date_cursor.next(),
            )

        for feature_index in range(75, 100):
            repo.checkout("release")
            repo.merge_no_ff(
                f"feature-{feature_index:03d}",
                f"us13-release-direct-{feature_index:03d}",
                date_cursor.next(),
            )

        repo.checkout("main")
        end_revision_id = repo.merge_no_ff("release", "us13-main-final", date_cursor.next())

        branch_count = len(repo._run(["git", "branch", "--format=%(refname:short)"]).splitlines())
        commit_count = int(repo._run(["git", "rev-list", "--count", "--all"]))
        return repo_dir, protocol_dir, end_revision_id, feature_tip_ids, branch_count, commit_count

    def test_build_result_matches_expected_result_for_production_scale_git_repo(self) -> None:
        query = self._query()
        expected_result = self._expected_result()

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_dir, protocol_dir, end_revision_id, feature_tip_ids, branch_count, commit_count = self._build_repo(Path(temp_dir))

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
                repoURL=str(repo_dir),
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
                workingDir=str(repo_dir),
                failOnMissingProtocol=False,
                includeBreakdown="none",
                logLevel="quiet",
            )

            with patch.object(aggregateGenCodeDesc, "build_gen_code_desc_provider", return_value=counting_provider):
                actual_result = aggregateGenCodeDesc.build_result(args)

            expected_result["REPOSITORY"]["repoURL"] = str(repo_dir)
            expected_result["REPOSITORY"]["revisionId"] = end_revision_id
            self.assertEqual(actual_result, expected_result)

            call_counts = Counter(counting_provider.calls)
            self.assertEqual(set(call_counts), set(feature_tip_ids))
            self.assertEqual(len(call_counts), FEATURE_BRANCH_COUNT)
            self.assertTrue(all(count == 1 for count in call_counts.values()))


if __name__ == "__main__":
    unittest.main()