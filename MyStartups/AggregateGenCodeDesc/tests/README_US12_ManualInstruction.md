# US-12 Manual Instruction

## Purpose

This document describes the branch-heavy Git verification scenario for US-12.

US-12 extends the earlier merge story by checking that many branches merged into the same target branch during one requested window still preserve per-line effective attribution.

This scenario is intentionally more complex than US-8 and the first US-12 draft. It is designed to feel closer to a real mainline integration window where several feature branches are merged back over time and one merged AI-origin line is subsequently rewritten by a human on `main`.

## Scenario Shape

The automated verification is implemented in [tests/test_us12_many_merged_branches_preserve_attribution_tdd.py](tests/test_us12_many_merged_branches_preserve_attribution_tdd.py).

The protocol-shaped revision metadata used by that test lives under [testdata/us12_many_merged_branches_preserve_attribution](testdata/us12_many_merged_branches_preserve_attribution).

The history uses one source file, `src/branch_matrix.py`, with ten live lines in the final file numbering. Three of those lines remain unchanged from before the requested window and must be excluded. Seven lines are in scope and must be resolved independently.

It creates a 15-commit history:

1. pre-window baseline on `src/branch_matrix.py`
2. mainline human rewrite inside the window
3. create `feature-alpha` and apply one full-AI rewrite
4. merge `feature-alpha` into `main`
5. create `feature-beta` and apply one partial-AI rewrite
6. merge `feature-beta` into `main`
7. create `feature-gamma` and apply one full-AI rewrite
8. later mainline human rewrite of a different surviving line before `feature-gamma` is merged
9. merge `feature-gamma` into `main`
10. create `feature-delta` and apply one partial-AI rewrite
11. merge `feature-delta` into `main`
12. create `feature-epsilon` and apply one full-AI rewrite
13. merge `feature-epsilon` into `main`
14. mainline human rewrite after the merges that resets the earlier `feature-epsilon` AI attribution
15. docs-only commit after source stabilization

## Revision Map

The fixture files and repository revisions align as follows:

1. `01_genCodeDesc.json` -> `us12-r1`
   Pre-window baseline. No AI-attributed lines.

2. `02_genCodeDesc.json` -> `us12-r2`
   Mainline human rewrite of `main_human` on line 2.

3. `03_genCodeDesc.json` -> `us12-r3`
   `feature-alpha` full-AI rewrite of line 3.

4. `04_genCodeDesc.json` -> `us12-r4`
   Merge of `feature-alpha`.

5. `05_genCodeDesc.json` -> `us12-r5`
   `feature-beta` partial-AI rewrite of line 4 at 70%.

6. `06_genCodeDesc.json` -> `us12-r6`
   Merge of `feature-beta`.

7. `07_genCodeDesc.json` -> `us12-r7`
   `feature-gamma` full-AI rewrite of line 5.

8. `08_genCodeDesc.json` -> `us12-r8`
   Mainline human rewrite of `main_tail` on line 9 before the branch merges are applied.

9. `09_genCodeDesc.json` -> `us12-r9`
   Merge of `feature-gamma`.

10. `10_genCodeDesc.json` -> `us12-r10`
    `feature-delta` partial-AI rewrite of line 6 at 40%.

11. `11_genCodeDesc.json` -> `us12-r11`
    Merge of `feature-delta`.

12. `12_genCodeDesc.json` -> `us12-r12`
    `feature-epsilon` full-AI rewrite of line 7. This line is intentionally not expected to remain AI-attributed in the final result.

13. `13_genCodeDesc.json` -> `us12-r13`
    Merge of `feature-epsilon`.

14. `14_genCodeDesc.json` -> `us12-r14`
    Mainline human rewrite of line 7 after the merges, resetting the earlier AI attribution from `feature-epsilon`.

15. `us12-r15`
    Docs-only final commit. This becomes the final repository revision in the aggregate output.

## Expected Final Result

The final aggregate should be:

- `totalCodeLines = 7`
- `fullGeneratedCodeLines = 2`
- `partialGeneratedCodeLines = 2`

## Final Per-Line Expectation

At `endTime`, the surviving in-scope lines should resolve as follows:

1. line 2 -> human/unattributed from `us12-r2`
2. line 3 -> `100%-ai` from `feature-alpha` revision `us12-r3`
3. line 4 -> `70%-ai` from `feature-beta` revision `us12-r4`
4. line 5 -> `100%-ai` from `feature-gamma` revision `us12-r5`
5. line 6 -> `40%-ai` from `feature-delta` revision `us12-r6`
6. line 7 -> human/unattributed from `us12-r14`, because the earlier merged AI line from `feature-epsilon` was superseded by a later mainline human rewrite
7. line 9 -> human/unattributed from `us12-r8`

The excluded live lines should be:

- line 1, unchanged from before the requested window
- line 8, unchanged from before the requested window
- line 10, unchanged from before the requested window

## What This Scenario Proves

This one scenario verifies all of the following together:

1. many branches can be integrated in one requested window without flattening attribution
2. each merged line keeps its own effective origin revision rather than inheriting the merge revision
3. different feature branches can contribute different AI ratios in the same final result
4. later mainline human rewrites can still override an earlier merged AI origin
5. unchanged pre-window lines remain excluded even when surrounded by many in-window merges
6. a docs-only final commit should not disturb the already stabilized source-code result

## Verification Command

```bash
cd /Users/enigmawu/VSCode/MyLLM_Arena/MyStartups/AggregateGenCodeDesc
python3 -m unittest tests.test_us12_many_merged_branches_preserve_attribution_tdd -v
```

For full regression validation:

```bash
cd /Users/enigmawu/VSCode/MyLLM_Arena/MyStartups/AggregateGenCodeDesc
python3 -m unittest discover tests -v
```

## Debug Logging Expectations

When `--logLevel debug` is used, the test expects to see:

1. `Metadata repoBranch differs` messages for feature-branch revisions, because those revisions legitimately originated on non-main branches before being merged
2. one `LiveLine ... aggregate ...` record for each included final live line
3. `Skip out-of-window line ...` messages for the unchanged pre-window lines
4. no aggregate record for the excluded pre-window lines

## Additional Hard Variant: Octopus Merge

The US-12 automated test file also contains a harder variant that is not represented by the main fixture directory.

That variant builds a conflict-free octopus merge where three feature branches are merged into `main` in a single multi-parent merge commit.

Why this variant matters:

1. the main US-12 scenario proves branch-heavy behavior across many sequential merges
2. the octopus variant adds a different merge topology where non-first-parent feature lines must still keep their real origin revisions
3. it increases confidence that the current blame-based implementation is not accidentally relying on only one-parent merge shapes

The octopus variant uses multiple source files so the merge itself stays conflict-free and the test isolates attribution behavior rather than merge-conflict mechanics.

Its expected final aggregate is:

1. `totalCodeLines = 4`
2. `fullGeneratedCodeLines = 2`
3. `partialGeneratedCodeLines = 1`

Its expected surviving in-scope lines are:

1. one full-AI line from `feature-alpha`
2. one partial-AI line from `feature-beta`
3. one full-AI line from `feature-gamma`
4. one later mainline human line added after the octopus merge

This variant currently passes and is useful evidence that the present implementation handles at least one real multi-parent merge topology correctly.

## Additional Hard Variant: Feature-Branch Rename Plus Merge

The US-12 automated test file also now contains a rename-focused branch variant with no merge conflicts.

Why this variant matters:

1. US-5 proved that a pure rename on one branch should preserve lineage
2. this variant raises the difficulty by moving the rename onto a feature branch and merging it later into `main`
3. it checks two different path cases in the same final merged file:
   one surviving line last changed before the rename and therefore expected to keep the old origin path
   two surviving lines changed after the rename and therefore expected to use the new origin path

The rename-plus-merge variant uses this shape:

1. pre-window baseline creates `src/legacy_merge_name.py` and `src/main_side.py`
2. feature branch makes an in-window human rewrite on `src/legacy_merge_name.py`
3. the same feature branch renames that file to `src/merged_name.py`
4. the feature branch then adds one full-AI line and one partial-AI line after the rename
5. `main` independently makes a human rewrite in `src/main_side.py`
6. the feature branch is merged into `main` without conflicts
7. a docs-only commit becomes the final repository revision

Its expected final aggregate is:

1. `totalCodeLines = 4`
2. `fullGeneratedCodeLines = 1`
3. `partialGeneratedCodeLines = 1`

Its most important path assertions are:

1. `src/merged_name.py:2` must report `origin_file=src/legacy_merge_name.py` because that line was last changed before the rename
2. `src/merged_name.py:3` and `src/merged_name.py:4` must report `origin_file=src/merged_name.py` because those lines were last changed after the rename

If this variant passes, it is strong evidence that the current implementation handles feature-branch rename lineage correctly across a later merge, at least for the non-conflict case.

## Additional Hard Variant: Feature-Branch Rename Inside Octopus Merge

The strongest non-conflict US-12 variant currently combines both of the previous hard cases:

1. one feature branch performs an in-window human rewrite before a rename
2. that same branch then renames the file and adds an AI rewrite after the rename
3. two other feature branches independently add AI-attributed changes in different files
4. all three feature branches are merged into `main` through a single conflict-free octopus merge
5. `main` then performs a later human rewrite in a separate file

Why this matters:

1. it checks that rename lineage is preserved even when the renamed branch is not merged back through a simple one-branch merge
2. it checks that the rename branch and two other feature branches can all survive one multi-parent merge without flattening origin revisions
3. it simultaneously requires the analyzer to get path lineage and merge topology correct

Its expected final aggregate is:

1. `totalCodeLines = 5`
2. `fullGeneratedCodeLines = 2`
3. `partialGeneratedCodeLines = 1`

Its most important assertions are:

1. the pre-rename branch line still reports the old path, `src/legacy_alpha.py`
2. the post-rename AI line reports the new path, `src/merged_alpha.py`
3. the other octopus-merged feature branches keep their own origin revisions in `src/beta_branch.py` and `src/gamma_branch.py`
4. the later mainline human line in `src/main_side.py` remains independently attributed to its post-merge mainline revision

If this variant passes, it is strong evidence that the present implementation handles one of the most demanding non-conflict Git topologies currently in scope for Model A.

## Additional Hard Variant: Double Rename On Feature Branch Before Merge

Another strong non-conflict US-12 variant now checks whether one feature branch can rename the same file twice before merging back to `main`.

Why this matters:

1. a single rename already proved useful, but two renames create three distinct historical path stages
2. the final merged file can then contain live lines whose current origins should map to three different path names:
   the original path before any rename
   the intermediate path after the first rename
   the final path after the second rename
3. this directly pressure-tests whether blame filename lineage and metadata lookup continue to agree after repeated path changes on one feature branch

The double-rename variant uses this shape:

1. pre-window baseline creates `src/legacy_round1.py` and `src/main_companion.py`
2. the feature branch makes an in-window human rewrite while the file is still named `src/legacy_round1.py`
3. the feature branch renames the file to `src/intermediate_round2.py`
4. the feature branch adds a full-AI line while the intermediate path is active
5. the feature branch renames the file again to `src/final_round3.py`
6. the feature branch adds a partial-AI line after the second rename
7. `main` independently makes a human rewrite in `src/main_companion.py`
8. the feature branch merges back into `main` without conflicts
9. a docs-only commit becomes the final repository revision

Its expected final aggregate is:

1. `totalCodeLines = 4`
2. `fullGeneratedCodeLines = 1`
3. `partialGeneratedCodeLines = 1`

Its most important lineage assertions are:

1. `src/final_round3.py:2` must report `origin_file=src/legacy_round1.py`
2. `src/final_round3.py:3` must report `origin_file=src/intermediate_round2.py`
3. `src/final_round3.py:4` must report `origin_file=src/final_round3.py`

If this variant passes, it is strong evidence that the current implementation preserves multi-step rename lineage correctly across a later merge, at least for the non-conflict case.

## Additional Hard Variant: Rename Lineage Across Branch Handoff Merges

The next stronger non-conflict US-12 variant splits the rename chain across two different non-main branches before the final merge back to `main`.

Why this matters:

1. the earlier double-rename variant kept both renames on a single feature branch
2. this handoff variant raises the difficulty by inserting an intermediate merge into a second branch before the final merge to `main`
3. it checks that surviving lines still keep the correct historical path stage even when the rename chain spans more than one branch context

The branch-handoff variant uses this shape:

1. pre-window baseline creates `src/stage_one_name.py` and `src/main_anchor.py`
2. `feature-alpha` makes an in-window human rewrite while the file is still named `src/stage_one_name.py`
3. `feature-alpha` renames it to `src/stage_two_name.py`
4. `feature-alpha` adds a full-AI line while the stage-two path is active
5. `integration-handoff` is created from `main` and merges `feature-alpha`
6. `integration-handoff` renames the file again to `src/stage_three_name.py`
7. `integration-handoff` adds a partial-AI line after the second rename
8. `main` independently makes a human rewrite in `src/main_anchor.py`
9. `integration-handoff` merges back into `main` without conflicts
10. a docs-only commit becomes the final repository revision

Its expected final aggregate is:

1. `totalCodeLines = 4`
2. `fullGeneratedCodeLines = 1`
3. `partialGeneratedCodeLines = 1`

Its most important lineage assertions are:

1. `src/stage_three_name.py:2` must report `origin_file=src/stage_one_name.py`
2. `src/stage_three_name.py:3` must report `origin_file=src/stage_two_name.py`
3. `src/stage_three_name.py:4` must report `origin_file=src/stage_three_name.py`

If this variant passes, it is strong evidence that the current implementation preserves rename lineage not only across repeated renames, but also across an intermediate branch handoff and two separate merge boundaries.

## Why This Exists

US-8 proved that one merge should not flatten attribution.

This stronger US-12 scenario raises the bar further:

1. many branches are merged back over the same requested window
2. they contribute distinct lines in sequence rather than as one isolated merge
3. they contribute both full-AI and partial-AI lines
4. one merged AI line is later reset by a human on `main`

That makes the scenario much closer to a real integration period on an active repository, while still staying small enough to reason about line by line.
