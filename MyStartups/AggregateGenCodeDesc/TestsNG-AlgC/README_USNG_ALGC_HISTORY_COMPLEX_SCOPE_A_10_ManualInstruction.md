# USNG-ALGC-HISTORY-COMPLEX-SCOPE-A-10 Manual Instruction

This story validates that deep history does not distort latest effective attribution when Algorithm C uses embedded blame.

Fixture roots:
- `TestdataNG-AlgC/history-complex/scope-a/10/git/default`
- `TestdataNG-AlgC/history-complex/scope-a/10/svn/default`

Synthetic fixture shape used by the TDD:
- one final surviving file
- five surviving lines
- one line has a pre-window origin and must be excluded
- four lines have in-window origins spread across widely separated revision identifiers
- among the in-window lines: one is full AI, one is partial AI, two are Manual

Expected result for both origins:
- `totalCodeLines = 4`
- `fullGeneratedCodeLines = 1`
- `partialGeneratedCodeLines = 1`
