# AggregateGenCodeDesc USNG (UserStoryNG)

## Purpose

This document defines the authoritative next-generation user stories and acceptance criteria for AggregateGenCodeDesc.

It works with the current base documents:

- `README.md` remains the product and contract base.
- `README_UserGuide.md` remains the operator and runtime base.

Within this repository, `UserStoryNG` may be abbreviated as `USNG`.

## USNG Story Rules

1. Make every story explicit in full `5W1H` form: `WHO`, `WHEN`, `WHERE`, `WHAT`, `WHY`, and `HOW`.
2. Keep the classic user-story sentence as the primary story form: `As ... I want ... so that ...`.
3. Keep acceptance criteria in classic `GIVEN ... WHEN ... THEN ...` form.
4. Keep current support boundaries explicit instead of hiding partial support.
5. Keep scenario anchors visible so each story can point to NG verification anchors without binding the story layer to implementation paths.

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

USNG now uses a 4D story index as the primary naming rule. Old family buckets such as `LS`, `PA`, `PG`, `SC`, `AB`, and `CA` are no longer part of the normative story ID.

The primary reading order is:

1. repository topology
2. `genCodeDesc` topology
3. repository history complexity
4. scope

`Algorithm A/B` still matters, but it is carried by `Support Coordinates`, `Support Snapshot`, and the acceptance clauses rather than by the story ID itself.

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
- logical scenario anchors such as `TestdataNG-*`, `TestsNG-*`, and `OperatorScenarioNG-*` remain a separate layer, but they now reuse the owning story's 4D core and add only optional variant suffixes such as `-GIT`, `-SVN`, `-SVN-PARITY`, or `-AI-TO-HUMAN-SHAPE`

## UserGuide Runtime Story Map

This section is now the primary navigation map.

### Git Local Repository + genCodeDesc Local

- `HISTORY-SIMPLE / SCOPE A`: local baseline measurement cards and the single-branch period-added baseline
- `HISTORY-SIMPLE / SCOPE B/C/D`: scope-expansion and Algorithm B scope-support cards
- `HISTORY-COMPLICATED / SCOPE A`: overwrite, deletion, rename, mixed-window, and merge-aware cards
- `HISTORY-COMPLEX / SCOPE A`: large-repository, deep-history, many-branch, and production-scale Git cards
- `SCOPE-RUNTIME`: the Git-local runtime hardening card

### Git Local Repository + genCodeDesc Shared

- shared metadata-topology contracts for the baseline live-snapshot story, the baseline period-added contract, and the Git production-scale gate

### Git Remote-Identity Repository + genCodeDesc Local

- the story contract follows the same measurement cards as Git local
- the distinction here is operator entry and runtime addressing rather than a different contract

### SVN Local Repository + genCodeDesc Local

- `HISTORY-SIMPLE / SCOPE A`: shared baseline and parity cards plus the defended Algorithm B SVN subset
- `HISTORY-COMPLEX / SCOPE A`: the production-scale SVN gate
- `SCOPE B/C/D`: use only the cards that explicitly declare shared or SVN-valid support

### SVN Remote Repository + genCodeDesc Local

- the story contract follows the same measurement cards as SVN local
- the distinction here is remote repository access rather than `file:///` entry

### Any Repository Topology + genCodeDesc Remote

- use the `GENCODEDESC-SHARED` or `GENCODEDESC-REMOTE` cards when provider-side metadata retrieval is the operator concern
- the baseline live-snapshot contract, baseline period-added contract, and production-scale gates are the main anchors for that view

## How To Read This File

Every rewritten story card uses the same shape:

- `NG Story ID`: the 4D primary identifier in `REPO -> GENCODEDESC -> HISTORY -> SCOPE -> sequence` order
- `WHO`: the user role or operator role
- `WHEN`: the trigger or business moment
- `WHERE`: the repository, runtime, or scope context in which the story matters
- `WHAT`: what that role wants from the analyzer
- `WHY`: why the outcome matters to that role
- `HOW`: the supported path, support coordinates, or evidence shape that makes the story concrete
- `Story Sentence`: the classic `As a ... I want ... so that ...` form
- `Support Coordinates`: the scope, algorithm, VCS, and verification tier that define the currently supported cells
- `Support Snapshot`: current support status without overclaiming
- `Scenario Anchors`: logical NG verification anchors rather than concrete filesystem paths
- `Acceptance Criteria`: the target is the classic `GIVEN ... WHEN ... THEN ...` contract

In practice inside this file:

- Start with the `UserGuide Runtime Story Map` to locate the operator-facing runtime bucket.
- Then read the 4D prefix of the `NG Story ID` to confirm repository topology, metadata topology, history complexity, and scope.
- Then read the detailed story cards below, which remain the normative contract layer.
- The detailed stories below are grouped only to keep a long behavior document scannable; that grouping is secondary, and the primary entry remains the UserGuide runtime view above.
- `Scenario Anchors` should be read as logical `TestdataNG-*`, `TestsNG-*`, or `OperatorScenarioNG-*` anchors first; when a concrete repository path is needed, resolve them through the corresponding NG asset README.
- Traceability lookups now live only in the appendix at the end of this file.
- `WHO`, `WHEN / Scenario`, `WHAT`, and `WHY` appear explicitly in each story card.
- `WHERE` is usually captured by the story situation plus scenario anchors.
- `Support Coordinates` capture algorithm, VCS, and verification tier on top of the 4D ID rather than replacing it.
- `HOW` is usually captured by support coordinates, support snapshot, and executable anchors.
- The classic story sentence remains the canonical story statement, and the 5W1H fields enrich it instead of replacing it.
- The acceptance sections below use story-local clause IDs such as `AC-01`, `AC-ALG-A-01`, and `AC-ALG-B-01`, with explicit `GIVEN / WHEN / THEN` blocks.

## Navigation

### 4D View

- Repository topology: `REPO-GIT-LOCAL`, `REPO-GIT-REMOTE`, `REPO-SVN-LOCAL`, `REPO-SVN-REMOTE`, `REPO-SHARED`
- Metadata topology: `GENCODEDESC-LOCAL`, `GENCODEDESC-REMOTE`, `GENCODEDESC-SHARED`
- History complexity: `HISTORY-SIMPLE`, `HISTORY-COMPLICATED`, `HISTORY-COMPLEX`
- Scope: `SCOPE-A`, `SCOPE-B`, `SCOPE-C`, `SCOPE-D`, `SCOPE-ALL`, `SCOPE-RUNTIME`
- Algorithm: stays in `Support Coordinates` and is not encoded in the story ID

## Detailed Story Cards

## Live-Snapshot Contract Stories

These stories describe the main live-snapshot metric: the AI ratio among live source-code lines whose current version changed inside the requested window.

### USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-01: Calculate Weighted AI Ratio For Live Changed Source Code In A Requested Time Window

- `WHO`: repository analyst
- `WHEN / Scenario`: when the analyst queries one repository branch for one requested window `startTime~endTime` and needs the final live-snapshot answer at `endTime`
- `WHAT`: calculate the weighted AI ratio for live source-code lines whose current version changed inside the requested window
- `WHY`: know how much of the current live changed source code is attributable to AI
- `Story Sentence`: As a repository analyst, I want to calculate the weighted AI ratio for live source-code lines whose current version falls in a requested period `startTime~endTime`, so that I can know how much of the current live changed source code is attributable to AI.
- `Support Coordinates`: `scope=A baseline`, `algorithms=A and B`, `vcs=git and svn`, `tier=Fast`
- `Support Snapshot`: `Algorithm A` covers Git and SVN for the approved baseline scenarios of this story. `Algorithm B` covers narrow Git and SVN live-snapshot replay for the same approved story-01 scenarios.
- `Scenario Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-01-GIT`, `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-01-SVN`

Acceptance Criteria

**`AC-01`**

- `GIVEN`: a query `repo + branch + startTime + endTime` for the live-snapshot metric
- `WHEN`: the analyzer computes the final result at `endTime`
- `THEN`: it returns exactly one repository-level final result describing the AI ratio among live source-code lines whose current version was added or modified in `startTime~endTime` as of `endTime`

**`AC-02`**

- `GIVEN`: external `genCodeDesc` records are stored outside the repository and indexed by `repoURL + repoBranch + revisionId`
- `WHEN`: the analyzer discovers in-scope origin revisions from the final live snapshot
- `THEN`: it fetches and uses the matching metadata records during aggregation

**`AC-03`**

- `GIVEN`: the analysis succeeds for the requested repository window
- `WHEN`: the final result is returned or serialized
- `THEN`: it remains protocol-shaped and contains repository identity in `REPOSITORY` and aggregate result values in `SUMMARY`

**`AC-04`**

- `GIVEN`: an implementation path claims support for `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-01`
- `WHEN`: that path is validated against an approved scenario
- `THEN`: the produced result matches the approved golden output for that scenario

**`AC-ALG-A-01`**

- `GIVEN`: the approved `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-01-GIT` scenario
- `WHEN`: the current `Algorithm A` path is executed
- `THEN`: the produced result matches the approved NG golden output for that scenario

**`AC-ALG-A-02`**

- `GIVEN`: the approved `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-01-SVN` scenario
- `WHEN`: the current `Algorithm A` SVN path is executed on the same baseline metric
- `THEN`: the same observable `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-01` contract is preserved

**`AC-ALG-B-01`**

- `GIVEN`: the approved `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-01-GIT` replay scenario
- `WHEN`: the current narrow `Algorithm B` Git live-snapshot path is executed
- `THEN`: the produced result matches the approved NG golden output for that scenario

**`AC-ALG-B-02`**

- `GIVEN`: the approved `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-01-SVN` replay scenario
- `WHEN`: the current narrow `Algorithm B` SVN live-snapshot path is executed
- `THEN`: the produced result matches the approved NG golden output for that scenario

**`AC-ALG-B-03`**

- `GIVEN`: the current `Algorithm B` evidence for `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-01`
- `WHEN`: the support boundary is documented or discussed
- `THEN`: it is described as narrow live-snapshot replay support for the approved story-01 scenarios, not as a blanket replacement for `Algorithm A` history handling

### USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-02: Human Rewrite Removes Prior AI Attribution

- `WHO`: repository analyst
- `WHEN / Scenario`: when a human revision overwrites code that had previously been attributed to AI before `endTime`
- `WHAT`: reset effective attribution to the newer human revision
- `WHY`: prevent old AI ownership from staying attached to overwritten code
- `Story Sentence`: As a repository analyst, I want a human rewrite of a previously AI-generated line to reset attribution to the newer human revision, so that old AI ownership does not remain attached to overwritten code.
- `Support Coordinates`: `scope=A baseline`, `algorithms=A and B`, `vcs=shared story with current narrow B Git slice`, `tier=Fast`
- `Support Snapshot`: `Algorithm A` evidence exists. `Algorithm B` evidence is narrow Git live-snapshot replay for the approved scenario of this story.
- `Scenario Anchors`: `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-02`

Acceptance Criteria

**`AC-01`**

- `GIVEN`: code previously attributed to AI is superseded by later human revisions before `endTime`
- `WHEN`: the final record is produced for the live changed source-code set at `endTime`
- `THEN`: it reflects the newer repository state and does not preserve outdated AI ownership

**`AC-02`**

- `GIVEN`: the analysis succeeds for the requested repository window
- `WHEN`: the final result is returned or serialized
- `THEN`: it remains protocol-shaped and contains repository identity in `REPOSITORY` and aggregate values in `SUMMARY`

**`AC-03`**

- `GIVEN`: an implementation path claims support for `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-02`
- `WHEN`: that path is validated against an approved scenario
- `THEN`: the produced result matches the approved golden output for that scenario

**`AC-ALG-A-01`**

- `GIVEN`: the approved `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-02` scenario
- `WHEN`: the current `Algorithm A` path is executed
- `THEN`: the produced result matches the approved NG golden output for that scenario

**`AC-ALG-B-01`**

- `GIVEN`: the approved `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-02` replay scenario
- `WHEN`: the current narrow `Algorithm B` Git live-snapshot path is executed
- `THEN`: the produced result matches the approved NG golden output for that scenario

**`AC-ALG-B-02`**

- `GIVEN`: the current `Algorithm B` evidence for `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-02`
- `WHEN`: the support boundary is documented or discussed
- `THEN`: it is described as narrow Git live-snapshot replay support for the approved scenario of this story, not as blanket support across other complicated-history shapes

### USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-03: AI Rewrite Replaces Prior Human Ownership

- `WHO`: repository analyst
- `WHEN / Scenario`: when a later AI revision overwrites a line that had previously been human-authored before `endTime`
- `WHAT`: make the later AI rewrite the effective attribution source
- `WHY`: ensure the live changed source code at `endTime` reflects the latest AI contribution
- `Story Sentence`: As a repository analyst, I want a later AI rewrite of a human line to become the effective attribution source, so that the live changed source code at `endTime` reflects the latest AI contribution.
- `Support Coordinates`: `scope=A baseline`, `algorithms=A and B`, `vcs=shared story with current narrow B Git slice`, `tier=Fast`
- `Support Snapshot`: `Algorithm A` evidence exists. `Algorithm B` evidence is narrow Git live-snapshot replay for the approved scenario of this story.
- `Scenario Anchors`: `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-03`

Acceptance Criteria

**`AC-01`**

- `GIVEN`: later revisions introduce new AI-attributed code before `endTime`
- `WHEN`: the final record is produced for the live changed source-code state at `endTime`
- `THEN`: it reflects that newer AI contribution

**`AC-02`**

- `GIVEN`: the analysis succeeds for the requested repository window
- `WHEN`: the final result is returned or serialized
- `THEN`: it remains protocol-shaped and contains repository identity in `REPOSITORY` and aggregate values in `SUMMARY`

**`AC-03`**

- `GIVEN`: an implementation path claims support for `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-03`
- `WHEN`: that path is validated against an approved scenario
- `THEN`: the produced result matches the approved golden output for that scenario

**`AC-ALG-A-01`**

- `GIVEN`: the approved `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-03` scenario
- `WHEN`: the current `Algorithm A` path is executed
- `THEN`: the produced result matches the approved NG golden output for that scenario

**`AC-ALG-B-01`**

- `GIVEN`: the approved `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-03` replay scenario
- `WHEN`: the current narrow `Algorithm B` Git live-snapshot path is executed
- `THEN`: the produced result matches the approved NG golden output for that scenario

**`AC-ALG-B-02`**

- `GIVEN`: the current `Algorithm B` evidence for `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-03`
- `WHEN`: the support boundary is documented or discussed
- `THEN`: it is described as narrow Git live-snapshot replay support for the approved scenario of this story, not as blanket support across other complicated-history shapes

### USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-04: Deleted AI Lines Must Not Count

- `WHO`: repository analyst
- `WHEN / Scenario`: when AI-generated lines existed earlier in the window but are gone from the branch state at `endTime`
- `WHAT`: exclude deleted AI lines from both numerator and denominator
- `WHY`: keep the result about the current live changed snapshot only
- `Story Sentence`: As a repository analyst, I want deleted AI-generated lines to disappear from both numerator and denominator, so that the result reflects only the current live changed source-code snapshot.
- `Support Coordinates`: `scope=A baseline`, `algorithms=A and B`, `vcs=shared story with current narrow B Git slice`, `tier=Fast`
- `Support Snapshot`: `Algorithm A` evidence exists. `Algorithm B` evidence is narrow Git live-snapshot replay for the approved scenario of this story.
- `Scenario Anchors`: `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-04`

Acceptance Criteria

**`AC-01`**

- `GIVEN`: earlier AI-attributed code no longer exists in the branch state at `endTime`
- `WHEN`: the final record is produced for the live changed source-code result
- `THEN`: that deleted code is excluded from the result

**`AC-02`**

- `GIVEN`: the analysis succeeds for the requested repository window
- `WHEN`: the final result is returned or serialized
- `THEN`: it remains protocol-shaped and contains repository identity in `REPOSITORY` and aggregate values in `SUMMARY`

**`AC-03`**

- `GIVEN`: an implementation path claims support for `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-04`
- `WHEN`: that path is validated against an approved scenario
- `THEN`: the produced result matches the approved golden output for that scenario

**`AC-ALG-A-01`**

- `GIVEN`: the approved `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-04` scenario
- `WHEN`: the current `Algorithm A` path is executed
- `THEN`: the produced result matches the approved NG golden output for that scenario

**`AC-ALG-B-01`**

- `GIVEN`: the approved `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-04` replay scenario
- `WHEN`: the current narrow `Algorithm B` Git live-snapshot path is executed
- `THEN`: the produced result matches the approved NG golden output for that scenario

**`AC-ALG-B-02`**

- `GIVEN`: the current `Algorithm B` evidence for `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-04`
- `WHEN`: the support boundary is documented or discussed
- `THEN`: it is described as narrow Git live-snapshot replay support for the approved scenario of this story, not as blanket support across other complicated-history shapes

### USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-05: Rename Must Preserve Attribution Lineage

- `WHO`: repository analyst
- `WHEN / Scenario`: when files are renamed or moved before `endTime` without changing their effective content contribution
- `WHAT`: preserve line attribution across path-only history changes
- `WHY`: prevent rename-only changes from distorting the final live changed source-code ratio
- `Story Sentence`: As a repository analyst, I want file rename or move operations to preserve line attribution when content does not change, so that the final live changed source-code ratio is not distorted by path-only history changes.
- `Support Coordinates`: `scope=A baseline`, `algorithms=A and B`, `vcs=shared story with current narrow B Git slice`, `tier=Fast`
- `Support Snapshot`: `Algorithm A` evidence exists. `Algorithm B` evidence is narrow Git live-snapshot replay for the approved scenario of this story.
- `Scenario Anchors`: `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-05`

Acceptance Criteria

**`AC-01`**

- `GIVEN`: files are renamed or moved before `endTime` without changing their effective contribution
- `WHEN`: the final record is produced for the live changed source-code set at `endTime`
- `THEN`: it remains stable under path-only history changes

**`AC-02`**

- `GIVEN`: the analysis succeeds for the requested repository window
- `WHEN`: the final result is returned or serialized
- `THEN`: it remains protocol-shaped and contains repository identity in `REPOSITORY` and aggregate values in `SUMMARY`

**`AC-03`**

- `GIVEN`: an implementation path claims support for `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-05`
- `WHEN`: that path is validated against an approved scenario
- `THEN`: the produced result matches the approved golden output for that scenario

**`AC-ALG-A-01`**

- `GIVEN`: the approved `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-05` scenario
- `WHEN`: the current `Algorithm A` path is executed
- `THEN`: the produced result matches the approved NG golden output for that scenario

**`AC-ALG-B-01`**

- `GIVEN`: the approved `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-05` replay scenario
- `WHEN`: the current narrow `Algorithm B` Git live-snapshot path is executed
- `THEN`: the produced result matches the approved NG golden output for that scenario

**`AC-ALG-B-02`**

- `GIVEN`: the current `Algorithm B` evidence for `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-05`
- `WHEN`: the support boundary is documented or discussed
- `THEN`: it is described as narrow Git live-snapshot replay support for the approved scenario of this story, not as blanket support across other complicated-history shapes

### USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-06: Resolve Mixed Multi-Commit History In One Requested Window

- `WHO`: repository analyst
- `WHEN / Scenario`: when one requested window contains many commits with mixed human-only, AI-only, rewrite, and deletion paths
- `WHAT`: resolve each surviving line by its latest effective attribution inside the window
- `WHY`: keep one final result correct even when history inside the window is mixed and complex
- `Story Sentence`: As a repository analyst, I want one requested window to correctly resolve mixed line histories across many commits, so that the final result remains correct when human-only lines, AI-only lines, human-then-AI rewrites, AI-then-human rewrites, and deleted AI lines all appear in the same period.
- `Support Coordinates`: `scope=A baseline`, `algorithms=A and B`, `vcs=shared story with current narrow B Git slice`, `tier=Fast`
- `Support Snapshot`: `Algorithm A` evidence exists. `Algorithm B` evidence is narrow Git live-snapshot replay for the approved scenario of this story.
- `Scenario Anchors`: `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-06`

Acceptance Criteria

**`AC-01`**

- `GIVEN`: multiple commits inside the requested window contain mixed ownership transitions across different live lines
- `WHEN`: the analyzer resolves the live changed source-code set at `endTime`
- `THEN`: it still produces exactly one final record using the latest effective attribution of each surviving line

**`AC-02`**

- `GIVEN`: a surviving line passes through a long chain of intermediate revisions inside the window
- `WHEN`: the analyzer resolves that live line at `endTime`
- `THEN`: it uses the latest effective live attribution without leaking superseded intermediate ownership into the final result

**`AC-03`**

- `GIVEN`: the analysis succeeds for the requested repository window
- `WHEN`: the final result is returned or serialized
- `THEN`: it remains protocol-shaped and contains repository identity in `REPOSITORY` and aggregate values in `SUMMARY`

**`AC-04`**

- `GIVEN`: an implementation path claims support for `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-06`
- `WHEN`: that path is validated against an approved scenario
- `THEN`: the produced result matches the approved golden output for that scenario

**`AC-ALG-A-01`**

- `GIVEN`: the approved `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-06` scenario
- `WHEN`: the current `Algorithm A` path is executed
- `THEN`: the produced result matches the approved NG golden output for that scenario

**`AC-ALG-B-01`**

- `GIVEN`: the approved `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-06` replay scenario
- `WHEN`: the current narrow `Algorithm B` Git live-snapshot path is executed
- `THEN`: the produced result matches the approved NG golden output for that scenario

**`AC-ALG-B-02`**

- `GIVEN`: the current `Algorithm B` evidence for `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-06`
- `WHEN`: the support boundary is documented or discussed
- `THEN`: it is described as narrow Git live-snapshot replay support for the approved scenario of this story, not as blanket support across other complicated-history shapes

### USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-07: Merge Commit Must Preserve Effective Attribution

- `WHO`: repository analyst
- `WHEN / Scenario`: when merged branches bring human and AI contributions into the target branch before `endTime`
- `WHAT`: preserve the effective attribution of each surviving line through merges
- `WHY`: prevent merge commits from resetting ownership or flattening provenance
- `Story Sentence`: As a repository analyst, I want merged branch content to preserve the effective attribution of surviving lines, so that a merge operation does not incorrectly reset line ownership to the merge commit itself.
- `Support Coordinates`: `scope=A baseline`, `algorithms=A and B`, `vcs=shared story with current narrow B Git slice`, `tier=Fast`
- `Support Snapshot`: `Algorithm A` evidence exists. `Algorithm B` evidence is narrow Git live-snapshot replay for the approved scenario of this story.
- `Scenario Anchors`: `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-07`

Acceptance Criteria

**`AC-01`**

- `GIVEN`: a merge commit brings together earlier human and AI-attributed changes before `endTime`
- `WHEN`: the final record is produced for the live changed source-code set at `endTime`
- `THEN`: it uses the effective attribution of surviving merged lines rather than treating the merge commit as a blanket origin

**`AC-02`**

- `GIVEN`: multiple branches are merged before `endTime` and surviving lines originate from different merged branches
- `WHEN`: the analyzer resolves the final live state
- `THEN`: it preserves each surviving line independently and does not collapse ownership to merge commits or final branch identity alone

**`AC-03`**

- `GIVEN`: the analysis succeeds for the requested repository window
- `WHEN`: the final result is returned or serialized
- `THEN`: it remains protocol-shaped and contains repository identity in `REPOSITORY` and aggregate values in `SUMMARY`

**`AC-04`**

- `GIVEN`: an implementation path claims support for `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-07`
- `WHEN`: that path is validated against an approved scenario
- `THEN`: the produced result matches the approved golden output for that scenario

**`AC-ALG-A-01`**

- `GIVEN`: the approved `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-07` scenario
- `WHEN`: the current `Algorithm A` path is executed
- `THEN`: the produced result matches the approved NG golden output for that scenario

**`AC-ALG-B-01`**

- `GIVEN`: the approved `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-07` replay scenario
- `WHEN`: the current narrow `Algorithm B` Git live-snapshot path is executed
- `THEN`: the produced result matches the approved NG golden output for that scenario

**`AC-ALG-B-02`**

- `GIVEN`: the current `Algorithm B` evidence for `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-07`
- `WHEN`: the support boundary is documented or discussed
- `THEN`: it is described as narrow Git live-snapshot replay support for the approved scenario of this story, not as blanket support across other complicated-history shapes

### USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-08: Git And SVN Must Follow The Same Result Contract

- `WHO`: repository analyst
- `WHEN / Scenario`: when the same primary metric is requested against equivalent supported Git and SVN histories
- `WHAT`: keep the query-result contract consistent across VCS targets
- `WHY`: ensure changing VCS type does not change metric semantics or output structure
- `Story Sentence`: As a repository analyst, I want Git and SVN targets to follow the same query-result contract for the current primary metric, so that changing VCS type does not change metric semantics or output structure.
- `Support Coordinates`: `scope=A baseline`, `algorithms=A and current narrow B parity slice`, `vcs=git and svn`, `tier=Fast`
- `Support Snapshot`: Git and SVN parity exists through `Algorithm A`, and narrow Git/SVN `Algorithm B` contract parity exists on the approved story-01 Git/SVN scenarios plus the approved story-08 SVN parity scenario.
- `Scenario Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-08-SVN-PARITY`, approved `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-01-GIT` and `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-01-SVN` baseline scenarios

Acceptance Criteria

**`AC-01`**

- `GIVEN`: equivalent supported repository history is represented in Git or SVN for the same requested window
- `WHEN`: the current primary metric is analyzed
- `THEN`: Git and SVN produce one final record with the same metric semantics and the same protocol-shaped structure, differing only in VCS-specific repository identity details

**`AC-02`**

- `GIVEN`: the analysis succeeds for the requested repository window
- `WHEN`: the final result is returned or serialized
- `THEN`: it remains protocol-shaped and contains repository identity in `REPOSITORY` and aggregate values in `SUMMARY`

**`AC-03`**

- `GIVEN`: a supported VCS-specific path claims support for `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-08`
- `WHEN`: that path is validated against an approved parity scenario
- `THEN`: the produced result matches the approved golden output for that scenario

**`AC-GIT-01`**

- `GIVEN`: the current Git path for the primary metric
- `WHEN`: it is validated through the baseline live-snapshot scenarios
- `THEN`: it defines one side of the observable parity contract

**`AC-SVN-01`**

- `GIVEN`: the approved `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-08-SVN-PARITY` scenario
- `WHEN`: the current SVN path is executed
- `THEN`: the produced result matches the approved NG golden output for that parity scenario while preserving the shared `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-08` contract

**`AC-SVN-02`**

- `GIVEN`: SVN path-history or blame differences require a VCS-specific parity shape
- `WHEN`: the parity scenario is designed
- `THEN`: it may use a defensible SVN-specific repository shape as long as the observable result contract stays the same

**`AC-ALG-B-01`**

- `GIVEN`: the approved narrow `Algorithm B` Git and SVN live-snapshot verification tracks for the baseline scenario
- `WHEN`: they are used as the current parity scenario
- `THEN`: they produce the same protocol-shaped observable contract across Git and SVN, differing only in VCS-specific repository identity fields

**`AC-ALG-B-02`**

- `GIVEN`: the current `Algorithm B` evidence for `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-08`
- `WHEN`: the support boundary is documented or discussed
- `THEN`: it is described as narrow parity on the approved story-01 and story-08 scenarios, not as full cross-story Git/SVN parity for every supported topology

### USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLEX-SCOPE-A-09: Large Repository Snapshot Must Preserve Result Semantics

- `WHO`: repository analyst
- `WHEN / Scenario`: when the repository contains many files and many live lines but the analyst still expects the same metric semantics
- `WHAT`: preserve the live-snapshot contract for large realistic repositories
- `WHY`: keep aggregate results trustworthy at larger repository scales
- `Story Sentence`: As a repository analyst, I want the analyzer to keep the same result semantics when the repository contains many source files and many live lines, so that the final aggregate result remains correct for realistic large codebases.
- `Support Coordinates`: `scope=A baseline`, `algorithms=A and current narrow B Git slice`, `vcs=shared story`, `tier=Fast`
- `Support Snapshot`: `Algorithm A` evidence exists. `Algorithm B` evidence is narrow Git live-snapshot replay for the approved scenario of this story, with focused real local-Git proof.
- `Scenario Anchors`: `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLEX-SCOPE-A-09`

Acceptance Criteria

**`AC-01`**

- `GIVEN`: the final live snapshot at `endTime` spans many source files and many live code lines
- `WHEN`: the analyzer computes the final aggregate result
- `THEN`: it still produces exactly one repository-level final result with the same metric semantics and protocol shape as smaller repositories

**`AC-02`**

- `GIVEN`: a large repository snapshot contains many in-scope lines across many files
- `WHEN`: the analyzer aggregates the result
- `THEN`: repository size or file count does not change per-line attribution rules, repository identity rules, or the meaning of the final `SUMMARY` fields

**`AC-03`**

- `GIVEN`: an implementation path claims support for `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLEX-SCOPE-A-09`
- `WHEN`: that path is validated against an approved scenario
- `THEN`: the produced result matches the approved golden output for that scenario

**`AC-ALG-A-01`**

- `GIVEN`: the approved `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLEX-SCOPE-A-09` scenario
- `WHEN`: the current `Algorithm A` path is executed
- `THEN`: the produced result matches the approved NG golden output for that scenario

**`AC-ALG-B-01`**

- `GIVEN`: the approved `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLEX-SCOPE-A-09` scenario expressed through fixture replay artifacts or the focused real local-Git replay path
- `WHEN`: the current narrow `Algorithm B` Git live-snapshot path is executed
- `THEN`: the produced result matches the approved NG golden output for that scenario

**`AC-ALG-B-02`**

- `GIVEN`: the current `Algorithm B` evidence for `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLEX-SCOPE-A-09`
- `WHEN`: the support boundary is documented or discussed
- `THEN`: it is described as narrow Git live-snapshot replay support for the approved scenario of this story with focused real local-Git proof, not as full matrix-ready large-snapshot scalability support

### USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLEX-SCOPE-A-10: Deep History Must Preserve Latest Effective Attribution

- `WHO`: repository analyst
- `WHEN / Scenario`: when surviving lines at `endTime` come through long revision chains with many intermediate rewrites
- `WHAT`: resolve each surviving line by its latest effective attribution instead of by superseded intermediate ownership
- `WHY`: prevent deep history from distorting the final live result
- `Story Sentence`: As a repository analyst, I want long revision chains to preserve the latest effective attribution of each surviving line, so that many intermediate rewrites do not distort the final live result.
- `Support Coordinates`: `scope=A baseline`, `algorithms=A and current narrow B Git slice`, `vcs=shared story`, `tier=Fast`
- `Support Snapshot`: `Algorithm A` evidence exists. `Algorithm B` evidence is narrow Git live-snapshot replay for the approved scenario of this story, with focused real local-Git proof.
- `Scenario Anchors`: `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLEX-SCOPE-A-10`

Acceptance Criteria

**`AC-01`**

- `GIVEN`: in-scope live lines at `endTime` depend on long revision chains with many intermediate rewrites
- `WHEN`: the analyzer resolves each surviving line
- `THEN`: it uses the latest effective live attribution rather than earlier superseded revisions in the chain

**`AC-02`**

- `GIVEN`: long history chains contain both human-to-AI and AI-to-human transitions before `endTime`
- `WHEN`: the final aggregate result is produced
- `THEN`: deleted or superseded intermediate states do not leak into that result

**`AC-03`**

- `GIVEN`: an implementation path claims support for `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLEX-SCOPE-A-10`
- `WHEN`: that path is validated against an approved scenario
- `THEN`: the produced result matches the approved golden output for that scenario

**`AC-ALG-A-01`**

- `GIVEN`: the approved `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLEX-SCOPE-A-10` scenario
- `WHEN`: the current `Algorithm A` path is executed
- `THEN`: the produced result matches the approved NG golden output for that scenario

**`AC-ALG-B-01`**

- `GIVEN`: the approved `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLEX-SCOPE-A-10` scenario expressed through fixture replay artifacts or the focused real local-Git replay path
- `WHEN`: the current narrow `Algorithm B` Git live-snapshot path is executed
- `THEN`: the produced result matches the approved NG golden output for that scenario

**`AC-ALG-B-02`**

- `GIVEN`: the current `Algorithm B` evidence for `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLEX-SCOPE-A-10`
- `WHEN`: the support boundary is documented or discussed
- `THEN`: it is described as narrow Git live-snapshot replay support for the approved scenario of this story with focused real local-Git proof, not as full matrix-ready deep-history support

### USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLEX-SCOPE-A-11: Many Merged Branches In One Window Must Preserve Per-Line Attribution

- `WHO`: repository analyst
- `WHEN / Scenario`: when many branches are merged into the target branch inside one requested window
- `WHAT`: preserve per-line effective attribution across branch-heavy merge history
- `WHY`: stop branch fan-in and merge order from distorting the final result
- `Story Sentence`: As a repository analyst, I want branch-heavy history inside one requested window to preserve per-line effective attribution, so that integrating many feature branches into the target branch does not distort the final result.
- `Support Coordinates`: `scope=A baseline`, `algorithms=A and current narrow B Git slice`, `vcs=shared story with SVN analogue note`, `tier=Fast`
- `Support Snapshot`: `Algorithm A` evidence exists. `Algorithm B` evidence is narrow Git live-snapshot replay for the approved scenario of this story. SVN parity may require a defensible analogue rather than a literal same-file Git port.
- `Scenario Anchors`: `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLEX-SCOPE-A-11`

Acceptance Criteria

**`AC-01`**

- `GIVEN`: many branches are merged into the target branch before `endTime`
- `WHEN`: the analyzer computes the final result for the live changed source-code set at `endTime`
- `THEN`: it still produces exactly one repository-level final result

**`AC-02`**

- `GIVEN`: surviving lines originate from different merged branches with different effective histories
- `WHEN`: the analyzer resolves the final live state
- `THEN`: it preserves each surviving line independently and does not flatten ownership to merge commits, branch labels, or merge order alone

**`AC-03`**

- `GIVEN`: an implementation path claims support for `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLEX-SCOPE-A-11`
- `WHEN`: that path is validated against an approved scenario
- `THEN`: the produced result matches the approved golden output for that scenario

**`AC-ALG-A-01`**

- `GIVEN`: the approved `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLEX-SCOPE-A-11` scenario
- `WHEN`: the current `Algorithm A` path is executed
- `THEN`: the produced result matches the approved NG golden output for that scenario

**`AC-ALG-A-02`**

- `GIVEN`: SVN parity for the same broad contract needs a defensible analogue
- `WHEN`: literal same-file Git shapes would be misleading for SVN
- `THEN`: an SVN-specific analogue may be used as long as the shared observable contract is preserved

**`AC-ALG-B-01`**

- `GIVEN`: the approved `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLEX-SCOPE-A-11` replay scenario
- `WHEN`: the current narrow `Algorithm B` Git live-snapshot path is executed
- `THEN`: the produced result matches the approved NG golden output for that scenario

**`AC-ALG-B-02`**

- `GIVEN`: the current `Algorithm B` evidence for `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLEX-SCOPE-A-11`
- `WHEN`: the support boundary is documented or discussed
- `THEN`: it is described as narrow Git live-snapshot replay support for the approved scenario of this story, not as full matrix-ready branch-heavy merge support

## Heavy Production Gates

These stories are production gates rather than ordinary small functional stories. They are still role-based stories, but their scenario is explicitly heavy and production-oriented.

### USNG-REPO-GIT-LOCAL-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-12: Git Production-Scale Local Repository Must Stay Correct Under Branch-Heavy Release Convergence

- `WHO`: repository analyst
- `WHEN / Scenario`: when validating production-readiness on a branch-heavy local Git repository that mirrors release convergence at scale
- `WHAT`: keep `Algorithm A + Scope A` correct on a production-scale local Git topology
- `WHY`: prove that large branch counts, deep history, and hybrid release merges do not distort the final live attribution result
- `Story Sentence`: As a repository analyst, I want Algorithm A and Scope A to remain correct on a production-scale local Git repository, so that large branch counts, deep history, and hybrid release merges do not distort the final live attribution result.
- `Support Coordinates`: `scope=A baseline`, `algorithm=A`, `vcs=git`, `tier=Heavy`
- `Support Snapshot`: production-facing heavy gate with real local Git repository generation and correctness plus scalability checks.
- `Scenario Anchors`: `TestsNG-REPO-GIT-LOCAL-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-12`

Acceptance Criteria

**`AC-GIT-01`**

- `GIVEN`: a local Git repository represents a production-like topology with on the order of `100+` branches, `1000+` commits, and repeated feature-to-integration-to-release merge fan-in before `endTime`
- `WHEN`: the analyzer computes the final result for the live changed source-code set at `endTime`
- `THEN`: it still produces exactly one repository-level final result

**`AC-GIT-02`**

- `GIVEN`: surviving lines reach the release branch through mixed direct merges, integration branches, and staged convergence
- `WHEN`: final attribution is resolved
- `THEN`: it is based on each surviving line's effective origin revision rather than merge shape, first-parent history alone, or branch naming

**`AC-GIT-03`**

- `GIVEN`: the production-like repository is local rather than remote-hosted
- `WHEN`: it is used as the production-readiness acceptance scenario
- `THEN`: it remains valid because transport is out of scope and history semantics must remain identical apart from network access

**`AC-GIT-04`**

- `GIVEN`: the heavy Git production-scale scenario completes successfully
- `WHEN`: the acceptance outcome is evaluated
- `THEN`: it verifies both correctness of the final aggregate result and scalability-oriented reuse behavior such as bounded metadata reuse or bounded revision-time lookup reuse

### USNG-REPO-SVN-LOCAL-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-13: SVN Production-Scale Local Repository Must Stay Correct Under Branch And Merge Pressure

- `WHO`: repository analyst
- `WHEN / Scenario`: when validating production-readiness on a production-scale local SVN repository with branch copying and reintegration pressure
- `WHAT`: keep `Algorithm A + Scope A` correct on a production-scale local SVN topology
- `WHY`: prove that SVN branch copying, merges, and release reintegration at scale do not break live attribution
- `Story Sentence`: As a repository analyst, I want Algorithm A and Scope A to remain correct on a production-scale local SVN repository, so that SVN branch copying, merges, and release reintegration at scale do not break live attribution.
- `Support Coordinates`: `scope=A baseline`, `algorithm=A`, `vcs=svn`, `tier=Heavy`
- `Support Snapshot`: production-facing heavy gate with real local SVN repository generation and correctness plus scalability checks.
- `Scenario Anchors`: `TestsNG-REPO-SVN-LOCAL-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-13`

Acceptance Criteria

**`AC-SVN-01`**

- `GIVEN`: a local SVN repository represents a production-like topology with on the order of `100+` branches or branch copies, `1000+` revisions, and repeated branch-to-release merge activity before `endTime`
- `WHEN`: the analyzer computes the final result for the live changed source-code set at `endTime`
- `THEN`: it still produces exactly one repository-level final result

**`AC-SVN-02`**

- `GIVEN`: surviving lines reach the release path through mixed direct work, branch copies, and merge or reintegration history
- `WHEN`: final attribution is resolved under supported SVN semantics
- `THEN`: it preserves each surviving line's effective origin revision and does not collapse ownership to merge timing or final branch path alone

**`AC-SVN-03`**

- `GIVEN`: the production-like SVN repository is local rather than remote-hosted
- `WHEN`: it is used as the production-readiness acceptance scenario
- `THEN`: it remains valid because transport is not part of the attribution contract

**`AC-SVN-04`**

- `GIVEN`: the heavy SVN production-scale scenario completes successfully
- `WHEN`: the acceptance outcome is evaluated
- `THEN`: it verifies both correctness of the final aggregate result and scalability-oriented reuse behavior such as branch-origin metadata reuse, bounded revision-time queries, or equivalent explicit reuse signals

## Scope Contract Stories

These stories broaden the counted content boundary. The role stays the same, but the scenario changes from "what happened in source code only" to "what content family is in scope".

### USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-B-14: Scope B Source Code With Comments Must Include Comment Lines In Totals

- `WHO`: repository analyst
- `WHEN / Scenario`: when the analyst wants source-file totals to include comment lines as part of the measured source text
- `WHAT`: make `--scope B` count all non-blank lines in source files, including comments
- `WHY`: measure AI contribution across the full textual content of source files, not just executable code
- `Story Sentence`: As a repository analyst, I want `--scope B` to count all non-blank lines in source files, including comment lines, in the aggregate result, so that I can measure AI contribution across the full textual content of source files, not just executable code.
- `Support Coordinates`: `scope=B`, `algorithms=primarily A at story level`, `vcs=shared`, `tier=Fast`
- `Support Snapshot`: first-class scope story for comment-inclusive source-file totals.
- `Scenario Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-B-14`

Acceptance Criteria

**`AC-01`**

- `GIVEN`: a source file contains both code lines and comment lines
- `WHEN`: the analyzer runs with `--scope B`
- `THEN`: `totalCodeLines` includes all non-blank source lines rather than only the code-only subset counted by `Scope A`

**`AC-02`**

- `GIVEN`: a source file contains comment lines covered through `codeLines`
- `WHEN`: the analyzer runs with `--scope B`
- `THEN`: comment lines with `genRatio 100` count as `fullGeneratedCodeLines`, and comment lines with `genRatio` between 1 and 99 count as `partialGeneratedCodeLines`

**`AC-03`**

- `GIVEN`: the same repository and metadata are analyzed under the baseline scope
- `WHEN`: the analyzer runs with `--scope A`
- `THEN`: comment lines remain excluded, preserving backward compatibility

### USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-C-15: Scope C Documentation Text Lines Must Be Counted From Doc Files Using docLines Protocol

- `WHO`: repository analyst
- `WHEN / Scenario`: when the analyst wants to measure documentation-only contribution instead of source-code contribution
- `WHAT`: make `--scope C` analyze documentation files and use `docLines` for attribution
- `WHY`: measure AI contribution to documentation artifacts separately from source code
- `Story Sentence`: As a repository analyst, I want `--scope C` to analyze documentation text files and use the `docLines` protocol field for AI attribution, so that I can measure AI contribution to documentation artifacts separately from source code.
- `Support Coordinates`: `scope=C`, `algorithms=primarily A at story level`, `vcs=shared`, `tier=Fast`
- `Support Snapshot`: first-class scope story for documentation-only analysis.
- `Scenario Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-C-15`

Acceptance Criteria

**`AC-01`**

- `GIVEN`: a repository contains files in `DOC_EXTENSIONS`
- `WHEN`: the analyzer runs with `--scope C`
- `THEN`: it includes only documentation files and excludes source-code files

**`AC-02`**

- `GIVEN`: documentation files are analyzed under `--scope C`
- `WHEN`: attribution is computed and the result is emitted
- `THEN`: attribution uses `docLines` and the output uses `totalDocLines`, `fullGeneratedDocLines`, and `partialGeneratedDocLines`

**`AC-03`**

- `GIVEN`: the same repository is analyzed under the source-code scopes
- `WHEN`: the analyzer runs with `--scope A` or `--scope B`
- `THEN`: documentation files remain excluded, preserving scope isolation

### USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-D-16: Scope D All Text Must Unify Source And Documentation Files Into A Single Aggregate

- `WHO`: repository analyst
- `WHEN / Scenario`: when the analyst wants one combined result across both source files and documentation files
- `WHAT`: make `--scope D` count all non-blank source and documentation lines in one aggregate
- `WHY`: measure total AI contribution across the full textual content of the repository
- `Story Sentence`: As a repository analyst, I want `--scope D` to count all non-blank lines from both source files and documentation files in one combined result, so that I can measure total AI contribution across the entire textual content of the repository.
- `Support Coordinates`: `scope=D`, `algorithms=primarily A at story level`, `vcs=shared`, `tier=Fast`
- `Support Snapshot`: first-class scope story for unified source-plus-documentation totals.
- `Scenario Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-D-16`

Acceptance Criteria

**`AC-01`**

- `GIVEN`: a repository contains both source files and documentation files
- `WHEN`: the analyzer runs with `--scope D`
- `THEN`: it includes both file families in one combined analysis

**`AC-02`**

- `GIVEN`: both source files and documentation files are analyzed under `--scope D`
- `WHEN`: attribution is computed and the combined result is emitted
- `THEN`: source lines are attributed through `codeLines`, documentation lines are attributed through `docLines`, and the combined summary uses `totalCodeLines`, `fullGeneratedCodeLines`, and `partialGeneratedCodeLines`

**`AC-03`**

- `GIVEN`: the same repository is analyzed under `--scope A`, `--scope B`, or `--scope C`
- `WHEN`: the analyzer evaluates files outside each scope boundary
- `THEN`: those file families remain excluded, preserving scope isolation

### USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-ALL-17: Scope Parity Matrix Must Confirm All Four Scopes Produce Correct And Isolated Results

- `WHO`: repository analyst
- `WHEN / Scenario`: when the analyst runs all four scopes on the same repository and expects each scope to stay distinct and correct
- `WHAT`: verify the full scope matrix across A, B, C, and D
- `WHY`: trust that scope selection really controls the measurement boundary
- `Story Sentence`: As a repository analyst, I want a cross-scope verification that runs Scope A, B, C, and D on the same repository and confirms each produces the expected distinct result, so that I can trust that scope selection genuinely controls the measurement boundary.
- `Support Coordinates`: `scope=A/B/C/D`, `algorithms=primarily A at story level`, `vcs=shared`, `tier=Fast`
- `Support Snapshot`: first-class cross-scope contract story.
- `Scenario Anchors`: `TestdataNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-ALL-17`

Acceptance Criteria

**`AC-01`**

- `GIVEN`: a repository contains source files with code and comments plus documentation files
- `WHEN`: the analyzer is run with `--scope A`, `--scope B`, `--scope C`, and `--scope D`
- `THEN`: each scope produces the correct summary for its own scope definition

**`AC-02`**

- `GIVEN`: the full four-scope matrix is executed on the same repository
- `WHEN`: the summaries are compared across scopes
- `THEN`: `Scope C` uses the doc-field family `totalDocLines`, `fullGeneratedDocLines`, and `partialGeneratedDocLines`, while `Scopes A`, `B`, and `D` use the code-field family `totalCodeLines`, `fullGeneratedCodeLines`, and `partialGeneratedCodeLines`

## Algorithm-B Scope Broadening Stories

These stories keep the same analyst role but move the scenario to replay-based attribution on broader scopes.

### USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-B-18: Algorithm B Must Support Scope B

- `WHO`: repository analyst
- `WHEN / Scenario`: when the analyst needs replay-based attribution across source code plus source comments
- `WHAT`: make `--algorithm B --scope B` count all non-blank source lines including comments
- `WHY`: measure total AI contribution to all source text using the incremental replay algorithm
- `Story Sentence`: As a repository analyst, I want `--algorithm B --scope B` to count all non-blank source lines including comments during replay, so that I can measure total AI contribution to all source text using the incremental replay algorithm.
- `Support Coordinates`: `scope=B`, `algorithm=B`, `vcs=current supported replay shapes`, `tier=Fast`
- `Support Snapshot`: first-class story for Algorithm B comment-inclusive source replay.
- `Scenario Anchors`: `TestsNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-B-18`

Acceptance Criteria

**`AC-ALG-B-01`**

- `GIVEN`: a source file contains both code lines and comment lines
- `WHEN`: `Algorithm B` runs with `--scope B`
- `THEN`: `totalCodeLines` includes all non-blank source lines

### USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-C-19: Algorithm B Must Support Scope C

- `WHO`: repository analyst
- `WHEN / Scenario`: when the analyst needs replay-based attribution on documentation files instead of source files
- `WHAT`: make `--algorithm B --scope C` replay and count documentation file lines through `docLines`
- `WHY`: measure AI contribution to documentation using the incremental replay algorithm
- `Story Sentence`: As a repository analyst, I want `--algorithm B --scope C` to replay and count documentation file lines using the `docLines` protocol field, so that I can measure AI contribution to documentation using the incremental replay algorithm.
- `Support Coordinates`: `scope=C`, `algorithm=B`, `vcs=current supported replay shapes`, `tier=Fast`
- `Support Snapshot`: first-class story for Algorithm B documentation replay.
- `Scenario Anchors`: `TestsNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-C-19`

Acceptance Criteria

**`AC-ALG-B-01`**

- `GIVEN`: a documentation file contains non-blank lines
- `WHEN`: `Algorithm B` runs with `--scope C`
- `THEN`: it emits the doc-field family `totalDocLines`, `fullGeneratedDocLines`, and `partialGeneratedDocLines`

**`AC-ALG-B-02`**

- `GIVEN`: the protocol `DETAIL` entry for the documentation file uses `docLines`
- `WHEN`: `Algorithm B` performs line-ratio lookup during replay
- `THEN`: it uses the doc protocol index

### USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-D-20: Algorithm B Must Support Scope D

- `WHO`: repository analyst
- `WHEN / Scenario`: when the analyst needs replay-based attribution across both source and documentation files in one run
- `WHAT`: make `--algorithm B --scope D` replay both file families into one combined result
- `WHY`: measure total AI contribution across all textual repository content using the incremental replay algorithm
- `Story Sentence`: As a repository analyst, I want `--algorithm B --scope D` to replay both source files and documentation files into a unified result, so that I can measure total AI contribution across all textual repository content using the incremental replay algorithm.
- `Support Coordinates`: `scope=D`, `algorithm=B`, `vcs=current supported replay shapes`, `tier=Fast`
- `Support Snapshot`: first-class story for Algorithm B unified source-plus-doc replay.
- `Scenario Anchors`: `TestsNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-D-20`

Acceptance Criteria

**`AC-ALG-B-01`**

- `GIVEN`: a repository contains both source files and documentation files
- `WHEN`: `Algorithm B` runs with `--scope D`
- `THEN`: it replays both file families, using `codeLines` for source files and `docLines` for documentation files

**`AC-ALG-B-02`**

- `GIVEN`: `Algorithm B` produces a combined replay result under `--scope D`
- `WHEN`: the summary is emitted
- `THEN`: it uses `totalCodeLines`, `fullGeneratedCodeLines`, and `partialGeneratedCodeLines`

## Period-Added Contract Stories

These stories are about contribution during the window, not inventory at `endTime`. The role is still the analyst, but the scenario changes from live-snapshot measurement to period-added measurement.

### USNG-REPO-GIT-LOCAL-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-21: Calculate AI-Added Ratio During The Requested Period

- `WHO`: repository analyst
- `WHEN / Scenario`: when the analyst wants to measure AI contribution added during the window itself, not the end-of-window inventory
- `WHAT`: calculate how much AI-generated code was added during `startTime~endTime`
- `WHY`: distinguish period contribution from end-of-period inventory
- `Story Sentence`: As a repository analyst, I want to calculate how much AI-generated code was added during `startTime~endTime`, so that I can distinguish period contribution from end-of-period inventory.
- `Support Coordinates`: `scope=shared story anchor`, `algorithms=A future and B current narrow baseline`, `vcs=shared story`, `tier=Fast`
- `Support Snapshot`: shared story anchor; current executable path is narrow `Algorithm B` Git baseline through offline replay and supported local-Git replay.
- `Scenario Anchors`: `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-21`

Acceptance Criteria

**`AC-01`**

- `GIVEN`: `repo`, `branch`, `startTime`, and `endTime` define a requested period
- `WHEN`: the period contribution metric is executed
- `THEN`: it returns exactly one repository-level final result describing the aggregate AI-added code result during that period

**`AC-02`**

- `GIVEN`: a period contribution analysis succeeds
- `WHEN`: the final result is returned or serialized
- `THEN`: it remains protocol-shaped and contains repository identity in `REPOSITORY` and aggregate values in `SUMMARY`

**`AC-03`**

- `GIVEN`: an implementation path claims support for `USNG-REPO-GIT-LOCAL-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-21`
- `WHEN`: that path is validated against an approved scenario
- `THEN`: the produced result matches the approved golden output for that scenario

**`AC-ALG-A-01`**

- `GIVEN`: a future `Algorithm A` path claims support for the period contribution metric
- `WHEN`: it is evaluated against the shared contract
- `THEN`: it satisfies the shared `USNG-REPO-GIT-LOCAL-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-21` clauses without weakening the observable contract

**`AC-ALG-A-02`**

- `GIVEN`: a future `Algorithm A` fixture or real-repository acceptance scenario is added for `USNG-REPO-GIT-LOCAL-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-21`
- `WHEN`: its support tier is documented
- `THEN`: it declares `Fast` or `Heavy` explicitly

**`AC-ALG-B-01`**

- `GIVEN`: the approved `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-21` scenario
- `WHEN`: the current narrow offline Git `Algorithm B` baseline is executed
- `THEN`: the produced result matches the approved NG golden output for that scenario

**`AC-ALG-B-02`**

- `GIVEN`: the input stays within the current narrow Git replay boundary
- `WHEN`: the CLI runs with `--algorithm B`
- `THEN`: the current slice may execute this story through the approved `TestdataNG-REPO-GIT-LOCAL-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-21` replay-input path or the supported local Git checkout path

**`AC-ALG-B-03`**

- `GIVEN`: broader `Algorithm B` history shapes such as multi-file replay, rename-path changes, or merge-aware accounting beyond accepted stories
- `WHEN`: support is described or discussed
- `THEN`: those shapes remain unsupported until proven by their own acceptance tracks

### USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-A-22: Single-Branch Period-Added Baseline Without Merges Or Renames

- `WHO`: repository analyst
- `WHEN / Scenario`: when the analyst wants the cleanest possible single-branch baseline for the period-added metric before topology complexity is introduced
- `WHAT`: prove the core `Algorithm B` period-added contract on a simple linear Git history
- `WHY`: establish a stable baseline before adding rewrites, renames, or merges
- `Story Sentence`: As a repository analyst, I want a single-branch period-added baseline without merges or renames, so that the core `Algorithm B` period-contribution contract is proven before topology complexity is introduced.
- `Support Coordinates`: `scope=A and B note`, `algorithm=B`, `vcs=git local replay`, `tier=Fast`
- `Support Snapshot`: first-class Algorithm B single-branch baseline story.
- `Scenario Anchors`: `TestsNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-A-22`

Acceptance Criteria

**`AC-ALG-B-01`**

- `GIVEN`: a single-branch Git repository has one pre-window human commit and two in-window commits
- `WHEN`: `Algorithm B` computes period-added totals
- `THEN`: it counts only lines whose origin revision falls inside the window, and `fullGeneratedCodeLines` counts only the AI-attributed in-window lines

**`AC-ALG-B-02`**

- `GIVEN`: the same single-branch repository is analyzed under `Scope B`
- `WHEN`: `Algorithm B` computes the period-added result
- `THEN`: it preserves period-added semantics while reflecting the broader source-line scope

### USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-23: Period-Added Accounting With Deletions, Resets, And Mixed Rewrites

- `WHO`: repository analyst
- `WHEN / Scenario`: when the requested period contains added lines, deleted lines, and mixed AI-human rewrites inside one window
- `WHAT`: keep period-added accounting correct across deletions, resets, and mixed rewrites
- `WHY`: prevent superseded or deleted in-window AI lines from distorting the period result
- `Story Sentence`: As a repository analyst, I want period-added accounting to handle deletions, resets, and mixed rewrites inside one window, so that superseded or deleted in-window AI lines do not distort the period result.
- `Support Coordinates`: `scope=primary baseline`, `algorithm=B`, `vcs=git local replay`, `tier=Fast`
- `Support Snapshot`: first-class Algorithm B rewrite and deletion story.
- `Scenario Anchors`: `TestsNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-23`

Acceptance Criteria

**`AC-ALG-B-01`**

- `GIVEN`: an AI line is added during the window and later deleted or replaced by a later in-window commit
- `WHEN`: `Algorithm B` computes the period-added result
- `THEN`: that deleted AI line does not appear in the final period-added total

**`AC-ALG-B-02`**

- `GIVEN`: a pre-window human line is rewritten during the window
- `WHEN`: `Algorithm B` computes the period-added result
- `THEN`: the rewritten line is counted as in-window with the rewriter's attribution

### USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-24: Git Rename And Move Handling For Period Contribution

- `WHO`: repository analyst
- `WHEN / Scenario`: when a file is renamed during the period and the analyst still needs true period-added accounting
- `WHAT`: preserve rename and move semantics in the period-added metric
- `WHY`: stop path-only changes from making old lines appear as new in-window additions
- `Story Sentence`: As a repository analyst, I want period-added accounting to preserve rename and move semantics, so that path-only history changes do not make older lines appear as new in-window additions.
- `Support Coordinates`: `scope=primary baseline`, `algorithm=B`, `vcs=git local replay`, `tier=Fast`
- `Support Snapshot`: first-class Algorithm B rename story for period contribution.
- `Scenario Anchors`: `TestsNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-24`

Acceptance Criteria

**`AC-ALG-B-01`**

- `GIVEN`: a file is renamed during the window and a new AI line is added
- `WHEN`: `Algorithm B` computes the period-added result
- `THEN`: only the new line counts in the period-added total while pre-window lines that survived the rename remain excluded

### USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-25: Merge-Aware Git Period Contribution Inside One Window

- `WHO`: repository analyst
- `WHEN / Scenario`: when the requested period includes branch work and non-fast-forward merge activity
- `WHAT`: keep period-added accounting correct across merge-aware Git history inside the window
- `WHY`: ensure contributions from both main and merged feature branches count correctly
- `Story Sentence`: As a repository analyst, I want period-added accounting to survive branch-and-merge history inside one window, so that contributions from both main and merged feature branches are counted correctly.
- `Support Coordinates`: `scope=primary baseline`, `algorithm=B`, `vcs=git local replay`, `tier=Fast`
- `Support Snapshot`: first-class Algorithm B merge-aware story for period contribution.
- `Scenario Anchors`: `TestsNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-25`

Acceptance Criteria

**`AC-ALG-B-01`**

- `GIVEN`: AI lines are added on main and on a feature branch and then merged during the window through a non-fast-forward merge
- `WHEN`: `Algorithm B` computes the period-added result
- `THEN`: both contributions survive and count correctly in the final period-added total

### USNG-REPO-SVN-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-A-26: SVN-Supported Subset For Algorithm-B Period Contribution

- `WHO`: repository analyst
- `WHEN / Scenario`: when the analyst wants a defended SVN subset for period-added replay without overclaiming full SVN parity
- `WHAT`: make the supported SVN fixture subset produce correct `Algorithm B` period-added results
- `WHY`: expand SVN support scenario-first while keeping claims defensible
- `Story Sentence`: As a repository analyst, I want the defended SVN subset of `Algorithm B` period-added replay to produce correct results from offline fixtures, so that SVN support can expand scenario-first without overclaiming general parity.
- `Support Coordinates`: `scope=primary baseline`, `algorithm=B`, `vcs=svn offline fixtures`, `tier=Fast`
- `Support Snapshot`: first-class Algorithm B SVN subset story through offline replay artifacts.
- `Scenario Anchors`: `TestsNG-REPO-SVN-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-A-26`

Acceptance Criteria

**`AC-ALG-B-01`**

- `GIVEN`: SVN-style offline commit-diff fixtures are provided together with protocol files
- `WHEN`: `Algorithm B` replays the period-added scenario
- `THEN`: it correctly counts AI versus human lines from the SVN patches

## Cross-Algorithm, Hardening, And Operator Stories

These stories move from pure metric semantics into algorithm parity, runtime safety, and operator-visible narrative.

### USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-ALL-27: Algorithm A And Algorithm B Must Produce Identical SUMMARY For Every Scope

- `WHO`: repository analyst
- `WHEN / Scenario`: when the analyst compares the blame-based and replay-based implementations on the same repository content
- `WHAT`: keep `SUMMARY` identical across Algorithm A and Algorithm B for every scope
- `WHY`: ensure algorithm choice does not change the measurement result
- `Story Sentence`: As a repository analyst, I want `Algorithm A` and `Algorithm B` to produce the same `SUMMARY` for every scope on the same repository content, so that algorithm choice does not change the measurement result.
- `Support Coordinates`: `scope=A/B/C/D`, `algorithms=A and B`, `vcs=shared replay-supported shapes`, `tier=Fast`
- `Support Snapshot`: first-class cross-algorithm cross-scope parity story.
- `Scenario Anchors`: `TestsNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-ALL-27`

Acceptance Criteria

**`AC-01`**

- `GIVEN`: a repository contains source files and documentation files
- `WHEN`: `Algorithm A` and `Algorithm B` are both run with `--scope A`
- `THEN`: they produce identical `SUMMARY` values

**`AC-02`**

- `GIVEN`: the same repository is analyzed under the remaining scopes
- `WHEN`: `Algorithm A` and `Algorithm B` are both run with `--scope B`, `--scope C`, and `--scope D`
- `THEN`: they produce identical `SUMMARY` values, including the correct doc-versus-code field family where relevant

**`AC-03`**

- `GIVEN`: both algorithms produce protocol-shaped results across all supported scopes
- `WHEN`: the protocol metadata is compared
- `THEN`: `protocolName` and `protocolVersion` match across algorithms

### USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-RUNTIME-28: Production Hardening - Scope Validation And File-Size Guard

- `WHO`: CLI operator
- `WHEN / Scenario`: when the operator passes invalid scope input or the runtime encounters oversized VCS output that could make processing unsafe
- `WHAT`: fail fast with explicit validation and size guards
- `WHY`: avoid silent wrong results, runaway memory use, or unclear failure behavior
- `Story Sentence`: As a CLI operator, I want invalid `--scope` values to be rejected at input validation and oversized VCS outputs to be caught before processing, so that the tool fails fast with clear diagnostics instead of producing silent wrong results or running out of memory.
- `Support Coordinates`: `scope=input and runtime guard`, `algorithms=A and B`, `vcs=git-focused runtime checks`, `tier=Fast`
- `Support Snapshot`: first-class hardening story.
- `Scenario Anchors`: `TestsNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-RUNTIME-28`

Acceptance Criteria

**`AC-HARD-01`**

- `GIVEN`: the CLI receives an invalid `--scope` value such as `Z`, lowercase `a`, or an empty string
- `WHEN`: input validation runs
- `THEN`: the tool exits with `EXIT_INPUT_ERROR` and a diagnostic containing `--scope must be one of: A, B, C, D`

**`AC-HARD-02`**

- `GIVEN`: a Git repository contains a file whose `git show` output exceeds `MAX_FILE_SIZE_BYTES`
- `WHEN`: `Algorithm B` reads the file through `read_git_file_lines_at_revision`
- `THEN`: it raises `RepositoryStateError` with a clear diagnostic

**`AC-HARD-03`**

- `GIVEN`: Git blame output exceeds `MAX_FILE_SIZE_BYTES`
- `WHEN`: `Algorithm A` parses blame through `parse_blame`
- `THEN`: it raises `RepositoryStateError` with a clear diagnostic

### USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-RUNTIME-29: Info-Level Log Must Show Initial Load, Per-Line State Transition, And Final Summary

- `WHO`: CLI operator running with `--logLevel info`
- `WHEN / Scenario`: when the operator wants to understand the attribution story from stderr without turning on the full volume of debug logging
- `WHAT`: show a three-phase info-level narrative covering start state, per-line transition hints, and final summary
- `WHY`: help the operator understand which lines changed ownership and what the final aggregate result means without switching to `--logLevel debug`
- `Story Sentence`: As a CLI operator running with `--logLevel info`, I want to see a three-phase narrative on stderr showing initial load state, per-line state transitions, and final summary, so that I can understand the full attribution story without switching to `--logLevel debug`.
- `Support Coordinates`: `scope=stderr behavior`, `algorithms=primarily A current operator path`, `vcs=shared`, `tier=Fast target`
- `Support Snapshot`: documented story record in USNG. Current executable test coverage is still an open gap.
- `Scenario Anchors`: `OperatorScenarioNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-RUNTIME-29-AI-TO-HUMAN-SHAPE`, `OperatorScenarioNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-RUNTIME-29-HUMAN-TO-AI-SHAPE`, `TestsNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-RUNTIME-29`

Acceptance Criteria

**`AC-OPS-01`**

- `GIVEN`: the CLI runs with `--logLevel info`
- `WHEN`: analysis starts
- `THEN`: stderr emits an `[INFO]` line containing `repo=`, `branch=`, `window=`, and `endRevision=`

**`AC-OPS-02`**

- `GIVEN`: the CLI runs with `--logLevel info` and a live line changes ownership relative to the parent revision
- `WHEN`: that line is processed
- `THEN`: stderr emits an `[INFO] TransitionHint` line containing `best_effort_transition=`

**`AC-OPS-03`**

- `GIVEN`: the CLI runs with `--logLevel info`
- `WHEN`: analysis finishes
- `THEN`: stderr emits an `[INFO]` summary line containing `totalCodeLines=`, `fullGeneratedCodeLines=`, `partialGeneratedCodeLines=`, and `elapsed=`

**`AC-OPS-04`**

- `GIVEN`: the CLI runs with `--logLevel quiet`
- `WHEN`: the analyzer would otherwise emit transition or live-line details
- `THEN`: `TransitionHint` lines and `LiveLine` lines are suppressed

**`AC-OPS-05`**

- `GIVEN`: the CLI runs with `--logLevel debug`
- `WHEN`: analysis progresses through loading, scanning, skips, and cache reuse
- `THEN`: metadata-loading, file-scanning, out-of-window skip, and cached-protocol reuse diagnostics remain visible in addition to all info-level lines

**`AC-OPS-06`**

- `GIVEN`: the approved `OperatorScenarioNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-RUNTIME-29-AI-TO-HUMAN-SHAPE` is executed with `--logLevel info`
- `WHEN`: the ownership transition is reported
- `THEN`: stderr includes `best_effort_transition=100%-ai->human/unattributed`

**`AC-OPS-07`**

- `GIVEN`: the approved `OperatorScenarioNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-RUNTIME-29-HUMAN-TO-AI-SHAPE` is executed with `--logLevel info`
- `WHEN`: the ownership transition is reported
- `THEN`: stderr includes `best_effort_transition=human/unattributed->100%-ai`

## Traceability Appendix

Use this appendix only when audit, comparison, or search still requires the earlier family-based `USNG-*` references or the legacy `US-*` references. The main story layer above now uses 4D `USNG-*` identifiers.

- Live-snapshot lineage: `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-01` -> previous `USNG-LS-01` -> `US-1`; `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-02` -> previous `USNG-LS-02` -> `US-2`; `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-03` -> previous `USNG-LS-03` -> `US-3`; `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-04` -> previous `USNG-LS-04` -> `US-4`; `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-05` -> previous `USNG-LS-05` -> `US-5`; `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-06` -> previous `USNG-LS-06` -> `US-7`; `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-07` -> previous `USNG-LS-07` -> `US-8`; `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-08` -> previous `USNG-LS-08` -> `US-9`; `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLEX-SCOPE-A-09` -> previous `USNG-LS-09` -> `US-10`; `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLEX-SCOPE-A-10` -> previous `USNG-LS-10` -> `US-11`; `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLEX-SCOPE-A-11` -> previous `USNG-LS-11` -> `US-12`
- Production-gate lineage: `USNG-REPO-GIT-LOCAL-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-12` -> previous `USNG-PG-01` -> `US-13`; `USNG-REPO-SVN-LOCAL-GENCODEDESC-SHARED-HISTORY-COMPLEX-SCOPE-A-13` -> previous `USNG-PG-02` -> `US-14`
- Scope-contract lineage: `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-B-14` -> previous `USNG-SC-01` -> `US-20`; `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-C-15` -> previous `USNG-SC-02` -> `US-21`; `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-D-16` -> previous `USNG-SC-03` -> `US-22`; `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-ALL-17` -> previous `USNG-SC-04` -> `US-23`
- Algorithm-B scope lineage: `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-B-18` -> previous `USNG-AB-01` -> `US-24`; `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-C-19` -> previous `USNG-AB-02` -> `US-25`; `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-D-20` -> previous `USNG-AB-03` -> `US-26`
- Period-added lineage: `USNG-REPO-GIT-LOCAL-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-A-21` -> previous `USNG-PA-01` -> `US-6`; `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-A-22` -> previous `USNG-PA-02` -> `US-15`; `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-23` -> previous `USNG-PA-03` -> `US-16`; `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-24` -> previous `USNG-PA-04` -> `US-17`; `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-COMPLICATED-SCOPE-A-25` -> previous `USNG-PA-05` -> `US-18`; `USNG-REPO-SVN-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-A-26` -> previous `USNG-PA-06` -> `US-19`
- Cross-algorithm, hardening, and operator lineage: `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-SIMPLE-SCOPE-ALL-27` -> previous `USNG-CA-01` -> `US-27`; `USNG-REPO-GIT-LOCAL-GENCODEDESC-LOCAL-HISTORY-SIMPLE-SCOPE-RUNTIME-28` -> previous `USNG-CA-02` -> `US-28`; `USNG-REPO-SHARED-GENCODEDESC-SHARED-HISTORY-COMPLICATED-SCOPE-RUNTIME-29` -> previous `USNG-CA-03` -> `US-29`
