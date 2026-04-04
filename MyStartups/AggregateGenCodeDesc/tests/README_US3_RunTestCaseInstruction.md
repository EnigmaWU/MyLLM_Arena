# US-3 Run Test Case Instruction

## Story Summary

US-3 proves that when AI rewrites human lines in a later commit, the final aggregate attributes those lines to AI (latest origin wins).

## Run All US-3 Tests

```bash
python3 -m pytest -q tests/test_us3_ai_overwrites_human_tdd.py -v
```

## Test Files

### test_us3_ai_overwrites_human_tdd.py

```bash
python3 -m pytest -q tests/test_us3_ai_overwrites_human_tdd.py -v
```

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_cli_matches_us3_expected_result_when_ai_rewrites_two_human_lines` | AI-overwritten lines counted as AI in final | SUMMARY: full=1, partial=1 |
| `test_cli_matches_us3_expected_result_for_narrow_algorithm_b_fixture_path` | Same via Algorithm B offline replay | Same SUMMARY |
| `test_cli_emits_debug_logs_for_us3_when_enabled` | Debug logs present | Logs contain `LiveLine` entries |
| `test_cli_info_logging_focuses_on_live_line_aggregation_progress` | Info logs present | Progress messages |

## Also Covered By

The US-2/3/4 cluster regression in `test_us2_us3_us4_algorithm_b_regression_tdd.py` (see [US-2 RunTestCaseInstruction](README_US2_RunTestCaseInstruction.md)).

## Run Single TC

```bash
python3 -m pytest -q "tests/test_us3_ai_overwrites_human_tdd.py::TestUs3AiOverwritesHumanTdd::test_cli_matches_us3_expected_result_when_ai_rewrites_two_human_lines" -v
```
