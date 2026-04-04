# US-5 Run Test Case Instruction

## Story Summary

US-5 proves that renaming a file does not break line attribution — `git blame` follows renames and preserves the original line origin.

## Run All US-5 Tests

```bash
python3 -m pytest -q tests/test_us5_rename_preserves_lineage_tdd.py tests/test_us5_us7_algorithm_b_regression_tdd.py -v
```

## Test Files

### test_us5_rename_preserves_lineage_tdd.py

```bash
python3 -m pytest -q tests/test_us5_rename_preserves_lineage_tdd.py -v
```

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_cli_matches_us5_expected_result_when_file_is_renamed_without_rewrite` | Rename without content change → attribution unchanged | SUMMARY matches `expected_result.json` |
| `test_cli_matches_us5_expected_result_for_narrow_algorithm_b_fixture_path` | Same via Algorithm B offline replay | Same SUMMARY |
| `test_cli_emits_debug_logs_for_us5_when_enabled` | Debug logs present | Logs present |
| `test_cli_info_logging_focuses_on_live_line_aggregation_progress_for_us5` | Info logs present | Progress messages |

### test_us5_us7_algorithm_b_regression_tdd.py (Cluster)

```bash
python3 -m pytest -q tests/test_us5_us7_algorithm_b_regression_tdd.py -v
```

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_algorithm_b_rename_and_mixed_history_cluster_matches_expected_results` | US-5 + US-7 pass together under AlgB offline | All match expected |
| `test_algorithm_b_rename_and_mixed_history_cluster_matches_expected_results_on_real_local_git_replay` | Same on real local Git repos | All match expected |

## Run Single TC

```bash
python3 -m pytest -q "tests/test_us5_rename_preserves_lineage_tdd.py::TestUs5RenamePreservesLineageTdd::test_cli_matches_us5_expected_result_when_file_is_renamed_without_rewrite" -v
```
