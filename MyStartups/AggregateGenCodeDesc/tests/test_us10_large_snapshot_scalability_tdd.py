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
        if revision_id == "rev-a":
            return {
                "DETAIL": [
                    {"fileName": "src/a.py", "codeLines": [{"lineLocation": 2, "genRatio": 100}]},
                    {"fileName": "src/b.py", "codeLines": [{"lineLocation": 2, "genRatio": 60}]},
                ]
            }
        if revision_id == "rev-b":
            return {
                "DETAIL": [
                    {"fileName": "src/c.py", "codeLines": [{"lineLocation": 2, "genRatio": 100}]},
                    {"fileName": "src/d.py", "codeLines": []},
                ]
            }
        raise AssertionError(f"Unexpected revision lookup: {revision_id}")


class TestUs10LargeSnapshotScalabilityTdd(unittest.TestCase):
    maxDiff = None

    def test_build_result_reuses_protocol_index_per_origin_revision(self) -> None:
        args = Namespace(
            repoURL="/virtual/repo",
            repoBranch="main",
            startTime="2026-03-01",
            endTime="2026-03-31",
            vcsType="git",
            algorithm="A",
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
        index_build_inputs: list[dict] = []

        def fake_run_git(repo_dir: Path, git_args: list[str]) -> str:
            if git_args[:2] == ["rev-list", "-1"]:
                return "end-revision"
            if git_args[:3] == ["show", "-s", "--format=%cI"]:
                commit_show_calls.append(git_args)
                return "2026-03-10T09:00:00+00:00"
            raise AssertionError(f"Unexpected git invocation: {git_args}")

        blame_by_file = {
            "src/a.py": [
                aggregateGenCodeDesc.BlameLine("rev-a", "src/a.py", 2, 2, "value = ai()"),
            ],
            "src/b.py": [
                aggregateGenCodeDesc.BlameLine("rev-a", "src/b.py", 2, 2, "value = mixed()"),
            ],
            "src/c.py": [
                aggregateGenCodeDesc.BlameLine("rev-b", "src/c.py", 2, 2, "value = ai_again()"),
            ],
            "src/d.py": [
                aggregateGenCodeDesc.BlameLine("rev-b", "src/d.py", 2, 2, "value = human()"),
            ],
        }

        original_build_protocol_index = aggregateGenCodeDesc.build_protocol_index

        def counting_build_protocol_index(protocol: dict) -> dict:
            index_build_inputs.append(protocol)
            return original_build_protocol_index(protocol)

        with patch.object(aggregateGenCodeDesc, "build_gen_code_desc_provider", return_value=provider), patch.object(
            aggregateGenCodeDesc, "run_git", side_effect=fake_run_git
        ), patch.object(
            aggregateGenCodeDesc, "list_source_files", return_value=["src/a.py", "src/b.py", "src/c.py", "src/d.py"]
        ), patch.object(
            aggregateGenCodeDesc,
            "parse_blame",
            side_effect=lambda repo_dir, revision_id, relative_path: blame_by_file[relative_path],
        ), patch.object(
            aggregateGenCodeDesc, "build_protocol_index", side_effect=counting_build_protocol_index
        ):
            result = aggregateGenCodeDesc.build_result(args)

        self.assertEqual(provider.calls, ["rev-a", "rev-b"])
        self.assertEqual(len(index_build_inputs), 2)
        self.assertEqual(len(commit_show_calls), 2)
        self.assertEqual(
            result,
            {
                "protocolName": "generatedTextDesc",
                "protocolVersion": "26.03",
                "SUMMARY": {
                    "totalCodeLines": 4,
                    "fullGeneratedCodeLines": 2,
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