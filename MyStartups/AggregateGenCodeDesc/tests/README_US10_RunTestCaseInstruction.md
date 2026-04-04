# US-10 Run Test Case Instruction

## Story Summary

US-10 proves the tool handles a large repository with many files and revisions correctly — scale testing for Algorithm A.

## Run All US-10 Tests

```bash
python3 -m pytest -q tests/test_us10_large_repository_snapshot_tdd.py tests/test_us10_large_repository_snapshot_svn_tdd.py tests/test_us10_us11_algorithm_b_regression_tdd.py -v
```

## Test Files

### test_us10_large_repository_snapshot_tdd.py (Git)

```bash
python3 -m pytest -q tests/test_us10_large_repository_snapshot_tdd.py -v
```

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_cli_matches_us10_expected_result_for_large_snapshot` | Large Git repo matches `expected_result.json` | SUMMARY matches golden file |
| `test_cli_matches_us10_expected_result_for_narrow_algorithm_b_fixture_path` | Same via Algorithm B offline replay | Same SUMMARY |
| `test_cli_emits_debug_logs_for_us10_when_enabled` | Debug logs present | Logs present |
| `test_cli_info_logging_focuses_on_live_line_aggregation_progress_for_us10` | Info log shows progress | Progress messages |

### test_us10_large_repository_snapshot_svn_tdd.py (SVN)

```bash
python3 -m pytest -q tests/test_us10_large_repository_snapshot_svn_tdd.py -v
```

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_cli_matches_us10_expected_result_for_large_snapshot` | Large SVN repo matches expected | SUMMARY matches golden file |
| `test_cli_emits_debug_logs_for_us10_when_enabled` | Debug logs present | Logs present |
| `test_cli_info_logging_focuses_on_live_line_aggregation_progress_for_us10` | Info logs present | Progress messages |

### test_us10_us11_algorithm_b_regression_tdd.py (Cluster)

```bash
python3 -m pytest -q tests/test_us10_us11_algorithm_b_regression_tdd.py -v
```

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_algorithm_b_scale_and_deep_history_cluster_matches_expected_results` | US-10 + US-11 pass together under AlgB offline | All match expected |
| `test_algorithm_b_scale_and_deep_history_cluster_matches_expected_results_on_real_local_git_replay` | Same on real local Git repos | All match expected |

## Run Single TC

```bash
python3 -m pytest -q "tests/test_us10_large_repository_snapshot_tdd.py::TestUs10LargeRepositorySnapshotTdd::test_cli_matches_us10_expected_result_for_large_snapshot" -v
```
