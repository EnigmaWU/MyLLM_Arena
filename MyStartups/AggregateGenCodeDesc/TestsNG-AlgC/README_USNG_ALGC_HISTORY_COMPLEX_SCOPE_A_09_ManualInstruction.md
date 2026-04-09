# USNG-ALGC-HISTORY-COMPLEX-SCOPE-A-09 Manual Instruction

This story validates that Algorithm C preserves result semantics across a large end-revision file set.

Fixture roots:
- `TestdataNG-AlgC/history-complex/scope-a/09/git/default`
- `TestdataNG-AlgC/history-complex/scope-a/09/svn/default`

Synthetic fixture shape used by the TDD:
- 60 source files
- distributed across `core`, `services`, and `utils` directories
- two protocol revisions instead of one flat snapshot:
	- baseline revision adds 4 Manual lines per file before the query window
	- end revision deletes and replaces two lines per file
- surviving file shape after accumulation:
	- lines 1 and 3 still come from the pre-window baseline and are excluded
	- line 2 is the classification line: 20 files full AI, 20 files partial AI, 20 files Manual
	- line 4 is a later in-window Manual stabilization line and is included

This keeps A-09 inside the large-file-set boundary, but makes the data shape more structurally complex than a single huge flat snapshot.

Expected result for both origins:
- `totalCodeLines = 120`
- `fullGeneratedCodeLines = 20`
- `partialGeneratedCodeLines = 20`
