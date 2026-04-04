# CLI Routing Run Test Case Instruction

These tests verify CLI argument parsing, routing to the correct algorithm path, and rejection of invalid CLI inputs.

## Run All CLI Routing Tests

```bash
python3 -m pytest -q tests/test_cli_algorithm_flag_tdd.py -v
```

## Test Files

### test_cli_algorithm_flag_tdd.py

```bash
python3 -m pytest -q tests/test_cli_algorithm_flag_tdd.py -v
```

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_cli_accepts_algorithm_flag` | `--algorithm` flag is accepted by CLI | No parse error |
| `test_cli_rejects_legacy_model_flag` | Legacy `--model` flag is rejected | Exits with error |
| `test_cli_executes_narrow_algorithm_b_offline_diff_path_for_us6_fixture` | AlgB offline diff path executes for US-6 fixture | Produces correct output |
| `test_cli_executes_algorithm_b_live_snapshot_path_for_us1_fixture` | AlgB live-snapshot path executes for US-1 Git fixture | Produces correct output |
| `test_cli_executes_algorithm_b_live_snapshot_path_for_us1_svn_fixture` | AlgB live-snapshot path executes for US-1 SVN fixture | Produces correct output |
| `test_cli_executes_algorithm_b_live_snapshot_path_for_local_git_repo_without_commit_diff_fixtures` | AlgB live-snapshot works with local Git repo (no fixtures) | Produces correct output |
| `test_cli_executes_algorithm_b_live_snapshot_path_with_logical_repo_url_and_working_dir` | AlgB live-snapshot works with logical repo URL + working dir | Produces correct output |
| `test_cli_executes_algorithm_b_period_added_path_for_local_git_repo_without_commit_diff_fixtures` | AlgB period-added path works with local Git repo | Produces correct output |
| `test_cli_rejects_algorithm_b_live_snapshot_without_commit_diff_fixtures_or_local_git_checkout` | AlgB live-snapshot without fixtures or local checkout is rejected | Exits with error |
| `test_cli_rejects_invalid_vcs_type_for_algorithm_b_live_snapshot_path` | Invalid VCS type for AlgB live-snapshot is rejected | Exits with error |
| `test_cli_rejects_algorithm_b_offline_first_patch_with_multiple_files` | AlgB offline rejects patch touching multiple files | Exits with error |
| `test_cli_rejects_algorithm_b_offline_first_patch_with_multiple_hunks` | AlgB offline rejects patch with multiple hunks | Exits with error |
| `test_cli_rejects_algorithm_b_offline_when_replayed_file_path_jumps_to_unrelated_file` | AlgB offline rejects when file path jumps mid-sequence | Exits with error |
| `test_cli_handles_algorithm_b_local_git_live_snapshot_when_first_window_commit_has_multiple_hunks` | AlgB handles first-window commit with multiple hunks | Processes correctly |
| `test_cli_algorithm_b_defaults_to_live_snapshot_when_no_metric_in_query` | AlgB defaults to live-snapshot when no metric is in query | live_changed_source_ratio used |
| `test_cli_algorithm_b_offline_uses_query_included_revision_ids_as_authoritative_replay_sequence` | AlgB offline uses query's included_revision_ids as replay order | Sequence follows query order |
| `test_cli_algorithm_b_period_added_continues_with_warning_when_middle_protocol_is_missing` | AlgB period-added continues (with warning) when a middle protocol file is missing | Warning emitted, no crash |

## Run Single TC

```bash
python3 -m pytest -q "tests/test_cli_algorithm_flag_tdd.py::TestCliAlgorithmFlagTdd::test_cli_accepts_algorithm_flag" -v
```
