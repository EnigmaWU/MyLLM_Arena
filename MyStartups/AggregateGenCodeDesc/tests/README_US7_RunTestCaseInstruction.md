# US-7 Run Test Case Instruction

## Story Summary

US-7 proves that multiple heterogeneous commits (human, AI, mixed) within one measurement window aggregate correctly.

## Run All US-7 Tests

```bash
python3 -m pytest -q tests/test_us7_mixed_multi_commit_window_tdd.py -v
```

## Test Files

### test_us7_mixed_multi_commit_window_tdd.py

```bash
python3 -m pytest -q tests/test_us7_mixed_multi_commit_window_tdd.py -v
```

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_cli_matches_us7_expected_result_for_mixed_multi_commit_window` | Multi-commit window produces correct aggregate | SUMMARY matches `expected_result.json` |
| `test_cli_matches_us7_expected_result_for_narrow_algorithm_b_fixture_path` | Same via Algorithm B offline replay | Same SUMMARY |
| `test_cli_emits_debug_logs_for_us7_when_enabled` | Debug logs present | Logs present |
| `test_cli_info_logging_focuses_on_live_line_aggregation_progress_for_us7` | Info logs present | Progress messages |

## Also Covered By

The US-5/7 cluster regression in `test_us5_us7_algorithm_b_regression_tdd.py` (see [US-5 RunTestCaseInstruction](README_US5_RunTestCaseInstruction.md)).

## Run Single TC

```bash
python3 -m pytest -q "tests/test_us7_mixed_multi_commit_window_tdd.py::TestUs7MixedMultiCommitWindowTdd::test_cli_matches_us7_expected_result_for_mixed_multi_commit_window" -v
```
