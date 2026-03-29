import unittest
from argparse import Namespace
from pathlib import Path
from unittest.mock import patch

import aggregateGenCodeDesc


class _ProviderStub:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def get_revision_metadata(self, repo_url: str, repo_branch: str, revision_id: str, vcs_type: str) -> dict:
        self.calls.append(revision_id)
        return {
            "DETAIL": [
                {
                    "fileName": "src/calc.py",
                    "codeLines": [
                        {"lineLocation": 1, "genRatio": 100},
                        {"lineLocation": 2, "genRatio": 60},
                    ],
                }
            ]
        }


class TestUs11DeepHistoryScalabilityTdd(unittest.TestCase):
    maxDiff = None

    def test_build_result_reuses_commit_time_lookup_per_origin_revision(self) -> None:
        args = Namespace(
            repoURL="/virtual/repo",
            repoBranch="main",
            startTime="2026-03-01",
            endTime="2026-03-31",
            vcsType="git",
            model="A",
            scope="A",
            outputFile=None,
            outputFormat="json",
            metadataSource="genCodeDesc",
            genCodeDescSetDir=None,
            workingDir="/virtual/repo",
            failOnMissingProtocol=False,
            includeBreakdown="none",
            logLevel="quiet",
        )
        provider = _ProviderStub()
        commit_show_calls: list[list[str]] = []

        def fake_run_git(repo_dir: Path, git_args: list[str]) -> str:
            if git_args[:2] == ["rev-list", "-1"]:
                return "end-revision"
            if git_args[:3] == ["ls-tree", "-r", "--name-only"]:
                return "src/calc.py"
            if git_args[:3] == ["show", "-s", "--format=%cI"]:
                commit_show_calls.append(git_args)
                return "2026-03-10T09:00:00+00:00"
            raise AssertionError(f"Unexpected git invocation: {git_args}")

        blame_lines = [
            aggregateGenCodeDesc.BlameLine(
                revision_id="rev-1",
                origin_file="src/calc.py",
                origin_line=1,
                final_line=1,
                content="line_one = ai()",
            ),
            aggregateGenCodeDesc.BlameLine(
                revision_id="rev-1",
                origin_file="src/calc.py",
                origin_line=2,
                final_line=2,
                content="line_two = mixed()",
            ),
        ]

        with patch.object(aggregateGenCodeDesc, "build_gen_code_desc_provider", return_value=provider), patch.object(
            aggregateGenCodeDesc, "run_git", side_effect=fake_run_git
        ), patch.object(aggregateGenCodeDesc, "list_source_files", return_value=["src/calc.py"]), patch.object(
            aggregateGenCodeDesc, "parse_blame", return_value=blame_lines
        ):
            result = aggregateGenCodeDesc.build_result(args)

        self.assertEqual(len(commit_show_calls), 1)
        self.assertEqual(provider.calls, ["rev-1"])
        self.assertEqual(
            result,
            {
                "protocolName": "generatedTextDesc",
                "protocolVersion": "26.03",
                "SUMMARY": {
                    "totalCodeLines": 2,
                    "fullGeneratedCodeLines": 1,
                    "partialGeneratedCodeLines": 1,
                },
                "REPOSITORY": {
                    "vcsType": "git",
                    "repoURL": "/virtual/repo",
                    "repoBranch": "main",
                    "revisionId": "end-revision",
                },
            },
        )


if __name__ == "__main__":
    unittest.main()