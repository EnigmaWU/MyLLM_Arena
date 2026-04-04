# US-11 Run Test Case Instruction

## Story Summary

US-11 proves that a repository with deep commit history (many sequential changes to the same lines) still produces correct line attribution.

## Run All US-11 Tests

```bash
python3 -m pytest -q tests/test_us11_deep_history_preserves_attribution_tdd.py tests/test_us11_deep_history_preserves_attribution_svn_tdd.py tests/test_us11_deep_history_scalability_tdd.py -v
```

## Test Files

### test_us11_deep_history_preserves_attribution_tdd.py (Git)

```bash
python3 -m pytest -q tests/test_us11_deep_history_preserves_attribution_tdd.py -v
```

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_cli_matches_us11_expected_result_for_deep_history` | Deep Git history matches `expected_result.json` | SUMMARY matches golden file |
| `test_cli_matches_us11_expected_result_for_narrow_algorithm_b_fixture_path` | Same via Algorithm B offline replay | Same SUMMARY |
| `test_cli_emits_debug_logs_for_us11_when_enabled` | Debug logs present | Logs present |
| `test_cli_info_logging_focuses_on_live_line_aggregation_progress_for_us11` | Info logs present | Progress messages |

### test_us11_deep_history_preserves_attribution_svn_tdd.py (SVN)

```bash
python3 -m pytest -q tests/test_us11_deep_history_preserves_attribution_svn_tdd.py -v
```

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_cli_matches_us11_expected_result_for_deep_history` | Deep SVN history matches expected | SUMMARY matches golden file |
| `test_cli_emits_debug_logs_for_us11_when_enabled` | Debug logs present | Logs present |
| `test_cli_info_logging_focuses_on_live_line_aggregation_progress_for_us11` | Info logs present | Progress messages |

### test_us11_deep_history_scalability_tdd.py

```bash
python3 -m pytest -q tests/test_us11_deep_history_scalability_tdd.py -v
```

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_build_result_reuses_commit_time_lookup_per_origin_revision` | Commit-time lookups are cached (not repeated per line) | Pass — no redundant lookups |

## Also Covered By

The US-10/11 cluster regression in `test_us10_us11_algorithm_b_regression_tdd.py` (see [US-10 RunTestCaseInstruction](README_US10_RunTestCaseInstruction.md)).

## Run Single TC

```bash
python3 -m pytest -q "tests/test_us11_deep_history_preserves_attribution_tdd.py::TestUs11DeepHistoryPreservesAttributionTdd::test_cli_matches_us11_expected_result_for_deep_history" -v
```
