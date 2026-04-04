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

## Real Info-Level Log Output (`--logLevel info`)

When running US-8 with `--logLevel info`, the tool emits the following three-phase narrative to stderr.
This proves merge commit attribution is preserved: line 3 shows a transition from human to AI through the feature branch merge.

```
[INFO] [agg] Starting analysis for repo=<repoDir> branch=main window=2026-03-01..2026-03-31 endRevision=<commit>
[INFO] [agg] LiveLine src/merge_case.py:1 aggregate origin=src/merge_case.py:1@<commit> classification=human/unattributed
[INFO] [agg] LiveLine src/merge_case.py:2 aggregate origin=src/merge_case.py:2@<commit> classification=human/unattributed
[INFO] [agg] TransitionHint src/merge_case.py:3 origin=src/merge_case.py:3@<commit> best_effort_transition=human/unattributed->100%-ai
[INFO] [agg] LiveLine src/merge_case.py:3 aggregate origin=src/merge_case.py:3@<commit> classification=100%-ai
[INFO] [agg] LiveLine src/merge_case.py:4 aggregate origin=src/merge_case.py:4@<commit> classification=human/unattributed
[INFO] [agg] Finished analysis with totalCodeLines=4 fullGeneratedCodeLines=1 partialGeneratedCodeLines=0 elapsed=<N>s
```

**How to read it:**
- `TransitionHint ...merge_case.py:3 ... human/unattributed->100%-ai` — line 3 (`value`) was human in r1, then rewritten by AI on the `feature-ai` branch and merged back
- After the no-ff merge, blame correctly traces line 3 to the feature branch commit where AI made the change
- `totalCodeLines=4, fullGeneratedCodeLines=1` — only the merged AI line counts as AI-attributed

### See Real Logs Live

The pytest assertions verify log content internally. To see the actual log output in your terminal:

```bash
SHOW_CLI_LOGS=1 python3 -m pytest -s tests/test_us8_merge_commit_preserves_attribution_tdd.py -k "test_cli_info_logging" -v
```
