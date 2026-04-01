import tempfile
import unittest
from pathlib import Path

from tests.cli_test_support import load_json


PROJECT_ROOT = Path(__file__).resolve().parent.parent
TESTDATA_ROOT = PROJECT_ROOT / "testdata"
US6_DIR = TESTDATA_ROOT / "us6_period_added_ratio"


def validate_algorithm_b_fixture_commit_diff_sequence(scenario_dir: Path) -> None:
    query = load_json(scenario_dir / "query.json")
    included_revision_ids = query.get("includedRevisionIds", [])
    if not isinstance(included_revision_ids, list) or not included_revision_ids:
        raise AssertionError("Algorithm B fixture must declare a non-empty includedRevisionIds list")

    commit_diff_dir = scenario_dir / "commitDiffSet"
    if not commit_diff_dir.is_dir():
        raise AssertionError(f"Algorithm B fixture missing commitDiffSet directory: {commit_diff_dir}")

    missing_revision_ids: list[str] = []
    for revision_id in included_revision_ids:
        expected_path = commit_diff_dir / f"{revision_id}_commitDiff.patch"
        if not expected_path.is_file():
            missing_revision_ids.append(revision_id)

    for revision_id in included_revision_ids:
        expected_path = commit_diff_dir / f"{revision_id}_commitDiff.patch"
        if expected_path.is_file() and not expected_path.read_text(encoding="utf-8").strip():
            raise AssertionError(f"Algorithm B fixture has empty commit diff patch: {revision_id}")

    if missing_revision_ids:
        raise AssertionError(
            "Algorithm B fixture has missing commit diffs in replay sequence: " + ", ".join(missing_revision_ids)
        )


class TestAlgorithmBFixtureContractTdd(unittest.TestCase):
    def test_us6_fixture_includes_commit_diff_for_each_replayed_revision(self) -> None:
        validate_algorithm_b_fixture_commit_diff_sequence(US6_DIR)

    def test_missing_commit_diff_inside_long_sequence_fails_fixture_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            scenario_dir = Path(temp_dir) / "usx_long_sequence"
            commit_diff_dir = scenario_dir / "commitDiffSet"
            commit_diff_dir.mkdir(parents=True)
            (scenario_dir / "query.json").write_text(
                """
{
  "vcsType": "git",
  "repoURL": "https://example.local/repo/demo",
  "repoBranch": "main",
  "metric": "period_added_ai_ratio",
  "algorithm": "B",
  "scope": "A",
  "startTime": "2026-03-01",
  "endTime": "2026-03-31",
  "includedRevisionIds": ["r101", "r102", "r103", "r104", "r105"]
}
""".strip() + "\n",
                encoding="utf-8",
            )
            for revision_id in ("r101", "r102", "r104", "r105"):
                (commit_diff_dir / f"{revision_id}_commitDiff.patch").write_text("diff --git a/src/demo.py b/src/demo.py\n", encoding="utf-8")

            with self.assertRaises(AssertionError) as context:
                validate_algorithm_b_fixture_commit_diff_sequence(scenario_dir)

        self.assertIn("missing commit diffs in replay sequence: r103", str(context.exception))


if __name__ == "__main__":
    unittest.main()
