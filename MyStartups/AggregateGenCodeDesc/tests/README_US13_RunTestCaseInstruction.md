# US-13 Run Test Case Instruction (Heavy Tier)

## Story Summary

US-13 validates Algorithm A against a production-scale Git repository. This test is marked `production_scale` and is **deselected** by default.

## Run US-13 Test

> **Note**: This test requires a production-scale Git repo and may take significant time. It is excluded from the default test run.

```bash
python3 -m pytest -q tests/test_us13_git_production_scale_local_repo_tdd.py -v -m "production_scale"
```

## Test Files

### test_us13_git_production_scale_local_repo_tdd.py

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_build_result_matches_expected_result_for_production_scale_git_repo` | Full end-to-end run on a production-scale Git repo produces expected aggregate | Output matches golden expected result |

## Run Single TC

```bash
python3 -m pytest -q "tests/test_us13_git_production_scale_local_repo_tdd.py::TestUs13GitProductionScaleLocalRepoTdd::test_build_result_matches_expected_result_for_production_scale_git_repo" -v
```
