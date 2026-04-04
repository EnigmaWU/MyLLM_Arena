# Integration & Stress Run Test Case Instruction

These tests exercise real Git/SVN repositories and high-commit-count scenarios to validate end-to-end correctness beyond unit-level fixtures.

## Run All Integration & Stress Tests

```bash
python3 -m pytest -q \
  tests/test_real_git_model_a_scenarios.py \
  tests/test_real_svn_contract_parity.py \
  tests/test_real_svn_lineage_experiments.py \
  tests/test_real_svn_same_file_merge_limitation.py \
  tests/test_stress_mixed_history_10plus_commits.py \
  -v
```

---

## Test Files

### 1. test_real_git_model_a_scenarios.py

Real Git repository scenarios for Algorithm A (blame-based end-snapshot).

```bash
python3 -m pytest -q tests/test_real_git_model_a_scenarios.py -v
```

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_human_overwrites_ai_resets_blame` | Human overwriting AI-generated lines resets blame origin | Blame shows human as author |
| `test_ai_overwrites_human_takes_latest_origin` | AI overwriting human lines takes latest origin | Blame shows AI as author |
| `test_deleted_lines_do_not_survive_final_snapshot` | Deleted lines are absent from final snapshot | No deleted lines in output |
| `test_rename_preserves_lineage_under_git_blame` | File rename preserves blame lineage | Origin commits unchanged |
| `test_merge_commit_keeps_effective_line_origin` | Merge commit keeps effective line origin | Correct origin after merge |

### 2. test_real_svn_contract_parity.py

SVN repository contract parity baseline.

```bash
python3 -m pytest -q tests/test_real_svn_contract_parity.py -v
```

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_local_svn_repo_can_be_created_for_future_parity_tests` | SVN test repo can be created | Repo initialised without error |

### 3. test_real_svn_lineage_experiments.py

SVN branch merge lineage experiments.

```bash
python3 -m pytest -q tests/test_real_svn_lineage_experiments.py -v
```

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_branch_owned_file_merge_can_preserve_branch_origin_path` | Branch-owned file merge preserves branch origin path | Origin path intact |
| `test_same_file_multi_branch_merge_remains_unsuitable_for_branch_tip_claims` | Same-file multi-branch merge is unsuitable for branch-tip claims | Documented limitation confirmed |

### 4. test_real_svn_same_file_merge_limitation.py

SVN same-file merge known limitation.

```bash
python3 -m pytest -q tests/test_real_svn_same_file_merge_limitation.py -v
```

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_same_file_branch_merges_collapse_to_trunk_side_revisions` | Same-file branch merges collapse to trunk-side revisions | Known SVN limitation documented |

### 5. test_stress_mixed_history_10plus_commits.py

Stress test with 11+ mixed-origin commits.

```bash
python3 -m pytest -q tests/test_stress_mixed_history_10plus_commits.py -v
```

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_cli_handles_realistic_mixed_history_with_eleven_commits` | CLI processes 11-commit mixed history end-to-end | Correct aggregate output |
| `test_cli_debug_logs_show_mixed_realistic_origins` | Debug logs capture mixed origins across commits | Log lines present for each origin |
