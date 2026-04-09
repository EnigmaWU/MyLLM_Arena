import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from tests.cli_test_support import PROJECT_ROOT, UTILITY_PATH, load_json


FIXTURE_GIT_DIR = Path(__file__).resolve().parents[3] / "TestdataNG-AlgC" / "history-complex" / "scope-a" / "10" / "git" / "default"
FIXTURE_SVN_DIR = Path(__file__).resolve().parents[3] / "TestdataNG-AlgC" / "history-complex" / "scope-a" / "10" / "svn" / "default"


class TestUsngAlgcHistoryComplexScopeA10Tdd(unittest.TestCase):
    maxDiff = None

    def _build_protocol(self, query: dict) -> dict:
        file_name = "src/deep_history.py"
        revision_ids = {
            "git": ["algc-us10-git-r0100", "algc-us10-git-r7800", "algc-us10-git-r8500", "algc-us10-git-r9200", "algc-us10-git-r9999"],
            "svn": ["r0100", "r7800", "r8500", "r9200", "r9999"],
        }
        base = revision_ids[query["vcsType"]]
        return {
            "protocolName": "generatedTextDesc",
            "protocolVersion": "26.04",
            "codeAgent": "DeepHistoryAgent",
            "SUMMARY": {
                "totalCodeLines": 4,
                "fullGeneratedCodeLines": 1,
                "partialGeneratedCodeLines": 1,
            },
            "DETAIL": [
                {
                    "fileName": file_name,
                    "codeLines": [
                        {
                            "changeType": "add",
                            "lineLocation": 1,
                            "genRatio": 0,
                            "genMethod": "Manual",
                            "blame": {
                                "revisionId": base[0],
                                "originalFilePath": file_name,
                                "originalLine": 1,
                                "timestamp": "2026-01-01T09:00:00Z",
                            },
                        },
                        {
                            "changeType": "add",
                            "lineLocation": 2,
                            "genRatio": 0,
                            "genMethod": "Manual",
                            "blame": {
                                "revisionId": base[1],
                                "originalFilePath": file_name,
                                "originalLine": 2,
                                "timestamp": "2026-03-05T09:00:00Z",
                            },
                        },
                        {
                            "changeType": "add",
                            "lineLocation": 3,
                            "genRatio": 60,
                            "genMethod": "codeCompletion",
                            "blame": {
                                "revisionId": base[2],
                                "originalFilePath": file_name,
                                "originalLine": 3,
                                "timestamp": "2026-03-10T09:00:00Z",
                            },
                        },
                        {
                            "changeType": "add",
                            "lineLocation": 4,
                            "genRatio": 0,
                            "genMethod": "Manual",
                            "blame": {
                                "revisionId": base[3],
                                "originalFilePath": file_name,
                                "originalLine": 4,
                                "timestamp": "2026-03-22T09:00:00Z",
                            },
                        },
                        {
                            "changeType": "add",
                            "lineLocation": 5,
                            "genRatio": 100,
                            "genMethod": "codeCompletion",
                            "blame": {
                                "revisionId": base[4],
                                "originalFilePath": file_name,
                                "originalLine": 5,
                                "timestamp": "2026-03-28T09:00:00Z",
                            },
                        },
                    ],
                }
            ],
            "REPOSITORY": {
                "vcsType": query["vcsType"],
                "repoURL": query["repoURL"],
                "repoBranch": query["repoBranch"],
                "revisionId": query["endRevisionId"],
                "revisionTimestamp": "2026-03-31T09:00:00Z",
            },
        }

    def _run_cli(self, fixture_dir: Path) -> dict:
        query = load_json(fixture_dir / "query.json")
        protocol = self._build_protocol(query)

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            output_file = temp_path / "out.json"
            protocol_path = temp_path / f"{query['endRevisionId']}_genCodeDesc.json"
            protocol_path.write_text(json.dumps(protocol, indent=2) + "\n", encoding="utf-8")

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
                    "C",
                    "--scope",
                    query["scope"],
                    "--outputFile",
                    str(output_file),
                    "--genCodeDescSetDir",
                    str(temp_path),
                ],
                cwd=PROJECT_ROOT,
                text=True,
                capture_output=True,
                check=True,
            )
            return load_json(output_file)

    def test_cli_matches_git_expected_result_for_deep_history(self) -> None:
        expected_result = load_json(FIXTURE_GIT_DIR / "expected_result.json")
        actual_result = self._run_cli(FIXTURE_GIT_DIR)
        self.assertEqual(actual_result, expected_result)

    def test_cli_matches_svn_expected_result_for_deep_history(self) -> None:
        expected_result = load_json(FIXTURE_SVN_DIR / "expected_result.json")
        actual_result = self._run_cli(FIXTURE_SVN_DIR)
        self.assertEqual(actual_result, expected_result)


if __name__ == "__main__":
    unittest.main()
