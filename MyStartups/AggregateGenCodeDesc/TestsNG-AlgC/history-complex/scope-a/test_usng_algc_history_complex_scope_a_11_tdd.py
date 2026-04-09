import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from tests.cli_test_support import PROJECT_ROOT, UTILITY_PATH, load_json


FIXTURE_GIT_DIR = Path(__file__).resolve().parents[3] / "TestdataNG-AlgC" / "history-complex" / "scope-a" / "11" / "git" / "default"
FIXTURE_SVN_DIR = Path(__file__).resolve().parents[3] / "TestdataNG-AlgC" / "history-complex" / "scope-a" / "11" / "svn" / "default"


class TestUsngAlgcHistoryComplexScopeA11Tdd(unittest.TestCase):
    maxDiff = None

    def _build_protocol(self, query: dict) -> dict:
        file_name = "src/merged_branches.py"
        revisions = {
            "git": [
                "algc-us11-git-main-r1000",
                "algc-us11-git-feature-a-r1010",
                "algc-us11-git-feature-b-r1020",
                "algc-us11-git-feature-c-r1030",
                "algc-us11-git-feature-d-r1040",
                "algc-us11-git-feature-e-r1050",
                "algc-us11-git-feature-f-r1060",
            ],
            "svn": ["r1000", "r1010", "r1020", "r1030", "r1040", "r1050", "r1060"],
        }
        branch_revisions = revisions[query["vcsType"]]
        ratios = [0, 100, 60, 0, 100, 60, 0]
        times = [
            "2026-03-02T09:00:00Z",
            "2026-03-05T09:00:00Z",
            "2026-03-07T09:00:00Z",
            "2026-03-09T09:00:00Z",
            "2026-03-12T09:00:00Z",
            "2026-03-16T09:00:00Z",
            "2026-03-20T09:00:00Z",
        ]
        code_lines = []
        for index, (revision_id, ratio, timestamp) in enumerate(zip(branch_revisions, ratios, times), start=1):
            code_lines.append(
                {
                    "changeType": "add",
                    "lineLocation": index,
                    "genRatio": ratio,
                    "genMethod": "codeCompletion" if ratio > 0 else "Manual",
                    "blame": {
                        "revisionId": revision_id,
                        "originalFilePath": file_name,
                        "originalLine": index,
                        "timestamp": timestamp,
                    },
                }
            )

        return {
            "protocolName": "generatedTextDesc",
            "protocolVersion": "26.04",
            "codeAgent": "MergeFanInAgent",
            "SUMMARY": {
                "totalCodeLines": 7,
                "fullGeneratedCodeLines": 2,
                "partialGeneratedCodeLines": 2,
            },
            "DETAIL": [{"fileName": file_name, "codeLines": code_lines}],
            "REPOSITORY": {
                "vcsType": query["vcsType"],
                "repoURL": query["repoURL"],
                "repoBranch": query["repoBranch"],
                "revisionId": query["endRevisionId"],
                "revisionTimestamp": "2026-03-25T09:00:00Z",
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

    def test_cli_matches_git_expected_result_for_many_merged_branches(self) -> None:
        expected_result = load_json(FIXTURE_GIT_DIR / "expected_result.json")
        actual_result = self._run_cli(FIXTURE_GIT_DIR)
        self.assertEqual(actual_result, expected_result)

    def test_cli_matches_svn_expected_result_for_many_merged_branches(self) -> None:
        expected_result = load_json(FIXTURE_SVN_DIR / "expected_result.json")
        actual_result = self._run_cli(FIXTURE_SVN_DIR)
        self.assertEqual(actual_result, expected_result)


if __name__ == "__main__":
    unittest.main()
