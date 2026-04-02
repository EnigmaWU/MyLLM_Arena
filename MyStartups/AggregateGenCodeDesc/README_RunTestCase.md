# AggregateGenCodeDesc Test Run Guide

## Purpose

This document explains how to run the current AggregateGenCodeDesc test cases clearly and consistently.

It complements:

- `README.md` for product and CLI scope
- `README_UserStory.md` for shared user stories and acceptance criteria
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
- `US-1` to `US-12`: current narrow live-snapshot `Algorithm B` convergence evidence is carried by the focused regression stack, with support still intentionally scoped to approved fixture shapes
- `US-13` and `US-14`: current `Heavy` tier production-scale acceptance cases
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

## Current Algorithm B Boundary

The current executable `Algorithm B` path is intentionally narrow.

Supported today:

- Git and SVN fixture-driven replay through `--algorithm B --commitDiffSetDir`
- narrow live-snapshot replay for the approved fixture shapes behind `US-1`, `US-2`, `US-3`, `US-4`, `US-5`, `US-7`, `US-8`, `US-10`, `US-11`, and `US-12`
- narrow offline period replay for the approved `US-6` fixture shape
- explicit Git/SVN contract parity for `US-9` on the approved `US-1` baseline shape

Explicitly unsupported today:

- first-patch multi-hunk base reconstruction
- broader Git/SVN parity claims beyond the approved baseline shapes
- full generic merge-graph-aware accounting beyond the approved replay fixtures
- blanket production-scale `Algorithm B` support claims for the `Heavy` gates

## When To Add New Commands Here

Update this document when:

- a new `Fast` suite becomes the default developer workflow
- a new `Heavy` production or daily integration gate is added
- a new shared US gets a stable executable acceptance track
- marker usage changes in `pytest.ini`
