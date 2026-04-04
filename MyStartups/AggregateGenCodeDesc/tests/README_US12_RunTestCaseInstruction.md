# US-12 Run Test Case Instruction

## Story Summary

US-12 proves that multiple feature branches merged into the main line preserve per-line attribution from each branch. Includes rename-across-merge variants and octopus merges.

## Run All US-12 Tests

```bash
python3 -m pytest -q tests/test_us12_many_merged_branches_preserve_attribution_tdd.py tests/test_us12_many_merged_branches_preserve_attribution_svn_tdd.py tests/test_us12_svn_merged_branch_scalability_tdd.py -v
```

## Test Files

### test_us12_many_merged_branches_preserve_attribution_tdd.py (Git)

```bash
python3 -m pytest -q tests/test_us12_many_merged_branches_preserve_attribution_tdd.py -v
```

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_cli_matches_us12_expected_result_with_many_merged_branches` | Branch-heavy Git merge produces correct SUMMARY | total=7, full=2, partial=2 |
| `test_cli_matches_us12_expected_result_for_narrow_algorithm_b_fixture_path` | Same via Algorithm B offline replay | Same SUMMARY |
| `test_cli_preserves_double_rename_lineage_after_merge_variant` | Rename→merge→rename lineage survives | Pass |
| `test_cli_preserves_non_first_parent_origins_under_octopus_merge_variant` | Octopus merge preserves non-first-parent origins | Pass |
| `test_cli_preserves_parallel_rename_lineages_from_two_merged_branches_variant` | Two branches rename different files, both survive merge | Pass |
| `test_cli_preserves_parallel_rename_lineages_inside_octopus_merge_variant` | Parallel renames inside octopus merge | Pass |
| `test_cli_preserves_pre_rename_branch_origin_after_rename_and_merge_variant` | Branch-side rename doesn't lose pre-rename origin | Pass |
| `test_cli_preserves_rename_lineage_across_branch_handoff_merges_variant` | Branch handoff (A→B→main) preserves rename lineage | Pass |
| `test_cli_preserves_rename_lineage_inside_octopus_merge_variant` | Rename inside octopus merge | Pass |
| `test_cli_resets_one_parallel_rename_lineage_on_main_while_preserving_other_variant` | Main-side rewrite resets one lineage without affecting the other | Pass |
| `test_cli_emits_debug_logs_for_us12_branch_heavy_history` | Debug logs present | Logs present |
| `test_cli_info_logging_focuses_on_live_line_aggregation_progress_for_us12` | Info logs present | Progress messages |

### test_us12_many_merged_branches_preserve_attribution_svn_tdd.py (SVN)

```bash
python3 -m pytest -q tests/test_us12_many_merged_branches_preserve_attribution_svn_tdd.py -v
```

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_cli_matches_us12_expected_result_with_many_merged_branches` | Branch-heavy SVN merge produces correct SUMMARY | total=7, full=2, partial=2 |
| `test_cli_emits_debug_logs_for_us12_branch_heavy_history` | Debug logs present | Logs present |
| `test_cli_info_logging_focuses_on_live_line_aggregation_progress_for_us12` | Info logs present | Progress messages |

### test_us12_svn_merged_branch_scalability_tdd.py

```bash
python3 -m pytest -q tests/test_us12_svn_merged_branch_scalability_tdd.py -v
```

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_build_result_reuses_svn_revision_lookups_for_shared_branch_origins` | SVN revision lookups cached for shared branch origins | Pass — no redundant lookups |

## Also Covered By

The US-8/12 cluster regression in `test_us8_us12_algorithm_b_regression_tdd.py` (see [US-8 RunTestCaseInstruction](README_US8_RunTestCaseInstruction.md)).

## Run Single TC

```bash
python3 -m pytest -q "tests/test_us12_many_merged_branches_preserve_attribution_tdd.py::TestUs12ManyMergedBranchesPreserveAttributionTdd::test_cli_matches_us12_expected_result_with_many_merged_branches" -v
```

## Real Info-Level Log Output (`--logLevel info`)

When running US-12 with `--logLevel info`, the tool emits the following three-phase narrative to stderr.
This proves multi-branch merge attribution is preserved: transitions show how lines from different branches carry their AI classification through merges.

```
[INFO] [agg] Starting analysis for repo=<repoDir> branch=main window=2026-03-01..2026-03-31 endRevision=<commit>
[INFO] [agg] LiveLine src/branch_matrix.py:2 aggregate origin=src/branch_matrix.py:2@<commit> classification=human/unattributed
[INFO] [agg] TransitionHint src/branch_matrix.py:3 origin=src/branch_matrix.py:3@<commit> best_effort_transition=human/unattributed->100%-ai
[INFO] [agg] LiveLine src/branch_matrix.py:3 aggregate origin=src/branch_matrix.py:3@<commit> classification=100%-ai
[INFO] [agg] TransitionHint src/branch_matrix.py:4 origin=src/branch_matrix.py:4@<commit> best_effort_transition=human/unattributed->70%-ai
[INFO] [agg] LiveLine src/branch_matrix.py:4 aggregate origin=src/branch_matrix.py:4@<commit> classification=70%-ai
[INFO] [agg] TransitionHint src/branch_matrix.py:5 origin=src/branch_matrix.py:5@<commit> best_effort_transition=human/unattributed->100%-ai
[INFO] [agg] LiveLine src/branch_matrix.py:5 aggregate origin=src/branch_matrix.py:5@<commit> classification=100%-ai
[INFO] [agg] TransitionHint src/branch_matrix.py:6 origin=src/branch_matrix.py:6@<commit> best_effort_transition=human/unattributed->40%-ai
[INFO] [agg] LiveLine src/branch_matrix.py:6 aggregate origin=src/branch_matrix.py:6@<commit> classification=40%-ai
[INFO] [agg] LiveLine src/branch_matrix.py:7 aggregate origin=src/branch_matrix.py:7@<commit> classification=human/unattributed
[INFO] [agg] LiveLine src/branch_matrix.py:9 aggregate origin=src/branch_matrix.py:9@<commit> classification=human/unattributed
[INFO] [agg] Finished analysis with totalCodeLines=7 fullGeneratedCodeLines=2 partialGeneratedCodeLines=2 elapsed=<N>s
```

**How to read it:**
- Lines 3 and 5 from `branch-a` and `branch-c` show `->100%-ai` transitions through merges
- Lines 4 and 6 show partial AI (`70%-ai`, `40%-ai`) from `branch-c`
- Lines 2, 7, 9 have no transition or stay human — base or merge-introduced lines without AI attribution
- `totalCodeLines=7, fullGeneratedCodeLines=2, partialGeneratedCodeLines=2` — matches expected result

### See Real Logs Live

The pytest assertions verify log content internally. To see the actual log output in your terminal:

```bash
SHOW_CLI_LOGS=1 python3 -m pytest -s tests/test_us12_many_merged_branches_preserve_attribution_tdd.py -k "test_cli_info_logging" -v
```
