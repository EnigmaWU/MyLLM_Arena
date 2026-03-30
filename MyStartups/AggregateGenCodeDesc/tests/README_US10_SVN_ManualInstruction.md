# US-10 SVN Manual Instruction

## Purpose

This document describes the large-snapshot SVN verification scenario for US-10.

The SVN variant keeps the same breadth-oriented goal as the Git US-10 scenario: many files survive in the final snapshot, each with one in-scope live line whose final origin must be resolved independently.

The important difference is repository shape:

1. the live branch is `trunk`
2. revision metadata paths are branch-qualified as `trunk/...`
3. all verification uses a real local SVN repository and real `svn blame`

## Scenario Shape

The automated verification is implemented in [tests/test_us10_large_repository_snapshot_svn_tdd.py](tests/test_us10_large_repository_snapshot_svn_tdd.py).

The protocol-shaped fixture payload reused by that test lives under [testdata/us10_large_repository_snapshot](testdata/us10_large_repository_snapshot).

The repository history uses eight source files under `trunk/`:

1. `trunk/src/core/alpha.py`
2. `trunk/src/core/beta.py`
3. `trunk/src/core/gamma.py`
4. `trunk/src/services/delta.py`
5. `trunk/src/services/epsilon.py`
6. `trunk/src/utils/zeta.py`
7. `trunk/src/utils/eta.py`
8. `trunk/src/app/theta.py`

Each file keeps three final live lines. The first and third lines remain pre-window and must be excluded. The middle line is the one in-scope live line for that file.

## Revision Map

The SVN test creates five revisions that mirror the Git US-10 shape:

1. `us10-svn-r1`
   Pre-window baseline for all eight files.

2. `us10-svn-r2`
   In-window updates to `alpha`, `beta`, and `gamma`.

3. `us10-svn-r3`
   In-window updates to `delta` and `epsilon`, plus a human reset of `beta`.

4. `us10-svn-r4`
   In-window updates to `zeta`, `eta`, and `theta`.

5. `us10-svn-r5`
   Docs-only final revision.

The reused fixture metadata is converted at runtime so that every `fileName` becomes `trunk/...` and every repository section uses `vcsType = svn` and `repoBranch = trunk`.

## Expected Final Result

The final aggregate should be:

- `totalCodeLines = 8`
- `fullGeneratedCodeLines = 3`
- `partialGeneratedCodeLines = 3`

## Final Per-Line Expectation

At `endTime`, the surviving in-scope lines should resolve as follows:

1. `trunk/src/core/alpha.py:2` -> `100%-ai` from `us10-svn-r2`
2. `trunk/src/core/beta.py:2` -> human/unattributed from `us10-svn-r3`
3. `trunk/src/core/gamma.py:2` -> `50%-ai` from `us10-svn-r2`
4. `trunk/src/services/delta.py:2` -> `100%-ai` from `us10-svn-r3`
5. `trunk/src/services/epsilon.py:2` -> `60%-ai` from `us10-svn-r3`
6. `trunk/src/utils/zeta.py:2` -> `100%-ai` from `us10-svn-r4`
7. `trunk/src/utils/eta.py:2` -> human/unattributed from `us10-svn-r4`
8. `trunk/src/app/theta.py:2` -> `40%-ai` from `us10-svn-r4`

## What This Scenario Proves

This SVN scenario proves all of the following together:

1. the broad-snapshot US-10 semantics hold under real SVN history, not only Git
2. the branch-qualified metadata path conversion from `src/...` to `trunk/src/...` is sufficient for same-path SVN joins
3. repeated reuse of the same origin revision across many files still produces the correct final aggregate
4. docs-only final revisions do not disturb the final source-code result in SVN either

## Verification Command

```bash
cd /Users/enigmawu/VSCode/MyLLM_Arena/MyStartups/AggregateGenCodeDesc
python3 -m unittest tests.test_us10_large_repository_snapshot_svn_tdd -v
```

For full regression validation:

```bash
cd /Users/enigmawu/VSCode/MyLLM_Arena/MyStartups/AggregateGenCodeDesc
python3 -m unittest discover tests -v
```

## Debug Logging Expectations

When `--logLevel debug` is used, the test expects to see:

1. one `LiveLine ... aggregate ...` record for each included final live line across all eight files
2. `Skip out-of-window line ...` messages for unchanged pre-window lines
3. `Reuse cached genCodeDesc for revision ...` messages because multiple files share the same SVN origin revision in this broad snapshot
4. transition hints showing later resets and partial-AI transitions still behave as expected

## Relationship To Git US-10

This scenario is intentionally a close SVN parity check rather than a new story shape.

The Git and SVN US-10 variants should agree on:

1. the revision-to-result mapping
2. the final summary totals
3. the line-by-line classification semantics

The key implementation difference is only that SVN metadata joins use `trunk/...` file names instead of Git's branch-relative `src/...` paths.