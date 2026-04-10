import json
import re
import subprocess
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from tests.cli_test_support import PROJECT_ROOT, UTILITY_PATH, build_query_args_cli_args, load_json


FIXTURE_DIR = Path(__file__).resolve().parents[3] / "TestdataNG-AlgC" / "history-complex" / "scope-a" / "13" / "svn" / "default"
FEATURE_BRANCH_COUNT = 100
BASELINE_REVISION_NUMBER = 2000
FINAL_REVISION_NUMBER = 12000
TOTAL_SYNTHETIC_COMMITS = FINAL_REVISION_NUMBER - BASELINE_REVISION_NUMBER + 1
TARGET_LINE_COUNT = FEATURE_BRANCH_COUNT * 2
REWRITES_PER_TARGET_LINE = (TOTAL_SYNTHETIC_COMMITS - 1) // TARGET_LINE_COUNT
MAX_COST_SECONDS = 30.0
FULL_AI_BRANCH_COUNT = 40
PARTIAL_AI_BRANCH_COUNT = 30
PARTIAL_AI_RATIO = 60
BASELINE_TIMESTAMP = "2026-02-20T09:00:00Z"
IN_WINDOW_BASE_TIMESTAMP = datetime(2026, 3, 1, 0, 0, tzinfo=timezone.utc)


@pytest.mark.production_scale
@pytest.mark.long_running
class TestUsngAlgcHistoryComplexScopeA13SvnTdd(unittest.TestCase):
    maxDiff = None

    def _parse_cost_seconds(self, stderr_text: str) -> float:
        match = re.search(r"costSeconds=(\d+\.\d+)s", stderr_text)
        self.assertIsNotNone(match)
        return float(match.group(1))

    def _format_revision_id(self, revision_number: int) -> str:
        return f"r{revision_number:05d}"

    def _revision_timestamp(self, revision_number: int) -> str:
        if revision_number == BASELINE_REVISION_NUMBER:
            return BASELINE_TIMESTAMP
        timestamp = IN_WINDOW_BASE_TIMESTAMP + timedelta(minutes=revision_number - BASELINE_REVISION_NUMBER - 1)
        return timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")

    def _target_ratio(self, feature_index: int) -> int:
        if feature_index < FULL_AI_BRANCH_COUNT:
            return 100
        if feature_index < FULL_AI_BRANCH_COUNT + PARTIAL_AI_BRANCH_COUNT:
            return PARTIAL_AI_RATIO
        return 0

    def _intermediate_ratio(self, feature_index: int, cycle_index: int) -> int:
        target_ratio = self._target_ratio(feature_index)
        if target_ratio == 100:
            ratio_cycle = [20, 40, 60, 80, 100]
        elif target_ratio == PARTIAL_AI_RATIO:
            ratio_cycle = [20, 40, 60, 80]
        else:
            ratio_cycle = [0]
        return ratio_cycle[cycle_index % len(ratio_cycle)]

    def _assert_deep_commit_chain(self, protocols: list[dict], query: dict) -> None:
        revision_ids = [protocol["REPOSITORY"]["revisionId"] for protocol in protocols]
        self.assertEqual(len(protocols), TOTAL_SYNTHETIC_COMMITS)
        self.assertEqual(len(revision_ids), TOTAL_SYNTHETIC_COMMITS)
        self.assertEqual(len(set(revision_ids)), TOTAL_SYNTHETIC_COMMITS)
        self.assertEqual(revision_ids[0], self._format_revision_id(BASELINE_REVISION_NUMBER))
        self.assertEqual(revision_ids[-1], query["endRevisionId"])

    def _build_rewrite_protocol(
        self,
        query: dict,
        revision_number: int,
        line_state: dict[tuple[int, int], dict[str, object]],
    ) -> dict:
        offset = revision_number - BASELINE_REVISION_NUMBER - 1
        slot_index = offset % TARGET_LINE_COUNT
        cycle_index = offset // TARGET_LINE_COUNT
        feature_index = slot_index // 2
        line_number = 2 if slot_index % 2 == 0 else 4
        file_name = self._file_name(feature_index)
        phase = "Integration" if line_number == 2 else "Release"
        new_ratio = self._target_ratio(feature_index) if cycle_index == REWRITES_PER_TARGET_LINE - 1 else self._intermediate_ratio(feature_index, cycle_index)
        revision_id = self._format_revision_id(revision_number)
        revision_timestamp = self._revision_timestamp(revision_number)
        previous_state = line_state[(feature_index, line_number)]
        protocol = {
            "protocolName": "generatedTextDesc",
            "protocolVersion": "26.04",
            "codeAgent": f"ProductionScaleSvn{phase}Agent",
            "SUMMARY": {
                "totalCodeLines": 1,
                "fullGeneratedCodeLines": 1 if new_ratio == 100 else 0,
                "partialGeneratedCodeLines": 1 if 0 < new_ratio < 100 else 0,
            },
            "DETAIL": [
                {
                    "fileName": file_name,
                    "codeLines": [
                        {
                            "changeType": "delete",
                            "lineLocation": line_number,
                            "genRatio": previous_state["genRatio"],
                            "genMethod": previous_state["genMethod"],
                            "blame": {
                                "revisionId": previous_state["revisionId"],
                                "originalFilePath": file_name,
                                "originalLine": line_number,
                                "timestamp": previous_state["timestamp"],
                            },
                        },
                        {
                            "changeType": "add",
                            "lineLocation": line_number,
                            "genRatio": new_ratio,
                            "genMethod": "Manual" if new_ratio == 0 else "codeCompletion",
                            "blame": {
                                "revisionId": revision_id,
                                "originalFilePath": file_name,
                                "originalLine": line_number,
                                "timestamp": revision_timestamp,
                            },
                        },
                    ],
                }
            ],
            "REPOSITORY": {
                "vcsType": query["vcsType"],
                "repoURL": query["repoURL"],
                "repoBranch": query["repoBranch"],
                "revisionId": revision_id,
                "revisionTimestamp": revision_timestamp,
            },
        }

        line_state[(feature_index, line_number)] = {
            "revisionId": revision_id,
            "timestamp": revision_timestamp,
            "genRatio": new_ratio,
            "genMethod": "Manual" if new_ratio == 0 else "codeCompletion",
        }
        return protocol

    def _file_name(self, feature_index: int) -> str:
        if feature_index < FEATURE_BRANCH_COUNT // 3:
            return f"trunk/src/core/feature_{feature_index:03d}.py"
        if feature_index < (2 * FEATURE_BRANCH_COUNT) // 3:
            return f"trunk/src/services/feature_{feature_index:03d}.py"
        return f"trunk/src/utils/feature_{feature_index:03d}.py"

    def _build_protocols(self, query: dict) -> list[dict]:
        baseline_detail = []
        baseline_revision_id = self._format_revision_id(BASELINE_REVISION_NUMBER)
        line_state: dict[tuple[int, int], dict[str, object]] = {}
        for feature_index in range(FEATURE_BRANCH_COUNT):
            file_name = self._file_name(feature_index)
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
                                "revisionId": baseline_revision_id,
                                "originalFilePath": file_name,
                                "originalLine": 1,
                                "timestamp": BASELINE_TIMESTAMP,
                            },
                        },
                        {
                            "changeType": "add",
                            "lineLocation": 2,
                            "genRatio": 0,
                            "genMethod": "Manual",
                            "blame": {
                                "revisionId": baseline_revision_id,
                                "originalFilePath": file_name,
                                "originalLine": 2,
                                "timestamp": BASELINE_TIMESTAMP,
                            },
                        },
                        {
                            "changeType": "add",
                            "lineLocation": 3,
                            "genRatio": 0,
                            "genMethod": "Manual",
                            "blame": {
                                "revisionId": baseline_revision_id,
                                "originalFilePath": file_name,
                                "originalLine": 3,
                                "timestamp": BASELINE_TIMESTAMP,
                            },
                        },
                        {
                            "changeType": "add",
                            "lineLocation": 4,
                            "genRatio": 0,
                            "genMethod": "Manual",
                            "blame": {
                                "revisionId": baseline_revision_id,
                                "originalFilePath": file_name,
                                "originalLine": 4,
                                "timestamp": BASELINE_TIMESTAMP,
                            },
                        },
                    ],
                }
            )
            line_state[(feature_index, 2)] = {
                "revisionId": baseline_revision_id,
                "timestamp": BASELINE_TIMESTAMP,
                "genRatio": 0,
                "genMethod": "Manual",
            }
            line_state[(feature_index, 4)] = {
                "revisionId": baseline_revision_id,
                "timestamp": BASELINE_TIMESTAMP,
                "genRatio": 0,
                "genMethod": "Manual",
            }
        protocols = [
            {
                "protocolName": "generatedTextDesc",
                "protocolVersion": "26.04",
                "codeAgent": "ProductionScaleSvnBaselineAgent",
                "SUMMARY": {
                    "totalCodeLines": FEATURE_BRANCH_COUNT * 4,
                    "fullGeneratedCodeLines": 0,
                    "partialGeneratedCodeLines": 0,
                },
                "DETAIL": baseline_detail,
                "REPOSITORY": {
                    "vcsType": query["vcsType"],
                    "repoURL": query["repoURL"],
                    "repoBranch": query["repoBranch"],
                    "revisionId": baseline_revision_id,
                    "revisionTimestamp": BASELINE_TIMESTAMP,
                },
            },
        ]

        for revision_number in range(BASELINE_REVISION_NUMBER + 1, FINAL_REVISION_NUMBER + 1):
            protocols.append(self._build_rewrite_protocol(query, revision_number, line_state))

        return protocols

    def _run_cli(self, log_level: str = "quiet") -> tuple[dict, str]:
        query = load_json(FIXTURE_DIR / "query.json")
        protocols = self._build_protocols(query)
        self._assert_deep_commit_chain(protocols, query)

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            output_file = temp_path / "out.json"
            for protocol in protocols:
                (temp_path / f"{protocol['REPOSITORY']['revisionId']}_genCodeDesc.json").write_text(json.dumps(protocol, indent=2) + "\n", encoding="utf-8")

            self.assertEqual(len(list(temp_path.glob("*_genCodeDesc.json"))), TOTAL_SYNTHETIC_COMMITS)

            result = subprocess.run(
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
                    *build_query_args_cli_args(query, include_identity=True, include_replay_selection=True),
                    "--logLevel",
                    log_level,
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

            return load_json(output_file), result.stderr

    def test_cli_matches_expected_result_for_svn_production_scale_fixture(self) -> None:
        self.assertGreaterEqual(FEATURE_BRANCH_COUNT, 100)
        self.assertGreaterEqual(TOTAL_SYNTHETIC_COMMITS, 10000)
        actual_result, _stderr = self._run_cli()
        expected_result = load_json(FIXTURE_DIR / "expected_result.json")
        self.assertEqual(actual_result, expected_result)

    def test_generated_history_contains_10001_distinct_commits(self) -> None:
        query = load_json(FIXTURE_DIR / "query.json")
        protocols = self._build_protocols(query)
        self._assert_deep_commit_chain(protocols, query)

    def test_info_log_reports_cost_seconds_within_budget_for_svn_production_scale_fixture(self) -> None:
        _actual_result, stderr_text = self._run_cli(log_level="info")
        self.assertIn("Finished analysis with totalCodeLines=200 fullGeneratedCodeLines=80 partialGeneratedCodeLines=60", stderr_text)
        self.assertLess(self._parse_cost_seconds(stderr_text), MAX_COST_SECONDS)


if __name__ == "__main__":
    unittest.main()
