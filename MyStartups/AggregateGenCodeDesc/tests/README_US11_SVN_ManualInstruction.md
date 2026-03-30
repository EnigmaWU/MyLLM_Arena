# US-11 SVN Manual Instruction

## Purpose

This document describes the deep-history SVN verification scenario for US-11.

The SVN variant keeps the same conceptual target as the Git US-11 scenario: a long single-path revision chain where only the latest effective surviving attribution at `endTime` should count.

## Scenario Shape

The automated verification is implemented in [tests/test_us11_deep_history_preserves_attribution_svn_tdd.py](tests/test_us11_deep_history_preserves_attribution_svn_tdd.py).

The reused fixture payload lives under [testdata/us11_deep_history_preserves_attribution](testdata/us11_deep_history_preserves_attribution).

The history uses one file, `trunk/src/deep_history.py`, with five final live lines:

1. line 1 stays pre-window and must be excluded
2. line 2 ends as human/unattributed after several earlier AI states
3. line 3 ends as `100%-ai`
4. line 4 ends as `60%-ai`
5. line 5 ends as human/unattributed after an earlier AI state is reset

## Revision Map

The SVN test creates nine revisions mirroring the Git US-11 chain:

1. `us11-svn-r1`
   Pre-window baseline.

2. `us11-svn-r2`
   Early AI rewrite of lines 2 and 5.

3. `us11-svn-r3`
   Partial-AI rewrite of line 3 and human reset of line 2.

4. `us11-svn-r4`
   Partial-AI rewrite of line 2 and human reset of line 3.

5. `us11-svn-r5`
   Final human rewrite of line 2.

6. `us11-svn-r6`
   Partial-AI rewrite of line 4.

7. `us11-svn-r7`
   Final human rewrite of line 5.

8. `us11-svn-r8`
   Final full-AI rewrite of line 3.

9. `us11-svn-r9`
   Docs-only final revision.

As with SVN US-10, the reused fixture payload is converted so each `fileName` becomes `trunk/src/deep_history.py` and the repository section uses `vcsType = svn` and `repoBranch = trunk`.

## Expected Final Result

The final aggregate should be:

- `totalCodeLines = 4`
- `fullGeneratedCodeLines = 1`
- `partialGeneratedCodeLines = 1`

## Final Per-Line Expectation

At `endTime`, the surviving in-scope lines should resolve as follows:

1. line 2 -> human/unattributed from `us11-svn-r5`
2. line 3 -> `100%-ai` from `us11-svn-r8`
3. line 4 -> `60%-ai` from `us11-svn-r6`
4. line 5 -> human/unattributed from `us11-svn-r7`

## What This Scenario Proves

This SVN scenario proves all of the following together:

1. long same-path linear history works under real SVN revision ancestry, not only Git commit ancestry
2. the current SVN parent-revision approximation is sufficient for the present deep-history US-11 slice
3. repeated rewrites do not leak stale AI states into the final aggregate result
4. docs-only final revisions remain harmless in the SVN path as well

## Verification Command

```bash
cd /Users/enigmawu/VSCode/MyLLM_Arena/MyStartups/AggregateGenCodeDesc
python3 -m unittest tests.test_us11_deep_history_preserves_attribution_svn_tdd -v
```

For full regression validation:

```bash
cd /Users/enigmawu/VSCode/MyLLM_Arena/MyStartups/AggregateGenCodeDesc
python3 -m unittest discover tests -v
```

## Debug Logging Expectations

When `--logLevel debug` is used, the test expects to see:

1. one `LiveLine ... aggregate ...` record for each included final live line
2. `Skip out-of-window line ...` for the unchanged pre-window line
3. transition hints showing that the latest effective SVN revision can replace earlier attribution states in the chain

The most important transition hints remain:

1. `50%-ai -> human/unattributed`
2. `human/unattributed -> 60%-ai`
3. `human/unattributed -> 100%-ai`

## Relationship To Git US-11

This is a true parity-style port.

The Git and SVN US-11 variants should agree on:

1. the final summary totals
2. the final per-line classifications
3. the interpretation of later human resets and later final AI rewrites

The main mechanical difference is only the branch-qualified file naming required by SVN metadata joins.