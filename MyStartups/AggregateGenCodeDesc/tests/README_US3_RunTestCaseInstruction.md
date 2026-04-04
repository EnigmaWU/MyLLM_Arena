# US-3 Run Test Case Instruction

## Story Summary

US-3 proves that when AI rewrites human lines in a later commit, the final aggregate attributes those lines to AI (latest origin wins).

## Run All US-3 Tests

```bash
python3 -m pytest -q tests/test_us3_ai_overwrites_human_tdd.py -v
```

## Test Files

### test_us3_ai_overwrites_human_tdd.py

```bash
python3 -m pytest -q tests/test_us3_ai_overwrites_human_tdd.py -v
```

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_cli_matches_us3_expected_result_when_ai_rewrites_two_human_lines` | AI-overwritten lines counted as AI in final | SUMMARY: full=1, partial=1 |
| `test_cli_matches_us3_expected_result_for_narrow_algorithm_b_fixture_path` | Same via Algorithm B offline replay | Same SUMMARY |
| `test_cli_emits_debug_logs_for_us3_when_enabled` | Debug logs present | Logs contain `LiveLine` entries |
| `test_cli_info_logging_focuses_on_live_line_aggregation_progress` | Info logs present | Progress messages |

## Also Covered By

The US-2/3/4 cluster regression in `test_us2_us3_us4_algorithm_b_regression_tdd.py` (see [US-2 RunTestCaseInstruction](README_US2_RunTestCaseInstruction.md)).

## Run Single TC

```bash
python3 -m pytest -q "tests/test_us3_ai_overwrites_human_tdd.py::TestUs3AiOverwritesHumanTdd::test_cli_matches_us3_expected_result_when_ai_rewrites_two_human_lines" -v
```

## Real Info-Level Log Output (`--logLevel info`)

When running US-3 with `--logLevel info`, the tool emits the following three-phase narrative to stderr.
This proves AI-overwrites-human is correctly tracked: line 2 shows a `TransitionHint` from human to AI.

```
[INFO] [agg] Starting analysis for repo=<repoDir> branch=main window=2026-03-01..2026-03-31 endRevision=<commit>
[INFO] [agg] LiveLine src/score.py:1 aggregate origin=src/score.py:1@<commit> classification=human/unattributed
[INFO] [agg] TransitionHint src/score.py:2 origin=src/score.py:2@<commit> best_effort_transition=human/unattributed->100%-ai
[INFO] [agg] LiveLine src/score.py:2 aggregate origin=src/score.py:2@<commit> classification=100%-ai
[INFO] [agg] LiveLine src/score.py:3 aggregate origin=src/score.py:3@<commit> classification=human/unattributed
[INFO] [agg] LiveLine src/score.py:4 aggregate origin=src/score.py:4@<commit> classification=human/unattributed
[INFO] [agg] Finished analysis with totalCodeLines=4 fullGeneratedCodeLines=1 partialGeneratedCodeLines=0 elapsed=<N>s
```

**How to read it:**
- `TransitionHint ...score.py:2 ... human/unattributed->100%-ai` — line 2 was human-written in r1, then rewritten by AI in r2
- The final `LiveLine` for line 2 shows `classification=100%-ai`, confirming ownership transferred to AI
- `totalCodeLines=4, fullGeneratedCodeLines=1` — only line 2 is now AI-attributed

### See Real Logs Live

The pytest assertions verify log content internally. To see the actual log output in your terminal:

```bash
SHOW_CLI_LOGS=1 python3 -m pytest -s tests/test_us3_ai_overwrites_human_tdd.py -k "test_cli_info_logging" -v
```
