# Shared-US Algorithm Convergence Roadmap

## Purpose

This document defines the concrete execution path from the current `US-6` baseline to the long-term target where every shared user story has defensible acceptance coverage across the full production matrix: `Algorithm A` and `Algorithm B`, each on both Git and SVN, unless an explicitly approved unsupported subset is documented.

It is intentionally not a pure idea list. Each phase below names the specific contract goal, the required implementation slice, the expected test artifacts, and the exit condition for moving to the next story.

For the concrete per-story `Algorithm B` execution spec, including target test files, fixture names, and code touch points, see `README_AlgorithmB_TDD.md`.

## Current Starting Point

- `US-6` is the first active shared user story with an executable `Algorithm B` path.
- `US-1` is now the first primary-metric shared story with explicit 2x2 matrix evidence: `Algorithm A` Git, `Algorithm A` SVN, `Algorithm B` Git, and `Algorithm B` SVN all have an approved `US-1` acceptance path, with the `Algorithm B` cells still intentionally narrow live-snapshot replay slices.
- The current `Algorithm B` Git live-snapshot path is no longer fixture-only: it can now replay a real local Git checkout when the operator provides either an absolute local `repoURL` or a logical Git `repoURL` plus `--workingDir`.
- `US-2`, `US-3`, and `US-4` now have accepted `Algorithm A` evidence plus narrow Git `Algorithm B` replay acceptance for the approved baseline shapes, with focused real local-Git proof now added for the rewrite/deletion cluster.
- `US-5` and `US-7` now have accepted `Algorithm A` evidence plus narrow Git `Algorithm B` replay acceptance for the approved baseline shapes, with focused real local-Git proof now added for the rename and mixed-history cluster.
- `US-8` now has accepted `Algorithm A` evidence plus narrow Git `Algorithm B` replay acceptance for the approved baseline shape, with focused real local-Git proof now added for the current merge-preservation slice.
- `US-12` now has accepted `Algorithm A` evidence plus narrow Git `Algorithm B` replay acceptance for the approved baseline fixture shape, while the branch-heavy local-Git replay path remains an explicit next-step limitation.
- `US-10` and `US-11` now have accepted `Algorithm A` evidence plus narrow Git `Algorithm B` replay acceptance for the approved baseline fixture shapes.
- `US-9` is a shared contract story whose first split is by VCS target, not by algorithm, and it now has narrow `Algorithm B` Git/SVN parity evidence on the approved `US-1` baseline shape.
- `US-13` and `US-14` are `Heavy` production gates, not ordinary shared functional stories.

## Non-Negotiable Rule

For a shared story to count as production-ready shared coverage, all of the following must exist:

1. One approved `Algorithm A` Git acceptance path.
2. One approved `Algorithm A` SVN acceptance path, or an explicitly approved unsupported subset.
3. One approved `Algorithm B` Git acceptance path.
4. One approved `Algorithm B` SVN acceptance path, or an explicitly approved unsupported subset.
5. Matching observable result semantics at the shared-story level across all claimed supported cells.
6. Clear unsupported-case boundaries for each algorithm and VCS combination where needed.
7. Automated tests or fixture validation that prevent silent contract drift.

## Convergence Strategy

The work should proceed in two layers:

1. Build the missing reusable `Algorithm B` live-snapshot engine for the primary metric family.
2. Use that engine to bring each shared story into full matrix coverage one story at a time.

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

- The repo has a reusable `Algorithm B` live-snapshot path suitable for `US-1` style stories, including real local Git replay for the currently supported narrow boundary.

## Phase 2: US-1 Dual Coverage

### Phase 2 Goal

Make `US-1` the first primary-metric shared story that demonstrates the full 2x2 production matrix.

### Phase 2 Required Work

1. Reuse the existing `US-1` golden result as the shared contract target.
2. Keep the existing `Algorithm A` Git and `Algorithm A` SVN evidence aligned to one shared `US-1` contract.
3. Add an `Algorithm B` Git acceptance path for the same `US-1` observable semantics.
4. Add an `Algorithm B` SVN acceptance path when the replay semantics are defensible for the approved `US-1` baseline shape.
5. Once the full 2x2 matrix exists, keep the supported baseline explicit and keep broader unsupported topology boundaries explicit rather than implying universal convergence.
6. Keep the current `Algorithm B` support claim narrow where the implementation is still narrow: approved baseline fixture shape, live-snapshot replay, and explicit unsupported topology boundaries.

### Phase 2 Required Tests

1. One `Algorithm B` Git fixture-driven acceptance test for `US-1`.
2. One explicit parity test that runs both algorithms against the approved Git `US-1` contract and compares output semantics.
3. One `Algorithm B` SVN acceptance test once a defensible SVN slice exists.
4. One matrix-style assertion that the claimed supported `US-1` cells all satisfy the same observable contract.
5. One unsupported-case test for every missing or intentionally rejected matrix cell.

### Phase 2 Exit Condition

- `US-1` has approved acceptance evidence for all four cells in the 2x2 matrix, with the supported `Algorithm B` cells explicitly scoped to the approved narrow baseline shape.

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

The repo now has one narrow algorithm-plus-VCS parity slice for `US-9` through the approved `US-1` baseline shape. The remaining work is to expand that parity claim only where broader Git/SVN `Algorithm B` semantics are actually defensible.

### Phase 7 Required Work

1. Keep the existing VCS-first structure.
2. Keep `Algorithm B` parity evidence explicit and scenario-scoped; add broader Git and SVN parity only when the replay semantics are actually defensible beyond the approved baseline.
3. Do not claim `Algorithm B` SVN parity unless the replay semantics are actually supportable under real SVN history behavior.
4. Use `US-9` as the explicit contract check that a shared story is not production-ready until the claimed Git/SVN cells behave the same way at the result-contract layer.

### Phase 7 Exit Condition

- `US-9` has explicit parity evidence for the currently approved supported cells, with any broader unsupported subsets still documented honestly.

## What Does Not Belong In This Convergence Path

- `US-13` and `US-14` are not prerequisites for shared-story dual coverage.
- New `Heavy` production gates for `Algorithm B` should be added only after the relevant `Fast` shared stories are already dual-covered.
- Future `US-15` to `US-19` remain useful `Algorithm B` design stories, but they do not replace the need to converge the existing shared stories.

## Practical Implementation Order

If the repo advances one concrete milestone at a time, the recommended order is:

1. Keep `US-6` stable.
2. Build `Algorithm B` live-snapshot foundation.
3. Make the `US-1` matrix explicit and fill `Algorithm B` Git first.
4. Add `Algorithm B` SVN for `US-1` if the semantics are defensible enough for production claims.
5. Extend the same matrix discipline to `US-2`, `US-3`, `US-4`.
6. Extend it to `US-5`, `US-7`.
7. Extend it to `US-8`, `US-12`.
8. Extend it to `US-10`, `US-11`.
9. Extend `US-9` from VCS parity to algorithm-plus-VCS parity where defensible.

## Done Criteria For The Long-Term Goal

The shared-story convergence goal is complete only when:

1. `US-1`, `US-2`, `US-3`, `US-4`, `US-5`, `US-6`, `US-7`, `US-8`, `US-10`, `US-11`, and `US-12` each have explicit matrix accounting across `Algorithm A`/`Algorithm B` and Git/SVN.
2. Every claimed supported matrix cell has accepted evidence and matching observable result semantics.
3. `US-9` has explicit, defensible parity coverage for the supported algorithm and VCS combinations.
4. Unsupported combinations remain documented rather than being silently implied.
