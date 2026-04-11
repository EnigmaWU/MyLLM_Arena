# AggregateGenCodeDesc User Examples

## Purpose

Real runnable user examples for every supported row in `README_UserGuide.md`.

This document is organized around the current support matrix, not around generic command shapes.
Each primary example below is intended to be real rather than illustrative:

- it uses shipped user-example assets under `UserExamples/`
- it gives an exact command to generate or run the example
- it gives the expected result location
- it gives an exact check step so the user can verify the result

Use `README_UserGuide.md` for the full argument contract and support matrix.

## How To Use This Document

Run all commands from the project root:

```bash
cd /PATH/2/AggregateGenCodeDesc
```

All generated examples write under `/tmp/` so you can replay them without changing repository files in this repo.

## Matrix Coverage Map

- `A (live repository) / Git / Scope A-D` -> Example 1: Git support-matrix real example generated on demand
- `A (live repository) / SVN / Scope A-D` -> Example 2: SVN support-matrix real example generated on demand
- `B (replay, local Git) / Git / Scope A-D` -> Example 1, mode `algb-local`
- `B (replay, local SVN) / SVN / Scope A-D` -> Example 2, mode `algb-svn-workflow`
- `B (replay, commit diff set) / Git / Scope A-D` -> Example 1, mode `algb-offline`
- `B (replay, commit diff set) / SVN / Scope A-D` -> Example 2, mode `algb-offline`
- `C (embedded blame, v26.04) / Git-origin blame / Scope A-D` -> Example 1, mode `algc`
- `C (embedded blame, v26.04) / SVN-origin blame / Scope A-D` -> Example 2, mode `algc`

Supplementary real examples are also included later for focused Algorithm B practice:

- Example 3: focused Git commit diff set replay with shipped data
- Example 4: focused SVN commit diff set replay with shipped data
- Example 5: focused SVN subset replay using `includedRevisionIds`
- Example 6: heavy Git production-scale real example

## 1. Real Example: Git Support-Matrix Coverage

This example is the primary real example for all currently supported Git rows in the UserGuide matrix.

Shipped generator:

- `UserExamples/matrix01-git-coverage/generate_example.py`

Generated example output:

- `/tmp/agg-userexample-matrix01-git/repo`
- `/tmp/agg-userexample-matrix01-git/genCodeDescSet`
- `/tmp/agg-userexample-matrix01-git/algcGenCodeDescSet`
- `/tmp/agg-userexample-matrix01-git/commitDiffSet`
- `/tmp/agg-userexample-matrix01-git/manifest.json`
- `/tmp/agg-userexample-matrix01-git/run_example.sh`
- `/tmp/agg-userexample-matrix01-git/check_output.sh`
- `/tmp/agg-userexample-matrix01-git/expected_<mode>_<scope>.json`

### Example 1 Generate The Dataset

```bash
python3 UserExamples/matrix01-git-coverage/generate_example.py \
  --outputDir /tmp/agg-userexample-matrix01-git \
  --force
```

### Example 1 Supported Modes

- `alga` -> `A (live repository) / Git / Scope A-D`
- `algb-local` -> `B (replay, local Git) / Git / Scope A-D`
- `algb-offline` -> `B (replay, commit diff set) / Git / Scope A-D`
- `algc` -> `C (embedded blame, v26.04) / Git-origin blame / Scope A-D`

### Example 1 Supported Scopes

- `A` -> source code only
- `B` -> source code plus comments
- `C` -> docs only
- `D` -> source code plus docs

### Example 1 Run Any Supported Git Cell

```bash
bash /tmp/agg-userexample-matrix01-git/run_example.sh <mode> <scope> /tmp/agg-userexample-matrix01-git-out.json
```

Examples:

Git + Algorithm A + Scope A:

```bash
bash /tmp/agg-userexample-matrix01-git/run_example.sh alga A /tmp/agg-userexample-matrix01-git-alga-a.json
```

Git + Algorithm B local replay + Scope D:

```bash
bash /tmp/agg-userexample-matrix01-git/run_example.sh algb-local D /tmp/agg-userexample-matrix01-git-algb-local-d.json
```

Git + Algorithm B commit diff set replay + Scope C:

```bash
bash /tmp/agg-userexample-matrix01-git/run_example.sh algb-offline C /tmp/agg-userexample-matrix01-git-algb-offline-c.json
```

Git-origin + Algorithm C + Scope B:

```bash
bash /tmp/agg-userexample-matrix01-git/run_example.sh algc B /tmp/agg-userexample-matrix01-git-algc-b.json
```

### Example 1 Expected Output

Expected files follow this pattern:

```bash
/tmp/agg-userexample-matrix01-git/expected_<mode>_<scope>.json
```

Examples:

- `/tmp/agg-userexample-matrix01-git/expected_alga_A.json`
- `/tmp/agg-userexample-matrix01-git/expected_algb-local_D.json`
- `/tmp/agg-userexample-matrix01-git/expected_algb-offline_C.json`
- `/tmp/agg-userexample-matrix01-git/expected_algc_B.json`

### Example 1 Diagnosis And Check

Inspect the generated manifest:

```bash
cat /tmp/agg-userexample-matrix01-git/manifest.json
```

Exact comparison against the expected result:

```bash
bash /tmp/agg-userexample-matrix01-git/check_output.sh <mode> <scope> /tmp/agg-userexample-matrix01-git-out.json
```

Example:

```bash
bash /tmp/agg-userexample-matrix01-git/check_output.sh algb-offline C /tmp/agg-userexample-matrix01-git-algb-offline-c.json
```

What to check if it fails:

- confirm the generator was run from the project root
- confirm `/tmp/agg-userexample-matrix01-git/repo` exists
- confirm `/tmp/agg-userexample-matrix01-git/commitDiffSet` exists for `algb-offline`
- confirm `/tmp/agg-userexample-matrix01-git/algcGenCodeDescSet` exists for `algc`
- confirm the requested `<mode>` and `<scope>` are spelled exactly as documented above

## 2. Real Example: SVN Support-Matrix Coverage

This example is the primary real example for all currently supported SVN rows in the UserGuide matrix.

Shipped generator:

- `UserExamples/matrix02-svn-coverage/generate_example.py`

Generated example output:

- `/tmp/agg-userexample-matrix02-svn/svnrepo`
- `/tmp/agg-userexample-matrix02-svn/workingCopy`
- `/tmp/agg-userexample-matrix02-svn/genCodeDescSet`
- `/tmp/agg-userexample-matrix02-svn/algcGenCodeDescSet`
- `/tmp/agg-userexample-matrix02-svn/commitDiffSet`
- `/tmp/agg-userexample-matrix02-svn/manifest.json`
- `/tmp/agg-userexample-matrix02-svn/run_example.sh`
- `/tmp/agg-userexample-matrix02-svn/check_output.sh`
- `/tmp/agg-userexample-matrix02-svn/expected_<mode>_<scope>.json`

### Example 2 Generate The Dataset

```bash
python3 UserExamples/matrix02-svn-coverage/generate_example.py \
  --outputDir /tmp/agg-userexample-matrix02-svn \
  --force
```

### Example 2 Supported Modes

- `alga` -> `A (live repository) / SVN / Scope A-D`
- `algb-svn-workflow` -> `B (replay, local SVN) / SVN / Scope A-D`
- `algb-offline` -> `B (replay, commit diff set) / SVN / Scope A-D`
- `algc` -> `C (embedded blame, v26.04) / SVN-origin blame / Scope A-D`

Notes for the two SVN Algorithm B modes:

- `algb-svn-workflow` and `algb-offline` use the same runtime path.
- The difference is instructional: `algb-svn-workflow` is the local-SVN operator workflow from the UserGuide, while `algb-offline` is the explicit commit-diff-set view of the same generated artifact set.

### Example 2 Supported Scopes

- `A` -> source code only
- `B` -> source code plus comments
- `C` -> docs only
- `D` -> source code plus docs

### Example 2 Run Any Supported SVN Cell

```bash
bash /tmp/agg-userexample-matrix02-svn/run_example.sh <mode> <scope> /tmp/agg-userexample-matrix02-svn-out.json
```

Examples:

SVN + Algorithm A + Scope A:

```bash
bash /tmp/agg-userexample-matrix02-svn/run_example.sh alga A /tmp/agg-userexample-matrix02-svn-alga-a.json
```

SVN + Algorithm B local workflow + Scope D:

```bash
bash /tmp/agg-userexample-matrix02-svn/run_example.sh algb-svn-workflow D /tmp/agg-userexample-matrix02-svn-algb-workflow-d.json
```

SVN + Algorithm B commit diff set replay + Scope C:

```bash
bash /tmp/agg-userexample-matrix02-svn/run_example.sh algb-offline C /tmp/agg-userexample-matrix02-svn-algb-offline-c.json
```

SVN-origin + Algorithm C + Scope B:

```bash
bash /tmp/agg-userexample-matrix02-svn/run_example.sh algc B /tmp/agg-userexample-matrix02-svn-algc-b.json
```

### Example 2 Expected Output

Expected files follow this pattern:

```bash
/tmp/agg-userexample-matrix02-svn/expected_<mode>_<scope>.json
```

Examples:

- `/tmp/agg-userexample-matrix02-svn/expected_alga_A.json`
- `/tmp/agg-userexample-matrix02-svn/expected_algb-svn-workflow_D.json`
- `/tmp/agg-userexample-matrix02-svn/expected_algb-offline_C.json`
- `/tmp/agg-userexample-matrix02-svn/expected_algc_B.json`

### Example 2 Diagnosis And Check

Inspect the generated manifest:

```bash
cat /tmp/agg-userexample-matrix02-svn/manifest.json
```

Exact comparison against the expected result:

```bash
bash /tmp/agg-userexample-matrix02-svn/check_output.sh <mode> <scope> /tmp/agg-userexample-matrix02-svn-out.json
```

Example:

```bash
bash /tmp/agg-userexample-matrix02-svn/check_output.sh algb-offline C /tmp/agg-userexample-matrix02-svn-algb-offline-c.json
```

What to check if it fails:

- confirm the generator was run from the project root
- confirm `/tmp/agg-userexample-matrix02-svn/svnrepo` exists
- confirm `/tmp/agg-userexample-matrix02-svn/commitDiffSet` exists for `algb-svn-workflow` and `algb-offline`
- confirm `/tmp/agg-userexample-matrix02-svn/algcGenCodeDescSet` exists for `algc`
- confirm the requested `<mode>` and `<scope>` are spelled exactly as documented above

## 3. Real Example: Focused Git Commit Diff Set Replay

This is a smaller shipped-data Algorithm B Git replay example. Use it when you want a compact commit-diff-set-only practice case instead of the full matrix generator.

Shipped data:

- `UserExamples/example01-algb-git-commitdiffset/genCodeDescSet/`
- `UserExamples/example01-algb-git-commitdiffset/commitDiffSet/`
- `UserExamples/example01-algb-git-commitdiffset/expected_result.json`

Command:

```bash
python3 aggregateGenCodeDesc.py \
  --vcsType git \
  --repoURL https://example.local/userexamples/git-basic \
  --repoBranch main \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --algorithm B \
  --scope A \
  --outputFile /tmp/agg-userexample-1-out.json \
  --genCodeDescSetDir UserExamples/example01-algb-git-commitdiffset/genCodeDescSet \
  --commitDiffSetDir UserExamples/example01-algb-git-commitdiffset/commitDiffSet
```

Check:

```bash
python3 - <<'PY'
import json
from pathlib import Path

actual = json.loads(Path('/tmp/agg-userexample-1-out.json').read_text())
expected = json.loads(Path('UserExamples/example01-algb-git-commitdiffset/expected_result.json').read_text())

if actual != expected:
    raise SystemExit('Example 3 mismatch')

print('Example 3 OK: actual output exactly matches expected_result.json')
PY
```

## 4. Real Example: Focused SVN Commit Diff Set Replay

This is a smaller shipped-data Algorithm B SVN replay example. Use it when you want a compact SVN-origin commit-diff-set-only practice case instead of the full matrix generator.

Shipped data:

- `UserExamples/example02-algb-svn-commitdiffset/genCodeDescSet/`
- `UserExamples/example02-algb-svn-commitdiffset/commitDiffSet/`
- `UserExamples/example02-algb-svn-commitdiffset/expected_result.json`

Command:

```bash
python3 aggregateGenCodeDesc.py \
  --vcsType svn \
  --repoURL https://example.local/userexamples/svn-basic \
  --repoBranch trunk \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --algorithm B \
  --scope A \
  --outputFile /tmp/agg-userexample-2-out.json \
  --genCodeDescSetDir UserExamples/example02-algb-svn-commitdiffset/genCodeDescSet \
  --commitDiffSetDir UserExamples/example02-algb-svn-commitdiffset/commitDiffSet
```

Check:

```bash
python3 - <<'PY'
import json
from pathlib import Path

actual = json.loads(Path('/tmp/agg-userexample-2-out.json').read_text())
expected = json.loads(Path('UserExamples/example02-algb-svn-commitdiffset/expected_result.json').read_text())

if actual != expected:
    raise SystemExit('Example 4 mismatch')

print('Example 4 OK: actual output exactly matches expected_result.json')
PY
```

## 5. Real Example: Focused SVN Subset Replay With `includedRevisionIds`

This is the focused real example for the special `includedRevisionIds` control.

Shipped data:

- `UserExamples/example03-algb-svn-period-added-subset/genCodeDescSet/`
- `UserExamples/example03-algb-svn-period-added-subset/commitDiffSet/`
- `UserExamples/example03-algb-svn-period-added-subset/expected_result.json`

Command:

```bash
python3 aggregateGenCodeDesc.py \
  --vcsType svn \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --algorithm B \
  --metric period_added_ai_ratio \
  --scope A \
  --outputFile /tmp/agg-userexample-3-out.json \
  --genCodeDescSetDir UserExamples/example03-algb-svn-period-added-subset/genCodeDescSet \
  --commitDiffSetDir UserExamples/example03-algb-svn-period-added-subset/commitDiffSet
```

Check:

```bash
python3 - <<'PY'
import json
from pathlib import Path

actual = json.loads(Path('/tmp/agg-userexample-3-out.json').read_text())
expected = json.loads(Path('UserExamples/example03-algb-svn-period-added-subset/expected_result.json').read_text())

if actual != expected:
    raise SystemExit('Example 5 mismatch')

print('Example 5 OK: actual output exactly matches expected_result.json')
PY
```

## 6. Real Example: Heavy Git Production-Scale Local Repository

This is the heavy real example for production-scale Git history.

Shipped generator:

- `UserExamples/heavy01-git-production-scale/generate_example.py`

Generate the dataset:

```bash
python3 UserExamples/heavy01-git-production-scale/generate_example.py \
  --outputDir /tmp/agg-userexample-heavy-01 \
  --force
```

Run the generated helper:

```bash
bash /tmp/agg-userexample-heavy-01/run_aggregate.sh /tmp/agg-userexample-heavy-01-out.json
```

Check:

```bash
bash /tmp/agg-userexample-heavy-01/check_output.sh /tmp/agg-userexample-heavy-01-out.json
```

Use this example when the goal is production-scale Git practice rather than support-matrix coverage breadth.

## Data Layout

Current shipped real-example assets live here:

- `UserExamples/matrix01-git-coverage`
- `UserExamples/matrix02-svn-coverage`
- `UserExamples/example01-algb-git-commitdiffset`
- `UserExamples/example02-algb-svn-commitdiffset`
- `UserExamples/example03-algb-svn-period-added-subset`
- `UserExamples/heavy01-git-production-scale`

## Related Docs

- `README_UserGuide.md`: operator contract, argument meanings, and support matrix
- `README_RunTestCase.md`: test commands
- `README.md`: product scope and measurement definitions
