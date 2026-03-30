# US-12 SVN Manual Instruction

## Purpose

This document describes the branch-heavy SVN verification scenario for US-12.

The SVN goal is the same as the Git story: many feature branches are merged into the main line during one requested window, and the final live lines must still preserve defensible per-line attribution.

The important caveat is that real SVN blame behavior differs from Git blame for same-file repeated-merge histories. Because of that, the current SVN US-12 scenario uses a multi-file branch-heavy merge shape rather than a literal copy of the Git same-file branch matrix.

## Scenario Shape

The automated verification is implemented in [tests/test_us12_many_merged_branches_preserve_attribution_svn_tdd.py](tests/test_us12_many_merged_branches_preserve_attribution_svn_tdd.py).

The test reuses the final expected summary from [testdata/us12_many_merged_branches_preserve_attribution](testdata/us12_many_merged_branches_preserve_attribution), but the repository history is an SVN-specific analogue rather than a line-for-line fixture replay.

The history uses seven final source files under `trunk/src/`:

1. `main_human.py`
2. `alpha_branch.py`
3. `beta_branch.py`
4. `gamma_branch.py`
5. `delta_branch.py`
6. `epsilon_branch.py`
7. `main_tail.py`

Each file has three live lines. The middle line is the in-scope line. The first and third lines remain pre-window and must be excluded.

## Revision Map

The SVN history shape is:

1. `us12-svn-r1`
   Pre-window baseline creates the seven source files.

2. `us12-svn-r2`
   Mainline human rewrite in `trunk/src/main_human.py`.

3. `us12-svn-r3`
   `feature-alpha` full-AI rewrite in `branches/feature-alpha/src/alpha_branch.py`.

4. `us12-svn-r5`
   `feature-beta` partial-AI rewrite in `branches/feature-beta/src/beta_branch.py`.

5. `us12-svn-r7`
   `feature-gamma` full-AI rewrite in `branches/feature-gamma/src/gamma_branch.py`.

6. `us12-svn-r8`
   Mainline human rewrite in `trunk/src/main_tail.py` before the `feature-gamma` merge is committed.

7. `us12-svn-r10`
   `feature-delta` partial-AI rewrite in `branches/feature-delta/src/delta_branch.py`.

8. `us12-svn-r12`
   `feature-epsilon` full-AI rewrite in `branches/feature-epsilon/src/epsilon_branch.py`.

9. `us12-svn-r14`
   Mainline human rewrite of `trunk/src/epsilon_branch.py` after the earlier branch merge, resetting the earlier AI state.

10. `us12-svn-r15`
    Docs-only final revision.

Intermediate merge revisions exist between those content revisions, but the test assertions focus on the content-origin revisions above.

## Expected Final Result

The final aggregate should be:

- `totalCodeLines = 7`
- `fullGeneratedCodeLines = 2`
- `partialGeneratedCodeLines = 2`

## Final Per-Line Expectation

At `endTime`, the in-scope lines should resolve as follows:

1. `src/main_human.py:2` -> human/unattributed from `us12-svn-r2`
2. `src/alpha_branch.py:2` -> `100%-ai` from `branches/feature-alpha` revision `us12-svn-r3`
3. `src/beta_branch.py:2` -> `70%-ai` from `branches/feature-beta` revision `us12-svn-r5`
4. `src/gamma_branch.py:2` -> `100%-ai` from `branches/feature-gamma` revision `us12-svn-r7`
5. `src/delta_branch.py:2` -> `40%-ai` from `branches/feature-delta` revision `us12-svn-r10`
6. `src/epsilon_branch.py:2` -> human/unattributed from `us12-svn-r14`
7. `src/main_tail.py:2` -> human/unattributed from `us12-svn-r8`

## What This Scenario Proves

This SVN scenario proves all of the following together:

1. multiple real SVN branches can merge back into `trunk` while preserving usable branch-origin attribution for branch-owned files
2. `svn blame -g --xml` plus branch-qualified metadata joins are strong enough for branch-heavy per-line attribution when the merged source path remains distinct
3. later mainline human rewrites can still override earlier branch-origin AI states
4. the current SVN implementation can accept feature-branch metadata whose `repoBranch` differs from the query branch and still compute the correct final result

## Why This Is Not A Literal Git Port

The Git US-12 main scenario uses one shared file whose different lines are rewritten on different branches and merged back over time.

Real SVN blame does not preserve that shape as cleanly:

1. same-file cherry-picked branch merges often collapse surviving line ownership to trunk-side merge revisions
2. that makes a literal same-file Git-to-SVN parity test misleading rather than informative
3. the current SVN US-12 scenario therefore uses a multi-file branch-heavy analogue that real SVN blame can preserve defensibly

## Verification Command

```bash
cd /Users/enigmawu/VSCode/MyLLM_Arena/MyStartups/AggregateGenCodeDesc
python3 -m unittest tests.test_us12_many_merged_branches_preserve_attribution_svn_tdd -v
```

For full regression validation:

```bash
cd /Users/enigmawu/VSCode/MyLLM_Arena/MyStartups/AggregateGenCodeDesc
python3 -m unittest discover tests -v
```

## Debug Logging Expectations

When `--logLevel debug` is used, the test expects to see:

1. `Metadata repoBranch differs` messages for branch-origin revisions
2. one `LiveLine ... aggregate ...` record for each in-scope file
3. `Skip out-of-window line ...` messages for the pre-window first and third lines in representative files

## Closer-Symmetry Exploration Result

The repository now also contains an exploratory real-behavior SVN test showing why a closer same-file Git/SVN symmetry claim is unsafe today.

See [tests/test_real_svn_same_file_merge_limitation.py](tests/test_real_svn_same_file_merge_limitation.py).

That test demonstrates that even when different branches change different lines of one shared file and merge back cleanly, `svn blame -g --xml` can still attribute the final lines to trunk-side merge revisions rather than the branch-origin revision/path. That is why the multi-file branch-heavy US-12 SVN scenario is currently the strongest defensible production-facing check.