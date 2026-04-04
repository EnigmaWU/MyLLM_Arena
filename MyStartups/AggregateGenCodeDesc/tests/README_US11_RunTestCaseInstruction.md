# US-11 Run Test Case Instruction

## Story Summary

US-11 proves that a repository with deep commit history (many sequential changes to the same lines) still produces correct line attribution.

## Run All US-11 Tests

```bash
python3 -m pytest -q tests/test_us11_deep_history_preserves_attribution_tdd.py tests/test_us11_deep_history_preserves_attribution_svn_tdd.py tests/test_us11_deep_history_scalability_tdd.py -v
```

## Test Files

### test_us11_deep_history_preserves_attribution_tdd.py (Git)

```bash
python3 -m pytest -q tests/test_us11_deep_history_preserves_attribution_tdd.py -v
```

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_cli_matches_us11_expected_result_for_deep_history` | Deep Git history matches `expected_result.json` | SUMMARY matches golden file |
| `test_cli_matches_us11_expected_result_for_narrow_algorithm_b_fixture_path` | Same via Algorithm B offline replay | Same SUMMARY |
| `test_cli_emits_debug_logs_for_us11_when_enabled` | Debug logs present | Logs present |
| `test_cli_info_logging_focuses_on_live_line_aggregation_progress_for_us11` | Info logs present | Progress messages |

### test_us11_deep_history_preserves_attribution_svn_tdd.py (SVN)

```bash
python3 -m pytest -q tests/test_us11_deep_history_preserves_attribution_svn_tdd.py -v
```

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_cli_matches_us11_expected_result_for_deep_history` | Deep SVN history matches expected | SUMMARY matches golden file |
| `test_cli_emits_debug_logs_for_us11_when_enabled` | Debug logs present | Logs present |
| `test_cli_info_logging_focuses_on_live_line_aggregation_progress_for_us11` | Info logs present | Progress messages |

### test_us11_deep_history_scalability_tdd.py

```bash
python3 -m pytest -q tests/test_us11_deep_history_scalability_tdd.py -v
```

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_build_result_reuses_commit_time_lookup_per_origin_revision` | Commit-time lookups are cached (not repeated per line) | Pass — no redundant lookups |

## Also Covered By

The US-10/11 cluster regression in `test_us10_us11_algorithm_b_regression_tdd.py` (see [US-10 RunTestCaseInstruction](README_US10_RunTestCaseInstruction.md)).

## Run Single TC

```bash
python3 -m pytest -q "tests/test_us11_deep_history_preserves_attribution_tdd.py::TestUs11DeepHistoryPreservesAttributionTdd::test_cli_matches_us11_expected_result_for_deep_history" -v
```

## Real Info-Level Log Output (`--logLevel info`)

When running US-11 with `--logLevel info`, the tool emits the following three-phase narrative to stderr.
This proves deep history attribution is preserved: only in-window lines (r3, r4) appear, and transitions show the prior revision's attribution.

```
[INFO] [agg] Starting analysis for repo=<repoDir> branch=main window=2026-03-01..2026-03-31 endRevision=<commit>
[INFO] [agg] TransitionHint src/deep_history.py:2 origin=src/deep_history.py:2@<commit> best_effort_transition=50%-ai->human/unattributed
[INFO] [agg] LiveLine src/deep_history.py:2 aggregate origin=src/deep_history.py:2@<commit> classification=human/unattributed
[INFO] [agg] TransitionHint src/deep_history.py:3 origin=src/deep_history.py:3@<commit> best_effort_transition=human/unattributed->100%-ai
[INFO] [agg] LiveLine src/deep_history.py:3 aggregate origin=src/deep_history.py:3@<commit> classification=100%-ai
[INFO] [agg] TransitionHint src/deep_history.py:4 origin=src/deep_history.py:4@<commit> best_effort_transition=human/unattributed->60%-ai
[INFO] [agg] LiveLine src/deep_history.py:4 aggregate origin=src/deep_history.py:4@<commit> classification=60%-ai
[INFO] [agg] LiveLine src/deep_history.py:5 aggregate origin=src/deep_history.py:5@<commit> classification=human/unattributed
[INFO] [agg] Finished analysis with totalCodeLines=4 fullGeneratedCodeLines=1 partialGeneratedCodeLines=1 elapsed=<N>s
```

**How to read it:**
- Line 1 (pre-window, from r1) is excluded — only lines with in-window origin appear
- `TransitionHint ...deep_history.py:2 ... 50%-ai->human/unattributed` — line 2 was 50% AI in the pre-window commit, now human in r3
- `TransitionHint ...deep_history.py:3 ... human/unattributed->100%-ai` — new AI line added in r3
- `totalCodeLines=4` — 4 in-window lines; pre-window line 1 correctly excluded

### See Real Logs Live

The pytest assertions verify log content internally. To see the actual log output in your terminal:

```bash
SHOW_CLI_LOGS=1 python3 -m pytest -s tests/test_us11_deep_history_preserves_attribution_tdd.py -k "test_cli_info_logging" -v
```
