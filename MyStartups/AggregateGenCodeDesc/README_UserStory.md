# AggregateGenCodeDesc User Stories And Acceptance Criteria

## Purpose

This document defines the first user stories for AggregateGenCodeDesc and the acceptance criteria used to verify them.

All stories assume the analysis request includes `repo + branch + startTime + endTime`.
For the current primary metric, `startTime~endTime` defines which live lines are in scope, and the result is calculated from the live snapshot at `endTime`.
The current baseline is `P0 / Scope A: pure source code` using `Algorithm A (preferred): blame-based end-snapshot attribution`.
Unless explicitly stated otherwise, the current user stories apply to both Git and SVN targets. VCS-specific differences may affect repository identity, branch or path conventions, and revision identifiers, but should not change the metric semantics or the protocol-shaped result contract.
At this stage, the acceptance criteria are intentionally defined at the repository query level, not at the internal file-level or line-level implementation level.
The final aggregate result may be returned in a report and may also be represented directly by the protocol `SUMMARY` section.
The user query and the final record are different artifacts: `query.json` represents analysis input, while `genCodeDescProtocol.json` represents the final result record.
The `genCodeDesc` records used during analysis are revision-level external metadata, not files committed into the analyzed repository.
The intended lookup key for one metadata record is `repoURL + repoBranch + revisionId`.
Unless a story explicitly defines another metric, `SUMMARY.totalCodeLines` always means only the code lines represented by that record's scope. For the current Algorithm A final result, this excludes deleted lines and counts only live lines still present at `endTime`.
For fixture verification, `expected_result.json` should remain a minimal protocol-shaped output artifact. It should keep result fields such as `protocolName`, `protocolVersion`, `SUMMARY`, and `REPOSITORY`, and should not duplicate query-only fields such as `metric`, `algorithm`, `scope`, `startTime`, or `endTime`.

Each story is paired with scenario-based test data under `testdata/`.
Each scenario contains:

- one `genCodeDesc` file per revision that describes AI attribution for that revision

For `Algorithm B`, each scenario must also carry a complete commit diff sequence in `commitDiffSet/`.
If a scenario expects revisions `r1..rn` to be replayed, every required replayed revision must have a matching raw patch artifact such as `<timeSeq>_<revisionId>_commitDiff.patch`.
A missing diff in the middle of a long sequence is a fixture contract failure, not an ignorable gap.

For planned future stories, the scenario name defines the intended verification target even if the concrete fixture or integration test has not been added yet.

Those `testdata/` scenarios are design-oriented fixtures.
Those local `genCodeDesc` files simulate the external metadata store used in real deployments.
For `Algorithm B`, local raw commit diff patch artifacts are also required in `testdata/` so replay completeness can be verified explicitly.
For real repository verification of `Algorithm A`, the preferred test layer is under `tests/`, where actual Git or SVN repositories are created and `*.diff` files are not required.

For production-oriented runs, the analyzer should discover relevant revisions from repository history first and then fetch matching `genCodeDesc` records from an external provider.

## Story Structure

- A shared `US` should describe the business requirement and expected user-visible outcome, independent of implementation strategy.
- Shared acceptance criteria should cover the observable contract that must remain true regardless of whether `Algorithm A` or `Algorithm B` satisfies the story, and regardless of whether the supported target is Git or SVN.
- Algorithm-specific acceptance tracks should be used only where support boundaries, edge-case semantics, or runtime constraints differ between `Algorithm A` and `Algorithm B`.
- If only one algorithm or one VCS cell is currently implemented for a shared story, the missing matrix cells may still be documented as planned, but they must not be treated as current acceptance evidence.
- For the current convergence plan, `US-6` remains the anchor shared story for the period-added metric, and the approved live-snapshot shared-story subset (`US-1/2/3/4/5/7/8/9/10/11/12`) now also has narrow fixture-driven `Algorithm B` acceptance. Any remaining matrix cells may stay planned, but they must not be presented as current evidence until implemented and proven.
- For production-ready claims, a shared story is not complete until the claimed support matrix is explicit across both algorithms and both VCS targets, unless an unsupported subset is deliberately approved and documented.
- Some stories are shared primarily across VCS targets rather than across algorithms. In those cases, the first acceptance split should be Git vs SVN, while algorithm-specific tracks stay planned until both algorithms are real contenders for the same observable contract.
- `US-13` and `US-14` are intentionally treated as `Heavy` production gates. They are important acceptance items, but they should not be used as the template for ordinary shared functional stories.

## Verification Tiers

- `Fast` verification: fixture-driven checks and short-running real-repository tests intended for routine local runs and normal CI execution.
- `Heavy` verification: production-oriented, long-running, or large-history acceptance checks intended for explicit production gates or scheduled daily integration runs.
- `Heavy` verification is the right home for tests that may take tens of minutes or about one hour, such as production-scale Git/SVN history validation.

## Scenario Mapping

- `US-1` -> `testdata/us1_live_changed_source_ratio` (`Shared US`, current matrix state: `Algorithm A` covers Git and SVN, `Algorithm B` covers narrow Git and SVN live-snapshot paths for the approved baseline shape, `Fast`)
- `US-2` -> `testdata/us2_human_overwrites_ai_live_changed` (`Shared US`, current active evidence is `Algorithm A` plus narrow Git `Algorithm B`, `Fast`)
- `US-3` -> `testdata/us3_ai_overwrites_human_live_changed` (`Shared US`, current active evidence is `Algorithm A` plus narrow Git `Algorithm B`, `Fast`)
- `US-4` -> `testdata/us4_deleted_lines_excluded` (`Shared US`, current active evidence is `Algorithm A` plus narrow Git `Algorithm B`, `Fast`)
- `US-5` -> `testdata/us5_rename_preserves_lineage` (`Shared US`, current active evidence is `Algorithm A` plus narrow Git `Algorithm B`, `Fast`)
- `US-6` -> `testdata/us6_period_added_ratio` (`Shared US`, current executable path is `Algorithm B`, `Fast`)
- `US-7` -> `testdata/us7_mixed_multi_commit_window` (`Shared US`, current active evidence is `Algorithm A` plus narrow Git `Algorithm B`, `Fast`)
- `US-8` -> `testdata/us8_merge_commit_preserves_attribution` (`Shared US`, current active evidence is `Algorithm A` plus narrow Git `Algorithm B`, `Fast`)
- `US-9` -> `testdata/us9_svn_contract_parity` (`Shared contract story`, current active evidence is Git/SVN parity through `Algorithm A` plus narrow Git/SVN `Algorithm B` parity on the approved `US-1` baseline shape, `Fast`)
- `US-10` -> `testdata/us10_large_repository_snapshot` (`Shared US`, current active evidence is `Algorithm A` plus narrow Git `Algorithm B`, `Fast`)
- `US-11` -> `testdata/us11_deep_history_preserves_attribution` (`Shared US`, current active evidence is `Algorithm A` plus narrow Git `Algorithm B`, `Fast`)
- `US-12` -> `testdata/us12_many_merged_branches_preserve_attribution` (`Shared US`, current active evidence is `Algorithm A` plus narrow Git `Algorithm B`, `Fast`)
- `US-13` -> production-scale Git local repository gate (`Heavy gate`, current active evidence is `Algorithm A`, daily integration candidate)
- `US-14` -> production-scale SVN local repository gate (`Heavy gate`, current active evidence is `Algorithm A`, daily integration candidate)

## Shared-US Convergence Order

- `Step 1`: keep `US-6` as the anchor shared story for the period-added metric and keep its narrow `Algorithm B` baseline defensible.
- `Step 2`: keep the current live-snapshot contract stories as shared stories, and only extend their `Algorithm B` claims where a matching narrow path is implemented and proven.
- `Step 3`: the approved live-snapshot subset now has narrow `Algorithm B` convergence across `US-1`, `US-2`, `US-3`, `US-4`, `US-5`, `US-7`, `US-8`, `US-10`, `US-11`, and `US-12`; any broader expansion should continue scenario-first.
- `Step 4`: treat `US-9` as a shared contract story whose first explicit split is Git vs SVN. The approved `US-1` baseline shape now has narrow Git/SVN `Algorithm B` parity, while broader algorithm convergence should still be added only scenario-first.
- `Step 5`: keep `US-13` and `US-14` as `Heavy` production gates rather than forcing them into the ordinary shared-story pattern.

The executable phase-by-phase roadmap for this sequence is documented in `README_SharedUS_Convergence.md`. For production-ready shared-story claims, the target is the full `Algorithm A`/`Algorithm B` x Git/SVN matrix unless an unsupported subset is explicitly accepted.

## Algorithm-B TDD Roadmap

The current repository no longer has only one explicit Algorithm-B story.
`US-6` remains the dedicated period-added baseline, and the approved live-snapshot shared-story subset (`US-1/2/3/4/5/7/8/9/10/11/12`) now has narrow fixture-driven `Algorithm B` acceptance.
That is still not enough to treat Algorithm B as implementation-ready.

Algorithm B should be expanded in TDD order with scenario-first contracts:

- `B0` contract lock: preserve the query/result envelope and define the exact semantic delta from Algorithm A.
- `B1` single-branch baseline: implement `period_added_ai_ratio` for one-branch histories with no merges or renames.
- `B2` mixed additions and deletions: prove how deleted, superseded, and partially rewritten in-window lines contribute to the period metric.
- `B3` rename handling: add Git rename and move scenarios before any copy-detection claim.
- `B4` merge-aware contribution accounting: add Git merge-window scenarios that force explicit contribution rules.
- `B5` SVN parity subset: add only the subset of SVN Algorithm-B behavior that can be defended under real SVN history semantics.
- `B6` scalability gate: add dedicated performance and large-history tests only after the correctness contract is stable.

Implemented scenario names:

- `US-15` -> `tests/test_us15_period_added_single_branch_baseline_tdd.py` (`Algorithm B`, local-git replay, `Fast`)
- `US-16` -> `tests/test_us16_period_added_deletions_and_rewrites_tdd.py` (`Algorithm B`, local-git replay, `Fast`)
- `US-17` -> `tests/test_us17_period_added_git_rename_tdd.py` (`Algorithm B`, local-git replay, `Fast`)
- `US-18` -> `tests/test_us18_period_added_merge_aware_tdd.py` (`Algorithm B`, local-git replay, `Fast`)
- `US-19` -> `tests/test_us19_period_added_svn_subset_tdd.py` (`Algorithm B`, offline SVN fixtures, `Fast`)

## User Stories

### US-1: Calculate Weighted AI Ratio For Live Changed Source Code In A Requested Time Window

**As a** repository analyst,
**I want** to calculate the weighted AI ratio for live source code lines whose current version falls in a requested period `startTime~endTime`,
**so that** I can know how much of the current live changed source code is attributable to AI.

Note: this should be treated as a shared live-snapshot contract story. The current repository now has accepted evidence across the full 2x2 `Algorithm A`/`Algorithm B` x Git/SVN matrix for the approved `US-1` baseline shape, with the `Algorithm B` cells still intentionally narrow live-snapshot replay slices.

#### Shared Acceptance Criteria For US-1

1. **GIVEN** a query `Repo:Branch:startTime:endTime`
   **WHEN** the user requests the AI code ratio
   **THEN** the system must return exactly one repository-level final result for that query, describing the AI ratio among live source code lines whose current version was added or modified in `startTime~endTime` as of `endTime`

2. **GIVEN** a set of revision-level `genCodeDesc` records stored outside the repository and indexed by `repoURL + repoBranch + revisionId`
   **WHEN** the analyzer discovers the in-scope origin revisions from the final live snapshot
   **THEN** it must fetch and use the matching external metadata records for those revisions during aggregation

3. **GIVEN** a successful result for `Repo:Branch:startTime:endTime`
   **WHEN** the result is returned or serialized as `genCodeDescProtocol.json`
   **THEN** it must be a final record in `genCodeDescProtocol.json` format, containing repository identity in `REPOSITORY` and aggregate final values in `SUMMARY`

4. **GIVEN** an algorithm-specific path that claims support for `US-1`
   **WHEN** that path is validated against an approved `US-1` scenario
   **THEN** the produced `SUMMARY` and `REPOSITORY` values must match the approved golden result for that scenario

#### Algorithm A Acceptance Track For US-1

1. **GIVEN** the fixture `testdata/us1_live_changed_source_ratio`
   **WHEN** the current `Algorithm A` implementation produces the final result
   **THEN** the produced `SUMMARY` and `REPOSITORY` values must match `expected_result.json`

2. **GIVEN** the supplementary SVN parity fixture `testdata/us1_live_changed_source_ratio_svn`
   **WHEN** the current `Algorithm A` implementation is exercised against the same baseline metric on SVN
   **THEN** the observable contract must remain aligned with the `US-1` shared acceptance criteria

#### Algorithm B Acceptance Track For US-1

1. **GIVEN** the fixture `testdata/us1_live_changed_source_ratio` together with its `commitDiffSet/` replay artifacts
   **WHEN** the current narrow `Algorithm B` live-snapshot path is executed for metric `live_changed_source_ratio` on Git
   **THEN** the produced `SUMMARY` and `REPOSITORY` values must match `expected_result.json`

2. **GIVEN** the fixture `testdata/us1_live_changed_source_ratio_svn` together with its `commitDiffSet/` replay artifacts
   **WHEN** the current narrow `Algorithm B` live-snapshot path is executed for metric `live_changed_source_ratio` on SVN
   **THEN** the produced `SUMMARY` and `REPOSITORY` values must match `expected_result.json`

3. **GIVEN** the current `Algorithm B` acceptance evidence for `US-1`
   **WHEN** that evidence is described in docs or roadmap discussions
   **THEN** it must be described as a narrow live-snapshot replay slice for the approved baseline fixture shape, not as a general-purpose replacement for all `Algorithm A` history handling

### US-2: Human Rewrite Removes Prior AI Attribution

**As a** repository analyst,
**I want** a human rewrite of a previously AI-generated line to reset attribution to the newer human revision,
**so that** old AI ownership does not remain attached to overwritten code.

Note: this should be treated as a shared overwrite-semantics story. The current repository now has accepted `Algorithm A` evidence plus a narrow Git `Algorithm B` replay slice for the approved baseline fixture shape.

#### Shared Acceptance Criteria For US-2

1. **GIVEN** a repository branch and a requested period `startTime~endTime`
   **WHEN** code previously attributed to AI has been superseded by later human revisions before `endTime`
   **THEN** the system must produce one final record for the live changed source code set at `endTime`, reflecting the newer repository state instead of preserving outdated AI ownership

2. **GIVEN** a successful result for `Repo:Branch:startTime:endTime`
   **WHEN** the result is returned or serialized as `genCodeDescProtocol.json`
   **THEN** it must be a final record in `genCodeDescProtocol.json` format, containing repository identity in `REPOSITORY` and aggregate final values in `SUMMARY`

3. **GIVEN** an algorithm-specific path that claims support for `US-2`
   **WHEN** that path is validated against an approved `US-2` scenario
   **THEN** the produced `SUMMARY` and `REPOSITORY` values must match the approved golden result for that scenario

#### Algorithm A Acceptance Track For US-2

1. **GIVEN** the fixture `testdata/us2_human_overwrites_ai_live_changed`
   **WHEN** the current `Algorithm A` implementation produces the final result
   **THEN** the produced `SUMMARY` and `REPOSITORY` values must match `expected_result.json`

#### Algorithm B Acceptance Track For US-2

1. **GIVEN** the fixture `testdata/us2_human_overwrites_ai_live_changed` together with its `commitDiffSet/` replay artifacts
   **WHEN** the current narrow `Algorithm B` live-snapshot path is executed on Git
   **THEN** the produced `SUMMARY` and `REPOSITORY` values must match `expected_result.json`

2. **GIVEN** the current `Algorithm B` acceptance evidence for `US-2`
   **WHEN** that evidence is described in docs or roadmap discussions
   **THEN** it must be described as a narrow Git live-snapshot replay slice for the approved baseline fixture shape, not as full matrix-ready overwrite support

### US-3: AI Rewrite Replaces Prior Human Ownership

**As a** repository analyst,
**I want** a later AI rewrite of a human line to become the effective attribution source,
**so that** the live changed source code at `endTime` reflects the latest AI contribution.

Note: this should be treated as a shared overwrite-semantics story. The current repository now has accepted `Algorithm A` evidence plus a narrow Git `Algorithm B` replay slice for the approved baseline fixture shape.

#### Shared Acceptance Criteria For US-3

1. **GIVEN** a repository branch and a requested period `startTime~endTime`
   **WHEN** later revisions introduce new AI-attributed code before `endTime`
   **THEN** the system must produce one final record that reflects that newer AI contribution in the live changed source code state at `endTime`

2. **GIVEN** a successful result for `Repo:Branch:startTime:endTime`
   **WHEN** the result is returned or serialized as `genCodeDescProtocol.json`
   **THEN** it must be a final record in `genCodeDescProtocol.json` format, containing repository identity in `REPOSITORY` and aggregate final values in `SUMMARY`

3. **GIVEN** an algorithm-specific path that claims support for `US-3`
   **WHEN** that path is validated against an approved `US-3` scenario
   **THEN** the produced `SUMMARY` and `REPOSITORY` values must match the approved golden result for that scenario

#### Algorithm A Acceptance Track For US-3

1. **GIVEN** the fixture `testdata/us3_ai_overwrites_human_live_changed`
   **WHEN** the current `Algorithm A` implementation produces the final result
   **THEN** the produced `SUMMARY` and `REPOSITORY` values must match `expected_result.json`

#### Algorithm B Acceptance Track For US-3

1. **GIVEN** the fixture `testdata/us3_ai_overwrites_human_live_changed` together with its `commitDiffSet/` replay artifacts
   **WHEN** the current narrow `Algorithm B` live-snapshot path is executed on Git
   **THEN** the produced `SUMMARY` and `REPOSITORY` values must match `expected_result.json`

2. **GIVEN** the current `Algorithm B` acceptance evidence for `US-3`
   **WHEN** that evidence is described in docs or roadmap discussions
   **THEN** it must be described as a narrow Git live-snapshot replay slice for the approved baseline fixture shape, not as full matrix-ready overwrite support

### US-4: Deleted AI Lines Must Not Count

**As a** repository analyst,
**I want** deleted AI-generated lines to disappear from both numerator and denominator,
**so that** the result reflects only the current live changed source code snapshot.

Note: this should be treated as a shared live-snapshot exclusion story. The current repository now has accepted `Algorithm A` evidence plus a narrow Git `Algorithm B` replay slice for the approved baseline fixture shape.

#### Shared Acceptance Criteria For US-4

1. **GIVEN** a repository branch and a requested period `startTime~endTime`
   **WHEN** some earlier AI-attributed code no longer exists in the branch state at `endTime`
   **THEN** the system must produce one final record that excludes that deleted code from the live changed source code result

2. **GIVEN** a successful result for `Repo:Branch:startTime:endTime`
   **WHEN** the result is returned or serialized as `genCodeDescProtocol.json`
   **THEN** it must be a final record in `genCodeDescProtocol.json` format, containing repository identity in `REPOSITORY` and aggregate final values in `SUMMARY`

3. **GIVEN** an algorithm-specific path that claims support for `US-4`
   **WHEN** that path is validated against an approved `US-4` scenario
   **THEN** the produced `SUMMARY` and `REPOSITORY` values must match the approved golden result for that scenario

#### Algorithm A Acceptance Track For US-4

1. **GIVEN** the fixture `testdata/us4_deleted_lines_excluded`
   **WHEN** the current `Algorithm A` implementation produces the final result
   **THEN** the produced `SUMMARY` and `REPOSITORY` values must match `expected_result.json`

#### Algorithm B Acceptance Track For US-4

1. **GIVEN** the fixture `testdata/us4_deleted_lines_excluded` together with its `commitDiffSet/` replay artifacts
   **WHEN** the current narrow `Algorithm B` live-snapshot path is executed on Git
   **THEN** the produced `SUMMARY` and `REPOSITORY` values must match `expected_result.json`

2. **GIVEN** the current `Algorithm B` acceptance evidence for `US-4`
   **WHEN** that evidence is described in docs or roadmap discussions
   **THEN** it must be described as a narrow Git live-snapshot replay slice for the approved baseline fixture shape, not as full matrix-ready deleted-line coverage

### US-5: Rename Must Preserve Attribution Lineage

**As a** repository analyst,
**I want** file rename or move operations to preserve line attribution when content does not change,
**so that** the final live changed source code ratio is not distorted by path-only history changes.

Note: this should be treated as a shared lineage-preservation story. The current repository now has accepted `Algorithm A` evidence plus a narrow Git `Algorithm B` replay slice for the approved baseline fixture shape.

#### Shared Acceptance Criteria For US-5

1. **GIVEN** a repository branch and a requested period `startTime~endTime`
   **WHEN** files are renamed or moved before `endTime` without changing their effective content contribution
   **THEN** the system must produce one final record that remains stable under path-only history changes in the live changed source code set at `endTime`

2. **GIVEN** a successful result for `Repo:Branch:startTime:endTime`
   **WHEN** the result is returned or serialized as `genCodeDescProtocol.json`
   **THEN** it must be a final record in `genCodeDescProtocol.json` format, containing repository identity in `REPOSITORY` and aggregate final values in `SUMMARY`

3. **GIVEN** an algorithm-specific path that claims support for `US-5`
   **WHEN** that path is validated against an approved `US-5` scenario
   **THEN** the produced `SUMMARY` and `REPOSITORY` values must match the approved golden result for that scenario

#### Algorithm A Acceptance Track For US-5

1. **GIVEN** the fixture `testdata/us5_rename_preserves_lineage`
   **WHEN** the current `Algorithm A` implementation produces the final result
   **THEN** the produced `SUMMARY` and `REPOSITORY` values must match `expected_result.json`

#### Algorithm B Acceptance Track For US-5

1. **GIVEN** the fixture `testdata/us5_rename_preserves_lineage` together with its `commitDiffSet/` replay artifacts
   **WHEN** the current narrow `Algorithm B` live-snapshot path is executed on Git
   **THEN** the produced `SUMMARY` and `REPOSITORY` values must match `expected_result.json`

2. **GIVEN** the current `Algorithm B` acceptance evidence for `US-5`
   **WHEN** that evidence is described in docs or roadmap discussions
   **THEN** it must be described as a narrow Git live-snapshot replay slice for the approved baseline fixture shape, not as full matrix-ready rename support

### US-6: Calculate AI-Added Ratio During The Requested Period

**As a** repository analyst,
**I want** to calculate how much AI-generated code was added during `startTime~endTime`,
**so that** I can distinguish period contribution from end-of-period inventory.

Note: this is not the current `P0 / Scope A` baseline metric. It is a separate history-oriented metric that should be treated as a shared user story, while allowing `Algorithm A` and `Algorithm B` to satisfy it through different acceptance tracks. The current implementation now includes a narrow executable Git baseline for `US-6` on the `Algorithm B` side, both through the approved fixture replay path and through the supported local-Git replay path.

#### Shared Acceptance Criteria For US-6

1. **GIVEN** a repository branch and a requested period `startTime~endTime`
   **WHEN** the user requests the period contribution metric
   **THEN** the system must return exactly one repository-level final result for that query window, describing the aggregate AI-added code result during that period

2. **GIVEN** a successful result for `Repo:Branch:startTime:endTime`
   **WHEN** the period contribution result is returned or serialized as `genCodeDescProtocol.json`
   **THEN** it must be a final record in `genCodeDescProtocol.json` format, containing repository identity in `REPOSITORY` and aggregate final values in `SUMMARY`

3. **GIVEN** an algorithm-specific implementation path that claims support for `US-6`
   **WHEN** that path is validated against an approved `US-6` scenario
   **THEN** the produced `SUMMARY` and `REPOSITORY` values must match the approved golden result for that scenario

#### Algorithm A Acceptance Track For US-6

1. **GIVEN** a future `Algorithm A` path that claims support for the period contribution metric
   **WHEN** that path is introduced
   **THEN** it must satisfy the shared `US-6` acceptance criteria without weakening the observable result contract

2. **GIVEN** a future `Algorithm A` fixture or real-repository acceptance scenario for `US-6`
   **WHEN** that scenario becomes active
   **THEN** it should be classified as `Fast` or `Heavy` explicitly, rather than being mixed implicitly into the current baseline suite

#### Algorithm B Acceptance Track For US-6

1. **GIVEN** the fixture `testdata/us6_period_added_ratio`
   **WHEN** the analyzer produces the final result through the current narrow offline Git baseline
   **THEN** the produced `SUMMARY` and `REPOSITORY` values must match `expected_result.json`

2. **GIVEN** the current CLI slice with `--algorithm B`
   **WHEN** the input follows the current narrow `US-6` Git replay boundary, either through `--commitDiffSetDir` or through a supported local Git checkout
   **THEN** the analyzer may execute the `US-6` offline Algorithm-B baseline under that same narrow support boundary

3. **GIVEN** broader Algorithm-B history shapes such as multi-file replay, rename/path changes, or merge-aware accounting
   **WHEN** the current CLI slice is used
   **THEN** those cases must remain explicitly unsupported until their own acceptance tracks are introduced and proven

### US-7: Resolve Mixed Multi-Commit History In One Requested Window

**As a** repository analyst,
**I want** one requested window to correctly resolve mixed line histories across many commits,
**so that** the final result remains correct when human-only lines, AI-only lines, human-then-AI rewrites, AI-then-human rewrites, and deleted AI lines all appear in the same period.

Note: this should be treated as a shared mixed-history story. The current repository now has accepted `Algorithm A` evidence plus a narrow Git `Algorithm B` replay slice for the approved baseline fixture shape.

#### Shared Acceptance Criteria For US-7

1. **GIVEN** a repository branch and a requested period `startTime~endTime`
   **WHEN** multiple commits inside that window contain mixed ownership transitions across different live lines
   **THEN** the system must produce exactly one final record for the live changed source code set at `endTime`, using the latest effective attribution of each surviving line

2. **GIVEN** a repository branch and a requested period `startTime~endTime`
   **WHEN** a surviving line has passed through a long chain of intermediate revisions inside that window
   **THEN** the system must still resolve that line by its latest effective live attribution at `endTime`, without leaking superseded intermediate ownership into the final result

3. **GIVEN** a successful result for `Repo:Branch:startTime:endTime`
   **WHEN** the result is returned or serialized as `genCodeDescProtocol.json`
   **THEN** it must be a final record in `genCodeDescProtocol.json` format, containing repository identity in `REPOSITORY` and aggregate final values in `SUMMARY`

4. **GIVEN** an algorithm-specific path that claims support for `US-7`
   **WHEN** that path is validated against an approved `US-7` scenario
   **THEN** the produced `SUMMARY` and `REPOSITORY` values must match the approved golden result for that scenario

#### Algorithm A Acceptance Track For US-7

1. **GIVEN** the fixture `testdata/us7_mixed_multi_commit_window`
   **WHEN** the current `Algorithm A` implementation produces the final result
   **THEN** the produced `SUMMARY` and `REPOSITORY` values must match `expected_result.json`

#### Algorithm B Acceptance Track For US-7

1. **GIVEN** the fixture `testdata/us7_mixed_multi_commit_window` together with its `commitDiffSet/` replay artifacts
   **WHEN** the current narrow `Algorithm B` live-snapshot path is executed on Git
   **THEN** the produced `SUMMARY` and `REPOSITORY` values must match `expected_result.json`

2. **GIVEN** the current `Algorithm B` acceptance evidence for `US-7`
   **WHEN** that evidence is described in docs or roadmap discussions
   **THEN** it must be described as a narrow Git live-snapshot replay slice for the approved baseline fixture shape, not as full matrix-ready mixed-history support

### US-8: Merge Commit Must Preserve Effective Attribution

**As a** repository analyst,
**I want** merged branch content to preserve the effective attribution of surviving lines,
**so that** a merge operation does not incorrectly reset line ownership to the merge commit itself.

Note: this should be treated as a shared merge-semantics story. The current repository now has accepted `Algorithm A` evidence plus a narrow Git `Algorithm B` replay slice for the approved baseline fixture shape.

#### Shared Acceptance Criteria For US-8

1. **GIVEN** a repository branch and a requested period `startTime~endTime`
   **WHEN** a merge commit brings together earlier human and AI-attributed changes before `endTime`
   **THEN** the system must produce one final record for the live changed source code set at `endTime`, using the effective attribution of the surviving merged lines rather than treating the merge commit as a blanket origin

2. **GIVEN** a repository branch and a requested period `startTime~endTime`
   **WHEN** multiple branches are merged into the target branch before `endTime` and surviving lines originate from different merged branches
   **THEN** the system must preserve the effective attribution of each surviving line independently, without collapsing ownership to merge commits or to the final branch identity alone

3. **GIVEN** a successful result for `Repo:Branch:startTime:endTime`
   **WHEN** the result is returned or serialized as `genCodeDescProtocol.json`
   **THEN** it must be a final record in `genCodeDescProtocol.json` format, containing repository identity in `REPOSITORY` and aggregate final values in `SUMMARY`

4. **GIVEN** an algorithm-specific path that claims support for `US-8`
   **WHEN** that path is validated against an approved `US-8` scenario
   **THEN** the produced `SUMMARY` and `REPOSITORY` values must match the approved golden result for that scenario

#### Algorithm A Acceptance Track For US-8

1. **GIVEN** the fixture `testdata/us8_merge_commit_preserves_attribution`
   **WHEN** the current `Algorithm A` implementation produces the final result
   **THEN** the produced `SUMMARY` and `REPOSITORY` values must match `expected_result.json`

#### Algorithm B Acceptance Track For US-8

1. **GIVEN** the fixture `testdata/us8_merge_commit_preserves_attribution` together with its `commitDiffSet/` replay artifacts
   **WHEN** the current narrow `Algorithm B` live-snapshot path is executed on Git
   **THEN** the produced `SUMMARY` and `REPOSITORY` values must match `expected_result.json`

2. **GIVEN** the current `Algorithm B` acceptance evidence for `US-8`
   **WHEN** that evidence is described in docs or roadmap discussions
   **THEN** it must be described as a narrow Git live-snapshot replay slice for the approved baseline fixture shape, not as full matrix-ready merge-topology support

### US-9: Git And SVN Must Follow The Same Result Contract

**As a** repository analyst,
**I want** Git and SVN targets to follow the same query/result contract for the current primary metric,
**so that** changing VCS type does not change the metric semantics or output structure.

Note: this is a shared contract story whose first explicit split is by VCS target. The current repository has Git/SVN acceptance evidence through `Algorithm A`, and it now also has narrow Git/SVN `Algorithm B` contract-parity evidence on the approved `US-1` baseline fixture shape.

#### Shared Acceptance Criteria For US-9

1. **GIVEN** equivalent repository history represented in a supported VCS target and a requested period `startTime~endTime`
   **WHEN** the user requests the current primary metric
   **THEN** the system must produce one final record with the same metric semantics and the same protocol-shaped output structure, differing only in VCS-specific repository identity such as `vcsType`, branch-path conventions, or `revisionId`

2. **GIVEN** a successful result for `Repo:Branch:startTime:endTime`
   **WHEN** the result is returned or serialized as `genCodeDescProtocol.json`
   **THEN** it must be a final record in `genCodeDescProtocol.json` format, containing repository identity in `REPOSITORY` and aggregate final values in `SUMMARY`

3. **GIVEN** a supported VCS-specific path that claims support for `US-9`
   **WHEN** that path is validated against an approved parity scenario
   **THEN** the produced `SUMMARY` and `REPOSITORY` values must match the approved golden result for that scenario

#### Git Acceptance Track For US-9

1. **GIVEN** the current Git path for the primary metric
   **WHEN** it is validated through the baseline live-snapshot scenarios
   **THEN** it acts as one side of the `US-9` parity contract and defines the observable Git result semantics to be matched

#### SVN Acceptance Track For US-9

1. **GIVEN** the fixture `testdata/us9_svn_contract_parity`
   **WHEN** the current SVN path produces the final result
   **THEN** the produced `SUMMARY` and `REPOSITORY` values must match `expected_result.json` while preserving the shared `US-9` contract

2. **GIVEN** VCS-specific path-history or blame differences
   **WHEN** SVN scenarios are designed for parity validation
   **THEN** they may use defensible SVN-specific repository shapes as long as the observable result contract remains the same

#### Algorithm Convergence Note For US-9

1. **GIVEN** the approved narrow `Algorithm B` Git and SVN live-snapshot fixture paths for `US-1`
   **WHEN** they are used as the current parity scenario for `US-9`
   **THEN** they must produce the same protocol-shaped observable contract across Git and SVN, differing only in VCS-specific repository identity fields

2. **GIVEN** the current `Algorithm B` evidence for `US-9`
   **WHEN** that evidence is described in docs or roadmap discussions
   **THEN** it must be described as narrow parity on the approved `US-1` baseline shape, not as full matrix-ready cross-story Git/SVN parity for every supported topology

### US-10: Large Repository Snapshot Must Preserve Result Semantics

**As a** repository analyst,
**I want** the analyzer to keep the same result semantics when the repository contains many source files and many live lines,
**so that** the final aggregate result remains correct for realistic large codebases.

Note: this should be treated as a shared scale-semantics story. The current repository now has accepted `Algorithm A` evidence plus a narrow Git `Algorithm B` replay slice for the approved baseline fixture shape.

#### Shared Acceptance Criteria For US-10

1. **GIVEN** a repository branch and a requested period `startTime~endTime`
   **WHEN** the final live snapshot at `endTime` spans many source files and many live code lines
   **THEN** the system must still produce exactly one repository-level final result with the same metric semantics and protocol-shaped structure as smaller repositories

2. **GIVEN** a large repository snapshot containing many in-scope lines across many files
   **WHEN** the analyzer aggregates the result
   **THEN** file count or repository size must not change the per-line attribution rules, the repository identity rules, or the meaning of the final `SUMMARY` fields

3. **GIVEN** an algorithm-specific path that claims support for `US-10`
   **WHEN** that path is validated against an approved `US-10` scenario
   **THEN** the produced `SUMMARY` and `REPOSITORY` values must match the approved golden result for that scenario

#### Algorithm A Acceptance Track For US-10

1. **GIVEN** the fixture `testdata/us10_large_repository_snapshot`
   **WHEN** the current `Algorithm A` implementation produces the final result
   **THEN** the produced `SUMMARY` and `REPOSITORY` values must match `expected_result.json`

#### Algorithm B Acceptance Track For US-10

1. **GIVEN** the approved `US-10` baseline shape, either through fixture replay artifacts or through the focused real local-Git replay path
   **WHEN** the current narrow `Algorithm B` live-snapshot path is executed on Git
   **THEN** the produced `SUMMARY` and `REPOSITORY` values must match `expected_result.json`

2. **GIVEN** the current `Algorithm B` acceptance evidence for `US-10`
   **WHEN** that evidence is described in docs or roadmap discussions
   **THEN** it must be described as a narrow Git live-snapshot replay slice for the approved baseline shape, with focused real local-Git proof, not as full matrix-ready large-snapshot scalability support

### US-11: Deep History Must Preserve Latest Effective Attribution

**As a** repository analyst,
**I want** long revision chains to preserve the latest effective attribution of each surviving line,
**so that** many intermediate rewrites do not distort the final live result.

Note: this should be treated as a shared deep-history story. The current repository now has accepted `Algorithm A` evidence plus a narrow Git `Algorithm B` replay slice for the approved baseline fixture shape.

#### Shared Acceptance Criteria For US-11

1. **GIVEN** a repository branch and a requested period `startTime~endTime`
   **WHEN** the in-scope live lines at `endTime` depend on long revision chains with many intermediate rewrites
   **THEN** the system must resolve each surviving line by its latest effective live attribution rather than by earlier superseded revisions in the chain

2. **GIVEN** a repository branch and a requested period `startTime~endTime`
   **WHEN** long history chains contain both human-to-AI and AI-to-human transitions before `endTime`
   **THEN** deleted or superseded intermediate states must not leak into the final aggregate result

3. **GIVEN** an algorithm-specific path that claims support for `US-11`
   **WHEN** that path is validated against an approved `US-11` scenario
   **THEN** the produced `SUMMARY` and `REPOSITORY` values must match the approved golden result for that scenario

#### Algorithm A Acceptance Track For US-11

1. **GIVEN** the fixture `testdata/us11_deep_history_preserves_attribution`
   **WHEN** the current `Algorithm A` implementation produces the final result
   **THEN** the produced `SUMMARY` and `REPOSITORY` values must match `expected_result.json`

#### Algorithm B Acceptance Track For US-11

1. **GIVEN** the approved `US-11` baseline shape, either through fixture replay artifacts or through the focused real local-Git replay path
   **WHEN** the current narrow `Algorithm B` live-snapshot path is executed on Git
   **THEN** the produced `SUMMARY` and `REPOSITORY` values must match `expected_result.json`

2. **GIVEN** the current `Algorithm B` acceptance evidence for `US-11`
   **WHEN** that evidence is described in docs or roadmap discussions
   **THEN** it must be described as a narrow Git live-snapshot replay slice for the approved baseline shape, with focused real local-Git proof, not as full matrix-ready deep-history support

### US-12: Many Merged Branches In One Window Must Preserve Per-Line Attribution

**As a** repository analyst,
**I want** branch-heavy history inside one requested window to preserve per-line effective attribution,
**so that** integrating many feature branches into the target branch does not distort the final result.

Note: this should be treated as a shared branch-heavy story. The current repository now has accepted `Algorithm A` evidence plus a narrow Git `Algorithm B` replay slice for the approved baseline fixture shape, and SVN parity for the same broad claim may still require a defensible analogue rather than a literal Git port.

#### Shared Acceptance Criteria For US-12

1. **GIVEN** a repository branch and a requested period `startTime~endTime`
   **WHEN** many branches are merged into the target branch before `endTime`
   **THEN** the system must still produce exactly one repository-level final result for the live changed source code set at `endTime`

2. **GIVEN** multiple merged branches inside one requested window
   **WHEN** surviving lines originate from different merged branches with different effective attribution histories
   **THEN** the system must preserve the effective attribution of each surviving line independently and must not flatten ownership to merge commits, branch labels, or merge order alone

3. **GIVEN** an algorithm-specific path that claims support for `US-12`
   **WHEN** that path is validated against an approved `US-12` scenario
   **THEN** the produced `SUMMARY` and `REPOSITORY` values must match the approved golden result for that scenario

#### Algorithm A Acceptance Track For US-12

1. **GIVEN** the fixture `testdata/us12_many_merged_branches_preserve_attribution`
   **WHEN** the current `Algorithm A` implementation produces the final result
   **THEN** the produced `SUMMARY` and `REPOSITORY` values must match `expected_result.json`

2. **GIVEN** SVN branch-heavy parity for the same broad contract
   **WHEN** real SVN blame semantics make a literal same-file Git port misleading
   **THEN** a defensible SVN-specific analogue may be used instead, as long as the shared `US-12` observable contract is preserved

#### Algorithm B Acceptance Track For US-12

1. **GIVEN** the fixture `testdata/us12_many_merged_branches_preserve_attribution` together with its `commitDiffSet/` replay artifacts
   **WHEN** the current narrow `Algorithm B` live-snapshot path is executed on Git
   **THEN** the produced `SUMMARY` and `REPOSITORY` values must match `expected_result.json`

2. **GIVEN** the current `Algorithm B` acceptance evidence for `US-12`
   **WHEN** that evidence is described in docs or roadmap discussions
   **THEN** it must be described as a narrow Git live-snapshot replay slice for the approved baseline fixture shape, not as full matrix-ready branch-heavy merge support

## Heavy Production Gates

The following items are intentionally treated as `Heavy` production gates rather than ordinary shared functional stories. They should remain explicit operational acceptance targets while shared-story convergence proceeds first on `US-6` and the smaller `Fast` stories.

### US-13: Git Production-Scale Local Repository Must Stay Correct Under Branch-Heavy Release Convergence

**As a** repository analyst,
**I want** Algorithm A and Scope A to remain correct on a production-scale local Git repository,
**so that** large branch counts, deep history, and hybrid release merges do not distort the final live attribution result.

#### Acceptance Criteria For US-13

1. **GIVEN** a local Git repository that represents a production-like topology
   **WHEN** it contains on the order of `100+` branches, `1000+` commits, and repeated feature-to-integration-to-release merge fan-in before `endTime`
   **THEN** the system must still compute exactly one repository-level final result for the live changed source-code set at `endTime`

2. **GIVEN** the same production-like local Git repository
   **WHEN** surviving lines originate from different feature branches and reach the release branch through mixed direct merges, integration branches, and staged convergence
   **THEN** the final attribution must be based on each surviving line's effective origin revision rather than merge commit shape, first-parent history alone, or branch naming conventions

3. **GIVEN** the same production-like local Git repository
   **WHEN** the repository is local rather than remote-hosted
   **THEN** the scenario is still a valid production-readiness acceptance case for this analyzer because repository transport is out of scope and history semantics must remain identical apart from network access

4. **GIVEN** the Git production-scale acceptance scenario
   **WHEN** the analyzer completes successfully
   **THEN** the test must verify both correctness of the final aggregate result and scalability-oriented behavior such as bounded metadata reuse, bounded revision-time lookup reuse, or other explicit reuse signals defined by the test harness

### US-14: SVN Production-Scale Local Repository Must Stay Correct Under Branch And Merge Pressure

**As a** repository analyst,
**I want** Algorithm A and Scope A to remain correct on a production-scale local SVN repository,
**so that** SVN branch copying, merges, and release reintegration at scale do not break live attribution.

#### Acceptance Criteria For US-14

1. **GIVEN** a local SVN repository that represents a production-like topology
   **WHEN** it contains on the order of `100+` branches or branch copies, `1000+` revisions, and repeated branch-to-release merge activity before `endTime`
   **THEN** the system must still compute exactly one repository-level final result for the live changed source-code set at `endTime`

2. **GIVEN** the same production-like local SVN repository
   **WHEN** surviving lines reach the release path through mixed direct work, branch copies, and merge or reintegration history
   **THEN** the final attribution must preserve each surviving line's effective origin revision within the supported SVN blame semantics and must not collapse ownership to merge timing or final branch path alone

3. **GIVEN** the same production-like local SVN repository
   **WHEN** the repository is local rather than remote-hosted
   **THEN** the scenario is still a valid production-readiness acceptance case for this analyzer because network transport is not part of the attribution contract

4. **GIVEN** the SVN production-scale acceptance scenario
   **WHEN** the analyzer completes successfully
   **THEN** the test must verify both correctness of the final aggregate result and scalability-oriented behavior such as reuse of branch-origin metadata lookups, bounded revision-time queries, or other explicit reuse signals defined by the test harness

## Scope Expansion Stories

The following stories extend the analyzer beyond the original `Scope A` (pure source code) baseline to cover broader line-type classifications. These are orthogonal to the Algorithm A/B axis — scope controls which files and line types are counted, while the algorithm controls how origin attribution is computed.

### US-20: Scope B Source Code With Comments Must Include Comment Lines In Totals

**As a** repository analyst,
**I want** `--scope B` to count all non-blank lines in source files — including comment lines — in the aggregate result,
**so that** I can measure AI contribution across the full textual content of source files, not just executable code.

#### Acceptance Criteria For US-20

1. **GIVEN** a source file containing both code lines and comment lines
   **WHEN** the analyzer runs with `--scope B`
   **THEN** `totalCodeLines` must include all non-blank lines (code and comments) rather than only the code-only subset counted by `Scope A`

2. **GIVEN** a `genCodeDesc` protocol with `codeLines` entries that cover comment lines in a source file
   **WHEN** the analyzer attributes those lines under `--scope B`
   **THEN** comment lines with `genRatio 100` must count as `fullGeneratedCodeLines` and comment lines with `genRatio` between 1 and 99 must count as `partialGeneratedCodeLines`

3. **GIVEN** the same repository and metadata
   **WHEN** the analyzer runs with `--scope A` instead of `--scope B`
   **THEN** comment lines must still be excluded from the totals, confirming backward compatibility

Fixture: `testdata/us20_scope_b_source_with_comments`

### US-21: Scope C Documentation Text Lines Must Be Counted From Doc Files Using docLines Protocol

**As a** repository analyst,
**I want** `--scope C` to analyze documentation text files (such as `.md`, `.rst`, `.txt`) and use the `docLines` protocol field for AI attribution,
**so that** I can measure AI contribution to documentation artifacts separately from source code.

#### Acceptance Criteria For US-21

1. **GIVEN** a repository containing documentation files with extensions in the `DOC_EXTENSIONS` set (`.md`, `.rst`, `.txt`)
   **WHEN** the analyzer runs with `--scope C`
   **THEN** the file listing must include only documentation files, not source code files

2. **GIVEN** a `genCodeDesc` protocol with `docLines` entries for a documentation file
   **WHEN** the analyzer attributes those lines under `--scope C`
   **THEN** the output must use `totalDocLines`, `fullGeneratedDocLines`, and `partialGeneratedDocLines` instead of the `*CodeLines` field names

3. **GIVEN** the same repository containing both source and documentation files
   **WHEN** the analyzer runs with `--scope A` or `--scope B`
   **THEN** documentation files must not appear in the analysis, confirming scope isolation

Fixture: `testdata/us21_scope_c_doc_lines`

### US-22: Scope D All Text Must Unify Source And Documentation Files Into A Single Aggregate

**As a** repository analyst,
**I want** `--scope D` to count all non-blank lines from both source files and documentation files in one combined result,
**so that** I can measure total AI contribution across the entire textual content of the repository.

#### Acceptance Criteria For US-22

1. **GIVEN** a repository containing both source files and documentation files
   **WHEN** the analyzer runs with `--scope D`
   **THEN** the file listing must include both source files (matching `SOURCE_EXTENSIONS`) and documentation files (matching `DOC_EXTENSIONS`)

2. **GIVEN** a `genCodeDesc` protocol with `codeLines` for source files and `docLines` for documentation files
   **WHEN** the analyzer attributes lines under `--scope D`
   **THEN** source file lines must be attributed using `codeLines` and documentation file lines must be attributed using `docLines`, with the combined result using `totalCodeLines`, `fullGeneratedCodeLines`, `partialGeneratedCodeLines`

3. **GIVEN** the same repository
   **WHEN** the analyzer runs with `--scope A`, `--scope B`, or `--scope C`
   **THEN** the result must not include files from the other scope family, confirming scope isolation

Fixture: `testdata/us22_scope_d_all_text`

### US-23: Scope Parity Matrix Must Confirm All Four Scopes Produce Correct And Isolated Results

**As a** repository analyst,
**I want** a cross-scope verification that runs Scope A, B, C, and D on the same repository and confirms each produces the expected distinct result,
**so that** I can trust that scope selection genuinely controls the measurement boundary.

#### Acceptance Criteria For US-23

1. **GIVEN** a repository with both source files (containing code and comment lines) and documentation files
   **WHEN** the analyzer runs four times with `--scope A`, `--scope B`, `--scope C`, and `--scope D`
   **THEN** each scope must produce a correct summary matching its definition:
   - Scope A: only code lines from source files
   - Scope B: all non-blank lines from source files
   - Scope C: all non-blank lines from doc files (with Doc field names)
   - Scope D: all non-blank lines from both source and doc files

2. **GIVEN** the four scope results
   **WHEN** compared for output field name families
   **THEN** Scope C must use `totalDocLines` / `fullGeneratedDocLines` / `partialGeneratedDocLines` while Scopes A, B, and D must use `totalCodeLines` / `fullGeneratedCodeLines` / `partialGeneratedCodeLines`

Fixture: `testdata/us23_scope_parity_matrix`

### Algorithm-B Scope Broadening Stories

#### US-24: Algorithm B Must Support Scope B (Source Files Including Comments)

**As a** repository analyst,
**I want** `--algorithm B --scope B` to count all non-blank source lines including comments during replay,
**so that** I can measure total AI contribution to all source text using the incremental replay algorithm.

##### Acceptance Criteria For US-24

1. **GIVEN** a source file with code and comment lines
   **WHEN** Algorithm B runs with `--scope B`
   **THEN** `totalCodeLines` must include all non-blank lines (code + comments)

Test: `tests/test_us24_algorithm_b_scope_b_tdd.py`

#### US-25: Algorithm B Must Support Scope C (Documentation Files)

**As a** repository analyst,
**I want** `--algorithm B --scope C` to replay and count documentation file lines using the `docLines` protocol field,
**so that** I can measure AI contribution to documentation using the incremental replay algorithm.

##### Acceptance Criteria For US-25

1. **GIVEN** a documentation file (`.md`) with non-blank lines
   **WHEN** Algorithm B runs with `--scope C`
   **THEN** the output uses `totalDocLines` / `fullGeneratedDocLines` / `partialGeneratedDocLines` field names

2. **GIVEN** the protocol DETAIL entry for the doc file uses `docLines` (not `codeLines`)
   **WHEN** Algorithm B attributes gen-ratios during replay
   **THEN** the doc protocol index is used for line-ratio lookup

Test: `tests/test_us25_algorithm_b_scope_c_tdd.py`

#### US-26: Algorithm B Must Support Scope D (Union Of Source And Documentation)

**As a** repository analyst,
**I want** `--algorithm B --scope D` to replay both source files and documentation files into a unified result,
**so that** I can measure total AI contribution across all textual repository content using the incremental replay algorithm.

##### Acceptance Criteria For US-26

1. **GIVEN** a repository with both source files and documentation files
   **WHEN** Algorithm B runs with `--scope D`
   **THEN** replay must include both source and doc files, using `codeLines` for source and `docLines` for doc files

2. **GIVEN** the combined replay
   **WHEN** the summary is computed
   **THEN** the output uses `totalCodeLines` / `fullGeneratedCodeLines` / `partialGeneratedCodeLines` field names

Test: `tests/test_us26_algorithm_b_scope_d_tdd.py`

### Cross-Algorithm Scope Parity Stories

#### US-27: Algorithm A And Algorithm B Must Produce Identical SUMMARY For Every Scope

**As a** repository analyst,
**I want** Algorithm A (blame-based) and Algorithm B (replay-based) to produce the same SUMMARY for every scope (A, B, C, D) on the same repository content,
**so that** I can trust that the choice of algorithm does not change the measurement result.

##### Acceptance Criteria For US-27

1. **GIVEN** a repository with source files (code + comments) and documentation files
   **WHEN** both Algorithm A and Algorithm B analyze the same content with `--scope A`
   **THEN** both must produce identical `totalCodeLines`, `fullGeneratedCodeLines`, `partialGeneratedCodeLines`

2. **GIVEN** the same repository
   **WHEN** both algorithms analyze with `--scope B`, `--scope C`, and `--scope D`
   **THEN** each scope must produce identical SUMMARY between algorithms, including correct field name families (Doc vs Code)

3. **GIVEN** both algorithm results
   **WHEN** compared for protocol contract shape
   **THEN** `protocolName` and `protocolVersion` must match across algorithms for every scope

Test: `tests/test_us27_cross_algorithm_scope_parity_tdd.py`

#### US-28: Production Hardening — Scope Validation And File-Size Guard

**As a** CLI operator,
**I want** invalid `--scope` values to be rejected at input validation and oversized VCS outputs to be caught before processing,
**so that** the tool fails fast with clear diagnostics instead of producing silent wrong results or running out of memory.

##### Acceptance Criteria For US-28

1. **GIVEN** an invalid `--scope` value (e.g. `Z`, `a`, empty string)
   **WHEN** invoking the CLI with either `--algorithm A` or `--algorithm B`
   **THEN** the tool exits with `EXIT_INPUT_ERROR` and a message containing `--scope must be one of: A, B, C, D`

2. **GIVEN** a git repository containing a file whose `git show` output exceeds `MAX_FILE_SIZE_BYTES` (100 MB)
   **WHEN** Algorithm B calls `read_git_file_lines_at_revision`
   **THEN** a `RepositoryStateError` is raised with a clear diagnostic

3. **GIVEN** a git repository where `git blame --line-porcelain` output exceeds `MAX_FILE_SIZE_BYTES`
   **WHEN** Algorithm A calls `parse_blame`
   **THEN** a `RepositoryStateError` is raised with a clear diagnostic

Test: `tests/test_us28_production_hardening_tdd.py`

### US-15: Single-Branch Period-Added Baseline Without Merges Or Renames

**Algorithm B** period-added metric on a single-branch linear Git history.

#### Acceptance Criteria

1. **GIVEN** a single-branch Git repository with 1 pre-window commit (human) and 2 in-window commits (AI + human)
   **WHEN** the tool runs with `--algorithm B --metric period_added_ai_ratio`
   **THEN** `totalCodeLines` counts only lines originated by in-window commits, pre-window lines are excluded, and `fullGeneratedCodeLines` counts only the AI-attributed lines

2. **GIVEN** Scope B (source + comments)
   **WHEN** the same repository is analyzed
   **THEN** results correctly reflect the scope without changing period-added semantics

Test: `tests/test_us15_period_added_single_branch_baseline_tdd.py`

### US-16: Period-Added Accounting With Deletions, Resets, And Mixed Rewrites

**Algorithm B** period-added metric with deletions and AI↔human rewrites inside one window.

#### Acceptance Criteria

1. **GIVEN** an AI line added in-window then deleted/replaced by a later in-window commit
   **WHEN** the tool runs with period-added metric
   **THEN** the deleted AI line does NOT appear in the result

2. **GIVEN** a pre-window human line rewritten in-window
   **WHEN** the origin shifts to the rewriting commit
   **THEN** the line is counted as in-window with the rewriter's attribution

Test: `tests/test_us16_period_added_deletions_and_rewrites_tdd.py`

### US-17: Git Rename And Move Handling For Period Contribution

**Algorithm B** period-added metric correctly tracks lines across file renames.

#### Acceptance Criteria

1. **GIVEN** a file renamed in-window with a new AI line added
   **WHEN** the tool runs with period-added metric
   **THEN** only the new line counts; pre-window lines that survived the rename are excluded

Test: `tests/test_us17_period_added_git_rename_tdd.py`

### US-18: Merge-Aware Git Period Contribution Inside One Window

**Algorithm B** period-added metric with branch-and-merge topology inside the window.

#### Acceptance Criteria

1. **GIVEN** AI lines added on main and a feature branch, then merged (no-ff) in-window
   **WHEN** the tool runs with period-added metric
   **THEN** both branch contributions survive the merge and count correctly

Test: `tests/test_us18_period_added_merge_aware_tdd.py`

### US-19: SVN-Supported Subset For Algorithm-B Period Contribution

**Algorithm B** period-added metric for SVN repositories via the offline fixtures path.

#### Acceptance Criteria

1. **GIVEN** SVN-style offline commit diff fixtures with 2 revisions and protocol files
   **WHEN** the tool runs with `--vcsType svn --algorithm B --metric period_added_ai_ratio --commitDiffSetDir`
   **THEN** the period-added result correctly counts AI vs human lines from the SVN patches

Test: `tests/test_us19_period_added_svn_subset_tdd.py`

### US-29: Info-Level Log Must Show Initial Load, Per-Line State Transition, And Final Summary

**As a** CLI operator running with `--logLevel info`,
**I want** to see a three-phase narrative on stderr: (1) initial load state showing what was resolved, (2) per-line state transition hints showing which live lines transferred from AI to human or human to AI, and (3) a final summary of the aggregate result,
**so that** I can understand the full attribution story without switching to `--logLevel debug`.

#### Rationale

Before US-29, `--logLevel info` emitted `LiveLine` classification per line and a start/finish banner but omitted the `TransitionHint` that revealed state transfers between revisions.
US-29 promoted `TransitionHint` to info level so operators can answer "which lines changed ownership between AI and human?" without the noise of debug-only metadata loading, file scanning, and cache-reuse messages.

#### Acceptance Criteria For US-29

##### AC-29.1: Initial load state is visible at info level

**GIVEN** a valid analysis request with `--logLevel info`
**WHEN** the analysis begins
**THEN** stderr contains an `[INFO]` line matching `Starting analysis for repo=...` that includes `repo=`, `branch=`, `window=`, and `endRevision=`

##### AC-29.2: Per-line TransitionHint is emitted at info level

**GIVEN** a repository where at least one live line's current revision rewrites an earlier version (e.g. human→AI or AI→human)
**WHEN** the tool runs with `--logLevel info`
**THEN** stderr contains `[INFO]` lines with `TransitionHint` showing `best_effort_transition=` for each line whose parent-revision attribution differs from the current revision attribution

##### AC-29.3: Final summary is visible at info level

**GIVEN** a valid analysis request with `--logLevel info`
**WHEN** the analysis finishes
**THEN** stderr contains an `[INFO]` line matching `Finished analysis with totalCodeLines=...` that includes `totalCodeLines=`, `fullGeneratedCodeLines=`, `partialGeneratedCodeLines=`, and `elapsed=`

##### AC-29.4: TransitionHint is suppressed at quiet level

**GIVEN** the same repository as AC-29.2
**WHEN** the tool runs with `--logLevel quiet` (the default)
**THEN** stderr contains no `TransitionHint` lines and no `LiveLine` lines

##### AC-29.5: Debug level still shows all messages

**GIVEN** the same repository as AC-29.2
**WHEN** the tool runs with `--logLevel debug`
**THEN** stderr contains `[DEBUG]` lines for metadata loading (`Loaded genCodeDesc`), file scanning (`Scanning file`), out-of-window skips (`Skip out-of-window`), and cached-protocol reuse (`Reuse cached genCodeDesc`), in addition to all info-level lines including `TransitionHint`

##### AC-29.6: Human-overwrites-AI transition is visible at info level

**GIVEN** a `US-2`-shaped repository where a human commit overwrites a previously AI-generated line
**WHEN** the tool runs with `--logLevel info`
**THEN** stderr contains a `TransitionHint` line with `best_effort_transition=100%-ai->human/unattributed`

##### AC-29.7: AI-overwrites-human transition is visible at info level

**GIVEN** a `US-3`-shaped repository where an AI commit overwrites a previously human-written line
**WHEN** the tool runs with `--logLevel info`
**THEN** stderr contains a `TransitionHint` line with `best_effort_transition=human/unattributed->100%-ai`

Test: `tests/test_us29_info_level_log_narrative_tdd.py`
