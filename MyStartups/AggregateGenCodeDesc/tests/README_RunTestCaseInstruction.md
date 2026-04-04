# AggregateGenCodeDesc — Run Test Case Instruction

## Purpose

This document tells you **how to run each automated test case** and **what to expect**.

It is NOT the same as `ManualInstruction` files (which teach you to reproduce a test by hand). This document is your guide to running the automated tests and understanding their meaning.

## Quick Reference

| Command | What It Runs |
|---------|-------------|
| `python3 -m pytest -q -m "not production_scale and not long_running and not experimental_svn"` | All Fast tests (205 TCs) |
| `python3 -m pytest -q tests/test_usXX_*.py` | One specific story |
| `python3 -m pytest -q tests/test_usXX_*.py::ClassName::test_method` | One specific TC |
| `bash run_production_gate.sh` | Heavy production-scale gate |

### How To Read The Output

- `205 passed` → all green, no regressions
- `FAILED tests/...::test_name` → that TC failed; read the `--tb=short` traceback
- `4 deselected` → production_scale / long_running / experimental_svn markers filtered out

---

## Infrastructure Tests (No User Story)

These tests verify internal building blocks. Run them when changing parser, replay, or provider internals.

### test_commit_diff_patch_parser_tdd.py

**Run:** `python3 -m pytest -q tests/test_commit_diff_patch_parser_tdd.py -v`

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_parser_extracts_added_lines_from_us6_r2_patch` | Parses a unified diff patch and extracts added lines from the US-6 r2 fixture | Pass — added lines match fixture |
| `test_parser_extracts_added_lines_from_us6_r3_patch` | Same for the r3 patch (context + addition) | Pass |
| `test_parser_infers_file_paths_from_diff_git_header_when_path_headers_are_absent` | Falls back to `diff --git a/... b/...` when `---`/`+++` headers are missing | Pass |
| `test_parser_rejects_malformed_hunk_header` | Malformed `@@` line → clear error | Raises error |
| `test_parser_rejects_patch_without_diff_git_header` | Missing `diff --git` → clear error | Raises error |

### test_commit_diff_replay_tdd.py

**Run:** `python3 -m pytest -q tests/test_commit_diff_replay_tdd.py -v`

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_replay_applies_us6_sequence_to_base_file_lines` | Replaying the US-6 patch sequence produces the correct final file state | Pass — final lines match |
| `test_replay_fails_when_patch_context_does_not_match_current_lines` | Context mismatch between patch and reconstructed file → error | Raises error |

### test_commit_diff_line_state_tdd.py

**Run:** `python3 -m pytest -q tests/test_commit_diff_line_state_tdd.py -v`

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_line_state_replay_preserves_origin_revision_for_added_lines` | Each added line remembers which revision introduced it | Pass |
| `test_line_state_replay_keeps_existing_origin_through_context_lines` | Context (unchanged) lines keep their original origin revision | Pass |

### test_commit_diff_line_attribution_tdd.py

**Run:** `python3 -m pytest -q tests/test_commit_diff_line_attribution_tdd.py -v`

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_replay_assigns_gen_ratios_from_revision_metadata` | After replay, each line gets its `genRatio` from the origin revision's protocol | Pass |
| `test_us6_period_added_summary_matches_expected_result` | US-6 period-added aggregate matches expected SUMMARY | Pass |

### test_commit_diff_sequence_loader_tdd.py

**Run:** `python3 -m pytest -q tests/test_commit_diff_sequence_loader_tdd.py -v`

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_loader_builds_ordered_sequence_from_us6_fixture` | Loads patches from commitDiffSetDir in revision order | Pass |
| `test_loader_fails_when_provider_has_gap_in_sequence` | Missing patch in the middle of a replay sequence → error | Raises error |

### test_commit_diff_set_dir_provider_tdd.py

**Run:** `python3 -m pytest -q tests/test_commit_diff_set_dir_provider_tdd.py -v`

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_build_commit_diff_provider_returns_empty_provider_without_config` | No `--commitDiffSetDir` → empty provider | Pass |
| `test_build_commit_diff_provider_returns_set_dir_provider_when_configured` | With `--commitDiffSetDir` → functional provider | Pass |
| `test_commit_diff_set_dir_provider_loads_raw_patch_text` | Provider loads patch content by revision ID | Pass |
| `test_commit_diff_set_dir_provider_loads_time_seq_prefixed_patch_for_revision` | Supports `NNNN_commitDiff.patch` naming | Pass |
| `test_commit_diff_set_dir_provider_fails_for_missing_patch` | Missing patch file → error | Raises error |
| `test_commit_diff_set_dir_provider_fails_for_empty_patch` | Empty patch file → error | Raises error |
| `test_commit_diff_set_dir_provider_rejects_mixed_legacy_and_time_seq_names` | Can't mix naming conventions in one dir | Raises error |
| `test_list_commit_diff_revision_ids_keeps_legacy_filename_fallback` | Legacy `<revId>_commitDiff.patch` naming still works | Pass |
| `test_list_commit_diff_revision_ids_prefers_time_seq_order_when_present` | Time-seq naming determines replay order | Pass |
| `test_list_commit_diff_revision_ids_rejects_mixed_legacy_and_time_seq_names` | Mixed naming → error | Raises error |

### test_gen_code_desc_set_dir_provider_tdd.py

**Run:** `python3 -m pytest -q tests/test_gen_code_desc_set_dir_provider_tdd.py -v`

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_provider_can_find_fixture_file_by_repository_revision_id` | Loads protocol JSON by revision ID | Pass |
| `test_provider_reports_missing_revision_when_required` | Missing protocol file → clear error | Raises error |

### test_protocol_jsonc_loading_tdd.py

**Run:** `python3 -m pytest -q tests/test_protocol_jsonc_loading_tdd.py -v`

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_loader_accepts_jsonc_protocol_sample` | Protocol files with `//` comments parse correctly | Pass |
| `test_cli_test_helper_uses_same_jsonc_loader` | Test helpers use the same JSONC loader as production code | Pass |

### test_algorithm_b_fixture_contract_tdd.py

**Run:** `python3 -m pytest -q tests/test_algorithm_b_fixture_contract_tdd.py -v`

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_us6_fixture_includes_commit_diff_for_each_replayed_revision` | US-6 fixture has a patch file for every revision in `includedRevisionIds` | Pass |
| `test_missing_commit_diff_inside_long_sequence_fails_fixture_contract` | Gap in patch sequence → fixture contract violation | Raises error |

### test_algorithm_b_live_snapshot_foundation_tdd.py

**Run:** `python3 -m pytest -q tests/test_algorithm_b_live_snapshot_foundation_tdd.py -v`

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_reconstruct_final_line_states_replays_us6_sequence` | Full line-state reconstruction from patch sequence (US-6) | Pass |
| `test_reconstruct_final_line_states_replays_us7_mixed_history_sequence` | Same for US-7 mixed history | Pass |
| `test_summarize_live_changed_line_states_respects_fixture_included_revision_ids` | Only included revisions participate in summary | Pass |
| `test_summarize_live_snapshot_line_states_filters_by_origin_commit_time` | Window filtering works (only in-window origins counted) | Pass |
| `test_summarize_live_snapshot_line_states_requires_commit_time_for_replayed_revision` | Missing commit time for a revision → error | Raises error |

---

## US-1: Live Changed Source Ratio — Baseline

**What US-1 proves:** The simplest end-to-end flow — one file, two revisions, Algorithm A produces the correct aggregate SUMMARY.

### test_us1_live_changed_source_ratio_tdd.py (Git)

**Run:** `python3 -m pytest -q tests/test_us1_live_changed_source_ratio_tdd.py -v`

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_cli_matches_us1_expected_result_for_real_git_repo` | End-to-end on real temp Git repo matches `expected_result.json` | Pass |
| `test_cli_fails_when_protocol_repository_identity_mismatches_query` | repoURL mismatch between protocol and query → `ProtocolValidationError` | Exit code ≠ 0 |
| `test_cli_emits_debug_logs_for_us1_when_enabled` | `--logLevel debug` produces expected log lines | Pass |
| `test_cli_info_logging_focuses_on_live_line_aggregation_progress` | `--logLevel info` emits progress messages | Pass |
| `test_cli_preserves_logical_git_repo_url_when_working_dir_is_separate` | `--workingDir` + logical `--repoURL` → output preserves logical URL | Pass |

### test_us1_live_changed_source_ratio_svn_tdd.py (SVN)

**Run:** `python3 -m pytest -q tests/test_us1_live_changed_source_ratio_svn_tdd.py -v`

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_cli_matches_us1_expected_result_for_real_svn_repo` | Same US-1 contract on a real temp SVN repo | Pass |
| `test_cli_emits_debug_logs_for_us1_svn_when_enabled` | Debug logging works for SVN path | Pass |
| `test_cli_info_logging_focuses_on_live_line_aggregation_progress_for_us1_svn` | Info logging works for SVN path | Pass |

### test_us1_matrix_parity_tdd.py

**Run:** `python3 -m pytest -q tests/test_us1_matrix_parity_tdd.py -v`

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_us1_all_four_cells_share_same_observable_contract` | Git×AlgA, Git×AlgB, SVN×AlgA, SVN×AlgB all produce the same SUMMARY | Pass |

---

## US-2: Human Overwrites AI

**What US-2 proves:** When a human rewrites an AI line in a later commit, the final aggregate reflects human ownership.

### test_us2_human_overwrites_ai_tdd.py

**Run:** `python3 -m pytest -q tests/test_us2_human_overwrites_ai_tdd.py -v`

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_cli_matches_us2_expected_result_when_human_rewrites_one_ai_line` | End-to-end: human-overwritten AI line not counted as AI | Pass |
| `test_cli_matches_us2_expected_result_for_narrow_algorithm_b_fixture_path` | Same via Algorithm B offline replay | Pass |
| `test_cli_emits_process_logs_for_us2_when_debug_logging_is_enabled` | Debug logs present | Pass |
| `test_cli_info_logging_focuses_on_live_line_aggregation_progress` | Info logs present | Pass |

---

## US-3: AI Overwrites Human

**What US-3 proves:** When an AI rewrites human lines, the final aggregate attributes them to AI (latest origin wins).

### test_us3_ai_overwrites_human_tdd.py

**Run:** `python3 -m pytest -q tests/test_us3_ai_overwrites_human_tdd.py -v`

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_cli_matches_us3_expected_result_when_ai_rewrites_two_human_lines` | End-to-end: AI-overwritten lines counted as AI | Pass |
| `test_cli_matches_us3_expected_result_for_narrow_algorithm_b_fixture_path` | Same via Algorithm B offline replay | Pass |
| `test_cli_emits_debug_logs_for_us3_when_enabled` | Debug logs present | Pass |
| `test_cli_info_logging_focuses_on_live_line_aggregation_progress` | Info logs present | Pass |

---

## US-4: Deleted Lines

**What US-4 proves:** Lines deleted before endTime do NOT appear in the final aggregate.

### test_us4_deleted_lines_tdd.py

**Run:** `python3 -m pytest -q tests/test_us4_deleted_lines_tdd.py -v`

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_cli_matches_us4_expected_result_when_ai_lines_are_deleted_before_endtime` | Deleted AI lines are excluded from SUMMARY | Pass |
| `test_cli_matches_us4_expected_result_for_narrow_algorithm_b_fixture_path` | Same via Algorithm B offline replay | Pass |
| `test_cli_emits_debug_logs_for_us4_when_enabled` | Debug logs present | Pass |
| `test_cli_info_logging_focuses_on_surviving_live_lines_for_us4` | Log mentions surviving lines only | Pass |

---

## US-2/3/4 Cluster: Algorithm B Regression

### test_us2_us3_us4_algorithm_b_regression_tdd.py

**Run:** `python3 -m pytest -q tests/test_us2_us3_us4_algorithm_b_regression_tdd.py -v`

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_algorithm_b_rewrite_and_deletion_cluster_matches_expected_results` | US-2, US-3, US-4 all pass together under AlgB offline | Pass |
| `test_algorithm_b_rewrite_and_deletion_cluster_matches_expected_results_on_real_local_git_replay` | Same on real local Git repos | Pass |

---

## US-5: Rename Preserves Lineage

**What US-5 proves:** Renaming a file does not break line attribution (git blame follows renames).

### test_us5_rename_preserves_lineage_tdd.py

**Run:** `python3 -m pytest -q tests/test_us5_rename_preserves_lineage_tdd.py -v`

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_cli_matches_us5_expected_result_when_file_is_renamed_without_rewrite` | Rename without content change → attribution unchanged | Pass |
| `test_cli_matches_us5_expected_result_for_narrow_algorithm_b_fixture_path` | Same via Algorithm B | Pass |
| `test_cli_emits_debug_logs_for_us5_when_enabled` | Debug logs present | Pass |
| `test_cli_info_logging_focuses_on_live_line_aggregation_progress_for_us5` | Info logs present | Pass |

---

## US-7: Mixed Multi-Commit Window

**What US-7 proves:** Multiple heterogeneous commits (human, AI, mixed) within one window aggregate correctly.

### test_us7_mixed_multi_commit_window_tdd.py

**Run:** `python3 -m pytest -q tests/test_us7_mixed_multi_commit_window_tdd.py -v`

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_cli_matches_us7_expected_result_for_mixed_multi_commit_window` | Multi-commit window produces correct aggregate | Pass |
| `test_cli_matches_us7_expected_result_for_narrow_algorithm_b_fixture_path` | Same via Algorithm B | Pass |
| `test_cli_emits_debug_logs_for_us7_when_enabled` | Debug logs present | Pass |
| `test_cli_info_logging_focuses_on_live_line_aggregation_progress_for_us7` | Info logs present | Pass |

---

## US-5/7 Cluster: Algorithm B Regression

### test_us5_us7_algorithm_b_regression_tdd.py

**Run:** `python3 -m pytest -q tests/test_us5_us7_algorithm_b_regression_tdd.py -v`

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_algorithm_b_rename_and_mixed_history_cluster_matches_expected_results` | US-5 + US-7 pass together under AlgB offline | Pass |
| `test_algorithm_b_rename_and_mixed_history_cluster_matches_expected_results_on_real_local_git_replay` | Same on real local Git repos | Pass |

---

## US-8: Merge Commit Preserves Attribution

**What US-8 proves:** A non-fast-forward merge preserves per-line origin from both parent branches.

### test_us8_merge_commit_preserves_attribution_tdd.py

**Run:** `python3 -m pytest -q tests/test_us8_merge_commit_preserves_attribution_tdd.py -v`

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_cli_matches_us8_expected_result_after_merge_preserves_effective_origin` | Merge preserves feature-branch AI attribution | Pass |
| `test_cli_matches_us8_expected_result_for_narrow_algorithm_b_fixture_path` | Same via Algorithm B | Pass |
| `test_cli_algorithm_b_matches_algorithm_a_when_manual_merge_adds_duplicate_text_matching_pre_window_parent_line` | Edge case: duplicate text after merge | Pass |
| `test_cli_algorithm_b_matches_algorithm_a_when_merge_keeps_feature_duplicate_line_after_main_deletes_original` | Edge case: feature duplicate survives main deletion | Pass |
| `test_cli_emits_debug_logs_for_us8_when_enabled` | Debug logs present | Pass |
| `test_cli_info_logging_focuses_on_live_line_aggregation_progress_for_us8` | Info logs present | Pass |

---

## US-9: Algorithm B Contract Parity (Git vs SVN)

### test_us9_algorithm_b_contract_parity_tdd.py

**Run:** `python3 -m pytest -q tests/test_us9_algorithm_b_contract_parity_tdd.py -v`

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_algorithm_b_git_and_svn_supported_cells_share_same_observable_contract` | Git and SVN produce same SUMMARY for the supported baseline shape | Pass |

---

## US-10: Large Repository Snapshot

**What US-10 proves:** The tool handles a repository with many files and revisions without breaking.

### test_us10_large_repository_snapshot_tdd.py (Git)

**Run:** `python3 -m pytest -q tests/test_us10_large_repository_snapshot_tdd.py -v`

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_cli_matches_us10_expected_result_for_large_snapshot` | Large Git repo matches expected SUMMARY | Pass |
| `test_cli_matches_us10_expected_result_for_narrow_algorithm_b_fixture_path` | Same via Algorithm B | Pass |
| `test_cli_emits_debug_logs_for_us10_when_enabled` | Debug logs present | Pass |
| `test_cli_info_logging_focuses_on_live_line_aggregation_progress_for_us10` | Info logs present | Pass |

### test_us10_large_repository_snapshot_svn_tdd.py (SVN)

**Run:** `python3 -m pytest -q tests/test_us10_large_repository_snapshot_svn_tdd.py -v`

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_cli_matches_us10_expected_result_for_large_snapshot` | Large SVN repo matches expected SUMMARY | Pass |
| `test_cli_emits_debug_logs_for_us10_when_enabled` | Debug logs present | Pass |
| `test_cli_info_logging_focuses_on_live_line_aggregation_progress_for_us10` | Info logs present | Pass |

---

## US-11: Deep History Preserves Attribution

**What US-11 proves:** A repository with deep commit history (many sequential changes) still produces correct line attribution.

### test_us11_deep_history_preserves_attribution_tdd.py (Git)

**Run:** `python3 -m pytest -q tests/test_us11_deep_history_preserves_attribution_tdd.py -v`

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_cli_matches_us11_expected_result_for_deep_history` | Deep Git history matches expected SUMMARY | Pass |
| `test_cli_matches_us11_expected_result_for_narrow_algorithm_b_fixture_path` | Same via Algorithm B | Pass |
| `test_cli_emits_debug_logs_for_us11_when_enabled` | Debug logs present | Pass |
| `test_cli_info_logging_focuses_on_live_line_aggregation_progress_for_us11` | Info logs present | Pass |

### test_us11_deep_history_preserves_attribution_svn_tdd.py (SVN)

**Run:** `python3 -m pytest -q tests/test_us11_deep_history_preserves_attribution_svn_tdd.py -v`

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_cli_matches_us11_expected_result_for_deep_history` | Deep SVN history matches expected SUMMARY | Pass |
| `test_cli_emits_debug_logs_for_us11_when_enabled` | Debug logs present | Pass |
| `test_cli_info_logging_focuses_on_live_line_aggregation_progress_for_us11` | Info logs present | Pass |

### test_us11_deep_history_scalability_tdd.py

**Run:** `python3 -m pytest -q tests/test_us11_deep_history_scalability_tdd.py -v`

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_build_result_reuses_commit_time_lookup_per_origin_revision` | Commit-time lookups are cached, not repeated per line | Pass |

---

## US-10/11 Cluster: Algorithm B Regression

### test_us10_us11_algorithm_b_regression_tdd.py

**Run:** `python3 -m pytest -q tests/test_us10_us11_algorithm_b_regression_tdd.py -v`

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_algorithm_b_scale_and_deep_history_cluster_matches_expected_results` | US-10 + US-11 pass together under AlgB offline | Pass |
| `test_algorithm_b_scale_and_deep_history_cluster_matches_expected_results_on_real_local_git_replay` | Same on real local Git repos | Pass |
| (US-11 tests) | Also includes US-11 standalone TCs (see above) | Pass |

---

## US-12: Many Merged Branches Preserve Attribution

**What US-12 proves:** Multiple feature branches merged into the main line preserve per-line attribution from each branch.

### test_us12_many_merged_branches_preserve_attribution_tdd.py (Git)

**Run:** `python3 -m pytest -q tests/test_us12_many_merged_branches_preserve_attribution_tdd.py -v`

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_cli_matches_us12_expected_result_with_many_merged_branches` | Branch-heavy Git merge history produces correct SUMMARY | Pass |
| `test_cli_matches_us12_expected_result_for_narrow_algorithm_b_fixture_path` | Same via Algorithm B | Pass |
| `test_cli_preserves_double_rename_lineage_after_merge_variant` | Rename→merge→rename lineage survives | Pass |
| `test_cli_preserves_non_first_parent_origins_under_octopus_merge_variant` | Octopus merge preserves non-first-parent origins | Pass |
| `test_cli_preserves_parallel_rename_lineages_from_two_merged_branches_variant` | Two branches rename different files, both survive merge | Pass |
| `test_cli_preserves_parallel_rename_lineages_inside_octopus_merge_variant` | Same under octopus merge | Pass |
| `test_cli_preserves_pre_rename_branch_origin_after_rename_and_merge_variant` | Branch-side rename doesn't lose pre-rename origin | Pass |
| `test_cli_preserves_rename_lineage_across_branch_handoff_merges_variant` | Branch handoff (A→B→main) preserves rename lineage | Pass |
| `test_cli_preserves_rename_lineage_inside_octopus_merge_variant` | Rename inside octopus merge | Pass |
| `test_cli_resets_one_parallel_rename_lineage_on_main_while_preserving_other_variant` | Main-side rewrite resets one lineage without affecting the other | Pass |
| `test_cli_emits_debug_logs_for_us12_branch_heavy_history` | Debug logs present | Pass |
| `test_cli_info_logging_focuses_on_live_line_aggregation_progress_for_us12` | Info logs present | Pass |

### test_us12_many_merged_branches_preserve_attribution_svn_tdd.py (SVN)

**Run:** `python3 -m pytest -q tests/test_us12_many_merged_branches_preserve_attribution_svn_tdd.py -v`

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_cli_matches_us12_expected_result_with_many_merged_branches` | Branch-heavy SVN merge history produces correct SUMMARY | Pass |
| `test_cli_emits_debug_logs_for_us12_branch_heavy_history` | Debug logs present | Pass |
| `test_cli_info_logging_focuses_on_live_line_aggregation_progress_for_us12` | Info logs present | Pass |

### test_us12_svn_merged_branch_scalability_tdd.py

**Run:** `python3 -m pytest -q tests/test_us12_svn_merged_branch_scalability_tdd.py -v`

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_build_result_reuses_svn_revision_lookups_for_shared_branch_origins` | SVN revision lookups are cached for shared branch origins | Pass |

---

## US-8/12 Cluster: Algorithm B Regression

### test_us8_us12_algorithm_b_regression_tdd.py

**Run:** `python3 -m pytest -q tests/test_us8_us12_algorithm_b_regression_tdd.py -v`

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_algorithm_b_merge_cluster_matches_expected_results` | US-8 + US-12 pass together under AlgB offline | Pass |
| `test_algorithm_b_merge_cluster_matches_expected_results_on_real_local_git_replay` | Same on real local Git repos | Pass |
| `test_algorithm_b_us12_branch_heavy_real_local_git_replay_matches_expected_result` | US-12 branch-heavy on real local Git | Pass |
| (US-12 duplicate tests) | Also includes full US-12 Git variant TCs | Pass |

---

## US-15: Period-Added Single-Branch Baseline

**What US-15 proves:** Algorithm B `period_added_ai_ratio` counts only lines whose origin commit falls inside the requested time window. Pre-window lines are excluded.

### test_us15_period_added_single_branch_baseline_tdd.py

**Run:** `python3 -m pytest -q tests/test_us15_period_added_single_branch_baseline_tdd.py -v`

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_period_added_counts_only_in_window_lines` | 3 in-window lines (2 AI + 1 human); SUMMARY: total=3, full=2, partial=0 | Pass |
| `test_period_added_excludes_pre_window_lines` | 6 lines in file but only 3 with in-window origin → totalCodeLines=3 | Pass |
| `test_period_added_scope_b_counts_all_source_lines` | Scope B variant — same count since all lines are pure code (no comments) | Pass |

---

## US-16: Period-Added Deletions And Rewrites

**What US-16 proves:** A line added then deleted in the same window is NOT counted. A rewritten line's origin shifts to the rewriting commit.

### test_us16_period_added_deletions_and_rewrites_tdd.py

**Run:** `python3 -m pytest -q tests/test_us16_period_added_deletions_and_rewrites_tdd.py -v`

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_deleted_ai_line_not_counted` | AI lines from r1 replaced by human in r2 → fullGenerated=0; total=2 | Pass |
| `test_rewritten_line_origin_shifts_to_rewriting_commit` | Pre-window line rewritten in-window has an in-window origin → totalCodeLines=2 | Pass |

---

## US-17: Period-Added Git Rename

**What US-17 proves:** Renaming a file does not make pre-window lines appear as in-window. Only genuinely new lines count.

### test_us17_period_added_git_rename_tdd.py

**Run:** `python3 -m pytest -q tests/test_us17_period_added_git_rename_tdd.py -v`

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_period_added_after_rename_counts_only_new_lines` | Only the new AI line counts; renamed pre-window lines excluded → total=1, full=1 | Pass |
| `test_renamed_file_appears_under_new_path` | SUMMARY totalCodeLines=1 proves rename tracking works | Pass |

---

## US-18: Period-Added Merge-Aware

**What US-18 proves:** AI lines from both main and a merged feature branch survive and are counted.

### test_us18_period_added_merge_aware_tdd.py

**Run:** `python3 -m pytest -q tests/test_us18_period_added_merge_aware_tdd.py -v`

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_period_added_merge_counts_both_branch_contributions` | Both AI lines survive merge → total=2, full=2 | Pass |

---

## US-19: Period-Added SVN Subset (Offline Fixtures)

**What US-19 proves:** Algorithm B `period_added_ai_ratio` works for SVN through the offline patch replay path. Also proves `--repoURL`/`--repoBranch` are optional when `--commitDiffSetDir` is provided.

### test_us19_period_added_svn_subset_tdd.py

**Run:** `python3 -m pytest -q tests/test_us19_period_added_svn_subset_tdd.py -v`

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_svn_period_added_via_offline_fixtures` | SVN patches replayed offline → total=3, full=2, revisionId="3" | Pass |
| `test_svn_period_added_works_without_repoURL_and_repoBranch` | Same result without `--repoURL`/`--repoBranch` (commitDiffSetDir is sufficient) | Pass |

---

## US-20: Scope B — Source With Comments

### test_us20_scope_b_source_with_comments_tdd.py

**Run:** `python3 -m pytest -q tests/test_us20_scope_b_source_with_comments_tdd.py -v`

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_scope_b_counts_comment_lines_alongside_code_lines` | Scope B includes comment lines in the count alongside code lines | Pass |

---

## US-21: Scope C — Documentation Lines

### test_us21_scope_c_doc_lines_tdd.py

**Run:** `python3 -m pytest -q tests/test_us21_scope_c_doc_lines_tdd.py -v`

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_scope_c_counts_doc_file_lines_using_doc_lines_protocol` | Scope C counts only doc file lines (using `docLines` protocol field) | Pass |

---

## US-22: Scope D — All Text (Source + Doc)

### test_us22_scope_d_all_text_tdd.py

**Run:** `python3 -m pytest -q tests/test_us22_scope_d_all_text_tdd.py -v`

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_scope_d_counts_all_non_blank_lines_from_source_and_doc_files` | Scope D counts all non-blank lines from both source and doc files | Pass |

---

## US-23: Scope Parity Matrix (Algorithm A)

### test_us23_scope_parity_matrix_tdd.py

**Run:** `python3 -m pytest -q tests/test_us23_scope_parity_matrix_tdd.py -v`

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_all_four_scopes_produce_valid_summaries_with_correct_field_names` | All scopes produce `totalCodeLines`, `fullGeneratedCodeLines`, `partialGeneratedCodeLines` | Pass |
| `test_scope_a_counts_only_code_lines_excluding_comments` | Scope A excludes comments | Pass |
| `test_scope_b_counts_code_and_comment_lines` | Scope B includes comments | Pass |
| `test_scope_c_counts_only_doc_file_lines` | Scope C counts only doc files | Pass |
| `test_scope_d_counts_all_source_and_doc_lines` | Scope D = union of source + doc | Pass |

---

## US-24: Algorithm B + Scope B

### test_us24_algorithm_b_scope_b_tdd.py

**Run:** `python3 -m pytest -q tests/test_us24_algorithm_b_scope_b_tdd.py -v`

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_algorithm_b_scope_b_counts_comments_via_live_changed` | AlgB + Scope B counts comments alongside code via live-changed replay | Pass |

---

## US-25: Algorithm B + Scope C

### test_us25_algorithm_b_scope_c_tdd.py

**Run:** `python3 -m pytest -q tests/test_us25_algorithm_b_scope_c_tdd.py -v`

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_algorithm_b_scope_c_counts_doc_lines_via_live_changed` | AlgB + Scope C counts doc lines via live-changed replay | Pass |

---

## US-26: Algorithm B + Scope D

### test_us26_algorithm_b_scope_d_tdd.py

**Run:** `python3 -m pytest -q tests/test_us26_algorithm_b_scope_d_tdd.py -v`

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_algorithm_b_scope_d_counts_source_and_doc_lines_via_live_changed` | AlgB + Scope D counts all text via live-changed replay | Pass |

---

## US-27: Cross-Algorithm × Cross-Scope Parity

**What US-27 proves:** Algorithm A and Algorithm B produce identical SUMMARY for all four scopes on the same repository.

### test_us27_cross_algorithm_scope_parity_tdd.py

**Run:** `python3 -m pytest -q tests/test_us27_cross_algorithm_scope_parity_tdd.py -v`

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_cross_algorithm_contract_shape_matches_for_all_scopes` | All 4 scopes have same field shape across algorithms | Pass |
| `test_scope_a_algorithm_a_and_b_produce_same_summary` | Scope A: AlgA == AlgB | Pass |
| `test_scope_b_algorithm_a_and_b_produce_same_summary` | Scope B: AlgA == AlgB | Pass |
| `test_scope_c_algorithm_a_and_b_produce_same_summary` | Scope C: AlgA == AlgB | Pass |
| `test_scope_d_algorithm_a_and_b_produce_same_summary` | Scope D: AlgA == AlgB | Pass |

---

## US-28: Production Hardening

**What US-28 proves:** Invalid scope values are rejected at input boundary. Oversized files are rejected before OOM.

### test_us28_production_hardening_tdd.py

**Run:** `python3 -m pytest -q tests/test_us28_production_hardening_tdd.py -v`

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_scope_Z_rejected_algorithm_a` | `--scope Z` → exit code ≠ 0 with error message | Rejected |
| `test_scope_Z_rejected_algorithm_b` | Same for Algorithm B | Rejected |
| `test_scope_empty_rejected` | `--scope ""` → rejected | Rejected |
| `test_scope_lowercase_a_rejected` | `--scope a` (lowercase) → rejected | Rejected |
| `test_read_git_file_rejects_oversized_output` | File > 100MB → `ValueError` | Raises error |
| `test_read_git_file_accepts_normal_output` | Normal-sized file → no error | Pass |
| `test_parse_blame_rejects_oversized_output` | Blame output > 100MB → `ValueError` | Raises error |

---

## CLI Routing & Algorithm B Acceptance

### test_cli_algorithm_flag_tdd.py

**Run:** `python3 -m pytest -q tests/test_cli_algorithm_flag_tdd.py -v`

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_cli_accepts_algorithm_flag` | `--algorithm B` is accepted without error | Pass |
| `test_cli_algorithm_b_defaults_to_live_snapshot_when_no_metric_in_query` | No `--metric` → defaults to `live_changed_source_ratio` | Pass |
| `test_cli_executes_narrow_algorithm_b_offline_diff_path_for_us6_fixture` | `--commitDiffSetDir` routes to offline replay | Pass |
| `test_cli_executes_algorithm_b_live_snapshot_path_for_us1_fixture` | US-1 Git fixture routes to live-snapshot | Pass |
| `test_cli_executes_algorithm_b_live_snapshot_path_for_us1_svn_fixture` | US-1 SVN fixture routes to live-snapshot | Pass |
| `test_cli_executes_algorithm_b_live_snapshot_path_for_local_git_repo_without_commit_diff_fixtures` | Local Git repo without commitDiffSetDir → live-snapshot path | Pass |
| `test_cli_executes_algorithm_b_live_snapshot_path_with_logical_repo_url_and_working_dir` | `--workingDir` + logical URL routes correctly | Pass |
| `test_cli_executes_algorithm_b_period_added_path_for_local_git_repo_without_commit_diff_fixtures` | `--metric period_added_ai_ratio` on local Git → period-added path | Pass |
| `test_cli_algorithm_b_offline_uses_query_included_revision_ids_as_authoritative_replay_sequence` | `query.json includedRevisionIds` controls replay order | Pass |
| `test_cli_algorithm_b_period_added_continues_with_warning_when_middle_protocol_is_missing` | Missing protocol in middle of sequence → warning + continue | Pass |
| `test_cli_handles_algorithm_b_local_git_live_snapshot_when_first_window_commit_has_multiple_hunks` | Multi-hunk first commit handled correctly | Pass |
| `test_cli_rejects_algorithm_b_live_snapshot_without_commit_diff_fixtures_or_local_git_checkout` | No commitDiffSetDir + no local checkout → error | Rejected |
| `test_cli_rejects_algorithm_b_offline_first_patch_with_multiple_files` | First patch with multiple files → error | Rejected |
| `test_cli_rejects_algorithm_b_offline_first_patch_with_multiple_hunks` | First patch with multiple hunks → error | Rejected |
| `test_cli_rejects_algorithm_b_offline_when_replayed_file_path_jumps_to_unrelated_file` | File path jump mid-sequence → error | Rejected |
| `test_cli_rejects_invalid_vcs_type_for_algorithm_b_live_snapshot_path` | Invalid vcsType → error | Rejected |
| `test_cli_rejects_legacy_model_flag` | `--model` flag → error (replaced by `--algorithm`) | Rejected |

---

## Runtime Hardening

### test_runtime_hardening_tdd.py

**Run:** `python3 -m pytest -q tests/test_runtime_hardening_tdd.py -v`

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_cli_algorithm_b_defaults_to_live_snapshot_when_no_metric_given` | No `--metric` in CLI or query → defaults to `live_changed_source_ratio` | Pass |
| `test_cli_allows_algorithm_b_commit_diff_set_dir_without_git_working_dir` | `--commitDiffSetDir` works without local Git checkout | Pass |
| `test_cli_fails_cleanly_for_gen_ratio_outside_valid_range` | `genRatio > 100` or `< 0` → error | Rejected |
| `test_cli_fails_cleanly_for_missing_file_name_in_protocol_detail` | Missing `fileName` in DETAIL → error | Rejected |
| `test_cli_fails_cleanly_for_missing_protocol_file_when_required` | Required protocol file missing → error | Rejected |
| `test_cli_fails_cleanly_for_overlapping_protocol_line_coverage` | Duplicate `lineLocation` → error | Rejected |
| `test_cli_fails_cleanly_when_no_revision_exists_before_end_time` | No revisions in window → error | Rejected |
| `test_cli_rejects_commit_diff_set_dir_for_algorithm_a` | `--commitDiffSetDir` with Algorithm A → error | Rejected |
| `test_cli_rejects_empty_repo_branch` | `--repoBranch ""` without `--commitDiffSetDir` → error | Rejected |
| `test_cli_rejects_repo_branch_with_path_traversal` | `--repoBranch ../hack` → error | Rejected |
| `test_cli_rejects_start_time_after_end_time` | `--startTime` > `--endTime` → error | Rejected |
| `test_cli_requires_working_dir_for_git_when_repo_url_is_logical_url` | Logical URL without `--workingDir` → error | Rejected |
| `test_parse_svn_blame_fails_when_blame_entries_and_file_lines_diverge` | Blame/file mismatch → error | Rejected |

---

## Real Git/SVN Scenarios (Integration)

### test_real_git_model_a_scenarios.py

**Run:** `python3 -m pytest -q tests/test_real_git_model_a_scenarios.py -v`

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_ai_overwrites_human_takes_latest_origin` | Real Git: AI overwrites human → blame shows AI origin | Pass |
| `test_deleted_lines_do_not_survive_final_snapshot` | Real Git: deleted lines absent from final blame | Pass |
| `test_human_overwrites_ai_resets_blame` | Real Git: human overwrites AI → blame shows human origin | Pass |
| `test_merge_commit_keeps_effective_line_origin` | Real Git: merge preserves effective line origin | Pass |
| `test_rename_preserves_lineage_under_git_blame` | Real Git: `git blame -C` follows renames | Pass |

### test_real_svn_contract_parity.py

**Run:** `python3 -m pytest -q tests/test_real_svn_contract_parity.py -v`

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_local_svn_repo_can_be_created_for_future_parity_tests` | Sanity check: SVN repo creation works on this machine | Pass |

### test_real_svn_same_file_merge_limitation.py

**Run:** `python3 -m pytest -q tests/test_real_svn_same_file_merge_limitation.py -v`

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_same_file_branch_merges_collapse_to_trunk_side_revisions` | Documents SVN blame limitation: same-file branch merges collapse to trunk revision | Pass |

---

## Stress Test

### test_stress_mixed_history_10plus_commits.py

**Run:** `python3 -m pytest -q tests/test_stress_mixed_history_10plus_commits.py -v`

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_cli_handles_realistic_mixed_history_with_eleven_commits` | 11-commit mixed history produces correct aggregate | Pass |
| `test_cli_debug_logs_show_mixed_realistic_origins` | Debug logs show per-line origin for the mixed history | Pass |

---

## Heavy Tier (Deselected By Default)

These are excluded from the fast suite. Run them explicitly.

### US-13: Git Production Scale

**Run:** `python3 -m pytest -q tests/test_us13_git_production_scale_local_repo_tdd.py -v`

### US-14: SVN Production Scale

**Run:** `python3 -m pytest -q tests/test_us14_svn_production_scale_local_repo_tdd.py -v`

### Combined Heavy Gate

**Run:** `bash run_production_gate.sh`

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `ModuleNotFoundError: No module named 'aggregateGenCodeDesc'` | Wrong working directory | `cd` to `MyStartups/AggregateGenCodeDesc` |
| `svnadmin: command not found` | SVN not installed | `brew install subversion` (macOS) |
| `4 deselected` | Normal — heavy/experimental tests filtered out | Expected behavior |
| Single TC fails after code change | Assertion mismatch | Read the `--tb=short` output; compare actual vs expected SUMMARY |
| All TCs fail | Likely a syntax/import error | Run `python3 -c "import aggregateGenCodeDesc"` to check |
