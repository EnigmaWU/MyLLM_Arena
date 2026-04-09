# USNG-ALGC-HISTORY-COMPLICATED-SCOPE-A-07 Manual Instruction

This story verifies that merged content keeps per-line effective attribution instead of flattening to merge identity.

Fixture roots:
- `TestdataNG-AlgC/history-complicated/scope-a/07/git/default`
- `TestdataNG-AlgC/history-complicated/scope-a/07/svn/default`

Expected result for both origins:
- `totalCodeLines = 2`
- `fullGeneratedCodeLines = 1`
- `partialGeneratedCodeLines = 0`

The important contract is that the final merged snapshot contains surviving lines with mixed blame origins:
- baseline manual lines from the older revision
- one AI line from a merged branch revision inside the window
- one human line from another merged branch revision inside the window

AlgC must preserve those embedded blame origins exactly and must not replace them with the merge revision identity.
The older baseline lines still survive in the final file, but they remain out of scope because their `blame.timestamp` is before the query `startTime`.
