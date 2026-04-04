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
