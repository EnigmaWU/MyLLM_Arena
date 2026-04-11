# TestsNG-AlgB — Run Test Case Instructions

## Purpose

This directory contains **TDD test cases** for **Algorithm B** (`--algorithm B`).

Algorithm B is the offline diff-replay algorithm.  It reconstructs line-level
state by replaying commit diff patches in chronological order, then
cross-references each surviving line's origin revision against per-revision
`genCodeDescProtoV26.03` metadata to compute the weighted AI ratio.

---

## Folder Structure

```
TestsNG-AlgB/
  README_RunTestCaseInstruction.md   ← this file
  history-simple/
    scope-a/     → stories 01, 08, 21, 22, 26 (scope A baselines)
    scope-b/     → stories 18, 33 (scope B: source + comments)
    scope-c/     → stories 19, 34 (scope C: doc files)
    scope-d/     → stories 20, 35 (scope D: all families)
    scope-all/   → story 27 (cross-algorithm parity)
    scope-runtime/ → story 28 (hardening / file-size guard)
  history-complicated/
    scope-a/     → stories 02, 03, 04, 05, 06, 07, 23, 24, 25
    scope-b/     → story 36 (scope expansion)
    scope-c/     → story 37 (scope expansion)
    scope-d/     → story 38 (scope expansion)
    scope-runtime/ → story 29 (operator logging)
  history-complex/
    scope-a/     → stories 09, 10, 11 (large scale / deep history)
    scope-b/     → story 39 (scope expansion)
    scope-c/     → story 40 (scope expansion)
    scope-d/     → story 41 (scope expansion)
```

## Fixture Location

Offline fixture replay tests reference fixtures in `TestdataNG-AlgB/`.

Fixture path convention:

```
TestdataNG-AlgB/<history>/<scope>/<NN>/<vcsType>/default/
  query.json
  commitDiffSet/<NNNN>_<revisionId>_commitDiff.patch  ...
  <revisionId>_genCodeDesc.json  ...
  expected_result.json
```

Live Git replay tests build temporary repositories on the fly using
`GitRepoHarness` from `tests/cli_test_support.py`.

---

## Protocol Version

All Algorithm B genCodeDesc fixture files use `protocolVersion: "26.03"`.
This is distinct from Algorithm C which uses `"26.04"` (with embedded `blame`
objects). Algorithm B `DETAIL[].codeLines[]` entries carry only `lineLocation`
and `genRatio` — no `blame` object.

---

## How To Run

Run all Algorithm B NG tests:

```bash
python -m pytest TestsNG-AlgB/ -v
```

Run a single story:

```bash
python -m pytest TestsNG-AlgB/history-simple/scope-a/test_usng_algb_history_simple_scope_a_01_tdd.py -v
```
