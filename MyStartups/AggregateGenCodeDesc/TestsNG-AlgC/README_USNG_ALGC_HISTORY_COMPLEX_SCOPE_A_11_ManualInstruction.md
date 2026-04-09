# USNG-ALGC-HISTORY-COMPLEX-SCOPE-A-11 Manual Instruction

This story validates that many merged branches preserve per-line attribution under Algorithm C.

Fixture roots:
- `TestdataNG-AlgC/history-complex/scope-a/11/git/default`
- `TestdataNG-AlgC/history-complex/scope-a/11/svn/default`

Synthetic fixture shape used by the TDD:
- one final file with seven surviving lines
- each line carries a different merged-branch `blame.revisionId`
- two lines are full AI
- two lines are partial AI
- three lines are Manual
- all lines are inside the query window

Expected result for both origins:
- `totalCodeLines = 7`
- `fullGeneratedCodeLines = 2`
- `partialGeneratedCodeLines = 2`
