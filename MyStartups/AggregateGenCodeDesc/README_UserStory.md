# AggregateGenCodeDesc User Stories And Acceptance Criteria

## Purpose

This document defines the first user stories for AggregateGenCodeDesc and the acceptance criteria used to verify them.

All stories assume the analysis request includes `repo + branch + startTime + endTime`.
For the current primary metric, `startTime~endTime` is the requested reporting window, while the actual codebase ratio is calculated from the live snapshot at `endTime`.
At this stage, the acceptance criteria are intentionally defined at the repository query level, not at the internal file-level or line-level implementation level.
The final aggregate result may be returned in a report and may also be represented directly by the protocol `SUMMARY` section.
The user query and the final record are different artifacts: `query.json` represents analysis input, while `genCodeDescProtocol.json` represents the final result record.

Each story is paired with scenario-based test data under `testdata/`.
Each scenario contains:

- one or more unified diff files that describe repository history
- one `genCodeDesc` file per revision that describes AI attribution for that revision

## Scenario Mapping

- `US-1` -> `testdata/us1_basic_end_snapshot`
- `US-2` -> `testdata/us2_human_overwrites_ai`
- `US-3` -> `testdata/us3_ai_overwrites_human`
- `US-4` -> `testdata/us4_deleted_ai_lines`
- `US-5` -> `testdata/us5_file_rename`
- `US-6` -> `testdata/us6_period_added_ratio`

## User Stories

### US-1: Calculate Weighted AI Ratio For A Requested Time Window

**As a** repository analyst,
**I want** to calculate the weighted AI code ratio for a branch in a requested period `startTime~endTime`,
**so that** I can know how much of the current live codebase is attributable to AI.

#### Acceptance Criteria For US-1

1. **GIVEN** a query `Repo:Branch:startTime:endTime`
   **WHEN** the user requests the AI code ratio
   **THEN** the system must return exactly one repository-level final result for that query, describing how much of the branch codebase is AI-generated as of `endTime`

2. **GIVEN** a successful result for `Repo:Branch:startTime:endTime`
   **WHEN** the result is returned or serialized as `genCodeDescProtocol.json`
   **THEN** it must be a final record in `genCodeDescProtocol.json` format, containing repository identity in `REPOSITORY` and aggregate final values in `SUMMARY`

3. **GIVEN** the fixture `testdata/us1_basic_end_snapshot`
   **WHEN** the analyzer produces the final result
   **THEN** the produced `SUMMARY` and `REPOSITORY` values must match `expected_result.json`

### US-2: Human Rewrite Removes Prior AI Attribution

**As a** repository analyst,
**I want** a human rewrite of a previously AI-generated line to reset attribution to the newer human revision,
**so that** old AI ownership does not remain attached to overwritten code.

#### Acceptance Criteria For US-2

1. **GIVEN** a repository branch and a requested period `startTime~endTime`
   **WHEN** code previously attributed to AI has been superseded by later human revisions before `endTime`
   **THEN** the system must produce one final record that reflects the newer repository state instead of preserving outdated AI ownership

2. **GIVEN** a successful result for `Repo:Branch:startTime:endTime`
   **WHEN** the result is returned or serialized as `genCodeDescProtocol.json`
   **THEN** it must be a final record in `genCodeDescProtocol.json` format, containing repository identity in `REPOSITORY` and aggregate final values in `SUMMARY`

3. **GIVEN** the fixture `testdata/us2_human_overwrites_ai`
   **WHEN** the analyzer produces the final result
   **THEN** the produced `SUMMARY` and `REPOSITORY` values must match `expected_result.json`

### US-3: AI Rewrite Replaces Prior Human Ownership

**As a** repository analyst,
**I want** a later AI rewrite of a human line to become the effective attribution source,
**so that** the live codebase reflects the latest AI contribution.

#### Acceptance Criteria For US-3

1. **GIVEN** a repository branch and a requested period `startTime~endTime`
   **WHEN** later revisions introduce new AI-attributed code before `endTime`
   **THEN** the system must produce one final record that reflects that newer AI contribution in the repository state at `endTime`

2. **GIVEN** a successful result for `Repo:Branch:startTime:endTime`
   **WHEN** the result is returned or serialized as `genCodeDescProtocol.json`
   **THEN** it must be a final record in `genCodeDescProtocol.json` format, containing repository identity in `REPOSITORY` and aggregate final values in `SUMMARY`

3. **GIVEN** the fixture `testdata/us3_ai_overwrites_human`
   **WHEN** the analyzer produces the final result
   **THEN** the produced `SUMMARY` and `REPOSITORY` values must match `expected_result.json`

### US-4: Deleted AI Lines Must Not Count

**As a** repository analyst,
**I want** deleted AI-generated lines to disappear from both numerator and denominator,
**so that** the result reflects only the current live snapshot.

#### Acceptance Criteria For US-4

1. **GIVEN** a repository branch and a requested period `startTime~endTime`
   **WHEN** some earlier AI-attributed code no longer exists in the branch state at `endTime`
   **THEN** the system must produce one final record that excludes that deleted code from the result

2. **GIVEN** a successful result for `Repo:Branch:startTime:endTime`
   **WHEN** the result is returned or serialized as `genCodeDescProtocol.json`
   **THEN** it must be a final record in `genCodeDescProtocol.json` format, containing repository identity in `REPOSITORY` and aggregate final values in `SUMMARY`

3. **GIVEN** the fixture `testdata/us4_deleted_ai_lines`
   **WHEN** the analyzer produces the final result
   **THEN** the produced `SUMMARY` and `REPOSITORY` values must match `expected_result.json`

### US-5: Rename Must Preserve Attribution Lineage

**As a** repository analyst,
**I want** file rename or move operations to preserve line attribution when content does not change,
**so that** the final ratio is not distorted by path-only history changes.

#### Acceptance Criteria For US-5

1. **GIVEN** a repository branch and a requested period `startTime~endTime`
   **WHEN** files are renamed or moved before `endTime` without changing their effective content contribution
   **THEN** the system must produce one final record that remains stable under path-only history changes

2. **GIVEN** a successful result for `Repo:Branch:startTime:endTime`
   **WHEN** the result is returned or serialized as `genCodeDescProtocol.json`
   **THEN** it must be a final record in `genCodeDescProtocol.json` format, containing repository identity in `REPOSITORY` and aggregate final values in `SUMMARY`

3. **GIVEN** the fixture `testdata/us5_file_rename`
   **WHEN** the analyzer produces the final result
   **THEN** the produced `SUMMARY` and `REPOSITORY` values must match `expected_result.json`

### US-6: Calculate AI-Added Ratio During The Requested Period

**As a** repository analyst,
**I want** to calculate how much AI-generated code was added during `startTime~endTime`,
**so that** I can distinguish period contribution from end-of-period inventory.

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
