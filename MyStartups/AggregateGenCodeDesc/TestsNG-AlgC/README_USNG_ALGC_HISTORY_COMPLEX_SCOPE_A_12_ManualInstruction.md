# USNG-ALGC-HISTORY-COMPLEX-SCOPE-A-12 Manual Instruction

This story is the heavy Git-origin production-scale gate for Algorithm C.

Fixture root:
- `TestdataNG-AlgC/history-complex/scope-a/12/git/default`

Synthetic scale used by the TDD:
- `100` branch-owned feature files distributed across `src/features/core`, `src/features/services`, and `src/features/utils`
- `10,001` distinct synthetic commits from baseline `r02000` through final `r12000`
- one pre-window baseline commit seeds four Manual surviving lines per file
- `5,000` in-window integration commits repeatedly rewrite line `2` across the `100` feature files
- `5,000` in-window release commits repeatedly rewrite line `4` across the `100` feature files
- two surviving in-window classification lines per feature file after convergence
- 40 feature files full AI
- 30 feature files partial AI at `60`
- 30 feature files Manual

Interpretation rule proven by this story:
- the end summary must reflect the latest effective attribution on surviving lines after `10K+` executed integration and release rewrites, not a flat one-snapshot bulk import

Expected result:
- `totalCodeLines = 200`
- `fullGeneratedCodeLines = 80`
- `partialGeneratedCodeLines = 60`
