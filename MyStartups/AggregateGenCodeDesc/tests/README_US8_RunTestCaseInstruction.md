# US-8 Run Test Case Instruction

## Story Summary

US-8 proves that a non-fast-forward merge preserves per-line origin from both parent branches. Feature-branch AI lines survive after merge.

## Run All US-8 Tests

```bash
python3 -m pytest -q tests/test_us8_merge_commit_preserves_attribution_tdd.py tests/test_us8_us12_algorithm_b_regression_tdd.py -v
```

## Test Files

### test_us8_merge_commit_preserves_attribution_tdd.py

```bash
python3 -m pytest -q tests/test_us8_merge_commit_preserves_attribution_tdd.py -v
```

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_cli_matches_us8_expected_result_after_merge_preserves_effective_origin` | Merge preserves feature-branch AI attribution | SUMMARY matches `expected_result.json` |
| `test_cli_matches_us8_expected_result_for_narrow_algorithm_b_fixture_path` | Same via Algorithm B offline replay | Same SUMMARY |
| `test_cli_algorithm_b_matches_algorithm_a_when_manual_merge_adds_duplicate_text_matching_pre_window_parent_line` | Edge case: merge adds duplicate text matching pre-window content | AlgA == AlgB |
| `test_cli_algorithm_b_matches_algorithm_a_when_merge_keeps_feature_duplicate_line_after_main_deletes_original` | Edge case: feature duplicate survives main deletion | AlgA == AlgB |
| `test_cli_emits_debug_logs_for_us8_when_enabled` | Debug logs present | Logs present |
| `test_cli_info_logging_focuses_on_live_line_aggregation_progress_for_us8` | Info logs present | Progress messages |

### test_us8_us12_algorithm_b_regression_tdd.py (Cluster)

```bash
python3 -m pytest -q tests/test_us8_us12_algorithm_b_regression_tdd.py -v
```

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_algorithm_b_merge_cluster_matches_expected_results` | US-8 + US-12 pass together under AlgB offline | All match expected |
| `test_algorithm_b_merge_cluster_matches_expected_results_on_real_local_git_replay` | Same on real local Git repos | All match expected |
| `test_algorithm_b_us12_branch_heavy_real_local_git_replay_matches_expected_result` | US-12 branch-heavy on real local Git | Matches expected |
| (US-12 variant TCs) | Full US-12 Git variant TCs also included | All pass |

## Run Single TC

```bash
python3 -m pytest -q "tests/test_us8_merge_commit_preserves_attribution_tdd.py::TestUs8MergeCommitPreservesAttributionTdd::test_cli_matches_us8_expected_result_after_merge_preserves_effective_origin" -v
```
