import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from tests.cli_test_support import PROJECT_ROOT, UTILITY_PATH, load_json


FIXTURE_GIT_DIR = Path(__file__).resolve().parents[3] / "TestdataNG-AlgC" / "history-complex" / "scope-a" / "09" / "git" / "default"
FIXTURE_SVN_DIR = Path(__file__).resolve().parents[3] / "TestdataNG-AlgC" / "history-complex" / "scope-a" / "09" / "svn" / "default"
FILE_COUNT = 60
FILES_PER_BUCKET = 20


class TestUsngAlgcHistoryComplexScopeA09Tdd(unittest.TestCase):
    maxDiff = None

    def _file_name(self, file_index: int) -> str:
        if file_index < FILE_COUNT // 3:
            return f"src/bulk/core/module_{file_index:03d}.py"
        if file_index < (2 * FILE_COUNT) // 3:
            return f"src/bulk/services/module_{file_index:03d}.py"
        return f"src/bulk/utils/module_{file_index:03d}.py"

    def _build_protocols(self, query: dict) -> list[dict]:
        baseline_detail = []
        end_detail = []
        for file_index in range(FILE_COUNT):
            file_name = self._file_name(file_index)
            if file_index < FILES_PER_BUCKET:
                ratio = 100
            elif file_index < FILES_PER_BUCKET * 2:
                ratio = 60
            else:
                ratio = 0

            baseline_detail.append(
                {
                    "fileName": file_name,
                    "codeLines": [
                        {
                            "changeType": "add",
                            "lineLocation": 1,
                            "genRatio": 0,
                            "genMethod": "Manual",
                            "blame": {
                                "revisionId": "baseline-r0",
                                "originalFilePath": file_name,
                                "originalLine": 1,
                                "timestamp": "2026-02-20T09:00:00Z",
                            },
                        },
                        {
                            "changeType": "add",
                            "lineLocation": 2,
                            "genRatio": 0,
                            "genMethod": "Manual",
                            "blame": {
                                "revisionId": "baseline-r0",
                                "originalFilePath": file_name,
                                "originalLine": 2,
                                "timestamp": "2026-02-20T09:00:00Z",
                            },
                        },
                        {
                            "changeType": "add",
                            "lineLocation": 3,
                            "genRatio": 0,
                            "genMethod": "Manual",
                            "blame": {
                                "revisionId": "baseline-r0",
                                "originalFilePath": file_name,
                                "originalLine": 3,
                                "timestamp": "2026-02-20T09:00:00Z",
                            },
                        },
                        {
                            "changeType": "add",
                            "lineLocation": 4,
                            "genRatio": 0,
                            "genMethod": "Manual",
                            "blame": {
                                "revisionId": "baseline-r0",
                                "originalFilePath": file_name,
                                "originalLine": 4,
                                "timestamp": "2026-02-20T09:00:00Z",
                            },
                        },
                    ],
                }
            )

            end_detail.append(
                {
                    "fileName": file_name,
                    "codeLines": [
                        {
                            "changeType": "delete",
                            "lineLocation": 2,
                            "genRatio": 0,
                            "genMethod": "Manual",
                            "blame": {
                                "revisionId": "baseline-r0",
                                "originalFilePath": file_name,
                                "originalLine": 2,
                                "timestamp": "2026-02-20T09:00:00Z",
                            },
                        },
                        {
                            "changeType": "add",
                            "lineLocation": 2,
                            "genRatio": ratio,
                            "genMethod": "codeCompletion" if ratio > 0 else "Manual",
                            "blame": {
                                "revisionId": f"feature-r{file_index:03d}",
                                "originalFilePath": file_name,
                                "originalLine": 2,
                                "timestamp": "2026-03-10T09:00:00Z",
                            },
                        },
                        {
                            "changeType": "delete",
                            "lineLocation": 4,
                            "genRatio": 0,
                            "genMethod": "Manual",
                            "blame": {
                                "revisionId": "baseline-r0",
                                "originalFilePath": file_name,
                                "originalLine": 4,
                                "timestamp": "2026-02-20T09:00:00Z",
                            },
                        },
                        {
                            "changeType": "add",
                            "lineLocation": 4,
                            "genRatio": 0,
                            "genMethod": "Manual",
                            "blame": {
                                "revisionId": f"stabilize-r{file_index:03d}",
                                "originalFilePath": file_name,
                                "originalLine": 4,
                                "timestamp": "2026-03-12T09:00:00Z",
                            },
                        },
                    ],
                }
            )

        return [
            {
                "protocolName": "generatedTextDesc",
                "protocolVersion": "26.04",
                "codeAgent": "ScaleBaselineAgent",
                "SUMMARY": {
                    "totalCodeLines": FILE_COUNT * 4,
                    "fullGeneratedCodeLines": 0,
                    "partialGeneratedCodeLines": 0,
                },
                "DETAIL": baseline_detail,
                "REPOSITORY": {
                    "vcsType": query["vcsType"],
                    "repoURL": query["repoURL"],
                    "repoBranch": query["repoBranch"],
                    "revisionId": "algc-us09-baseline-r0",
                    "revisionTimestamp": "2026-02-20T09:00:00Z",
                },
            },
            {
                "protocolName": "generatedTextDesc",
                "protocolVersion": "26.04",
                "codeAgent": "ScaleAgent",
                "SUMMARY": {
                    "totalCodeLines": FILE_COUNT * 2,
                    "fullGeneratedCodeLines": 20,
                    "partialGeneratedCodeLines": 20,
                },
                "DETAIL": end_detail,
                "REPOSITORY": {
                    "vcsType": query["vcsType"],
                    "repoURL": query["repoURL"],
                    "repoBranch": query["repoBranch"],
                    "revisionId": query["endRevisionId"],
                    "revisionTimestamp": "2026-03-25T09:00:00Z",
                },
            },
        ]

    def _run_cli(self, fixture_dir: Path) -> dict:
        query = load_json(fixture_dir / "query.json")
        protocols = self._build_protocols(query)

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            output_file = temp_path / "out.json"
            for protocol in protocols:
                protocol_path = temp_path / f"{protocol['REPOSITORY']['revisionId']}_genCodeDesc.json"
                protocol_path.write_text(json.dumps(protocol, indent=2) + "\n", encoding="utf-8")

            subprocess.run(
                [
                    "python3",
                    str(UTILITY_PATH),
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

    def test_cli_matches_git_expected_result_for_large_file_set(self) -> None:
        expected_result = load_json(FIXTURE_GIT_DIR / "expected_result.json")
        actual_result = self._run_cli(FIXTURE_GIT_DIR)
        self.assertEqual(actual_result, expected_result)

    def test_cli_matches_svn_expected_result_for_large_file_set(self) -> None:
        expected_result = load_json(FIXTURE_SVN_DIR / "expected_result.json")
        actual_result = self._run_cli(FIXTURE_SVN_DIR)
        self.assertEqual(actual_result, expected_result)


if __name__ == "__main__":
    unittest.main()
