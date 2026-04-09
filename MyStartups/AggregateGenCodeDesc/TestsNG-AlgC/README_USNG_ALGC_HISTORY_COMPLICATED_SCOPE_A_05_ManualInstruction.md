# USNG-ALGC-HISTORY-COMPLICATED-SCOPE-A-05 Manual Instruction

This story verifies that a pure rename or move does not change line ownership.

Fixture roots:
- `TestdataNG-AlgC/history-complicated/scope-a/05/git/default`
- `TestdataNG-AlgC/history-complicated/scope-a/05/svn/default`

Expected result for both origins:
- `totalCodeLines = 3`
- `fullGeneratedCodeLines = 2`
- `partialGeneratedCodeLines = 0`

The important contract is that the final file path is different from the blame origin path:
- final `fileName`: `src/current_name.py`
- `blame.originalFilePath`: `src/legacy_name.py`

So the surviving lines still carry the old origin path while the runtime consumes the renamed final file snapshot without repository access.
