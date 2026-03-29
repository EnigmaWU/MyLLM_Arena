# US-10 Manual Instruction

## Purpose

This document describes the large-snapshot Git verification scenario for US-10.

US-10 focuses on scale shape rather than on unusual history topology. It checks that a final snapshot with many source files and many in-scope live lines still preserves the same per-line attribution semantics as the smaller earlier stories.

This scenario is intentionally different from US-11 and US-12:

1. US-11 stresses long rewrite chains on one branch
2. US-12 stresses merged-branch topology
3. US-10 stresses breadth across many files in the final snapshot

## Scenario Shape

The automated verification is implemented in [tests/test_us10_large_repository_snapshot_tdd.py](tests/test_us10_large_repository_snapshot_tdd.py).

The protocol-shaped revision metadata used by that test lives under [testdata/us10_large_repository_snapshot](testdata/us10_large_repository_snapshot).

The history uses eight source files spread across multiple directories:

1. `src/core/alpha.py`
2. `src/core/beta.py`
3. `src/core/gamma.py`
4. `src/services/delta.py`
5. `src/services/epsilon.py`
6. `src/utils/zeta.py`
7. `src/utils/eta.py`
8. `src/app/theta.py`

Each file keeps three final live lines. The first and third lines are unchanged from before the requested window and must be excluded. The middle line is the in-scope line in each file.

The history uses five commits:

1. pre-window baseline creates all eight source files
2. one in-window revision updates three core files
3. one in-window revision updates two service files and resets one earlier AI-attributed file to human
4. one in-window revision updates three more files across `utils` and `app`
5. docs-only final commit after source stabilization

## Revision Map

The fixture files and repository revisions align as follows:

1. `01_genCodeDesc.json` -> `us10-r1`
   Pre-window baseline. No AI-attributed lines.

2. `02_genCodeDesc.json` -> `us10-r2`
   Updates three core files:
   one full-AI line in `alpha`
   one full-AI line in `beta`
   one partial-AI line in `gamma`

3. `03_genCodeDesc.json` -> `us10-r3`
   Updates two service files and resets `beta` to human:
   one full-AI line in `delta`
   one partial-AI line in `epsilon`

4. `04_genCodeDesc.json` -> `us10-r4`
   Updates three more files:
   one full-AI line in `zeta`
   one human line in `eta`
   one partial-AI line in `theta`

5. `us10-r5`
   Docs-only final commit. This becomes the final repository revision in the aggregate output.

## Expected Final Result

The final aggregate should be:

- `totalCodeLines = 8`
- `fullGeneratedCodeLines = 3`
- `partialGeneratedCodeLines = 3`

## Final Per-Line Expectation

At `endTime`, the surviving in-scope lines should resolve as follows:

1. `alpha` -> `100%-ai` from `us10-r2`
2. `beta` -> human/unattributed from `us10-r3`
3. `gamma` -> `50%-ai` from `us10-r2`
4. `delta` -> `100%-ai` from `us10-r3`
5. `epsilon` -> `60%-ai` from `us10-r3`
6. `zeta` -> `100%-ai` from `us10-r4`
7. `eta` -> human/unattributed from `us10-r4`
8. `theta` -> `40%-ai` from `us10-r4`

The excluded live lines are the unchanged pre-window first and third lines in every file.

## What This Scenario Proves

This one scenario verifies all of the following together:

1. many source files in the final snapshot do not change the meaning of the aggregate result
2. per-line attribution still works independently across different directories and files
3. one revision can legitimately contribute live lines across multiple files without changing attribution semantics
4. a later human reset in one file does not disturb other files that still originate from the earlier revision
5. a docs-only final commit does not disturb the stabilized source-code result

## Verification Command

```bash
cd /Users/enigmawu/VSCode/MyLLM_Arena/MyStartups/AggregateGenCodeDesc
python3 -m unittest tests.test_us10_large_repository_snapshot_tdd -v
```

For full regression validation:

```bash
cd /Users/enigmawu/VSCode/MyLLM_Arena/MyStartups/AggregateGenCodeDesc
python3 -m unittest discover tests -v
```

## Debug Logging Expectations

When `--logLevel debug` is used, the test expects to see:

1. one `LiveLine ... aggregate ...` record for each included final live line across all eight files
2. `Skip out-of-window line ...` records for unchanged pre-window lines
3. `Reuse cached genCodeDesc for revision ...` messages because multiple files share the same origin revision in this broad snapshot
4. `best_effort_transition=` hints showing resets and AI transitions still work in the large snapshot shape

The most important transition hints in this scenario are:

1. `100%-ai -> human/unattributed` for the later reset of `beta`
2. `human/unattributed -> 50%-ai` for `gamma`
3. `human/unattributed -> 60%-ai` for `epsilon`
