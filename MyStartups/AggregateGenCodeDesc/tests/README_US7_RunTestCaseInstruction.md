# US-7 Run Test Case Instruction

## Story Summary

US-7 proves that multiple heterogeneous commits (human, AI, mixed) within one measurement window aggregate correctly.

## Run All US-7 Tests

```bash
python3 -m pytest -q tests/test_us7_mixed_multi_commit_window_tdd.py -v
```

## Test Files

### test_us7_mixed_multi_commit_window_tdd.py

```bash
python3 -m pytest -q tests/test_us7_mixed_multi_commit_window_tdd.py -v
```

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_cli_matches_us7_expected_result_for_mixed_multi_commit_window` | Multi-commit window produces correct aggregate | SUMMARY matches `expected_result.json` |
| `test_cli_matches_us7_expected_result_for_narrow_algorithm_b_fixture_path` | Same via Algorithm B offline replay | Same SUMMARY |
| `test_cli_emits_debug_logs_for_us7_when_enabled` | Debug logs present | Logs present |
| `test_cli_info_logging_focuses_on_live_line_aggregation_progress_for_us7` | Info logs present | Progress messages |

## Also Covered By

The US-5/7 cluster regression in `test_us5_us7_algorithm_b_regression_tdd.py` (see [US-5 RunTestCaseInstruction](README_US5_RunTestCaseInstruction.md)).

## Run Single TC

```bash
python3 -m pytest -q "tests/test_us7_mixed_multi_commit_window_tdd.py::TestUs7MixedMultiCommitWindowTdd::test_cli_matches_us7_expected_result_for_mixed_multi_commit_window" -v
```

## Real Info-Level Log Output (`--logLevel info`)

When running US-7 with `--logLevel info`, the tool emits the following three-phase narrative to stderr.
This proves mixed multi-commit ownership is correctly tracked: lines 3, 4, and 5 each show a `TransitionHint`.

```
[INFO] [agg] Starting analysis for repo=<repoDir> branch=main window=2026-03-01..2026-03-31 endRevision=<commit>
[INFO] [agg] LiveLine src/mixed.py:1 aggregate origin=src/mixed.py:1@<commit> classification=human/unattributed
[INFO] [agg] LiveLine src/mixed.py:2 aggregate origin=src/mixed.py:2@<commit> classification=human/unattributed
[INFO] [agg] TransitionHint src/mixed.py:3 origin=src/mixed.py:3@<commit> best_effort_transition=human/unattributed->100%-ai
[INFO] [agg] LiveLine src/mixed.py:3 aggregate origin=src/mixed.py:3@<commit> classification=100%-ai
[INFO] [agg] TransitionHint src/mixed.py:4 origin=src/mixed.py:4@<commit> best_effort_transition=100%-ai->human/unattributed
[INFO] [agg] LiveLine src/mixed.py:4 aggregate origin=src/mixed.py:4@<commit> classification=human/unattributed
[INFO] [agg] TransitionHint src/mixed.py:5 origin=src/mixed.py:5@<commit> best_effort_transition=human/unattributed->60%-ai
[INFO] [agg] LiveLine src/mixed.py:5 aggregate origin=src/mixed.py:5@<commit> classification=60%-ai
[INFO] [agg] Finished analysis with totalCodeLines=5 fullGeneratedCodeLines=1 partialGeneratedCodeLines=1 elapsed=<N>s
```

**How to read it:**
- `TransitionHint ...mixed.py:3 ... human/unattributed->100%-ai` — line 3 was human in r1, became fully AI in r2
- `TransitionHint ...mixed.py:4 ... 100%-ai->human/unattributed` — line 4 was AI in r2, rewritten by human in r3
- `TransitionHint ...mixed.py:5 ... human/unattributed->60%-ai` — line 5 was human in r1, partially AI-rewritten in r4
- Lines 1-2 have no transition — they kept the same attribution across all commits

### See Real Logs Live

The pytest assertions verify log content internally. To see the actual log output in your terminal:

```bash
SHOW_CLI_LOGS=1 python3 -m pytest -s tests/test_us7_mixed_multi_commit_window_tdd.py -k "test_cli_info_logging" -v
```
