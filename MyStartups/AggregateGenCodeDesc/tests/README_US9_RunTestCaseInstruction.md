# US-9 Run Test Case Instruction

## Story Summary

US-9 proves Algorithm B contract parity between Git and SVN — both VCS types produce the same SUMMARY for the same logical scenario.

## Run All US-9 Tests

```bash
python3 -m pytest -q tests/test_us9_algorithm_b_contract_parity_tdd.py -v
```

## Test Files

### test_us9_algorithm_b_contract_parity_tdd.py

```bash
python3 -m pytest -q tests/test_us9_algorithm_b_contract_parity_tdd.py -v
```

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_algorithm_b_git_and_svn_supported_cells_share_same_observable_contract` | Git and SVN produce identical SUMMARY for the US-1 baseline shape | Git SUMMARY == SVN SUMMARY |

## Run Single TC

```bash
python3 -m pytest -q "tests/test_us9_algorithm_b_contract_parity_tdd.py::TestUs9AlgorithmBContractParityTdd::test_algorithm_b_git_and_svn_supported_cells_share_same_observable_contract" -v
```
