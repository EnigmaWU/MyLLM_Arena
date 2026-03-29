# US-11 Manual Instruction

## Purpose

This document describes the deep-history Git verification scenario for US-11.

US-11 focuses on long revision chains on one branch. It checks that many intermediate rewrites do not distort the final live result and that only the latest effective surviving attribution is counted at `endTime`.

This scenario is intentionally different from US-7 and US-12:

1. US-7 mixes several transitions in one short history window
2. US-12 stresses branch and merge topology
3. US-11 stresses repeated rewrites on the same live lines over a longer single-branch chain

## Scenario Shape

The automated verification is implemented in [tests/test_us11_deep_history_preserves_attribution_tdd.py](tests/test_us11_deep_history_preserves_attribution_tdd.py).

The protocol-shaped revision metadata used by that test lives under [testdata/us11_deep_history_preserves_attribution](testdata/us11_deep_history_preserves_attribution).

The history uses one source file, `src/deep_history.py`, with five final live lines.

1. line 1 is unchanged from before the requested window and must be excluded
2. line 2 bounces through AI, human, partial-AI, then human again and must end as human/unattributed
3. line 3 bounces through partial-AI, human, then full-AI and must end as `100%-ai`
4. line 4 stays human for most of the chain and is only later rewritten as partial-AI
5. line 5 becomes full-AI early in the chain but is later reset by a human rewrite

The history uses nine commits:

1. pre-window baseline
2. early full-AI rewrite of lines 2 and 5
3. human reset of line 2 and partial-AI rewrite of line 3
4. later partial-AI rewrite of line 2 and human reset of line 3
5. final human rewrite of line 2
6. partial-AI rewrite of line 4
7. final human rewrite of line 5
8. final full-AI rewrite of line 3
9. docs-only final commit after source stabilization

## Revision Map

The fixture files and repository revisions align as follows:

1. `01_genCodeDesc.json` -> `us11-r1`
   Pre-window baseline. No AI-attributed lines.

2. `02_genCodeDesc.json` -> `us11-r2`
   Early full-AI rewrite of line 2 and line 5.

3. `03_genCodeDesc.json` -> `us11-r3`
   Partial-AI rewrite of line 3 at 40% while line 2 is reset by a human.

4. `04_genCodeDesc.json` -> `us11-r4`
   Partial-AI rewrite of line 2 at 50% while line 3 is reset by a human.

5. `05_genCodeDesc.json` -> `us11-r5`
   Final human rewrite of line 2.

6. `06_genCodeDesc.json` -> `us11-r6`
   Partial-AI rewrite of line 4 at 60%.

7. `07_genCodeDesc.json` -> `us11-r7`
   Final human rewrite of line 5.

8. `08_genCodeDesc.json` -> `us11-r8`
   Final full-AI rewrite of line 3.

9. `us11-r9`
   Docs-only final commit. This becomes the final repository revision in the aggregate output.

## Expected Final Result

The final aggregate should be:

- `totalCodeLines = 4`
- `fullGeneratedCodeLines = 1`
- `partialGeneratedCodeLines = 1`

## Final Per-Line Expectation

At `endTime`, the surviving in-scope lines should resolve as follows:

1. line 2 -> human/unattributed from `us11-r5`
2. line 3 -> `100%-ai` from `us11-r8`
3. line 4 -> `60%-ai` from `us11-r6`
4. line 5 -> human/unattributed from `us11-r7`

The excluded live lines should be:

- line 1, unchanged from before the requested window

## What This Scenario Proves

This one scenario verifies all of the following together:

1. a long single-branch revision chain still resolves each surviving line by its latest effective origin
2. earlier AI states do not leak into the final result after later human rewrites
3. earlier human states do not block a later final AI rewrite from becoming the effective attribution
4. the final aggregate depends only on the current live line origins, not on how many intermediate rewrites preceded them
5. a docs-only final commit does not disturb the stabilized source-code result

## Verification Command

```bash
cd /Users/enigmawu/VSCode/MyLLM_Arena/MyStartups/AggregateGenCodeDesc
python3 -m unittest tests.test_us11_deep_history_preserves_attribution_tdd -v
```

For full regression validation:

```bash
cd /Users/enigmawu/VSCode/MyLLM_Arena/MyStartups/AggregateGenCodeDesc
python3 -m unittest discover tests -v
```

## Debug Logging Expectations

When `--logLevel debug` is used, the test expects to see:

1. one `LiveLine ... aggregate ...` record for each included final live line
2. one `Skip out-of-window line ...` record for the unchanged pre-window line
3. `best_effort_transition=` hints showing that later revisions can reset or replace earlier ownership in the chain

The most important transition hints in this scenario are:

1. `50%-ai -> human/unattributed` for the final reset of line 2
2. `human/unattributed -> 60%-ai` for the later partial-AI rewrite of line 4
3. `human/unattributed -> 100%-ai` for the final AI rewrite of line 3

## Additional US-11 Scalability Check

US-11 also now includes a focused scalability regression test in [tests/test_us11_deep_history_scalability_tdd.py](tests/test_us11_deep_history_scalability_tdd.py).

That test does not build a real repository history. Instead, it directly exercises the product code and proves that commit timestamps are looked up once per origin revision rather than once per live line.

Why that matters:

1. deep history often means many live lines share a smaller set of origin revisions
2. repeated `git show --format=%cI` calls per line would add avoidable subprocess cost
3. caching those commit times is a real product improvement aligned with US-11 and future US-10 scale pressure
