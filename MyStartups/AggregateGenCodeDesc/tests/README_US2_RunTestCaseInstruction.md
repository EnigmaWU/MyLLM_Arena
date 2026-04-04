# US-2 Run Test Case Instruction

## Story Summary

US-2 proves that when a human rewrites an AI-generated line in a later commit, the final aggregate reflects human ownership (not AI).

## Run All US-2 Tests

```bash
python3 -m pytest -q tests/test_us2_human_overwrites_ai_tdd.py tests/test_us2_us3_us4_algorithm_b_regression_tdd.py -v
```

## Test Files

### test_us2_human_overwrites_ai_tdd.py

```bash
python3 -m pytest -q tests/test_us2_human_overwrites_ai_tdd.py -v
```

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_cli_matches_us2_expected_result_when_human_rewrites_one_ai_line` | End-to-end: human-overwritten AI line no longer counted as AI | SUMMARY matches `expected_result.json` |
| `test_cli_matches_us2_expected_result_for_narrow_algorithm_b_fixture_path` | Same result via Algorithm B offline replay path | Same SUMMARY |
| `test_cli_emits_process_logs_for_us2_when_debug_logging_is_enabled` | `--logLevel debug` emits per-line process logs | Logs present |
| `test_cli_info_logging_focuses_on_live_line_aggregation_progress` | `--logLevel info` emits progress messages | Logs present |

### test_us2_us3_us4_algorithm_b_regression_tdd.py (Cluster)

```bash
python3 -m pytest -q tests/test_us2_us3_us4_algorithm_b_regression_tdd.py -v
```

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_algorithm_b_rewrite_and_deletion_cluster_matches_expected_results` | US-2, US-3, US-4 all pass together under AlgB offline | All match expected |
| `test_algorithm_b_rewrite_and_deletion_cluster_matches_expected_results_on_real_local_git_replay` | Same on real local Git repos (no fixtures, live replay) | All match expected |

## Run Single TC

```bash
python3 -m pytest -q "tests/test_us2_human_overwrites_ai_tdd.py::TestUs2HumanOverwritesAiTdd::test_cli_matches_us2_expected_result_when_human_rewrites_one_ai_line" -v
```

## Real Info-Level Log Output (`--logLevel info`)

When running US-2 with `--logLevel info`, the tool emits the following three-phase narrative to stderr.
This proves human-overwrites-AI is correctly tracked: line 2 shows a `TransitionHint` from AI to human.

```
[INFO] [agg] Starting analysis for repo=<repoDir> branch=main window=2026-03-01..2026-03-31 endRevision=<commit>
[INFO] [agg] LiveLine src/normalize.py:1 aggregate origin=src/normalize.py:1@<commit> classification=100%-ai
[INFO] [agg] TransitionHint src/normalize.py:2 origin=src/normalize.py:2@<commit> best_effort_transition=100%-ai->human/unattributed
[INFO] [agg] LiveLine src/normalize.py:2 aggregate origin=src/normalize.py:2@<commit> classification=human/unattributed
[INFO] [agg] LiveLine src/normalize.py:3 aggregate origin=src/normalize.py:3@<commit> classification=100%-ai
[INFO] [agg] Finished analysis with totalCodeLines=3 fullGeneratedCodeLines=2 partialGeneratedCodeLines=0 elapsed=<N>s
```

**How to read it:**
- `TransitionHint ...normalize.py:2 ... 100%-ai->human/unattributed` — line 2 was AI-generated in r1, then rewritten by human in r2
- The final `LiveLine` for line 2 shows `classification=human/unattributed`, confirming ownership transferred
- `totalCodeLines=3, fullGeneratedCodeLines=2` — only lines 1 and 3 remain AI-attributed

### See Real Logs Live

The pytest assertions verify log content internally. To see the actual log output in your terminal:

```bash
SHOW_CLI_LOGS=1 python3 -m pytest -s tests/test_us2_human_overwrites_ai_tdd.py -k "test_cli_info_logging" -v
```
