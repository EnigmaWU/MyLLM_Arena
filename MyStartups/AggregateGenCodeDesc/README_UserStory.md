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
If a scenario expects revisions `r1..rn` to be replayed, every required replayed revision must have a matching raw patch artifact such as `<revisionId>_commitDiff.patch`.
A missing diff in the middle of a long sequence is a fixture contract failure, not an ignorable gap.

For planned future stories, the scenario name defines the intended verification target even if the concrete fixture or integration test has not been added yet.

Those `testdata/` scenarios are design-oriented fixtures.
Those local `genCodeDesc` files simulate the external metadata store used in real deployments.
For `Algorithm B`, local raw commit diff patch artifacts are also required in `testdata/` so replay completeness can be verified explicitly.
For real repository verification of `Algorithm A`, the preferred test layer is under `tests/`, where actual Git or SVN repositories are created and `*.diff` files are not required.

For production-oriented runs, the analyzer should discover relevant revisions from repository history first and then fetch matching `genCodeDesc` records from an external provider.

## Scenario Mapping

- `US-1` -> `testdata/us1_live_changed_source_ratio` (`Algorithm A`)
- `US-2` -> `testdata/us2_human_overwrites_ai_live_changed` (`Algorithm A`)
- `US-3` -> `testdata/us3_ai_overwrites_human_live_changed` (`Algorithm A`)
- `US-4` -> `testdata/us4_deleted_lines_excluded` (`Algorithm A`)
- `US-5` -> `testdata/us5_rename_preserves_lineage` (`Algorithm A`)
- `US-6` -> `testdata/us6_period_added_ratio` (`Algorithm B`)
- `US-7` -> `testdata/us7_mixed_multi_commit_window` (`Algorithm A`)
- `US-8` -> `testdata/us8_merge_commit_preserves_attribution` (`Algorithm A`)
- `US-9` -> `testdata/us9_svn_contract_parity` (`Algorithm A`)
- `US-10` -> `testdata/us10_large_repository_snapshot` (`Algorithm A`)
- `US-11` -> `testdata/us11_deep_history_preserves_attribution` (`Algorithm A`)
- `US-12` -> `testdata/us12_many_merged_branches_preserve_attribution` (`Algorithm A`)

## Algorithm-B TDD Roadmap

The current repository has only one explicit Algorithm-B story today: `US-6`.
That is not enough to treat Algorithm B as implementation-ready.

Algorithm B should be expanded in TDD order with scenario-first contracts:

- `B0` contract lock: preserve the query/result envelope and define the exact semantic delta from Algorithm A.
- `B1` single-branch baseline: implement `period_added_ai_ratio` for one-branch histories with no merges or renames.
- `B2` mixed additions and deletions: prove how deleted, superseded, and partially rewritten in-window lines contribute to the period metric.
- `B3` rename handling: add Git rename and move scenarios before any copy-detection claim.
- `B4` merge-aware contribution accounting: add Git merge-window scenarios that force explicit contribution rules.
- `B5` SVN parity subset: add only the subset of SVN Algorithm-B behavior that can be defended under real SVN history semantics.
- `B6` scalability gate: add dedicated performance and large-history tests only after the correctness contract is stable.

Recommended future scenario names:

- `US-15` -> `testdata/us15_period_added_single_branch_baseline` (`Algorithm B`)
- `US-16` -> `testdata/us16_period_added_with_deletions_and_resets` (`Algorithm B`)
- `US-17` -> `testdata/us17_period_added_git_rename_handling` (`Algorithm B`)
- `US-18` -> `testdata/us18_period_added_git_merge_window` (`Algorithm B`)
- `US-19` -> `testdata/us19_period_added_svn_supported_subset` (`Algorithm B`)

## User Stories

### US-1: Calculate Weighted AI Ratio For Live Changed Source Code In A Requested Time Window

**As a** repository analyst,
**I want** to calculate the weighted AI ratio for live source code lines whose current version falls in a requested period `startTime~endTime`,
**so that** I can know how much of the current live changed source code is attributable to AI.

#### Acceptance Criteria For US-1

1. **GIVEN** a query `Repo:Branch:startTime:endTime`
   **WHEN** the user requests the AI code ratio
   **THEN** the system must return exactly one repository-level final result for that query, describing the AI ratio among live source code lines whose current version was added or modified in `startTime~endTime` as of `endTime`

2. **GIVEN** a set of revision-level `genCodeDesc` records stored outside the repository and indexed by `repoURL + repoBranch + revisionId`
   **WHEN** the analyzer discovers the in-scope origin revisions from the final live snapshot
   **THEN** it must fetch and use the matching external metadata records for those revisions during aggregation

3. **GIVEN** a successful result for `Repo:Branch:startTime:endTime`
   **WHEN** the result is returned or serialized as `genCodeDescProtocol.json`
   **THEN** it must be a final record in `genCodeDescProtocol.json` format, containing repository identity in `REPOSITORY` and aggregate final values in `SUMMARY`

4. **GIVEN** the fixture `testdata/us1_live_changed_source_ratio`
   **WHEN** the analyzer produces the final result
   **THEN** the produced `SUMMARY` and `REPOSITORY` values must match `expected_result.json`

### US-2: Human Rewrite Removes Prior AI Attribution

**As a** repository analyst,
**I want** a human rewrite of a previously AI-generated line to reset attribution to the newer human revision,
**so that** old AI ownership does not remain attached to overwritten code.

#### Acceptance Criteria For US-2

1. **GIVEN** a repository branch and a requested period `startTime~endTime`
   **WHEN** code previously attributed to AI has been superseded by later human revisions before `endTime`
   **THEN** the system must produce one final record for the live changed source code set at `endTime`, reflecting the newer repository state instead of preserving outdated AI ownership

2. **GIVEN** a successful result for `Repo:Branch:startTime:endTime`
   **WHEN** the result is returned or serialized as `genCodeDescProtocol.json`
   **THEN** it must be a final record in `genCodeDescProtocol.json` format, containing repository identity in `REPOSITORY` and aggregate final values in `SUMMARY`

3. **GIVEN** the fixture `testdata/us2_human_overwrites_ai_live_changed`
   **WHEN** the analyzer produces the final result
   **THEN** the produced `SUMMARY` and `REPOSITORY` values must match `expected_result.json`

### US-3: AI Rewrite Replaces Prior Human Ownership

**As a** repository analyst,
**I want** a later AI rewrite of a human line to become the effective attribution source,
**so that** the live changed source code at `endTime` reflects the latest AI contribution.

#### Acceptance Criteria For US-3

1. **GIVEN** a repository branch and a requested period `startTime~endTime`
   **WHEN** later revisions introduce new AI-attributed code before `endTime`
   **THEN** the system must produce one final record that reflects that newer AI contribution in the live changed source code state at `endTime`

2. **GIVEN** a successful result for `Repo:Branch:startTime:endTime`
   **WHEN** the result is returned or serialized as `genCodeDescProtocol.json`
   **THEN** it must be a final record in `genCodeDescProtocol.json` format, containing repository identity in `REPOSITORY` and aggregate final values in `SUMMARY`

3. **GIVEN** the fixture `testdata/us3_ai_overwrites_human_live_changed`
   **WHEN** the analyzer produces the final result
   **THEN** the produced `SUMMARY` and `REPOSITORY` values must match `expected_result.json`

### US-4: Deleted AI Lines Must Not Count

**As a** repository analyst,
**I want** deleted AI-generated lines to disappear from both numerator and denominator,
**so that** the result reflects only the current live changed source code snapshot.

#### Acceptance Criteria For US-4

1. **GIVEN** a repository branch and a requested period `startTime~endTime`
   **WHEN** some earlier AI-attributed code no longer exists in the branch state at `endTime`
   **THEN** the system must produce one final record that excludes that deleted code from the live changed source code result

2. **GIVEN** a successful result for `Repo:Branch:startTime:endTime`
   **WHEN** the result is returned or serialized as `genCodeDescProtocol.json`
   **THEN** it must be a final record in `genCodeDescProtocol.json` format, containing repository identity in `REPOSITORY` and aggregate final values in `SUMMARY`

3. **GIVEN** the fixture `testdata/us4_deleted_lines_excluded`
   **WHEN** the analyzer produces the final result
   **THEN** the produced `SUMMARY` and `REPOSITORY` values must match `expected_result.json`

### US-5: Rename Must Preserve Attribution Lineage

**As a** repository analyst,
**I want** file rename or move operations to preserve line attribution when content does not change,
**so that** the final live changed source code ratio is not distorted by path-only history changes.

#### Acceptance Criteria For US-5

1. **GIVEN** a repository branch and a requested period `startTime~endTime`
   **WHEN** files are renamed or moved before `endTime` without changing their effective content contribution
   **THEN** the system must produce one final record that remains stable under path-only history changes in the live changed source code set at `endTime`

2. **GIVEN** a successful result for `Repo:Branch:startTime:endTime`
   **WHEN** the result is returned or serialized as `genCodeDescProtocol.json`
   **THEN** it must be a final record in `genCodeDescProtocol.json` format, containing repository identity in `REPOSITORY` and aggregate final values in `SUMMARY`

3. **GIVEN** the fixture `testdata/us5_rename_preserves_lineage`
   **WHEN** the analyzer produces the final result
   **THEN** the produced `SUMMARY` and `REPOSITORY` values must match `expected_result.json`

### US-6: Calculate AI-Added Ratio During The Requested Period

**As a** repository analyst,
**I want** to calculate how much AI-generated code was added during `startTime~endTime`,
**so that** I can distinguish period contribution from end-of-period inventory.

Note: this is not the current `P0 / Scope A` baseline metric. It is a separate history-oriented metric that may align better with `Algorithm B` or another future implementation.

#### Acceptance Criteria For US-6

1. **GIVEN** a repository branch and a requested period `startTime~endTime`
   **WHEN** the user requests the period contribution metric
   **THEN** the system must return exactly one repository-level final result for that query window, describing the aggregate AI-added code result during that period

2. **GIVEN** a successful result for `Repo:Branch:startTime:endTime`
   **WHEN** the period contribution result is returned or serialized as `genCodeDescProtocol.json`
   **THEN** it must be a final record in `genCodeDescProtocol.json` format, containing repository identity in `REPOSITORY` and aggregate final values in `SUMMARY`

3. **GIVEN** the fixture `testdata/us6_period_added_ratio`
   **WHEN** the analyzer produces the final result
   **THEN** the produced `SUMMARY` and `REPOSITORY` values must match `expected_result.json`

### US-7: Resolve Mixed Multi-Commit History In One Requested Window

**As a** repository analyst,
**I want** one requested window to correctly resolve mixed line histories across many commits,
**so that** the final result remains correct when human-only lines, AI-only lines, human-then-AI rewrites, AI-then-human rewrites, and deleted AI lines all appear in the same period.

#### Acceptance Criteria For US-7

1. **GIVEN** a repository branch and a requested period `startTime~endTime`
   **WHEN** multiple commits inside that window contain mixed ownership transitions across different live lines
   **THEN** the system must produce exactly one final record for the live changed source code set at `endTime`, using the latest effective attribution of each surviving line

2. **GIVEN** a repository branch and a requested period `startTime~endTime`
   **WHEN** a surviving line has passed through a long chain of intermediate revisions inside that window
   **THEN** the system must still resolve that line by its latest effective live attribution at `endTime`, without leaking superseded intermediate ownership into the final result

3. **GIVEN** a successful result for `Repo:Branch:startTime:endTime`
   **WHEN** the result is returned or serialized as `genCodeDescProtocol.json`
   **THEN** it must be a final record in `genCodeDescProtocol.json` format, containing repository identity in `REPOSITORY` and aggregate final values in `SUMMARY`

4. **GIVEN** the fixture `testdata/us7_mixed_multi_commit_window`
   **WHEN** the analyzer produces the final result
   **THEN** the produced `SUMMARY` and `REPOSITORY` values must match `expected_result.json`

### US-8: Merge Commit Must Preserve Effective Attribution

**As a** repository analyst,
**I want** merged branch content to preserve the effective attribution of surviving lines,
**so that** a merge operation does not incorrectly reset line ownership to the merge commit itself.

#### Acceptance Criteria For US-8

1. **GIVEN** a repository branch and a requested period `startTime~endTime`
   **WHEN** a merge commit brings together earlier human and AI-attributed changes before `endTime`
   **THEN** the system must produce one final record for the live changed source code set at `endTime`, using the effective attribution of the surviving merged lines rather than treating the merge commit as a blanket origin

2. **GIVEN** a repository branch and a requested period `startTime~endTime`
   **WHEN** multiple branches are merged into the target branch before `endTime` and surviving lines originate from different merged branches
   **THEN** the system must preserve the effective attribution of each surviving line independently, without collapsing ownership to merge commits or to the final branch identity alone

3. **GIVEN** a successful result for `Repo:Branch:startTime:endTime`
   **WHEN** the result is returned or serialized as `genCodeDescProtocol.json`
   **THEN** it must be a final record in `genCodeDescProtocol.json` format, containing repository identity in `REPOSITORY` and aggregate final values in `SUMMARY`

4. **GIVEN** the fixture `testdata/us8_merge_commit_preserves_attribution`
   **WHEN** the analyzer produces the final result
   **THEN** the produced `SUMMARY` and `REPOSITORY` values must match `expected_result.json`

### US-9: Git And SVN Must Follow The Same Result Contract

**As a** repository analyst,
**I want** Git and SVN targets to follow the same query/result contract for the current primary metric,
**so that** changing VCS type does not change the metric semantics or output structure.

#### Acceptance Criteria For US-9

1. **GIVEN** equivalent repository history represented in a supported VCS target and a requested period `startTime~endTime`
   **WHEN** the user requests the current primary metric
   **THEN** the system must produce one final record with the same metric semantics and the same protocol-shaped output structure, differing only in VCS-specific repository identity such as `vcsType`, branch-path conventions, or `revisionId`

2. **GIVEN** a successful result for `Repo:Branch:startTime:endTime`
   **WHEN** the result is returned or serialized as `genCodeDescProtocol.json`
   **THEN** it must be a final record in `genCodeDescProtocol.json` format, containing repository identity in `REPOSITORY` and aggregate final values in `SUMMARY`

3. **GIVEN** the fixture `testdata/us9_svn_contract_parity`
   **WHEN** the analyzer produces the final result
   **THEN** the produced `SUMMARY` and `REPOSITORY` values must match `expected_result.json`

### US-10: Large Repository Snapshot Must Preserve Result Semantics

**As a** repository analyst,
**I want** the analyzer to keep the same result semantics when the repository contains many source files and many live lines,
**so that** the final aggregate result remains correct for realistic large codebases.

#### Acceptance Criteria For US-10

1. **GIVEN** a repository branch and a requested period `startTime~endTime`
   **WHEN** the final live snapshot at `endTime` spans many source files and many live code lines
   **THEN** the system must still produce exactly one repository-level final result with the same metric semantics and protocol-shaped structure as smaller repositories

2. **GIVEN** a large repository snapshot containing many in-scope lines across many files
   **WHEN** the analyzer aggregates the result
   **THEN** file count or repository size must not change the per-line attribution rules, the repository identity rules, or the meaning of the final `SUMMARY` fields

3. **GIVEN** the fixture `testdata/us10_large_repository_snapshot`
   **WHEN** the analyzer produces the final result
   **THEN** the produced `SUMMARY` and `REPOSITORY` values must match `expected_result.json`

### US-11: Deep History Must Preserve Latest Effective Attribution

**As a** repository analyst,
**I want** long revision chains to preserve the latest effective attribution of each surviving line,
**so that** many intermediate rewrites do not distort the final live result.

#### Acceptance Criteria For US-11

1. **GIVEN** a repository branch and a requested period `startTime~endTime`
   **WHEN** the in-scope live lines at `endTime` depend on long revision chains with many intermediate rewrites
   **THEN** the system must resolve each surviving line by its latest effective live attribution rather than by earlier superseded revisions in the chain

2. **GIVEN** a repository branch and a requested period `startTime~endTime`
   **WHEN** long history chains contain both human-to-AI and AI-to-human transitions before `endTime`
   **THEN** deleted or superseded intermediate states must not leak into the final aggregate result

3. **GIVEN** the fixture `testdata/us11_deep_history_preserves_attribution`
   **WHEN** the analyzer produces the final result
   **THEN** the produced `SUMMARY` and `REPOSITORY` values must match `expected_result.json`

### US-12: Many Merged Branches In One Window Must Preserve Per-Line Attribution

**As a** repository analyst,
**I want** branch-heavy history inside one requested window to preserve per-line effective attribution,
**so that** integrating many feature branches into the target branch does not distort the final result.

#### Acceptance Criteria For US-12

1. **GIVEN** a repository branch and a requested period `startTime~endTime`
   **WHEN** many branches are merged into the target branch before `endTime`
   **THEN** the system must still produce exactly one repository-level final result for the live changed source code set at `endTime`

2. **GIVEN** multiple merged branches inside one requested window
   **WHEN** surviving lines originate from different merged branches with different effective attribution histories
   **THEN** the system must preserve the effective attribution of each surviving line independently and must not flatten ownership to merge commits, branch labels, or merge order alone

3. **GIVEN** the fixture `testdata/us12_many_merged_branches_preserve_attribution`
   **WHEN** the analyzer produces the final result
   **THEN** the produced `SUMMARY` and `REPOSITORY` values must match `expected_result.json`

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

### Future Algorithm-B Story Intent

The next intended Algorithm-B user stories are:

1. `US-15`: single-branch period-added baseline without merges or renames
2. `US-16`: period-added accounting with deletions, resets, and mixed rewrites inside one window
3. `US-17`: Git rename and move handling for period contribution
4. `US-18`: merge-aware Git period contribution inside one requested window
5. `US-19`: SVN-supported subset for Algorithm-B period contribution

These should be introduced one by one under TDD with explicit `query.json` and `expected_result.json` artifacts before any Algorithm-B production-readiness claim is made.
