# US-10 Run Test Case Instruction

## Story Summary

US-10 proves the tool handles a large repository with many files and revisions correctly — scale testing for Algorithm A.

## Run All US-10 Tests

```bash
python3 -m pytest -q tests/test_us10_large_repository_snapshot_tdd.py tests/test_us10_large_repository_snapshot_svn_tdd.py tests/test_us10_us11_algorithm_b_regression_tdd.py -v
```

## Test Files

### test_us10_large_repository_snapshot_tdd.py (Git)

```bash
python3 -m pytest -q tests/test_us10_large_repository_snapshot_tdd.py -v
```

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_cli_matches_us10_expected_result_for_large_snapshot` | Large Git repo matches `expected_result.json` | SUMMARY matches golden file |
| `test_cli_matches_us10_expected_result_for_narrow_algorithm_b_fixture_path` | Same via Algorithm B offline replay | Same SUMMARY |
| `test_cli_emits_debug_logs_for_us10_when_enabled` | Debug logs present | Logs present |
| `test_cli_info_logging_focuses_on_live_line_aggregation_progress_for_us10` | Info log shows progress | Progress messages |

### test_us10_large_repository_snapshot_svn_tdd.py (SVN)

```bash
python3 -m pytest -q tests/test_us10_large_repository_snapshot_svn_tdd.py -v
```

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_cli_matches_us10_expected_result_for_large_snapshot` | Large SVN repo matches expected | SUMMARY matches golden file |
| `test_cli_emits_debug_logs_for_us10_when_enabled` | Debug logs present | Logs present |
| `test_cli_info_logging_focuses_on_live_line_aggregation_progress_for_us10` | Info logs present | Progress messages |

### test_us10_us11_algorithm_b_regression_tdd.py (Cluster)

```bash
python3 -m pytest -q tests/test_us10_us11_algorithm_b_regression_tdd.py -v
```

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_algorithm_b_scale_and_deep_history_cluster_matches_expected_results` | US-10 + US-11 pass together under AlgB offline | All match expected |
| `test_algorithm_b_scale_and_deep_history_cluster_matches_expected_results_on_real_local_git_replay` | Same on real local Git repos | All match expected |

## Run Single TC

```bash
python3 -m pytest -q "tests/test_us10_large_repository_snapshot_tdd.py::TestUs10LargeRepositorySnapshotTdd::test_cli_matches_us10_expected_result_for_large_snapshot" -v
```

## Real Info-Level Log Output (`--logLevel info`)

When running US-10 with `--logLevel info`, the tool emits the following three-phase narrative to stderr.
This proves large multi-file snapshots are correctly analyzed with state transitions across 8 files in 4 directories.

```
[INFO] [agg] Starting analysis for repo=<repoDir> branch=main window=2026-03-01..2026-03-31 endRevision=<commit>
[INFO] [agg] TransitionHint src/app/theta.py:2 origin=src/app/theta.py:2@<commit> best_effort_transition=human/unattributed->40%-ai
[INFO] [agg] LiveLine src/app/theta.py:2 aggregate origin=src/app/theta.py:2@<commit> classification=40%-ai
[INFO] [agg] TransitionHint src/core/alpha.py:2 origin=src/core/alpha.py:2@<commit> best_effort_transition=human/unattributed->100%-ai
[INFO] [agg] LiveLine src/core/alpha.py:2 aggregate origin=src/core/alpha.py:2@<commit> classification=100%-ai
[INFO] [agg] TransitionHint src/core/beta.py:2 origin=src/core/beta.py:2@<commit> best_effort_transition=100%-ai->human/unattributed
[INFO] [agg] LiveLine src/core/beta.py:2 aggregate origin=src/core/beta.py:2@<commit> classification=human/unattributed
[INFO] [agg] TransitionHint src/core/gamma.py:2 origin=src/core/gamma.py:2@<commit> best_effort_transition=human/unattributed->50%-ai
[INFO] [agg] LiveLine src/core/gamma.py:2 aggregate origin=src/core/gamma.py:2@<commit> classification=50%-ai
[INFO] [agg] TransitionHint src/services/delta.py:2 origin=src/services/delta.py:2@<commit> best_effort_transition=human/unattributed->100%-ai
[INFO] [agg] LiveLine src/services/delta.py:2 aggregate origin=src/services/delta.py:2@<commit> classification=100%-ai
[INFO] [agg] TransitionHint src/services/epsilon.py:2 origin=src/services/epsilon.py:2@<commit> best_effort_transition=human/unattributed->60%-ai
[INFO] [agg] LiveLine src/services/epsilon.py:2 aggregate origin=src/services/epsilon.py:2@<commit> classification=60%-ai
[INFO] [agg] LiveLine src/utils/eta.py:2 aggregate origin=src/utils/eta.py:2@<commit> classification=human/unattributed
[INFO] [agg] TransitionHint src/utils/zeta.py:2 origin=src/utils/zeta.py:2@<commit> best_effort_transition=human/unattributed->100%-ai
[INFO] [agg] LiveLine src/utils/zeta.py:2 aggregate origin=src/utils/zeta.py:2@<commit> classification=100%-ai
[INFO] [agg] Finished analysis with totalCodeLines=8 fullGeneratedCodeLines=3 partialGeneratedCodeLines=3 elapsed=<N>s
```

**How to read it:**
- 6 of 8 files show `TransitionHint` — their line-2 changed attribution between commits
- `beta.py` reversed: `100%-ai->human/unattributed` (AI line rewritten by human)
- `eta.py` has no transition — it stayed `human/unattributed` across both commits
- `totalCodeLines=8, fullGeneratedCodeLines=3, partialGeneratedCodeLines=3` — matches expected result

### See Real Logs Live

The pytest assertions verify log content internally. To see the actual log output in your terminal:

```bash
SHOW_CLI_LOGS=1 python3 -m pytest -s tests/test_us10_large_repository_snapshot_tdd.py -k "test_cli_info_logging" -v
```
