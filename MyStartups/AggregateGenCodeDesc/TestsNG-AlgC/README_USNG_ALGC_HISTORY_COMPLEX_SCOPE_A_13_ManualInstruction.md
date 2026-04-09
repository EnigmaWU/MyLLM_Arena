# USNG-ALGC-HISTORY-COMPLEX-SCOPE-A-13 Manual Instruction

This story is the heavy SVN-origin production-scale gate for Algorithm C.

Fixture root:
- `TestdataNG-AlgC/history-complex/scope-a/13/svn/default`

Synthetic scale used by the TDD:
- `100` branch-owned feature files under `trunk/src`, distributed across `core`, `services`, and `utils`
- `10,001` distinct synthetic revisions from baseline `r02000` through final `r12000`
- one pre-window baseline revision seeds four Manual surviving lines per file
- `5,000` in-window integration revisions repeatedly rewrite line `2` across the `100` feature files
- `5,000` in-window release revisions repeatedly rewrite line `4` across the `100` feature files
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
