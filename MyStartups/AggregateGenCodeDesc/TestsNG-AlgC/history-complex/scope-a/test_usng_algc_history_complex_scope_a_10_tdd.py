import json
import re
import subprocess
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from tests.cli_test_support import PROJECT_ROOT, UTILITY_PATH, build_query_args_cli_args, load_json


FIXTURE_GIT_DIR = Path(__file__).resolve().parents[3] / "TestdataNG-AlgC" / "history-complex" / "scope-a" / "10" / "git" / "default"
FIXTURE_SVN_DIR = Path(__file__).resolve().parents[3] / "TestdataNG-AlgC" / "history-complex" / "scope-a" / "10" / "svn" / "default"

BASELINE_REVISION_NUMBER = 100
FINAL_REVISION_NUMBER = 10100
TOTAL_SYNTHETIC_COMMITS = FINAL_REVISION_NUMBER - BASELINE_REVISION_NUMBER + 1
MAX_COST_SECONDS = 30.0
PRE_WINDOW_TIMESTAMP = "2026-01-01T09:00:00Z"
IN_WINDOW_BASE_TIMESTAMP = datetime(2026, 3, 1, 0, 0, tzinfo=timezone.utc)
FINAL_LINE_RATIOS = {
    2: 0,
    3: 60,
    4: 0,
    5: 100,
}


class TestUsngAlgcHistoryComplexScopeA10Tdd(unittest.TestCase):
    maxDiff = None

    def _parse_cost_seconds(self, stderr_text: str) -> float:
        match = re.search(r"costSeconds=(\d+\.\d+)s", stderr_text)
        self.assertIsNotNone(match)
        return float(match.group(1))

    def _assert_deep_commit_chain(self, protocols: list[dict], query: dict) -> None:
        revision_ids = [protocol["REPOSITORY"]["revisionId"] for protocol in protocols]
        self.assertEqual(len(protocols), TOTAL_SYNTHETIC_COMMITS)
        self.assertEqual(len(revision_ids), TOTAL_SYNTHETIC_COMMITS)
        self.assertEqual(len(set(revision_ids)), TOTAL_SYNTHETIC_COMMITS)
        self.assertEqual(revision_ids[0], self._format_revision_id(query["vcsType"], BASELINE_REVISION_NUMBER))
        self.assertEqual(revision_ids[-1], query["endRevisionId"])

    def _format_revision_id(self, vcs_type: str, revision_number: int) -> str:
        if vcs_type == "git":
            return f"algc-us10-git-r{revision_number:05d}"
        return f"r{revision_number:05d}"

    def _revision_timestamp(self, revision_number: int) -> str:
        if revision_number == BASELINE_REVISION_NUMBER:
            return PRE_WINDOW_TIMESTAMP
        timestamp = IN_WINDOW_BASE_TIMESTAMP + timedelta(minutes=revision_number - BASELINE_REVISION_NUMBER - 1)
        return timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")

    def _intermediate_ratio(self, revision_number: int, line_number: int) -> int:
        ratio_cycle = [0, 20, 40, 60, 80, 100]
        return ratio_cycle[(revision_number + line_number) % len(ratio_cycle)]

    def _build_protocol(self, query: dict, revision_number: int, line_state: dict[int, dict[str, object]]) -> dict:
        file_name = "src/deep_history.py"
        revision_id = self._format_revision_id(query["vcsType"], revision_number)
        revision_timestamp = self._revision_timestamp(revision_number)

        if revision_number >= FINAL_REVISION_NUMBER - 3:
            line_number = revision_number - (FINAL_REVISION_NUMBER - 3) + 2
            new_ratio = FINAL_LINE_RATIOS[line_number]
        else:
            line_number = 2 + ((revision_number - BASELINE_REVISION_NUMBER - 1) % 4)
            new_ratio = self._intermediate_ratio(revision_number, line_number)

        previous_state = line_state[line_number]
        protocol = {
            "protocolName": "generatedTextDesc",
            "protocolVersion": "26.04",
            "codeAgent": "DeepHistoryRewriteAgent" if revision_number < FINAL_REVISION_NUMBER - 3 else "DeepHistoryFinalAgent",
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

        line_state[line_number] = {
            "revisionId": revision_id,
            "timestamp": revision_timestamp,
            "genRatio": new_ratio,
            "genMethod": "Manual" if new_ratio == 0 else "codeCompletion",
        }
        return protocol

    def _build_protocols(self, query: dict) -> list[dict]:
        file_name = "src/deep_history.py"
        baseline_revision_id = self._format_revision_id(query["vcsType"], BASELINE_REVISION_NUMBER)
        line_state: dict[int, dict[str, object]] = {
            line_number: {
                "revisionId": baseline_revision_id,
                "timestamp": PRE_WINDOW_TIMESTAMP,
                "genRatio": 0,
                "genMethod": "Manual",
            }
            for line_number in range(1, 6)
        }

        protocols = [
            {
                "protocolName": "generatedTextDesc",
                "protocolVersion": "26.04",
                "codeAgent": "DeepHistoryBaselineAgent",
                "SUMMARY": {
                    "totalCodeLines": 5,
                    "fullGeneratedCodeLines": 0,
                    "partialGeneratedCodeLines": 0,
                },
                "DETAIL": [
                    {
                        "fileName": file_name,
                        "codeLines": [
                            {
                                "changeType": "add",
                                "lineLocation": line_number,
                                "genRatio": 0,
                                "genMethod": "Manual",
                                "blame": {
                                    "revisionId": baseline_revision_id,
                                    "originalFilePath": file_name,
                                    "originalLine": line_number,
                                    "timestamp": PRE_WINDOW_TIMESTAMP,
                                },
                            }
                            for line_number in range(1, 6)
                        ],
                    }
                ],
                "REPOSITORY": {
                    "vcsType": query["vcsType"],
                    "repoURL": query["repoURL"],
                    "repoBranch": query["repoBranch"],
                    "revisionId": baseline_revision_id,
                    "revisionTimestamp": PRE_WINDOW_TIMESTAMP,
                },
            }
        ]

        for revision_number in range(BASELINE_REVISION_NUMBER + 1, FINAL_REVISION_NUMBER + 1):
            protocols.append(self._build_protocol(query, revision_number, line_state))

        protocols[-1]["REPOSITORY"]["revisionId"] = query["endRevisionId"]
        return protocols

    def _run_cli(self, fixture_dir: Path, log_level: str = "quiet") -> tuple[dict, str]:
        query = load_json(fixture_dir / "query.json")
        protocols = self._build_protocols(query)
        self._assert_deep_commit_chain(protocols, query)

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            output_file = temp_path / "out.json"
            for protocol in protocols:
                protocol_path = temp_path / f"{protocol['REPOSITORY']['revisionId']}_genCodeDesc.json"
                protocol_path.write_text(json.dumps(protocol, indent=2) + "\n", encoding="utf-8")

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

    def test_cli_matches_git_expected_result_for_deep_history(self) -> None:
        expected_result = load_json(FIXTURE_GIT_DIR / "expected_result.json")
        actual_result, _stderr = self._run_cli(FIXTURE_GIT_DIR)
        self.assertEqual(actual_result, expected_result)

    def test_cli_matches_svn_expected_result_for_deep_history(self) -> None:
        expected_result = load_json(FIXTURE_SVN_DIR / "expected_result.json")
        actual_result, _stderr = self._run_cli(FIXTURE_SVN_DIR)
        self.assertEqual(actual_result, expected_result)

    def test_info_log_reports_cost_seconds_within_budget_for_git_deep_history(self) -> None:
        _actual_result, stderr_text = self._run_cli(FIXTURE_GIT_DIR, log_level="info")
        self.assertIn("Finished analysis with totalCodeLines=4 fullGeneratedCodeLines=1 partialGeneratedCodeLines=1", stderr_text)
        self.assertLess(self._parse_cost_seconds(stderr_text), MAX_COST_SECONDS)

    def test_info_log_reports_cost_seconds_within_budget_for_svn_deep_history(self) -> None:
        _actual_result, stderr_text = self._run_cli(FIXTURE_SVN_DIR, log_level="info")
        self.assertIn("Finished analysis with totalCodeLines=4 fullGeneratedCodeLines=1 partialGeneratedCodeLines=1", stderr_text)
        self.assertLess(self._parse_cost_seconds(stderr_text), MAX_COST_SECONDS)

    def test_generated_git_history_contains_10001_distinct_commits(self) -> None:
        query = load_json(FIXTURE_GIT_DIR / "query.json")
        protocols = self._build_protocols(query)
        self._assert_deep_commit_chain(protocols, query)

    def test_generated_svn_history_contains_10001_distinct_commits(self) -> None:
        query = load_json(FIXTURE_SVN_DIR / "query.json")
        protocols = self._build_protocols(query)
        self._assert_deep_commit_chain(protocols, query)


if __name__ == "__main__":
    unittest.main()
