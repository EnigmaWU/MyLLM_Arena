# USNG-ALGC-HISTORY-COMPLEX-SCOPE-A-10 Manual Instruction

This story validates that deep history does not distort latest effective attribution when Algorithm C uses embedded blame.

Fixture roots:
- `TestdataNG-AlgC/history-complex/scope-a/10/git/default`
- `TestdataNG-AlgC/history-complex/scope-a/10/svn/default`

Synthetic fixture shape used by the TDD:
- one final surviving file
- `10,001` distinct synthetic commits, represented by `10,001` protocol revision documents from baseline `r00100` through final `r10100`
- repeated delete-and-readd transitions on the same logical lines before the final surviving attribution is established
- one line has a pre-window origin and must be excluded
- four surviving lines have in-window effective origins after deep-history rewrites
- among the in-window surviving lines: one is full AI, one is partial AI, two are Manual

This means A-10 now verifies more than distant revision IDs. The TDD explicitly asserts that `10,001` unique protocol files are generated and consumed, with one protocol document per synthetic commit, so the deep-history chain is truly `10K+` in commit count as well as label depth.

Expected result for both origins:
- `totalCodeLines = 4`
- `fullGeneratedCodeLines = 1`
- `partialGeneratedCodeLines = 1`
