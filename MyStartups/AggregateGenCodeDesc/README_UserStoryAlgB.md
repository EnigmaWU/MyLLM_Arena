# AggregateGenCodeDesc — Algorithm B User Stories

## Purpose

This document defines the user stories for **Algorithm B** (`AlgB`).

Algorithm B is an offline, replay-based attribution algorithm.
It reconstructs line-level state by replaying commit diff patches in chronological
order, then cross-references each surviving line's origin revision against
per-revision `genCodeDescProtoV26.03` metadata to compute the weighted AI ratio.

Algorithm B operates in two modes:

- **Local Git replay**: reads diffs directly from a local Git checkout.
- **Offline fixture replay**: reads pre-exported patch files from
  `--commitDiffSetDir`, requiring no active repository access at runtime.

Algorithm B is the only algorithm that supports the **period-added metric** —
measuring AI contribution added during the requested window, not the
end-of-window inventory. This is distinct from the live-snapshot metric that
Algorithm A and Algorithm C provide.

Algorithm B supports all four measurement scopes (A, B, C, D) and both Git and
SVN source patches (SVN support is currently through offline fixtures in select
scenarios).

## Protocol Precondition

All AlgB stories require `protocolVersion: "26.03"` per-revision metadata files.
Algorithm B reads `codeLines` (or `docLines`) entries from per-revision metadata
to determine `genRatio` and `genMethod` for each in-scope origin revision
discovered during replay.

A `genCodeDescProtoV26.04` input is not expected by Algorithm B.

Offline fixture replay additionally requires `--commitDiffSetDir` containing
unified-diff patch files paired with matching metadata in `--genCodeDescSetDir`.

## Relationship To Algorithm A and Algorithm C

| Property | Algorithm A | Algorithm B | Algorithm C |
| --- | --- | --- | --- |
| Repository access | live `git/svn blame` | offline diff replay | none |
| Input | repo + per-revision genCodeDesc v26.03 | commitDiffSet + per-revision genCodeDesc v26.03 | per-revision genCodeDesc **v26.04** only |
| Blame source | VCS subprocess | diff patch reconstruction | embedded `blame` object in DETAIL |
| DETAIL completeness required | no (AI lines only) | no (AI lines only) | exhaustive surviving-line DETAIL required |
| VCS support | git and svn | git and svn | git-origin and svn-origin blame |
| Scope support | A, B, C, D | A, B, C, D | A (current slice) |
| Period-added metric | not yet supported | supported | not yet supported |
| Metric semantics | identical | identical | identical |

## Story Rules

1. Every story follows the `WHO` / `WHEN` / `WHAT` / `WHY` / `Story` / `Support` / `Status` / `Anchors` format.
2. Acceptance criteria use plain `GIVEN / WHEN / THEN` blocks with story-local IDs.
3. Every story that claims parity with Algorithm A or Algorithm C must name the matching USNG story ID.
4. `tier=Heavy` stories must name a concrete scale floor in at least one acceptance criterion.

## Story ID Convention

```text
USNG-ALGB-HISTORY-<C>-SCOPE-<D>-<NN>: Title
```

- `HISTORY-<C>`: `SIMPLE` | `COMPLICATED` | `COMPLEX`
  - `SIMPLE`: linear baselines, direct parity contracts, scope-only contracts
  - `COMPLICATED`: overwrites, deletions, renames, mixed commit chains, merge-aware flows
  - `COMPLEX`: large file sets, deep history, many-branch fan-in, production scale
- `SCOPE-<D>`: `A` | `B` | `C` | `D` | `ALL`
- `REPO` and `GENCODEDESC` dimensions are carried by the `Support` and `Status` fields, not by the story ID.

---

## Universal Story Invariants

The following invariants apply to every AlgB story unless overridden explicitly.

- `UI-PROTOCOL`: the result must be a valid protocol-shaped output with `protocolName`,
  `protocolVersion`, `SUMMARY`, and `REPOSITORY` fields.
- `UI-GOLDEN`: for scenarios whose fixtures provide approved golden outputs, the result
  must match the approved golden output for the scenario.
- `UI-REPLAY-BASED`: Algorithm B determines each surviving line's effective origin
  revision by replaying commit diff patches in chronological order and tracking
  line-level add/delete/modify transitions. It does not invoke any VCS blame subprocess.
- `UI-DUAL-MODE`: Algorithm B supports two replay modes. Local Git replay reads diffs
  directly from a local Git checkout. Offline fixture replay reads pre-exported patches
  from `--commitDiffSetDir`. Both modes must produce the same result for the same
  logical scenario.
- `UI-NARROW-BOUNDARY`: Any Algorithm B evidence attached to a `HISTORY-COMPLICATED`
  or `HISTORY-COMPLEX` story covers the approved scenario of that story only. It is not
  blanket support across all complicated or complex history shapes.
- `UI-GENCODEDESC-V2603`: Algorithm B reads per-revision `genCodeDescProtoV26.03`
  metadata from `--genCodeDescSetDir`. Each replayed revision must have a matching
  `<revisionId>_genCodeDesc.json` file.
- `UI-PARITY`: the target contract is parity with Algorithm A. Algorithm B must produce
  the same `SUMMARY` as Algorithm A for the same repository content under the
  live-snapshot metric.
- `UI-COMMITDIFFSET-CONTRACT`: offline fixture replay requires each replayed revision
  to have both a `<timeSeq>_<revisionId>_commitDiff.patch` and a matching
  `<revisionId>_genCodeDesc.json`.

---

## HISTORY-SIMPLE Stories — Live-Snapshot Parity

### USNG-ALGB-HISTORY-SIMPLE-SCOPE-A-01: Calculate Weighted AI Ratio For Live Changed Source Code Via Replay

- `WHO`: repository analyst
- `WHEN`: querying a time window `startTime~endTime` and replaying commit diffs instead of invoking live blame
- `WHAT`: calculate the weighted AI ratio for source-code lines by reconstructing the live snapshot through diff replay
- `WHY`: reproduce the same live-changed metric as Algorithm A without requiring live blame subprocess
- `Story`: As a repository analyst, I want to calculate the weighted AI ratio for live source-code lines using diff replay instead of live blame, so that I can reproduce the Algorithm A result through an offline replay path.
- `Support`: `scope=A baseline` | `alg=B` | `vcs=git (local replay and offline fixture) and svn (offline fixture)` | `tier=Fast`
- `Status`: Covered for Git local replay and Git/SVN offline fixture replay. Parity target: `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-01`.
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-01-GIT`, `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-01-SVN`

**AC-01** — *Core replay-based measurement contract*

- GIVEN commit diff patches and per-revision genCodeDesc metadata covering the `startTime~endTime` window
- WHEN Algorithm B replays patches in chronological order and reconstructs the surviving-line state at `endRevision`
- THEN it returns exactly one repository-level result describing the AI ratio among live source-code lines changed in the window

**AC-02** — *Missing genCodeDesc record treated as human/unattributed*

- GIVEN one or more replayed revisions have no matching `genCodeDesc` record
- WHEN Algorithm B aggregates the final result
- THEN those lines are counted as human/unattributed

**AC-GIT-01** — *Git local replay*

- GIVEN a local Git checkout and the approved baseline scenario
- WHEN Algorithm B replays diffs from the local Git repository
- THEN the result matches the approved NG golden output

**AC-GIT-02** — *Git offline fixture replay*

- GIVEN pre-exported Git commit-diff patches and the approved baseline scenario
- WHEN Algorithm B replays from `--commitDiffSetDir`
- THEN the result matches the approved NG golden output

**AC-SVN-01** — *SVN offline fixture replay*

- GIVEN pre-exported SVN commit-diff patches and the approved baseline scenario
- WHEN Algorithm B replays from `--commitDiffSetDir`
- THEN the result matches the approved NG golden output

---

### USNG-ALGB-HISTORY-SIMPLE-SCOPE-A-08: Git And SVN Must Follow The Same Result Contract Via Replay

- `WHO`: repository analyst
- `WHEN`: verifying that Algorithm B produces the same result semantics regardless of whether the replayed patches originate from a Git or SVN repository
- `WHAT`: confirm that VCS origin does not change replay-based result semantics
- `WHY`: VCS type must not change metric semantics for the replay algorithm
- `Story`: As a repository analyst, I want Algorithm B to produce the same result semantics for Git-origin and SVN-origin replay patches, so that VCS type does not affect the replay-based attribution contract.
- `Support`: `scope=A baseline` | `alg=B` | `vcs=git and svn` | `tier=Fast`
- `Status`: Covered through narrow Git/SVN live-snapshot replay for the approved story-01 and story-08 scenarios. Parity target: `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-08`.
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-08-SVN-PARITY`

**AC-01** — *Same semantics across VCS-origin patches*

- GIVEN equivalent replay patches originating from Git or SVN for the same logical scenario
- WHEN Algorithm B replays each
- THEN both produce one final record with the same metric semantics, differing only in VCS-specific repository identity

---

## HISTORY-COMPLICATED Stories — Live-Snapshot Parity

### USNG-ALGB-HISTORY-COMPLICATED-SCOPE-A-02: Human Rewrite Removes Prior AI Attribution Via Replay

- `WHO`: repository analyst
- `WHEN`: a human revision overwrites code previously attributed to AI before `endTime`
- `WHAT`: the replayed line state reflects the later human revision; attribution resets to Manual
- `WHY`: prevent old AI ownership from staying attached to overwritten code
- `Story`: As a repository analyst, I want a human rewrite of a previously AI-generated line to reset attribution to Manual through diff replay, so that old AI ownership does not persist in the Algorithm B result.
- `Support`: `scope=A baseline` | `alg=B` | `vcs=narrow Git slice` | `tier=Fast`
- `Status`: Covered via narrow Git live-snapshot replay. Parity target: `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-02`.
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-02`

**AC-01** — *Human rewrite clears prior AI attribution via replay*

- GIVEN a diff patch overwrites an AI-attributed line with human content
- WHEN Algorithm B replays the patch sequence to reconstruct the surviving-line state
- THEN the line is counted as `totalCodeLines` only, not in any AI counter

**AC-GIT-01** — *Git replay parity*

- GIVEN the approved narrow Git replay scenario
- WHEN Algorithm B is executed
- THEN `SUMMARY` matches the Algorithm A golden result

---

### USNG-ALGB-HISTORY-COMPLICATED-SCOPE-A-03: AI Rewrite Replaces Prior Human Ownership Via Replay

- `WHO`: repository analyst
- `WHEN`: a later AI revision overwrites a line previously human-authored
- `WHAT`: the replayed line state reflects the AI revision; AI attribution applies
- `WHY`: ensure the replay result at `endTime` reflects the latest AI contribution
- `Story`: As a repository analyst, I want a later AI rewrite of a human line to become the effective attribution source through diff replay, so that Algorithm B reflects the latest AI contribution.
- `Support`: `scope=A baseline` | `alg=B` | `vcs=narrow Git slice` | `tier=Fast`
- `Status`: Covered via narrow Git live-snapshot replay. Parity target: `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-03`.
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-03`

**AC-01** — *Later AI revision becomes effective attribution via replay*

- GIVEN a diff patch overwrites a human-attributed line with AI content
- WHEN Algorithm B replays the patch sequence
- THEN the line is counted in both `totalCodeLines` and the appropriate AI counter

**AC-GIT-01** — *Git replay parity*

- GIVEN the approved narrow Git replay scenario
- WHEN Algorithm B is executed
- THEN `SUMMARY` matches the Algorithm A golden result

---

### USNG-ALGB-HISTORY-COMPLICATED-SCOPE-A-04: Deleted Lines Must Not Count Via Replay

- `WHO`: repository analyst
- `WHEN`: lines existed earlier in the window but are removed by a later diff patch before `endRevision`
- `WHAT`: those lines do not appear in the result
- `WHY`: deleted lines are removed during replay and should not count
- `Story`: As a repository analyst, I want deleted lines to be correctly removed during Algorithm B diff replay, so that the result reflects only the surviving live snapshot.
- `Support`: `scope=A baseline` | `alg=B` | `vcs=narrow Git slice` | `tier=Fast`
- `Status`: Covered via narrow Git live-snapshot replay. Parity target: `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-04`.
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-04`

**AC-01** — *Deleted lines removed during replay*

- GIVEN a diff patch deletes lines that existed in an earlier replayed state
- WHEN Algorithm B replays the patch sequence
- THEN the deleted lines are absent from the final reconstructed state and excluded from all counters

**AC-GIT-01** — *Git replay parity*

- GIVEN the approved narrow Git replay scenario
- WHEN Algorithm B is executed
- THEN `SUMMARY` matches the Algorithm A golden result

---

### USNG-ALGB-HISTORY-COMPLICATED-SCOPE-A-05: Rename Must Preserve Attribution Lineage Via Replay

- `WHO`: repository analyst
- `WHEN`: a file was renamed or moved between replayed patches
- `WHAT`: preserve line attribution across the rename by tracking file identity through the diff stream
- `WHY`: prevent rename-only changes from distorting the replay-based result
- `Story`: As a repository analyst, I want renamed or moved files to be tracked correctly through Algorithm B diff replay, so that path-only changes do not distort attribution.
- `Support`: `scope=A baseline` | `alg=B` | `vcs=narrow Git slice` | `tier=Fast`
- `Status`: Covered via narrow Git live-snapshot replay. Parity target: `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-05`.
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-05`

**AC-01** — *Rename tracked through diff stream*

- GIVEN a diff patch contains a rename header (old path → new path)
- WHEN Algorithm B replays the patch sequence
- THEN surviving lines retain their pre-rename attribution

**AC-GIT-01** — *Git replay parity*

- GIVEN the approved narrow Git replay scenario
- WHEN Algorithm B is executed
- THEN `SUMMARY` matches the Algorithm A golden result

---

### USNG-ALGB-HISTORY-COMPLICATED-SCOPE-A-06: Resolve Mixed Multi-Commit History In One Window Via Replay

- `WHO`: repository analyst
- `WHEN`: one requested window contains many replayed patches with mixed human-only, AI-only, rewrite, and deletion paths
- `WHAT`: resolve each surviving line by its latest effective attribution after sequential replay
- `WHY`: keep one final result correct even when the replayed history is mixed
- `Story`: As a repository analyst, I want one requested window to correctly resolve mixed line histories across many replayed patches, so that the final result remains correct under complex replay scenarios.
- `Support`: `scope=A baseline` | `alg=B` | `vcs=narrow Git slice` | `tier=Fast`
- `Status`: Covered via narrow Git live-snapshot replay. Parity target: `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-06`.
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-06`

**AC-01** — *Mixed replay produces one correct final record*

- GIVEN multiple patches in the window contain mixed ownership transitions
- WHEN Algorithm B replays them sequentially
- THEN it produces exactly one final record using the latest effective attribution of each surviving line

**AC-GIT-01** — *Git replay parity*

- GIVEN the approved narrow Git replay scenario
- WHEN Algorithm B is executed
- THEN `SUMMARY` matches the Algorithm A golden result

---

### USNG-ALGB-HISTORY-COMPLICATED-SCOPE-A-07: Merge Commit Must Preserve Effective Attribution Via Replay

- `WHO`: repository analyst
- `WHEN`: merged branches bring human and AI contributions through the replayed patch stream
- `WHAT`: each surviving line retains the attribution from its effective origin revision through replay
- `WHY`: merge commits must not reset or flatten per-line provenance in the replay result
- `Story`: As a repository analyst, I want merged branches to preserve per-line effective attribution through Algorithm B diff replay, so that merge operations do not flatten ownership.
- `Support`: `scope=A baseline` | `alg=B` | `vcs=narrow Git slice` | `tier=Fast`
- `Status`: Covered via narrow Git live-snapshot replay. Parity target: `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-07`.
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-07`

**AC-01** — *Merge does not reset ownership during replay*

- GIVEN a merge patch introduces lines from different branch histories
- WHEN Algorithm B replays the patch
- THEN it attributes each surviving line based on the patch that last modified it, not the merge commit identity

**AC-02** — *Per-line independence across merged branches*

- GIVEN surviving lines originate from different merged branches
- WHEN Algorithm B fully replays the window
- THEN it preserves each surviving line independently

**AC-GIT-01** — *Git replay parity*

- GIVEN the approved narrow Git replay scenario
- WHEN Algorithm B is executed
- THEN `SUMMARY` matches the Algorithm A golden result

---

## HISTORY-COMPLEX Stories — Live-Snapshot Parity

### USNG-ALGB-HISTORY-COMPLEX-SCOPE-A-09: Large File Set Must Preserve Result Semantics Via Replay

- `WHO`: repository analyst
- `WHEN`: the replayed scenario covers a large repository with many files and many surviving lines
- `WHAT`: Algorithm B correctly replays all patches at scale and produces the correct SUMMARY
- `WHY`: production repositories have large file sets; correctness must hold at scale
- `Story`: As a repository analyst, I want Algorithm B to remain correct across a large file set during replay, so that result semantics are preserved at production scale.
- `Support`: `scope=A baseline` | `alg=B` | `vcs=narrow Git local replay` | `tier=Fast`
- `Status`: Covered via narrow Git real local-checkout replay. Parity target: `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-09`.
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-09`

**AC-01** — *Large file set produces one correct result*

- GIVEN a replay scenario covers hundreds of files and thousands of surviving lines
- WHEN Algorithm B replays all patches
- THEN it produces exactly one repository-level SUMMARY and the counts match the golden result

**AC-GIT-01** — *Git replay parity*

- GIVEN the approved scenario through local Git replay
- WHEN Algorithm B is executed
- THEN `SUMMARY` matches the Algorithm A golden result

---

### USNG-ALGB-HISTORY-COMPLEX-SCOPE-A-10: Deep History Must Preserve Latest Effective Attribution Via Replay

- `WHO`: repository analyst
- `WHEN`: surviving lines pass through many intermediate rewrites across a long replay sequence
- `WHAT`: Algorithm B preserves each line's latest effective attribution after full replay
- `WHY`: deep history must not distort per-line attribution; sequential replay must converge to the correct final state
- `Story`: As a repository analyst, I want deep commit history and repeated rewrites to be correctly processed by Algorithm B sequential replay, so that lines from early and late revisions are attributed correctly after full replay.
- `Support`: `scope=A baseline` | `alg=B` | `vcs=narrow Git local replay` | `tier=Fast`
- `Status`: Covered via narrow Git real local-checkout replay. Parity target: `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-10`.
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-10`

**AC-01** — *Latest effective attribution wins after full replay*

- GIVEN surviving lines pass through many intermediate rewrites in the replay sequence
- WHEN Algorithm B completes full sequential replay
- THEN each surviving line's attribution reflects the latest effective modification, not earlier superseded states

**AC-GIT-01** — *Git replay parity*

- GIVEN the approved scenario through local Git replay
- WHEN Algorithm B is executed
- THEN `SUMMARY` matches the Algorithm A golden result

---

### USNG-ALGB-HISTORY-COMPLEX-SCOPE-A-11: Many Merged Branches Must Preserve Per-Line Attribution Via Replay

- `WHO`: repository analyst
- `WHEN`: many branches are merged into the target branch through the replayed patch stream
- `WHAT`: Algorithm B preserves per-line attribution regardless of how many merged branches contributed
- `WHY`: branch-heavy repositories must not distort attribution via replay
- `Story`: As a repository analyst, I want branch-heavy history to be transparent to Algorithm B diff replay, so that integrating many feature branches does not distort the final result.
- `Support`: `scope=A baseline` | `alg=B` | `vcs=narrow Git local replay` | `tier=Fast`
- `Status`: Covered via narrow Git real local-checkout replay. Parity target: `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-11`.
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-11`

**AC-01** — *Per-line independence across many merged branches*

- GIVEN surviving lines originate from many different merged branches in the replay stream
- WHEN Algorithm B completes full sequential replay
- THEN it attributes each line independently

**AC-GIT-01** — *Git replay parity*

- GIVEN the approved scenario through local Git replay
- WHEN Algorithm B is executed
- THEN `SUMMARY` matches the Algorithm A golden result

---

## Period-Added Contract Stories

These stories define the **period-added metric**, which is unique to Algorithm B.
The period-added metric measures AI contribution **added during** the requested
window, not the end-of-window inventory. This is a distinct metric from the
live-snapshot metric provided by Algorithms A and C.

### USNG-ALGB-HISTORY-SIMPLE-SCOPE-A-21: Calculate AI-Added Ratio During The Requested Period

- `WHO`: repository analyst
- `WHEN`: wanting to measure AI contribution added during the window itself, not the end-of-window inventory
- `WHAT`: calculate how much AI-generated code was added during `startTime~endTime`
- `WHY`: distinguish period contribution from end-of-period inventory
- `Story`: As a repository analyst, I want to calculate how much AI-generated code was added during `startTime~endTime`, so that I can distinguish period contribution from end-of-period inventory.
- `Support`: `scope=shared story anchor` | `alg=B` | `vcs=shared` | `tier=Fast`
- `Status`: Current executable path is narrow Algorithm B Git baseline through offline replay and supported local-Git replay. Parity target: `USNG-REPO-GIT-LOCAL-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-21`.
- `Anchors`: `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-21`

**AC-01** — *Core period-added contract*

- GIVEN `repo`, `branch`, `startTime`, and `endTime` define a requested period
- WHEN Algorithm B replays commit diffs and computes the period contribution metric
- THEN it returns exactly one repository-level final result describing the aggregate AI-added code result during that period

**AC-ALG-B-01** — *Algorithm B current path*

- GIVEN the approved baseline scenario
- WHEN the narrow offline Git Algorithm B baseline is executed
- THEN the result matches the approved NG golden output

---

### USNG-ALGB-HISTORY-SIMPLE-SCOPE-A-22: Single-Branch Period-Added Baseline Without Merges Or Renames

- `WHO`: repository analyst
- `WHEN`: wanting the cleanest possible single-branch baseline for the period-added metric
- `WHAT`: prove the core Algorithm B period-added contract on a simple linear Git history
- `WHY`: establish a stable baseline before adding rewrites, renames, or merges
- `Story`: As a repository analyst, I want a single-branch period-added baseline without merges or renames, so that the core Algorithm B period-contribution contract is proven before topology complexity is introduced.
- `Support`: `scope=A and B note` | `alg=B` | `vcs=git local replay` | `tier=Fast`
- `Status`: First-class Algorithm B single-branch baseline story. Parity target: `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-A-22`.
- `Anchors`: `TestsNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-A-22`

**AC-ALG-B-01** — *Core period-added baseline*

- GIVEN a single-branch Git repository has one pre-window human commit and two in-window commits
- WHEN Algorithm B computes period-added totals
- THEN it counts only lines whose origin revision falls inside the window, and `fullGeneratedCodeLines` counts only the AI-attributed in-window lines

**AC-ALG-B-02** — *Scope B note*

- GIVEN the same single-branch repository is analyzed under Scope B
- WHEN Algorithm B computes the period-added result
- THEN it preserves period-added semantics while reflecting the broader source-line scope

---

### USNG-ALGB-HISTORY-COMPLICATED-SCOPE-A-23: Period-Added Accounting With Deletions, Resets, And Mixed Rewrites

- `WHO`: repository analyst
- `WHEN`: the requested period contains added lines, deleted lines, and mixed AI-human rewrites inside one window
- `WHAT`: keep period-added accounting correct across deletions, resets, and mixed rewrites
- `WHY`: prevent superseded or deleted in-window AI lines from distorting the period result
- `Story`: As a repository analyst, I want period-added accounting to handle deletions, resets, and mixed rewrites inside one window, so that superseded or deleted in-window AI lines do not distort the period result.
- `Support`: `scope=primary baseline` | `alg=B` | `vcs=git local replay` | `tier=Fast`
- `Status`: First-class Algorithm B rewrite and deletion story. Parity target: `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-23`.
- `Anchors`: `TestsNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-23`

**AC-ALG-B-01** — *Deleted in-window AI lines excluded*

- GIVEN an AI line is added during the window and later deleted or replaced by a later in-window commit
- WHEN Algorithm B computes the period-added result
- THEN that deleted AI line does not appear in the final period-added total

**AC-ALG-B-02** — *Rewritten lines use rewriter attribution*

- GIVEN a pre-window human line is rewritten during the window
- WHEN Algorithm B computes the period-added result
- THEN the rewritten line is counted as in-window with the rewriter's attribution

**AC-ALG-B-03** — *Pre-window lines that survive untouched excluded from period-added totals*

- GIVEN a file contains lines whose origin revision predates `startTime` and those lines survive unchanged into `endTime`
- WHEN Algorithm B computes the period-added result
- THEN those pre-window surviving lines are excluded from the period-added total

---

### USNG-ALGB-HISTORY-COMPLICATED-SCOPE-A-24: Git Rename And Move Handling For Period Contribution

- `WHO`: repository analyst
- `WHEN`: a file is renamed during the period and the analyst still needs true period-added accounting
- `WHAT`: preserve rename and move semantics in the period-added metric
- `WHY`: stop path-only changes from making old lines appear as new in-window additions
- `Story`: As a repository analyst, I want period-added accounting to preserve rename and move semantics, so that path-only history changes do not make older lines appear as new in-window additions.
- `Support`: `scope=primary baseline` | `alg=B` | `vcs=git local replay` | `tier=Fast`
- `Status`: First-class Algorithm B rename story. Parity target: `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-24`.
- `Anchors`: `TestsNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-24`

**AC-ALG-B-01** — *Rename preserves period-added accuracy*

- GIVEN a file is renamed during the window and a new AI line is added
- WHEN Algorithm B computes the period-added result
- THEN only the new line counts in the period-added total while pre-window lines that survived the rename remain excluded

---

### USNG-ALGB-HISTORY-COMPLICATED-SCOPE-A-25: Merge-Aware Git Period Contribution Inside One Window

- `WHO`: repository analyst
- `WHEN`: the requested period includes branch work and non-fast-forward merge activity
- `WHAT`: keep period-added accounting correct across merge-aware Git history
- `WHY`: ensure contributions from both main and merged feature branches count correctly
- `Story`: As a repository analyst, I want period-added accounting to survive branch-and-merge history inside one window, so that contributions from both main and merged feature branches are counted correctly.
- `Support`: `scope=primary baseline` | `alg=B` | `vcs=git local replay` | `tier=Fast`
- `Status`: First-class Algorithm B merge-aware story. Parity target: `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-25`.
- `Anchors`: `TestsNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-25`

**AC-ALG-B-01** — *Both main and feature branch contributions counted*

- GIVEN AI lines are added on main and on a feature branch and then merged during the window
- WHEN Algorithm B computes the period-added result
- THEN both contributions survive and count correctly

**AC-ALG-B-02** — *Lines present on both branches before the merge must not be double-counted*

- GIVEN a line exists on both main and the feature branch before the in-window merge
- WHEN Algorithm B computes the period-added result
- THEN that line is counted at most once

---

### USNG-ALGB-HISTORY-SIMPLE-SCOPE-A-26: SVN-Supported Subset For Algorithm-B Period Contribution

- `WHO`: repository analyst
- `WHEN`: wanting a defended SVN subset for period-added replay without overclaiming full SVN parity
- `WHAT`: make the supported SVN fixture subset produce correct Algorithm B period-added results
- `WHY`: expand SVN support scenario-first while keeping claims defensible
- `Story`: As a repository analyst, I want the defended SVN subset of Algorithm B period-added replay to produce correct results from offline fixtures, so that SVN support can expand scenario-first without overclaiming general parity.
- `Support`: `scope=primary baseline` | `alg=B` | `vcs=svn offline fixtures` | `tier=Fast`
- `Status`: First-class Algorithm B SVN subset story through offline replay. Parity target: `USNG-REPO-SVN-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-A-26`.
- `Anchors`: `TestsNG-REPO-SVN-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-A-26`

**AC-ALG-B-01** — *SVN offline fixtures produce correct period-added result*

- GIVEN SVN-style offline commit-diff fixtures are provided together with protocol files
- WHEN Algorithm B replays the period-added scenario
- THEN it correctly counts AI versus human lines from the SVN patches

---

## Algorithm-B Scope Broadening Stories

These stories extend Algorithm B replay to Scope B (code + comments), Scope C
(documentation), and Scope D (all families).

### USNG-ALGB-HISTORY-SIMPLE-SCOPE-B-18: Algorithm B Must Support Scope B

- `WHO`: repository analyst
- `WHEN`: needing replay-based attribution across source code plus source comments
- `WHAT`: make `--algorithm B --scope B` count all non-blank source lines including comments
- `WHY`: measure total AI contribution to all source text using the incremental replay algorithm
- `Story`: As a repository analyst, I want `--algorithm B --scope B` to count all non-blank source lines including comments during replay, so that I can measure total AI contribution to all source text using the incremental replay algorithm.
- `Support`: `scope=B` | `alg=B` | `vcs=current supported replay shapes` | `tier=Fast`
- `Status`: First-class scope story. Parity target: `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-B-18`.
- `Anchors`: `TestsNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-B-18`

**AC-ALG-B-01** — *Comment lines counted under Algorithm B Scope B*

- GIVEN a source file contains both code lines and comment lines
- WHEN Algorithm B runs with `--scope B`
- THEN `totalCodeLines` includes all non-blank source lines

---

### USNG-ALGB-HISTORY-SIMPLE-SCOPE-C-19: Algorithm B Must Support Scope C

- `WHO`: repository analyst
- `WHEN`: needing replay-based attribution on documentation files instead of source files
- `WHAT`: make `--algorithm B --scope C` replay and count documentation file lines through `docLines`
- `WHY`: measure AI contribution to documentation using the incremental replay algorithm
- `Story`: As a repository analyst, I want `--algorithm B --scope C` to replay and count documentation file lines using the `docLines` protocol field, so that I can measure AI contribution to documentation using the incremental replay algorithm.
- `Support`: `scope=C` | `alg=B` | `vcs=current supported replay shapes` | `tier=Fast`
- `Status`: First-class scope story. Parity target: `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-C-19`.
- `Anchors`: `TestsNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-C-19`

**AC-ALG-B-01** — *Doc field family emitted*

- GIVEN a documentation file contains non-blank lines
- WHEN Algorithm B runs with `--scope C`
- THEN it emits `totalDocLines`, `fullGeneratedDocLines`, and `partialGeneratedDocLines`

**AC-ALG-B-02** — *docLines protocol index used during replay*

- GIVEN the protocol `DETAIL` entry for the documentation file uses `docLines`
- WHEN Algorithm B performs line-ratio lookup during replay
- THEN it uses the doc protocol index

---

### USNG-ALGB-HISTORY-SIMPLE-SCOPE-D-20: Algorithm B Must Support Scope D

- `WHO`: repository analyst
- `WHEN`: needing replay-based attribution across both source and documentation files in one run
- `WHAT`: make `--algorithm B --scope D` replay both file families into one combined result
- `WHY`: measure total AI contribution across all textual repository content using the incremental replay algorithm
- `Story`: As a repository analyst, I want `--algorithm B --scope D` to replay both source files and documentation files into a unified result, so that I can measure total AI contribution across all textual repository content using the incremental replay algorithm.
- `Support`: `scope=D` | `alg=B` | `vcs=current supported replay shapes` | `tier=Fast`
- `Status`: First-class scope story. Parity target: `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-D-20`.
- `Anchors`: `TestsNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-D-20`

**AC-ALG-B-01** — *Both file families replayed*

- GIVEN a repository contains both source files and documentation files
- WHEN Algorithm B runs with `--scope D`
- THEN it replays both file families, using `codeLines` for source files and `docLines` for documentation files

**AC-ALG-B-02** — *Combined summary fields*

- GIVEN Algorithm B produces a combined replay result under `--scope D`
- WHEN the summary is emitted
- THEN it uses `totalCodeLines`, `fullGeneratedCodeLines`, and `partialGeneratedCodeLines`

---

## Period-Added Scope Broadening Stories

These stories extend the period-added metric to Scope B, C, and D.

### USNG-ALGB-HISTORY-SIMPLE-SCOPE-B-33: Period-Added Metric For Documentation Lines

- `WHO`: repository analyst
- `WHEN`: wanting to measure AI contribution to documentation lines added during a requested period
- `WHAT`: report period-added AI attribution for documentation lines in the requested window
- `WHY`: documentation evolution needs its own attribution window separate from source-code measurement
- `Story`: As a repository analyst, I want the period-added metric for documentation lines (SCOPE-B) to report correct AI attribution within a requested period window.
- `Support`: `scope=B` | `alg=B` | `vcs=git local replay` | `tier=Fast`
- `Status`: New USNG cell. Parity target: `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-B-33`.
- `Anchors`: `TestsNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-B-33`

**AC-ALG-B-01** — *Correct period-added documentation attribution*

- GIVEN a Git repository contains documentation files and the requested period defines a `startTime~endTime` window
- WHEN Algorithm B computes the period-added metric with `--scope B`
- THEN it reports the AI-attributed documentation lines added during the window

---

### USNG-ALGB-HISTORY-SIMPLE-SCOPE-C-34: Period-Added Metric For Combined Source Scope

- `WHO`: repository analyst
- `WHEN`: wanting to measure AI contribution to combined source lines (code + comments) added during a requested period
- `WHAT`: report period-added AI attribution for both code and comment lines in one combined result
- `WHY`: some teams attribute AI contribution across both code and comments
- `Story`: As a repository analyst, I want the period-added metric for combined source lines (SCOPE-C) to aggregate both code and comment lines in one period result.
- `Support`: `scope=C` | `alg=B` | `vcs=git local replay` | `tier=Fast`
- `Status`: New USNG cell. Parity target: `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-C-34`.
- `Anchors`: `TestsNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-C-34`

**AC-ALG-B-01** — *Combined source attribution in one period result*

- GIVEN a Git repository contains source files with both code lines and comment lines
- WHEN Algorithm B computes the period-added metric with `--scope C`
- THEN it reports AI-attributed lines from both code and comment families added during the window in one combined result

**AC-ALG-B-02** — *Code and comment families stay distinct inside the combined result*

- GIVEN Algorithm B produces a period-added SCOPE-C result
- WHEN the result `SUMMARY` is read
- THEN code-family and comment-family attribution values are independently accessible

---

### USNG-ALGB-HISTORY-SIMPLE-SCOPE-D-35: Period-Added Metric For All Scopes

- `WHO`: repository analyst
- `WHEN`: wanting a single comprehensive view of AI contribution across all line families during a period
- `WHAT`: report period-added AI attribution for all line families in one period result
- `WHY`: leadership-level summaries need one number that covers all AI-added content
- `Story`: As a repository analyst, I want the period-added metric for all line families (SCOPE-D) to cover code, comment, and documentation lines in one period result.
- `Support`: `scope=D` | `alg=B` | `vcs=git local replay` | `tier=Fast`
- `Status`: New USNG cell. Parity target: `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-D-35`.
- `Anchors`: `TestsNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-D-35`

**AC-ALG-B-01** — *All-families period-added result*

- GIVEN a Git repository contains both source files and documentation files
- WHEN Algorithm B computes the period-added metric with `--scope D`
- THEN it reports AI-attributed lines across code, comment, and documentation families in one combined result

**AC-ALG-B-02** — *Field families stay independently accessible*

- GIVEN Algorithm B produces a period-added SCOPE-D result
- WHEN the result `SUMMARY` is read
- THEN code-family, comment-family, and documentation-family attribution values are each independently accessible

---

## Cross-Algorithm Parity

### USNG-ALGB-HISTORY-SIMPLE-SCOPE-ALL-27: Algorithm A And Algorithm B Must Produce Identical SUMMARY For Every Scope

- `WHO`: repository analyst
- `WHEN`: comparing the blame-based and replay-based implementations on the same repository content
- `WHAT`: keep `SUMMARY` identical across Algorithm A and Algorithm B for every scope
- `WHY`: ensure algorithm choice does not change the measurement result
- `Story`: As a repository analyst, I want Algorithm A and Algorithm B to produce the same `SUMMARY` for every scope on the same repository content, so that algorithm choice does not change the measurement result.
- `Support`: `scope=A/B/C/D` | `alg=A and B` | `vcs=shared replay-supported shapes` | `tier=Fast`
- `Status`: First-class cross-algorithm cross-scope parity story. Parity target: `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-ALL-27`.
- `Anchors`: `TestsNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-ALL-27`

**AC-01** — *Scope A parity*

- GIVEN a repository contains source files and documentation files
- WHEN Algorithm A and Algorithm B are both run with `--scope A`
- THEN they produce identical `SUMMARY` values

**AC-02** — *Remaining-scope parity*

- GIVEN the same repository is analyzed under scopes B, C, and D
- WHEN Algorithm A and Algorithm B are both run
- THEN they produce identical `SUMMARY` values

---

## Hardening

### USNG-ALGB-HISTORY-SIMPLE-SCOPE-RUNTIME-28: Production Hardening — File-Size Guard

- `Support`: `scope=input and runtime guard` | `alg=B` | `vcs=git-focused runtime checks` | `tier=Fast`
- `Status`: Shared hardening story with Algorithm A. Parity target: `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-RUNTIME-28`.
- `Anchors`: `TestsNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-RUNTIME-28`

**AC-HARD-02** — *Algorithm B oversized-file guard*

- GIVEN a Git repository contains a file whose `git show` output exceeds `MAX_FILE_SIZE_BYTES`
- WHEN Algorithm B reads the file through `read_git_file_lines_at_revision`
- THEN it raises `RepositoryStateError` with a clear diagnostic

---

## Operator Logging

### USNG-ALGB-HISTORY-COMPLICATED-SCOPE-RUNTIME-29: Info-Level Log Must Show Replay Progress And Final Summary

- `WHO`: CLI operator running with `--logLevel info`
- `WHEN`: the operator wants to understand the replay attribution story from stderr without enabling debug logging
- `WHAT`: show a structured info-level narrative covering replay start state, per-batch replay progress, and final summary
- `WHY`: help the operator confirm replay progressed correctly and understand the final aggregate result without switching to `--logLevel debug`
- `Story`: As a CLI operator running with `--logLevel info`, I want to see a structured replay narrative on stderr covering initial load state, per-batch replay hints, and final summary, so that I can verify the replay attributed lines correctly without switching to `--logLevel debug`.
- `Support`: `scope=stderr behavior` | `alg=B` | `vcs=shared replay shapes` | `tier=Fast target`
- `Status`: Partial AlgB analog of parent story `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-RUNTIME-29`. AlgB emits replay-phase progress instead of per-file blame phases. Logging phases: (1) load: commitDiffSet count and window, (2) replay: per-patch progress hints, (3) summarize: final aggregate.
- `Anchors`: `OperatorScenarioNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-RUNTIME-29`

**AC-OPS-01** — *Start-state header on stderr*

- GIVEN the CLI runs with `--logLevel info` and Algorithm B is selected
- WHEN replay starts
- THEN stderr emits an `[INFO]` line containing `commitDiffSetDir=` (offline mode) or `repo=` (local Git mode), `branch=`, `window=`, and `patchCount=`

**AC-OPS-02** — *Replay transition hint on ownership change*

- GIVEN the CLI runs with `--logLevel info` and a replayed patch changes a line's ownership state
- WHEN that patch is processed
- THEN stderr may emit an `[INFO] ReplayHint` line noting the transition direction, e.g. `best_effort_transition=`

**AC-OPS-03** — *Final summary on stderr*

- GIVEN the CLI runs with `--logLevel info` and replay finishes
- WHEN the final aggregate is produced
- THEN stderr emits an `[INFO]` summary line containing `totalCodeLines=`, `fullGeneratedCodeLines=`, `partialGeneratedCodeLines=`, `elapsed=`, and `costSeconds=`

**AC-OPS-04** — *Quiet mode suppresses replay hints*

- GIVEN the CLI runs with `--logLevel quiet`
- WHEN the analyzer would otherwise emit replay transition hints
- THEN `ReplayHint` lines are suppressed

**AC-OPS-05** — *Debug mode shows all replay diagnostic tiers*

- GIVEN the CLI runs with `--logLevel debug`
- WHEN replay progresses through patch loading, line-state transitions, metadata lookup, and cache reuse
- THEN patch-level, line-state, out-of-window skip, and cached-metadata-reuse diagnostics remain visible in addition to all info-level lines

---

## Scope Expansion Under Complicated And Complex History

These stories extend the SHARED behavioral contracts of stories 02–07 (COMPLICATED attribution semantics) and stories 09–11 (COMPLEX scale/depth semantics) to the documentation-file family (SCOPE-B), the combined source scope (SCOPE-C), and the all-families scope (SCOPE-D). Coverage is bounded by `UI-NARROW-BOUNDARY`: Algorithm B evidence covers the approved replay scenario for each story only. The attribution contracts are identical across scopes; only the file-family selector changes.

### USNG-ALGB-HISTORY-COMPLICATED-SCOPE-B-36: Attribution Contract Applies Identically To Documentation Lines Via Replay

- `WHO`: repository analyst
- `WHEN`: the target scope is the documentation-file family (SCOPE-B) and the replay window contains rewrites, deletes, renames, or merges
- `WHAT`: apply the same attribution resolution rules as SCOPE-A to documentation-only lines during replay
- `WHY`: the metric contract for attribution semantics must hold for documentation files the same way it holds for source files
- `Story`: As a repository analyst, I want the complete COMPLICATED-history attribution contract to apply to documentation lines (SCOPE-B) during Algorithm B replay, so that file family does not create a different rule set for human-vs-AI ownership resolution.
- `Support`: `scope=B doc baseline` | `alg=B via narrow replay scenario` | `vcs=shared replay shapes` | `tier=Fast`
- `Status`: Scope expansion of stories 02–07 to the documentation family via Algorithm B replay. Subject to `UI-NARROW-BOUNDARY`. Parent: `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-B-36`.
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-B-36`

**AC-01** — *Human rewrite of doc line clears prior AI attribution via replay*

- GIVEN a documentation line was previously attributed to AI before `endTime`
- WHEN Algorithm B replays the patch that overwrites that line with a human revision
- THEN attribution resets to the human revision and the line is counted as `totalDocLines` only

**AC-02** — *AI rewrite of doc line replaces prior human ownership via replay*

- GIVEN a documentation line was previously attributed to a human before `endTime`
- WHEN Algorithm B replays the patch that overwrites that line with an AI revision
- THEN attribution becomes the AI revision and the line is reflected in the AI doc counter

**AC-03** — *Deleted AI doc lines excluded from SCOPE-B result*

- GIVEN AI-attributed documentation lines existed in the replay window but are absent from the surviving state at `endTime`
- WHEN Algorithm B aggregates the SCOPE-B result
- THEN deleted AI doc lines are excluded from both numerator and denominator

**AC-04** — *Rename preserves doc-line attribution across replay*

- GIVEN a documentation file is renamed or moved before `endTime` without changing content
- WHEN Algorithm B replays the rename patch
- THEN line attribution is preserved across the path-only change

**AC-05** — *Mixed replay window resolves to one correct SCOPE-B result*

- GIVEN one replay window contains documentation patches with mixed human-only, AI-only, rewrite, and deletion paths
- WHEN Algorithm B replays the full window and aggregates the SCOPE-B result
- THEN each surviving doc line is resolved by its latest effective attribution from the replay

**AC-ALG-B-01** — *Algorithm B approved scenario*

- GIVEN the approved `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-B-36` replay scenario
- WHEN Algorithm B is executed
- THEN the result matches the approved NG golden output

---

### USNG-ALGB-HISTORY-COMPLICATED-SCOPE-C-37: Attribution Contract Applies Identically To Combined Source Lines Via Replay

- `WHO`: repository analyst
- `WHEN`: the target scope is combined source code and comments (SCOPE-C) and the replay window contains attribution edge cases
- `WHAT`: apply the same attribution resolution rules as SCOPE-A to combined source lines during replay
- `WHY`: the metric contract must be consistent when comment lines are included in the source scope
- `Story`: As a repository analyst, I want the complete COMPLICATED-history attribution contract to apply to combined source-and-comment lines (SCOPE-C) during Algorithm B replay, so that adding comment lines to the scope does not change attribution resolution semantics.
- `Support`: `scope=C combined baseline` | `alg=B via narrow replay scenario` | `vcs=shared replay shapes` | `tier=Fast`
- `Status`: Scope expansion of stories 02–07 to the combined source scope via Algorithm B replay. Subject to `UI-NARROW-BOUNDARY`. Parent: `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-C-37`.
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-C-37`

**AC-01** — *Full attribution contract holds for combined source lines via replay*

- GIVEN the target scope is SCOPE-C and the replay window contains human rewrites, AI rewrites, deletions, renames, and merges
- WHEN Algorithm B replays the full window
- THEN each surviving line's attribution is determined by the same latest-effective-attribution rule as SCOPE-A, applied independently to code lines and comment lines alike

**AC-02** — *Deleted AI lines excluded across both code and comment sub-families*

- GIVEN AI-attributed code lines or comment lines existed in the replay window but are absent from the surviving state at `endTime`
- WHEN Algorithm B aggregates the SCOPE-C result
- THEN deleted AI lines from both sub-families are excluded from both numerator and denominator

**AC-03** — *Rename preserves attribution for combined source lines across replay*

- GIVEN a source file is renamed or moved before `endTime` without changing content
- WHEN Algorithm B replays the rename patch
- THEN line attribution is preserved across the path-only change for both code and comment sub-families

**AC-ALG-B-01** — *Algorithm B approved scenario*

- GIVEN the approved `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-C-37` replay scenario
- WHEN Algorithm B is executed
- THEN the result matches the approved NG golden output

---

### USNG-ALGB-HISTORY-COMPLICATED-SCOPE-D-38: Attribution Contract Applies Identically To All-Families Scope Via Replay

- `WHO`: repository analyst
- `WHEN`: the target scope covers all file families (SCOPE-D) and the replay window contains attribution edge cases
- `WHAT`: apply the same attribution resolution rules as SCOPE-A to all file families during replay
- `WHY`: a single aggregate result across all families must resolve attribution consistently with per-family results
- `Story`: As a repository analyst, I want the complete COMPLICATED-history attribution contract to apply when SCOPE-D covers all file families together during Algorithm B replay, so that combining families in one aggregate does not create attribution inconsistencies.
- `Support`: `scope=D all-families baseline` | `alg=B via narrow replay scenario` | `vcs=shared replay shapes` | `tier=Fast`
- `Status`: Scope expansion of stories 02–07 to all-families scope via Algorithm B replay. Subject to `UI-NARROW-BOUNDARY`. Parent: `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-D-38`.
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-D-38`

**AC-01** — *Full attribution contract holds across all families via replay*

- GIVEN the target scope is SCOPE-D and the replay window contains attribution edge cases spanning source, documentation, and other file families
- WHEN Algorithm B replays the full window and produces the all-families aggregate
- THEN each surviving line's attribution is resolved by the same latest-effective-attribution rule regardless of which family it belongs to

**AC-02** — *SCOPE-D aggregate is consistent with per-family sub-results via replay*

- GIVEN replay produces specific results for each constituent family scope
- WHEN the SCOPE-D aggregate is computed
- THEN its aggregate values are arithmetically consistent with summing the constituent family numerators and denominators

**AC-03** — *Rename preserves attribution across all file families via replay*

- GIVEN a source or documentation file is renamed or moved before `endTime` without changing content
- WHEN Algorithm B replays the rename patch under SCOPE-D
- THEN line attribution is preserved across the path-only change regardless of which file family the file belongs to

**AC-ALG-B-01** — *Algorithm B approved scenario*

- GIVEN the approved `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-D-38` replay scenario
- WHEN Algorithm B is executed
- THEN the result matches the approved NG golden output

---

### USNG-ALGB-HISTORY-COMPLEX-SCOPE-B-39: Large File Set Scale Contract Holds For Documentation Lines Via Replay

- `WHO`: repository analyst
- `WHEN`: the target scope is SCOPE-B and the replay window spans many documentation files and many patch operations
- `WHAT`: preserve result semantics for documentation lines at scale, consistent with story 09
- `WHY`: patch set size must not degrade or change metric semantics for the documentation-file family
- `Story`: As a repository analyst, I want the COMPLEX-history scale contract for large repositories to apply to documentation lines (SCOPE-B) during Algorithm B replay, so that file family does not cause different scale behaviour under heavy patch volume.
- `Support`: `scope=B doc baseline` | `alg=B via narrow replay scenario` | `vcs=shared replay shapes` | `tier=Fast`
- `Status`: Scope expansion of stories 09–11 to the documentation family via Algorithm B replay. Subject to `UI-NARROW-BOUNDARY`. Parent: `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-B-39`.
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-B-39`

**AC-01** — *Per-line attribution rules unchanged by documentation scope size during replay*

- GIVEN the replay window contains many documentation files and many patch operations spanning many revisions
- WHEN Algorithm B replays the full window and computes the final aggregate SCOPE-B result
- THEN patch volume and documentation-file count do not change per-line attribution rules or the protocol shape of the final result

**AC-02** — *Deep replay history preserves latest effective attribution for doc lines*

- GIVEN surviving documentation lines at `endTime` come through long patch chains with many intermediate rewrites
- WHEN Algorithm B resolves each surviving doc line
- THEN it uses latest effective attribution rather than earlier superseded revisions

**AC-03** — *Merge patches preserve per-doc-line attribution*

- GIVEN the replay window contains merge patches and surviving documentation lines originate from different merged branches
- WHEN Algorithm B resolves the final SCOPE-B live state
- THEN each surviving doc line is preserved independently and ownership is not flattened to the merge patch identity

**AC-ALG-B-01** — *Algorithm B approved scenario*

- GIVEN the approved `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-B-39` replay scenario
- WHEN Algorithm B is executed
- THEN the result matches the approved NG golden output

---

### USNG-ALGB-HISTORY-COMPLEX-SCOPE-C-40: Large File Set Scale Contract Holds For Combined Source Lines Via Replay

- `WHO`: repository analyst
- `WHEN`: the target scope is SCOPE-C and the replay window spans many source and comment patches from many revisions
- `WHAT`: preserve result semantics for combined source lines at scale, consistent with story 09
- `WHY`: patch set size must not degrade or change metric semantics for combined source scope
- `Story`: As a repository analyst, I want the COMPLEX-history scale contract for large repositories to apply to combined source-and-comment lines (SCOPE-C) during Algorithm B replay, so that combining code and comment families does not cause different scale behaviour under heavy patch volume.
- `Support`: `scope=C combined baseline` | `alg=B via narrow replay scenario` | `vcs=shared replay shapes` | `tier=Fast`
- `Status`: Scope expansion of stories 09–11 to the combined source scope via Algorithm B replay. Subject to `UI-NARROW-BOUNDARY`. Parent: `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-C-40`.
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-C-40`

**AC-01** — *Scale contract holds for combined source and comment lines via replay*

- GIVEN the final live SCOPE-C snapshot spans many source and comment patches from many files
- WHEN Algorithm B replays the full window and produces the SCOPE-C aggregate
- THEN result semantics, per-line attribution rules, and protocol shape are identical to the SCOPE-A scale contract

**AC-02** — *Merge patches preserve per-line attribution across SCOPE-C*

- GIVEN the replay window contains merge patches and surviving lines span code and comment families
- WHEN Algorithm B resolves the final SCOPE-C live state
- THEN per-line attribution is preserved independently regardless of file family

**AC-03** — *Deep replay history preserves latest effective attribution for combined source lines*

- GIVEN surviving code and comment lines at `endTime` come through long patch chains with many intermediate rewrites
- WHEN Algorithm B resolves each surviving SCOPE-C line
- THEN it uses the latest effective attribution rather than earlier superseded revisions, applied independently to code lines and comment lines

**AC-ALG-B-01** — *Algorithm B approved scenario*

- GIVEN the approved `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-C-40` replay scenario
- WHEN Algorithm B is executed
- THEN the result matches the approved NG golden output

---

### USNG-ALGB-HISTORY-COMPLEX-SCOPE-D-41: Large File Set Scale Contract Holds For All-Families Scope Via Replay

- `WHO`: repository analyst
- `WHEN`: the target scope is SCOPE-D and the replay window spans many files across all families from many revisions
- `WHAT`: preserve result semantics for the all-families scope at scale, consistent with story 09
- `WHY`: the comprehensive all-families aggregate must remain correct and consistent under heavy patch volume
- `Story`: As a repository analyst, I want the COMPLEX-history scale contract for large repositories to apply to all file families together (SCOPE-D) during Algorithm B replay, so that the comprehensive aggregate result remains correct and consistent under heavy replay volume.
- `Support`: `scope=D all-families baseline` | `alg=B via narrow replay scenario` | `vcs=shared replay shapes` | `tier=Fast`
- `Status`: Scope expansion of stories 09–11 to all-families scope via Algorithm B replay. Subject to `UI-NARROW-BOUNDARY`. Parent: `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-D-41`.
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-D-41`

**AC-01** — *Scale contract holds across all families at once via replay*

- GIVEN the final live SCOPE-D snapshot spans many patches from source, documentation, and all other families
- WHEN Algorithm B replays the full window and produces the all-families aggregate
- THEN result semantics, per-line attribution rules, and protocol shape are identical to the SCOPE-A scale contract

**AC-02** — *SCOPE-D aggregate remains consistent with per-family sub-results at replay scale*

- GIVEN a large replay window produces well-defined results for each constituent family scope
- WHEN the SCOPE-D aggregate is computed against the same replay input
- THEN its aggregate values are arithmetically consistent with summing the constituent family numerators and denominators

**AC-03** — *Deep replay history preserves latest effective attribution across all families*

- GIVEN surviving lines at `endTime` across all file families come through long patch chains with many intermediate rewrites
- WHEN Algorithm B resolves each surviving SCOPE-D line
- THEN it uses the latest effective attribution rather than earlier superseded revisions, regardless of which file family the line belongs to

**AC-04** — *Merge patches preserve per-line attribution across all families*

- GIVEN the replay window contains merge patches and surviving lines originate from different merged branches across source, documentation, and other file families
- WHEN Algorithm B resolves the final SCOPE-D live state
- THEN each surviving line is preserved independently and ownership is not flattened to the merge patch identity, regardless of file family

**AC-ALG-B-01** — *Algorithm B approved scenario*

- GIVEN the approved `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-D-41` replay scenario
- WHEN Algorithm B is executed
- THEN the result matches the approved NG golden output

---

## Explicit Exclusions

The following USNG stories are intentionally **not** carried in this document because they require live VCS access or operations that Algorithm B's offline replay model does not perform.

| USNG Story | Reason Not In AlgB |
|---|---|
| 12 — Git production-scale Heavy gate | Requires live `git blame` at production scale. AlgB operates offline; tier-Heavy replay scale is covered under `UI-NARROW-BOUNDARY` in stories 09–11. |
| 13 — SVN production-scale Heavy gate | Same — live SVN blame access is not part of the AlgB execution path. |
| 30 — Remote Git identity | AlgB reads diffs from a local Git checkout or offline fixture directory. Remote Git identity routing does not change the replay algorithm contract. |
| 31 — Remote SVN URL | AlgB SVN support uses offline fixtures only. Remote SVN URL resolution is not part of the replay path. |
| 32 — Provider-side genCodeDesc | AlgB reads per-revision metadata from `--genCodeDescSetDir`. Provider-side fetching changes only the data-prep step, not the replay algorithm contract itself. |
| 42 — SVN path-copy branching | AlgB SVN support is via offline fixtures with pre-resolved history. Path-copy tracking is a preprocessing concern outside the replay path. |
