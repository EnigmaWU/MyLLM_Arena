# US-16 Run Test Case Instruction

## Story Summary

US-16 proves that under `period_added_ai_ratio`, a line added then deleted within the same window is NOT counted, and a rewritten line's origin shifts to the rewriting commit.

## Run All US-16 Tests

```bash
python3 -m pytest -q tests/test_us16_period_added_deletions_and_rewrites_tdd.py -v
```

## Test Files

### test_us16_period_added_deletions_and_rewrites_tdd.py

```bash
python3 -m pytest -q tests/test_us16_period_added_deletions_and_rewrites_tdd.py -v
```

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_deleted_ai_line_not_counted` | AI lines from r1 are replaced by human lines in r2 → both surviving in-window lines are human | total=2, full=0, partial=0; revisionId=r2 |
| `test_rewritten_line_origin_shifts_to_rewriting_commit` | A pre-window line rewritten in-window gets an in-window origin → totalCodeLines=2 | totalCodeLines=2 |

## Scenario Shape

```
r0 (2026-02-20, before window): src/report.py — 4 human lines
r1 (2026-03-10, in window):     AI rewrites line 2 + adds line 4 (AI)
r2 (2026-03-20, in window):     human rewrites line 2 back, replaces AI line 4 with human line 4
Window: 2026-03-01 ~ 2026-03-31
```

Key: AI's r1 contributions were fully undone by r2 → 0 AI lines in the output.

## Run Single TC

```bash
python3 -m pytest -q "tests/test_us16_period_added_deletions_and_rewrites_tdd.py::TestUS16PeriodAddedDeletionsAndRewrites::test_deleted_ai_line_not_counted" -v
```
