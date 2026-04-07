# AggregateGenCodeDesc — Introduction to Algorithm A, B, and C

## Purpose

This document introduces the three attribution algorithms implemented or planned in
AggregateGenCodeDesc and explains what problem each solves, what its inputs are,
and what pitfalls it still carries.

The shared goal of all three algorithms is identical:

> For the source-code lines that survive in the final repository snapshot at `endTime`
> and whose current form originated inside `[startTime, endTime]`,
> how much is attributable to AI?

The algorithms differ in **how they discover line origins** — not in what they measure.

---

## One-Glance Comparison

```mermaid
mindmap
  root((AggregateGenCodeDesc))
    Algorithm A
      blame-based end-snapshot
      live VCS access required
      git blame / svn blame
      genCodeDesc v26.03
      production quality today
    Algorithm B
      diff replay without blame
      commitDiffSet artifacts
      genCodeDesc v26.03
      offline capable
      higher correctness risk
    Algorithm C
      embedded blame
      genCodeDesc v26.04 only
      zero VCS access
      exhaustive DETAIL required
      planned
```

| | **Algorithm A** | **Algorithm B** | **Algorithm C** |
|---|---|---|---|
| Core technique | live `git/svn blame` | offline diff replay | embedded `blame` in genCodeDesc |
| Repository access at runtime | **required** | not required | **not required** |
| genCodeDesc version | v26.03 | v26.03 | **v26.04** |
| DETAIL completeness | AI lines only | AI lines only | **all surviving lines** |
| Production status | production quality | narrow replay paths active | planned |
| Correctness authority | VCS blame (authoritative) | rebuilt partial blame (risk) | codeAgent at write time (trusted) |

---

## Algorithm A — Blame-Based End-Snapshot Attribution

### What it is

Algorithm A is the primary, production-quality baseline.
It starts from the live file snapshot at `endTime`, runs `git blame` or `svn blame`
on every surviving source line, and uses the blame result to discover which commit
last introduced the current form of each line.
Lines whose origin commit falls inside `[startTime, endTime]` are in scope.
For each in-scope line, Algorithm A looks up `genRatio` from the matching
per-revision `genCodeDesc` (v26.03) record.

### Data Flow

```mermaid
flowchart TD
    Q[Query\nrepoURL · repoBranch · startTime · endTime]
    Q --> RA[RepositoryAnalyzer]
    RA --> S[Resolve end snapshot at endTime\nlist surviving source files]
    S --> B[Run git blame / svn blame\nwith rename detection\nper surviving file]
    B --> F[Filter: keep lines whose\nblame timestamp ∈ startTime~endTime]
    F --> R[Distinct origin revisionId set]
    R --> P[GenCodeDescProvider\nfetch one genCodeDesc v26.03 per revisionId]
    P --> J[AggregationEngine\njoin blame origin file+line → genRatio]
    F --> J
    J --> O[SUMMARY output\ntotalCodeLines · fullGenerated · partialGenerated]
```

### What problem it solves

- Directly answers the P0 metric on the live snapshot.
- Rename and move detection is handled by mature VCS blame implementations.
- Low logical risk: blame is the authoritative source of line origin; no partial reconstruction needed.
- Works for both Git and SVN.

### Pitfalls

| Pitfall | Detail |
|---|---|
| Requires live repository access | A local checkout must be present at runtime. The current implementation does not clone or fetch remote repositories automatically. `--workingDir` is required when `--repoURL` is a logical URL. |
| Blame performance on large repositories | `git/svn blame` runs per surviving file. Large repos with many large files can make this slow. |
| Depends on VCS blame quality | Blame correctness is only as good as the VCS implementation. SVN blame with complex mergeinfo or path-copy history may return imprecise results. |
| per-revision genCodeDesc required | One v26.03 file must exist for every origin revision discovered by blame. Missing records are treated as unattributed, not as an error. |
| Remote transport is out of scope | Network-accessing remote-repository clients are not validated. |

---

## Algorithm B — Incremental Lineage Reconstruction Without Blame

### What it is

Algorithm B replays an ordered sequence of commit diff patches (`commitDiffSet`)
to reconstruct line ownership incrementally.
Instead of asking the VCS "who last changed this line?", it simulates the history
by applying diffs in order and tracking which commit introduced each surviving line.
No live repository access is needed at runtime.

### Data Flow

```mermaid
flowchart TD
    Q[Query\nrepoURL · repoBranch · startTime · endTime]
    Q --> CDP[CommitDiffSetDirProvider\nload ordered diff patches]
    CDP --> D1[Diff patch for revision r1]
    CDP --> D2[Diff patch for revision r2]
    CDP --> DN[Diff patch for revision rN]
    D1 & D2 & DN --> RE[Replay Engine\napply_commit_diff_file_to_line_states\nper revision in order]
    RE --> LS[Final line-state map\nsurviving lines with origin revisionId]
    LS --> F[Filter: keep lines whose\norigin revision timestamp ∈ startTime~endTime]
    F --> P[GenCodeDescProvider\nfetch one genCodeDesc v26.03 per revisionId]
    P --> J[AggregationEngine\njoin origin file+line → genRatio]
    F --> J
    J --> O[SUMMARY output\ntotalCodeLines · fullGenerated · partialGenerated]
```

### What problem it solves

- Enables offline analysis without a live repository checkout.
- Useful when blame is operationally slow or unavailable.
- Diff artifacts can be pre-indexed and queried cheaply.
- Can compute history-process metrics beyond live-snapshot attribution.
- Enables deterministic replay in test environments.

### Pitfalls

| Pitfall | Detail |
|---|---|
| Correctness risk is higher | Algorithm B effectively rebuilds a partial blame engine. Any gap in the replay logic produces wrong attributions silently. |
| commitDiffSet artifacts must be prepared | One unified-diff patch file per replayed revision must exist before the run. Missing patches cause the contract to fail fast. |
| Merge-aware lineage replay is complex | Choosing a defensible first-parent vs merged-parent accounting policy for merge commits is non-trivial. Production readiness for merge-heavy histories requires explicit TDD before any claim is safe. |
| SVN parity is limited | SVN path-copy and mergeinfo semantics introduce replay edge cases that are not yet fully covered. |
| Scalability not yet independently validated | Do not reuse Algorithm A production-readiness evidence as Algorithm B evidence. A dedicated scalability gate is required. |
| Still needs per-revision genCodeDesc v26.03 | Same metadata dependency as Algorithm A; only the blame step is removed. |

---

## Algorithm C — Embedded Blame, Pure genCodeDesc

### What it is

Algorithm C is a planned offline algorithm that requires **no repository access and
no diff artifacts at runtime**.
The codeAgent embeds `git blame` or `svn blame` information directly into each line
entry of a `genCodeDescProtoV26.04.json` file at write time.
Because every surviving line carries `blame.revisionId`, `blame.originalFilePath`,
`blame.originalLine`, and `blame.timestamp`, a downstream consumer can apply the
`[startTime, endTime]` filter and read `genRatio` directly — no VCS, no diffs needed.

DETAIL must be **exhaustive**: every surviving line must appear, including human lines
recorded as `genRatio=0 / genMethod=Manual`.

### Data Flow

```mermaid
flowchart TD
    W[codeAgent at commit time\ngit blame / svn blame]
    W --> GCD["genCodeDescProtoV26.04.json\nexhaustive DETAIL:\n• AI lines genRatio>0\n• Manual lines genRatio=0\n• blame per line"]

    subgraph Runtime["Algorithm C Runtime (zero VCS access)"]
        GCD --> F["Filter DETAIL entries\nblame.timestamp ∈ [startTime, endTime]"]
        F --> AI[AI lines: genRatio > 0\ncount full / partial]
        F --> HU[Manual lines: genRatio = 0\ncount total only]
        AI & HU --> O[SUMMARY output\ntotalCodeLines · fullGenerated · partialGenerated]
    end
```

### What problem it solves

- Zero VCS access at analysis time — no checkout, no subprocess, no network.
- Simpler deployment: one JSON file per revision is all that is needed.
- Same metric semantics as Algorithm A and Algorithm B.
- Works for both Git-origin and SVN-origin blame (VCS type is embedded metadata).
- Single-file self-contained analysis enables fully air-gapped or edge deployments.

### Pitfalls

| Pitfall | Detail |
|---|---|
| Requires v26.04 exhaustive DETAIL | The codeAgent must record every surviving line, not just AI-generated ones. File size grows significantly compared to v26.03. |
| Blame accuracy depends on codeAgent | Correctness at consume time is entirely trusted from the codeAgent's write-time blame call. No independent VCS verification is possible during analysis. |
| lineRange constraint for Manual lines | A lineRange entry is only valid when all lines in that range share the same blame origin. Lines with different blame origins must each have a separate `lineLocation` entry. |
| No catch for stale blame | If a codeAgent produced a genCodeDesc file and the repository was later force-pushed or amended, the embedded blame is silently stale. |
| Implementation not yet started | Algorithm C is planned only. Protocol shape is defined in `genCodeDescProtoV26.04.json`; no runtime exists yet. |

---

## How the Three Algorithms Relate

```mermaid
flowchart LR
    subgraph Input["Inputs at analysis time"]
        R[(Live repository\ngit / svn)]
        D[(commitDiffSet\norderd patch files)]
        J[(genCodeDescProtoV26.04\nexhaustive + blame embedded)]
    end

    subgraph Meta["Per-revision genCodeDesc"]
        M03[(genCodeDesc v26.03\nAI lines only)]
        M04[(genCodeDesc v26.04\nall lines + blame)]
    end

    subgraph Algs["Algorithms"]
        A[Algorithm A\nlive blame]
        B[Algorithm B\ndiff replay]
        C[Algorithm C\nembedded blame]
    end

    R --> A
    M03 --> A
    D --> B
    M03 --> B
    J --> C
    M04 --> C

    A --> OUT[SUMMARY\ntotalCodeLines\nfullGenerated\npartialGenerated]
    B --> OUT
    C --> OUT
```

The three algorithms are **semantically equivalent** for the same scenario.
The choice is driven by what is available and what trade-offs are acceptable:

```mermaid
flowchart TD
    Start([Start: choose an algorithm]) --> Q1{Live repository\naccessible at runtime?}
    Q1 -->|Yes| Q2{Blame performance\nacceptable?}
    Q1 -->|No| Q3{commitDiffSet\nartifacts prepared?}
    Q2 -->|Yes| AlgA[✅ Algorithm A\npreferred baseline]
    Q2 -->|No| Q3
    Q3 -->|Yes| Q4{Merge-heavy\nhistory?}
    Q3 -->|No| Q5{genCodeDesc v26.04\nwith exhaustive DETAIL?}
    Q4 -->|No| AlgB[⚠️ Algorithm B\noffline replay]
    Q4 -->|Yes, defended by TDD| AlgB
    Q5 -->|Yes| AlgC[🔬 Algorithm C\nplanned · zero VCS]
    Q5 -->|No| Block[❌ Cannot proceed\ninsufficient inputs]
```

---

## Summary: What Each Algorithm Leaves Unsolved

| | **Algorithm A** | **Algorithm B** | **Algorithm C** |
|---|---|---|---|
| Works without a live repository | ❌ | ✅ | ✅ |
| Works without diff artifacts | ✅ | ❌ | ✅ |
| Correctness authority | VCS blame (highest) | rebuilt partial blame (medium) | codeAgent write-time (trusted but unverifiable at consume time) |
| Merge-heavy history at scale | ✅ | ⚠️ needs explicit TDD per topology | ✅ (blame already resolved at write time) |
| Large-repo performance risk | blame can be slow | replay can be slow for long windows | file parsing only — scales with DETAIL size |
| Remote repository support | ⚠️ not yet validated | ✅ (no VCS needed) | ✅ (no VCS needed) |
| Production status | ✅ production quality | ⚠️ narrow paths active | 🔬 planned |
