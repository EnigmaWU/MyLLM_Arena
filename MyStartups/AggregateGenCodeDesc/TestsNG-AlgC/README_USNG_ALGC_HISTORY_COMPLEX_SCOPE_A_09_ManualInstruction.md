# USNG-ALGC-HISTORY-COMPLEX-SCOPE-A-09 Manual Instruction

This story validates that Algorithm C preserves result semantics across a large end-revision file set.

Fixture roots:
- `TestdataNG-AlgC/history-complex/scope-a/09/git/default`
- `TestdataNG-AlgC/history-complex/scope-a/09/svn/default`

Synthetic fixture shape used by the TDD:
- 60 source files
- 3 surviving lines per file in the end revision
- line 1 is pre-window Manual and therefore excluded
- line 2 is the classification line: 20 files full AI, 20 files partial AI, 20 files Manual
- line 3 is in-window Manual and therefore included

Expected result for both origins:
- `totalCodeLines = 120`
- `fullGeneratedCodeLines = 20`
- `partialGeneratedCodeLines = 20`
