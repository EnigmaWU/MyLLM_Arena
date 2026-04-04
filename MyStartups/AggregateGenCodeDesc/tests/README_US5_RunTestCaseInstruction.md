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

## Real Info-Level Log Output (`--logLevel info`)

When running US-5 with `--logLevel info`, the tool emits the following three-phase narrative to stderr.
This proves rename tracking works: the live file is `current_name.py` but origin points back to `legacy_name.py`.

```
[INFO] [agg] Starting analysis for repo=<repoDir> branch=main window=2026-03-01..2026-03-31 endRevision=<commit>
[INFO] [agg] LiveLine src/current_name.py:1 aggregate origin=src/legacy_name.py:1@<commit> classification=100%-ai
[INFO] [agg] LiveLine src/current_name.py:2 aggregate origin=src/legacy_name.py:2@<commit> classification=100%-ai
[INFO] [agg] LiveLine src/current_name.py:3 aggregate origin=src/legacy_name.py:3@<commit> classification=human/unattributed
[INFO] [agg] Finished analysis with totalCodeLines=3 fullGeneratedCodeLines=2 partialGeneratedCodeLines=0 elapsed=<N>s
```

**How to read it:**
- `LiveLine src/current_name.py:1 ... origin=src/legacy_name.py:1` — blame traces through the rename back to the original file
- Line attribution is preserved through the rename: lines 1-2 remain AI, line 3 remains human
- No `TransitionHint` — the rename did not change attribution, only the file path

### See Real Logs Live

The pytest assertions verify log content internally. To see the actual log output in your terminal:

```bash
SHOW_CLI_LOGS=1 python3 -m pytest -s tests/test_us5_rename_preserves_lineage_tdd.py -k "test_cli_info_logging" -v
```
