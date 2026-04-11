# AggregateGenCodeDesc — Algorithm A User Stories

## Purpose

This document defines the user stories for **Algorithm A** (`AlgA`).

Algorithm A is the recommended production algorithm for live-snapshot attribution.
It operates directly on an active repository checkout, invoking `git blame` or
`svn blame` subprocesses to determine each surviving line's effective origin revision.
Combined with per-revision `genCodeDescProtoV26.03` metadata, it computes the
weighted AI ratio for live source-code lines whose current version changed inside
the requested `startTime~endTime` window.

Algorithm A supports all four measurement scopes (A, B, C, D), both Git and SVN
repositories, and both local and remote-identity access patterns.

## Protocol Precondition

All AlgA stories require `protocolVersion: "26.03"` per-revision metadata files.
Algorithm A relies on the VCS subprocess (`git blame` / `svn blame`) for line
attribution and reads only the `codeLines` (or `docLines`) entries from the
per-revision metadata to determine `genRatio` and `genMethod` for each in-scope origin
revision.

A `genCodeDescProtoV26.04` input is not expected by Algorithm A. When Algorithm A
encounters a v26.04 file, it reads only the v26.03-compatible fields.

## Relationship To Algorithm B and Algorithm C

| Property | Algorithm A | Algorithm B | Algorithm C |
| --- | --- | --- | --- |
| Repository access | live `git/svn blame` | offline diff replay | none |
| Input | repo + per-revision genCodeDesc v26.03 | commitDiffSet + per-revision genCodeDesc v26.03 | per-revision genCodeDesc **v26.04** only |
| Blame source | VCS subprocess | diff patch reconstruction | embedded `blame` object in DETAIL |
| DETAIL completeness required | no (AI lines only) | no (AI lines only) | exhaustive surviving-line DETAIL required for correctness in the current slice |
| VCS support | git and svn | git and svn | git-origin and svn-origin blame |
| Scope support | A, B, C, D | A, B, C, D | A (current slice) |
| Metric semantics | identical | identical | identical |

## Story Rules

1. Every story follows the `WHO` / `WHEN` / `WHAT` / `WHY` / `Story` / `Support` / `Status` / `Anchors` format.
2. Acceptance criteria use plain `GIVEN / WHEN / THEN` blocks with story-local IDs.
3. Every story that claims parity with Algorithm B or Algorithm C must name the matching USNG story ID.
4. `tier=Heavy` stories must name a concrete scale floor in at least one acceptance criterion.

## Story ID Convention

```text
USNG-ALGA-HISTORY-<C>-SCOPE-<D>-<NN>: Title
```

- `HISTORY-<C>`: `SIMPLE` | `COMPLICATED` | `COMPLEX`
  - `SIMPLE`: linear baselines, direct parity contracts, scope-only contracts
  - `COMPLICATED`: overwrites, deletions, renames, mixed commit chains, merge-aware flows
  - `COMPLEX`: large file sets, deep history, many-branch fan-in, production scale (≥10 000 commits, ≥100 branches)
- `SCOPE-<D>`: `A` | `B` | `C` | `D` | `ALL` | `RUNTIME`
- `REPO` and `GENCODEDESC` dimensions are carried by the `Support` and `Status` fields, not by the story ID.

---

## Universal Story Invariants

The following invariants apply to every AlgA story unless overridden explicitly.

- `UI-PROTOCOL`: the result must be a valid protocol-shaped output with `protocolName`,
  `protocolVersion`, `SUMMARY`, and `REPOSITORY` fields.
- `UI-GOLDEN`: for scenarios whose fixtures provide approved golden outputs, the result
  must match the approved golden output for the scenario.
- `UI-LIVE-BLAME`: Algorithm A determines each surviving line's effective origin revision
  by invoking `git blame` or `svn blame` at `endRevision`. The VCS subprocess output is
  the authoritative evidence source.
- `UI-VCS-REQUIRED`: Algorithm A requires runtime access to the repository. A local Git
  checkout or an accessible SVN repository must be available.
- `UI-GENCODEDESC-V2603`: Algorithm A reads per-revision `genCodeDescProtoV26.03`
  metadata from `--genCodeDescSetDir`. Each in-scope origin revision discovered from
  blame must have a matching `<revisionId>_genCodeDesc.json` file.
- `UI-SCOPE-ORTHOGONAL`: scope selection (A, B, C, D) is orthogonal to algorithm choice.
  Scope controls **which files and lines** are measured; the algorithm controls **how**
  line-origin attribution is determined.
- `UI-VCS-DUAL`: Algorithm A supports both Git and SVN. Git uses `git blame --porcelain`;
  SVN uses `svn blame` with revision-range filtering. Both paths produce the same
  metric semantics.
- `UI-PARITY`: the target contract is parity with Algorithm B and Algorithm C.
  Algorithm A is the reference implementation; Algorithm B and Algorithm C claim parity
  with Algorithm A, not the reverse.

---

## HISTORY-SIMPLE Stories

### USNG-ALGA-HISTORY-SIMPLE-SCOPE-A-01: Calculate Weighted AI Ratio For Live Changed Source Code In A Requested Time Window

- `WHO`: repository analyst
- `WHEN`: querying one repository branch for a window `startTime~endTime`, needing the live-snapshot answer at `endTime`
- `WHAT`: calculate the weighted AI ratio for live source-code lines whose current version changed inside the requested window
- `WHY`: know how much of the current live changed source code is attributable to AI
- `Story`: As a repository analyst, I want to calculate the weighted AI ratio for live source-code lines whose current version falls in a requested period `startTime~endTime`, so that I can know how much of the current live changed source code is attributable to AI.
- `Support`: `scope=A baseline` | `alg=A` | `vcs=git and svn` | `tier=Fast`
- `Status`: Covered by Algorithm A for both Git and SVN. Parity target: `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-01`.
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-01-GIT`, `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-01-SVN`

**AC-01** — *Core measurement contract*

- GIVEN a query `repo + branch + startTime + endTime` for the live-snapshot metric
- WHEN Algorithm A invokes `git blame` or `svn blame` at `endRevision` and cross-references each surviving line's origin revision against per-revision `genCodeDescProtoV26.03` metadata
- THEN it returns exactly one repository-level result describing the AI ratio among live source-code lines whose current version was added or modified in `startTime~endTime`

**AC-02** — *External genCodeDesc integration*

- GIVEN external `genCodeDesc` records stored in `--genCodeDescSetDir`, indexed by `repoURL + repoBranch + revisionId`
- WHEN Algorithm A discovers in-scope origin revisions from blame output
- THEN it fetches and uses the matching metadata records during aggregation

**AC-03** — *Missing genCodeDesc record treated as human/unattributed*

- GIVEN one or more in-scope origin revisions have no matching `genCodeDesc` record in the metadata store
- WHEN the analyzer aggregates the final result
- THEN those lines are counted as human/unattributed rather than being silently skipped or causing the run to error

**AC-GIT-01** — *Algorithm A · Git*

- GIVEN a local Git checkout and the approved baseline scenario
- WHEN Algorithm A is executed with `--vcsType git`
- THEN the result matches the approved NG golden output

**AC-SVN-01** — *Algorithm A · SVN*

- GIVEN a local SVN repository and the approved baseline scenario
- WHEN Algorithm A is executed with `--vcsType svn`
- THEN the result matches the approved NG golden output

---

### USNG-ALGA-HISTORY-SIMPLE-SCOPE-A-08: Git And SVN Must Follow The Same Result Contract

- `WHO`: repository analyst
- `WHEN`: the same primary metric is requested against equivalent supported Git and SVN histories
- `WHAT`: keep the query-result contract consistent across VCS targets
- `WHY`: ensure changing VCS type does not change metric semantics or output structure
- `Story`: As a repository analyst, I want Git and SVN targets to follow the same query-result contract for the current primary metric, so that changing VCS type does not change metric semantics or output structure.
- `Support`: `scope=A baseline` | `alg=A` | `vcs=git and svn` | `tier=Fast`
- `Status`: Covered by Algorithm A for Git and SVN. Parity target: `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-08`.
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-08-SVN-PARITY`

**AC-01** — *Same semantics across VCS types*

- GIVEN equivalent supported repository history in Git or SVN for the same requested window
- WHEN Algorithm A computes the live-snapshot metric
- THEN Git and SVN produce one final record with the same metric semantics and protocol-shaped structure, differing only in VCS-specific repository identity details

**AC-GIT-01** — *Git track defines one parity side*

- GIVEN the current Git path for the primary metric
- WHEN it is validated through the baseline live-snapshot scenarios
- THEN it defines one side of the observable parity contract

**AC-SVN-01** — *SVN track preserves shared contract*

- GIVEN the approved SVN parity scenario
- WHEN Algorithm A SVN path is executed
- THEN the result matches the approved NG golden output while preserving the shared story-08 contract

---

## HISTORY-COMPLICATED Stories

### USNG-ALGA-HISTORY-COMPLICATED-SCOPE-A-02: Human Rewrite Removes Prior AI Attribution

- `WHO`: repository analyst
- `WHEN`: a human revision overwrites code previously attributed to AI before `endTime`
- `WHAT`: reset effective attribution to the newer human revision
- `WHY`: prevent old AI ownership from staying attached to overwritten code
- `Story`: As a repository analyst, I want a human rewrite of a previously AI-generated line to reset attribution to the newer human revision, so that old AI ownership does not remain attached to overwritten code.
- `Support`: `scope=A baseline` | `alg=A` | `vcs=git and svn` | `tier=Fast`
- `Status`: Covered by Algorithm A for Git and SVN. Parity target: `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-02`.
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-02`

**AC-01** — *Human rewrite clears prior AI attribution via live blame*

- GIVEN a line's `git blame` / `svn blame` output shows a human commit as the origin inside `[startTime, endTime]`
- WHEN Algorithm A cross-references that origin revision against genCodeDesc metadata and finds `genRatio=0 / genMethod=Manual` (or no metadata)
- THEN the line is counted as `totalCodeLines` only, not in any AI counter

**AC-GIT-01** — *Git human-rewrite*

- GIVEN the approved scenario with a Git repository
- WHEN Algorithm A is executed
- THEN the result matches the approved NG golden output

**AC-SVN-01** — *SVN human-rewrite*

- GIVEN the approved scenario with an SVN repository
- WHEN Algorithm A is executed
- THEN the result matches the approved NG golden output

---

### USNG-ALGA-HISTORY-COMPLICATED-SCOPE-A-03: AI Rewrite Replaces Prior Human Ownership

- `WHO`: repository analyst
- `WHEN`: a later AI revision overwrites a line previously human-authored before `endTime`
- `WHAT`: make the later AI rewrite the effective attribution source
- `WHY`: ensure live changed source code at `endTime` reflects the latest AI contribution
- `Story`: As a repository analyst, I want a later AI rewrite of a human line to become the effective attribution source, so that the live changed source code at `endTime` reflects the latest AI contribution.
- `Support`: `scope=A baseline` | `alg=A` | `vcs=git and svn` | `tier=Fast`
- `Status`: Covered by Algorithm A for Git and SVN. Parity target: `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-03`.
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-03`

**AC-01** — *Later AI revision becomes effective attribution via live blame*

- GIVEN a line's live blame output shows an AI commit (`genRatio > 0`) as the origin inside `[startTime, endTime]`
- WHEN Algorithm A cross-references that origin revision against genCodeDesc metadata
- THEN the line is counted in both `totalCodeLines` and the appropriate AI counter

**AC-GIT-01** — *Git AI-rewrite*

- GIVEN the approved scenario with a Git repository
- WHEN Algorithm A is executed
- THEN the result matches the approved NG golden output

**AC-SVN-01** — *SVN AI-rewrite*

- GIVEN the approved scenario with an SVN repository
- WHEN Algorithm A is executed
- THEN the result matches the approved NG golden output

---

### USNG-ALGA-HISTORY-COMPLICATED-SCOPE-A-04: Deleted AI Lines Must Not Count

- `WHO`: repository analyst
- `WHEN`: AI-generated lines existed earlier in the window but are gone from the branch state at `endTime`
- `WHAT`: exclude deleted AI lines from both numerator and denominator
- `WHY`: keep the result about the current live changed snapshot only
- `Story`: As a repository analyst, I want deleted AI-generated lines to disappear from both numerator and denominator, so that the result reflects only the current live changed source-code snapshot.
- `Support`: `scope=A baseline` | `alg=A` | `vcs=git and svn` | `tier=Fast`
- `Status`: Covered by Algorithm A for Git and SVN. Parity target: `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-04`.
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-04`

**AC-01** — *Deleted lines are absent from blame output and therefore excluded*

- GIVEN live blame at `endRevision` does not return any deleted lines (they no longer exist in the file)
- WHEN Algorithm A processes blame output
- THEN no deleted-line entry exists to be counted; deletion is implicit by absence from blame

**AC-GIT-01** — *Git deletion*

- GIVEN the approved scenario with a Git repository
- WHEN Algorithm A is executed
- THEN the result matches the approved NG golden output

**AC-SVN-01** — *SVN deletion*

- GIVEN the approved scenario with an SVN repository
- WHEN Algorithm A is executed
- THEN the result matches the approved NG golden output

---

### USNG-ALGA-HISTORY-COMPLICATED-SCOPE-A-05: Rename Must Preserve Attribution Lineage

- `WHO`: repository analyst
- `WHEN`: files are renamed or moved before `endTime` without changing their effective content contribution
- `WHAT`: preserve line attribution across path-only history changes
- `WHY`: prevent rename-only changes from distorting the final live changed source-code ratio
- `Story`: As a repository analyst, I want file rename or move operations to preserve line attribution when content does not change, so that the final live changed source-code ratio is not distorted by path-only history changes.
- `Support`: `scope=A baseline` | `alg=A` | `vcs=git (git-follow) and svn (path-copy tracking)` | `tier=Fast`
- `Status`: Covered by Algorithm A for Git and SVN. Git uses `git-follow` semantics; SVN uses path-copy tracking. Parity target: `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-05`.
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-05`

**AC-01** — *Attribution stable across renames via blame*

- GIVEN a file was renamed and `git blame` / `svn blame` traces lines back through the rename to the original authoring revision
- WHEN Algorithm A resolves attribution for surviving lines
- THEN attribution reflects the original authoring revision, not the rename commit

**AC-GIT-01** — *Git rename via git-follow*

- GIVEN the approved rename scenario with a Git repository
- WHEN Algorithm A is executed
- THEN the result matches the approved NG golden output

**AC-SVN-01** — *SVN rename via path-copy*

- GIVEN the approved rename scenario with an SVN repository
- WHEN Algorithm A is executed
- THEN the result matches the approved NG golden output

---

### USNG-ALGA-HISTORY-COMPLICATED-SCOPE-A-06: Resolve Mixed Multi-Commit History In One Requested Window

- `WHO`: repository analyst
- `WHEN`: one requested window contains many commits with mixed human-only, AI-only, rewrite, and deletion paths
- `WHAT`: resolve each surviving line by its latest effective attribution inside the window
- `WHY`: keep one final result correct even when history inside the window is mixed and complex
- `Story`: As a repository analyst, I want one requested window to correctly resolve mixed line histories across many commits, so that the final result remains correct when human-only lines, AI-only lines, human-then-AI rewrites, AI-then-human rewrites, and deleted AI lines all appear in the same period.
- `Support`: `scope=A baseline` | `alg=A` | `vcs=git and svn` | `tier=Fast`
- `Status`: Covered by Algorithm A for Git and SVN. Parity target: `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-06`.
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-06`

**AC-01** — *Mixed window produces one correct final record*

- GIVEN multiple commits inside the requested window contain mixed ownership transitions across different live lines
- WHEN Algorithm A resolves blame at `endRevision` and cross-references each line's origin revision
- THEN it produces exactly one final record using the latest effective attribution of each surviving line

**AC-02** — *Superseded intermediate states do not leak*

- GIVEN a surviving line passes through a long chain of intermediate revisions inside the window
- WHEN Algorithm A resolves that live line at `endRevision` through blame
- THEN blame returns only the latest effective origin, and superseded intermediate ownership does not leak into the final result

**AC-GIT-01** — *Algorithm A · Git*

- GIVEN the approved scenario
- WHEN Algorithm A is executed
- THEN the result matches the approved NG golden output

**AC-SVN-01** — *Algorithm A · SVN*

- GIVEN the approved scenario
- WHEN Algorithm A is executed
- THEN the result matches the approved NG golden output

---

### USNG-ALGA-HISTORY-COMPLICATED-SCOPE-A-07: Merge Commit Must Preserve Effective Attribution

- `WHO`: repository analyst
- `WHEN`: merged branches bring human and AI contributions into the target branch before `endTime`
- `WHAT`: preserve the effective attribution of each surviving line through merges
- `WHY`: prevent merge commits from resetting ownership or flattening provenance
- `Story`: As a repository analyst, I want merged branch content to preserve the effective attribution of surviving lines, so that a merge operation does not incorrectly reset line ownership to the merge commit itself.
- `Support`: `scope=A baseline` | `alg=A` | `vcs=git and svn` | `tier=Fast`
- `Status`: Covered by Algorithm A for Git and SVN merge semantics. Parity target: `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-07`.
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-07`

**AC-01** — *Merge does not reset ownership*

- GIVEN a merge commit brings together earlier human and AI-attributed changes before `endTime`
- WHEN Algorithm A runs `git blame` / `svn blame` at `endRevision`
- THEN blame returns the effective authoring revision for each surviving line, not the merge commit

**AC-02** — *Per-line independence across merged branches*

- GIVEN multiple branches are merged before `endTime` and surviving lines originate from different merged branches
- WHEN Algorithm A resolves the final live state through blame
- THEN it preserves each surviving line independently and does not collapse ownership to merge commits or branch identity alone

**AC-03** — *Merge conflict resolution follows post-resolution committer*

- GIVEN a merge results in conflict markers or manually resolved regions before `endTime`
- WHEN Algorithm A runs blame at `endRevision`
- THEN each post-resolution surviving line is attributed according to the committer of the conflict-resolution commit

**AC-GIT-01** — *Algorithm A · Git*

- GIVEN the approved scenario
- WHEN Algorithm A is executed
- THEN the result matches the approved NG golden output

**AC-SVN-01** — *Algorithm A · SVN*

- GIVEN the approved scenario
- WHEN Algorithm A is executed
- THEN the result matches the approved NG golden output

---

## HISTORY-COMPLEX Stories

### USNG-ALGA-HISTORY-COMPLEX-SCOPE-A-09: Large Repository Snapshot Must Preserve Result Semantics

- `WHO`: repository analyst
- `WHEN`: the repository contains many files and many live lines but the analyst still expects the same metric semantics
- `WHAT`: preserve the live-snapshot contract for large realistic repositories
- `WHY`: keep aggregate results trustworthy at larger repository scales
- `Story`: As a repository analyst, I want the analyzer to keep the same result semantics when the repository contains many source files and many live lines, so that the final aggregate result remains correct for realistic large codebases.
- `Support`: `scope=A baseline` | `alg=A` | `vcs=git and svn` | `tier=Fast`
- `Status`: Covered by Algorithm A for Git and SVN. Parity target: `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-09`.
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-09`

**AC-01** — *Semantics preserved at scale*

- GIVEN the final live snapshot at `endTime` spans many source files and many live code lines
- WHEN Algorithm A invokes blame per file and aggregates all in-scope lines
- THEN it still produces exactly one repository-level final result with the same metric semantics

**AC-02** — *Per-line attribution rules unchanged by size*

- GIVEN a large repository snapshot contains many in-scope lines across many files
- WHEN Algorithm A aggregates the result
- THEN repository size or file count does not change per-line attribution rules

**AC-GIT-01** — *Algorithm A · Git*

- GIVEN the approved scenario
- WHEN Algorithm A is executed
- THEN the result matches the approved NG golden output

**AC-SVN-01** — *Algorithm A · SVN*

- GIVEN the approved scenario
- WHEN Algorithm A is executed
- THEN the result matches the approved NG golden output

---

### USNG-ALGA-HISTORY-COMPLEX-SCOPE-A-10: Deep History Must Preserve Latest Effective Attribution

- `WHO`: repository analyst
- `WHEN`: surviving lines at `endTime` come through long revision chains with many intermediate rewrites
- `WHAT`: resolve each surviving line by its latest effective attribution instead of by superseded intermediate ownership
- `WHY`: prevent deep history from distorting the final live result
- `Story`: As a repository analyst, I want long revision chains to preserve the latest effective attribution of each surviving line, so that many intermediate rewrites do not distort the final live result.
- `Support`: `scope=A baseline` | `alg=A` | `vcs=git and svn` | `tier=Fast`
- `Status`: Covered by Algorithm A for Git and SVN. Parity target: `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-10`.
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-10`

**AC-01** — *Latest effective attribution wins*

- GIVEN in-scope live lines at `endTime` depend on long revision chains with many intermediate rewrites
- WHEN Algorithm A runs blame at `endRevision`
- THEN blame returns each line's latest effective origin revision, not earlier superseded revisions

**AC-02** — *Superseded states do not leak*

- GIVEN long history chains contain both human-to-AI and AI-to-human transitions before `endTime`
- WHEN Algorithm A produces the final aggregate result
- THEN deleted or superseded intermediate states do not leak into that result

**AC-GIT-01** — *Algorithm A · Git*

- GIVEN the approved scenario
- WHEN Algorithm A is executed
- THEN the result matches the approved NG golden output

**AC-SVN-01** — *Algorithm A · SVN*

- GIVEN the approved scenario
- WHEN Algorithm A is executed
- THEN the result matches the approved NG golden output

---

### USNG-ALGA-HISTORY-COMPLEX-SCOPE-A-11: Many Merged Branches Must Preserve Per-Line Attribution

- `WHO`: repository analyst
- `WHEN`: many branches are merged into the target branch inside one requested window
- `WHAT`: preserve per-line effective attribution across branch-heavy merge history
- `WHY`: stop branch fan-in and merge order from distorting the final result
- `Story`: As a repository analyst, I want branch-heavy history inside one requested window to preserve per-line effective attribution, so that integrating many feature branches into the target branch does not distort the final result.
- `Support`: `scope=A baseline` | `alg=A` | `vcs=git and svn (SVN may use defensible analogue)` | `tier=Fast`
- `Status`: Covered by Algorithm A for Git and SVN. SVN parity may require a defensible analogue. Parity target: `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-11`.
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-11`

**AC-01** — *One final record despite branch fan-in*

- GIVEN many branches are merged into the target branch before `endTime`
- WHEN Algorithm A runs blame at `endRevision` and aggregates all in-scope lines
- THEN it still produces exactly one repository-level final result

**AC-02** — *Per-line independence across merged branches*

- GIVEN surviving lines originate from different merged branches with different effective histories
- WHEN Algorithm A resolves blame for each line
- THEN it preserves each surviving line independently and does not flatten ownership to merge commits or branch labels

**AC-GIT-01** — *Algorithm A · Git*

- GIVEN the approved scenario
- WHEN Algorithm A is executed
- THEN the result matches the approved NG golden output

**AC-SVN-01** — *Algorithm A · SVN analogue*

- GIVEN SVN parity requires a defensible analogue (SVN path-copy vs Git reference branches)
- WHEN Algorithm A is executed against the SVN-specific scenario
- THEN the observable result contract is preserved

---

## Heavy Production Gates

These stories are production-scale correctness gates.

### USNG-ALGA-HISTORY-COMPLEX-SCOPE-A-12: Git Production-Scale Local Repository Must Stay Correct Under Branch-Heavy Release Convergence

- `WHO`: repository analyst
- `WHEN`: validating production-readiness on a branch-heavy local Git repository that mirrors release convergence at scale
- `WHAT`: keep Algorithm A + Scope A correct on a production-scale local Git topology
- `WHY`: prove that large branch counts, deep history, and hybrid release merges do not distort the final live attribution result
- `Story`: As a repository analyst, I want Algorithm A and Scope A to remain correct on a production-scale local Git repository, so that large branch counts, deep history, and hybrid release merges do not distort the final live attribution result.
- `Support`: `scope=A baseline` | `alg=A` | `vcs=git` | `tier=Heavy`
- `Status`: Production-facing heavy gate with real local Git repository generation, correctness, and scalability checks. Corresponds to `USNG-REPO-GIT-LOCAL-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-12`.
- `Anchors`: `TestsNG-REPO-GIT-LOCAL-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-12`

**AC-GIT-01** — *Scale floor: ~100+ branches, ~1000+ commits*

- GIVEN a local Git repository with ~100+ branches, ~1000+ commits, and repeated feature-to-integration-to-release merge fan-in before `endTime`
- WHEN Algorithm A computes the final result
- THEN it produces exactly one repository-level final result and the counts match the golden result

**AC-GIT-02** — *Effective origin preserved across deep Git history*

- GIVEN surviving lines reach the release branch through mixed direct merges, integration branches, and staged convergence
- WHEN Algorithm A resolves blame-based attribution
- THEN it is based on each surviving line's effective origin revision rather than merge shape or branch naming

**AC-GIT-03** — *Local topology is valid for production-readiness*

- GIVEN the production-like repository is local rather than remote-hosted
- WHEN it is used as the production-readiness acceptance scenario
- THEN it remains valid because transport is out of scope and history semantics must remain identical

**AC-GIT-04** — *Correctness and scalability both verified*

- GIVEN the heavy Git production-scale scenario completes successfully
- WHEN the acceptance outcome is evaluated
- THEN it verifies both correctness of the final aggregate result and scalability-oriented reuse behavior such as bounded metadata reuse or bounded revision-time lookup reuse

---

### USNG-ALGA-HISTORY-COMPLEX-SCOPE-A-13: SVN Production-Scale Local Repository Must Stay Correct Under Branch And Merge Pressure

- `WHO`: repository analyst
- `WHEN`: validating production-readiness on a production-scale local SVN repository with branch copying and reintegration pressure
- `WHAT`: keep Algorithm A + Scope A correct on a production-scale local SVN topology
- `WHY`: prove that SVN branch copying, merges, and release reintegration at scale do not break live attribution
- `Story`: As a repository analyst, I want Algorithm A and Scope A to remain correct on a production-scale local SVN repository, so that SVN branch copying, merges, and release reintegration at scale do not break live attribution.
- `Support`: `scope=A baseline` | `alg=A` | `vcs=svn` | `tier=Heavy`
- `Status`: Production-facing heavy gate with real local SVN repository generation, correctness, and scalability checks. Corresponds to `USNG-REPO-SVN-LOCAL-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-13`.
- `Anchors`: `TestsNG-REPO-SVN-LOCAL-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-13`

**AC-SVN-01** — *Scale floor: ~100+ branch copies, ~1000+ revisions*

- GIVEN a local SVN repository with ~100+ branch copies, ~1000+ revisions, and repeated branch-to-release merge activity before `endTime`
- WHEN Algorithm A computes the final result
- THEN it produces exactly one repository-level final result and the counts match the golden result

**AC-SVN-02** — *Effective origin preserved across SVN history*

- GIVEN surviving lines reach the release path through mixed direct work, branch copies, and merge or reintegration history
- WHEN Algorithm A resolves blame-based attribution under SVN semantics
- THEN it preserves each surviving line's effective origin revision

**AC-SVN-03** — *Local topology is valid for production-readiness*

- GIVEN the production-like SVN repository is local rather than remote-hosted
- WHEN it is used as the production-readiness acceptance scenario
- THEN it remains valid because transport is not part of the attribution contract

**AC-SVN-04** — *Correctness and scalability both verified*

- GIVEN the heavy SVN production-scale scenario completes successfully
- WHEN the acceptance outcome is evaluated
- THEN it verifies both correctness and scalability-oriented reuse behavior such as branch-origin metadata reuse or bounded revision-time queries

---

## Scope Contract Stories

These stories extend Algorithm A coverage across all four measurement scopes.

### USNG-ALGA-HISTORY-SIMPLE-SCOPE-B-14: Scope B Source Code With Comments Must Include Comment Lines In Totals

- `WHO`: repository analyst
- `WHEN`: wanting source-file totals to include comment lines as part of measured source text
- `WHAT`: make `--scope B` count all non-blank lines in source files, including comments
- `WHY`: measure AI contribution across the full textual content of source files, not just executable code
- `Story`: As a repository analyst, I want `--scope B` to count all non-blank lines in source files, including comment lines, in the aggregate result, so that I can measure AI contribution across the full textual content of source files.
- `Support`: `scope=B` | `alg=A` | `vcs=shared` | `tier=Fast`
- `Status`: First-class scope story. Parity target: `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-B-14`.
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-B-14`

**AC-01** — *Comment lines included in scope B totals*

- GIVEN a source file contains both code lines and comment lines
- WHEN Algorithm A runs with `--scope B`
- THEN `totalCodeLines` includes all non-blank source lines including comments

**AC-02** — *Comment line attribution*

- GIVEN a source file contains comment lines covered through `codeLines`
- WHEN Algorithm A runs with `--scope B`
- THEN comment lines with `genRatio=100` count as `fullGeneratedCodeLines`, and those with `genRatio` between 1 and 99 count as `partialGeneratedCodeLines`

---

### USNG-ALGA-HISTORY-SIMPLE-SCOPE-C-15: Scope C Documentation Text Lines

- `WHO`: repository analyst
- `WHEN`: wanting to measure documentation-only contribution instead of source-code contribution
- `WHAT`: make `--scope C` analyze documentation files and use `docLines` for attribution
- `WHY`: measure AI contribution to documentation artifacts separately from source code
- `Story`: As a repository analyst, I want `--scope C` to analyze documentation text files using the `docLines` protocol field, so that I can measure AI contribution to documentation artifacts separately from source code.
- `Support`: `scope=C` | `alg=A` | `vcs=shared` | `tier=Fast`
- `Status`: First-class scope story. Parity target: `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-C-15`.
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-C-15`

**AC-01** — *Scope C analyzes doc files only*

- GIVEN a repository contains files in `DOC_EXTENSIONS`
- WHEN Algorithm A runs with `--scope C`
- THEN it includes only documentation files and excludes source-code files

**AC-02** — *docLines protocol used for attribution*

- GIVEN documentation files are analyzed under `--scope C`
- WHEN attribution is computed
- THEN the output uses `totalDocLines`, `fullGeneratedDocLines`, and `partialGeneratedDocLines`

---

### USNG-ALGA-HISTORY-SIMPLE-SCOPE-D-16: Scope D All Text Must Unify Source And Documentation

- `WHO`: repository analyst
- `WHEN`: wanting one combined result across both source files and documentation files
- `WHAT`: make `--scope D` count all non-blank source and documentation lines in one aggregate
- `WHY`: measure total AI contribution across the full textual content of the repository
- `Story`: As a repository analyst, I want `--scope D` to count all non-blank lines from both source files and documentation files in one combined result, so that I can measure total AI contribution across the entire textual content of the repository.
- `Support`: `scope=D` | `alg=A` | `vcs=shared` | `tier=Fast`
- `Status`: First-class scope story. Parity target: `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-D-16`.
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-D-16`

**AC-01** — *Both file families included*

- GIVEN a repository contains both source files and documentation files
- WHEN Algorithm A runs with `--scope D`
- THEN it includes both file families in one combined analysis

**AC-02** — *Combined attribution fields*

- GIVEN both source files and documentation files are analyzed under `--scope D`
- WHEN the combined result is emitted
- THEN source lines use `codeLines`, documentation lines use `docLines`, and the combined summary uses `totalCodeLines`, `fullGeneratedCodeLines`, and `partialGeneratedCodeLines`

---

### USNG-ALGA-HISTORY-SIMPLE-SCOPE-ALL-17: Scope Parity Matrix

- `WHO`: repository analyst
- `WHEN`: running all four scopes on the same repository and expecting each scope to stay distinct and correct
- `WHAT`: verify the full scope matrix across A, B, C, and D
- `WHY`: trust that scope selection really controls the measurement boundary
- `Story`: As a repository analyst, I want a cross-scope verification that runs Scope A, B, C, and D on the same repository and confirms each produces the expected distinct result, so that I can trust that scope selection genuinely controls the measurement boundary.
- `Support`: `scope=A/B/C/D` | `alg=A` | `vcs=shared` | `tier=Fast`
- `Status`: First-class cross-scope contract story. Parity target: `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-ALL-17`.
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-ALL-17`

**AC-01** — *Each scope correct independently*

- GIVEN a repository contains source files with code and comments plus documentation files
- WHEN Algorithm A is run with `--scope A`, `--scope B`, `--scope C`, and `--scope D`
- THEN each scope produces the correct summary for its own scope definition

**AC-02** — *Doc vs code field families stay distinct*

- GIVEN the full four-scope matrix is executed
- WHEN the summaries are compared across scopes
- THEN Scope C uses `totalDocLines` / `fullGeneratedDocLines` / `partialGeneratedDocLines`, while Scopes A, B, D use `totalCodeLines` / `fullGeneratedCodeLines` / `partialGeneratedCodeLines`

---

## Scope Expansion Under Complicated And Complex History

These stories extend the COMPLICATED (stories 02–07) and COMPLEX (stories 09–11) attribution contracts to Scope B, C, and D.

### USNG-ALGA-HISTORY-COMPLICATED-SCOPE-B-36: Attribution Contract Applies Identically To Documentation Lines

- `Support`: `scope=B doc baseline` | `alg=A` | `vcs=shared` | `tier=Fast`
- `Status`: Scope expansion of stories 02–07 to the documentation family. Parity target: `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-B-36`.
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-B-36`

**AC-01–AC-05** — Human rewrite, AI rewrite, deletion, rename, and mixed-window contracts apply identically to documentation lines under Scope B.

### USNG-ALGA-HISTORY-COMPLICATED-SCOPE-C-37: Attribution Contract Applies Identically To Combined Source Lines

- `Support`: `scope=C combined baseline` | `alg=A` | `vcs=shared` | `tier=Fast`
- `Status`: Scope expansion of stories 02–07 to the combined source scope. Parity target: `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-C-37`.
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-C-37`

### USNG-ALGA-HISTORY-COMPLICATED-SCOPE-D-38: Attribution Contract Applies Identically To All-Families Scope

- `Support`: `scope=D all-families baseline` | `alg=A` | `vcs=shared` | `tier=Fast`
- `Status`: Scope expansion of stories 02–07 to all-families scope. Parity target: `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-D-38`.
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-D-38`

### USNG-ALGA-HISTORY-COMPLEX-SCOPE-B-39: Large-Repository Scale Contract Holds For Documentation Lines

- `Support`: `scope=B doc baseline` | `alg=A` | `vcs=shared` | `tier=Fast`
- `Status`: Scope expansion of stories 09–11 to the documentation family. Parity target: `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-B-39`.
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-B-39`

### USNG-ALGA-HISTORY-COMPLEX-SCOPE-C-40: Large-Repository Scale Contract Holds For Combined Source Lines

- `Support`: `scope=C combined baseline` | `alg=A` | `vcs=shared` | `tier=Fast`
- `Status`: Scope expansion of stories 09–11 to the combined source scope. Parity target: `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-C-40`.
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-C-40`

### USNG-ALGA-HISTORY-COMPLEX-SCOPE-D-41: Large-Repository Scale Contract Holds For All-Families Scope

- `Support`: `scope=D all-families baseline` | `alg=A` | `vcs=shared` | `tier=Fast`
- `Status`: Scope expansion of stories 09–11 to all-families scope. Parity target: `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-D-41`.
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-D-41`

---

## VCS-Specific Stories

### USNG-ALGA-HISTORY-COMPLICATED-SCOPE-A-42: SVN Path-Copy Branching Must Not Distort Attribution Lineage

- `WHO`: repository analyst
- `WHEN`: the SVN repository uses path-based branching (copy-then-modify) inside the measurement window
- `WHAT`: track line attribution through path-copy branch origins correctly, not from the copy operation timestamp
- `WHY`: SVN branches through file-system `svn copy`, not references; a copy-then-modify pattern must not flatten attribution to the copy act itself
- `Story`: As a repository analyst using an SVN repository, I want path-copy branches to trace attribution back to the original lines on the trunk or source branch, so that the copy operation itself is never treated as the attribution origin.
- `Support`: `scope=A baseline` | `alg=A` | `vcs=svn-local; path-based branching` | `tier=Fast`
- `Status`: SVN-specific COMPLICATED behavior. This story has no Git equivalent. Parity target: `USNG-REPO-SVN-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-42`.
- `Anchors`: `TestdataNG-REPO-SVN-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-42`

**AC-01** — *Path-copy origin is tracked, not the copy commit*

- GIVEN an SVN branch is created by `svn copy trunk@R branches/feature` at revision R
- WHEN Algorithm A resolves `svn blame` for lines on `branches/feature` that were unchanged since the copy
- THEN those lines retain their original trunk attribution rather than receiving an attribution timestamp of revision R

**AC-02** — *Lines modified after path-copy carry the modification's attribution*

- GIVEN a line was copied from trunk via `svn copy` and then overwritten on the feature branch before `endTime`
- WHEN Algorithm A resolves `svn blame` for that line
- THEN it uses the post-copy modification's attribution

**AC-03** — *Merged path-copy branch does not collapse attribution to the merge revision*

- GIVEN a path-copy branch is merged back to trunk before `endTime`
- WHEN Algorithm A resolves `svn blame` for surviving merged lines
- THEN each line retains the attribution from its effective originating revision, not from the merge commit

**AC-04** — *Nested path-copy chains preserve deepest effective attribution*

- GIVEN a branch was itself created from another path-copy branch (nested copy)
- WHEN Algorithm A walks `svn blame` output
- THEN it follows the copy chain to the deepest effective modifying revision

---

## Remote Topology Stories

### USNG-ALGA-HISTORY-SIMPLE-SCOPE-A-30: Remote Git Identity Must Not Change The Measurement Contract

- `Support`: `scope=A baseline` | `alg=A` | `vcs=git remote-identity resolution` | `tier=Fast`
- `Status`: Remote Git identity is an addressing concern. All SHARED behavioral stories apply through delegation. Parity target: `USNG-REPO-GIT-REMOTE-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-A-30`.

**AC-01** — Remote identity does not change metric output contract.

**AC-02** — Unresolvable remote identity fails with explicit diagnostic.

### USNG-ALGA-HISTORY-SIMPLE-SCOPE-A-31: Remote SVN URL Must Not Change The Measurement Contract

- `Support`: `scope=A baseline` | `alg=A` | `vcs=svn remote URL resolution` | `tier=Fast`
- `Status`: Remote SVN URL is an access-path concern. Parity target: `USNG-REPO-SVN-REMOTE-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-A-31`.

**AC-01** — Remote SVN URL does not change metric output contract.

**AC-02** — Unresolvable SVN remote fails with explicit diagnostic.

### USNG-ALGA-HISTORY-SIMPLE-SCOPE-A-32: Provider-Side genCodeDesc Metadata Must Not Change The Measurement Contract

- `Support`: `scope=A baseline` | `alg=A` | `vcs=shared` | `tier=Fast`
- `Status`: Provider-side metadata is a metadata-topology concern. Parity target: `USNG-REPO-SHARED-GENCODEDESC-REMOTE-HISTORY-SIMPLE-SCOPE-A-32`.

**AC-01** — Remote genCodeDesc metadata produces contract-identical result.

**AC-02** — Provider fetch failure is explicit.

---

## Hardening And Operator Stories

### USNG-ALGA-HISTORY-SIMPLE-SCOPE-RUNTIME-28: Production Hardening — Scope Validation And File-Size Guard

- `Support`: `scope=input and runtime guard` | `alg=A` | `vcs=git-focused runtime checks` | `tier=Fast`
- `Status`: First-class hardening story. Parity target: `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-RUNTIME-28`.
- `Anchors`: `TestsNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-RUNTIME-28`

**AC-HARD-01** — Invalid `--scope` rejected at input with `EXIT_INPUT_ERROR`.

**AC-HARD-03** — Algorithm A oversized-blame guard raises `RepositoryStateError`.

**AC-HARD-04** — Invalid `--algorithm` value rejected at input.

**AC-HARD-05** — Invalid `startTime` or `endTime` format rejected at input.

### USNG-ALGA-HISTORY-COMPLICATED-SCOPE-RUNTIME-29: Info-Level Log Must Show Three-Phase Narrative

- `Support`: `scope=stderr behavior` | `alg=A` | `vcs=shared` | `tier=Fast target`
- `Status`: Documented story record. Current executable test coverage is an open gap. Parity target: `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-RUNTIME-29`.

**AC-OPS-01** — Start-state header on stderr containing `repo=`, `branch=`, `window=`, `endRevision=`.

**AC-OPS-02** — Per-line `TransitionHint` on ownership change.

**AC-OPS-03** — Final summary on stderr with `totalCodeLines=`, `elapsed=`, `costSeconds=`.

**AC-OPS-04** — Quiet mode suppresses transition and live-line lines.

**AC-OPS-05** — Debug mode shows all diagnostic tiers.

---

## Cross-Algorithm Parity

### USNG-ALGA-HISTORY-SIMPLE-SCOPE-ALL-27: Algorithm A And Algorithm B Must Produce Identical SUMMARY For Every Scope

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
