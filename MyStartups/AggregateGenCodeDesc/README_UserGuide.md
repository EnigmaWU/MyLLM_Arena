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
| **B** (replay, local Git) | Git | ✅ supported | ✅ supported | ✅ supported | ✅ supported |
| **B** (replay, offline fixtures) | Git | ✅ supported | ✅ supported | ✅ supported | ✅ supported |
| **B** (replay, offline fixtures) | SVN | ✅ supported | — | — | — |

**Algorithm A** is the recommended production path. It works against a live repository checkout.

**Algorithm B** replays commit diffs to reconstruct line states. It is designed for two modes:

- **Local Git replay**: reads diffs directly from a local Git checkout
- **Offline fixture replay**: reads pre-exported patch files from `--commitDiffSetDir` (works with both Git and SVN-sourced fixtures for Scope A)

## Prerequisites

- Python 3.10+
- Git installed locally (for Git runs)
- SVN installed locally (for SVN runs)

## Arguments Reference

### Required for every run

| Argument | Description |
|----------|-------------|
| `--repoURL` | Repository identity. For Git, can be a local path (`/path/to/repo`) or a logical URL (`https://...`). For SVN, the server or `file:///` URL. |
| `--repoBranch` | Branch name (e.g. `main`, `trunk`). |
| `--startTime` | Start date in ISO-8601 format (e.g. `2026-03-01`). |
| `--endTime` | End date in ISO-8601 format (e.g. `2026-03-31`). |

### Commonly used

| Argument | Default | Description |
|----------|---------|-------------|
| `--genCodeDescSetDir` | — | Directory containing `<revisionId>_genCodeDesc.json` metadata files. The `REPOSITORY` block inside each file must match the CLI `--repoURL`. |
| `--outputFile` | stdout | Path to write the JSON result. |
| `--scope` | `A` | Which files and lines to count. See [Scope](#--scope) below. |
| `--algorithm` | `A` | `A` for live-repository analysis, `B` for replay-based analysis. |
| `--vcsType` | `git` | `git` or `svn`. |

### Algorithm B specific

| Argument | Description |
|----------|-------------|
| `--commitDiffSetDir` | Directory of pre-exported patch files for offline replay. Required for fixture-driven Algorithm B. Must be paired with `--genCodeDescSetDir`. |

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

### `--commitDiffSetDir` contract

When using Algorithm B with offline fixtures:

- Pair `--commitDiffSetDir` with `--genCodeDescSetDir` — they are the diff side and metadata side of the same replay run.
- Every replayed revision needs both `<timeSeq>_<revisionId>_commitDiff.patch` and `<revisionId>_genCodeDesc.json`.
- If `query.json` provides `includedRevisionIds`, that list defines the replay sequence; extra patch files are ignored.
- Otherwise, the `<timeSeq>` filename prefix determines replay order.
- Legacy `<revisionId>_commitDiff.patch` naming is accepted for older fixtures, but new fixtures should use the time-sequenced form.
- Do not mix legacy and time-sequenced naming in the same directory.
- Patch artifacts may originate from Git or SVN history but must be in unified diff format.

## Usage Examples

### 1. Git + Algorithm A (production)

The most common case: analyze a local Git repository.

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

To count documentation lines instead of code lines, change `--scope A` to `--scope C`.
To count everything (source + docs), use `--scope D`.

### 2. Git + Algorithm A with logical URL

When metadata uses a logical URL but Git commands run against a local checkout:

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

### 3. SVN + Algorithm A (production)

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

You can also use an SVN server URL (e.g. `svn://host/repo`) instead of `file:///`.

### 4. Algorithm B — local Git replay

Replay commit diffs from a live Git checkout.

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

Scopes B, C, and D are also supported — just change `--scope`.

### 5. Algorithm B — offline fixture replay

Replay from pre-exported patch files. No live repository access needed.

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
  --genCodeDescSetDir testdata/us1_live_changed_source_ratio \
  --commitDiffSetDir testdata/us1_live_changed_source_ratio/commitDiffSet
```

SVN-sourced fixtures also work for Scope A — just change `--vcsType svn` and point to SVN fixture directories.

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
| `README_UserStory.md` | Story-level acceptance criteria |
| `README_SharedUS_Convergence.md` | Production convergence roadmap (completed) |
| `README_RunTestCase.md` | Test commands |
| `README_ArchDesign.md` | Architecture and design decisions |
| `README_UbiLang.md` | Ubiquitous Language glossary |
