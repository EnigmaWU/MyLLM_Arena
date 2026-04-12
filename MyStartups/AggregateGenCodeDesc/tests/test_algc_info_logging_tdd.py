import json
import tempfile
import unittest
from pathlib import Path

from tests.cli_test_support import run_cli


def write_algc_protocol(
    protocol_dir: Path,
    repo_dir: Path,
    revision_id: str,
    revision_timestamp: str,
    line_entries: list[dict],
    summary: dict[str, int],
) -> None:
    protocol = {
        "protocolName": "generatedTextDesc",
        "protocolVersion": "26.04",
        "SUMMARY": summary,
        "DETAIL": [
            {
                "fileName": "src/app.py",
                "codeLines": line_entries,
            }
        ],
        "REPOSITORY": {
            "vcsType": "git",
            "repoURL": str(repo_dir),
            "repoBranch": "main",
            "revisionId": revision_id,
            "revisionTimestamp": revision_timestamp,
        },
    }
    (protocol_dir / f"{revision_id}_genCodeDesc.json").write_text(json.dumps(protocol, indent=2), encoding="utf-8")


class TestAlgCInfoLoggingTdd(unittest.TestCase):
    def test_cli_info_logging_emits_live_line_entries_for_algorithm_c(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo_dir = root / "repo"
            protocol_dir = root / "protocols"
            output_file = root / "out.json"

            repo_dir.mkdir()
            protocol_dir.mkdir()

            write_algc_protocol(
                protocol_dir,
                repo_dir,
                "algc-r1",
                "2026-03-01T09:00:00Z",
                [
                    {
                        "changeType": "add",
                        "lineLocation": 1,
                        "genRatio": 0,
                        "genMethod": "Manual",
                        "blame": {
                            "revisionId": "algc-r1",
                            "originalFilePath": "src/app.py",
                            "originalLine": 1,
                            "timestamp": "2026-03-01T09:00:00Z",
                        },
                    }
                ],
                {"totalCodeLines": 1, "fullGeneratedCodeLines": 0, "partialGeneratedCodeLines": 0},
            )
            write_algc_protocol(
                protocol_dir,
                repo_dir,
                "algc-r2",
                "2026-03-05T09:00:00Z",
                [
                    {
                        "changeType": "add",
                        "lineLocation": 2,
                        "genRatio": 100,
                        "genMethod": "codeCompletion",
                        "blame": {
                            "revisionId": "algc-r2",
                            "originalFilePath": "src/app.py",
                            "originalLine": 2,
                            "timestamp": "2026-03-05T09:00:00Z",
                        },
                    }
                ],
                {"totalCodeLines": 1, "fullGeneratedCodeLines": 1, "partialGeneratedCodeLines": 0},
            )

            query = {
                "vcsType": "git",
                "repoBranch": "main",
                "startTime": "2026-03-01",
                "endTime": "2026-03-31",
                "scope": "A",
            }

            result = run_cli(
                repo_dir,
                output_file,
                protocol_dir,
                query,
                extra_args=["--algorithm", "C", "--logLevel", "info"],
            )

            self.assertIn("Starting analysis", result.stderr)
            self.assertIn("LiveLine src/app.py:1 aggregate", result.stderr)
            self.assertIn("classification=human/unattributed", result.stderr)
            self.assertIn("LiveLine src/app.py:2 aggregate", result.stderr)
            self.assertIn("classification=100%-ai", result.stderr)
            self.assertIn(
                "Finished analysis with totalCodeLines=2 fullGeneratedCodeLines=1 partialGeneratedCodeLines=0",
                result.stderr,
            )


if __name__ == "__main__":
    unittest.main()