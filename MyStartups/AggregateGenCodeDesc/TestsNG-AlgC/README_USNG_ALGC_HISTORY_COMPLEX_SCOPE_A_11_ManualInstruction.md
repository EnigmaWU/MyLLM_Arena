# USNG-ALGC-HISTORY-COMPLEX-SCOPE-A-11 Manual Instruction

This story validates that many merged branches preserve per-line attribution under Algorithm C.

Fixture roots:
- `TestdataNG-AlgC/history-complex/scope-a/11/git/default`
- `TestdataNG-AlgC/history-complex/scope-a/11/svn/default`

Synthetic fixture shape used by the TDD:
- two files with seven surviving lines in total
- `10,001` distinct synthetic commits from baseline `r02000` through final `r12000`
- a baseline revision seeds all lines as Manual
- `10,000` in-window rewrite commits repeatedly reassign six surviving lines across five branch families plus one stabilization family before the final surviving attribution is established
- two lines are full AI
- two lines are partial AI
- three lines are Manual
- one surviving line is explicitly stabilized after merge, so the scenario covers branch fan-in plus later cleanup across a real `10K+` rewrite chain rather than one flat merged snapshot
- all surviving lines are inside the query window

Expected result for both origins:
- `totalCodeLines = 7`
- `fullGeneratedCodeLines = 2`
- `partialGeneratedCodeLines = 2`
