import json
import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path

from tests.cli_test_support import PROJECT_ROOT, UTILITY_PATH, load_json


TESTS_ROOT = Path(__file__).resolve().parents[3] / "TestsNG-AlgC"


def _load_module(relative_path: str, module_name: str):
    module_path = TESTS_ROOT / relative_path
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestUsngAlgcHistorySimpleScopeA06Tdd(unittest.TestCase):
    maxDiff = None

    def _run_cli_with_protocol(self, query: dict, protocol: dict) -> tuple[subprocess.CompletedProcess[str], dict | None]:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            output_file = temp_path / "out.json"
            protocol_file = temp_path / f"{protocol['REPOSITORY']['revisionId']}_genCodeDesc.json"
            protocol_file.write_text(json.dumps(protocol, indent=2) + "\n", encoding="utf-8")

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
                    "--outputFile",
                    str(output_file),
                    "--genCodeDescSetDir",
                    str(temp_path),
                ],
                cwd=PROJECT_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            parsed_output = None
            if result.returncode == 0 and output_file.exists():
                parsed_output = load_json(output_file)
            return result, parsed_output

    def test_algorithm_c_summary_matches_story_golden_summary_for_all_covered_fast_scenarios(self) -> None:
        a01 = _load_module("history-simple/scope-a/test_usng_algc_history_simple_scope_a_01_tdd.py", "algc_a01")
        a08 = _load_module("history-simple/scope-a/test_usng_algc_history_simple_scope_a_08_tdd.py", "algc_a08")
        a02 = _load_module("history-complicated/scope-a/test_usng_algc_history_complicated_scope_a_02_tdd.py", "algc_a02")
        a03 = _load_module("history-complicated/scope-a/test_usng_algc_history_complicated_scope_a_03_tdd.py", "algc_a03")
        a04 = _load_module("history-complicated/scope-a/test_usng_algc_history_complicated_scope_a_04_tdd.py", "algc_a04")
        a05 = _load_module("history-complicated/scope-a/test_usng_algc_history_complicated_scope_a_05_tdd.py", "algc_a05")
        a07 = _load_module("history-complicated/scope-a/test_usng_algc_history_complicated_scope_a_07_tdd.py", "algc_a07")
        a09 = _load_module("history-complex/scope-a/test_usng_algc_history_complex_scope_a_09_tdd.py", "algc_a09")
        a10 = _load_module("history-complex/scope-a/test_usng_algc_history_complex_scope_a_10_tdd.py", "algc_a10")
        a11 = _load_module("history-complex/scope-a/test_usng_algc_history_complex_scope_a_11_tdd.py", "algc_a11")

        scenarios = [
            (a01.TestUsngAlgcHistorySimpleScopeA01Tdd, a01.FIXTURE_GIT_DIR, a01.FIXTURE_SVN_DIR),
            (a08.TestUsngAlgcHistorySimpleScopeA08Tdd, a08.FIXTURE_GIT_DIR, a08.FIXTURE_SVN_DIR),
            (a02.TestUsngAlgcHistoryComplicatedScopeA02Tdd, a02.FIXTURE_GIT_DIR, a02.FIXTURE_SVN_DIR),
            (a03.TestUsngAlgcHistoryComplicatedScopeA03Tdd, a03.FIXTURE_GIT_DIR, a03.FIXTURE_SVN_DIR),
            (a04.TestUsngAlgcHistoryComplicatedScopeA04Tdd, a04.FIXTURE_GIT_DIR, a04.FIXTURE_SVN_DIR),
            (a05.TestUsngAlgcHistoryComplicatedScopeA05Tdd, a05.FIXTURE_GIT_DIR, a05.FIXTURE_SVN_DIR),
            (a07.TestUsngAlgcHistoryComplicatedScopeA07Tdd, a07.FIXTURE_GIT_DIR, a07.FIXTURE_SVN_DIR),
            (a09.TestUsngAlgcHistoryComplexScopeA09Tdd, a09.FIXTURE_GIT_DIR, a09.FIXTURE_SVN_DIR),
            (a10.TestUsngAlgcHistoryComplexScopeA10Tdd, a10.FIXTURE_GIT_DIR, a10.FIXTURE_SVN_DIR),
            (a11.TestUsngAlgcHistoryComplexScopeA11Tdd, a11.FIXTURE_GIT_DIR, a11.FIXTURE_SVN_DIR),
        ]

        for runner_class, git_fixture_dir, svn_fixture_dir in scenarios:
            runner = runner_class(methodName="runTest")
            git_actual = runner._run_cli(git_fixture_dir)
            svn_actual = runner._run_cli(svn_fixture_dir)
            git_expected = load_json(git_fixture_dir / "expected_result.json")
            svn_expected = load_json(svn_fixture_dir / "expected_result.json")

            self.assertEqual(git_actual["SUMMARY"], git_expected["SUMMARY"])
            self.assertEqual(svn_actual["SUMMARY"], svn_expected["SUMMARY"])
            self.assertEqual(git_actual["SUMMARY"], svn_actual["SUMMARY"])

    def test_protocol_version_mismatch_is_a_hard_error(self) -> None:
        a01 = _load_module("history-simple/scope-a/test_usng_algc_history_simple_scope_a_01_tdd.py", "algc_a01_query")
        query = load_json(a01.FIXTURE_GIT_DIR / "query.json")
        bad_protocol = {
            "protocolName": "generatedTextDesc",
            "protocolVersion": "26.03",
            "codeAgent": "BadVersionAgent",
            "SUMMARY": {
                "totalCodeLines": 1,
                "fullGeneratedCodeLines": 1,
                "partialGeneratedCodeLines": 0,
            },
            "DETAIL": [
                {
                    "fileName": "src/example.py",
                    "codeLines": [
                        {
                            "changeType": "add",
                            "lineLocation": 1,
                            "genRatio": 100,
                            "genMethod": "codeCompletion",
                            "blame": {
                                "revisionId": "algc-bad-version-r1",
                                "originalFilePath": "src/example.py",
                                "originalLine": 1,
                                "timestamp": "2026-03-10T09:00:00Z",
                            },
                        }
                    ],
                }
            ],
            "REPOSITORY": {
                "vcsType": query["vcsType"],
                "repoURL": query["repoURL"],
                "repoBranch": query["repoBranch"],
                "revisionId": "algc-bad-version-r1",
                "revisionTimestamp": "2026-03-10T09:00:00Z",
            },
        }

        result, _output = self._run_cli_with_protocol(query, bad_protocol)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Algorithm C requires protocolVersion 26.04", result.stderr)

    def test_omitted_surviving_line_falls_back_to_manual_with_warning(self) -> None:
        a01 = _load_module("history-simple/scope-a/test_usng_algc_history_simple_scope_a_01_tdd.py", "algc_a01_omission")
        query = load_json(a01.FIXTURE_GIT_DIR / "query.json")
        query = dict(query)
        query["startTime"] = "2026-03-01"
        query["endTime"] = "2026-03-31"

        protocol = {
            "protocolName": "generatedTextDesc",
            "protocolVersion": "26.04",
            "codeAgent": "OmissionAgent",
            "SUMMARY": {
                "totalCodeLines": 3,
                "fullGeneratedCodeLines": 1,
                "partialGeneratedCodeLines": 0,
            },
            "DETAIL": [
                {
                    "fileName": "src/omission_case.py",
                    "codeLines": [
                        {
                            "changeType": "add",
                            "lineLocation": 1,
                            "genRatio": 100,
                            "genMethod": "codeCompletion",
                            "blame": {
                                "revisionId": "algc-omit-r1",
                                "originalFilePath": "src/omission_case.py",
                                "originalLine": 1,
                                "timestamp": "2026-03-10T09:00:00Z",
                            },
                        },
                        {
                            "changeType": "add",
                            "lineLocation": 3,
                            "genRatio": 0,
                            "genMethod": "Manual",
                            "blame": {
                                "revisionId": "algc-omit-r1",
                                "originalFilePath": "src/omission_case.py",
                                "originalLine": 3,
                                "timestamp": "2026-03-10T09:00:00Z",
                            },
                        },
                    ],
                }
            ],
            "REPOSITORY": {
                "vcsType": query["vcsType"],
                "repoURL": query["repoURL"],
                "repoBranch": query["repoBranch"],
                "revisionId": "algc-omit-r1",
                "revisionTimestamp": "2026-03-10T09:00:00Z",
            },
        }

        result, actual_result = self._run_cli_with_protocol(query, protocol)
        self.assertEqual(result.returncode, 0, msg=result.stderr)

        self.assertIsNotNone(actual_result)
        self.assertEqual(
            actual_result["SUMMARY"],
            {
                "totalCodeLines": 3,
                "fullGeneratedCodeLines": 1,
                "partialGeneratedCodeLines": 0,
            },
        )
        self.assertIn("WARNINGS", actual_result)
        self.assertTrue(any("omitted" in warning.lower() for warning in actual_result["WARNINGS"]))


if __name__ == "__main__":
    unittest.main()
