# AggregateGenCodeDesc User Stories And Acceptance Criteria

## Purpose

This document defines the first user stories for AggregateGenCodeDesc and the acceptance criteria used to verify them.

All stories assume the analysis request includes `repo + branch + startTime + endTime`.
For the current primary metric, `startTime~endTime` defines which live lines are in scope, and the result is calculated from the live snapshot at `endTime`.
The current baseline is `P0 / Scope A: pure source code` using `Model A (preferred): blame-based end-snapshot attribution`.
Unless explicitly stated otherwise, the current user stories apply to both Git and SVN targets. VCS-specific differences may affect repository identity, branch or path conventions, and revision identifiers, but should not change the metric semantics or the protocol-shaped result contract.
At this stage, the acceptance criteria are intentionally defined at the repository query level, not at the internal file-level or line-level implementation level.
The final aggregate result may be returned in a report and may also be represented directly by the protocol `SUMMARY` section.
The user query and the final record are different artifacts: `query.json` represents analysis input, while `genCodeDescProtocol.json` represents the final result record.
The `genCodeDesc` records used during analysis are revision-level external metadata, not files committed into the analyzed repository.
The intended lookup key for one metadata record is `repoURL + repoBranch + revisionId`.
For fixture verification, `expected_result.json` should remain a minimal protocol-shaped output artifact. It should keep result fields such as `protocolName`, `protocolVersion`, `SUMMARY`, and `REPOSITORY`, and should not duplicate query-only fields such as `metric`, `model`, `scope`, `startTime`, or `endTime`.

Each story is paired with scenario-based test data under `testdata/`.
Each scenario contains:

- one `genCodeDesc` file per revision that describes AI attribution for that revision

Those `testdata/` scenarios are design-oriented fixtures.
Those local `genCodeDesc` files simulate the external metadata store used in real deployments.
The earlier diff artifacts have been removed from `testdata` to keep the fixture contract small and focused.
For real repository verification of `Model A`, the preferred test layer is under `tests/`, where actual Git or SVN repositories are created and `*.diff` files are not required.

For production-oriented runs, the analyzer should discover relevant revisions from repository history first and then fetch matching `genCodeDesc` records from an external provider.

## Scenario Mapping

- `US-1` -> `testdata/us1_live_changed_source_ratio` (`Model A`)
- `US-2` -> `testdata/us2_human_overwrites_ai_live_changed` (`Model A`)
- `US-3` -> `testdata/us3_ai_overwrites_human_live_changed` (`Model A`)
- `US-4` -> `testdata/us4_deleted_lines_excluded` (`Model A`)
- `US-5` -> `testdata/us5_rename_preserves_lineage` (`Model A`)
- `US-6` -> `testdata/us6_period_added_ratio` (`Model B`)
- `US-7` -> `testdata/us7_mixed_multi_commit_window` (`Model A`)
- `US-8` -> `testdata/us8_merge_commit_preserves_attribution` (`Model A`)
- `US-9` -> `testdata/us9_svn_contract_parity` (`Model A`)

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

Note: this is not the current `P0 / Scope A` baseline metric. It is a separate history-oriented metric that may align better with `Model B` or another future implementation.

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

2. **GIVEN** a successful result for `Repo:Branch:startTime:endTime`
   **WHEN** the result is returned or serialized as `genCodeDescProtocol.json`
   **THEN** it must be a final record in `genCodeDescProtocol.json` format, containing repository identity in `REPOSITORY` and aggregate final values in `SUMMARY`

3. **GIVEN** the fixture `testdata/us7_mixed_multi_commit_window`
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

2. **GIVEN** a successful result for `Repo:Branch:startTime:endTime`
   **WHEN** the result is returned or serialized as `genCodeDescProtocol.json`
   **THEN** it must be a final record in `genCodeDescProtocol.json` format, containing repository identity in `REPOSITORY` and aggregate final values in `SUMMARY`

3. **GIVEN** the fixture `testdata/us8_merge_commit_preserves_attribution`
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
