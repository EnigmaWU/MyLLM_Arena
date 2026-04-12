# AggregateGenCodeDesc User Guide NG

## Purpose

Operator-first guide for running `aggregateGenCodeDesc.py` from the assets you already have.

Use this guide when your first question is one of these:

- I have a local Git repository. Which example should I copy first?
- I have only `genCodeDesc.json` files plus a commit diff set. Which algorithm should I use?
- What metadata must exist for `startTime~endTime` before I run the CLI?
- How do I verify that my input set is complete and my output is correct?

Use `UserExamplesNG/README_UserExamplesNG.md` for exact runnable examples.
Use `README_UserGuide.md` for the broader legacy-style argument reference.

## First Principle

`aggregateGenCodeDesc.py` consumes repository history, commit diff artifacts, and `genCodeDesc.json` metadata that already exists.

More precisely, it does not generate or backfill the per-revision `genCodeDesc.json` metadata set that it uses as input.

What it does produce is a new aggregated result JSON for the requested `startTime~endTime` window, written to `--outputFile`. If you choose to name that output file `genCodeDesc.json`, that is fine.

For offline replay, `commitDiffSet/*.patch` must stay plain unified diffs.

If a patch line carries a tail comment such as `# genRatio=100` for easy human reading and checking, treat it as a human-only hint. The actual line attribution belongs in the matching `*_genCodeDesc.json` file under `DETAIL.codeLines` or `DETAIL.docLines`, and `aggregateGenCodeDesc.py` does not read the patch-line comment.

For executable NG datasets, keep the patch payload itself clean because the replay parser applies those lines as real content.

That means the operator workflow is always:

1. prepare or receive the metadata set
2. point `aggregateGenCodeDesc.py` at that metadata set
3. verify the JSON result

Only dataset materialization may be automated by helper scripts such as `generate_example.py`.

The actual aggregate step should be an explicit `python3 aggregateGenCodeDesc.py ...` command.

## What `startTime~endTime` Means

- `startTime` and `endTime` define the analysis window.
- For Algorithm A and Algorithm B, the tool needs matching revision-scoped v26.03 metadata for the revisions it must inspect or replay for that window.
- For Algorithm C, the tool accumulates v26.04 files up to the selected end revision and then filters surviving lines by embedded `blame.timestamp` inside `[startTime, endTime]`.
- Because of that, the required metadata set is usually larger than a single file at `endTime`.

## What Must Exist Before You Run

### Algorithm A: live repository analysis

- a local Git checkout or a reachable SVN repository
- `--genCodeDescSetDir` containing matching v26.03 `<revisionId>_genCodeDesc.json` files
- metadata coverage for the revisions the analysis must inspect inside the target window
- explicit repository identity and time window arguments

### Algorithm B: replay analysis

- For local Git replay:
  - a local Git repository
  - matching v26.03 metadata in `--genCodeDescSetDir`
- For SVN scenarios, including a local SVN workflow:
  - first export the `startTime~endTime` revision window into an ordered patch set
  - then run through the existing `--commitDiffSetDir` + `--genCodeDescSetDir` + `--vcsType svn` path
  - in other words, there is no separate direct local-SVN replay engine today; SVN uses the same commit-diff-set replay path
- For commit diff set replay, for either Git or SVN:
  - `--commitDiffSetDir` with ordered `NN_<revisionId>_commitDiff.patch` files
  - matching v26.03 metadata files in `--genCodeDescSetDir`
  - optional `queryArgs.json` or explicit CLI values for `endRevisionId` and `includedRevisionIds`
- explicit `--vcsType`, because it selects the runtime path

### Algorithm C: embedded-blame offline analysis

- v26.04 `*_genCodeDesc.json` files in `--genCodeDescSetDir`
- valid `REPOSITORY.revisionTimestamp` in every v26.04 file
- enough files to accumulate history up to the selected end revision
- either:
  - `queryArgs.json` inside `--genCodeDescSetDir`, or
  - explicit CLI identity fields such as `--vcsType`, `--repoURL`, `--repoBranch`, and `--endRevisionId`
- For SVN-origin Algorithm C, do not rely on the bare command unless the dataset includes `queryArgs.json`; otherwise the current CLI defaults a missing `--vcsType` to `git`.

## Choose By What You Have

| What you already have | Start with | Dataset path | Why this is the right first example |
| --- | --- | --- | --- |
| local Git repository plus v26.03 metadata | `example-AlgA-localGIT` | `UserExamplesNG/dataset-localGIT-fullCoverage` | simplest live-repository baseline |
| local Git repository plus v26.03 metadata and you want replay behavior | `example-AlgB-localGIT` | `UserExamplesNG/dataset-localGIT-fullCoverage` | same generated dataset also supports local Git replay |
| local SVN repository plus v26.03 metadata | `example-AlgA-localSVN` | `UserExamplesNG/dataset-localSVN-fullCoverage` | simplest live SVN baseline |
| local SVN repository and you want replay behavior through exported patches | `example-AlgB-localSVN` | `UserExamplesNG/dataset-localSVN-fullCoverage` | generator materializes the patch set and matching metadata |
| Git patch set plus v26.03 metadata only | `example-AlgB-offline-GIT-basic` | `UserExamplesNG/dataset-AlgB-offline-GIT-basic` | no live repository required |
| SVN patch set plus v26.03 metadata only | `example-AlgB-offline-SVN-basic` | `UserExamplesNG/dataset-AlgB-offline-SVN-basic` | no live repository required |
| v26.04 embedded blame from Git-origin history | `example-AlgC-embeddedBlame-GIT` | `UserExamplesNG/dataset-localGIT-fullCoverage` | generator materializes an AlgC-ready dataset with `queryArgs.json` |
| v26.04 embedded blame from SVN-origin history | `example-AlgC-embeddedBlame-SVN` | `UserExamplesNG/dataset-localSVN-fullCoverage` | generator materializes an AlgC-ready SVN dataset with `queryArgs.json` |
| large real Git history for production-scale practice | `example-AlgA-localGIT-productionScale` | `UserExamplesNG/dataset-localGIT-productionScale` | heavy real repository example |

## Recommended Operator Flow

1. Choose the algorithm that matches the assets you already have.
2. Verify that the metadata set covers the target `startTime~endTime`.
3. Run one example from `UserExamplesNG/README_UserExamplesNG.md` without changing anything except the output file path.
4. Only after that succeeds, replace the example dataset paths with your real paths.
5. Whenever the dataset ships an `expected_result.json` or `expected_<mode>_<scope>.json`, compare your output exactly against it.

## Summary Field Reminder

- Scope `A`, `B`, and `D` use `totalCodeLines`, `fullGeneratedCodeLines`, and `partialGeneratedCodeLines`.
- Scope `C` uses `totalDocLines`, `fullGeneratedDocLines`, and `partialGeneratedDocLines`.
- Scope `D` still uses the `*CodeLines` summary field family even though it combines source and documentation files.

## Related Docs

- `UserExamplesNG/README_UserExamplesNG.md`
- `README_UserGuide.md`
- `README_UserStoryNG.md`
