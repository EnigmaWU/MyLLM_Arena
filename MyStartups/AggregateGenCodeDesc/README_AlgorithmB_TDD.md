# Algorithm B Implementation Plan

This document turns the shared-story convergence roadmap into an executable `Algorithm B` backlog.

It is intentionally concrete:

- every milestone names the fixture directory to use or create
- every milestone names the test files to extend or add
- every milestone names the primary code seams in `aggregateGenCodeDesc.py`

The current baseline is already in place:

- `US-6` has the first narrow executable `Algorithm B` offline Git path
- `US-1` has the first narrow live-snapshot `Algorithm B` 2x2 matrix example across Git and SVN

The next work is not to broaden support vaguely. The next work is to converge story-by-story semantics in a controlled order.

## Working Rules

1. Every new `Algorithm B` story claim must have one golden fixture result and one replay-complete `commitDiffSet/` contract.
2. Every newly claimed Git or SVN matrix cell must name its supported topology boundary explicitly.
3. No new story should claim broad production coverage until parity-style assertions exist against the matching `Algorithm A` contract.
4. Operator-facing CLI behavior must not depend on hidden internal routing knobs once the production UX is claimed in docs.

## Cross-Cutting Code Touch Points

These are the main seams that almost every `Algorithm B` milestone will use.

### CLI and dispatch

- `parse_args(...)`
- `validate_inputs(...)`
- `build_result(...)`

### Replay and line-state engine

- `parse_commit_diff_patch(...)`
- `apply_commit_diff_file_to_line_states(...)`
- `reconstruct_base_line_states_from_patch(...)`
- `reconstruct_final_line_states_from_commit_diff_sequence(...)`

### Live-snapshot and period summaries

- `summarize_period_added_line_states(...)`
- `summarize_live_changed_line_states_by_revision_ids(...)`
- `summarize_live_snapshot_line_states(...)`
- `build_result_algorithm_b_offline(...)`
- `build_result_algorithm_b_live_snapshot_offline(...)`

### Provider and fixture plumbing

- `CommitDiffSetDirProvider`
- `load_commit_diff_sequence(...)`
- `list_commit_diff_revision_ids(...)`
- `build_gen_code_desc_provider(...)`
- `build_commit_diff_provider(...)`

## Milestone 1: Remove The Metric UX Seam

### Goal

Make the CLI route the current supported `Algorithm B` modes without exposing `--metric` as a production operator requirement.

### Why This Comes First

The docs already describe a production-facing UX where operators choose `Algorithm B` and the supported scenario, not an internal dispatch knob. If this is left unresolved, every new `Algorithm B` story inherits the wrong public contract.

### Code Touch Points

- `parse_args(...)`: keep `--metric` transitional if still needed internally, but stop treating it as the operator contract
- `validate_inputs(...)`: validate supported `Algorithm B` combinations by actual mode/fixture inputs rather than by user-visible metric routing
- `build_result(...)`: replace direct `args.metric == "live_changed_source_ratio"` dispatch with one explicit supported-mode resolver
- new helper to infer supported `Algorithm B` path from fixture/query shape or explicit internal mode mapping

### Tests To Update Or Add

- Extend `tests/test_cli_algorithm_flag_tdd.py`
- Add CLI regressions that prove the current `US-1` and `US-6` fixture commands work without a user-facing `--metric`
- Keep one negative-path test for ambiguous or unsupported `Algorithm B` routing

### Exit Condition

- `US-1` narrow live-snapshot replay and `US-6` narrow period replay are both callable under the intended production UX boundary

## Milestone 2: Rewrite And Deletion Foundation

This is the highest-leverage functional cluster because almost every remaining live-snapshot story depends on these semantics.

## US-2: Human Rewrite Removes Prior AI Attribution

### US-2 Existing Fixture

- `testdata/us2_human_overwrites_ai_live_changed`

### US-2 Fixture Work

- add `commitDiffSet/` under `testdata/us2_human_overwrites_ai_live_changed`
- add one supplementary SVN fixture directory: `testdata/us2_human_overwrites_ai_live_changed_svn`
- add `commitDiffSet/` under the SVN fixture once the supported SVN slice is defined

### US-2 Tests

- extend existing story test: `tests/test_us2_human_overwrites_ai_tdd.py`
- add one dedicated AlgB parity file: `tests/test_us2_algorithm_b_parity_tdd.py`
- add one low-level replay regression file only if needed: `tests/test_algorithm_b_overwrite_reset_foundation_tdd.py`

### US-2 Code Touch Points

- `apply_commit_diff_file_to_line_states(...)`: ensure delete+add rewrite sequences replace origin ownership cleanly
- `resolve_added_line_gen_ratios(...)`: ensure rewritten added lines receive the correct new revision ratio
- `summarize_live_changed_line_states_by_revision_ids(...)`: ensure only the surviving rewritten line counts
- `build_result_algorithm_b_live_snapshot_offline(...)`: keep story output aligned to `expected_result.json`

### US-2 Done Evidence

- Git AlgB acceptance matches `expected_result.json`
- SVN AlgB acceptance exists or the unsupported subset is documented explicitly
- parity assertion proves matching observable `SUMMARY` and `REPOSITORY`

## US-3: AI Rewrite Replaces Prior Human Ownership

### US-3 Existing Fixture

- `testdata/us3_ai_overwrites_human_live_changed`

### US-3 Fixture Work

- add `commitDiffSet/` under `testdata/us3_ai_overwrites_human_live_changed`
- add supplementary SVN fixture directory: `testdata/us3_ai_overwrites_human_live_changed_svn`

### US-3 Tests

- extend existing story test: `tests/test_us3_ai_overwrites_human_tdd.py`
- add one dedicated AlgB parity file: `tests/test_us3_algorithm_b_parity_tdd.py`
- extend combined rewrite regression coverage later in `tests/test_us2_us3_us4_algorithm_b_regression_tdd.py`

### US-3 Code Touch Points

- same replay seam as `US-2`, but with emphasis on promoting new AI ownership rather than clearing stale ownership
- `resolve_added_line_gen_ratios(...)`
- `apply_commit_diff_file_to_line_states(...)`
- `summarize_live_changed_line_states_by_revision_ids(...)`

### US-3 Done Evidence

- Git AlgB acceptance matches `expected_result.json`
- SVN AlgB acceptance exists or unsupported subset is explicit
- parity assertion proves the later AI rewrite becomes the final effective owner

## US-4: Deleted AI Lines Must Not Count

### US-4 Existing Fixture

- `testdata/us4_deleted_lines_excluded`

### US-4 Fixture Work

- add `commitDiffSet/` under `testdata/us4_deleted_lines_excluded`
- add supplementary SVN fixture directory: `testdata/us4_deleted_lines_excluded_svn`

### US-4 Tests

- extend existing story test: `tests/test_us4_deleted_lines_tdd.py`
- add one dedicated AlgB parity file: `tests/test_us4_algorithm_b_parity_tdd.py`
- add one shared cluster regression file: `tests/test_us2_us3_us4_algorithm_b_regression_tdd.py`

### US-4 Code Touch Points

- `apply_commit_diff_file_to_line_states(...)`: deleted lines must disappear from final line state, not remain as stale ownership
- `reconstruct_final_line_states_from_commit_diff_sequence(...)`: ensure replay sequence handles deletion-only revisions safely
- `summarize_live_changed_line_states_by_revision_ids(...)`: verify deleted lines never contribute to final totals

### US-4 Done Evidence

- Git AlgB acceptance matches `expected_result.json`
- deletion cluster regression proves `US-1` behavior does not regress

## Milestone 3: Rename And Mixed History

## US-5: Rename Must Preserve Attribution Lineage

### US-5 Existing Fixture

- `testdata/us5_rename_preserves_lineage`

### US-5 Fixture Work

- add `commitDiffSet/` under `testdata/us5_rename_preserves_lineage`
- add supplementary SVN fixture directory: `testdata/us5_rename_preserves_lineage_svn`

### US-5 Tests

- extend existing story test: `tests/test_us5_rename_preserves_lineage_tdd.py`
- add low-level replay file: `tests/test_algorithm_b_rename_foundation_tdd.py`
- add parity file: `tests/test_us5_algorithm_b_parity_tdd.py`

### US-5 Code Touch Points

- `parse_commit_diff_patch(...)`: preserve old/new path identity from raw patches
- `reconstruct_final_line_states_from_commit_diff_sequence(...)`: allow controlled single-file path evolution instead of requiring one stable `new_path`
- `apply_commit_diff_file_to_line_states(...)`: maintain line-state continuity across path-only changes

### US-5 Done Evidence

- supported rename baseline is explicit
- path-only rename does not reset origin ownership
- unsupported multi-file rename topologies remain explicit if still out of scope

## US-7: Resolve Mixed Multi-Commit History

### US-7 Existing Fixture

- `testdata/us7_mixed_multi_commit_window`

### US-7 Fixture Work

- add `commitDiffSet/` under `testdata/us7_mixed_multi_commit_window`
- add supplementary SVN fixture directory: `testdata/us7_mixed_multi_commit_window_svn`

### US-7 Tests

- extend existing story test: `tests/test_us7_mixed_multi_commit_window_tdd.py`
- add parity file: `tests/test_us7_algorithm_b_parity_tdd.py`
- extend cluster regression coverage so rewrite, survival, and deletion interact in one replay window

### US-7 Code Touch Points

- `reconstruct_final_line_states_from_commit_diff_sequence(...)`: multi-revision correctness across longer sequences
- `apply_commit_diff_file_to_line_states(...)`: stable line offsets under repeated rewrites and deletions
- `summarize_live_changed_line_states_by_revision_ids(...)`: final line attribution must ignore superseded intermediate states

### US-7 Done Evidence

- mixed multi-commit histories converge to the latest surviving line ownership
- no leakage of intermediate ownership into final totals

## Milestone 4: Merge And Branch-Heavy Topology

## US-8: Merge Commit Must Preserve Effective Attribution

### US-8 Existing Fixture

- `testdata/us8_merge_commit_preserves_attribution`

### US-8 Fixture Work

- add `commitDiffSet/` under `testdata/us8_merge_commit_preserves_attribution` only after a merge replay policy is chosen
- add supplementary SVN fixture directory only if an SVN-supported subset is defensible

### US-8 Tests

- extend existing story test: `tests/test_us8_merge_commit_preserves_attribution_tdd.py`
- add low-level merge policy tests: `tests/test_algorithm_b_merge_policy_tdd.py`
- add parity file: `tests/test_us8_algorithm_b_parity_tdd.py`

### US-8 Code Touch Points

- `load_commit_diff_sequence(...)`: may need parent-order metadata if merge policy requires it
- `reconstruct_final_line_states_from_commit_diff_sequence(...)`: merge-aware replay policy
- helper functions around revision ancestry if patch replay alone is not enough

### US-8 Done Evidence

- merge policy is explicit in docs and tests
- surviving merged lines preserve effective ownership instead of flattening to merge commits

## US-12: Many Merged Branches Preserve Attribution

### US-12 Existing Fixture

- `testdata/us12_many_merged_branches_preserve_attribution`

### US-12 Fixture Work

- add `commitDiffSet/` only after `US-8` merge policy is stable
- add SVN supplementary fixture only after the Git-supported subset is stable

### US-12 Tests

- extend existing story tests:
  - `tests/test_us12_many_merged_branches_preserve_attribution_tdd.py`
  - `tests/test_us12_many_merged_branches_preserve_attribution_svn_tdd.py`
- add parity file: `tests/test_us12_algorithm_b_parity_tdd.py`
- extend merge policy tests for branch-heavy sequences

### US-12 Code Touch Points

- same merge-aware replay seam as `US-8`
- scalability protections inside `reconstruct_final_line_states_from_commit_diff_sequence(...)`

### US-12 Done Evidence

- branch-heavy merge topology preserves per-line ownership
- supported branch/merge subset is explicit and defended by tests

## Milestone 5: Scale And Deep History

## US-10: Large Snapshot Stability

### US-10 Existing Fixture

- `testdata/us10_large_repository_snapshot`

### US-10 Fixture Work

- only add `commitDiffSet/` if a fixture-driven AlgB path remains tractable
- prefer real-repo scale tests if the fixture becomes too synthetic

### US-10 Tests

- extend existing story tests:
  - `tests/test_us10_large_repository_snapshot_tdd.py`
  - `tests/test_us10_large_repository_snapshot_svn_tdd.py`
  - `tests/test_us10_large_snapshot_scalability_tdd.py`
- add AlgB scale regression file: `tests/test_us10_algorithm_b_scalability_tdd.py`

### US-10 Code Touch Points

- replay engine hot path in `apply_commit_diff_file_to_line_states(...)`
- replay loop in `reconstruct_final_line_states_from_commit_diff_sequence(...)`
- protocol lookup hot path in `build_result_algorithm_b_live_snapshot_offline(...)`

### US-10 Done Evidence

- correctness remains stable under broad file and line counts
- no premature caching complexity before correctness is locked

## US-11: Deep History Preserves Attribution

### US-11 Existing Fixture

- `testdata/us11_deep_history_preserves_attribution`

### US-11 Fixture Work

- add `commitDiffSet/` if the deep-history sequence is maintained as a fixture
- otherwise prefer the existing real-repo deep-history tests as the main acceptance path

### US-11 Tests

- extend existing story tests:
  - `tests/test_us11_deep_history_preserves_attribution_tdd.py`
  - `tests/test_us11_deep_history_preserves_attribution_svn_tdd.py`
  - `tests/test_us11_deep_history_scalability_tdd.py`
- add AlgB deep-history regression file: `tests/test_us11_algorithm_b_scalability_tdd.py`

### US-11 Code Touch Points

- replay correctness over long chains in `reconstruct_final_line_states_from_commit_diff_sequence(...)`
- line offset stability in `apply_commit_diff_file_to_line_states(...)`
- optional later caching around protocol indexes only after correctness is stable

### US-11 Done Evidence

- long rewrite chains preserve latest effective ownership
- no leakage of old ownership into the final result under deep history

## Milestone 6: US-9 Contract Convergence

## US-9: Git And SVN Must Follow The Same Result Contract

### US-9 Existing Fixture

- `testdata/us9_svn_contract_parity`

### US-9 Fixture Work

- add one Git-side AlgB parity fixture only after the main live-snapshot stories are stable enough
- add one SVN-side AlgB parity fixture only for the explicitly supported subset

### US-9 Tests

- extend the current VCS parity track with one AlgB parity file: `tests/test_us9_algorithm_b_contract_parity_tdd.py`
- reuse matrix-normalization helpers from `tests/test_us1_matrix_parity_tdd.py`

### US-9 Code Touch Points

- `build_result(...)`: ensure Git and SVN route through the same AlgB result envelope logic
- `validate_inputs(...)`: keep VCS boundary checks explicit
- `build_result_algorithm_b_live_snapshot_offline(...)`: maintain protocol-shaped parity across supported VCS targets

### US-9 Done Evidence

- Git and SVN supported AlgB cells match the same shared contract semantics
- differences are limited to VCS identity fields only
- current approved evidence is the narrow `US-1` baseline shape, not a blanket parity claim across every live-snapshot story

## Suggested File-By-File Execution Order

1. `aggregateGenCodeDesc.py`
   - remove the direct metric-based public routing seam
   - add one explicit AlgB mode resolver
2. `tests/test_cli_algorithm_flag_tdd.py`
   - lock the new operator contract before story expansion
3. `tests/test_us2_human_overwrites_ai_tdd.py`
4. `tests/test_us3_ai_overwrites_human_tdd.py`
5. `tests/test_us4_deleted_lines_tdd.py`
6. `tests/test_us2_us3_us4_algorithm_b_regression_tdd.py`
7. `tests/test_us5_rename_preserves_lineage_tdd.py`
8. `tests/test_us7_mixed_multi_commit_window_tdd.py`
9. merge-policy and scale files only after the rewrite/deletion cluster is stable

## Recommended Near-Term Deliverables

The next concrete implementation slice should be:

1. CLI cleanup for the AlgB production UX boundary
2. `US-2` Git AlgB acceptance
3. `US-3` Git AlgB acceptance
4. `US-4` Git AlgB acceptance
5. one combined regression for overwrite plus deletion transitions

That sequence gives the best leverage because it hardens the core live-line ownership rules before rename, merge, or scale complexity is added.
