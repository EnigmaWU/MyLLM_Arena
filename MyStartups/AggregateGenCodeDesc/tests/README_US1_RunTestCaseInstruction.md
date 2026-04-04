# US-1 Run Test Case Instruction

## Story Summary

US-1 is the baseline end-to-end story: one file, two revisions, Algorithm A produces the correct aggregate SUMMARY.

## Run All US-1 Tests

```bash
python3 -m pytest -q tests/test_us1_live_changed_source_ratio_tdd.py tests/test_us1_live_changed_source_ratio_svn_tdd.py tests/test_us1_matrix_parity_tdd.py -v
```

## Test Files

### test_us1_live_changed_source_ratio_tdd.py (Git)

```bash
python3 -m pytest -q tests/test_us1_live_changed_source_ratio_tdd.py -v
```

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_cli_matches_us1_expected_result_for_real_git_repo` | End-to-end on a real temp Git repo; output matches `testdata/us1_*/expected_result.json` | SUMMARY: total=3, full=1, partial=1 |
| `test_cli_fails_when_protocol_repository_identity_mismatches_query` | repoURL in protocol doesn't match query → `ProtocolValidationError` | Exit code ≠ 0 |
| `test_cli_emits_debug_logs_for_us1_when_enabled` | `--logLevel debug` produces `LiveLine` log records | Logs contain per-line origin info |
| `test_cli_info_logging_focuses_on_live_line_aggregation_progress` | `--logLevel info` emits aggregation progress messages | Logs contain progress messages |
| `test_cli_preserves_logical_git_repo_url_when_working_dir_is_separate` | `--workingDir /real/path --repoURL https://logical` → output `repoURL` is the logical one | `REPOSITORY.repoURL == "https://logical"` |

### test_us1_live_changed_source_ratio_svn_tdd.py (SVN)

```bash
python3 -m pytest -q tests/test_us1_live_changed_source_ratio_svn_tdd.py -v
```

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_cli_matches_us1_expected_result_for_real_svn_repo` | Same US-1 contract on a real temp SVN repo | Same SUMMARY as Git |
| `test_cli_emits_debug_logs_for_us1_svn_when_enabled` | Debug logging works for SVN path | Logs present |
| `test_cli_info_logging_focuses_on_live_line_aggregation_progress_for_us1_svn` | Info logging works for SVN path | Logs present |

### test_us1_matrix_parity_tdd.py

```bash
python3 -m pytest -q tests/test_us1_matrix_parity_tdd.py -v
```

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_us1_all_four_cells_share_same_observable_contract` | Git×AlgA, Git×AlgB, SVN×AlgA, SVN×AlgB all produce the same SUMMARY | All 4 cells identical |

## Run Single TC

```bash
python3 -m pytest -q "tests/test_us1_live_changed_source_ratio_tdd.py::TestUs1LiveChangedSourceRatioTdd::test_cli_matches_us1_expected_result_for_real_git_repo" -v
```
