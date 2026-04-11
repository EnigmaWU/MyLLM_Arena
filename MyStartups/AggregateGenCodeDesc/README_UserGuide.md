# AggregateGenCodeDesc User Guide

## Purpose

Operator-facing guide for running `aggregateGenCodeDesc.py`.

For the authoritative next-generation user stories and acceptance model, see `README_UserStoryNG.md`.
`README_UserStory.md` remains available only as the legacy migration source.

## Quick Start

Analyze a local Git repository with default settings (Algorithm A, Scope A):

```bash
python3 aggregateGenCodeDesc.py \
  --vcsType git \
  --repoURL /path/to/local/git/repo \
  --repoBranch main \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --outputFile /tmp/agg-out.json \
  --genCodeDescSetDir /path/to/genCodeDescSet
```

All examples below assume you run from the project directory:

```bash
cd /path/to/AggregateGenCodeDesc
```

## Current Support Matrix

| Algorithm | VCS | Scope A | Scope B | Scope C | Scope D |
|-----------|-----|---------|---------|---------|---------|
| **A** (live repository) | Git | ✅ production | ✅ production | ✅ production | ✅ production |
| **A** (live repository) | SVN | ✅ production | ✅ production | ✅ production | ✅ production |
| **B** (replay, local Git) | Git | ✅ production | ✅ production | ✅ production | ✅ production |
| **B** (replay, local SVN) | SVN | ✅ supported workflow | ✅ supported workflow | ✅ supported workflow | ✅ supported workflow |
| **B** (replay, commit diff set) | Git | ✅ production | ✅ production | ✅ production | ✅ production |
| **B** (replay, commit diff set) | SVN | ✅ production | ✅ production | ✅ production | ✅ production |
| **C** (embedded blame, v26.04) | Git-origin blame | ✅ production | ✅ production | ✅ production | ✅ production |
| **C** (embedded blame, v26.04) | SVN-origin blame | ✅ production | ✅ production | ✅ production | ✅ production |

Notes for the local SVN AlgB row:

- It is a supported workflow, not a separate direct local-SVN replay engine.
- First export the `startTime~endTime` revision window from the local SVN repository into a serial commit diff set.
- Then run Algorithm B through the existing `--commitDiffSetDir` path with `--vcsType svn`.
- In other words, the local-SVN row and the `B (replay, commit diff set) | SVN` row use the same AlgB runtime path; the difference is where the patch set comes from.

**Algorithm A** is the recommended production path. It works against a live repository checkout.

**Algorithm B** replays commit diffs to reconstruct line states. It is designed for two modes:

- **Local Git replay**: reads diffs directly from a local Git checkout
- **Commit diff set replay**: reads pre-exported patch files from `--commitDiffSetDir` (works with both Git-origin and SVN-origin patch sets for all Scopes A–D, and is the recommended path for SVN scenarios)

**Algorithm C** consumes embedded blame from `genCodeDescProtoV26.04` files. It supports Scopes A–D, requires `--genCodeDescSetDir`, does not call Git or SVN at runtime, and can derive repository identity from explicit CLI arguments or optional `queryArgs.json` plus the selected end-revision protocol.

## Global Prerequisites

- Python 3.10+
- Git installed locally (for Git runs)
- SVN installed locally (for SVN runs)

## Algorithm Dependencies And Prerequisites

### Algorithm A

- Depends on: live repository access plus per-revision `genCodeDesc` v26.03 metadata.
- Runtime prerequisites:
  - local Git checkout or reachable SVN repository
  - Git installed for Git runs, SVN installed for SVN runs
  - `--repoURL`, `--repoBranch`, `--startTime`, `--endTime`
  - `--genCodeDescSetDir` containing matching per-revision metadata
- Use A when:
  - production correctness and explainability matter most
  - operators need to trace results back to raw VCS evidence
  - live repository access is acceptable

### Algorithm B

- Depends on: replayable commit diffs plus per-revision `genCodeDesc` v26.03 metadata.
- Runtime prerequisites:
  - explicit `--vcsType` is important because it selects the Git or SVN execution path; do not treat it as a passive reference field derived from `--repoURL`
  - for local Git replay: local Git checkout and Git installed
  - for commit diff set replay: `--commitDiffSetDir` plus `--genCodeDescSetDir`
  - every replayed revision must have both a patch artifact and matching metadata
  - `--startTime` and `--endTime`
  - local Git replay still needs repository location (`--repoURL` or `--workingDir`), and in the current CLI usually needs `--repoBranch`
  - commit diff set replay does not fundamentally depend on live repository access; `--repoURL` is mainly used today for metadata identity validation and output identity, while `--repoBranch` is retained as query/output context
  - for SVN, prefer exporting all revisions in `startTime~endTime` into one serial commit diff set and then running AlgB from that exported patch set
- Use B when:
  - runtime must be repository-free but patch artifacts are available
  - you want deterministic historical replay or process reconstruction from the same diff stream
  - the team accepts the highest replay-logic complexity

### Algorithm C

- Depends on: per-revision `genCodeDescProtoV26.04` files with embedded blame and valid `REPOSITORY.revisionTimestamp`.
- Runtime prerequisites:
  - `--algorithm C`
  - `--genCodeDescSetDir` containing at least one `*_genCodeDesc.json`
  - every AlgC protocol file must declare `protocolVersion: "26.04"`
  - Scope A only in the current CLI slice
  - exhaustive surviving-line DETAIL for correctness in the current slice
  - optional `queryArgs.json` in `--genCodeDescSetDir`, or `--queryArgsFile`, to provide `endRevisionId` and/or repository identity
- Use C when:
  - runtime must avoid both repository access and diff replay
  - you are operating in air-gapped, edge, or batch-offline environments
  - write-time protocol quality is trusted and governed tightly enough to support embedded-blame consumption

## Arguments Reference

### Baseline required arguments

| Argument | Description |
|----------|-------------|
| `--repoURL` | Repository identity. Required for Algorithm A. For Algorithm B local Git replay, it is needed unless `--workingDir` is used instead. For Algorithm B offline replay, it is recommended for metadata identity validation and output identity, but the replay data itself comes from `--commitDiffSetDir` plus `--genCodeDescSetDir`. Algorithm C can derive repo identity from explicit CLI arguments or `queryArgs.json` plus the selected v26.04 end protocol. |
| `--repoBranch` | Branch name (e.g. `main`, `trunk`). Required for Algorithm A. For Algorithm B local Git replay, it is typically needed to resolve the end revision. For Algorithm B offline replay, it is best treated as query/output context rather than the core replay dependency. Optional for Algorithm C when identity is derived from explicit CLI arguments or `queryArgs.json` and the end protocol set. |
| `--startTime` | Start date in ISO-8601 format (e.g. `2026-03-01`). |
| `--endTime` | End date in ISO-8601 format (e.g. `2026-03-31`). |

### Commonly used

| Argument | Default | Description |
|----------|---------|-------------|
| `--genCodeDescSetDir` | — | Metadata directory. For Algorithm A/B, it contains `<revisionId>_genCodeDesc.json` files. For Algorithm C, it contains `*_genCodeDesc.json` files with `protocolVersion: "26.04"`, plus optional `queryArgs.json`. |
| `--outputFile` | stdout | Path to write the JSON result. |
| `--scope` | `A` | Which files and lines to count. See [Scope](#--scope) below. |
| `--algorithm` | `A` | `A` for live-repository analysis, `B` for replay-based analysis, `C` for embedded-blame offline analysis. |
| `--vcsType` | `git` | `git` or `svn`. This is an important runtime control field, not just a reference label: it selects whether the analyzer runs Git logic or SVN logic. It is not inferred reliably from `--repoURL`. For Algorithm A and Algorithm B, treat it as explicit input and expect metadata to cross-check it rather than replace it. Optional for Algorithm C when identity is derived from explicit CLI arguments or `queryArgs.json` and the selected end protocol. |

### Algorithm B specific

| Argument | Description |
|----------|-------------|
| `--commitDiffSetDir` | Directory of pre-exported patch files for commit diff set replay. Required for commit-diff-set-driven Algorithm B. Must be paired with `--genCodeDescSetDir`. This is the recommended AlgB path for SVN. |
| `--endRevisionId` | Optional explicit end revision for Algorithm B/C. When omitted, the runtime resolves the latest eligible revision by time. |
| `--includedRevisionIds` | Optional explicit revision subset for Algorithm B. Use it only when you intentionally want to replay a selected subset of revisions from the commit diff set. For normal operator-facing runs, prefer replaying the full `NN_`-ordered commit diff set and let the patch filenames describe order. |
| `--queryArgsFile` | Optional path to a production-facing JSON args file. If omitted, the runtime also looks for `queryArgs.json` inside `--genCodeDescSetDir`. |

Algorithm B note: `repoURL` and `repoBranch` are not equally fundamental in every mode. They matter most in local Git replay. In offline replay, the real hard inputs are the patch stream and matching metadata; `repoURL` is primarily an identity check against metadata, and `repoBranch` is mostly retained for query/result context in the current CLI.

`vcsType` note: for Algorithm A and Algorithm B, prefer passing `--vcsType` explicitly even when `repoURL` or metadata appears to make the VCS obvious. The runtime uses `vcsType` to decide which implementation path to execute, and then uses metadata identity fields to validate consistency.

### Algorithm C specific

| Argument | Description |
|----------|-------------|
| `--genCodeDescSetDir` | Required. Directory of AlgC `genCodeDescProtoV26.04` files. The current slice reads only embedded blame from these files. |
| `queryArgs.json` inside `--genCodeDescSetDir` or `--queryArgsFile` | Optional but recommended. May provide `endRevisionId`, `vcsType`, `repoURL`, and `repoBranch`. If provided, these fields must match the selected end-revision protocol. |
| `--repoURL`, `--repoBranch`, `--vcsType` | Optional for Algorithm C when `--genCodeDescSetDir` is present. Repository identity is derived from explicit CLI values or `queryArgs.json` and the end-revision protocol set. |
| `--scope` | Algorithm C supports Scopes A, B, C, and D. Scopes A/B/D count `codeLines` entries and output `totalCodeLines`/`fullGeneratedCodeLines`/`partialGeneratedCodeLines`. Scope C counts `docLines` entries and outputs `totalDocLines`/`fullGeneratedDocLines`/`partialGeneratedDocLines`. Scope D counts both `codeLines` and `docLines` entries combined. |

### Git logical URL mode

| Argument | Description |
|----------|-------------|
| `--workingDir` | Local Git checkout path. Required when `--repoURL` is a logical URL (not a local path) and `--vcsType` is `git`. Not needed for SVN. |

### Diagnostics and limits

| Argument | Default | Description |
|----------|---------|-------------|
| `--logLevel` | `quiet` | `quiet`, `info`, or `debug`. `info` emits a three-phase narrative: (1) `Starting analysis` banner with repo/branch/window/endRevision, (2) per-line `LiveLine` classification (e.g. `LiveLine src/calc.py:3 classification=100%-ai`) and `TransitionHint` lines showing state transfers between revisions (e.g. `100%-ai->human/unattributed`), (3) `Finished analysis` summary with totals, `elapsed`, and `costSeconds`. `debug` adds metadata loading, file scanning, out-of-window skips, and cached-protocol reuse messages. Output goes to stderr. |
| `--timeout` | `30` | Per-command timeout in seconds (each `git blame`, `git show`, etc.). |
| `--maxRuntime` | `3600` | Overall analysis timeout in seconds. |
| `--warnOnMissingProtocol` | off | Continue in degraded mode when a revision's metadata file is missing; emit a `WARNINGS` entry in the output. |
| `--failOnMissingProtocol` | off | Fail immediately when a revision's metadata file is missing. |

### `--scope`

Controls which file types and line types are included in the result.

| Scope | Files included | Lines counted | Output fields |
|-------|----------------|---------------|---------------|
| **A** (default) | Source files (`.c`, `.cc`, `.cpp`, `.cxx`, `.go`, `.h`, `.hpp`, `.java`, `.js`, `.py`, `.rs`, `.ts`) | Code lines only (exclude comments and blanks) | `totalCodeLines`, `fullGeneratedCodeLines`, `partialGeneratedCodeLines` |
| **B** | Source files | All non-blank lines including comments | `totalCodeLines`, `fullGeneratedCodeLines`, `partialGeneratedCodeLines` |
| **C** | Doc files (`.md`, `.rst`, `.txt`) | Non-blank lines, using the `docLines` protocol field | `totalDocLines`, `fullGeneratedDocLines`, `partialGeneratedDocLines` |
| **D** | Source files + Doc files | All non-blank lines from both; `codeLines` for source, `docLines` for docs | `totalCodeLines`, `fullGeneratedCodeLines`, `partialGeneratedCodeLines` |

Scope is orthogonal to algorithm choice. Scope controls *what* to count; algorithm controls *how* line-origin attribution is computed.

## How To Choose An Algorithm

| If your primary concern is... | Choose | Why |
|---|---|---|
| Lowest logical risk and best auditability | **Algorithm A** | Live blame remains the most authoritative evidence path. |
| Offline replay from explicit historical diff artifacts | **Algorithm B** | It is the only path built around a replayable patch stream. |
| Repository-free and diff-free runtime operation | **Algorithm C** | It consumes only v26.04 files with embedded blame. |
| Best system-wide production baseline when live repo access is acceptable | **Algorithm A** | Lowest explanation risk, lowest protocol burden, and full scope coverage today. |
| Best system-wide effect in controlled offline pipelines with existing patch export jobs | **Algorithm B** | Reuses patch artifacts for replay, experiments, and deterministic re-execution. |
| Best system-wide effect in air-gapped or edge deployment topologies | **Algorithm C** | Minimizes runtime dependencies and permission exposure. |

Recommended default: choose **Algorithm A** unless you have a concrete systems reason to avoid live repository access. Choose **Algorithm B** only when patch-stream replay is itself valuable. Choose **Algorithm C** when the deployment model benefits enough from zero-repository, zero-diff runtime to justify the stricter v26.04 protocol discipline.

### `--commitDiffSetDir` contract

When using Algorithm B with a commit diff set:

- Pair `--commitDiffSetDir` with `--genCodeDescSetDir` — they are the diff side and metadata side of the same replay run.
- Standardize commit diff set patch naming as `NN_<revisionId>_commitDiff.patch` or `NN_<commitId>_commitDiff.patch`, where `NN` is the zero-padded replay sequence.
- Every replayed revision needs both one time-sequenced patch file and the matching `<revisionId>_genCodeDesc.json` file.
- Treat the `NN_` filename prefix as the primary and clearest replay-order contract for a commit diff set.
- Prefer not to use `--includedRevisionIds` or `queryArgs.json.includedRevisionIds` to encode replay order. Keep them only for explicit subset selection when needed.
- Typical special uses of `includedRevisionIds` are:
  - intentionally skip one or more patch files from the commit diff set
  - replay only the defended scenario slice for a test, bug reproduction, or acceptance case
  - compare a full replay against a selected replay to study the effect of specific revisions
- If older fixtures still rely on non-prefixed names or list-driven ordering, treat those as legacy compatibility behavior rather than the preferred fixture contract.
- Patch artifacts may originate from Git or SVN history but must be in unified diff format.

Recommended SVN workflow:

1. Resolve the SVN revisions that fall inside `startTime~endTime`.
2. Export one unified diff patch per revision.
3. Name the patch files in chronological order as `NN_<revisionId>_commitDiff.patch`.
4. Keep the matching `<revisionId>_genCodeDesc.json` files in `--genCodeDescSetDir`.
5. Run Algorithm B with `--vcsType svn --commitDiffSetDir ... --genCodeDescSetDir ...`.

This is the recommended practical way to use Algorithm B for SVN today. It is simpler and lower-risk than introducing a separate local-SVN replay mode.

### Special use of `--includedRevisionIds`

Treat `--includedRevisionIds` as a deliberate control, not the normal way to describe commit diff set order.

- Normal case: do not pass `--includedRevisionIds`; replay the whole commit diff set in `NN_` filename order.
- Special case: pass `--includedRevisionIds` only when you intentionally want to replay a subset.

Example: the commit diff set contains:

- `0001_r101_commitDiff.patch`
- `0002_r102_commitDiff.patch`
- `0003_r103_commitDiff.patch`
- `0004_r104_commitDiff.patch`

Default replay behavior:

```bash
python3 aggregateGenCodeDesc.py \
  --algorithm B \
  --vcsType git \
  --startTime 2026-03-10 \
  --endTime 2026-03-31 \
  --genCodeDescSetDir /path/to/genCodeDescSet \
  --commitDiffSetDir /path/to/commitDiffSet
```

This replays `r101 -> r102 -> r103 -> r104` in `NN_` order.

Intentional subset replay:

```bash
python3 aggregateGenCodeDesc.py \
  --algorithm B \
  --vcsType git \
  --startTime 2026-03-10 \
  --endTime 2026-03-31 \
  --genCodeDescSetDir /path/to/genCodeDescSet \
  --commitDiffSetDir /path/to/commitDiffSet \
  --includedRevisionIds r101 r103 r104
```

This means `r102` is skipped intentionally. Use this only when that omission is part of the purpose of the run.

## User Examples

All user-facing runnable examples now live in `UserExamples/README_UserExamples.md`.

Use that document for:

- generic operator command patterns for Algorithm A, B, and C
- replayable real examples with shipped data under `UserExamples/`
- example-specific diagnosis and output checks

## Output Shape

### Scope A, B, or D

```json
{
  "protocolName": "generatedTextDesc",
  "protocolVersion": "26.03",
  "SUMMARY": {
    "totalCodeLines": 4,
    "fullGeneratedCodeLines": 2,
    "partialGeneratedCodeLines": 1
  },
  "REPOSITORY": {
    "vcsType": "git",
    "repoURL": "/path/to/repo",
    "repoBranch": "main",
    "revisionId": "abc123"
  }
}
```

### Scope C

```json
{
  "protocolName": "generatedTextDesc",
  "protocolVersion": "26.03",
  "SUMMARY": {
    "totalDocLines": 4,
    "fullGeneratedDocLines": 2,
    "partialGeneratedDocLines": 1
  },
  "REPOSITORY": {
    "vcsType": "git",
    "repoURL": "/path/to/repo",
    "repoBranch": "main",
    "revisionId": "abc123"
  }
}
```

### Algorithm C output shape (current slice)

```json
{
  "protocolName": "generatedTextDesc",
  "protocolVersion": "26.04",
  "SUMMARY": {
    "totalCodeLines": 4,
    "fullGeneratedCodeLines": 2,
    "partialGeneratedCodeLines": 1
  },
  "REPOSITORY": {
    "vcsType": "git",
    "repoURL": "https://example.local/repo/demo.git",
    "repoBranch": "main",
    "revisionId": "abc123"
  }
}
```

For Algorithm C, `REPOSITORY` identity comes from the selected v26.04 end protocol and may be cross-checked against explicit CLI values or `queryArgs.json` when provided.

### Optional `WARNINGS` field

When `--warnOnMissingProtocol` is enabled and a revision's metadata is missing, the output includes:

```json
{
  "WARNINGS": [
    "Protocol file not found for revision abc122 in /path/to/genCodeDescSet; treating affected lines as human/unattributed"
  ]
}
```

## Common Problems And Fixes

### `--workingDir is required for git`

You used a logical `--repoURL` (e.g. `https://...`) without telling the tool where the local checkout is.

**Fix:** Add `--workingDir /path/to/local/git/checkout`.

### `Metadata repoURL mismatch`

The `REPOSITORY.repoURL` inside the metadata JSON does not match your CLI `--repoURL`.

**Fix:** Ensure they are identical strings.

### `Protocol file not found for revision`

The `--genCodeDescSetDir` is missing a `<revisionId>_genCodeDesc.json` file.

**Fix:** Add the missing file, or use `--warnOnMissingProtocol` to continue in degraded mode.

### `Commit diff patch file not found`

Algorithm B expects a patch file that is not in `--commitDiffSetDir`.

**Fix:** Add the missing `<timeSeq>_<revisionId>_commitDiff.patch`.

### `--scope must be one of: A, B, C, D`

Invalid scope value (e.g. lowercase `a`, or `Z`).

**Fix:** Use uppercase `A`, `B`, `C`, or `D`.

### `--vcsType must be one of: git, svn`

**Fix:** Use `git` or `svn`.

### `File ... exceeds ... byte limit`

A single file in the repository is larger than 100 MB. This is likely a binary or generated file that should not be tracked as source code.

**Fix:** Exclude the file from tracking, or check if it was committed by mistake.

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | Input validation error (bad arguments) |
| `2` | Repository access error (git/svn command failed) |
| `3` | Protocol/metadata error (malformed JSON, missing fields) |
| `4` | Timeout (exceeded `--maxRuntime`) |

## Further Reading

| Document | Content |
|----------|---------|
| `README.md` | Product scope and measurement definitions |
| `UserExamples/README_UserExamples.md` | Example command patterns grouped for operators |
| `README_UserStory.md` | Story-level acceptance criteria |
| `README_SharedUS_Convergence.md` | Production convergence roadmap (completed) |
| `README_RunTestCase.md` | Test commands |
| `README_ArchDesign.md` | Architecture and design decisions |
| `README_UbiLang.md` | Ubiquitous Language glossary |

*** Add File: /Users/enigmawu/VSCode/MyLLM_Arena/MyStartups/AggregateGenCodeDesc/UserExamples/README_UserExamples.md
# AggregateGenCodeDesc User Examples

## Purpose

Concrete operator-oriented command examples for running `aggregateGenCodeDesc.py`.

Use this document when you want copyable command patterns.
Use `README_UserGuide.md` when you want the full argument contract and support matrix.

## Example Index

1. Git + Algorithm A
2. Git + Algorithm A with logical URL
3. SVN + Algorithm A
4. Algorithm B + local Git replay
5. Algorithm B + commit diff set replay
6. Algorithm B + local SVN workflow via exported commit diff set
7. Algorithm C + embedded blame offline analysis

## 1. Git + Algorithm A

```bash
python3 aggregateGenCodeDesc.py \
  --vcsType git \
  --repoURL /path/to/local/git/repo \
  --repoBranch main \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --scope A \
  --outputFile /tmp/agg-out.json \
  --genCodeDescSetDir /path/to/genCodeDescSet
```

## 2. Git + Algorithm A with logical URL

```bash
python3 aggregateGenCodeDesc.py \
  --vcsType git \
  --repoURL https://example.local/repo/demo.git \
  --workingDir /path/to/local/git/checkout \
  --repoBranch main \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --scope A \
  --outputFile /tmp/agg-out.json \
  --genCodeDescSetDir /path/to/genCodeDescSet
```

## 3. SVN + Algorithm A

```bash
python3 aggregateGenCodeDesc.py \
  --vcsType svn \
  --repoURL file:///path/to/local/svn/repo \
  --repoBranch trunk \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --scope A \
  --outputFile /tmp/agg-out.json \
  --genCodeDescSetDir /path/to/genCodeDescSet
```

## 4. Algorithm B + local Git replay

```bash
python3 aggregateGenCodeDesc.py \
  --vcsType git \
  --repoURL /path/to/local/git/repo \
  --repoBranch main \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --algorithm B \
  --scope A \
  --outputFile /tmp/agg-b-out.json \
  --genCodeDescSetDir /path/to/genCodeDescSet
```

## 5. Algorithm B + commit diff set replay

```bash
python3 aggregateGenCodeDesc.py \
  --vcsType git \
  --repoURL https://example.local/repo/demo \
  --repoBranch main \
  --startTime 2026-03-10 \
  --endTime 2026-03-31 \
  --algorithm B \
  --scope A \
  --outputFile /tmp/agg-b-fixture-out.json \
  --genCodeDescSetDir /path/to/genCodeDescSet \
  --commitDiffSetDir /path/to/commitDiffSet
```

Preferred patch naming:

- `0001_r1_commitDiff.patch`
- `0002_r2_commitDiff.patch`
- `0003_r3_commitDiff.patch`

## 6. Algorithm B + local SVN workflow via exported commit diff set

This is the recommended practical SVN workflow today.

1. Resolve the revisions inside `startTime~endTime`.
2. Export one unified diff patch per revision.
3. Name them in chronological order as `NN_<revisionId>_commitDiff.patch`.
4. Keep matching `<revisionId>_genCodeDesc.json` files in `--genCodeDescSetDir`.
5. Run Algorithm B from the exported patch set.

```bash
python3 aggregateGenCodeDesc.py \
  --vcsType svn \
  --repoURL file:///path/to/local/svn/repo \
  --repoBranch trunk \
  --startTime 2026-03-10 \
  --endTime 2026-03-31 \
  --algorithm B \
  --scope A \
  --outputFile /tmp/agg-b-svn-out.json \
  --genCodeDescSetDir /path/to/genCodeDescSet \
  --commitDiffSetDir /path/to/commitDiffSet
```

## 7. Algorithm C + embedded blame offline analysis

```bash
python3 aggregateGenCodeDesc.py \
  --algorithm C \
  --startTime 2026-03-10 \
  --endTime 2026-03-31 \
  --scope A \
  --outputFile /tmp/agg-c-out.json \
  --genCodeDescSetDir /path/to/algc-v26.04-set
```

## Related Docs

- `README_UserGuide.md`: operator contract, argument meanings, and support matrix
- `README_RunTestCase.md`: test commands
- `README.md`: product scope and measurement definitions
