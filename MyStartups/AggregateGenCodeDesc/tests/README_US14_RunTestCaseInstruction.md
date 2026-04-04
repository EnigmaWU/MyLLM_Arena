# US-14 Run Test Case Instruction (Heavy Tier)

## Story Summary

US-14 validates Algorithm A against a production-scale SVN repository. This test is marked `production_scale` and is **deselected** by default.

## Run US-14 Test

> **Note**: This test requires a production-scale SVN repo and may take significant time. It is excluded from the default test run.

```bash
python3 -m pytest -q tests/test_us14_svn_production_scale_local_repo_tdd.py -v -m "production_scale"
```

## Test Files

### test_us14_svn_production_scale_local_repo_tdd.py

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_build_result_matches_expected_result_for_production_scale_svn_repo` | Full end-to-end run on a production-scale SVN repo produces expected aggregate | Output matches golden expected result |

## Run Single TC

```bash
python3 -m pytest -q "tests/test_us14_svn_production_scale_local_repo_tdd.py::TestUs14SvnProductionScaleLocalRepoTdd::test_build_result_matches_expected_result_for_production_scale_svn_repo" -v
```
