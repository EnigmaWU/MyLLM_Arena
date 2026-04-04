# Runtime Hardening Run Test Case Instruction

These tests verify edge-case handling, input validation, error messages, and defensive guards in the CLI and core logic.

## Run All Runtime Hardening Tests

```bash
python3 -m pytest -q tests/test_runtime_hardening_tdd.py -v
```

## Test Files

### test_runtime_hardening_tdd.py

```bash
python3 -m pytest -q tests/test_runtime_hardening_tdd.py -v
```

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_cli_algorithm_b_defaults_to_live_snapshot_when_no_metric_given` | AlgB defaults to live-snapshot metric when none specified | No error, live_changed_source_ratio used |
| `test_cli_fails_cleanly_for_missing_file_name_in_protocol_detail` | Missing file name in protocol detail fails cleanly | Clear error message |
| `test_cli_fails_cleanly_for_missing_protocol_file_when_required` | Missing required protocol file fails cleanly | Clear error message |
| `test_cli_fails_cleanly_for_overlapping_protocol_line_coverage` | Overlapping line coverage in protocol fails cleanly | Clear error message |
| `test_cli_fails_cleanly_for_gen_ratio_outside_valid_range` | generatedRatio outside [0.0, 1.0] fails cleanly | Clear error message |
| `test_cli_fails_cleanly_when_no_revision_exists_before_end_time` | No revision before endTime fails cleanly | Clear error message |
| `test_cli_requires_working_dir_for_git_when_repo_url_is_logical_url` | Logical repo URL without working dir is rejected | Clear error message |
| `test_cli_rejects_commit_diff_set_dir_for_algorithm_a` | `--commitDiffSetDir` rejected for Algorithm A | Clear error message |
| `test_cli_allows_algorithm_b_commit_diff_set_dir_without_git_working_dir` | `--commitDiffSetDir` works for AlgB without Git working dir | No error |
| `test_cli_rejects_repo_branch_with_path_traversal` | `--repoBranch` with `../` path traversal is rejected | Security validation error |
| `test_cli_rejects_empty_repo_branch` | `--repoBranch ""` (empty string) is rejected | Validation error |
| `test_cli_rejects_start_time_after_end_time` | `--startTime` after `--endTime` is rejected | Validation error |
| `test_parse_svn_blame_fails_when_blame_entries_and_file_lines_diverge` | SVN blame entry count ≠ file line count fails | Clear error message |

## Run Single TC

```bash
python3 -m pytest -q "tests/test_runtime_hardening_tdd.py::TestRuntimeHardeningTdd::test_cli_rejects_repo_branch_with_path_traversal" -v
```
