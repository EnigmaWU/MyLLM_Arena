# SVN Lineage Experiments

## Purpose

This document separates exploratory SVN lineage behavior from the accepted production contract.

The production contract for large-scale SVN validation is currently US-14, which is intentionally based on stable trunk reintegration revisions. This experiment file exists so stronger or narrower lineage claims can be tested without silently expanding what US-14 is supposed to prove.

## Automated Coverage

The experiments live in [tests/test_real_svn_lineage_experiments.py](tests/test_real_svn_lineage_experiments.py).

## Current Experiments

1. branch-owned file merge can preserve branch-origin path information in `svn blame -g --xml`
2. same-file multi-branch merges still collapse to trunk-side merge revisions often enough that branch-tip claims are unsafe as a production contract

## Why This Is Separate From US-14

US-14 is a production-scale acceptance scenario.
It should stay stable and defensible.

These experiments are narrower and more exploratory:

1. they help explain what current SVN blame behavior can support
2. they guard against accidental overclaims in docs or tests
3. they make future SVN lineage improvements measurable without changing the accepted production gate prematurely

## Verification Command

```bash
cd /Users/enigmawu/VSCode/MyLLM_Arena/MyStartups/AggregateGenCodeDesc
python3 -m pytest -q -m experimental_svn tests/test_real_svn_lineage_experiments.py
```
