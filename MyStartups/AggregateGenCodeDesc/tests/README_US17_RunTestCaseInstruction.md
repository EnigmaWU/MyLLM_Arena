# US-17 Run Test Case Instruction

## Story Summary

US-17 proves that renaming a file does not make pre-window lines appear as in-window under `period_added_ai_ratio`. Only genuinely new lines added during the rename commit count.

## Run All US-17 Tests

```bash
python3 -m pytest -q tests/test_us17_period_added_git_rename_tdd.py -v
```

## Test Files

### test_us17_period_added_git_rename_tdd.py

```bash
python3 -m pytest -q tests/test_us17_period_added_git_rename_tdd.py -v
```

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_period_added_after_rename_counts_only_new_lines` | Only the new AI line added during rename counts; 3 pre-window lines excluded | total=1, full=1, partial=0; revisionId=r1 |
| `test_renamed_file_appears_under_new_path` | SUMMARY totalCodeLines=1 proves the rename was tracked without inflating the count | totalCodeLines=1 |

## Scenario Shape

```
r0 (2026-02-20, before window): src/old_name.py — 3 human lines
r1 (2026-03-15, in window):     rename → src/new_name.py + add 1 AI line
Window: 2026-03-01 ~ 2026-03-31
```

Key: The 3 pre-window lines survive the rename but their origin (r0) is before the window.

## Run Single TC

```bash
python3 -m pytest -q "tests/test_us17_period_added_git_rename_tdd.py::TestUS17PeriodAddedGitRename::test_period_added_after_rename_counts_only_new_lines" -v
```
