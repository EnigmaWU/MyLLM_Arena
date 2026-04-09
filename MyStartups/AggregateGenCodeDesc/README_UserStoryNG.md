# AggregateGenCodeDesc USNG (UserStoryNG)

## Purpose

This document defines the authoritative next-generation user stories and acceptance criteria for AggregateGenCodeDesc.

It works with the current base documents:

- `README.md` remains the product and contract base.
- `README_UserGuide.md` remains the operator and runtime base.

Within this repository, `UserStoryNG` may be abbreviated as `USNG`.

## USNG Story Rules

1. Make every story explicit with `WHO`, `WHEN`, `WHAT`, and `WHY` fields plus a classic `As a … I want … so that …` story sentence.
2. Keep acceptance criteria in classic `GIVEN … WHEN … THEN …` form.
3. Keep current support boundaries explicit — never hide partial support.
4. Keep scenario anchors visible using logical `TestdataNG-*`, `TestsNG-*`, and `OperatorScenarioNG-*` anchors rather than concrete file paths.

## NG Verification Anchor Policy

USNG must not be normatively coupled to concrete filesystem paths or golden filenames.

- `TestdataNG-*`: logical next-generation fixture or scenario-data anchors
- `TestsNG-*`: logical next-generation executable verification anchors
- `OperatorScenarioNG-*`: logical next-generation operator-observation anchors

These are logical story-layer anchors, not required directory names. The future `TestsNG` and `TestdataNG` assets may choose their own concrete filesystem layout as long as they realize the same story contract.

The repository uses a canonical layout for those future assets so story anchors can map to stable concrete paths.

## NG Verification Asset Layout

Canonical NG verification roots are:

- `TestdataNG/`: scenario fixtures and approved golden outputs
- `TestsNG/`: executable verification modules
- `OperatorScenarioNG/`: operator-facing narrative or log-observation scenarios

USNG story cards continue to use logical anchors as the normative contract surface. When a concrete repository path is needed, resolve it through the corresponding root README:

- `TestdataNG/README.md`
- `TestsNG/README.md`
- `OperatorScenarioNG/README.md`

Logical NG asset anchors now follow this shape:

- `<AssetType>-REPO-<repo-topology>-GENCODEDESC-<metadata-topology>-HISTORY-<complexity>-SCOPE-<scope>-<NN>[-<VARIANT>]`
- the 4D core must match the owning USNG story
- `[-<VARIANT>]` is optional and is used only when one story needs more than one approved fixture, executable, or operator-observation shape

## UserGuide-First Structure

USNG uses a 4D story index as the primary naming rule.

The primary reading order is:

1. repository topology
2. `genCodeDesc` topology
3. repository history complexity
4. scope

`Algorithm A/B` is carried by the `Support` and `Status` fields and by the acceptance clauses, not by the story ID itself.

### Dim A: Repository Topology

- `REPO-GIT-LOCAL`: analyze a local Git checkout directly
- `REPO-GIT-REMOTE`: enter through a logical or remote-style Git identity while execution still resolves through the supported runtime path
- `REPO-SVN-LOCAL`: analyze a local SVN repository or `file:///` URL directly
- `REPO-SVN-REMOTE`: analyze a remote-style SVN URL through SVN history access
- `REPO-SHARED`: one card intentionally spans more than one repository topology

### Dim B: genCodeDesc Topology

- `GENCODEDESC-LOCAL`: metadata is supplied from a local directory such as `--genCodeDescSetDir`
- `GENCODEDESC-REMOTE`: metadata is conceptually fetched from an external provider or service
- `GENCODEDESC-SHARED`: one card is intentionally valid for both local and provider-side metadata paths

### Dim C: History Complexity

- `HISTORY-SIMPLE`: linear single-branch baselines, direct parity baselines, or scope-only contracts
- `HISTORY-COMPLICATED`: overwrites, deletions, renames, mixed commit chains, or limited merge-aware flows
- `HISTORY-COMPLEX`: large repositories, deep history, many-branch fan-in, or production-scale release convergence

### Dim D: Scope

- `SCOPE-A`, `SCOPE-B`, `SCOPE-C`, `SCOPE-D`: the four measurement scopes
- `SCOPE-ALL`: cross-scope cards
- `SCOPE-RUNTIME`: operator or guardrail cards that are not owned by one measurement scope

### 4D USNG ID Grammar

Every normative story ID now follows this shape:

`USNG-REPO-<repo-topology>-GENCODEDESC-<metadata-topology>-HISTORY-<complexity>-SCOPE-<scope>-<NN>`

Where:

- `<NN>` is a stable story sequence, not a family code
- `Algorithm A/B` is intentionally not encoded in the ID
- logical scenario anchors (`TestdataNG-*`, `TestsNG-*`, `OperatorScenarioNG-*`) are a separate layer; they reuse the owning story's 4D core and add only optional variant suffixes such as `-GIT`, `-SVN`, `-SVN-PARITY`, or `-AI-TO-HUMAN-SHAPE`

## UserGuide Runtime Story Map

This section is the primary navigation map.

### Git Local Repository + genCodeDesc Local

- `HISTORY-SIMPLE / SCOPE A`: local baseline measurement cards and the single-branch period-added baseline
- `HISTORY-SIMPLE / SCOPE B/C/D`: scope-expansion, Algorithm B scope-support cards, and period-added SCOPE-B/C/D cards
- `HISTORY-COMPLICATED / SCOPE A`: overwrite, deletion, rename, mixed-window, and merge-aware cards
- `HISTORY-COMPLEX / SCOPE A`: large-repository, deep-history, many-branch, and production-scale Git cards
- `SCOPE-RUNTIME`: the Git-local runtime hardening card

### Git Local Repository + genCodeDesc Shared

- shared metadata-topology contracts for the baseline live-snapshot story, the baseline period-added contract, and the Git production-scale gate

### Git Remote-Identity Repository + genCodeDesc Local

- `USNG-30` defines the contract boundary: remote Git identity is an addressing concern that must not change metric semantics
- story 30 is the explicit normative card for this topology

### SVN Local Repository + genCodeDesc Local

- `HISTORY-SIMPLE / SCOPE A`: shared baseline and parity cards plus the defended Algorithm B SVN subset
- `HISTORY-COMPLEX / SCOPE A`: the production-scale SVN gate
- `SCOPE B/C/D`: use only the cards that explicitly declare shared or SVN-valid support

### SVN Remote Repository + genCodeDesc Local

- `USNG-31` defines the contract boundary: remote SVN URL is an access-path concern that must not change metric semantics
- story 31 is the explicit normative card for this topology

### Any Repository Topology + genCodeDesc Remote

- `USNG-32` defines the contract boundary: provider-side metadata must not change metric semantics
- story 32 is the explicit normative card for this metadata topology

## How To Read This File

Every story card uses this shape:

- **Story ID** — 4D identifier: `USNG-REPO-<A>-GENCODEDESC-<B>-HISTORY-<C>-SCOPE-<D>-<NN>: Title`
- `WHO` — the user or operator role
- `WHEN` — the trigger or business moment
- `WHAT` — what that role wants from the analyzer
- `WHY` — why the outcome matters
- `Story` — classic `As a … I want … so that …` sentence
- `Support` — inline pipe-separated: `scope=…` | `alg=…` | `vcs=…` | `tier=…`
- `Status` — current support status, explicit about gaps
- `Anchors` — logical `TestdataNG-*`, `TestsNG-*`, or `OperatorScenarioNG-*` verification anchors

Acceptance criteria use story-local IDs (`AC-01`, `AC-ALG-A-01`, `AC-ALG-B-01`) with plain `GIVEN / WHEN / THEN` blocks and a short descriptive label.

Navigation:

- Use the `UserGuide Runtime Story Map` to locate the right bucket by runtime topology.
- Confirm the 4D prefix of the story ID to identify repository topology, metadata topology, history complexity, and scope.
- Resolve `Anchors` to concrete paths through the corresponding NG asset README.
- Traceability lookups are in the appendix only.

## Navigation

### 4D View

- Repository topology: `REPO-GIT-LOCAL`, `REPO-GIT-REMOTE`, `REPO-SVN-LOCAL`, `REPO-SVN-REMOTE`, `REPO-SHARED`
- Metadata topology: `GENCODEDESC-LOCAL`, `GENCODEDESC-REMOTE`, `GENCODEDESC-SHARED`
- History complexity: `HISTORY-SIMPLE`, `HISTORY-COMPLICATED`, `HISTORY-COMPLEX`
- Scope: `SCOPE-A`, `SCOPE-B`, `SCOPE-C`, `SCOPE-D`, `SCOPE-ALL`, `SCOPE-RUNTIME`
- Algorithm: carried in `Support` and `Status` fields; not encoded in the story ID

### Coverage Policy

**SHARED topology stories cover all topology combinations.** A story with `REPO-SHARED-GENCODEDESC-SHARED` in its ID establishes a behavioral contract that applies regardless of whether the actual execution uses Git, SVN, local, or remote access. Remote topology stories (30–32) and specific-VCS stories (e.g., 12, 13, 42) add contracts that are unique to those topologies; they do not replace SHARED stories.

### Coverage Summary (42 stories)

| Dim-C × Dim-D | SCOPE-A | SCOPE-B | SCOPE-C | SCOPE-D |
|---|---|---|---|---|
| **SIMPLE** | 01 (SHARED) | 14 (SHARED), 18 (GIT-LOCAL), 33 (GIT-LOCAL) | 15 (SHARED), 19 (GIT-LOCAL), 34 | 16 (SHARED), 20 (GIT-LOCAL), 35 |
| **COMPLICATED** | 02–07 (SHARED), 23–25 (GIT-LOCAL period-added), 42 (SVN-LOCAL) | 36 (SHARED) | 37 (SHARED) | 38 (SHARED) |
| **COMPLEX** | 09–11 (SHARED), 12 (GIT-LOCAL gate), 13 (SVN-LOCAL gate) | 39 (SHARED) | 40 (SHARED) | 41 (SHARED) |

Remote topologies (GIT-REMOTE: story 30, SVN-REMOTE: story 31, GENCODEDESC-REMOTE: story 32) delegate all SHARED behavioral contracts and add access-path boundary contracts only.

Additional stories covering SCOPE-ALL (17, 27), SCOPE-RUNTIME (28, 29), and period-added SCOPE-A contracts (21, 22, 26) are not shown in the matrix above.

## Detailed Story Cards

### Universal Story Invariants

All story cards below share these standing requirements unless a specific card explicitly overrides one.

**UI-PROTOCOL** — A successful result is always protocol-shaped: repository identity in `REPOSITORY`, aggregate values in `SUMMARY`.

**UI-GOLDEN** — Any implementation path claiming support for a story must produce output matching the approved golden output for the approved scenario of that story.

**UI-ALG-B-BOUNDARY** — Any `Algorithm B` evidence attached to a `HISTORY-COMPLICATED` or `HISTORY-COMPLEX` story covers the approved scenario of that story only. It is not blanket support across all complicated or complex history shapes.

Story cards that need exceptions state the override explicitly by naming the invariant they are overriding.

---

## Live-Snapshot Contract Stories

These stories define the primary live-snapshot metric: the weighted AI ratio among live source-code lines whose current version changed inside the requested window.

### USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-01: Calculate Weighted AI Ratio For Live Changed Source Code In A Requested Time Window

- `WHO`: repository analyst
- `WHEN`: querying one repository branch for a window `startTime~endTime`, needing the live-snapshot answer at `endTime`
- `WHAT`: calculate the weighted AI ratio for live source-code lines whose current version changed inside the requested window
- `WHY`: know how much of the current live changed source code is attributable to AI
- `Story`: As a repository analyst, I want to calculate the weighted AI ratio for live source-code lines whose current version falls in a requested period `startTime~endTime`, so that I can know how much of the current live changed source code is attributable to AI.
- `Support`: `scope=A baseline` | `alg=A and B` | `vcs=git and svn` | `tier=Fast`
- `Status`: Algorithm A covers Git and SVN for the approved baseline scenarios. Algorithm B covers narrow Git and SVN live-snapshot replay for the same approved story-01 scenarios.
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-01-GIT`, `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-01-SVN`

**AC-01** — *Core measurement contract*

- GIVEN a query `repo + branch + startTime + endTime` for the live-snapshot metric
- WHEN the analyzer computes the final result at `endTime`
- THEN it returns exactly one repository-level result describing the AI ratio among live source-code lines whose current version was added or modified in `startTime~endTime` as of `endTime`

**AC-02** — *External genCodeDesc integration*

- GIVEN external `genCodeDesc` records stored outside the repository, indexed by `repoURL + repoBranch + revisionId`
- WHEN the analyzer discovers in-scope origin revisions from the final live snapshot
- THEN it fetches and uses the matching metadata records during aggregation

**AC-03** — *Missing genCodeDesc record is treated as unattributed, not silent error*

- GIVEN one or more in-scope origin revisions have no matching `genCodeDesc` record in the metadata store
- WHEN the analyzer aggregates the final result
- THEN those lines are counted as human-unattributed (not AI-generated) rather than being silently skipped or causing the run to error, and the absence is observable through `--logLevel debug`

**AC-ALG-A-01** — *Algorithm A · Git*

- GIVEN the approved `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-01-GIT` scenario
- WHEN Algorithm A is executed
- THEN the result matches the approved NG golden output

**AC-ALG-A-02** — *Algorithm A · SVN*

- GIVEN the approved `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-01-SVN` scenario
- WHEN Algorithm A SVN path is executed
- THEN the same observable story-01 contract is preserved

**AC-ALG-B-01** — *Algorithm B · Git*

- GIVEN the approved `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-01-GIT` replay scenario
- WHEN the narrow Algorithm B Git live-snapshot path is executed
- THEN the result matches the approved NG golden output

**AC-ALG-B-02** — *Algorithm B · SVN*

- GIVEN the approved `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-01-SVN` replay scenario
- WHEN the narrow Algorithm B SVN live-snapshot path is executed
- THEN the result matches the approved NG golden output

### USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-02: Human Rewrite Removes Prior AI Attribution

- `WHO`: repository analyst
- `WHEN`: a human revision overwrites code previously attributed to AI before `endTime`
- `WHAT`: reset effective attribution to the newer human revision
- `WHY`: prevent old AI ownership from staying attached to overwritten code
- `Story`: As a repository analyst, I want a human rewrite of a previously AI-generated line to reset attribution to the newer human revision, so that old AI ownership does not remain attached to overwritten code.
- `Support`: `scope=A baseline` | `alg=A and B` | `vcs=shared (Algorithm B evidence via narrow Git slice)` | `tier=Fast`
- `Status`: VCS-agnostic attribution contract. Algorithm A covers Git and SVN. Algorithm B evidence is via the narrow Git live-snapshot replay path.
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-02`

**AC-01** — *Human rewrite clears prior AI attribution*

- GIVEN code previously attributed to AI is superseded by a later human revision before `endTime`
- WHEN the final record is produced for the live changed source-code set at `endTime`
- THEN it reflects the newer state and does not preserve outdated AI ownership

**AC-ALG-A-01** — *Algorithm A*

- GIVEN the approved scenario
- WHEN Algorithm A is executed
- THEN the result matches the approved NG golden output

**AC-ALG-B-01** — *Algorithm B · Git*

- GIVEN the approved replay scenario
- WHEN the narrow Algorithm B Git live-snapshot path is executed
- THEN the result matches the approved NG golden output

---

### USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-03: AI Rewrite Replaces Prior Human Ownership

- `WHO`: repository analyst
- `WHEN`: a later AI revision overwrites a line previously human-authored before `endTime`
- `WHAT`: make the later AI rewrite the effective attribution source
- `WHY`: ensure live changed source code at `endTime` reflects the latest AI contribution
- `Story`: As a repository analyst, I want a later AI rewrite of a human line to become the effective attribution source, so that the live changed source code at `endTime` reflects the latest AI contribution.
- `Support`: `scope=A baseline` | `alg=A and B` | `vcs=shared (Algorithm B evidence via narrow Git slice)` | `tier=Fast`
- `Status`: VCS-agnostic attribution contract. Algorithm A covers Git and SVN. Algorithm B evidence is via the narrow Git live-snapshot replay path.
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-03`

**AC-01** — *Later AI revision becomes effective attribution*

- GIVEN later revisions introduce new AI-attributed code before `endTime`
- WHEN the final record is produced for the live changed source-code state at `endTime`
- THEN it reflects that newer AI contribution

**AC-ALG-A-01** — *Algorithm A*

- GIVEN the approved scenario
- WHEN Algorithm A is executed
- THEN the result matches the approved NG golden output

**AC-ALG-B-01** — *Algorithm B · Git*

- GIVEN the approved replay scenario
- WHEN the narrow Algorithm B Git live-snapshot path is executed
- THEN the result matches the approved NG golden output

---

### USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-04: Deleted AI Lines Must Not Count

- `WHO`: repository analyst
- `WHEN`: AI-generated lines existed earlier in the window but are gone from the branch state at `endTime`
- `WHAT`: exclude deleted AI lines from both numerator and denominator
- `WHY`: keep the result about the current live changed snapshot only
- `Story`: As a repository analyst, I want deleted AI-generated lines to disappear from both numerator and denominator, so that the result reflects only the current live changed source-code snapshot.
- `Support`: `scope=A baseline` | `alg=A and B` | `vcs=shared (Algorithm B evidence via narrow Git slice)` | `tier=Fast`
- `Status`: VCS-agnostic attribution contract. Algorithm A covers Git and SVN. Algorithm B evidence is via the narrow Git live-snapshot replay path.
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-04`

**AC-01** — *Deleted AI lines excluded*

- GIVEN earlier AI-attributed code no longer exists in the branch state at `endTime`
- WHEN the final record is produced for the live changed source-code result
- THEN that deleted code is excluded from the result

**AC-ALG-A-01** — *Algorithm A*

- GIVEN the approved scenario
- WHEN Algorithm A is executed
- THEN the result matches the approved NG golden output

**AC-ALG-B-01** — *Algorithm B · Git*

- GIVEN the approved replay scenario
- WHEN the narrow Algorithm B Git live-snapshot path is executed
- THEN the result matches the approved NG golden output

---

### USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-05: Rename Must Preserve Attribution Lineage

- `WHO`: repository analyst
- `WHEN`: files are renamed or moved before `endTime` without changing their effective content contribution
- `WHAT`: preserve line attribution across path-only history changes
- `WHY`: prevent rename-only changes from distorting the final live changed source-code ratio
- `Story`: As a repository analyst, I want file rename or move operations to preserve line attribution when content does not change, so that the final live changed source-code ratio is not distorted by path-only history changes.
- `Support`: `scope=A baseline` | `alg=A and B` | `vcs=shared (Algorithm B evidence via narrow Git slice)` | `tier=Fast`
- `Status`: VCS-agnostic attribution contract. Git uses git-follow semantics; SVN uses path-copy tracking. Algorithm B evidence is via the narrow Git live-snapshot replay path.
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-05`

**AC-01** — *Attribution stable across renames*

- GIVEN files are renamed or moved before `endTime` without changing their effective contribution
- WHEN the final record is produced for the live changed source-code set at `endTime`
- THEN it remains stable under path-only history changes

**AC-ALG-A-01** — *Algorithm A*

- GIVEN the approved scenario
- WHEN Algorithm A is executed
- THEN the result matches the approved NG golden output

**AC-ALG-B-01** — *Algorithm B · Git*

- GIVEN the approved replay scenario
- WHEN the narrow Algorithm B Git live-snapshot path is executed
- THEN the result matches the approved NG golden output

---

### USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-06: Resolve Mixed Multi-Commit History In One Requested Window

- `WHO`: repository analyst
- `WHEN`: one requested window contains many commits with mixed human-only, AI-only, rewrite, and deletion paths
- `WHAT`: resolve each surviving line by its latest effective attribution inside the window
- `WHY`: keep one final result correct even when history inside the window is mixed and complex
- `Story`: As a repository analyst, I want one requested window to correctly resolve mixed line histories across many commits, so that the final result remains correct when human-only lines, AI-only lines, human-then-AI rewrites, AI-then-human rewrites, and deleted AI lines all appear in the same period.
- `Support`: `scope=A baseline` | `alg=A and B` | `vcs=shared (Algorithm B evidence via narrow Git slice)` | `tier=Fast`
- `Status`: VCS-agnostic attribution contract. Algorithm A covers Git and SVN. Algorithm B evidence is via the narrow Git live-snapshot replay path.
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-06`

**AC-01** — *Mixed window produces one correct final record*

- GIVEN multiple commits inside the requested window contain mixed ownership transitions across different live lines
- WHEN the analyzer resolves the live changed source-code set at `endTime`
- THEN it produces exactly one final record using the latest effective attribution of each surviving line

**AC-02** — *Superseded intermediate states do not leak*

- GIVEN a surviving line passes through a long chain of intermediate revisions inside the window
- WHEN the analyzer resolves that live line at `endTime`
- THEN it uses the latest effective live attribution without leaking superseded intermediate ownership into the final result

**AC-ALG-A-01** — *Algorithm A*

- GIVEN the approved scenario
- WHEN Algorithm A is executed
- THEN the result matches the approved NG golden output

**AC-ALG-B-01** — *Algorithm B · Git*

- GIVEN the approved replay scenario
- WHEN the narrow Algorithm B Git live-snapshot path is executed
- THEN the result matches the approved NG golden output

---

### USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-07: Merge Commit Must Preserve Effective Attribution

- `WHO`: repository analyst
- `WHEN`: merged branches bring human and AI contributions into the target branch before `endTime`
- `WHAT`: preserve the effective attribution of each surviving line through merges
- `WHY`: prevent merge commits from resetting ownership or flattening provenance
- `Story`: As a repository analyst, I want merged branch content to preserve the effective attribution of surviving lines, so that a merge operation does not incorrectly reset line ownership to the merge commit itself.
- `Support`: `scope=A baseline` | `alg=A and B` | `vcs=shared (Algorithm B evidence via narrow Git slice)` | `tier=Fast`
- `Status`: VCS-agnostic attribution contract. Algorithm A covers Git and SVN merge semantics. Algorithm B evidence is via the narrow Git live-snapshot replay path.
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-07`

**AC-01** — *Merge does not reset ownership*

- GIVEN a merge commit brings together earlier human and AI-attributed changes before `endTime`
- WHEN the final record is produced for the live changed source-code set at `endTime`
- THEN it uses the effective attribution of surviving merged lines rather than treating the merge commit as a blanket origin

**AC-02** — *Per-line independence across merged branches*

- GIVEN multiple branches are merged before `endTime` and surviving lines originate from different merged branches
- WHEN the analyzer resolves the final live state
- THEN it preserves each surviving line independently and does not collapse ownership to merge commits or final branch identity alone

**AC-03** — *Merge conflict resolution follows post-resolution committer*

- GIVEN a merge results in conflict markers or manually resolved regions that mix AI-originated and human-originated content before `endTime`
- WHEN the final record is produced for the live changed source-code set at `endTime`
- THEN each post-resolution surviving line is attributed according to the committer of the conflict-resolution commit, not the pre-merge origin revisions of the conflicting regions

**AC-ALG-A-01** — *Algorithm A*

- GIVEN the approved scenario
- WHEN Algorithm A is executed
- THEN the result matches the approved NG golden output

**AC-ALG-B-01** — *Algorithm B · Git*

- GIVEN the approved replay scenario
- WHEN the narrow Algorithm B Git live-snapshot path is executed
- THEN the result matches the approved NG golden output

### USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-08: Git And SVN Must Follow The Same Result Contract

- `WHO`: repository analyst
- `WHEN`: the same primary metric is requested against equivalent supported Git and SVN histories
- `WHAT`: keep the query-result contract consistent across VCS targets
- `WHY`: ensure changing VCS type does not change metric semantics or output structure
- `Story`: As a repository analyst, I want Git and SVN targets to follow the same query-result contract for the current primary metric, so that changing VCS type does not change metric semantics or output structure.
- `Support`: `scope=A baseline` | `alg=A and narrow B parity slice` | `vcs=git and svn` | `tier=Fast`
- `Status`: Git and SVN parity exists through Algorithm A. Narrow Algorithm B contract parity exists on the approved story-01 Git/SVN scenarios plus the approved story-08 SVN parity scenario.
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-08-SVN-PARITY`

**AC-01** — *Same semantics across VCS types*

- GIVEN equivalent supported repository history in Git or SVN for the same requested window
- WHEN the current primary metric is analyzed
- THEN Git and SVN produce one final record with the same metric semantics and protocol-shaped structure, differing only in VCS-specific repository identity details

**AC-GIT-01** — *Git track defines one parity side*

- GIVEN the current Git path for the primary metric
- WHEN it is validated through the baseline live-snapshot scenarios
- THEN it defines one side of the observable parity contract

**AC-SVN-01** — *SVN track*

- GIVEN the approved `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-08-SVN-PARITY` scenario
- WHEN the current SVN path is executed
- THEN the result matches the approved NG golden output while preserving the shared story-08 contract

**AC-SVN-02** — *SVN-specific analogue allowed*

- GIVEN SVN path-history or blame differences require a VCS-specific parity shape
- WHEN the parity scenario is designed
- THEN it may use a defensible SVN-specific repository shape as long as the observable result contract stays the same

**AC-ALG-B-01** — *Algorithm B cross-VCS parity*

- GIVEN the approved narrow Algorithm B Git and SVN live-snapshot verification tracks for the baseline scenario
- WHEN they are used as the parity scenario
- THEN they produce the same protocol-shaped observable contract across Git and SVN, differing only in VCS-specific repository identity fields

---

### USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-09: Large Repository Snapshot Must Preserve Result Semantics

- `WHO`: repository analyst
- `WHEN`: the repository contains many files and many live lines but the analyst still expects the same metric semantics
- `WHAT`: preserve the live-snapshot contract for large realistic repositories
- `WHY`: keep aggregate results trustworthy at larger repository scales
- `Story`: As a repository analyst, I want the analyzer to keep the same result semantics when the repository contains many source files and many live lines, so that the final aggregate result remains correct for realistic large codebases.
- `Support`: `scope=A baseline` | `alg=A and narrow B Git slice` | `vcs=shared` | `tier=Fast`
- `Status`: VCS-agnostic scale contract. Algorithm A covers Git and SVN. Algorithm B evidence is via the narrow Git live-snapshot replay path.
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-09`

**AC-01** — *Semantics preserved at scale*

- GIVEN the final live snapshot at `endTime` spans many source files and many live code lines
- WHEN the analyzer computes the final aggregate result
- THEN it still produces exactly one repository-level final result with the same metric semantics and protocol shape as smaller repositories

**AC-02** — *Per-line attribution rules unchanged by size*

- GIVEN a large repository snapshot contains many in-scope lines across many files
- WHEN the analyzer aggregates the result
- THEN repository size or file count does not change per-line attribution rules, repository identity rules, or the meaning of the final `SUMMARY` fields

**AC-ALG-A-01** — *Algorithm A*

- GIVEN the approved scenario
- WHEN Algorithm A is executed
- THEN the result matches the approved NG golden output

**AC-ALG-B-01** — *Algorithm B · Git*

- GIVEN the approved scenario expressed through fixture replay or the focused real local-Git replay path
- WHEN the narrow Algorithm B Git live-snapshot path is executed
- THEN the result matches the approved NG golden output

---

### USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-10: Deep History Must Preserve Latest Effective Attribution

- `WHO`: repository analyst
- `WHEN`: surviving lines at `endTime` come through long revision chains with many intermediate rewrites
- `WHAT`: resolve each surviving line by its latest effective attribution instead of by superseded intermediate ownership
- `WHY`: prevent deep history from distorting the final live result
- `Story`: As a repository analyst, I want long revision chains to preserve the latest effective attribution of each surviving line, so that many intermediate rewrites do not distort the final live result.
- `Support`: `scope=A baseline` | `alg=A and narrow B Git slice` | `vcs=shared` | `tier=Fast`
- `Status`: VCS-agnostic depth contract. Algorithm A covers Git and SVN. Algorithm B evidence is via the narrow Git live-snapshot replay path.
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-10`

**AC-01** — *Latest effective attribution wins*

- GIVEN in-scope live lines at `endTime` depend on long revision chains with many intermediate rewrites
- WHEN the analyzer resolves each surviving line
- THEN it uses the latest effective live attribution rather than earlier superseded revisions in the chain

**AC-02** — *Superseded states do not leak*

- GIVEN long history chains contain both human-to-AI and AI-to-human transitions before `endTime`
- WHEN the final aggregate result is produced
- THEN deleted or superseded intermediate states do not leak into that result

**AC-ALG-A-01** — *Algorithm A*

- GIVEN the approved scenario
- WHEN Algorithm A is executed
- THEN the result matches the approved NG golden output

**AC-ALG-B-01** — *Algorithm B · Git*

- GIVEN the approved scenario expressed through fixture replay or focused real local-Git replay
- WHEN the narrow Algorithm B Git live-snapshot path is executed
- THEN the result matches the approved NG golden output

---

### USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-11: Many Merged Branches In One Window Must Preserve Per-Line Attribution

- `WHO`: repository analyst
- `WHEN`: many branches are merged into the target branch inside one requested window
- `WHAT`: preserve per-line effective attribution across branch-heavy merge history
- `WHY`: stop branch fan-in and merge order from distorting the final result
- `Story`: As a repository analyst, I want branch-heavy history inside one requested window to preserve per-line effective attribution, so that integrating many feature branches into the target branch does not distort the final result.
- `Support`: `scope=A baseline` | `alg=A and narrow B Git slice` | `vcs=shared; SVN analogue note` | `tier=Fast`
- `Status`: VCS-agnostic merge-branch contract. Algorithm A covers Git and SVN. Algorithm B evidence is via the narrow Git live-snapshot replay path. SVN parity may require a defensible analogue rather than a literal Git port.
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-11`

**AC-01** — *One final record despite branch fan-in*

- GIVEN many branches are merged into the target branch before `endTime`
- WHEN the analyzer computes the final result for the live changed source-code set at `endTime`
- THEN it still produces exactly one repository-level final result

**AC-02** — *Per-line independence across merged branches*

- GIVEN surviving lines originate from different merged branches with different effective histories
- WHEN the analyzer resolves the final live state
- THEN it preserves each surviving line independently and does not flatten ownership to merge commits, branch labels, or merge order alone

**AC-ALG-A-01** — *Algorithm A*

- GIVEN the approved scenario
- WHEN Algorithm A is executed
- THEN the result matches the approved NG golden output

**AC-ALG-A-02** — *SVN analogue*

- GIVEN SVN parity for the same broad contract needs a defensible analogue and literal same-file Git shapes would be misleading for SVN
- WHEN the parity scenario is designed
- THEN an SVN-specific analogue may be used as long as the shared observable contract is preserved

**AC-ALG-B-01** — *Algorithm B · Git*

- GIVEN the approved replay scenario
- WHEN the narrow Algorithm B Git live-snapshot path is executed
- THEN the result matches the approved NG golden output

## Heavy Production Gates

These stories are production-scale correctness gates. They verify that result semantics are preserved under realistic heavy workloads.

### USNG-REPO-GIT-LOCAL-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-12: Git Production-Scale Local Repository Must Stay Correct Under Branch-Heavy Release Convergence

- `WHO`: repository analyst
- `WHEN`: validating production-readiness on a branch-heavy local Git repository that mirrors release convergence at scale
- `WHAT`: keep Algorithm A + Scope A correct on a production-scale local Git topology
- `WHY`: prove that large branch counts, deep history, and hybrid release merges do not distort the final live attribution result
- `Story`: As a repository analyst, I want Algorithm A and Scope A to remain correct on a production-scale local Git repository, so that large branch counts, deep history, and hybrid release merges do not distort the final live attribution result.
- `Support`: `scope=A baseline` | `alg=A` | `vcs=git` | `tier=Heavy`
- `Status`: production-facing heavy gate with real local Git repository generation, correctness, and scalability checks.
- `Anchors`: `TestsNG-REPO-GIT-LOCAL-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-12`

**AC-GIT-01** — *Scale: one correct result*

- GIVEN a local Git repository with ~100+ branches, ~1000+ commits, and repeated feature-to-integration-to-release merge fan-in before `endTime`
- WHEN the analyzer computes the final result
- THEN it still produces exactly one repository-level final result

**AC-GIT-02** — *Scale: effective origin preserved*

- GIVEN surviving lines reach the release branch through mixed direct merges, integration branches, and staged convergence
- WHEN final attribution is resolved
- THEN it is based on each surviving line's effective origin revision rather than merge shape, first-parent history alone, or branch naming

**AC-GIT-03** — *Local topology is valid for production-readiness*

- GIVEN the production-like repository is local rather than remote-hosted
- WHEN it is used as the production-readiness acceptance scenario
- THEN it remains valid because transport is out of scope and history semantics must remain identical apart from network access

**AC-GIT-04** — *Correctness and scalability both verified*

- GIVEN the heavy Git production-scale scenario completes successfully
- WHEN the acceptance outcome is evaluated
- THEN it verifies both correctness of the final aggregate result and scalability-oriented reuse behavior such as bounded metadata reuse or bounded revision-time lookup reuse

---

### USNG-REPO-SVN-LOCAL-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-13: SVN Production-Scale Local Repository Must Stay Correct Under Branch And Merge Pressure

- `WHO`: repository analyst
- `WHEN`: validating production-readiness on a production-scale local SVN repository with branch copying and reintegration pressure
- `WHAT`: keep Algorithm A + Scope A correct on a production-scale local SVN topology
- `WHY`: prove that SVN branch copying, merges, and release reintegration at scale do not break live attribution
- `Story`: As a repository analyst, I want Algorithm A and Scope A to remain correct on a production-scale local SVN repository, so that SVN branch copying, merges, and release reintegration at scale do not break live attribution.
- `Support`: `scope=A baseline` | `alg=A` | `vcs=svn` | `tier=Heavy`
- `Status`: production-facing heavy gate with real local SVN repository generation, correctness, and scalability checks.
- `Anchors`: `TestsNG-REPO-SVN-LOCAL-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-13`

**AC-SVN-01** — *Scale: one correct result*

- GIVEN a local SVN repository with ~100+ branch copies, ~1000+ revisions, and repeated branch-to-release merge activity before `endTime`
- WHEN the analyzer computes the final result
- THEN it still produces exactly one repository-level final result

**AC-SVN-02** — *Scale: effective origin preserved*

- GIVEN surviving lines reach the release path through mixed direct work, branch copies, and merge or reintegration history
- WHEN final attribution is resolved under supported SVN semantics
- THEN it preserves each surviving line's effective origin revision and does not collapse ownership to merge timing or final branch path alone

**AC-SVN-03** — *Local topology is valid for production-readiness*

- GIVEN the production-like SVN repository is local rather than remote-hosted
- WHEN it is used as the production-readiness acceptance scenario
- THEN it remains valid because transport is not part of the attribution contract

**AC-SVN-04** — *Correctness and scalability both verified*

- GIVEN the heavy SVN production-scale scenario completes successfully
- WHEN the acceptance outcome is evaluated
- THEN it verifies both correctness of the final aggregate result and scalability-oriented reuse behavior such as branch-origin metadata reuse, bounded revision-time queries, or equivalent explicit reuse signals

## Scope Contract Stories

These stories broaden the counted content boundary from source-code-only to comment-inclusive, documentation-only, and combined views.

### USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-B-14: Scope B Source Code With Comments Must Include Comment Lines In Totals

- `WHO`: repository analyst
- `WHEN`: wanting source-file totals to include comment lines as part of measured source text
- `WHAT`: make `--scope B` count all non-blank lines in source files, including comments
- `WHY`: measure AI contribution across the full textual content of source files, not just executable code
- `Story`: As a repository analyst, I want `--scope B` to count all non-blank lines in source files, including comment lines, in the aggregate result, so that I can measure AI contribution across the full textual content of source files, not just executable code.
- `Support`: `scope=B` | `alg=primarily A at story level` | `vcs=shared` | `tier=Fast`
- `Status`: first-class scope story for comment-inclusive source-file totals.
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-B-14`

**AC-01** — *Comment lines included in scope B totals*

- GIVEN a source file contains both code lines and comment lines
- WHEN the analyzer runs with `--scope B`
- THEN `totalCodeLines` includes all non-blank source lines rather than only the code-only subset counted by Scope A

**AC-02** — *Comment line attribution*

- GIVEN a source file contains comment lines covered through `codeLines`
- WHEN the analyzer runs with `--scope B`
- THEN comment lines with `genRatio=100` count as `fullGeneratedCodeLines`, and comment lines with `genRatio` between 1 and 99 count as `partialGeneratedCodeLines`

**AC-03** — *Scope A backward compatibility*

- GIVEN the same repository and metadata analyzed under the baseline scope
- WHEN the analyzer runs with `--scope A`
- THEN comment lines remain excluded, preserving backward compatibility

---

### USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-C-15: Scope C Documentation Text Lines Must Be Counted From Doc Files Using docLines Protocol

- `WHO`: repository analyst
- `WHEN`: wanting to measure documentation-only contribution instead of source-code contribution
- `WHAT`: make `--scope C` analyze documentation files and use `docLines` for attribution
- `WHY`: measure AI contribution to documentation artifacts separately from source code
- `Story`: As a repository analyst, I want `--scope C` to analyze documentation text files and use the `docLines` protocol field for AI attribution, so that I can measure AI contribution to documentation artifacts separately from source code.
- `Support`: `scope=C` | `alg=primarily A at story level` | `vcs=shared` | `tier=Fast`
- `Status`: first-class scope story for documentation-only analysis.
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-C-15`

**AC-01** — *Scope C analyzes doc files only*

- GIVEN a repository contains files in `DOC_EXTENSIONS`
- WHEN the analyzer runs with `--scope C`
- THEN it includes only documentation files and excludes source-code files

**AC-02** — *docLines protocol used for attribution*

- GIVEN documentation files are analyzed under `--scope C`
- WHEN attribution is computed and the result is emitted
- THEN attribution uses `docLines` and the output uses `totalDocLines`, `fullGeneratedDocLines`, and `partialGeneratedDocLines`

**AC-03** — *Scope isolation*

- GIVEN the same repository is analyzed under source-code scopes
- WHEN the analyzer runs with `--scope A` or `--scope B`
- THEN documentation files remain excluded, preserving scope isolation

---

### USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-D-16: Scope D All Text Must Unify Source And Documentation Files Into A Single Aggregate

- `WHO`: repository analyst
- `WHEN`: wanting one combined result across both source files and documentation files
- `WHAT`: make `--scope D` count all non-blank source and documentation lines in one aggregate
- `WHY`: measure total AI contribution across the full textual content of the repository
- `Story`: As a repository analyst, I want `--scope D` to count all non-blank lines from both source files and documentation files in one combined result, so that I can measure total AI contribution across the entire textual content of the repository.
- `Support`: `scope=D` | `alg=primarily A at story level` | `vcs=shared` | `tier=Fast`
- `Status`: first-class scope story for unified source-plus-documentation totals.
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-D-16`

**AC-01** — *Both file families included*

- GIVEN a repository contains both source files and documentation files
- WHEN the analyzer runs with `--scope D`
- THEN it includes both file families in one combined analysis

**AC-02** — *Combined attribution fields*

- GIVEN both source files and documentation files are analyzed under `--scope D`
- WHEN attribution is computed and the combined result is emitted
- THEN source lines are attributed through `codeLines`, documentation lines through `docLines`, and the combined summary uses `totalCodeLines`, `fullGeneratedCodeLines`, and `partialGeneratedCodeLines`

**AC-03** — *Scope isolation preserved*

- GIVEN the same repository is analyzed under `--scope A`, `--scope B`, or `--scope C`
- WHEN the analyzer evaluates files outside each scope boundary
- THEN those file families remain excluded

---

### USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-ALL-17: Scope Parity Matrix Must Confirm All Four Scopes Produce Correct And Isolated Results

- `WHO`: repository analyst
- `WHEN`: running all four scopes on the same repository and expecting each scope to stay distinct and correct
- `WHAT`: verify the full scope matrix across A, B, C, and D
- `WHY`: trust that scope selection really controls the measurement boundary
- `Story`: As a repository analyst, I want a cross-scope verification that runs Scope A, B, C, and D on the same repository and confirms each produces the expected distinct result, so that I can trust that scope selection genuinely controls the measurement boundary.
- `Support`: `scope=A/B/C/D` | `alg=primarily A at story level` | `vcs=shared` | `tier=Fast`
- `Status`: first-class cross-scope contract story.
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-ALL-17`

**AC-01** — *Each scope correct independently*

- GIVEN a repository contains source files with code and comments plus documentation files
- WHEN the analyzer is run with `--scope A`, `--scope B`, `--scope C`, and `--scope D`
- THEN each scope produces the correct summary for its own scope definition

**AC-02** — *Doc vs code field families stay distinct*

- GIVEN the full four-scope matrix is executed on the same repository
- WHEN the summaries are compared across scopes
- THEN Scope C uses `totalDocLines`, `fullGeneratedDocLines`, `partialGeneratedDocLines`, while Scopes A, B, and D use `totalCodeLines`, `fullGeneratedCodeLines`, `partialGeneratedCodeLines`

---

## Algorithm-B Scope Broadening Stories

These stories keep the same analyst role but move the scenario to replay-based attribution on broader scopes.

### USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-B-18: Algorithm B Must Support Scope B

- `WHO`: repository analyst
- `WHEN`: needing replay-based attribution across source code plus source comments
- `WHAT`: make `--algorithm B --scope B` count all non-blank source lines including comments
- `WHY`: measure total AI contribution to all source text using the incremental replay algorithm
- `Story`: As a repository analyst, I want `--algorithm B --scope B` to count all non-blank source lines including comments during replay, so that I can measure total AI contribution to all source text using the incremental replay algorithm.
- `Support`: `scope=B` | `alg=B` | `vcs=current supported replay shapes` | `tier=Fast`
- `Status`: first-class story for Algorithm B comment-inclusive source replay.
- `Anchors`: `TestsNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-B-18`

**AC-ALG-B-01** — *Comment lines counted under Algorithm B Scope B*

- GIVEN a source file contains both code lines and comment lines
- WHEN Algorithm B runs with `--scope B`
- THEN `totalCodeLines` includes all non-blank source lines

---

### USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-C-19: Algorithm B Must Support Scope C

- `WHO`: repository analyst
- `WHEN`: needing replay-based attribution on documentation files instead of source files
- `WHAT`: make `--algorithm B --scope C` replay and count documentation file lines through `docLines`
- `WHY`: measure AI contribution to documentation using the incremental replay algorithm
- `Story`: As a repository analyst, I want `--algorithm B --scope C` to replay and count documentation file lines using the `docLines` protocol field, so that I can measure AI contribution to documentation using the incremental replay algorithm.
- `Support`: `scope=C` | `alg=B` | `vcs=current supported replay shapes` | `tier=Fast`
- `Status`: first-class story for Algorithm B documentation replay.
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

### USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-D-20: Algorithm B Must Support Scope D

- `WHO`: repository analyst
- `WHEN`: needing replay-based attribution across both source and documentation files in one run
- `WHAT`: make `--algorithm B --scope D` replay both file families into one combined result
- `WHY`: measure total AI contribution across all textual repository content using the incremental replay algorithm
- `Story`: As a repository analyst, I want `--algorithm B --scope D` to replay both source files and documentation files into a unified result, so that I can measure total AI contribution across all textual repository content using the incremental replay algorithm.
- `Support`: `scope=D` | `alg=B` | `vcs=current supported replay shapes` | `tier=Fast`
- `Status`: first-class story for Algorithm B unified source-plus-doc replay.
- `Anchors`: `TestsNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-D-20`

**AC-ALG-B-01** — *Both file families replayed*

- GIVEN a repository contains both source files and documentation files
- WHEN Algorithm B runs with `--scope D`
- THEN it replays both file families, using `codeLines` for source files and `docLines` for documentation files

**AC-ALG-B-02** — *Combined summary fields*

- GIVEN Algorithm B produces a combined replay result under `--scope D`
- WHEN the summary is emitted
- THEN it uses `totalCodeLines`, `fullGeneratedCodeLines`, and `partialGeneratedCodeLines`

## Period-Added Contract Stories

These stories measure AI contribution added during the window, not the end-of-window inventory.

### USNG-REPO-GIT-LOCAL-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-21: Calculate AI-Added Ratio During The Requested Period

- `WHO`: repository analyst
- `WHEN`: wanting to measure AI contribution added during the window itself, not the end-of-window inventory
- `WHAT`: calculate how much AI-generated code was added during `startTime~endTime`
- `WHY`: distinguish period contribution from end-of-period inventory
- `Story`: As a repository analyst, I want to calculate how much AI-generated code was added during `startTime~endTime`, so that I can distinguish period contribution from end-of-period inventory.
- `Support`: `scope=shared story anchor` | `alg=A future; B current narrow baseline` | `vcs=shared` | `tier=Fast`
- `Status`: shared story anchor; current executable path is narrow Algorithm B Git baseline through offline replay and supported local-Git replay.
- `Anchors`: `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-21`

**AC-01** — *Core period-added contract*

- GIVEN `repo`, `branch`, `startTime`, and `endTime` define a requested period
- WHEN the period contribution metric is executed
- THEN it returns exactly one repository-level final result describing the aggregate AI-added code result during that period

**AC-ALG-A-01** — *Algorithm A future path satisfies shared contract*

- GIVEN a future Algorithm A path claims support for the period contribution metric
- WHEN it is evaluated against the shared contract
- THEN it satisfies the shared story-21 clauses without weakening the observable contract

**AC-ALG-A-02** — *Algorithm A tier declaration required*

- GIVEN a future Algorithm A fixture or real-repository acceptance scenario is added for story-21
- WHEN its support tier is documented
- THEN it declares `Fast` or `Heavy` explicitly

**AC-ALG-B-01** — *Algorithm B current path*

- GIVEN the approved `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-21` scenario
- WHEN the current narrow offline Git Algorithm B baseline is executed
- THEN the result matches the approved NG golden output

**AC-ALG-B-02** — *Algorithm B current boundary*

- GIVEN the input stays within the current narrow Git replay boundary
- WHEN the CLI runs with `--algorithm B`
- THEN the current slice may execute this story through the approved replay-input path or the supported local Git checkout path

**AC-ALG-B-03** — *Broader shapes remain unsupported*

- GIVEN broader Algorithm B history shapes such as multi-file replay, rename-path changes, or merge-aware accounting beyond accepted stories
- WHEN support is described or discussed
- THEN those shapes remain unsupported until proven by their own acceptance tracks

---

### USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-A-22: Single-Branch Period-Added Baseline Without Merges Or Renames

- `WHO`: repository analyst
- `WHEN`: wanting the cleanest possible single-branch baseline for the period-added metric before topology complexity is introduced
- `WHAT`: prove the core Algorithm B period-added contract on a simple linear Git history
- `WHY`: establish a stable baseline before adding rewrites, renames, or merges
- `Story`: As a repository analyst, I want a single-branch period-added baseline without merges or renames, so that the core Algorithm B period-contribution contract is proven before topology complexity is introduced.
- `Support`: `scope=A and B note` | `alg=B` | `vcs=git local replay` | `tier=Fast`
- `Status`: first-class Algorithm B single-branch baseline story.
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

### USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-23: Period-Added Accounting With Deletions, Resets, And Mixed Rewrites

- `WHO`: repository analyst
- `WHEN`: the requested period contains added lines, deleted lines, and mixed AI-human rewrites inside one window
- `WHAT`: keep period-added accounting correct across deletions, resets, and mixed rewrites
- `WHY`: prevent superseded or deleted in-window AI lines from distorting the period result
- `Story`: As a repository analyst, I want period-added accounting to handle deletions, resets, and mixed rewrites inside one window, so that superseded or deleted in-window AI lines do not distort the period result.
- `Support`: `scope=primary baseline` | `alg=B` | `vcs=git local replay` | `tier=Fast`
- `Status`: first-class Algorithm B rewrite and deletion story.
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
- THEN those pre-window surviving lines are excluded from the period-added total regardless of their attribution

---

### USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-24: Git Rename And Move Handling For Period Contribution

- `WHO`: repository analyst
- `WHEN`: a file is renamed during the period and the analyst still needs true period-added accounting
- `WHAT`: preserve rename and move semantics in the period-added metric
- `WHY`: stop path-only changes from making old lines appear as new in-window additions
- `Story`: As a repository analyst, I want period-added accounting to preserve rename and move semantics, so that path-only history changes do not make older lines appear as new in-window additions.
- `Support`: `scope=primary baseline` | `alg=B` | `vcs=git local replay` | `tier=Fast`
- `Status`: first-class Algorithm B rename story for period contribution.
- `Anchors`: `TestsNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-24`

**AC-ALG-B-01** — *Rename preserves period-added accuracy*

- GIVEN a file is renamed during the window and a new AI line is added
- WHEN Algorithm B computes the period-added result
- THEN only the new line counts in the period-added total while pre-window lines that survived the rename remain excluded

---

### USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-25: Merge-Aware Git Period Contribution Inside One Window

- `WHO`: repository analyst
- `WHEN`: the requested period includes branch work and non-fast-forward merge activity
- `WHAT`: keep period-added accounting correct across merge-aware Git history inside the window
- `WHY`: ensure contributions from both main and merged feature branches count correctly
- `Story`: As a repository analyst, I want period-added accounting to survive branch-and-merge history inside one window, so that contributions from both main and merged feature branches are counted correctly.
- `Support`: `scope=primary baseline` | `alg=B` | `vcs=git local replay` | `tier=Fast`
- `Status`: first-class Algorithm B merge-aware story for period contribution.
- `Anchors`: `TestsNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-25`

**AC-ALG-B-01** — *Both main and feature branch contributions counted*

- GIVEN AI lines are added on main and on a feature branch and then merged during the window through a non-fast-forward merge
- WHEN Algorithm B computes the period-added result
- THEN both contributions survive and count correctly in the final period-added total

**AC-ALG-B-02** — *Lines present on both branches before the merge must not be double-counted*

- GIVEN a line exists on both main and the feature branch before the in-window merge (e.g. identical content on both sides)
- WHEN Algorithm B computes the period-added result
- THEN that line is counted at most once in the final period-added total, regardless of how many branch histories include it

---

### USNG-REPO-SVN-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-A-26: SVN-Supported Subset For Algorithm-B Period Contribution

- `WHO`: repository analyst
- `WHEN`: wanting a defended SVN subset for period-added replay without overclaiming full SVN parity
- `WHAT`: make the supported SVN fixture subset produce correct Algorithm B period-added results
- `WHY`: expand SVN support scenario-first while keeping claims defensible
- `Story`: As a repository analyst, I want the defended SVN subset of Algorithm B period-added replay to produce correct results from offline fixtures, so that SVN support can expand scenario-first without overclaiming general parity.
- `Support`: `scope=primary baseline` | `alg=B` | `vcs=svn offline fixtures` | `tier=Fast`
- `Status`: first-class Algorithm B SVN subset story through offline replay artifacts.
- `Anchors`: `TestsNG-REPO-SVN-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-A-26`

**AC-ALG-B-01** — *SVN offline fixtures produce correct period-added result*

- GIVEN SVN-style offline commit-diff fixtures are provided together with protocol files
- WHEN Algorithm B replays the period-added scenario
- THEN it correctly counts AI versus human lines from the SVN patches

---

### USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-B-33: Period-Added Metric For Documentation Lines Must Follow The Same Window Contract As SCOPE-A

- `WHO`: repository analyst
- `WHEN`: wanting to measure AI contribution to documentation lines added or modified during a requested period
- `WHAT`: report period-added AI attribution for documentation lines in the requested window
- `WHY`: documentation evolution needs its own attribution window separate from source-code measurement
- `Story`: As a repository analyst, I want the period-added metric for documentation lines (SCOPE-B) to report correct AI attribution within a requested period window, so that documentation output can be attributed with the same rigor as source-code output.
- `Support`: `scope=B` | `alg=B` | `vcs=git local replay` | `tier=Fast`
- `Status`: New USNG cell. Algorithm B documentation-line replay coverage for the approved period window defines this story's boundary.
- `Anchors`: `TestsNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-B-33`

**AC-ALG-B-01** — *Correct period-added documentation attribution*

- GIVEN a Git repository contains documentation files and the requested period defines a `startTime~endTime` window
- WHEN Algorithm B computes the period-added metric with `--scope B`
- THEN it reports the AI-attributed documentation lines added during the window using the same replay contract as SCOPE-A but filtering to the documentation-line family only

---

### USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-C-34: Period-Added Metric For Combined Source Scope Must Aggregate Code And Comments In One Period Result

- `WHO`: repository analyst
- `WHEN`: wanting to measure AI contribution to combined source lines (code + comments) added during a requested period
- `WHAT`: report period-added AI attribution for both code and comment lines in one combined result
- `WHY`: some teams attribute AI contribution across both code and comments to capture the full source-editing picture in one query
- `Story`: As a repository analyst, I want the period-added metric for combined source lines (SCOPE-C) to aggregate both code and comment lines in one period result, so that AI attribution covers the full source-editing footprint during a period.
- `Support`: `scope=C` | `alg=B` | `vcs=git local replay` | `tier=Fast`
- `Status`: New USNG cell covering the combined source family for period-added measurement.
- `Anchors`: `TestsNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-C-34`

**AC-ALG-B-01** — *Combined source attribution in one period result*

- GIVEN a Git repository contains source files with both code lines and comment lines and the requested period defines a window
- WHEN Algorithm B computes the period-added metric with `--scope C`
- THEN it reports AI-attributed lines from both code and comment families added during the window in one combined period result

**AC-ALG-B-02** — *Code and comment families stay distinct inside the combined result*

- GIVEN Algorithm B produces a period-added SCOPE-C result
- WHEN the result `SUMMARY` is read
- THEN code-family and comment-family attribution values are independently accessible inside the `SUMMARY` fields rather than collapsed into a single undifferentiated count

---

### USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-D-35: Period-Added Metric For All Scopes Must Cover Code, Comments, And Documentation In One Period Result

- `WHO`: repository analyst
- `WHEN`: wanting a single comprehensive view of AI contribution across all line families (code, comments, documentation) during a period
- `WHAT`: report period-added AI attribution for all line families in one period result
- `WHY`: leadership-level summaries need one number that covers all AI-added content regardless of line family
- `Story`: As a repository analyst, I want the period-added metric for all line families (SCOPE-D) to cover code, comment, and documentation lines in one period result, so that one query answers how much total content was AI-attributed during a period.
- `Support`: `scope=D` | `alg=B` | `vcs=git local replay` | `tier=Fast`
- `Status`: New USNG cell covering the all-families aggregate for period-added measurement.
- `Anchors`: `TestsNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-D-35`

**AC-ALG-B-01** — *All-families period-added result*

- GIVEN a Git repository contains both source files and documentation files and the requested period defines a window
- WHEN Algorithm B computes the period-added metric with `--scope D`
- THEN it reports AI-attributed lines across code, comment, and documentation families in one combined period result

**AC-ALG-B-02** — *Field families stay independently accessible*

- GIVEN Algorithm B produces a period-added SCOPE-D result
- WHEN the result `SUMMARY` is read
- THEN code-family, comment-family, and documentation-family attribution values are each independently accessible inside the `SUMMARY` fields

---

## Cross-Algorithm, Hardening, And Operator Stories

These stories address algorithm parity, runtime safety, and operator-visible narrative.

### USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-ALL-27: Algorithm A And Algorithm B Must Produce Identical SUMMARY For Every Scope

- `WHO`: repository analyst
- `WHEN`: comparing the blame-based and replay-based implementations on the same repository content
- `WHAT`: keep `SUMMARY` identical across Algorithm A and Algorithm B for every scope
- `WHY`: ensure algorithm choice does not change the measurement result
- `Story`: As a repository analyst, I want Algorithm A and Algorithm B to produce the same `SUMMARY` for every scope on the same repository content, so that algorithm choice does not change the measurement result.
- `Support`: `scope=A/B/C/D` | `alg=A and B` | `vcs=shared replay-supported shapes` | `tier=Fast`
- `Status`: first-class cross-algorithm cross-scope parity story.
- `Anchors`: `TestsNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-ALL-27`

**AC-01** — *Scope A parity*

- GIVEN a repository contains source files and documentation files
- WHEN Algorithm A and Algorithm B are both run with `--scope A`
- THEN they produce identical `SUMMARY` values

**AC-02** — *Remaining-scope parity*

- GIVEN the same repository is analyzed under scopes B, C, and D
- WHEN Algorithm A and Algorithm B are both run with `--scope B`, `--scope C`, and `--scope D`
- THEN they produce identical `SUMMARY` values, including the correct doc-versus-code field family where relevant

---

### USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-RUNTIME-28: Production Hardening - Scope Validation And File-Size Guard

- `WHO`: CLI operator
- `WHEN`: the operator passes invalid scope input or the runtime encounters oversized VCS output
- `WHAT`: fail fast with explicit validation and size guards
- `WHY`: avoid silent wrong results, runaway memory use, or unclear failure behavior
- `Story`: As a CLI operator, I want invalid `--scope` values to be rejected at input validation and oversized VCS outputs to be caught before processing, so that the tool fails fast with clear diagnostics instead of producing silent wrong results or running out of memory.
- `Support`: `scope=input and runtime guard` | `alg=A and B` | `vcs=git-focused runtime checks` | `tier=Fast`
- `Status`: first-class hardening story.
- `Anchors`: `TestsNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-RUNTIME-28`

**AC-HARD-01** — *Invalid scope rejected at input*

- GIVEN the CLI receives an invalid `--scope` value such as `Z`, lowercase `a`, or an empty string
- WHEN input validation runs
- THEN the tool exits with `EXIT_INPUT_ERROR` and a diagnostic containing `--scope must be one of: A, B, C, D`

**AC-HARD-02** — *Algorithm B oversized-file guard*

- GIVEN a Git repository contains a file whose `git show` output exceeds `MAX_FILE_SIZE_BYTES`
- WHEN Algorithm B reads the file through `read_git_file_lines_at_revision`
- THEN it raises `RepositoryStateError` with a clear diagnostic

**AC-HARD-03** — *Algorithm A oversized-blame guard*

- GIVEN Git blame output exceeds `MAX_FILE_SIZE_BYTES`
- WHEN Algorithm A parses blame through `parse_blame`
- THEN it raises `RepositoryStateError` with a clear diagnostic

**AC-HARD-04** — *Invalid `--algorithm` value rejected at input*

- GIVEN the CLI receives an invalid `--algorithm` value such as `C`, `0`, or an empty string
- WHEN input validation runs
- THEN the tool exits with `EXIT_INPUT_ERROR` and a diagnostic containing `--algorithm must be one of: A, B`

**AC-HARD-05** — *Invalid `startTime` or `endTime` format rejected at input*

- GIVEN the CLI receives a `startTime` or `endTime` value that cannot be parsed as a valid timestamp (e.g. not ISO-8601, missing timezone, or not a number)
- WHEN input validation runs
- THEN the tool exits with `EXIT_INPUT_ERROR` and a diagnostic identifying which field is invalid and what format is expected

---

### USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-RUNTIME-29: Info-Level Log Must Show Initial Load, Per-Line State Transition, And Final Summary

- `WHO`: CLI operator running with `--logLevel info`
- `WHEN`: the operator wants to understand the attribution story from stderr without turning on the full volume of debug logging
- `WHAT`: show a three-phase info-level narrative covering start state, per-line transition hints, and final summary
- `WHY`: help the operator understand which lines changed ownership and what the final aggregate result means without switching to `--logLevel debug`
- `Story`: As a CLI operator running with `--logLevel info`, I want to see a three-phase narrative on stderr showing initial load state, per-line state transitions, and final summary, so that I can understand the full attribution story without switching to `--logLevel debug`.
- `Support`: `scope=stderr behavior` | `alg=primarily A` | `vcs=shared` | `tier=Fast target`
- `Status`: documented story record in USNG. Current executable test coverage is still an open gap.
- `Anchors`: `OperatorScenarioNG-...-29-AI-TO-HUMAN-SHAPE`, `OperatorScenarioNG-...-29-HUMAN-TO-AI-SHAPE`, `TestsNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-RUNTIME-29`

**AC-OPS-01** — *Start-state header on stderr*

- GIVEN the CLI runs with `--logLevel info`
- WHEN analysis starts
- THEN stderr emits an `[INFO]` line containing `repo=`, `branch=`, `window=`, and `endRevision=`

**AC-OPS-02** — *Per-line transition hint on ownership change*

- GIVEN the CLI runs with `--logLevel info` and a live line changes ownership relative to the parent revision
- WHEN that line is processed
- THEN stderr emits an `[INFO] TransitionHint` line containing `best_effort_transition=`

**AC-OPS-03** — *Final summary on stderr*

- GIVEN the CLI runs with `--logLevel info`
- WHEN analysis finishes
- THEN stderr emits an `[INFO]` summary line containing `totalCodeLines=`, `fullGeneratedCodeLines=`, `partialGeneratedCodeLines=`, `elapsed=`, and `costSeconds=`

**AC-OPS-04** — *Quiet mode suppresses transition and live-line lines*

- GIVEN the CLI runs with `--logLevel quiet`
- WHEN the analyzer would otherwise emit transition or live-line details
- THEN `TransitionHint` lines and `LiveLine` lines are suppressed

**AC-OPS-05** — *Debug mode shows all diagnostic tiers*

- GIVEN the CLI runs with `--logLevel debug`
- WHEN analysis progresses through loading, scanning, skips, and cache reuse
- THEN metadata-loading, file-scanning, out-of-window skip, and cached-protocol reuse diagnostics remain visible in addition to all info-level lines

**AC-OPS-06** — *AI-to-human transition scenario golden narrative*

- GIVEN the approved AI-to-human operator scenario is executed with `--logLevel info`
- WHEN the ownership transition is reported
- THEN stderr includes `best_effort_transition=100%-ai->human/unattributed`

**AC-OPS-07** — *Human-to-AI transition scenario golden narrative*

- GIVEN the approved human-to-AI operator scenario is executed with `--logLevel info`
- WHEN the ownership transition is reported
- THEN stderr includes `best_effort_transition=human/unattributed->100%-ai`

## Scope Expansion Under Complicated And Complex History

These stories extend the SHARED behavioral contracts of stories 02–07 (COMPLICATED attribution semantics) and stories 09–11 (COMPLEX scale/depth semantics) to the documentation-file family (SCOPE-B), the combined source scope (SCOPE-C), and the all-families scope (SCOPE-D). The contracts are identical across scopes; only the file-family selector changes.

### USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-B-36: Attribution Contract Applies Identically To Documentation Lines

- `WHO`: repository analyst
- `WHEN`: the target scope is the documentation-file family (SCOPE-B) and the history window contains rewrites, deletes, renames, or merges
- `WHAT`: apply the same attribution resolution rules as SCOPE-A to documentation-only lines
- `WHY`: the metric contract for attribution semantics must hold for documentation files the same way it holds for source files
- `Story`: As a repository analyst, I want the complete COMPLICATED-history attribution contract to apply to documentation lines (SCOPE-B), so that file family does not create a different rule set for human-vs-AI ownership resolution.
- `Support`: `scope=B doc baseline` | `alg=A` | `vcs=shared` | `tier=Fast`
- `Status`: Scope expansion of stories 02–07 to the documentation family. Behavioral contracts are identical to SCOPE-A; only the `scope` selector changes.
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-B-36`

**AC-01** — *Human rewrite of doc line clears prior AI attribution*

- GIVEN a documentation line was previously attributed to AI before `endTime`
- WHEN a human revision overwrites that line
- THEN attribution resets to the human revision

**AC-02** — *AI rewrite of doc line replaces prior human ownership*

- GIVEN a documentation line was previously attributed to a human before `endTime`
- WHEN a later AI revision overwrites that line
- THEN attribution becomes the AI revision

**AC-03** — *Deleted AI doc lines excluded from both numerator and denominator*

- GIVEN AI-attributed documentation lines existed in the window but are gone from the branch state at `endTime`
- WHEN the analyzer aggregates the SCOPE-B result
- THEN deleted AI doc lines are excluded from both numerator and denominator

**AC-04** — *Rename preserves doc-line attribution*

- GIVEN a documentation file is renamed or moved before `endTime` without changing content
- WHEN the analyzer resolves attribution for surviving lines
- THEN line attribution is preserved across the path-only change

**AC-05** — *Mixed multi-commit window resolves to one correct SCOPE-B result*

- GIVEN one requested window contains documentation commits with mixed human-only, AI-only, rewrite, and deletion paths
- WHEN the analyzer produces the SCOPE-B aggregate
- THEN each surviving doc line is resolved by its latest effective attribution

**AC-ALG-A-01** — *Algorithm A*

- GIVEN the approved scenario
- WHEN Algorithm A is executed
- THEN the result matches the approved NG golden output

---

### USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-C-37: Attribution Contract Applies Identically To Combined Source Lines

- `WHO`: repository analyst
- `WHEN`: the target scope is combined source code and comments (SCOPE-C) and the history window contains attribution edge cases
- `WHAT`: apply the same attribution resolution rules as SCOPE-A to combined source lines
- `WHY`: the metric contract must be consistent when comment lines are included in the source scope
- `Story`: As a repository analyst, I want the complete COMPLICATED-history attribution contract to apply to combined source-and-comment lines (SCOPE-C), so that adding comment lines to the scope does not change attribution resolution semantics.
- `Support`: `scope=C combined baseline` | `alg=A` | `vcs=shared` | `tier=Fast`
- `Status`: Scope expansion of stories 02–07 to the combined source scope. Behavioral contracts are identical to SCOPE-A; only the `scope` selector changes.
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-C-37`

**AC-01** — *Full attribution contract holds for combined source lines*

- GIVEN the target scope is SCOPE-C (code + comments) and the window contains human rewrites, AI rewrites, deletions, renames, and merges
- WHEN the analyzer resolves attribution for all surviving lines
- THEN each surviving line's attribution is determined by the same latest-effective-attribution rule as SCOPE-A, applied independently to code lines and comment lines alike

**AC-02** — *Deleted AI lines excluded across both code and comment sub-families*

- GIVEN AI-attributed code lines or comment lines existed in the window but are absent from the branch state at `endTime`
- WHEN the analyzer aggregates the SCOPE-C result
- THEN deleted AI lines from both sub-families are excluded from both numerator and denominator

**AC-03** — *Rename preserves attribution for combined source lines*

- GIVEN a source file is renamed or moved before `endTime` without changing its content
- WHEN the analyzer resolves attribution for surviving code and comment lines from that file
- THEN line attribution is preserved across the path-only change for both code and comment sub-families

**AC-ALG-A-01** — *Algorithm A*

- GIVEN the approved scenario
- WHEN Algorithm A is executed
- THEN the result matches the approved NG golden output

---

### USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-D-38: Attribution Contract Applies Identically To All-Families Scope

- `WHO`: repository analyst
- `WHEN`: the target scope covers all file families (SCOPE-D) and the history window contains attribution edge cases
- `WHAT`: apply the same attribution resolution rules as SCOPE-A to all file families collectively
- `WHY`: a single aggregate result across all families must resolve attribution consistently with per-family results
- `Story`: As a repository analyst, I want the complete COMPLICATED-history attribution contract to apply when SCOPE-D covers all file families together, so that combining families in one aggregate does not create attribution inconsistencies.
- `Support`: `scope=D all-families baseline` | `alg=A` | `vcs=shared` | `tier=Fast`
- `Status`: Scope expansion of stories 02–07 to all-families scope. Behavioral contracts are identical to SCOPE-A; only the `scope` selector changes.
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-D-38`

**AC-01** — *Full attribution contract holds across all families*

- GIVEN the target scope is SCOPE-D and the window contains attribution edge cases spanning source, documentation, and other file families
- WHEN the analyzer produces the all-families aggregate
- THEN each surviving line's attribution is resolved by the same latest-effective-attribution rule regardless of which family it belongs to

**AC-02** — *SCOPE-D aggregate is consistent with per-family sub-results*

- GIVEN attribution edge cases produce specific results for each constituent family scope
- WHEN the SCOPE-D aggregate is computed
- THEN its aggregate values are arithmetically consistent with summing the constituent family numerators and denominators

**AC-03** — *Rename preserves attribution across all file families*

- GIVEN a source or documentation file is renamed or moved before `endTime` without changing its content
- WHEN the analyzer resolves attribution for surviving lines from that file under SCOPE-D
- THEN line attribution is preserved across the path-only change regardless of which file family the file belongs to

**AC-ALG-A-01** — *Algorithm A*

- GIVEN the approved scenario
- WHEN Algorithm A is executed
- THEN the result matches the approved NG golden output

---

### USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-B-39: Large-Repository Scale Contract Holds For Documentation Lines

- `WHO`: repository analyst
- `WHEN`: the repository contains many documentation files and many live documentation lines, and the target scope is SCOPE-B
- `WHAT`: preserve result semantics for documentation lines at scale, consistent with story 09
- `WHY`: repository size must not degrade or change metric semantics for the documentation-file family
- `Story`: As a repository analyst, I want the COMPLEX-history scale contract for large repositories to apply to documentation lines (SCOPE-B), so that file family does not cause different scale behaviour.
- `Support`: `scope=B doc baseline` | `alg=A` | `vcs=shared` | `tier=Fast`
- `Status`: Scope expansion of stories 09–11 to the documentation family. Semantic contracts are identical to SCOPE-A; only the `scope` selector changes.
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-B-39`

**AC-01** — *Per-line attribution rules unchanged by documentation scope size*

- GIVEN the final live SCOPE-B snapshot at `endTime` spans many documentation files and many live lines
- WHEN the analyzer computes the final aggregate SCOPE-B result
- THEN repository size and documentation-file count do not change per-line attribution rules or the protocol shape of the final result

**AC-02** — *Deep history preserves latest effective attribution for doc lines*

- GIVEN surviving documentation lines at `endTime` come through long revision chains
- WHEN the analyzer resolves each surviving doc line
- THEN it uses latest effective attribution rather than earlier superseded revisions

**AC-03** — *Branch-heavy history preserves per-doc-line attribution*

- GIVEN many branches are merged into the target branch before `endTime` and surviving documentation lines originate from different merged branches
- WHEN the analyzer resolves the final SCOPE-B live state
- THEN each surviving doc line is preserved independently and ownership is not flattened to merge commits or branch identity alone

**AC-ALG-A-01** — *Algorithm A*

- GIVEN the approved scenario
- WHEN Algorithm A is executed
- THEN the result matches the approved NG golden output

---

### USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-C-40: Large-Repository Scale Contract Holds For Combined Source Lines

- `WHO`: repository analyst
- `WHEN`: the repository contains many source and comment lines, and the target scope is SCOPE-C
- `WHAT`: preserve result semantics for combined source lines at scale, consistent with story 09
- `WHY`: repository size must not degrade or change metric semantics for combined source scope
- `Story`: As a repository analyst, I want the COMPLEX-history scale contract for large repositories to apply to combined source-and-comment lines (SCOPE-C), so that combining code and comment families does not cause different scale behaviour.
- `Support`: `scope=C combined baseline` | `alg=A` | `vcs=shared` | `tier=Fast`
- `Status`: Scope expansion of stories 09–11 to the combined source scope. Semantic contracts are identical to SCOPE-A; only the `scope` selector changes.
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-C-40`

**AC-01** — *Scale contract holds for combined source and comment lines*

- GIVEN the final live SCOPE-C snapshot spans many source and comment lines from many files
- WHEN the analyzer produces the SCOPE-C aggregate
- THEN result semantics, per-line attribution rules, and protocol shape are identical to the SCOPE-A scale contract

**AC-02** — *Branch-heavy history preserves per-line attribution across SCOPE-C*

- GIVEN many branches are merged into the target branch and surviving lines span code and comment families
- WHEN the analyzer resolves the final SCOPE-C live state
- THEN per-line attribution is preserved independently regardless of file family

**AC-03** — *Deep history preserves latest effective attribution for combined source lines*

- GIVEN surviving code and comment lines at `endTime` come through long revision chains with many intermediate rewrites
- WHEN the analyzer resolves each surviving SCOPE-C line
- THEN it uses the latest effective attribution rather than earlier superseded revisions, applied independently to code lines and comment lines

**AC-ALG-A-01** — *Algorithm A*

- GIVEN the approved scenario
- WHEN Algorithm A is executed
- THEN the result matches the approved NG golden output

---

### USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-D-41: Large-Repository Scale Contract Holds For All-Families Scope

- `WHO`: repository analyst
- `WHEN`: the repository contains many files across all families, and the target scope is SCOPE-D
- `WHAT`: preserve result semantics for the all-families scope at scale, consistent with story 09
- `WHY`: the comprehensive all-families aggregate must remain correct and consistent at large repository scale
- `Story`: As a repository analyst, I want the COMPLEX-history scale contract for large repositories to apply to all file families together (SCOPE-D), so that the comprehensive aggregate result remains correct and consistent at production scale.
- `Support`: `scope=D all-families baseline` | `alg=A` | `vcs=shared` | `tier=Fast`
- `Status`: Scope expansion of stories 09–11 to all-families scope. Semantic contracts are identical to SCOPE-A; only the `scope` selector changes.
- `Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-D-41`

**AC-01** — *Scale contract holds across all families at once*

- GIVEN the final live SCOPE-D snapshot spans many files from source, documentation, and all other families
- WHEN the analyzer produces the all-families aggregate
- THEN result semantics, per-line attribution rules, and protocol shape are identical to the SCOPE-A scale contract

**AC-02** — *SCOPE-D aggregate remains consistent with per-family sub-results at scale*

- GIVEN a large repository produces well-defined results for each constituent family scope
- WHEN the SCOPE-D aggregate is computed against the same repository
- THEN its aggregate values are arithmetically consistent with summing the constituent family numerators and denominators

**AC-03** — *Deep history preserves latest effective attribution across all families*

- GIVEN surviving lines at `endTime` across all file families come through long revision chains with many intermediate rewrites
- WHEN the analyzer resolves each surviving SCOPE-D line
- THEN it uses the latest effective attribution rather than earlier superseded revisions, regardless of which file family the line belongs to

**AC-04** — *Branch-heavy history preserves per-line attribution across all families*

- GIVEN many branches are merged into the target branch before `endTime` and surviving lines originate from different merged branches across source, documentation, and other file families
- WHEN the analyzer resolves the final SCOPE-D live state
- THEN each surviving line is preserved independently and ownership is not flattened to merge commits or branch identity alone, regardless of file family

**AC-ALG-A-01** — *Algorithm A*

- GIVEN the approved scenario
- WHEN Algorithm A is executed
- THEN the result matches the approved NG golden output

---

### USNG-REPO-SVN-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-42: SVN Path-Copy Branching Must Not Distort Attribution Lineage

- `WHO`: repository analyst
- `WHEN`: the SVN repository uses path-based branching (copy-then-modify) inside the measurement window
- `WHAT`: track line attribution through path-copy branch origins correctly, not from the copy operation timestamp
- `WHY`: SVN branches through file-system `svn copy`, not references; a copy-then-modify pattern is the canonical SVN branch mechanic and must not flatten attribution to the copy act itself
- `Story`: As a repository analyst using an SVN repository, I want path-copy branches to trace attribution back to the original lines on the trunk or source branch, so that the copy operation itself is never treated as the attribution origin.
- `Support`: `scope=A baseline` | `alg=A` | `vcs=svn-local; path-based branching` | `tier=Fast`
- `Status`: SVN-specific COMPLICATED behavior. Git uses reference branches and git-follow; SVN uses path-copy semantics. This story has no Git-LOCAL equivalent — it is not covered by the SHARED COMPLICATED stories 02–07.
- `Anchors`: `TestdataNG-REPO-SVN-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-42`

**AC-01** — *Path-copy origin is tracked, not the copy commit*

- GIVEN an SVN branch is created by `svn copy trunk@R branches/feature` at revision R
- WHEN the analyzer resolves attribution for lines present on `branches/feature` that were unchanged since the copy
- THEN those lines retain their original trunk attribution rather than receiving an attribution timestamp of revision R

**AC-02** — *Lines modified after path-copy carry the modification's attribution*

- GIVEN a line was copied from trunk via `svn copy` and then overwritten on the feature branch before `endTime`
- WHEN the analyzer resolves that line's attribution
- THEN it uses the post-copy modification's attribution, not the original trunk attribution

**AC-03** — *Merged path-copy branch does not collapse attribution to the merge revision*

- GIVEN a path-copy branch is merged back to trunk before `endTime`
- WHEN the analyzer resolves attribution for surviving merged lines
- THEN each line retains the attribution from its effective originating revision, not from the merge commit at trunk

**AC-04** — *Nested path-copy chains preserve deepest effective attribution*

- GIVEN a branch was itself created from another path-copy branch (nested copy)
- WHEN the analyzer walks the revision history
- THEN it follows the copy chain to the deepest effective modifying revision, not stopping at an intermediate copy revision

**AC-ALG-A-01** — *Algorithm A*

- GIVEN the approved scenario
- WHEN Algorithm A is executed
- THEN the result matches the approved NG golden output

---

## Remote Topology Contract Stories

These stories define the contract boundary for remote repository access and provider-side metadata topology. All SHARED behavioral stories (stories 01–11, 14–17, 36–41) apply to remote topologies through delegation. Remote topology stories add only the access-path boundary contracts that are unique to the remote case.

### USNG-REPO-GIT-REMOTE-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-A-30: Remote Git Identity Must Not Change The Measurement Contract

- `WHO`: repository analyst or CLI operator
- `WHEN`: the repository is addressed through a remote Git identity (clone URL, remote tracking branch, or logical remote name) while the supported runtime resolves through an available local checkout or delegated fetch path
- `WHAT`: keep the measurement contract identical to the equivalent Git local access
- `WHY`: analysts should not need to know whether the runtime resolved through a local clone or a remote call — entry point is an addressing concern, not a contract change
- `Story`: As a repository analyst, I want addressing a repository through a remote Git identity to produce the same measurement contract as Git local access, so that operator entry point does not change metric semantics.
- `Support`: `scope=A baseline` | `alg=A` | `vcs=git remote-identity resolution` | `tier=Fast`
- `Status`: Remote Git identity is an addressing concern resolved by the runtime. All SHARED behavioral stories for HISTORY-COMPLICATED (02–07, 36–38) and HISTORY-COMPLEX (09–11, 39–41) apply to this topology through delegation. This story adds only the access-path boundary contracts unique to the remote case.
- `Anchors`: `TestsNG-REPO-GIT-REMOTE-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-A-30`

**AC-01** — *Remote identity does not change metric output contract*

- GIVEN the same repository content is addressed through a remote Git identity instead of a direct local path
- WHEN the measurement runs through the supported runtime resolution path
- THEN the result is protocol-shaped and contract-identical to addressing the same content through a local Git checkout

**AC-02** — *Unresolvable remote identity fails with explicit diagnostic*

- GIVEN the remote Git identity cannot be resolved (network unreachable, invalid remote, missing credentials)
- WHEN the CLI or API executes
- THEN it exits with a clear diagnostic naming the unresolvable remote address rather than silently producing an empty or partial result

---

### USNG-REPO-SVN-REMOTE-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-A-31: Remote SVN URL Must Not Change The Measurement Contract

- `WHO`: repository analyst or CLI operator
- `WHEN`: the SVN repository is addressed through a remote URL (`svn+ssh://`, `https://`, `svn://`) rather than a `file:///` path
- `WHAT`: keep the measurement contract identical to the equivalent SVN local access
- `WHY`: SVN remote access is an access-path concern — changing it should not change metric semantics or output structure
- `Story`: As a repository analyst, I want addressing a repository through a remote SVN URL to produce the same measurement contract as SVN local (`file:///`) access, so that SVN access method does not change metric semantics.
- `Support`: `scope=A baseline` | `alg=A` | `vcs=svn remote URL resolution` | `tier=Fast`
- `Status`: Remote SVN URL is an access-path concern resolved by the runtime. All SHARED behavioral stories for HISTORY-COMPLICATED (02–07, 36–38) and HISTORY-COMPLEX (09–11, 39–41) plus the SVN-specific COMPLICATED contract (42) apply to this topology through delegation. This story adds only the access-path boundary contracts unique to the remote case.
- `Anchors`: `TestsNG-REPO-SVN-REMOTE-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-A-31`

**AC-01** — *Remote SVN URL does not change metric output contract*

- GIVEN the same repository content is addressed through a remote SVN URL instead of a `file:///` path
- WHEN the measurement runs through the supported SVN runtime path
- THEN the result is protocol-shaped and contract-identical to addressing the same content through a local SVN path

**AC-02** — *Unresolvable SVN remote fails with explicit diagnostic*

- GIVEN the remote SVN URL cannot be resolved (authentication failure, network error, invalid URL scheme)
- WHEN the CLI or API executes
- THEN it exits with a clear diagnostic naming the SVN remote access failure rather than silently producing an empty or partial result

---

### USNG-REPO-SHARED-GENCODEDESC-REMOTE-HISTORY-SIMPLE-SCOPE-A-32: Provider-Side genCodeDesc Metadata Must Not Change The Measurement Contract

- `WHO`: repository analyst
- `WHEN`: genCodeDesc metadata is retrieved from a provider service or external API rather than read from a local directory
- `WHAT`: keep the measurement contract the same regardless of where metadata originates
- `WHY`: the measurement result (weighted AI ratio) should not depend on whether metadata came from a local cache or a remote service
- `Story`: As a repository analyst, I want the measurement result to be contract-identical whether genCodeDesc metadata comes from a local directory or an external provider service, so that metadata topology does not change metric semantics.
- `Support`: `scope=A baseline` | `alg=A` | `vcs=shared` | `tier=Fast`
- `Status`: Provider-side metadata retrieval is a metadata-topology concern. All SHARED behavioral stories for HISTORY-COMPLICATED (02–07, 36–38) and HISTORY-COMPLEX (09–11, 39–41) apply to this topology through delegation. This story adds only the metadata-provider boundary contracts unique to the remote-provider case.
- `Anchors`: `TestsNG-REPO-SHARED-GENCODEDESC-REMOTE-HISTORY-SIMPLE-SCOPE-A-32`

**AC-01** — *Remote genCodeDesc metadata produces contract-identical result*

- GIVEN genCodeDesc records are fetched from a remote provider indexed by `repoURL + repoBranch + revisionId`
- WHEN the analyzer aggregates the live-snapshot result
- THEN the result is protocol-shaped and contract-identical to the equivalent local-metadata analysis

**AC-02** — *Provider fetch failure is explicit*

- GIVEN a remote genCodeDesc provider returns an error, timeout, or partial response for required records
- WHEN the analyzer attempts to fetch those records
- THEN it fails with a clear diagnostic identifying the provider failure rather than treating missing records as human attribution

**AC-03** — *Partial provider response treated as missing records, not silent human attribution*

- GIVEN a remote genCodeDesc provider successfully returns records for some revisions but returns no record for one or more other required revisions in the same run
- WHEN the analyzer processes the partial response
- THEN the missing revisions' lines are counted as human-unattributed (same as AC-03 of story 01) and the partial gap is observable through `--logLevel debug`, rather than being silently merged into AI attribution

## Traceability Appendix

Use this appendix for audit, comparison, or search that requires earlier family-based IDs (`USNG-LS-*`, `USNG-PA-*`, etc.) or legacy `US-*` references.

- Live-snapshot lineage: `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-01` -> previous `USNG-LS-01` -> `US-1`; `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-02` -> previous `USNG-LS-02` (was `USNG-REPO-GIT-LOCAL-…-02`) -> `US-2`; `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-03` -> previous `USNG-LS-03` (was `USNG-REPO-GIT-LOCAL-…-03`) -> `US-3`; `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-04` -> previous `USNG-LS-04` (was `USNG-REPO-GIT-LOCAL-…-04`) -> `US-4`; `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-05` -> previous `USNG-LS-05` (was `USNG-REPO-GIT-LOCAL-…-05`) -> `US-5`; `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-06` -> previous `USNG-LS-06` (was `USNG-REPO-GIT-LOCAL-…-06`) -> `US-7`; `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-A-07` -> previous `USNG-LS-07` (was `USNG-REPO-GIT-LOCAL-…-07`) -> `US-8`; `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-08` -> previous `USNG-LS-08` -> `US-9`; `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-09` -> previous `USNG-LS-09` (was `USNG-REPO-GIT-LOCAL-…-09`) -> `US-10`; `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-10` -> previous `USNG-LS-10` (was `USNG-REPO-GIT-LOCAL-…-10`) -> `US-11`; `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-11` -> previous `USNG-LS-11` (was `USNG-REPO-GIT-LOCAL-…-11`) -> `US-12`
- Production-gate lineage: `USNG-REPO-GIT-LOCAL-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-12` -> previous `USNG-PG-01` -> `US-13`; `USNG-REPO-SVN-LOCAL-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-13` -> previous `USNG-PG-02` -> `US-14`
- Scope-contract lineage: `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-B-14` -> previous `USNG-SC-01` -> `US-20`; `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-C-15` -> previous `USNG-SC-02` -> `US-21`; `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-D-16` -> previous `USNG-SC-03` -> `US-22`; `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-ALL-17` -> previous `USNG-SC-04` -> `US-23`
- Algorithm-B scope lineage: `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-B-18` -> previous `USNG-AB-01` -> `US-24`; `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-C-19` -> previous `USNG-AB-02` -> `US-25`; `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-D-20` -> previous `USNG-AB-03` -> `US-26`
- Period-added lineage: `USNG-REPO-GIT-LOCAL-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-21` -> previous `USNG-PA-01` -> `US-6`; `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-A-22` -> previous `USNG-PA-02` -> `US-15`; `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-23` -> previous `USNG-PA-03` -> `US-16`; `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-24` -> previous `USNG-PA-04` -> `US-17`; `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-25` -> previous `USNG-PA-05` -> `US-18`; `USNG-REPO-SVN-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-A-26` -> previous `USNG-PA-06` -> `US-19`
- Cross-algorithm, hardening, and operator lineage: `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-ALL-27` -> previous `USNG-CA-01` -> `US-27`; `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-RUNTIME-28` -> previous `USNG-CA-02` -> `US-28`; `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-RUNTIME-29` -> previous `USNG-CA-03` -> `US-29`
- New USNG-only stories (no old-US equivalent): `USNG-REPO-GIT-REMOTE-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-A-30` (remote Git contract); `USNG-REPO-SVN-REMOTE-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-A-31` (remote SVN contract); `USNG-REPO-SHARED-GENCODEDESC-REMOTE-HISTORY-SIMPLE-SCOPE-A-32` (remote genCodeDesc contract); `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-B-33` (period-added SCOPE-B); `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-C-34` (period-added SCOPE-C); `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-D-35` (period-added SCOPE-D); `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-B-36` (COMPLICATED attribution contract for documentation lines); `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-C-37` (COMPLICATED attribution contract for combined source lines); `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-D-38` (COMPLICATED attribution contract for all-families scope); `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-B-39` (COMPLEX scale contract for documentation lines); `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-C-40` (COMPLEX scale contract for combined source lines); `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-D-41` (COMPLEX scale contract for all-families scope); `USNG-REPO-SVN-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-42` (SVN path-copy branching attribution contract)
