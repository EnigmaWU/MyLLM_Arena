# AggregateGenCodeDesc User Stories And Acceptance Criteria

## Purpose

This document defines the first user stories for AggregateGenCodeDesc and the acceptance criteria used to verify them.

All stories assume the analysis request includes `repo + branch + startTime + endTime`.
For the current primary metric, `startTime~endTime` is the requested reporting window, while the actual codebase ratio is calculated from the live snapshot at `endTime`.

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

1. **GIVEN** a repository branch and a requested period `startTime~endTime`
   **WHEN** the analyzer resolves the latest revision at or before `endTime`
   **THEN** it must use that snapshot as the only counting baseline

2. **GIVEN** a repository branch and a requested period `startTime~endTime`
   **WHEN** the analyzer returns the final result
   **THEN** the report must preserve both `startTime` and `endTime` as the query window metadata

3. **GIVEN** a live file in that snapshot
   **WHEN** the analyzer processes each live line
   **THEN** it must obtain the origin revision for the current line and look up the matching `genRatio`

4. **GIVEN** line-level `genRatio` values of `100`, `50`, and `0`
   **WHEN** the analyzer aggregates all live lines
   **THEN** it must compute a weighted ratio instead of a binary AI-or-human count

5. **GIVEN** the test data in `testdata/us1_basic_end_snapshot`
   **WHEN** the analyzer finishes the calculation
   **THEN** the expected result must be `2.5 / 4 = 62.5%`

### US-2: Human Rewrite Removes Prior AI Attribution

**As a** repository analyst,
**I want** a human rewrite of a previously AI-generated line to reset attribution to the newer human revision,
**so that** old AI ownership does not remain attached to overwritten code.

#### Acceptance Criteria For US-2

1. **GIVEN** a line was AI-generated in an earlier revision
   **WHEN** a later human revision changes the current text of that line
   **THEN** the final snapshot must attribute that line to the newer human revision

2. **GIVEN** the newer human revision has no AI line entry for that line
   **WHEN** the analyzer looks up the line attribution
   **THEN** the effective `genRatio` for that live line must be `0`

3. **GIVEN** the test data in `testdata/us2_human_overwrites_ai`
   **WHEN** the analyzer evaluates the final snapshot
   **THEN** the expected result must be `2 / 3 = 66.67%`

### US-3: AI Rewrite Replaces Prior Human Ownership

**As a** repository analyst,
**I want** a later AI rewrite of a human line to become the effective attribution source,
**so that** the live codebase reflects the latest AI contribution.

#### Acceptance Criteria For US-3

1. **GIVEN** a line was originally written by a human
   **WHEN** a later revision rewrites that line using AI assistance
   **THEN** the origin for the final live line must be the later AI-related revision

2. **GIVEN** the new revision assigns partial AI ownership such as `80`
   **WHEN** the analyzer aggregates the live lines
   **THEN** that partial weight must be included in the final ratio

3. **GIVEN** the test data in `testdata/us3_ai_overwrites_human`
   **WHEN** the analyzer evaluates the final snapshot
   **THEN** the expected result must be `1.8 / 3 = 60.0%`

### US-4: Deleted AI Lines Must Not Count

**As a** repository analyst,
**I want** deleted AI-generated lines to disappear from both numerator and denominator,
**so that** the result reflects only the current live snapshot.

#### Acceptance Criteria For US-4

1. **GIVEN** an earlier revision added AI-generated lines
   **WHEN** a later revision deletes some of those lines
   **THEN** deleted lines must not contribute to the final result

2. **GIVEN** only two AI-generated lines survive in the final snapshot
   **WHEN** the analyzer computes totals
   **THEN** the denominator must be the two surviving lines only

3. **GIVEN** the test data in `testdata/us4_deleted_ai_lines`
   **WHEN** the analyzer evaluates the final snapshot
   **THEN** the expected result must be `2 / 2 = 100%`

### US-5: Rename Must Preserve Attribution Lineage

**As a** repository analyst,
**I want** file rename or move operations to preserve line attribution when content does not change,
**so that** the final ratio is not distorted by path-only history changes.

#### Acceptance Criteria For US-5

1. **GIVEN** a file is renamed without changing its line content
   **WHEN** the analyzer resolves origin revisions with rename-aware blame
   **THEN** the live lines must still trace back to the original content revision

2. **GIVEN** the rename revision contributes no new AI-generated lines
   **WHEN** the analyzer reads the protocol for the final live lines
   **THEN** it must keep the original attribution from before the rename

3. **GIVEN** the test data in `testdata/us5_file_rename`
   **WHEN** the analyzer evaluates the final snapshot
   **THEN** the expected result must be `2 / 3 = 66.67%`

### US-6: Calculate AI-Added Ratio During The Requested Period

**As a** repository analyst,
**I want** to calculate how much AI-generated code was added during `startTime~endTime`,
**so that** I can distinguish period contribution from end-of-period inventory.

#### Acceptance Criteria For US-6

1. **GIVEN** a repository branch and a requested period `startTime~endTime`
   **WHEN** the analyzer evaluates the period metric
   **THEN** it must consider only revisions whose commit time falls inside the requested window

2. **GIVEN** revisions both before and inside the requested period
   **WHEN** the analyzer calculates period contribution
   **THEN** code introduced before `startTime` must not be counted in the numerator or denominator

3. **GIVEN** AI-generated and human-generated added lines within the requested period
   **WHEN** the analyzer aggregates the added lines for those revisions
   **THEN** it must compute `AI-weighted added lines / total added lines in period`

4. **GIVEN** the test data in `testdata/us6_period_added_ratio`
   **WHEN** the analyzer evaluates the period metric
   **THEN** the expected result must be `3 / 5 = 60.0%`
