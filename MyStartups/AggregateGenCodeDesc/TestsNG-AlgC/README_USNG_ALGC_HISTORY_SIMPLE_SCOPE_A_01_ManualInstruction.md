# USNG-ALGC-HISTORY-SIMPLE-SCOPE-A-01 Manual Instruction

## Purpose

This document explains the intended manual verification flow for the first Algorithm C TDD scenario.

Unlike Algorithm A and Algorithm B manual flows, this AlgC flow does not require a live repository at runtime.
The runtime input is only the fixture directory containing `genCodeDescProtoV26.04` records and `query.json`.

## Fixture Directories

- Git-origin: `TestdataNG-AlgC/history-simple/scope-a/01/git/default`
- SVN-origin: `TestdataNG-AlgC/history-simple/scope-a/01/svn/default`

## Scenario Summary

The scenario models one file with an earlier out-of-window baseline revision and a later in-window revision.

- The older revision contributes surviving lines that remain outside the requested window.
- The later revision deletes one old AI line and adds three new surviving lines in the window.
- The final in-window surviving set is:
  - one full AI line
  - one partial AI line
  - one manual line

So the expected final result is:

- `totalCodeLines = 3`
- `fullGeneratedCodeLines = 1`
- `partialGeneratedCodeLines = 1`

## Important Distinction

Algorithm C does not need a repository at runtime, but the `genCodeDescProtoV26.04`
files must still be created from a real Git or SVN history at write time.

That means the manual flow has two phases:

1. create a tiny Git or SVN repository history
2. write the corresponding `*_genCodeDesc.json` files from those revisions

The fixture directories in `TestdataNG-AlgC` already contain the finished protocol
files. The steps below explain how to recreate them manually.

## Git: Create The Source Revisions First

Create a temporary Git repository with one baseline revision and one in-window revision.

```bash
mkdir -p /tmp/algc-us01-git/repo
cd /tmp/algc-us01-git/repo

git init -b main

# Optional only when this machine does not already have Git identity configured.
# git config user.name "AggregateGenCodeDesc Manual"
# git config user.email "manual@example.local"

mkdir -p src
cat > src/app.py <<'EOF'
prefix = raw
alpha = make_alpha(raw)
beta = make_beta(raw)
EOF

GIT_AUTHOR_DATE="2026-02-20T09:00:00Z" \
GIT_COMMITTER_DATE="2026-02-20T09:00:00Z" \
git add -A

GIT_AUTHOR_DATE="2026-02-20T09:00:00Z" \
GIT_COMMITTER_DATE="2026-02-20T09:00:00Z" \
git commit -m "algc-us01-git-r1"

cat > src/app.py <<'EOF'
prefix = raw
alpha = regenerate_alpha(raw)
beta = make_beta(raw)
gamma = assist_gamma(raw)
delta = raw
EOF

GIT_AUTHOR_DATE="2026-03-10T10:00:00Z" \
GIT_COMMITTER_DATE="2026-03-10T10:00:00Z" \
git add -A

GIT_AUTHOR_DATE="2026-03-10T10:00:00Z" \
GIT_COMMITTER_DATE="2026-03-10T10:00:00Z" \
git commit -m "algc-us01-git-r2"
```

Resolve the real revision ids:

```bash
cd /tmp/algc-us01-git/repo
REVISION_ID_R2="$(git rev-parse HEAD)"
REVISION_ID_R1="$(git rev-parse HEAD~1)"
echo "$REVISION_ID_R1"
echo "$REVISION_ID_R2"
```

## Git: Capture The Real `git blame` Output

This is the missing proof step.

AlgC requires the embedded `blame` fields to come from real VCS blame output,
so before writing the v26.04 protocol files, inspect the repository with
`git blame` and derive the embedded blame fields from that output.

Check the baseline revision:

```bash
cd /tmp/algc-us01-git/repo
git blame --line-porcelain "$REVISION_ID_R1" -- src/app.py
```

Check the final in-window revision:

```bash
cd /tmp/algc-us01-git/repo
git blame --line-porcelain "$REVISION_ID_R2" -- src/app.py
```

What you should observe from the final revision blame:

1. final line 1 still points to `REVISION_ID_R1`
2. final line 2 points to `REVISION_ID_R2`
3. final line 3 still points to `REVISION_ID_R1`
4. final line 4 points to `REVISION_ID_R2`
5. final line 5 points to `REVISION_ID_R2`

How that maps into AlgC protocol writing:

1. `blame.revisionId` comes from the blame header revision id
2. `blame.originalFilePath` comes from `filename ...`
3. `blame.originalLine` comes from the blame header origin-line field
4. `blame.timestamp` comes from the originating commit timestamp for that blamed revision
5. when a line disappears from the final snapshot because it was replaced, represent that old origin as a `changeType=delete` entry keyed by its original blame identity

## Git: Write The Two v26.04 Protocol Files

Create a protocol output directory:

```bash
mkdir -p /tmp/algc-us01-git/genCodeDescSet
```

Write the pre-window baseline record:

```bash
cat > "/tmp/algc-us01-git/genCodeDescSet/${REVISION_ID_R1}_genCodeDesc.json" <<EOF
{
  "protocolName": "generatedTextDesc",
  "protocolVersion": "26.04",
  "codeAgent": "ExampleAgent",
  "SUMMARY": {
    "totalCodeLines": 3,
    "fullGeneratedCodeLines": 1,
    "partialGeneratedCodeLines": 1
  },
  "DETAIL": [
    {
      "fileName": "src/app.py",
      "codeLines": [
        {
          "changeType": "add",
          "lineLocation": 1,
          "genRatio": 0,
          "genMethod": "Manual",
          "blame": {
            "revisionId": "${REVISION_ID_R1}",
            "originalFilePath": "src/app.py",
            "originalLine": 1,
            "timestamp": "2026-02-20T09:00:00Z"
          }
        },
        {
          "changeType": "add",
          "lineLocation": 2,
          "genRatio": 100,
          "genMethod": "codeCompletion",
          "blame": {
            "revisionId": "${REVISION_ID_R1}",
            "originalFilePath": "src/app.py",
            "originalLine": 2,
            "timestamp": "2026-02-20T09:00:00Z"
          }
        },
        {
          "changeType": "add",
          "lineLocation": 3,
          "genRatio": 40,
          "genMethod": "vibeCoding",
          "blame": {
            "revisionId": "${REVISION_ID_R1}",
            "originalFilePath": "src/app.py",
            "originalLine": 3,
            "timestamp": "2026-02-20T09:00:00Z"
          }
        }
      ]
    }
  ],
  "REPOSITORY": {
    "vcsType": "git",
    "repoURL": "https://example.local/repo/algc-demo",
    "repoBranch": "main",
    "revisionId": "${REVISION_ID_R1}",
    "revisionTimestamp": "2026-02-20T09:00:00Z"
  }
}
EOF
```

Write the in-window update record:

```bash
cat > "/tmp/algc-us01-git/genCodeDescSet/${REVISION_ID_R2}_genCodeDesc.json" <<EOF
{
  "protocolName": "generatedTextDesc",
  "protocolVersion": "26.04",
  "codeAgent": "ExampleAgent",
  "SUMMARY": {
    "totalCodeLines": 4,
    "fullGeneratedCodeLines": 1,
    "partialGeneratedCodeLines": 1
  },
  "DETAIL": [
    {
      "fileName": "src/app.py",
      "codeLines": [
        {
          "changeType": "delete",
          "blame": {
            "revisionId": "${REVISION_ID_R1}",
            "originalFilePath": "src/app.py",
            "originalLine": 2
          }
        },
        {
          "changeType": "add",
          "lineLocation": 2,
          "genRatio": 100,
          "genMethod": "codeCompletion",
          "blame": {
            "revisionId": "${REVISION_ID_R2}",
            "originalFilePath": "src/app.py",
            "originalLine": 2,
            "timestamp": "2026-03-10T10:00:00Z"
          }
        },
        {
          "changeType": "add",
          "lineLocation": 4,
          "genRatio": 50,
          "genMethod": "vibeCoding",
          "blame": {
            "revisionId": "${REVISION_ID_R2}",
            "originalFilePath": "src/app.py",
            "originalLine": 4,
            "timestamp": "2026-03-10T10:00:00Z"
          }
        },
        {
          "changeType": "add",
          "lineLocation": 5,
          "genRatio": 0,
          "genMethod": "Manual",
          "blame": {
            "revisionId": "${REVISION_ID_R2}",
            "originalFilePath": "src/app.py",
            "originalLine": 5,
            "timestamp": "2026-03-10T10:00:00Z"
          }
        }
      ]
    }
  ],
  "REPOSITORY": {
    "vcsType": "git",
    "repoURL": "https://example.local/repo/algc-demo",
    "repoBranch": "main",
    "revisionId": "${REVISION_ID_R2}",
    "revisionTimestamp": "2026-03-10T10:00:00Z"
  }
}
EOF
```

## SVN: Create The Source Revisions First

Create a tiny local SVN repository and two revisions.

```bash
mkdir -p /tmp/algc-us01-svn
svnadmin create /tmp/algc-us01-svn/repo
printf '#!/bin/sh\nexit 0\n' > /tmp/algc-us01-svn/repo/hooks/pre-revprop-change
chmod +x /tmp/algc-us01-svn/repo/hooks/pre-revprop-change

svn checkout file:///tmp/algc-us01-svn/repo /tmp/algc-us01-svn/wc
mkdir -p /tmp/algc-us01-svn/wc/trunk/src
svn add /tmp/algc-us01-svn/wc/trunk

cat > /tmp/algc-us01-svn/wc/trunk/src/app.py <<'EOF'
prefix = raw
alpha = make_alpha(raw)
beta = make_beta(raw)
EOF

svn add /tmp/algc-us01-svn/wc/trunk/src/app.py
svn commit -m "algc-us01-svn-r100" /tmp/algc-us01-svn/wc
svn propset --revprop -r 1 svn:date "2026-02-20T09:00:00.000000Z" file:///tmp/algc-us01-svn/repo

cat > /tmp/algc-us01-svn/wc/trunk/src/app.py <<'EOF'
prefix = raw
alpha = regenerate_alpha(raw)
beta = make_beta(raw)
gamma = assist_gamma(raw)
delta = raw
EOF

svn commit -m "algc-us01-svn-r101" /tmp/algc-us01-svn/wc
svn propset --revprop -r 2 svn:date "2026-03-10T10:00:00.000000Z" file:///tmp/algc-us01-svn/repo
```

For this tiny local repository, the real SVN revisions are `1` and `2`.
The checked-in fixture uses symbolic ids `r100` and `r101` to keep the test
data stable and readable. When reproducing manually, you can either:

1. write files named `1_genCodeDesc.json` and `2_genCodeDesc.json`, or
2. keep the fixture-style names `r100_genCodeDesc.json` and `r101_genCodeDesc.json` if the embedded `REPOSITORY.revisionId` and `blame.revisionId` values match those symbolic ids consistently.

## SVN: Capture The Real `svn blame` Output

This is the corresponding proof step for SVN.

AlgC requires the embedded `blame` fields to come from real VCS blame output,
so before writing the v26.04 protocol files, inspect the repository with
`svn blame` and derive the embedded blame fields from that output.

Check the baseline revision:

```bash
svn blame --xml -g -r 1 file:///tmp/algc-us01-svn/repo/trunk/src/app.py
```

Check the final in-window revision:

```bash
svn blame --xml -g -r 2 file:///tmp/algc-us01-svn/repo/trunk/src/app.py
```

You can also inspect the exact file content at the final revision:

```bash
svn cat -r 2 file:///tmp/algc-us01-svn/repo/trunk/src/app.py
```

What you should observe from the final revision blame:

1. one surviving pre-window line still maps to the older revision
2. the rewritten AI line maps to the newer revision
3. the preserved older line keeps its earlier origin
4. the newly added lines map to the newer revision

How that maps into AlgC protocol writing:

1. `blame.revisionId` comes from the SVN blame revision
2. `blame.originalFilePath` is the repository-relative origin path for the blamed line
3. `blame.originalLine` is the origin line identity carried into the protocol
4. `blame.timestamp` comes from the originating SVN revision timestamp
5. lines that no longer survive at the end revision become `changeType=delete` entries keyed by their prior blame identity

## SVN: Write The Two v26.04 Protocol Files

Create a protocol output directory:

```bash
mkdir -p /tmp/algc-us01-svn/genCodeDescSet
```

Write the baseline record:

```bash
cat > /tmp/algc-us01-svn/genCodeDescSet/r100_genCodeDesc.json <<'EOF'
{
  "protocolName": "generatedTextDesc",
  "protocolVersion": "26.04",
  "codeAgent": "ExampleAgent",
  "SUMMARY": {
    "totalCodeLines": 3,
    "fullGeneratedCodeLines": 1,
    "partialGeneratedCodeLines": 1
  },
  "DETAIL": [
    {
      "fileName": "src/app.py",
      "codeLines": [
        {
          "changeType": "add",
          "lineLocation": 1,
          "genRatio": 0,
          "genMethod": "Manual",
          "blame": {
            "revisionId": "r100",
            "originalFilePath": "src/app.py",
            "originalLine": 1,
            "timestamp": "2026-02-20T09:00:00Z"
          }
        },
        {
          "changeType": "add",
          "lineLocation": 2,
          "genRatio": 100,
          "genMethod": "codeCompletion",
          "blame": {
            "revisionId": "r100",
            "originalFilePath": "src/app.py",
            "originalLine": 2,
            "timestamp": "2026-02-20T09:00:00Z"
          }
        },
        {
          "changeType": "add",
          "lineLocation": 3,
          "genRatio": 40,
          "genMethod": "vibeCoding",
          "blame": {
            "revisionId": "r100",
            "originalFilePath": "src/app.py",
            "originalLine": 3,
            "timestamp": "2026-02-20T09:00:00Z"
          }
        }
      ]
    }
  ],
  "REPOSITORY": {
    "vcsType": "svn",
    "repoURL": "file:///example/svn/algc-demo",
    "repoBranch": "trunk",
    "revisionId": "r100",
    "revisionTimestamp": "2026-02-20T09:00:00Z"
  }
}
EOF
```

Write the in-window update record:

```bash
cat > /tmp/algc-us01-svn/genCodeDescSet/r101_genCodeDesc.json <<'EOF'
{
  "protocolName": "generatedTextDesc",
  "protocolVersion": "26.04",
  "codeAgent": "ExampleAgent",
  "SUMMARY": {
    "totalCodeLines": 4,
    "fullGeneratedCodeLines": 1,
    "partialGeneratedCodeLines": 1
  },
  "DETAIL": [
    {
      "fileName": "src/app.py",
      "codeLines": [
        {
          "changeType": "delete",
          "blame": {
            "revisionId": "r100",
            "originalFilePath": "src/app.py",
            "originalLine": 2
          }
        },
        {
          "changeType": "add",
          "lineLocation": 2,
          "genRatio": 100,
          "genMethod": "codeCompletion",
          "blame": {
            "revisionId": "r101",
            "originalFilePath": "src/app.py",
            "originalLine": 2,
            "timestamp": "2026-03-10T10:00:00Z"
          }
        },
        {
          "changeType": "add",
          "lineLocation": 4,
          "genRatio": 50,
          "genMethod": "vibeCoding",
          "blame": {
            "revisionId": "r101",
            "originalFilePath": "src/app.py",
            "originalLine": 4,
            "timestamp": "2026-03-10T10:00:00Z"
          }
        },
        {
          "changeType": "add",
          "lineLocation": 5,
          "genRatio": 0,
          "genMethod": "Manual",
          "blame": {
            "revisionId": "r101",
            "originalFilePath": "src/app.py",
            "originalLine": 5,
            "timestamp": "2026-03-10T10:00:00Z"
          }
        }
      ]
    }
  ],
  "REPOSITORY": {
    "vcsType": "svn",
    "repoURL": "file:///example/svn/algc-demo",
    "repoBranch": "trunk",
    "revisionId": "r101",
    "revisionTimestamp": "2026-03-10T10:00:00Z"
  }
}
EOF
```

## Then Run Algorithm C Against The Generated Files

The important rule is: do not invent the embedded blame first and then treat the
repository history as illustrative. The order must be the reverse:

1. create the real Git/SVN history
2. run real `git blame` or `svn blame`
3. copy that provenance into the v26.04 `blame` fields
4. then run Algorithm C against those generated files

## Manual CLI Command

Git-origin fixture:

```bash
python3 aggregateGenCodeDesc.py \
  --vcsType git \
  --repoURL https://example.local/repo/algc-demo \
  --repoBranch main \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --algorithm C \
  --scope A \
  --genCodeDescSetDir TestdataNG-AlgC/history-simple/scope-a/01/git/default \
  --outputFile /tmp/algc-us01-git-out.json
```

SVN-origin fixture:

```bash
python3 aggregateGenCodeDesc.py \
  --vcsType svn \
  --repoURL file:///example/svn/algc-demo \
  --repoBranch trunk \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --algorithm C \
  --scope A \
  --genCodeDescSetDir TestdataNG-AlgC/history-simple/scope-a/01/svn/default \
  --outputFile /tmp/algc-us01-svn-out.json
```

## Current TDD Expectation

At this stage, failure is acceptable and expected until the first Algorithm C runtime slice is implemented.

The first passing milestone for this story is:

1. CLI accepts `--algorithm C`.
2. CLI reads v26.04 protocol files from `--genCodeDescSetDir`.
3. CLI accumulates add/delete entries in revisionTimestamp order.
4. CLI filters surviving lines by `blame.timestamp`.
5. CLI returns the expected `SUMMARY`.