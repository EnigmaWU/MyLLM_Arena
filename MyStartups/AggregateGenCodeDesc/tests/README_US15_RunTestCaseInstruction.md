# US-15 Run Test Case Instruction

## Story Summary

US-15 proves Algorithm B `period_added_ai_ratio` counts only lines whose origin commit falls **inside** the requested time window. Pre-window lines are excluded even though they survive to the final state.

## Run All US-15 Tests

```bash
python3 -m pytest -q tests/test_us15_period_added_single_branch_baseline_tdd.py -v
```

## Test Files

### test_us15_period_added_single_branch_baseline_tdd.py

```bash
python3 -m pytest -q tests/test_us15_period_added_single_branch_baseline_tdd.py -v
```

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_period_added_counts_only_in_window_lines` | r0 (pre-window) creates 3 lines; r1 (in-window) adds 2 AI lines; r2 (in-window) adds 1 human line → only 3 in-window lines counted | total=3, full=2, partial=0; revisionId=r2 |
| `test_period_added_excludes_pre_window_lines` | File has 6 total lines but only 3 originated in window → totalCodeLines=3 | totalCodeLines=3 (not 6) |
| `test_period_added_scope_b_counts_all_source_lines` | Scope B variant — same count because all lines are pure code (no comments in this scenario) | total=3, full=2 (same as Scope A) |

## Scenario Shape

```
r0 (2026-02-20, before window): src/calc.py — 3 human lines
r1 (2026-03-10, in window):     AI adds 2 lines (norm, score)
r2 (2026-03-20, in window):     human adds 1 line (total)
Window: 2026-03-01 ~ 2026-03-31
```

## Run Single TC

```bash
python3 -m pytest -q "tests/test_us15_period_added_single_branch_baseline_tdd.py::TestUS15PeriodAddedSingleBranchBaseline::test_period_added_counts_only_in_window_lines" -v
```
