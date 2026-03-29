# AggregateGenCodeDesc Test Data

This folder contains scenario-based fixture data for the user stories in `README_UserStory.md`.

## Structure

Each scenario directory contains:

- one matching `*_genCodeDesc.json` file per revision
- one `query.json` file describing the requested `vcsType`, `repoURL`, `repoBranch`, `metric`, `model`, `scope`, and `startTime~endTime`
- one `expected_result.json` file describing the expected aggregate final result using the same field structure as `genCodeDescProtocol.json` where applicable

## Scenarios

- `us1_live_changed_source_ratio` (`Model A`): weighted AI ratio for live changed source code lines in the requested window, expected `62.5%`
- `us2_human_overwrites_ai_live_changed` (`Model A`): later human rewrite resets one live changed line to `0`, expected `66.67%`
- `us3_ai_overwrites_human_live_changed` (`Model A`): later AI rewrite takes ownership of one live changed line, expected `60.0%`
- `us4_deleted_lines_excluded` (`Model A`): deleted lines are excluded from the live changed snapshot, expected `100%`
- `us5_rename_preserves_lineage` (`Model A`): rename preserves original attribution lineage, expected `66.67%`
- `us6_period_added_ratio` (`Model B`): true period contribution ratio inside `startTime~endTime`, expected `60.0%`
- `us7_mixed_multi_commit_window` (`Model A`): mixed multi-commit history with human-only lines, AI-only lines, human-then-AI rewrites, AI-then-human rewrites, and deleted AI lines, expected final summary `total=5, full=1, partial=1`
- `us8_merge_commit_preserves_attribution` (`Model A`): merge commit keeps effective attribution of surviving lines, expected final summary `total=4, full=1, partial=0`
- `us9_svn_contract_parity` (`Model A`): SVN target follows the same protocol-shaped result contract as Git for the primary metric, expected final summary `total=4, full=2, partial=1`

## Supplementary VCS Parity Fixture

- `us1_live_changed_source_ratio_svn` (`Model A`): SVN mirror of the `US-1` baseline metric, used to confirm that the primary live changed source ratio contract is not Git-specific

## Metrics Used In Fixtures

- `live_changed_source_ratio`: weighted AI ratio of live source code lines at `endTime` whose current version falls inside `startTime~endTime`
- `period_added_ai_ratio`: weighted AI ratio of added lines inside `startTime~endTime`

## Model Mapping

- `Model A`: end-snapshot attribution fixtures for the current primary metric
- `Model B`: period-contribution or history-oriented fixtures
- Current mapping in `testdata`:
  - `US-1`, `US-2`, `US-3`, `US-4`, `US-5`, `US-7`, `US-8`, and `US-9` are `Model A`
  - `US-6` is `Model B`

## Note

The earlier `*.diff` files were simplified fixtures for product design and algorithm verification.
They were not full repository exports and have now been removed from `testdata` to keep the fixture layer minimal.

For `Model A` real repository tests, `*.diff` files are not required.
Real repo tests should use actual Git or SVN history plus revision-level `genCodeDesc.json`, `query.json`, and `expected_result.json`.

If a future design task needs human-readable patch examples again, `*.diff` artifacts can be regenerated and reintroduced as optional explanatory material rather than required fixture input.

`expected_result.json` is intended to be the golden repository-level output for each scenario.
It should be stable enough for future automated verification.

To avoid contract drift, `expected_result.json` should follow `genCodeDescProtocol.json` naming and nesting for shared concepts such as `SUMMARY` and `REPOSITORY`.
It can still be a result-focused subset and does not need to repeat fields like `DETAIL` when they are not needed for golden-output comparison.
It also should not repeat query-only inputs such as `metric`, `model`, `scope`, `startTime`, or `endTime`, because those belong to `query.json`, not to the final protocol-shaped result.
