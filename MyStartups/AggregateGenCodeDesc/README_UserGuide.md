# AggregateGenCodeDesc User Guide

## Purpose

This document is the operator-facing guide for running `aggregateGenCodeDesc.py`.

Use it when you want practical commands, not architecture discussion.

It focuses on:

- what the tool needs as input
- which command to run for common cases
- how to choose `Algorithm A` vs `Algorithm B`
- how `repoURL` and `workingDir` should be used
- what the current support boundary is

For acceptance criteria and roadmap details, use:

- `README_UserStory.md`
- `README_SharedUS_Convergence.md`
- `README_ArchDesign.md`

## Quick Start

The most common current usage is:

1. prepare revision-level `genCodeDesc` metadata under `--genCodeDescSetDir`
2. choose `--vcsType git` or `--vcsType svn`
3. run `Algorithm A` for real repository analysis
4. use `Algorithm B` only when you intentionally want the current narrow replay-based path with `--commitDiffSetDir`

## Current Support Matrix

### Production-oriented path

- `Algorithm A + Git + Scope A`: production target
- `Algorithm A + SVN + Scope A`: production target

### Narrow replay baseline path

- `Algorithm B + Git + Scope A`: supported for the current approved replay scenarios
- `Algorithm B + SVN + Scope A`: supported for the current approved replay scenarios

Important boundary:

- `Algorithm B` is still a narrow replay-based path
- it is good for the currently approved fixture shapes
- it is not yet a claim that all broader history topologies are production-ready

## Prerequisites

### Required runtime

- Python 3
- local Git installed for Git runs
- local SVN installed for SVN runs

### Required inputs

Every run needs:

- `--repoURL`
- `--repoBranch`
- `--startTime`
- `--endTime`

Most useful runs also need:

- `--genCodeDescSetDir`

`Algorithm B` runs additionally require:

- `--algorithm B`
- `--commitDiffSetDir`

## Core Arguments

### `--repoURL`

Logical repository identity.

- For Git local-path runs, this can be the local repository path.
- For Git logical-URL runs such as `https://example.local/repo/demo.git`, this is the metadata identity and output identity, not the checkout path.
- For SVN, this is both the logical repository identity and the live SVN access target.

### `--workingDir`

Git-only helper for logical `repoURL` mode.

Use it when:

- `--vcsType git`
- `--repoURL` is not a local absolute path
- you still want Git commands to run against a local checkout

Do not use it for normal SVN URL-based runs.

### `--genCodeDescSetDir`

Directory containing revision-level metadata files such as:

- `<revisionId>_genCodeDesc.json`

The current runtime validates metadata identity fields, so the metadata `REPOSITORY` block must match the target run.

### `--algorithm`

- `A`: the current production-oriented live-repository path
- `B`: the current narrow replay-based path

Default is `A`.

### `--metric`

Use this explicitly for `Algorithm B` when needed.

Current important values:

- `live_changed_source_ratio`
- `period_added_ai_ratio`

### `--commitDiffSetDir`

Required for the current `Algorithm B` path.

This directory must contain raw unified diff patch files such as:

- `<revisionId>_commitDiff.patch`

## Typical Usage Examples

### 1. Typical Git production-style run with `Algorithm A`

Use this when you have a real local Git repository and local metadata files.

```bash
cd /Users/enigmawu/VSCode/MyLLM_Arena/MyStartups/AggregateGenCodeDesc

python3 aggregateGenCodeDesc.py \
  --vcsType git \
  --repoURL /path/to/local/git/repo \
  --repoBranch main \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --outputFile /tmp/agg-out.json \
  --genCodeDescSetDir /path/to/genCodeDescSet
```

Use this when:

- Git history is available locally
- you want the main live-snapshot metric path
- you are not intentionally testing replay fixtures

### 2. Typical Git run with logical `repoURL` and separate checkout

Use this when metadata identity must use a logical URL, but Git commands still run against a local checkout.

```bash
cd /Users/enigmawu/VSCode/MyLLM_Arena/MyStartups/AggregateGenCodeDesc

python3 aggregateGenCodeDesc.py \
  --vcsType git \
  --repoURL https://example.local/repo/demo.git \
  --workingDir /path/to/local/git/checkout \
  --repoBranch main \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --outputFile /tmp/agg-out.json \
  --genCodeDescSetDir /path/to/genCodeDescSet
```

Use this when:

- metadata records are indexed by a logical Git URL
- you still want to analyze a local checkout

### 3. Typical SVN production-style run with `Algorithm A`

Use this when you want the current production-oriented SVN path.

```bash
cd /Users/enigmawu/VSCode/MyLLM_Arena/MyStartups/AggregateGenCodeDesc

python3 aggregateGenCodeDesc.py \
  --vcsType svn \
  --repoURL file:///path/to/local/svn/repo \
  --repoBranch trunk \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --outputFile /tmp/agg-out.json \
  --genCodeDescSetDir /path/to/genCodeDescSet
```

You can also use an SVN server URL instead of `file:///...` if the environment supports it.

### 4. Typical `Algorithm B` Git replay run

Use this only when you intentionally want the current narrow replay-based path.

```bash
cd /Users/enigmawu/VSCode/MyLLM_Arena/MyStartups/AggregateGenCodeDesc

python3 aggregateGenCodeDesc.py \
  --vcsType git \
  --repoURL https://example.local/repo/demo \
  --repoBranch main \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --algorithm B \
  --metric live_changed_source_ratio \
  --scope A \
  --outputFile /tmp/agg-b-git-out.json \
  --genCodeDescSetDir testdata/us1_live_changed_source_ratio \
  --commitDiffSetDir testdata/us1_live_changed_source_ratio/commitDiffSet
```

### 5. Typical `Algorithm B` SVN replay run

Use this only when you intentionally want the current narrow replay-based path on SVN.

```bash
cd /Users/enigmawu/VSCode/MyLLM_Arena/MyStartups/AggregateGenCodeDesc

python3 aggregateGenCodeDesc.py \
  --vcsType svn \
  --repoURL https://svn.example.com/repos/project \
  --repoBranch trunk \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --algorithm B \
  --metric live_changed_source_ratio \
  --scope A \
  --outputFile /tmp/agg-b-svn-out.json \
  --genCodeDescSetDir testdata/us1_live_changed_source_ratio_svn \
  --commitDiffSetDir testdata/us1_live_changed_source_ratio_svn/commitDiffSet
```

### 6. Current `US-6` style period-added replay example

```bash
cd /Users/enigmawu/VSCode/MyLLM_Arena/MyStartups/AggregateGenCodeDesc

python3 aggregateGenCodeDesc.py \
  --vcsType git \
  --repoURL https://example.local/repo/demo \
  --repoBranch main \
  --startTime 2026-03-10 \
  --endTime 2026-03-31 \
  --algorithm B \
  --scope A \
  --outputFile /tmp/agg-b-period-out.json \
  --genCodeDescSetDir testdata/us6_period_added_ratio \
  --commitDiffSetDir testdata/us6_period_added_ratio/commitDiffSet
```

## Output Shape

Typical output is protocol-shaped JSON such as:

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

## Common Problems And Fixes

### `--workingDir is required for git`

Cause:

- you used a logical Git `repoURL` instead of a local absolute path

Fix:

- add `--workingDir /path/to/local/git/checkout`

### `Metadata repoURL mismatch`

Cause:

- the metadata file and the CLI target do not use the same repository identity string

Fix:

- make `REPOSITORY.repoURL` inside the metadata exactly match the CLI `--repoURL`

### `Protocol file not found for revision`

Cause:

- the metadata directory does not contain the required revision-level `genCodeDesc` file

Fix:

- add the missing `<revisionId>_genCodeDesc.json`

### `Commit diff patch file not found`

Cause:

- the current `Algorithm B` replay sequence expects a patch file that is missing from `--commitDiffSetDir`

Fix:

- add the missing `<revisionId>_commitDiff.patch`

### `--vcsType must be one of: git, svn`

Cause:

- unsupported VCS value

Fix:

- use `git` or `svn`

## Which Document Should I Read Next?

- Use `README.md` for product scope and metric definition.
- Use `README_UserStory.md` for story-level acceptance criteria.
- Use `README_SharedUS_Convergence.md` for the production convergence roadmap.
- Use `README_RunTestCase.md` for test commands.
- Use `tests/README_US1_ManualInstruction.md` for a more detailed US-1 manual walkthrough.
