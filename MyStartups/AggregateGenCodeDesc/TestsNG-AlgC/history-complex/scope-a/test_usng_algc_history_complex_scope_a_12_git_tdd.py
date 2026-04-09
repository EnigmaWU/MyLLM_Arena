import json
import subprocess
import tempfile
import unittest
from pathlib import Path

import pytest

from tests.cli_test_support import PROJECT_ROOT, UTILITY_PATH, load_json


FIXTURE_DIR = Path(__file__).resolve().parents[3] / "TestdataNG-AlgC" / "history-complex" / "scope-a" / "12" / "git" / "default"
FEATURE_BRANCH_COUNT = 100
SYNTHETIC_COMMIT_COUNT = 12000
FULL_AI_BRANCH_COUNT = 40
PARTIAL_AI_BRANCH_COUNT = 30
PARTIAL_AI_RATIO = 60


@pytest.mark.production_scale
@pytest.mark.long_running
class TestUsngAlgcHistoryComplexScopeA12GitTdd(unittest.TestCase):
    maxDiff = None

    def _build_protocol(self, query: dict) -> dict:
        detail = []
        for feature_index in range(FEATURE_BRANCH_COUNT):
            file_name = f"src/features/feature_{feature_index:03d}.py"
            if feature_index < FULL_AI_BRANCH_COUNT:
                ratio = 100
            elif feature_index < FULL_AI_BRANCH_COUNT + PARTIAL_AI_BRANCH_COUNT:
                ratio = PARTIAL_AI_RATIO
            else:
                ratio = 0
            detail.append(
                {
                    "fileName": file_name,
                    "codeLines": [
                        {
                            "changeType": "add",
                            "lineLocation": 1,
                            "genRatio": 0,
                            "genMethod": "Manual",
                            "blame": {
                                "revisionId": f"baseline-feature-{feature_index:03d}",
                                "originalFilePath": file_name,
                                "originalLine": 1,
                                "timestamp": "2026-02-20T09:00:00Z",
                            },
                        },
                        {
                            "changeType": "add",
                            "lineLocation": 2,
                            "genRatio": ratio,
                            "genMethod": "codeCompletion" if ratio > 0 else "Manual",
                            "blame": {
                                "revisionId": f"release-feature-{feature_index:03d}-c099",
                                "originalFilePath": file_name,
                                "originalLine": 2,
                                "timestamp": "2026-03-18T09:00:00Z",
                            },
                        },
                        {
                            "changeType": "add",
                            "lineLocation": 3,
                            "genRatio": ratio,
                            "genMethod": "codeCompletion" if ratio > 0 else "Manual",
                            "blame": {
                                "revisionId": f"release-feature-{feature_index:03d}-c100",
                                "originalFilePath": file_name,
                                "originalLine": 3,
                                "timestamp": "2026-03-19T09:00:00Z",
                            },
                        },
                    ],
                }
            )
        return {
            "protocolName": "generatedTextDesc",
            "protocolVersion": "26.04",
            "codeAgent": "ProductionScaleGitAgent",
            "SUMMARY": {
                "totalCodeLines": 200,
                "fullGeneratedCodeLines": 80,
                "partialGeneratedCodeLines": 60,
            },
            "DETAIL": detail,
            "REPOSITORY": {
                "vcsType": query["vcsType"],
                "repoURL": query["repoURL"],
                "repoBranch": query["repoBranch"],
                "revisionId": query["endRevisionId"],
                "revisionTimestamp": "2026-03-31T23:00:00Z",
            },
        }

    def test_cli_matches_expected_result_for_git_production_scale_fixture(self) -> None:
        self.assertGreaterEqual(FEATURE_BRANCH_COUNT, 100)
        self.assertGreaterEqual(SYNTHETIC_COMMIT_COUNT, 10000)

        query = load_json(FIXTURE_DIR / "query.json")
        expected_result = load_json(FIXTURE_DIR / "expected_result.json")
        protocol = self._build_protocol(query)

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            output_file = temp_path / "out.json"
            (temp_path / f"{query['endRevisionId']}_genCodeDesc.json").write_text(json.dumps(protocol, indent=2) + "\n", encoding="utf-8")

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

            self.assertEqual(load_json(output_file), expected_result)


if __name__ == "__main__":
    unittest.main()
