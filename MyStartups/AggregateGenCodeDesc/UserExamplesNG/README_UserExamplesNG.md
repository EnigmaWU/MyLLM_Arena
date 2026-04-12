# AggregateGenCodeDesc User Examples NG

## Purpose

Real operator-facing examples organized by what you already have.

This document answers four practical questions for each example:

- HAVE what
- HOW to run `aggregateGenCodeDesc.py`
- how to verify that the input set is ready
- how to verify that the output matches the expected result

All commands below assume you run from the project root:

```bash
cd /PATH/2/AggregateGenCodeDesc
```

## Quick Index

| Example label | When to use it | Dataset path |
| --- | --- | --- |
| `example-AlgA-localGIT` | You have a local Git repository and v26.03 metadata | `UserExamplesNG/dataset-localGIT-fullCoverage` |
| `example-AlgB-localGIT` | You have a local Git repository and want local replay behavior | `UserExamplesNG/dataset-localGIT-fullCoverage` |
| `example-AlgC-embeddedBlame-GIT` | You have or want an AlgC-ready Git-origin embedded-blame dataset | `UserExamplesNG/dataset-localGIT-fullCoverage` |
| `example-AlgA-localSVN` | You have a local SVN repository and v26.03 metadata | `UserExamplesNG/dataset-localSVN-fullCoverage` |
| `example-AlgB-localSVN` | You have a local SVN workflow and exported replay artifacts | `UserExamplesNG/dataset-localSVN-fullCoverage` |
| `example-AlgC-embeddedBlame-SVN` | You have or want an AlgC-ready SVN-origin embedded-blame dataset | `UserExamplesNG/dataset-localSVN-fullCoverage` |
| `example-AlgB-offline-GIT-basic` | You have only a Git patch stream plus v26.03 metadata | `UserExamplesNG/dataset-AlgB-offline-GIT-basic` |
| `example-AlgB-offline-SVN-basic` | You have only an SVN patch stream plus v26.03 metadata | `UserExamplesNG/dataset-AlgB-offline-SVN-basic` |
| `example-AlgB-offline-SVN-includedRevisionIds` | You want explicit subset replay with `includedRevisionIds` | `UserExamplesNG/dataset-AlgB-offline-SVN-includedRevisionIds` |
| `example-AlgA-localGIT-productionScale` | You want a heavy real Git repository example | `UserExamplesNG/dataset-localGIT-productionScale` |

## Shared Reminder

`aggregateGenCodeDesc.py` reads existing `genCodeDesc.json` files as input.

It does not generate that per-revision input metadata set for you, but it does write a new aggregated result JSON for the requested `startTime~endTime` window to `--outputFile`.

For Algorithm B offline replay, `commitDiffSet/*.patch` contains only real unified diff content.

If a patch line shows a `genRatio` tail comment for easy human reading and checking, treat it as a human-only hint. The aggregate input still comes from the matching `*_genCodeDesc.json` file in `genCodeDescSet/`.

For the generator-backed datasets below, the `generate_example.py` script materializes all required inputs under `/tmp/` so the operator can run the CLI against a real local repository and matching metadata.

The generator is helper-only. Every operator aggregate command below is shown explicitly as `python3 aggregateGenCodeDesc.py ...` rather than a shell wrapper.

## Dataset: `dataset-localGIT-fullCoverage`

This generator materializes one local Git repository plus three matching input sets:

- `genCodeDescSet/` for Algorithm A and Algorithm B
- `algcGenCodeDescSet/` for Algorithm C
- `commitDiffSet/` for Algorithm B offline replay

### Materialize `dataset-localGIT-fullCoverage`

```bash
python3 UserExamplesNG/dataset-localGIT-fullCoverage/generate_example.py \
  --outputDir /tmp/agg-userexample-ng-localgit \
  --force
```

### Verify `dataset-localGIT-fullCoverage` Inputs

```bash
python3 - <<'PY'
from pathlib import Path

base = Path('/tmp/agg-userexample-ng-localgit')
required = [
    base / 'repo',
    base / 'genCodeDescSet',
    base / 'algcGenCodeDescSet',
    base / 'algcGenCodeDescSet' / 'queryArgs.json',
    base / 'commitDiffSet',
    base / 'manifest.json',
]

for path in required:
    if not path.exists():
        raise SystemExit(f'Missing required input: {path}')

print('Input OK: local Git full-coverage dataset is ready')
PY
```

### `example-AlgA-localGIT`

HAVE:

- a local Git repository
- matching v26.03 metadata for the target window

RUN:

```bash
LOCAL_GIT_REPO="$(python3 - <<'PY'
from pathlib import Path
print(Path('/tmp/agg-userexample-ng-localgit/repo').resolve())
PY
)"

python3 aggregateGenCodeDesc.py \
  --vcsType git \
  --repoURL "$LOCAL_GIT_REPO" \
  --repoBranch main \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --scope A \
  --outputFile /tmp/agg-userexample-ng-alga-localgit-a.json \
  --genCodeDescSetDir /tmp/agg-userexample-ng-localgit/genCodeDescSet
```

VERIFY OUTPUT:

```bash
python3 - <<'PY'
import json
from pathlib import Path

actual = json.loads(Path('/tmp/agg-userexample-ng-alga-localgit-a.json').read_text())
expected = json.loads(Path('/tmp/agg-userexample-ng-localgit/expected_alga_A.json').read_text())

if actual != expected:
    raise SystemExit('example-AlgA-localGIT mismatch')

print('example-AlgA-localGIT OK')
PY
```

### `example-AlgB-localGIT`

HAVE:

- a local Git repository
- matching v26.03 metadata
- you want replay behavior without building an external patch-only workflow

RUN:

```bash
LOCAL_GIT_REPO="$(python3 - <<'PY'
from pathlib import Path
print(Path('/tmp/agg-userexample-ng-localgit/repo').resolve())
PY
)"

python3 aggregateGenCodeDesc.py \
  --vcsType git \
  --repoURL "$LOCAL_GIT_REPO" \
  --repoBranch main \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --algorithm B \
  --scope D \
  --outputFile /tmp/agg-userexample-ng-algb-localgit-d.json \
  --genCodeDescSetDir /tmp/agg-userexample-ng-localgit/genCodeDescSet
```

VERIFY OUTPUT:

```bash
python3 - <<'PY'
import json
from pathlib import Path

actual = json.loads(Path('/tmp/agg-userexample-ng-algb-localgit-d.json').read_text())
expected = json.loads(Path('/tmp/agg-userexample-ng-localgit/expected_algb-local_D.json').read_text())

if actual != expected:
    raise SystemExit('example-AlgB-localGIT mismatch')

print('example-AlgB-localGIT OK')
PY
```

### `example-AlgC-embeddedBlame-GIT`

HAVE:

- v26.04 embedded-blame files
- a dataset that includes `queryArgs.json` inside `algcGenCodeDescSet/`

RUN:

```bash
python3 aggregateGenCodeDesc.py \
  --algorithm C \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --scope B \
  --outputFile /tmp/agg-userexample-ng-algc-localgit-b.json \
  --genCodeDescSetDir /tmp/agg-userexample-ng-localgit/algcGenCodeDescSet
```

VERIFY OUTPUT:

```bash
python3 - <<'PY'
import json
from pathlib import Path

actual = json.loads(Path('/tmp/agg-userexample-ng-algc-localgit-b.json').read_text())
expected = json.loads(Path('/tmp/agg-userexample-ng-localgit/expected_algc_B.json').read_text())

if actual != expected:
    raise SystemExit('example-AlgC-embeddedBlame-GIT mismatch')

print('example-AlgC-embeddedBlame-GIT OK')
PY
```

## Dataset: `dataset-localSVN-fullCoverage`

This generator materializes one local SVN repository plus matching Algorithm A, Algorithm B, and Algorithm C inputs.

### Materialize `dataset-localSVN-fullCoverage`

```bash
python3 UserExamplesNG/dataset-localSVN-fullCoverage/generate_example.py \
  --outputDir /tmp/agg-userexample-ng-localsvn \
  --force
```

### Verify `dataset-localSVN-fullCoverage` Inputs

```bash
python3 - <<'PY'
from pathlib import Path

base = Path('/tmp/agg-userexample-ng-localsvn')
required = [
    base / 'svnrepo',
    base / 'workingCopy',
    base / 'genCodeDescSet',
    base / 'algcGenCodeDescSet',
    base / 'algcGenCodeDescSet' / 'queryArgs.json',
    base / 'commitDiffSet',
    base / 'manifest.json',
]

for path in required:
    if not path.exists():
        raise SystemExit(f'Missing required input: {path}')

print('Input OK: local SVN full-coverage dataset is ready')
PY
```

### `example-AlgA-localSVN`

HAVE:

- a local SVN repository
- matching v26.03 metadata for the target window

RUN:

```bash
python3 aggregateGenCodeDesc.py \
  --vcsType svn \
  --repoURL "$(python3 - <<'PY'
from pathlib import Path
print(Path('/tmp/agg-userexample-ng-localsvn/svnrepo').resolve().as_uri())
PY
)" \
  --repoBranch trunk \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --scope A \
  --outputFile /tmp/agg-userexample-ng-alga-localsvn-a.json \
  --genCodeDescSetDir /tmp/agg-userexample-ng-localsvn/genCodeDescSet
```

VERIFY OUTPUT:

```bash
python3 - <<'PY'
import json
from pathlib import Path

actual = json.loads(Path('/tmp/agg-userexample-ng-alga-localsvn-a.json').read_text())
expected = json.loads(Path('/tmp/agg-userexample-ng-localsvn/expected_alga_A.json').read_text())

if actual != expected:
    raise SystemExit('example-AlgA-localSVN mismatch')

print('example-AlgA-localSVN OK')
PY
```

### `example-AlgB-localSVN`

HAVE:

- a local SVN workflow
- exported patch artifacts for the window
- matching v26.03 metadata

One quick clarification: although this example is labeled `localSVN`, the runtime path is still the exported-patch `--commitDiffSetDir` path rather than a separate direct local-SVN replay engine.

RUN:

```bash
python3 aggregateGenCodeDesc.py \
  --vcsType svn \
  --repoURL "$(python3 - <<'PY'
from pathlib import Path
print(Path('/tmp/agg-userexample-ng-localsvn/svnrepo').resolve().as_uri())
PY
)" \
  --repoBranch trunk \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --algorithm B \
  --scope D \
  --outputFile /tmp/agg-userexample-ng-algb-localsvn-d.json \
  --genCodeDescSetDir /tmp/agg-userexample-ng-localsvn/genCodeDescSet \
  --commitDiffSetDir /tmp/agg-userexample-ng-localsvn/commitDiffSet
```

VERIFY OUTPUT:

```bash
python3 - <<'PY'
import json
from pathlib import Path

actual = json.loads(Path('/tmp/agg-userexample-ng-algb-localsvn-d.json').read_text())
expected = json.loads(Path('/tmp/agg-userexample-ng-localsvn/expected_algb-svn-workflow_D.json').read_text())

if actual != expected:
    raise SystemExit('example-AlgB-localSVN mismatch')

print('example-AlgB-localSVN OK')
PY
```

### `example-AlgC-embeddedBlame-SVN`

HAVE:

- v26.04 embedded-blame files for SVN-origin history
- a dataset that includes `queryArgs.json` in `algcGenCodeDescSet/`

RUN:

```bash
python3 aggregateGenCodeDesc.py \
  --algorithm C \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --scope B \
  --outputFile /tmp/agg-userexample-ng-algc-localsvn-b.json \
  --genCodeDescSetDir /tmp/agg-userexample-ng-localsvn/algcGenCodeDescSet
```

VERIFY OUTPUT:

```bash
python3 - <<'PY'
import json
from pathlib import Path

actual = json.loads(Path('/tmp/agg-userexample-ng-algc-localsvn-b.json').read_text())
expected = json.loads(Path('/tmp/agg-userexample-ng-localsvn/expected_algc_B.json').read_text())

if actual != expected:
    raise SystemExit('example-AlgC-embeddedBlame-SVN mismatch')

print('example-AlgC-embeddedBlame-SVN OK')
PY
```

## `example-AlgB-offline-GIT-basic`

HAVE:

- a Git-origin `commitDiffSet/`
- matching v26.03 `genCodeDescSet/`
- no live repository at runtime

VERIFY INPUT:

```bash
python3 - <<'PY'
from pathlib import Path

base = Path('UserExamplesNG/dataset-AlgB-offline-GIT-basic')
patches = list((base / 'commitDiffSet').glob('*_commitDiff.patch'))
protocols = list((base / 'genCodeDescSet').glob('*_genCodeDesc.json'))

if len(patches) != 5 or len(protocols) != 5:
    raise SystemExit(f'Unexpected input counts: patches={len(patches)} protocols={len(protocols)}')

print('Input OK: offline Git basic dataset is ready')
PY
```

RUN:

```bash
python3 aggregateGenCodeDesc.py \
  --vcsType git \
  --repoURL https://example.local/userexamples/git-basic \
  --repoBranch main \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --algorithm B \
  --scope A \
  --outputFile /tmp/agg-userexample-ng-algb-offline-git-basic.json \
  --genCodeDescSetDir UserExamplesNG/dataset-AlgB-offline-GIT-basic/genCodeDescSet \
  --commitDiffSetDir UserExamplesNG/dataset-AlgB-offline-GIT-basic/commitDiffSet
```

VERIFY OUTPUT:

```bash
python3 - <<'PY'
import json
from pathlib import Path

actual = json.loads(Path('/tmp/agg-userexample-ng-algb-offline-git-basic.json').read_text())
expected = json.loads(Path('UserExamplesNG/dataset-AlgB-offline-GIT-basic/expected_result.json').read_text())

if actual != expected:
    raise SystemExit('example-AlgB-offline-GIT-basic mismatch')

print('example-AlgB-offline-GIT-basic OK')
PY
```

## `example-AlgB-offline-SVN-basic`

HAVE:

- an SVN-origin `commitDiffSet/`
- matching v26.03 `genCodeDescSet/`
- no live repository at runtime

VERIFY INPUT:

```bash
python3 - <<'PY'
from pathlib import Path

base = Path('UserExamplesNG/dataset-AlgB-offline-SVN-basic')
patches = list((base / 'commitDiffSet').glob('*_commitDiff.patch'))
protocols = list((base / 'genCodeDescSet').glob('*_genCodeDesc.json'))

if len(patches) != 5 or len(protocols) != 5:
    raise SystemExit(f'Unexpected input counts: patches={len(patches)} protocols={len(protocols)}')

print('Input OK: offline SVN basic dataset is ready')
PY
```

RUN:

```bash
python3 aggregateGenCodeDesc.py \
  --vcsType svn \
  --repoURL https://example.local/userexamples/svn-basic \
  --repoBranch trunk \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --algorithm B \
  --scope A \
  --outputFile /tmp/agg-userexample-ng-algb-offline-svn-basic.json \
  --genCodeDescSetDir UserExamplesNG/dataset-AlgB-offline-SVN-basic/genCodeDescSet \
  --commitDiffSetDir UserExamplesNG/dataset-AlgB-offline-SVN-basic/commitDiffSet
```

VERIFY OUTPUT:

```bash
python3 - <<'PY'
import json
from pathlib import Path

actual = json.loads(Path('/tmp/agg-userexample-ng-algb-offline-svn-basic.json').read_text())
expected = json.loads(Path('UserExamplesNG/dataset-AlgB-offline-SVN-basic/expected_result.json').read_text())

if actual != expected:
    raise SystemExit('example-AlgB-offline-SVN-basic mismatch')

print('example-AlgB-offline-SVN-basic OK')
PY
```

## `example-AlgB-offline-SVN-includedRevisionIds`

HAVE:

- an SVN-origin `commitDiffSet/`
- matching v26.03 `genCodeDescSet/`
- `queryArgs.json` that declares `includedRevisionIds` and `endRevisionId`

VERIFY INPUT:

```bash
python3 - <<'PY'
from pathlib import Path

base = Path('UserExamplesNG/dataset-AlgB-offline-SVN-includedRevisionIds')
query_args = base / 'genCodeDescSet' / 'queryArgs.json'

if not query_args.exists():
    raise SystemExit(f'Missing required query args file: {query_args}')

print('Input OK: subset replay dataset is ready')
PY
```

RUN:

```bash
python3 aggregateGenCodeDesc.py \
  --vcsType svn \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --algorithm B \
  --metric period_added_ai_ratio \
  --scope A \
  --outputFile /tmp/agg-userexample-ng-algb-offline-svn-included.json \
  --genCodeDescSetDir UserExamplesNG/dataset-AlgB-offline-SVN-includedRevisionIds/genCodeDescSet \
  --commitDiffSetDir UserExamplesNG/dataset-AlgB-offline-SVN-includedRevisionIds/commitDiffSet
```

VERIFY OUTPUT:

```bash
python3 - <<'PY'
import json
from pathlib import Path

actual = json.loads(Path('/tmp/agg-userexample-ng-algb-offline-svn-included.json').read_text())
expected = json.loads(Path('UserExamplesNG/dataset-AlgB-offline-SVN-includedRevisionIds/expected_result.json').read_text())

if actual != expected:
    raise SystemExit('example-AlgB-offline-SVN-includedRevisionIds mismatch')

print('example-AlgB-offline-SVN-includedRevisionIds OK')
PY
```

## Dataset: `dataset-localGIT-productionScale`

This generator materializes a heavy real Git repository for production-scale practice.

### Materialize `dataset-localGIT-productionScale`

```bash
python3 UserExamplesNG/dataset-localGIT-productionScale/generate_example.py \
  --outputDir /tmp/agg-userexample-ng-localgit-heavy \
  --force
```

### Verify `dataset-localGIT-productionScale` Inputs

```bash
python3 - <<'PY'
from pathlib import Path

base = Path('/tmp/agg-userexample-ng-localgit-heavy')
required = [
    base / 'repo',
    base / 'genCodeDescSet',
    base / 'manifest.json',
    base / 'expected_result.json',
]

for path in required:
    if not path.exists():
        raise SystemExit(f'Missing required input: {path}')

print('Input OK: local Git production-scale dataset is ready')
PY
```

### `example-AlgA-localGIT-productionScale`

HAVE:

- a large local Git repository
- matching v26.03 metadata for a branch-heavy history window

RUN:

```bash
LOCAL_GIT_HEAVY_REPO="$(python3 - <<'PY'
from pathlib import Path
print(Path('/tmp/agg-userexample-ng-localgit-heavy/repo').resolve())
PY
)"

python3 aggregateGenCodeDesc.py \
  --vcsType git \
  --repoURL "$LOCAL_GIT_HEAVY_REPO" \
  --repoBranch main \
  --startTime 2026-02-20 \
  --endTime 2026-03-31 \
  --scope A \
  --outputFile /tmp/agg-userexample-ng-alga-localgit-heavy.json \
  --genCodeDescSetDir /tmp/agg-userexample-ng-localgit-heavy/genCodeDescSet
```

VERIFY OUTPUT:

```bash
python3 - <<'PY'
import json
from pathlib import Path

actual = json.loads(Path('/tmp/agg-userexample-ng-alga-localgit-heavy.json').read_text())
expected = json.loads(Path('/tmp/agg-userexample-ng-localgit-heavy/expected_result.json').read_text())

if actual != expected:
    raise SystemExit('example-AlgA-localGIT-productionScale mismatch')

print('example-AlgA-localGIT-productionScale OK')
PY
```

## Related Docs

- `README_UserGuideNG.md`
- `README_UserGuide.md`
- `README_UserStoryNG.md`
