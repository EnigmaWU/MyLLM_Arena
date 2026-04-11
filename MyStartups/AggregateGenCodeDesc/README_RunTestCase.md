# AggregateGenCodeDesc Test Run Guide

## Purpose

This document explains how to run the current AggregateGenCodeDesc test cases clearly and consistently.

It complements:

- `README.md` for product and CLI scope
- `README_UserStoryNG.md` for the authoritative next-generation user stories and acceptance criteria
- `README_UserStory.md` for legacy migration context only
- `tests/README.md` for real repository and manual verification notes

## Verification Tiers

The repository uses three practical verification tiers.

### 1. Fast

Use `Fast` verification for routine local development and normal CI.

Typical properties:

- fixture-driven checks
- short-running real repository tests
- current narrow Algorithm B convergence checks
- expected to finish quickly enough for frequent runs

### 2. Heavy

Use `Heavy` verification for production-readiness checks and scheduled daily integration.

Typical properties:

- production-scale Git/SVN histories
- long-running branch-heavy or deep-history checks
- expected to take tens of minutes and possibly about one hour

### 3. Experimental

Use `Experimental` verification for exploratory tracks that must not silently change the accepted contract.

Current example:

- `experimental_svn`

## Current Story Mapping

- `US-1` to `US-12`: current `Fast` tier scenarios
- `US-6`: first shared US example; current executable path is the narrow `Algorithm B` offline baseline
- `US-1` to `US-12`: current narrow live-snapshot `Algorithm B` convergence evidence is carried by the focused regression stack, with support still intentionally scoped to approved shapes, and with the `US-2`/`US-3`/`US-4`, `US-5`/`US-7`, `US-8`, `US-10`/`US-11`, and `US-12` slices now including focused real local-Git replay proof for the accepted shapes
- `US-13` and `US-14`: current `Heavy` tier production-scale acceptance cases
- `US-20`: `Fast` tier Scope B (source code with comments) end-to-end verification
- `US-21`: `Fast` tier Scope C (documentation text lines) end-to-end verification
- `US-22`: `Fast` tier Scope D (all text: source + documentation) end-to-end verification
- `US-23`: `Fast` tier scope parity matrix — cross-scope isolation verification for all four scopes
- `US-24`: `Fast` tier Algorithm B + Scope B (source code with comments via replay)
- `US-25`: `Fast` tier Algorithm B + Scope C (documentation text lines via replay)
- `US-26`: `Fast` tier Algorithm B + Scope D (all text: source + documentation via replay)
- `US-27`: `Fast` tier cross-algorithm × cross-scope parity matrix — verifies Algorithm A and B produce identical results for all scopes
- `US-28`: `Fast` tier production hardening — scope validation at input boundary and file-size OOM guard
- `US-15`: `Fast` tier Algorithm B period-added single-branch baseline (no merges, no renames)
- `US-16`: `Fast` tier Algorithm B period-added with deletions, resets, and mixed rewrites
- `US-17`: `Fast` tier Algorithm B period-added Git rename and move handling
- `US-18`: `Fast` tier Algorithm B period-added merge-aware contribution
- `US-19`: `Fast` tier Algorithm B period-added SVN subset via offline fixtures
- experimental SVN lineage work: separate `Experimental` tier

## Recommended Commands

### Fast: current focused Algorithm B stack

Use this when working on the current narrow `Algorithm B` convergence stack:

```bash
python3 -m pytest -q \
  tests/test_algorithm_b_live_snapshot_foundation_tdd.py \
  tests/test_us2_us3_us4_algorithm_b_regression_tdd.py \
  tests/test_us5_us7_algorithm_b_regression_tdd.py \
  tests/test_us8_us12_algorithm_b_regression_tdd.py \
  tests/test_us10_us11_algorithm_b_regression_tdd.py \
  tests/test_us9_algorithm_b_contract_parity_tdd.py
```

### Fast: default non-heavy, non-experimental suite

Use this for broad routine verification without the production-scale or experimental tracks:

```bash
python3 -m pytest -q -m "not production_scale and not long_running and not experimental_svn"
```

### Fast: single shared US-6 baseline

Use this when validating the current shared `US-6` requirement through the `Algorithm B` acceptance track:

```bash
python3 -m pytest -q \
  tests/test_cli_algorithm_flag_tdd.py \
  tests/test_commit_diff_line_attribution_tdd.py
```

### Heavy: production gate

Use this for explicit production-scale verification:

```bash
bash run_production_gate.sh
```

Equivalent direct pytest command:

```bash
python3 -m pytest -q -m "production_scale" \
  tests/test_us13_git_production_scale_local_repo_tdd.py \
  tests/test_us14_svn_production_scale_local_repo_tdd.py
```

### Experimental: SVN lineage track

Use this only when working on exploratory SVN lineage behavior:

```bash
python3 -m pytest -q -m experimental_svn tests/test_real_svn_lineage_experiments.py
```

## Daily Integration Suggestion

For a daily integration cadence, use:

1. one `Fast` suite run on every normal change
2. one `Heavy` production gate run once per day or before release decisions
3. one separate `Experimental` run only when that track is actively being changed

Recommended daily integration command:

```bash
bash run_production_gate.sh
```

## How To Read Test Intent

- If a test is tied to `testdata/`, it is usually fixture-oriented and closer to `Fast` verification.
- If a test creates a real Git or SVN repository, it is integration-style verification.
- If a test is marked with `production_scale` or `long_running`, treat it as `Heavy`.
- If a test is marked with `experimental_svn`, treat it as exploratory rather than accepted contract coverage.

## Algorithm B Production Boundary

`Algorithm B` is production-ready. All four entry-point paths (local Git live-snapshot, local Git period-added, commit-diff-set live-snapshot, commit-diff-set period-added) are covered by the 40-test `TestsNG-AlgB/` suite across Scopes A, B, C, and D, and by the legacy fixture-based tests.

Supported in production:

- local Git live-snapshot and period-added replay through `--algorithm B` when Git history is available via an absolute `repoURL` or via logical `repoURL` plus `--workingDir`
- Git and SVN commit-diff-set replay through `--algorithm B --commitDiffSetDir` for Scopes A, B, C, D (Git) and Scope A (SVN)
- all four Scopes (A, B, C, D) for Git; Scope A for SVN commit-diff-set
- timing logs (`elapsed=` / `costSeconds=`) emitted for all four entry-point paths
- explicit Git/SVN contract parity on the `US-1` baseline shape

Known unsupported configurations:

- first-patch multi-hunk base reconstruction
- generic non-local Git replay without either `--commitDiffSetDir` or a local checkout behind `--repoURL` / `--workingDir`
- full generic merge-graph-aware accounting beyond the approved replay fixtures

## When To Add New Commands Here

Update this document when:

- a new `Fast` suite becomes the default developer workflow
- a new `Heavy` production or daily integration gate is added
- a new shared US gets a stable executable acceptance track
- marker usage changes in `pytest.ini`
