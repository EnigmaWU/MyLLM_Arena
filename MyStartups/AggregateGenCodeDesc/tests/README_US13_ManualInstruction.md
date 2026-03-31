# US-13 Manual Instruction

## Purpose

This document describes the production-scale Git verification scenario for US-13.

US-13 raises the current Git acceptance bar to a large local repository with both topology and scale pressure:

1. `100+` branches
2. `1000+` commits
3. hybrid merge fan-in through integration branches, octopus merges, and direct release merges
4. one final `release -> main` merge that becomes the end revision

## Automated Coverage

The automated verification is implemented in [tests/test_us13_git_production_scale_local_repo_tdd.py](tests/test_us13_git_production_scale_local_repo_tdd.py).

Its golden input and output artifacts live under [testdata/us13_git_production_scale_local_repo](testdata/us13_git_production_scale_local_repo).

## Scenario Shape

The repository shape is intentionally large but deterministic:

1. baseline commit creates `100` final source files under `src/features/`
2. `100` feature branches are created from `main`
3. each feature branch receives `10` commits on its owned file
4. the first `50` branches are merged through `5` integration branches into `release`
5. the next `25` branches are merged into `release` by octopus merges
6. the final `25` branches are merged directly into `release`
7. `release` is merged back into `main`

## Expected Final Result

The golden output in `expected_result.json` requires:

1. `totalCodeLines = 200`
2. `fullGeneratedCodeLines = 80`
3. `partialGeneratedCodeLines = 60`

That comes from `100` final files, each contributing two in-scope live code lines.

## Additional Production Assertion

The test also wraps the real metadata provider and verifies that each origin revision is loaded exactly once even though each revision contributes two final live lines.

## Verification Command

```bash
cd /Users/enigmawu/VSCode/MyLLM_Arena/MyStartups/AggregateGenCodeDesc
python3 -m unittest tests.test_us13_git_production_scale_local_repo_tdd -v
```
