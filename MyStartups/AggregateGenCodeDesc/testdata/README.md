# AggregateGenCodeDesc Test Data

This folder contains scenario-based fixture data for the user stories in `README_UserStory.md`.

## Structure

Each scenario directory contains:

- one matching `*_genCodeDesc.json` file per revision
- one `query.json` file describing the requested `vcsType`, `repoURL`, `repoBranch`, `metric`, `algorithm`, `scope`, and `startTime~endTime`
- one `expected_result.json` file describing the expected aggregate final result using the same field structure as `genCodeDescProtocol.json` where applicable

For `Algorithm B`, the fixture contract is stricter:

- the scenario must also contain a `commitDiffSet/` directory
- the directory must contain one raw patch artifact such as `<revisionId>_commitDiff.patch` for every revision that the scenario expects the implementation to replay
- each patch artifact should be plain unified diff text, conceptually equivalent to `git diff > commitDiff.patch`, not a custom JSON protocol
- if the replay sequence is long, a missing commit diff in the middle of the sequence is a contract error and must fail fixture validation rather than being silently skipped

## Scenarios

- `us1_live_changed_source_ratio` (`Shared US`, current active evidence is `Algorithm A` plus a narrow `Algorithm B` Git live-snapshot path): weighted AI ratio for live changed source code lines in the requested window, expected `62.5%`
- `us2_human_overwrites_ai_live_changed` (`Shared US`, current active evidence is `Algorithm A`): later human rewrite resets one live changed line to `0`, expected `66.67%`
- `us3_ai_overwrites_human_live_changed` (`Shared US`, current active evidence is `Algorithm A`): later AI rewrite takes ownership of one live changed line, expected `60.0%`
- `us4_deleted_lines_excluded` (`Shared US`, current active evidence is `Algorithm A`): deleted lines are excluded from the live changed snapshot, expected `100%`
- `us5_rename_preserves_lineage` (`Shared US`, current active evidence is `Algorithm A`): rename preserves original attribution lineage, expected `66.67%`
- `us6_period_added_ratio` (`Shared US`, current executable path is `Algorithm B`): true period contribution ratio inside `startTime~endTime`, expected `60.0%`, with required `commitDiffSet/` artifacts for the replayed revisions; this is the current narrow executable Algorithm-B baseline fixture
- `us7_mixed_multi_commit_window` (`Shared US`, current active evidence is `Algorithm A`): mixed multi-commit history with human-only lines, AI-only lines, human-then-AI rewrites, AI-then-human rewrites, and deleted AI lines, expected final summary `total=5, full=1, partial=1`
- `us8_merge_commit_preserves_attribution` (`Shared US`, current active evidence is `Algorithm A`): merge commit keeps effective attribution of surviving lines, expected final summary `total=4, full=1, partial=0`
- `us9_svn_contract_parity` (`Shared contract story`, current active evidence is Git/SVN parity through `Algorithm A`): SVN target follows the same protocol-shaped result contract as Git for the primary metric, expected final summary `total=4, full=2, partial=1`
- `us10_large_repository_snapshot` (`Shared US`, current active evidence is `Algorithm A`): large-snapshot semantics remain stable under broad file and line counts
- `us11_deep_history_preserves_attribution` (`Shared US`, current active evidence is `Algorithm A`): deep history preserves latest effective attribution without leaking superseded states
- `us12_many_merged_branches_preserve_attribution` (`Shared US`, current active evidence is `Algorithm A`): branch-heavy merges preserve effective per-line attribution
- `us13_git_production_scale_local_repo` (`Heavy gate`, current active evidence is `Algorithm A`): production-scale Git golden query and expected aggregate result for a `100+` branch and `1000+` commit local repository, expected final summary `total=200, full=80, partial=60`
- `us14_svn_production_scale_local_repo` (`Heavy gate`, current active evidence is `Algorithm A`): production-scale SVN golden query and expected aggregate result for a `100+` branch-copy and `1000+` revision local repository, expected final summary `total=200, full=80, partial=60`

## Supplementary VCS Parity Fixture

- `us1_live_changed_source_ratio_svn` (`Algorithm A`): SVN mirror of the `US-1` baseline metric, used to confirm that the primary live changed source ratio contract is not Git-specific

## Metrics Used In Fixtures

- `live_changed_source_ratio`: weighted AI ratio of live source code lines at `endTime` whose current version falls inside `startTime~endTime`
- `period_added_ai_ratio`: weighted AI ratio of added lines inside `startTime~endTime`

## Algorithm Mapping

- `Algorithm A`: current active evidence for the primary live-snapshot metric and the present production gates
- `Algorithm B`: current active evidence for the narrow `US-6` period-contribution baseline and a narrow Git live-snapshot `US-1` baseline; broader shared-story convergence remains planned
- Current convergence interpretation in `testdata`:
  - `US-1` is the first primary-metric shared story with accepted `Algorithm A` evidence plus a narrow `Algorithm B` Git live-snapshot acceptance slice
  - `US-2`, `US-3`, `US-4`, `US-5`, `US-7`, `US-8`, `US-10`, `US-11`, and `US-12` are shared stories with current active evidence on the `Algorithm A` side
  - `US-9` is a shared contract story whose current active evidence is Git/SVN parity through `Algorithm A`
  - `US-6` is the first shared story with an executable `Algorithm B` acceptance track
  - `US-13` and `US-14` are `Heavy` production gates, not ordinary shared functional stories

## Note

The earlier `*.diff` files were simplified fixtures for product design and algorithm verification.
That earlier removal rule no longer applies to `Algorithm B`.
For `Algorithm B`, raw commit diff patch artifacts are required fixture input, not optional explanatory material.

For `Algorithm A` real repository tests, `*.diff` files are not required.
Real repo tests should use actual Git or SVN history plus revision-level `genCodeDesc.json`, `query.json`, and `expected_result.json`.

For `Algorithm B` fixture-driven tests, `testdata/` must carry both revision-level `genCodeDesc` records and raw commit diff patch artifacts so that replay completeness is explicit and verifiable.

Production-scale branch and merge topology scenarios should live under `tests/` with real local repositories rather than under `testdata/`.
Those scenarios validate VCS semantics and scalability behavior directly and are intentionally different from the simplified design fixtures kept in this folder.

If a future design task needs human-readable patch examples again, `*.diff` artifacts can be regenerated and reintroduced as optional explanatory material rather than required fixture input.

`expected_result.json` is intended to be the golden repository-level output for each scenario.
It should be stable enough for future automated verification.

To avoid contract drift, `expected_result.json` should follow `genCodeDescProtocol.json` naming and nesting for shared concepts such as `SUMMARY` and `REPOSITORY`.
It can still be a result-focused subset and does not need to repeat fields like `DETAIL` when they are not needed for golden-output comparison.
It also should not repeat query-only inputs such as `metric`, `algorithm`, `scope`, `startTime`, or `endTime`, because those belong to `query.json`, not to the final protocol-shaped result.
