import unittest
from argparse import Namespace
from unittest.mock import patch

import aggregateGenCodeDesc


class _ProviderStub:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def get_revision_metadata(self, repo_url: str, repo_branch: str, revision_id: str, vcs_type: str) -> dict:
        self.calls.append(revision_id)
        if revision_id == "5":
            return {
                "DETAIL": [
                    {"fileName": "branches/feature-alpha/src/alpha.py", "codeLines": [{"lineLocation": 2, "genRatio": 100}]},
                    {"fileName": "branches/feature-alpha/src/beta.py", "codeLines": [{"lineLocation": 2, "genRatio": 70}]},
                ]
            }
        if revision_id == "7":
            return {
                "DETAIL": [
                    {"fileName": "branches/feature-gamma/src/gamma.py", "codeLines": [{"lineLocation": 2, "genRatio": 40}]},
                ]
            }
        raise AssertionError(f"Unexpected revision lookup: {revision_id}")


class TestUs12SvnMergedBranchScalabilityTdd(unittest.TestCase):
    maxDiff = None

    def test_build_result_reuses_svn_revision_lookups_for_shared_branch_origins(self) -> None:
        args = Namespace(
            repoURL="file:///virtual/repo",
            repoBranch="trunk",
            startTime="2026-03-01",
            endTime="2026-03-31",
            vcsType="svn",
            model="A",
            scope="A",
            outputFile=None,
            outputFormat="json",
            metadataSource="genCodeDesc",
            genCodeDescSetDir=None,
            workingDir=None,
            failOnMissingProtocol=False,
            includeBreakdown="none",
            logLevel="quiet",
        )
        provider = _ProviderStub()
        revision_log_calls: list[str] = []
        index_build_inputs: list[dict] = []

        def fake_run_svn(svn_args: list[str]) -> str:
            if svn_args[:3] == ["log", "--xml", "-r"]:
                revision_id = svn_args[3]
                revision_log_calls.append(revision_id)
                return (
                    '<?xml version="1.0" encoding="UTF-8"?>\n'
                    f'<log><logentry revision="{revision_id}"><date>2026-03-10T09:00:00.000000Z</date></logentry></log>'
                )
            raise AssertionError(f"Unexpected svn invocation: {svn_args}")

        blame_by_file = {
            "src/alpha.py": [aggregateGenCodeDesc.BlameLine("5", "branches/feature-alpha/src/alpha.py", 2, 2, "alpha = ai()")],
            "src/beta.py": [aggregateGenCodeDesc.BlameLine("5", "branches/feature-alpha/src/beta.py", 2, 2, "beta = partial()")],
            "src/gamma.py": [aggregateGenCodeDesc.BlameLine("7", "branches/feature-gamma/src/gamma.py", 2, 2, "gamma = partial()")],
        }

        original_build_protocol_index = aggregateGenCodeDesc.build_protocol_index

        def counting_build_protocol_index(protocol: dict) -> dict:
            index_build_inputs.append(protocol)
            return original_build_protocol_index(protocol)

        with patch.object(aggregateGenCodeDesc, "build_gen_code_desc_provider", return_value=provider), patch.object(
            aggregateGenCodeDesc, "resolve_svn_end_revision", return_value="end-revision"
        ), patch.object(
            aggregateGenCodeDesc, "list_svn_source_files", return_value=["src/alpha.py", "src/beta.py", "src/gamma.py"]
        ), patch.object(
            aggregateGenCodeDesc,
            "parse_svn_blame",
            side_effect=lambda repo_url, branch, revision_id, relative_path: blame_by_file[relative_path],
        ), patch.object(
            aggregateGenCodeDesc, "run_svn", side_effect=fake_run_svn
        ), patch.object(
            aggregateGenCodeDesc, "build_protocol_index", side_effect=counting_build_protocol_index
        ):
            result = aggregateGenCodeDesc.build_result(args)

        self.assertEqual(provider.calls, ["5", "7"])
        self.assertEqual(len(index_build_inputs), 2)
        self.assertEqual(revision_log_calls.count("5"), 1)
        self.assertEqual(revision_log_calls.count("7"), 1)
        self.assertEqual(
            result,
            {
                "protocolName": "generatedTextDesc",
                "protocolVersion": "26.03",
                "SUMMARY": {
                    "totalCodeLines": 3,
                    "fullGeneratedCodeLines": 1,
                    "partialGeneratedCodeLines": 2,
                },
                "REPOSITORY": {
                    "vcsType": "svn",
                    "repoURL": "file:///virtual/repo",
                    "repoBranch": "trunk",
                    "revisionId": "end-revision",
                },
            },
        )


if __name__ == "__main__":
    unittest.main()