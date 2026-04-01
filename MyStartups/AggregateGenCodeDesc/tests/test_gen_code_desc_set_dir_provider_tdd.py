import unittest
from pathlib import Path

from aggregateGenCodeDesc import GenCodeDescSetDirProvider, ProtocolValidationError, RuntimeLogger


US6_DIR = Path(__file__).resolve().parent.parent / "testdata" / "us6_period_added_ratio"


class TestGenCodeDescSetDirProviderTdd(unittest.TestCase):
    def test_provider_can_find_fixture_file_by_repository_revision_id(self) -> None:
        provider = GenCodeDescSetDirProvider(US6_DIR, False, RuntimeLogger("quiet"))

        protocol = provider.get_revision_metadata(
            "https://example.local/repo/demo",
            "main",
            "us6-r2",
            "git",
        )

        self.assertEqual(protocol["REPOSITORY"]["revisionId"], "us6-r2")
        self.assertEqual(protocol["DETAIL"][0]["codeLines"][0]["lineLocation"], 4)

    def test_provider_reports_missing_revision_when_required(self) -> None:
        provider = GenCodeDescSetDirProvider(US6_DIR, True, RuntimeLogger("quiet"))

        with self.assertRaises(ProtocolValidationError) as context:
            provider.get_revision_metadata(
                "https://example.local/repo/demo",
                "main",
                "us6-r404",
                "git",
            )

        self.assertIn("Protocol file not found for revision us6-r404", str(context.exception))


if __name__ == "__main__":
    unittest.main()
