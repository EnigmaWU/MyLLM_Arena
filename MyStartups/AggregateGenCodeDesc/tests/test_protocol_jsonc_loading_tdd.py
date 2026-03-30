import tempfile
import unittest
from pathlib import Path

from aggregateGenCodeDesc import load_json_document
from tests.cli_test_support import load_json


class TestProtocolJsoncLoadingTdd(unittest.TestCase):
    def test_loader_accepts_jsonc_protocol_sample(self) -> None:
        protocol_text = """
        {
          // line comment before the protocol name
          "protocolName": "generatedTextDesc",
          "protocolVersion": "26.03",
          "REPOSITORY": {
            "repoURL": "https://example.com/repo.git",
            "revisionId": "abc123" /* block comment after a value */
          },
          "DETAIL": [
            {
              "fileName": "src/example.py",
              "codeLines": [
                {"lineLocation": 1, "genRatio": 100, "genMethod": "vibeCoding"}
              ]
            }
          ]
        }
        """

        protocol = load_json_document(protocol_text)

        self.assertEqual(protocol["protocolName"], "generatedTextDesc")
        self.assertEqual(protocol["REPOSITORY"]["repoURL"], "https://example.com/repo.git")
        self.assertEqual(protocol["DETAIL"][0]["codeLines"][0]["genRatio"], 100)

    def test_cli_test_helper_uses_same_jsonc_loader(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            protocol_path = Path(temp_dir) / "protocol.json"
            protocol_path.write_text(
                '{\n  // comment\n  "protocolName": "generatedTextDesc"\n}\n',
                encoding="utf-8",
            )

            protocol = load_json(protocol_path)

            self.assertEqual(protocol, {"protocolName": "generatedTextDesc"})


if __name__ == "__main__":
    unittest.main()