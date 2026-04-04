# US-18 Run Test Case Instruction

## Story Summary

US-18 proves that `period_added_ai_ratio` correctly handles non-fast-forward merges — AI lines from both the main branch and a merged feature branch survive and are counted.

## Run All US-18 Tests

```bash
python3 -m pytest -q tests/test_us18_period_added_merge_aware_tdd.py -v
```

## Test Files

### test_us18_period_added_merge_aware_tdd.py

```bash
python3 -m pytest -q tests/test_us18_period_added_merge_aware_tdd.py -v
```

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_period_added_merge_counts_both_branch_contributions` | AI line from main (r1) + AI line from feature (r2) both survive merge (r3) | total=2, full=2, partial=0; revisionId=r3 |

## Scenario Shape

```
r0 (2026-02-20, before window): src/base.py — 2 human lines
r1 (2026-03-05, in window, main):    AI adds line 2 (ai_init)
r2 (2026-03-08, in window, feature): AI adds line 3 (ai_enhance) — branched from r0
r3 (2026-03-15, in window, main):    merge feature→main with manual resolution
Window: 2026-03-01 ~ 2026-03-31
```

Key: Both AI contributions survive the merge into the final state.

## Run Single TC

```bash
python3 -m pytest -q "tests/test_us18_period_added_merge_aware_tdd.py::TestUS18PeriodAddedMergeAware::test_period_added_merge_counts_both_branch_contributions" -v
```
