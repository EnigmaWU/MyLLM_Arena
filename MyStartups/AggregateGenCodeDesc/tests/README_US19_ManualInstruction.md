# US-19 Manual Instruction

## Purpose

This document describes how to verify `US-19` manually in standalone mode, outside the automated test harness.

The current goal is to prove that `aggregateGenCodeDesc.py` can:

- handle SVN repositories through the offline replay path (`--commitDiffSetDir`) under Algorithm B (`period_added_ai_ratio`)
- work **without** `--repoURL` and `--repoBranch` when `--commitDiffSetDir` is provided
- replay patch files to reconstruct file state and count period-added lines
- produce the expected protocol-shaped aggregate output

## Current Scope

This manual flow matches the current implementation boundary:

- SVN (offline fixture replay via `--commitDiffSetDir`)
- `Algorithm B` only (`--metric period_added_ai_ratio`)
- `Scope A` only
- `metadataSource=genCodeDesc` only
- `--genCodeDescSetDir` as the current local metadata adapter
- `--repoURL` and `--repoBranch` are **optional** (demonstrated without them)

## Files Used As Reference

- `aggregateGenCodeDesc.py`
- `tests/test_us19_period_added_svn_subset_tdd.py`

## Step 1: Create A Temporary Working Area

```bash
mkdir -p /tmp/agg-us19-manual/protocols
mkdir -p /tmp/agg-us19-manual/commitDiffSet
```

## Step 2: Create The Offline Patch Files

These patches simulate SVN commit diffs. No real SVN repository is needed.

```bash
# r1 patch (revision 2): create file with 2 lines
cat > /tmp/agg-us19-manual/commitDiffSet/2_commitDiff.patch <<'EOF'
diff --git a/trunk/src/report.py b/trunk/src/report.py
--- /dev/null
+++ b/trunk/src/report.py
@@ -0,0 +1,2 @@
+def report():
+    data = ai_fetch()
EOF

# r2 patch (revision 3): add 1 more line
cat > /tmp/agg-us19-manual/commitDiffSet/3_commitDiff.patch <<'EOF'
diff --git a/trunk/src/report.py b/trunk/src/report.py
--- a/trunk/src/report.py
+++ b/trunk/src/report.py
@@ -1,2 +1,3 @@
 def report():
     data = ai_fetch()
+    result = ai_process(data)
EOF
```

## Step 3: Create The Revision-Level genCodeDesc Records

```bash
# Protocol for revision 2: line 2 is AI-generated
cat > /tmp/agg-us19-manual/protocols/2_genCodeDesc.json <<'EOF'
{
  "protocolName": "generatedTextDesc",
  "protocolVersion": "26.03",
  "SUMMARY": {
    "totalCodeLines": 1,
    "fullGeneratedCodeLines": 1,
    "partialGeneratedCodeLines": 0
  },
  "REPOSITORY": {
    "vcsType": "svn",
    "repoURL": "file:///svn/testrepo",
    "repoBranch": "trunk",
    "revisionId": "2"
  },
  "DETAIL": [
    {
      "fileName": "trunk/src/report.py",
      "codeLines": [
        {"lineLocation": 2, "genRatio": 100}
      ]
    }
  ]
}
EOF

# Protocol for revision 3: line 3 is AI-generated
cat > /tmp/agg-us19-manual/protocols/3_genCodeDesc.json <<'EOF'
{
  "protocolName": "generatedTextDesc",
  "protocolVersion": "26.03",
  "SUMMARY": {
    "totalCodeLines": 1,
    "fullGeneratedCodeLines": 1,
    "partialGeneratedCodeLines": 0
  },
  "REPOSITORY": {
    "vcsType": "svn",
    "repoURL": "file:///svn/testrepo",
    "repoBranch": "trunk",
    "revisionId": "3"
  },
  "DETAIL": [
    {
      "fileName": "trunk/src/report.py",
      "codeLines": [
        {"lineLocation": 3, "genRatio": 100}
      ]
    }
  ]
}
EOF
```

## Step 4: Create The Query Metadata

The `query.json` tells the offline path which revisions to include.

```bash
cat > /tmp/agg-us19-manual/protocols/query.json <<'EOF'
{
  "includedRevisionIds": ["2", "3"],
  "endRevisionId": "3"
}
EOF
```

## Step 5: Run The CLI (Without --repoURL And --repoBranch)

This demonstrates the new capability: when `--commitDiffSetDir` is provided, `--repoURL` and `--repoBranch` are optional.

```bash
cd /Users/enigmawu/VSCode/MyLLM_Arena/MyStartups/AggregateGenCodeDesc

python3 aggregateGenCodeDesc.py \
  --vcsType svn \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --algorithm B \
  --metric period_added_ai_ratio \
  --scope A \
  --outputFile /tmp/agg-us19-manual/out.json \
  --genCodeDescSetDir /tmp/agg-us19-manual/protocols \
  --commitDiffSetDir /tmp/agg-us19-manual/commitDiffSet
```

## Step 6: Inspect The Output

```bash
cat /tmp/agg-us19-manual/out.json
```

Expected shape:

```json
{
  "protocolName": "generatedTextDesc",
  "protocolVersion": "26.03",
  "SUMMARY": {
    "totalCodeLines": 3,
    "fullGeneratedCodeLines": 2,
    "partialGeneratedCodeLines": 0
  },
  "REPOSITORY": {
    "vcsType": "svn",
    "repoURL": "",
    "repoBranch": "",
    "revisionId": "3"
  }
}
```

## Step 7: What To Check

Verify these values:

1. `SUMMARY.totalCodeLines == 3` — all 3 lines were added in-window (2 from r1 + 1 from r2)
2. `SUMMARY.fullGeneratedCodeLines == 2` — the 2 AI lines (`ai_fetch` and `ai_process`)
3. `SUMMARY.partialGeneratedCodeLines == 0`
4. `REPOSITORY.vcsType == "svn"`
5. `REPOSITORY.revisionId == "3"` (the end revision)
6. The CLI exited with code 0 — no error about missing `--repoURL` or `--repoBranch`

## Alternative: Run With --repoURL And --repoBranch For Consistency Checking

You can also run with `--repoURL` and `--repoBranch` for metadata consistency checking. They are used only to verify that the protocol files' REPOSITORY fields match:

```bash
python3 aggregateGenCodeDesc.py \
  --vcsType svn \
  --repoURL file:///svn/testrepo \
  --repoBranch trunk \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --algorithm B \
  --metric period_added_ai_ratio \
  --scope A \
  --outputFile /tmp/agg-us19-manual/out_with_repo.json \
  --genCodeDescSetDir /tmp/agg-us19-manual/protocols \
  --commitDiffSetDir /tmp/agg-us19-manual/commitDiffSet
```

The output should be identical, with `repoURL` and `repoBranch` populated from the protocol files.
