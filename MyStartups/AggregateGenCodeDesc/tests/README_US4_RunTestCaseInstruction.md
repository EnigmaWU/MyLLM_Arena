# US-4 Run Test Case Instruction

## Story Summary

US-4 proves that lines deleted before `endTime` do NOT appear in the final aggregate — only surviving lines count.

## Run All US-4 Tests

```bash
python3 -m pytest -q tests/test_us4_deleted_lines_tdd.py -v
```

## Test Files

### test_us4_deleted_lines_tdd.py

```bash
python3 -m pytest -q tests/test_us4_deleted_lines_tdd.py -v
```

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_cli_matches_us4_expected_result_when_ai_lines_are_deleted_before_endtime` | Deleted AI lines excluded from SUMMARY | SUMMARY matches `expected_result.json` |
| `test_cli_matches_us4_expected_result_for_narrow_algorithm_b_fixture_path` | Same via Algorithm B offline replay | Same SUMMARY |
| `test_cli_emits_debug_logs_for_us4_when_enabled` | Debug logs present | Logs present |
| `test_cli_info_logging_focuses_on_surviving_live_lines_for_us4` | Log mentions surviving lines only | Progress messages |

## Also Covered By

The US-2/3/4 cluster regression in `test_us2_us3_us4_algorithm_b_regression_tdd.py` (see [US-2 RunTestCaseInstruction](README_US2_RunTestCaseInstruction.md)).

## Run Single TC

```bash
python3 -m pytest -q "tests/test_us4_deleted_lines_tdd.py::TestUs4DeletedLinesTdd::test_cli_matches_us4_expected_result_when_ai_lines_are_deleted_before_endtime" -v
```
