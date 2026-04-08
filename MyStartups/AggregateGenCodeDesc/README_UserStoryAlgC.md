# AggregateGenCodeDesc — Algorithm C User Stories

## Purpose

This document defines the user stories for **Algorithm C** (`AlgC`).

Algorithm C is an offline, repository-free attribution algorithm.
It achieves the same metric result as Algorithm A and Algorithm B using only
`genCodeDescProtoV26.04.json` files — no live repository access, no blame subprocess,
no diff replay.

The key enabler is the `blame` object embedded per line in `DETAIL` at write time by
the codeAgent. Because every surviving line carries `blame.revisionId`,
`blame.originalFilePath`, `blame.originalLine`, and `blame.timestamp`, the downstream
analyzer can apply the `startTime~endTime` filter and read `genRatio` directly from
the file without touching the VCS.

The embedded blame must be produced at write time directly from real `git blame`
or `svn blame` output.
Synthetic, inferred, replay-reconstructed, or hand-edited blame data is outside
the AlgC contract.
Both origins are explicitly supported. The `REPOSITORY.vcsType` field (`git` or `svn`)
and the `blame.revisionId` format (Git SHA vs SVN revision number such as `r12345`)
allow consumers to distinguish origin VCS without repository access.

## Protocol Precondition

All AlgC stories require `protocolVersion: "26.04"` and expect **exhaustive DETAIL**:
every surviving line in the file should appear in `codeLines` (or `docLines`), including
human-written lines as `genRatio=0 / genMethod=Manual`.
If a surviving line is omitted from DETAIL, Algorithm C imputes that line as
`genRatio=0 / genMethod=Manual` and emits a WARNING.
Exact parity and golden-result guarantees apply only when no such omission warning occurs.
A `genCodeDescProtoV26.03.json` input is not sufficient for AlgC.

## Relationship To Algorithm A and Algorithm B

| Property | Algorithm A | Algorithm B | Algorithm C |
|---|---|---|---|
| Repository access | live `git/svn blame` | offline diff replay | none |
| Input | repo + per-revision genCodeDesc v26.03 | commitDiffSet + per-revision genCodeDesc v26.03 | per-revision genCodeDesc **v26.04** only |
| Blame source | VCS subprocess | diff patch reconstruction | embedded `blame` object in DETAIL |
| DETAIL completeness required | no (AI lines only) | no (AI lines only) | expected for all surviving lines; omitted surviving lines fall back to Manual with WARNING |
| VCS support | git and svn | git and svn | git-origin and svn-origin blame |
| Metric semantics | identical | identical | identical |

## Story Rules

1. Every story follows the `WHO` / `WHEN` / `WHAT` / `WHY` / `Story` / `Support` / `Status` / `Anchors` format.
2. Acceptance criteria use plain `GIVEN / WHEN / THEN` blocks with story-local IDs.
3. Every story that claims parity with Algorithm A or Algorithm B must name the matching USNG story ID.
4. `tier=Heavy` stories must name a concrete scale floor in at least one acceptance criterion.

## Story ID Convention

```
USNG-ALGC-HISTORY-<C>-SCOPE-<D>-<NN>: Title
```

- `HISTORY-<C>`: `SIMPLE` | `COMPLICATED` | `COMPLEX`
  - `SIMPLE`: linear baselines, direct parity contracts, scope-only contracts
  - `COMPLICATED`: overwrites, deletions, renames, merge-aware flows
  - `COMPLEX`: large file sets, deep history, many-branch fan-in, production scale (≥10 000 commits, ≥100 branches)
- `SCOPE-<D>`: `A` | `B` | `C` | `D`
- No `REPO` dimension: Algorithm C has no live repository dependency.
- No `GENCODEDESC` dimension: always `genCodeDescProtoV26.04` local files.

---

## Universal Story Invariants

The following invariants apply to every AlgC story unless overridden explicitly.

- `UI-PROTOCOL`: the result must be a valid protocol-shaped output with `protocolName`,
  `protocolVersion`, `SUMMARY`, and `REPOSITORY` fields.
- `UI-GOLDEN`: when no omission warning is emitted, the result must match the approved golden output for the scenario.
- `UI-BLAME-MANDATORY`: every DETAIL entry must carry a `blame` object with
  `revisionId`, `originalFilePath`, `originalLine`, and `timestamp`.
  A missing or partial `blame` object is a protocol violation and must not produce a partial result.
- `UI-BLAME-REAL-VCS`: embedded `blame` must come from real `git blame` or `svn blame`
  output captured at write time. Synthetic, inferred, replay-reconstructed, or manually
  edited blame data is out of contract for AlgC.
- `UI-EXHAUSTIVE-DETAIL`: every surviving line in the file should be listed in DETAIL.
  If a surviving line is omitted and `protocolVersion` is confirmed as `"26.04"`,
  Algorithm C imputes `genRatio=0 / genMethod=Manual` for that line and emits a WARNING.
- `UI-PARITY`: for the same repository scenario, and when no omission warning is emitted,
  Algorithm C must produce the same `SUMMARY` counts as Algorithm A and Algorithm B.
- `UI-VCS-AGNOSTIC-CONSUMPTION`: Algorithm C never calls any VCS tool at runtime.
  VCS origin (git or svn) is carried by `REPOSITORY.vcsType` and `blame.revisionId` format only.
- `UI-ALG-C-BOUNDARY`: Any AlgC evidence attached to a `HISTORY-COMPLICATED` or
  `HISTORY-COMPLEX` story covers the approved scenario of that story only. It is not
  blanket support across all complicated or complex history shapes.

---

## HISTORY-SIMPLE Stories

### USNG-ALGC-HISTORY-SIMPLE-SCOPE-A-01: Calculate Weighted AI Ratio For Live Changed Source Code Using Only genCodeDesc

- `WHO`: repository analyst
- `WHEN`: querying a time window `startTime~endTime` and holding only `genCodeDescProtoV26.04` files — no repository checkout available
- `WHAT`: calculate the weighted AI ratio for source-code lines whose `blame.timestamp` falls inside the requested window
- `WHY`: reproduce the same live-changed metric as Algorithm A without requiring repository access
- `Story`: As a repository analyst, I want to calculate the weighted AI ratio for live source-code lines using only `genCodeDescProtoV26.04` files, so that I can reproduce the Algorithm A result without a live repository.
- `Support`: `scope=A baseline` | `alg=C` | `vcs=git-origin and svn-origin` | `tier=Fast`
- `Status`: Planned. No implementation exists yet. Protocol shape is defined in `genCodeDescProtoV26.04.json`. Parity target: `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-01`.
- `Anchors`: `TestdataNG-ALGC-HISTORY-SIMPLE-SCOPE-A-01-GIT`, `TestdataNG-ALGC-HISTORY-SIMPLE-SCOPE-A-01-SVN`

**AC-01** — *Core offline measurement contract*

- GIVEN a `genCodeDescProtoV26.04` file for the `endRevision` with exhaustive DETAIL
- WHEN the analyzer filters DETAIL entries whose `blame.timestamp` falls in `[startTime, endTime]`
- THEN the result `SUMMARY` counts only those in-scope lines and their `genRatio` values

**AC-02** — *Manual lines counted in total but not in AI numerator*

- GIVEN DETAIL entries with `genRatio=0` and `genMethod=Manual` whose `blame.timestamp` is in scope
- WHEN the analyzer aggregates in-scope lines
- THEN those lines increment `totalCodeLines` but not `fullGeneratedCodeLines` or `partialGeneratedCodeLines`

**AC-03** — *Lines outside the time window are excluded from both numerator and denominator*

- GIVEN DETAIL entries whose `blame.timestamp` is outside `[startTime, endTime]`
- WHEN the analyzer aggregates the final result
- THEN those lines do not appear in `totalCodeLines`, `fullGeneratedCodeLines`, or `partialGeneratedCodeLines`

**AC-GIT-01** — *Git-origin blame parity*

- GIVEN a `genCodeDescProtoV26.04` file whose `REPOSITORY.vcsType` is `git` and whose `blame.revisionId` values are Git SHAs
- WHEN Algorithm C is executed
- THEN `SUMMARY` matches the Algorithm A Git golden result for the equivalent scenario

**AC-SVN-01** — *SVN-origin blame parity*

- GIVEN a `genCodeDescProtoV26.04` file whose `REPOSITORY.vcsType` is `svn` and whose `blame.revisionId` values are SVN revision numbers (e.g. `r12345`)
- WHEN Algorithm C is executed
- THEN `SUMMARY` matches the Algorithm A SVN golden result for the equivalent scenario

---

### USNG-ALGC-HISTORY-SIMPLE-SCOPE-A-08: Git-Origin And SVN-Origin Must Follow The Same Result Contract

- `WHO`: repository analyst
- `WHEN`: verifying that Algorithm C produces the same result semantics regardless of whether the embedded blame originates from a Git or SVN repository
- `WHAT`: confirm that `REPOSITORY.vcsType` does not change result semantics; only `blame.timestamp` and `genRatio` drive the metric
- `WHY`: Algorithm C must be VCS-agnostic at consumption time; origin VCS is metadata only
- `Story`: As a repository analyst, I want Algorithm C to produce the same result semantics for Git-origin and SVN-origin blame data, so that VCS type does not affect the attribution contract.
- `Support`: `scope=A baseline` | `alg=C` | `vcs=git-origin and svn-origin` | `tier=Fast`
- `Status`: Planned. Parity target: `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-08`.
- `Anchors`: `TestdataNG-ALGC-HISTORY-SIMPLE-SCOPE-A-08-GIT`, `TestdataNG-ALGC-HISTORY-SIMPLE-SCOPE-A-08-SVN`

**AC-01** — *Same scenario, same result across VCS origins*

- GIVEN two `genCodeDescProtoV26.04` files describing the same logical scenario — one with `vcsType=git` blame and one with `vcsType=svn` blame
- WHEN Algorithm C is executed against each
- THEN both produce the same `SUMMARY` counts

**AC-02** — *No VCS tool is invoked regardless of vcsType*

- GIVEN `REPOSITORY.vcsType` is either `git` or `svn`
- WHEN Algorithm C processes the file
- THEN it reads only the embedded `blame` fields and does not call any git or svn subprocess

---

## HISTORY-COMPLICATED Stories

### USNG-ALGC-HISTORY-COMPLICATED-SCOPE-A-02: Human Rewrite Removes Prior AI Attribution

- `WHO`: repository analyst
- `WHEN`: a human revision overwrites code previously attributed to AI before `endTime`
- `WHAT`: the embedded `blame` for that line reflects the later human revision; attribution resets to Manual
- `WHY`: prevent old AI ownership from staying attached to overwritten code
- `Story`: As a repository analyst, I want a human rewrite of a previously AI-generated line to reset attribution to Manual via the embedded `blame.timestamp`, so that old AI ownership does not persist in the Algorithm C result.
- `Support`: `scope=A baseline` | `alg=C` | `vcs=git-origin and svn-origin` | `tier=Fast`
- `Status`: Planned. Parity target: `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-02`.
- `Anchors`: `TestdataNG-ALGC-HISTORY-COMPLICATED-SCOPE-A-02`

**AC-01** — *Human rewrite clears prior AI attribution via blame*

- GIVEN a line whose `blame.revisionId` points to a human commit (`genRatio=0 / genMethod=Manual`) inside `[startTime, endTime]`
- WHEN the analyzer processes that DETAIL entry
- THEN the line is counted as `totalCodeLines` only, not in any AI counter

**AC-GIT-01** — *Git-origin human-rewrite parity*

- GIVEN the same scenario as `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-02` with Git blame origin
- WHEN Algorithm C is executed
- THEN `SUMMARY` matches the Algorithm A Git golden result

**AC-SVN-01** — *SVN-origin human-rewrite parity*

- GIVEN the same scenario with SVN blame origin
- WHEN Algorithm C is executed
- THEN `SUMMARY` matches the Algorithm A SVN golden result

---

### USNG-ALGC-HISTORY-COMPLICATED-SCOPE-A-03: AI Rewrite Replaces Prior Human Ownership

- `WHO`: repository analyst
- `WHEN`: a later AI revision overwrites a line previously human-authored
- `WHAT`: the embedded `blame` for that line reflects the AI revision; AI attribution applies
- `WHY`: ensure the live snapshot at `endTime` reflects the latest AI contribution
- `Story`: As a repository analyst, I want a later AI rewrite of a human line to become the effective attribution source via the embedded `blame`, so that Algorithm C reflects the latest AI contribution without repository access.
- `Support`: `scope=A baseline` | `alg=C` | `vcs=git-origin and svn-origin` | `tier=Fast`
- `Status`: Planned. Parity target: `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-03`.
- `Anchors`: `TestdataNG-ALGC-HISTORY-COMPLICATED-SCOPE-A-03`

**AC-01** — *Later AI revision becomes effective attribution via blame*

- GIVEN a line whose `blame.revisionId` points to an AI commit (`genRatio > 0`) inside `[startTime, endTime]`
- WHEN the analyzer processes that DETAIL entry
- THEN the line is counted in both `totalCodeLines` and the appropriate AI counter

**AC-GIT-01** — *Git-origin AI-rewrite parity*

- GIVEN the same scenario as `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-03` with Git blame origin
- WHEN Algorithm C is executed
- THEN `SUMMARY` matches the Algorithm A Git golden result

**AC-SVN-01** — *SVN-origin AI-rewrite parity*

- GIVEN the same scenario with SVN blame origin
- WHEN Algorithm C is executed
- THEN `SUMMARY` matches the Algorithm A SVN golden result

---

### USNG-ALGC-HISTORY-COMPLICATED-SCOPE-A-04: Deleted Lines Must Not Count

- `WHO`: repository analyst
- `WHEN`: lines existed earlier in the window but are absent from the DETAIL of the `endRevision` genCodeDesc
- `WHAT`: those lines do not appear in the result
- `WHY`: deleted lines are simply absent from exhaustive DETAIL; no repository access is needed to confirm deletion
- `Story`: As a repository analyst, I want deleted lines to be invisible to Algorithm C by their absence from exhaustive DETAIL, so that the result reflects only the surviving live snapshot.
- `Support`: `scope=A baseline` | `alg=C` | `vcs=git-origin and svn-origin` | `tier=Fast`
- `Status`: Planned. Parity target: `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-04`.
- `Anchors`: `TestdataNG-ALGC-HISTORY-COMPLICATED-SCOPE-A-04`

**AC-01** — *Deleted lines are absent from exhaustive DETAIL and therefore excluded*

- GIVEN a `genCodeDescProtoV26.04` file whose exhaustive DETAIL covers only surviving lines at `endRevision`
- WHEN the analyzer processes DETAIL
- THEN no deleted-line entry exists to be counted; deletion is implicit by absence

**AC-GIT-01** — *Git-origin deletion parity*

- GIVEN the same scenario as `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-04` with Git blame origin
- WHEN Algorithm C is executed
- THEN `SUMMARY` matches the Algorithm A Git golden result

**AC-SVN-01** — *SVN-origin deletion parity*

- GIVEN the same scenario with SVN blame origin
- WHEN Algorithm C is executed
- THEN `SUMMARY` matches the Algorithm A SVN golden result

---

### USNG-ALGC-HISTORY-COMPLICATED-SCOPE-A-05: Rename Or Move Is Transparent Via originalFilePath

- `WHO`: repository analyst
- `WHEN`: a file was renamed or moved between its origin revision and `endRevision`
- `WHAT`: `blame.originalFilePath` correctly names the file at the origin revision; rename is resolved without repository access
- `WHY`: rename transparency is required for correct line attribution and must not require a VCS subprocess in Algorithm C
- `Story`: As a repository analyst, I want renamed or moved files to be attributed correctly via `blame.originalFilePath`, so that Algorithm C handles rename history without repository access.
- `Support`: `scope=A baseline` | `alg=C` | `vcs=git-origin and svn-origin` | `tier=Fast`
- `Status`: Planned. Parity target: `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-05`.
- `Anchors`: `TestdataNG-ALGC-HISTORY-COMPLICATED-SCOPE-A-05`

**AC-01** — *originalFilePath differs from fileName for renamed files*

- GIVEN a DETAIL entry where `blame.originalFilePath` differs from the parent `fileName`
- WHEN the analyzer reads the blame attribution
- THEN it uses `blame.originalFilePath` and `blame.originalLine` as the canonical origin key, matching the Algorithm A blame contract

**AC-02** — *Renamed-file lines are attributed correctly*

- GIVEN a line in a renamed file whose `blame.timestamp` falls in `[startTime, endTime]`
- WHEN Algorithm C aggregates in-scope lines
- THEN the line is counted with its `genRatio` regardless of the rename

**AC-GIT-01** — *Git-origin rename parity*

- GIVEN the same rename scenario as `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-05` with Git blame origin
- WHEN Algorithm C is executed
- THEN `SUMMARY` matches the Algorithm A Git golden result

**AC-SVN-01** — *SVN-origin rename parity*

- GIVEN the same scenario with SVN blame origin (SVN path-copy semantics)
- WHEN Algorithm C is executed
- THEN `SUMMARY` matches the Algorithm A SVN golden result

---

### USNG-ALGC-HISTORY-COMPLICATED-SCOPE-A-07: Merge Commit Must Preserve Effective Attribution

- `WHO`: repository analyst
- `WHEN`: merged branches bring human and AI contributions into the target branch before `endTime`
- `WHAT`: each surviving line retains the attribution from its effective origin revision as embedded in `blame`, regardless of merge shape
- `WHY`: merge commits must not reset or flatten per-line provenance in the Algorithm C result
- `Story`: As a repository analyst, I want merged branches to preserve per-line effective attribution via embedded `blame`, so that Algorithm C does not flatten ownership to merge commits or branch labels.
- `Support`: `scope=A baseline` | `alg=C` | `vcs=git-origin and svn-origin` | `tier=Fast`
- `Status`: Planned. Parity target: `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-07`.
- `Anchors`: `TestdataNG-ALGC-HISTORY-COMPLICATED-SCOPE-A-07`

**AC-01** — *Merge does not override embedded blame*

- GIVEN surviving lines originate from different merged branches and each carries an accurate `blame` in DETAIL
- WHEN Algorithm C processes the file
- THEN it respects each line's embedded `blame.revisionId` and `blame.timestamp` without collapsing to merge commit identity

**AC-02** — *Per-line independence across merged branches*

- GIVEN multiple branches are merged before `endTime` and surviving lines originate from different merged branches
- WHEN Algorithm C aggregates in-scope lines
- THEN it preserves each surviving line independently

---

## HISTORY-COMPLEX Stories

### USNG-ALGC-HISTORY-COMPLEX-SCOPE-A-09: Large File Set Must Preserve Result Semantics

- `WHO`: repository analyst
- `WHEN`: the `endRevision` genCodeDesc covers a large repository with many files and many surviving lines
- `WHAT`: Algorithm C correctly processes all DETAIL entries at scale and produces the correct SUMMARY
- `WHY`: production repositories have large file sets; correctness must hold at scale
- `Story`: As a repository analyst, I want Algorithm C to remain correct across a large file set so that result semantics are preserved at production scale.
- `Support`: `scope=A baseline` | `alg=C` | `vcs=git-origin and svn-origin` | `tier=Fast`
- `Status`: Planned. Parity target: `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-09`.
- `Anchors`: `TestdataNG-ALGC-HISTORY-COMPLEX-SCOPE-A-09`

**AC-01** — *Large file set produces one correct result*

- GIVEN a `genCodeDescProtoV26.04` file with exhaustive DETAIL covering hundreds of files and thousands of surviving lines
- WHEN Algorithm C computes the final result
- THEN it produces exactly one repository-level SUMMARY and the counts match the golden result

**AC-02** — *Result semantics are independent of file count*

- GIVEN the same scenario at small scale and at large scale
- WHEN Algorithm C is executed in both cases
- THEN the per-line attribution logic is identical regardless of file count

---

### USNG-ALGC-HISTORY-COMPLEX-SCOPE-A-10: Deep History Must Preserve Latest Effective Attribution

- `WHO`: repository analyst
- `WHEN`: surviving lines originate from revisions spread across a long commit history (thousands of commits deep)
- `WHAT`: Algorithm C respects each line's `blame.timestamp` regardless of how old or recent the origin revision is
- `WHY`: deep history must not distort per-line attribution; embedded blame covers all depths equally
- `Story`: As a repository analyst, I want deep commit history to be transparent to Algorithm C via embedded blame, so that lines from old revisions and recent revisions are attributed equally correctly.
- `Support`: `scope=A baseline` | `alg=C` | `vcs=git-origin and svn-origin` | `tier=Fast`
- `Status`: Planned. Parity target: `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-10`.
- `Anchors`: `TestdataNG-ALGC-HISTORY-COMPLEX-SCOPE-A-10`

**AC-01** — *Old-origin lines attributed correctly*

- GIVEN a surviving line whose `blame.timestamp` predates `startTime`
- WHEN Algorithm C filters by time window
- THEN the line is excluded from the result (not in scope)

**AC-02** — *Recent-origin lines attributed correctly*

- GIVEN a surviving line whose `blame.timestamp` falls inside `[startTime, endTime]`
- WHEN Algorithm C filters by time window
- THEN the line is included with its `genRatio` regardless of how many commits exist between the origin and `endRevision`

---

### USNG-ALGC-HISTORY-COMPLEX-SCOPE-A-11: Many Merged Branches Must Preserve Per-Line Attribution

- `WHO`: repository analyst
- `WHEN`: many branches are merged into the target branch inside one requested window and the final genCodeDesc covers all surviving lines with their individual blame origins
- `WHAT`: Algorithm C preserves per-line attribution regardless of how many merged branches contributed surviving lines
- `WHY`: branch-heavy repositories must not distort attribution when Algorithm C is used
- `Story`: As a repository analyst, I want branch-heavy history to be transparent to Algorithm C via embedded blame, so that integrating many feature branches does not distort the final result.
- `Support`: `scope=A baseline` | `alg=C` | `vcs=git-origin and svn-origin` | `tier=Fast`
- `Status`: Planned. Parity target: `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-11`.
- `Anchors`: `TestdataNG-ALGC-HISTORY-COMPLEX-SCOPE-A-11`

**AC-01** — *Per-line independence across many merged branches*

- GIVEN surviving lines originate from many different merged branches each with its own `blame.revisionId` and `blame.timestamp`
- WHEN Algorithm C processes the exhaustive DETAIL
- THEN it attributes each line independently and does not flatten ownership to merge order or branch label

---

## Heavy Production Gates

These stories are production-scale correctness gates. They verify that result semantics
are preserved under realistic heavy workloads using genCodeDesc files generated from
repositories at production scale.

### USNG-ALGC-HISTORY-COMPLEX-SCOPE-A-12: Git Production-Scale genCodeDesc Must Stay Correct Under Branch-Heavy History

- `WHO`: repository analyst
- `WHEN`: validating production-readiness of Algorithm C against a `genCodeDescProtoV26.04` file generated from a large branch-heavy Git repository
- `WHAT`: keep Algorithm C correct and performant when processing exhaustive DETAIL derived from a production-scale Git repository
- `WHY`: prove that Algorithm C handles files derived from repositories with ≥10 000 commits and ≥100 branches without correctness or performance degradation
- `Story`: As a repository analyst, I want Algorithm C to remain correct and performant when processing genCodeDesc files derived from production-scale Git repositories with ≥10 000 commits and ≥100 branches, so that it is production-ready for real-world Git histories.
- `Support`: `scope=A baseline` | `alg=C` | `vcs=git-origin` | `tier=Heavy`
- `Status`: Planned. No implementation. Corresponds to AlgA gate `USNG-REPO-GIT-LOCAL-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-12`.
- `Anchors`: `TestsNG-ALGC-HISTORY-COMPLEX-SCOPE-A-12-GIT`

**AC-GIT-01** — *Scale floor: ≥10 000 commits, ≥100 branches*

- GIVEN a `genCodeDescProtoV26.04` file with exhaustive DETAIL derived from a Git repository with ≥10 000 commits, ≥100 branches, and repeated feature-to-integration-to-release merge fan-in
- WHEN Algorithm C computes the final result
- THEN it produces exactly one repository-level SUMMARY and the counts match the golden result

**AC-GIT-02** — *Effective origin preserved across deep Git history*

- GIVEN surviving lines reach the release branch through mixed direct merges, integration branches, and staged convergence, with each carrying an accurate `blame` in DETAIL
- WHEN Algorithm C resolves attribution
- THEN it is based on each line's embedded `blame.revisionId` and `blame.timestamp`, not merge shape or branch naming

**AC-GIT-03** — *Correctness and scalability both verified*

- GIVEN the heavy Git production-scale scenario completes successfully
- WHEN the acceptance outcome is evaluated
- THEN it verifies both correctness of the final aggregate result and that processing time scales acceptably relative to total DETAIL line count

**AC-GIT-04** — *Parity with Algorithm A Git production gate*

- GIVEN the same scenario used for `USNG-REPO-GIT-LOCAL-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-12`
- WHEN Algorithm C is executed against the equivalent `genCodeDescProtoV26.04` file
- THEN `SUMMARY` matches the Algorithm A golden result

---

### USNG-ALGC-HISTORY-COMPLEX-SCOPE-A-13: SVN Production-Scale genCodeDesc Must Stay Correct Under Branch And Merge Pressure

- `WHO`: repository analyst
- `WHEN`: validating production-readiness of Algorithm C against a `genCodeDescProtoV26.04` file generated from a large SVN repository under branch and merge pressure
- `WHAT`: keep Algorithm C correct and performant when processing exhaustive DETAIL derived from a production-scale SVN repository
- `WHY`: prove that Algorithm C handles files derived from repositories with ≥10 000 SVN revisions and ≥100 branch copies without correctness or performance degradation
- `Story`: As a repository analyst, I want Algorithm C to remain correct and performant when processing genCodeDesc files derived from production-scale SVN repositories with ≥10 000 revisions and ≥100 branch copies, so that it is production-ready for real-world SVN histories.
- `Support`: `scope=A baseline` | `alg=C` | `vcs=svn-origin` | `tier=Heavy`
- `Status`: Planned. No implementation. Corresponds to AlgA gate `USNG-REPO-SVN-LOCAL-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-13`.
- `Anchors`: `TestsNG-ALGC-HISTORY-COMPLEX-SCOPE-A-13-SVN`

**AC-SVN-01** — *Scale floor: ≥10 000 revisions, ≥100 branch copies*

- GIVEN a `genCodeDescProtoV26.04` file with exhaustive DETAIL derived from an SVN repository with ≥10 000 revisions, ≥100 branch copies, and repeated branch-to-release merge or reintegration activity
- WHEN Algorithm C computes the final result
- THEN it produces exactly one repository-level SUMMARY and the counts match the golden result

**AC-SVN-02** — *Effective origin preserved across deep SVN history*

- GIVEN surviving lines reach the release path through mixed direct work, branch copies, and merge or reintegration history, with each carrying an accurate `blame` in DETAIL
- WHEN Algorithm C resolves attribution
- THEN it is based on each line's embedded `blame.revisionId` (SVN revision number) and `blame.timestamp`, not merge timing or branch path alone

**AC-SVN-03** — *Correctness and scalability both verified*

- GIVEN the heavy SVN production-scale scenario completes successfully
- WHEN the acceptance outcome is evaluated
- THEN it verifies both correctness of the final aggregate result and that processing time scales acceptably relative to total DETAIL line count

**AC-SVN-04** — *Parity with Algorithm A SVN production gate*

- GIVEN the same scenario used for `USNG-REPO-SVN-LOCAL-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-13`
- WHEN Algorithm C is executed against the equivalent `genCodeDescProtoV26.04` file
- THEN `SUMMARY` matches the Algorithm A golden result

---

## Cross-Algorithm Parity Gate

### USNG-ALGC-HISTORY-SIMPLE-SCOPE-A-06: Algorithm C Parity Gate Against Algorithm A And Algorithm B

- `WHO`: quality engineer
- `WHEN`: validating that Algorithm C produces the same aggregate result as Algorithm A and Algorithm B for every shared story scenario
- `WHAT`: a cross-algorithm parity assertion that Algorithm C `SUMMARY` matches Algorithm A and Algorithm B `SUMMARY` for the same inputs
- `WHY`: guarantee that the three algorithms are semantically equivalent; detect any divergence introduced by the offline blame-embedding approach
- `Story`: As a quality engineer, I want a parity gate that asserts Algorithm C produces the same `SUMMARY` as Algorithm A and Algorithm B for every shared story scenario, so that the three algorithms remain semantically equivalent.
- `Support`: `scope=A baseline` | `alg=A and B and C` | `vcs=git-origin and svn-origin` | `tier=Fast`
- `Status`: Planned. Depends on ALGC-01 through ALGC-05 and ALGC-07 through ALGC-11 being green.
- `Anchors`: `TestsNG-ALGC-PARITY-GATE`

**AC-01** — *Algorithm C matches Algorithm A for all shared simple-history scenarios*

- GIVEN a shared scenario where Algorithm A produces a known golden `SUMMARY`
- WHEN Algorithm C is executed against the equivalent `genCodeDescProtoV26.04` files
- THEN the `SUMMARY` is identical to the Algorithm A golden result

**AC-02** — *Algorithm C matches Algorithm B for all shared simple-history scenarios*

- GIVEN a shared scenario where Algorithm B produces a known golden `SUMMARY`
- WHEN Algorithm C is executed against the equivalent `genCodeDescProtoV26.04` files
- THEN the `SUMMARY` is identical to the Algorithm B golden result

**AC-03** — *Protocol version mismatch is a hard error*

- GIVEN an input file with `protocolVersion` other than `"26.04"`
- WHEN Algorithm C attempts to process it
- THEN the analyzer raises a protocol version error and does not produce a partial result

**AC-04** — *Omitted surviving lines fall back to Manual with warning*

- GIVEN a `protocolVersion="26.04"` input where a surviving line is omitted from DETAIL
- WHEN Algorithm C processes the file
- THEN it imputes `genRatio=0 / genMethod=Manual` for that line, emits a WARNING, and the result is not eligible for exact parity or golden-result assertions
