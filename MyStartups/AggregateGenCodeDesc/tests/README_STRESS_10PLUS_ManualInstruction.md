# Stress Manual Instruction

## Purpose

This document describes a more realistic mixed-history verification run for `aggregateGenCodeDesc.py`.

Unlike the smaller user-story fixtures, this scenario intentionally combines several already-proven behaviors in one repository history:

- pre-window baseline lines that should be excluded
- in-window human rewrites
- full-AI line introduction
- rename preservation
- AI-then-human reset
- partial-AI rewrite
- feature-branch AI rewrite merged into `main`
- later non-source commits that should not affect the final result

## Scenario Shape

The automated stress test is implemented in [tests/test_stress_mixed_history_10plus_commits.py](tests/test_stress_mixed_history_10plus_commits.py).

It creates an 11-commit history:

1. pre-window human baseline on `src/legacy_mix.py`
2. in-window human change
3. full-AI rewrite of several lines
4. pure rename to `src/current_mix.py`
5. human rewrite that removes one earlier AI attribution
6. partial-AI rewrite
7. human deletion of an earlier AI line
8. feature branch AI rewrite
9. main branch human rewrite
10. merge commit back to `main`
11. docs-only commit after source stabilization

## Expected Final Result

The final aggregate should be:

- `totalCodeLines = 5`
- `fullGeneratedCodeLines = 2`
- `partialGeneratedCodeLines = 1`

The excluded lines are:

- the unchanged pre-window head line
- the unchanged pre-window tail line
- the deleted AI line

## Verification Command

```bash
cd /Users/enigmawu/VSCode/MyLLM_Arena/MyStartups/AggregateGenCodeDesc
python3 -m unittest tests.test_stress_mixed_history_10plus_commits -v
```

## Why This Exists

This is not a replacement for the smaller user-story contract tests.

The smaller tests isolate one rule each.
This stress scenario checks that those same rules still compose correctly in a more realistic repository history.
