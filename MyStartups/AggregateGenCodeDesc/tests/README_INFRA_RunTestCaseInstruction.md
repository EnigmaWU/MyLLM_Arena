# Infrastructure Run Test Case Instruction

These tests verify the internal building blocks (parsers, loaders, providers, replay engines) that underpin Algorithm B's commit-diff pipeline and protocol loading.

## Run All Infrastructure Tests

```bash
python3 -m pytest -q \
  tests/test_commit_diff_patch_parser_tdd.py \
  tests/test_commit_diff_replay_tdd.py \
  tests/test_commit_diff_line_state_tdd.py \
  tests/test_commit_diff_line_attribution_tdd.py \
  tests/test_commit_diff_sequence_loader_tdd.py \
  tests/test_commit_diff_set_dir_provider_tdd.py \
  tests/test_gen_code_desc_set_dir_provider_tdd.py \
  tests/test_protocol_jsonc_loading_tdd.py \
  tests/test_algorithm_b_fixture_contract_tdd.py \
  tests/test_algorithm_b_live_snapshot_foundation_tdd.py \
  -v
```

---

## Test Files

### 1. test_commit_diff_patch_parser_tdd.py

```bash
python3 -m pytest -q tests/test_commit_diff_patch_parser_tdd.py -v
```

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_parser_extracts_added_lines_from_us6_r2_patch` | Parser extracts added lines from US-6 revision 2 patch | Correct added lines returned |
| `test_parser_extracts_added_lines_from_us6_r3_patch` | Parser extracts added lines from US-6 revision 3 patch | Correct added lines returned |
| `test_parser_rejects_patch_without_diff_git_header` | Patch without `diff --git` header is rejected | Raises error |
| `test_parser_rejects_malformed_hunk_header` | Patch with malformed hunk header is rejected | Raises error |
| `test_parser_infers_file_paths_from_diff_git_header_when_path_headers_are_absent` | File path inferred from `diff --git a/… b/…` when `---`/`+++` headers absent | Correct path returned |

### 2. test_commit_diff_replay_tdd.py

```bash
python3 -m pytest -q tests/test_commit_diff_replay_tdd.py -v
```

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_replay_applies_us6_sequence_to_base_file_lines` | Replay engine applies US-6 diff sequence to produce correct final file | Final lines match expected snapshot |
| `test_replay_fails_when_patch_context_does_not_match_current_lines` | Replay detects context mismatch | Raises error |

### 3. test_commit_diff_line_state_tdd.py

```bash
python3 -m pytest -q tests/test_commit_diff_line_state_tdd.py -v
```

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_line_state_replay_preserves_origin_revision_for_added_lines` | Added lines are tagged with their origin revision | Origin revision preserved |
| `test_line_state_replay_keeps_existing_origin_through_context_lines` | Context lines keep their earlier origin revision | Existing origin unchanged |

### 4. test_commit_diff_line_attribution_tdd.py

```bash
python3 -m pytest -q tests/test_commit_diff_line_attribution_tdd.py -v
```

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_replay_assigns_gen_ratios_from_revision_metadata` | Replay assigns generatedRatio from each revision's metadata | Correct ratios attributed |
| `test_us6_period_added_summary_matches_expected_result` | Period-added summary for US-6 sequence matches expected result | Summary shape and values match |

### 5. test_commit_diff_sequence_loader_tdd.py

```bash
python3 -m pytest -q tests/test_commit_diff_sequence_loader_tdd.py -v
```

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_loader_builds_ordered_sequence_from_us6_fixture` | Loader builds time-ordered commit-diff sequence from US-6 fixture | Correct ordered sequence |
| `test_loader_fails_when_provider_has_gap_in_sequence` | Loader detects gap in sequence | Raises error |

### 6. test_commit_diff_set_dir_provider_tdd.py

```bash
python3 -m pytest -q tests/test_commit_diff_set_dir_provider_tdd.py -v
```

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_commit_diff_set_dir_provider_loads_raw_patch_text` | Provider loads raw patch text from file | Correct patch text returned |
| `test_commit_diff_set_dir_provider_loads_time_seq_prefixed_patch_for_revision` | Provider loads time-sequence-prefixed patch | Correct patch text returned |
| `test_commit_diff_set_dir_provider_fails_for_missing_patch` | Missing patch file is detected | Raises error |
| `test_commit_diff_set_dir_provider_fails_for_empty_patch` | Empty patch file is detected | Raises error |
| `test_build_commit_diff_provider_returns_set_dir_provider_when_configured` | Factory returns set-dir provider when commitDiffSetDir is configured | Correct provider type |
| `test_build_commit_diff_provider_returns_empty_provider_without_config` | Factory returns empty provider when no config | Empty provider returned |
| `test_list_commit_diff_revision_ids_prefers_time_seq_order_when_present` | Time-sequence prefixed files determine ordering | Correct order |
| `test_list_commit_diff_revision_ids_keeps_legacy_filename_fallback` | Legacy filenames used as fallback ordering | Correct order |
| `test_list_commit_diff_revision_ids_rejects_mixed_legacy_and_time_seq_names` | Mixed legacy and time-seq naming rejected | Raises error |
| `test_commit_diff_set_dir_provider_rejects_mixed_legacy_and_time_seq_names` | Provider rejects mixed naming at load time | Raises error |

### 7. test_gen_code_desc_set_dir_provider_tdd.py

```bash
python3 -m pytest -q tests/test_gen_code_desc_set_dir_provider_tdd.py -v
```

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_provider_can_find_fixture_file_by_repository_revision_id` | Provider locates protocol fixture by revision ID | Correct file content returned |
| `test_provider_reports_missing_revision_when_required` | Missing revision detected | Raises error |

### 8. test_protocol_jsonc_loading_tdd.py

```bash
python3 -m pytest -q tests/test_protocol_jsonc_loading_tdd.py -v
```

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_loader_accepts_jsonc_protocol_sample` | JSONC (JSON with comments) protocol file is parsed correctly | Parsed without error |
| `test_cli_test_helper_uses_same_jsonc_loader` | CLI test helper uses same JSONC loader as production code | Consistent parsing |

### 9. test_algorithm_b_fixture_contract_tdd.py

```bash
python3 -m pytest -q tests/test_algorithm_b_fixture_contract_tdd.py -v
```

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_us6_fixture_includes_commit_diff_for_each_replayed_revision` | US-6 fixture has commit-diff for every replayed revision | All revisions present |
| `test_missing_commit_diff_inside_long_sequence_fails_fixture_contract` | Missing commit-diff in long sequence breaks contract | Raises error |

### 10. test_algorithm_b_live_snapshot_foundation_tdd.py

```bash
python3 -m pytest -q tests/test_algorithm_b_live_snapshot_foundation_tdd.py -v
```

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_reconstruct_final_line_states_replays_us6_sequence` | Reconstructs final line states from US-6 replay sequence | Correct line states |
| `test_summarize_live_snapshot_line_states_filters_by_origin_commit_time` | Live-snapshot summary filters by origin commit time | Only relevant lines counted |
| `test_summarize_live_snapshot_line_states_requires_commit_time_for_replayed_revision` | Missing commit time raises error | Raises error |
| `test_reconstruct_final_line_states_replays_us7_mixed_history_sequence` | Replays US-7 mixed history sequence | Correct line states |
| `test_summarize_live_changed_line_states_respects_fixture_included_revision_ids` | Summary respects fixture-included revision IDs | Only fixture-included revisions counted |
