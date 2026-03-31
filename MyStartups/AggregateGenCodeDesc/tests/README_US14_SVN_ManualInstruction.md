# US-14 SVN Manual Instruction

## Purpose

This document describes the production-scale SVN verification scenario for US-14.

US-14 raises the SVN acceptance bar to a large local repository with branch-copy scale and reintegration pressure:

1. `100+` branch copies
2. `1000+` revisions
3. `10` content commits per branch copy
4. batched trunk reintegration commits after branch work completes

## Automated Coverage

The automated verification is implemented in [tests/test_us14_svn_production_scale_local_repo_tdd.py](tests/test_us14_svn_production_scale_local_repo_tdd.py).

Its golden input and output artifacts live under [testdata/us14_svn_production_scale_local_repo](testdata/us14_svn_production_scale_local_repo).

## Scenario Shape

The repository shape is intentionally large but keeps the attribution contract stable under current SVN behavior:

1. baseline commit creates `100` trunk files under `trunk/src/`
2. `100` branch copies are created from `trunk`
3. each branch copy receives `10` commits on one owned file
4. trunk then reintegrates those final branch results in batches of `10` files per commit
5. a final docs-only trunk revision becomes the end revision

This yields more than `1000` revisions while keeping the final live-line attribution tied to stable trunk integration revisions.

## Expected Final Result

The golden output in `expected_result.json` requires:

1. `totalCodeLines = 200`
2. `fullGeneratedCodeLines = 80`
3. `partialGeneratedCodeLines = 60`

## Additional Production Assertion

The test wraps the real metadata provider and verifies that each trunk integration revision is loaded exactly once even though each such revision contributes many final live lines.

## Verification Command

```bash
cd /Users/enigmawu/VSCode/MyLLM_Arena/MyStartups/AggregateGenCodeDesc
python3 -m unittest tests.test_us14_svn_production_scale_local_repo_tdd -v
```
