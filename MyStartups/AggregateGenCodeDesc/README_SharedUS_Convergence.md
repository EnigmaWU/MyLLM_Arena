# Shared-US Algorithm Convergence Roadmap

## Purpose

This document defines the concrete execution path from the current `US-6` baseline to the long-term target where every shared user story has defensible acceptance coverage for both `Algorithm A` and `Algorithm B`.

It is intentionally not a pure idea list. Each phase below names the specific contract goal, the required implementation slice, the expected test artifacts, and the exit condition for moving to the next story.

## Current Starting Point

- `US-6` is the first active shared user story with an executable `Algorithm B` path.
- `Algorithm A` currently provides the accepted implementation evidence for the primary live-snapshot metric stories: `US-1`, `US-2`, `US-3`, `US-4`, `US-5`, `US-7`, `US-8`, `US-10`, `US-11`, and `US-12`.
- `US-9` is a shared contract story whose first split is by VCS target, not by algorithm.
- `US-13` and `US-14` are `Heavy` production gates, not ordinary shared functional stories.

## Non-Negotiable Rule

For a shared story to count as covered by both algorithms, all of the following must exist:

1. One approved `Algorithm A` acceptance path.
2. One approved `Algorithm B` acceptance path.
3. Matching observable result semantics at the shared-story level.
4. Clear unsupported-case boundaries for each algorithm where needed.
5. Automated tests or fixture validation that prevent silent contract drift.

## Convergence Strategy

The work should proceed in two layers:

1. Build the missing reusable `Algorithm B` live-snapshot engine for the primary metric family.
2. Use that engine to bring each shared story into dual-algorithm acceptance one by one.

This matters because `US-6` is a period-contribution metric, while most other shared stories are live-snapshot metrics. Without a reusable `Algorithm B` live-snapshot path, story-by-story convergence will turn into ad hoc special cases.

## Phase 0: Lock US-6 As The Algorithm-B Baseline

### Phase 0 Goal

Keep `US-6` as the first stable shared story and use it as the quality bar for all future `Algorithm B` additions.

### Phase 0 Required Work

1. Keep the current narrow Git offline baseline green.
2. Keep unsupported shapes explicit: multi-file first patch, path changes, merge-aware replay, and other already-rejected cases must stay rejected until their own stories exist.
3. Treat `US-6` as the template for what dual-algorithm acceptance evidence looks like, even though `Algorithm A` is not implemented for that metric yet.

### Phase 0 Exit Condition

- `US-6` remains clean, stable, and documented as the first executable shared-story `Algorithm B` track.

## Phase 1: Introduce Algorithm-B Live-Snapshot Foundation

### Phase 1 Goal

Create the reusable `Algorithm B` path that can target the same observable live-snapshot contract currently served by `Algorithm A`.

### Phase 1 Why This Comes Before US-1 Dual Coverage

The main shared stories after `US-6` are not period-contribution stories. They all depend on reconstructing the final live snapshot and resolving the latest effective attribution at `endTime`.

### Phase 1 Required Work

1. Define one explicit `Algorithm B` live-snapshot contract that matches `Algorithm A` observable outputs for the current primary metric.
2. Introduce one dedicated internal mode or implementation slice for replay-to-final-live-snapshot behavior rather than overloading the current period-added path.
3. Define line-state rules for surviving line attribution, deletion removal, rewrite replacement, and rename preservation.
4. Add negative-path tests for unsupported live-snapshot replay shapes before broad claims are made.

### Phase 1 Required Tests

1. One dedicated `Algorithm B` live-snapshot contract test file.
2. One end-to-end CLI test proving the new path can produce protocol-shaped final output.
3. One parity-style assertion proving the same approved fixture can be satisfied by both algorithms once a story is marked dual-covered.

### Phase 1 Exit Condition

- The repo has a reusable `Algorithm B` live-snapshot path suitable for `US-1` style stories.

## Phase 2: US-1 Dual Coverage

### Phase 2 Goal

Make `US-1` the first primary-metric shared story that is covered by both `Algorithm A` and `Algorithm B`.

### Phase 2 Required Work

1. Reuse the existing `US-1` golden result as the shared contract target.
2. Add an `Algorithm B` acceptance path for the same `US-1` observable semantics.
3. Keep the current supplementary SVN parity evidence as `Algorithm A` evidence only unless and until `Algorithm B` can credibly target the same VCS shape.

### Phase 2 Required Tests

1. One `Algorithm B` fixture-driven acceptance test for `US-1`.
2. One explicit parity test that runs both algorithms against the approved `US-1` contract and compares output semantics.
3. One unsupported-case test if the first `Algorithm B` slice does not yet support all history topologies that `Algorithm A` handles.

### Phase 2 Exit Condition

- `US-1` is the first live-snapshot story with approved evidence on both algorithms.

## Phase 3: Rewrite And Deletion Cluster

### Phase 3 Stories

- `US-2`
- `US-3`
- `US-4`

### Phase 3 Why These Come Next

These three stories are all direct consequences of correct final live-line state handling.

### Phase 3 Required Work

1. `US-2`: prove that a later human rewrite removes stale AI ownership under `Algorithm B`.
2. `US-3`: prove that a later AI rewrite becomes the effective owner under `Algorithm B`.
3. `US-4`: prove that deleted lines disappear entirely from final aggregation under `Algorithm B`.

### Phase 3 Required Tests

1. One `Algorithm B` acceptance test per story using the existing golden result.
2. One focused low-level replay test per behavior if the failure mode is subtle.
3. One combined regression test proving mixed rewrite and deletion transitions do not regress earlier stories.

### Phase 3 Exit Condition

- `US-2`, `US-3`, and `US-4` each have clear dual-algorithm evidence.

## Phase 4: Rename And Mixed History Cluster

### Phase 4 Stories

- `US-5`
- `US-7`

### Phase 4 Why These Come Next

Once rewrite and deletion semantics are stable, the next critical expansion is path continuity and mixed in-window history.

### Phase 4 Required Work

1. `US-5`: add defensible `Algorithm B` rename handling for path-only changes.
2. `US-7`: prove that mixed history across multiple commits still resolves to the latest effective live attribution under `Algorithm B`.

### Phase 4 Required Tests

1. One `Algorithm B` acceptance test per story.
2. Rename-specific low-level replay tests.
3. Mixed-history low-level replay tests that combine rewrite, survival, and deletion behavior.

### Phase 4 Exit Condition

- `US-5` and `US-7` have approved dual-algorithm evidence.

## Phase 5: Merge And Topology Cluster

### Phase 5 Stories

- `US-8`
- `US-12`

### Phase 5 Why These Are Later

Merge semantics are where a replay-based lineage engine becomes genuinely hard. They should not be attempted before single-branch and mixed-history correctness is stable.

### Phase 5 Required Work

1. Choose and document the `Algorithm B` merge replay policy explicitly.
2. `US-8`: prove one merge does not flatten attribution.
3. `US-12`: prove branch-heavy history does not flatten per-line attribution.

### Phase 5 Required Tests

1. One `Algorithm B` acceptance test per story.
2. One low-level merge-policy test set for first-parent vs merged-parent behavior.
3. One explicit unsupported-case boundary if certain merge shapes remain out of scope at first.

### Phase 5 Exit Condition

- `US-8` and `US-12` have approved dual-algorithm evidence with merge policy made explicit.

## Phase 6: Scale And Deep-History Stability

### Phase 6 Stories

- `US-10`
- `US-11`

### Phase 6 Why These Follow Functional Correctness

Scale and long history should validate a mature engine, not define one.

### Phase 6 Required Work

1. `US-10`: prove that broad final snapshots preserve semantics under `Algorithm B`.
2. `US-11`: prove that long rewrite chains preserve latest effective attribution under `Algorithm B`.
3. Add bounded-reuse or caching assertions only after correctness is already stable.

### Phase 6 Required Tests

1. One `Algorithm B` acceptance test per story.
2. One targeted scalability or reuse-oriented test where the story already justifies it.

### Phase 6 Exit Condition

- `US-10` and `US-11` have approved dual-algorithm evidence.

## Phase 7: US-9 Algorithm Convergence

### Phase 7 Goal

Only after the primary shared stories are dual-covered should `US-9` be extended from VCS parity to algorithm-plus-VCS parity.

### Phase 7 Required Work

1. Keep the existing VCS-first structure.
2. Add `Algorithm B` evidence separately for Git and only then for any defensible SVN subset.
3. Do not claim `Algorithm B` SVN parity unless the replay semantics are actually supportable under real SVN history behavior.

### Phase 7 Exit Condition

- `US-9` has a defensible matrix of support rather than a hand-waved parity claim.

## What Does Not Belong In This Convergence Path

- `US-13` and `US-14` are not prerequisites for shared-story dual coverage.
- New `Heavy` production gates for `Algorithm B` should be added only after the relevant `Fast` shared stories are already dual-covered.
- Future `US-15` to `US-19` remain useful `Algorithm B` design stories, but they do not replace the need to converge the existing shared stories.

## Practical Implementation Order

If the repo advances one concrete milestone at a time, the recommended order is:

1. Keep `US-6` stable.
2. Build `Algorithm B` live-snapshot foundation.
3. Dual-cover `US-1`.
4. Dual-cover `US-2`, `US-3`, `US-4`.
5. Dual-cover `US-5`, `US-7`.
6. Dual-cover `US-8`, `US-12`.
7. Dual-cover `US-10`, `US-11`.
8. Extend `US-9` from VCS parity to algorithm-plus-VCS parity where defensible.

## Done Criteria For The Long-Term Goal

The shared-story convergence goal is complete only when:

1. `US-1`, `US-2`, `US-3`, `US-4`, `US-5`, `US-6`, `US-7`, `US-8`, `US-10`, `US-11`, and `US-12` each have accepted evidence for both `Algorithm A` and `Algorithm B`.
2. `US-9` has explicit, defensible parity coverage for the supported algorithm and VCS combinations.
3. Unsupported combinations remain documented rather than being silently implied.
