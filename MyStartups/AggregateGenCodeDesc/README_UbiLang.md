# AggregateGenCodeDesc — Ubiquitous Language

This document defines every domain term used across code, CLI, protocol, tests, and documentation.
All contributors and AI agents must use these terms consistently.

---

## 1. Core Concepts

| Term | Definition | Appears In |
|---|---|---|
| **genCodeDesc** | External revision-level metadata record describing which lines in a commit are AI-generated; indexed by `repoURL + repoBranch + revisionId` | code, protocol, CLI, docs |
| **generatedTextDesc** | The protocol name for genCodeDesc records; covers both source code and document text | protocol (`protocolName`), code |
| **PROTOCOL_VERSION** | Versioned contract identifier for the genCodeDesc protocol schema (currently `"26.03"`) | code, protocol (`protocolVersion`) |
| **AggregateGenCodeDesc** | The analyzer tool itself — aggregates revision-level AI attribution into a single repository-level result for a time window | code (module), docs |
| **LiveLine** | A source/doc line that survives (is present) in the repository snapshot at `endTime`; the unit of measurement | code (log label), docs |
| **live changed source code** | The subset of LiveLines whose current form was added or modified within `startTime~endTime` — the population measured by the primary metric | docs |
| **end snapshot** | The repository state at the latest commit whose commit time ≤ `endTime`; the baseline for all live-line enumeration | code, docs |
| **origin revision** | The revision that last introduced the current form of a surviving line, discovered via blame | code (`origin_revision_id`), docs |
| **metadata identity key** | The composite key `repoURL + repoBranch + revisionId` used to look up one genCodeDesc record from the external metadata store | docs (ArchDesign), code |
| **line-level lookup key** | `origin file path + origin line number` — used after fetching a revision's metadata to resolve a specific line's `genRatio` | docs (ArchDesign), code |

## 2. Metrics & Classifications

| Term | Definition | Appears In |
|---|---|---|
| **genRatio** | Integer 0–100 indicating the percentage of AI attribution for a single line; 100 = fully AI-generated, 0 = fully human | protocol, code, docs |
| **AI_Window_Live_Ratio** | The primary metric formula: `Sum(line.genRatio/100 for in-window live lines) / Total_Live_Changed_Lines_In_Window` | docs (README formula) |
| **live_changed_source_ratio** | Metric identifier string for the primary (Algorithm A default) metric — AI ratio among live changed source lines | code, CLI `--metric` |
| **period_added_ai_ratio** | Metric identifier string for the Algorithm B period-contribution metric — AI ratio among lines *added* during the period | code, CLI `--metric`, docs (US-6) |
| **100%-ai** | Classification label for a line with `genRatio == 100` (fully AI-generated) | code (`describe_ratio`) |
| **N%-ai** | Classification label for a line with `0 < genRatio < 100` (partial AI) | code (`describe_ratio`) |
| **human/unattributed** | Classification label for a line with `genRatio == 0` or no metadata | code (`describe_ratio`) |
| **TransitionHint** | Best-effort log diagnostic showing how a line's attribution changed from parent → current revision (e.g., `human/unattributed→100%-ai`) | code (log label) |
| **best_effort_transition** | The formatted transition string inside a TransitionHint (e.g., `best_effort_transition=human/unattributed->100%-ai`) | code (`best_effort_transition_hint`) |

### SUMMARY Count Fields

| Field | Definition |
|---|---|
| **totalCodeLines** | Count of all non-blank added ('+') code lines in the commit diff (excludes deleted and blank lines) |
| **fullGeneratedCodeLines** | Subset of added code lines whose `genRatio` is 100 |
| **partialGeneratedCodeLines** | Subset of added code lines whose `genRatio` is between 1 and 99 |
| **totalDocLines** | (Scope C) Count of represented documentation lines in scope |
| **fullGeneratedDocLines** | (Scope C) Doc lines with `genRatio == 100` |
| **partialGeneratedDocLines** | (Scope C) Doc lines with `0 < genRatio < 100` |

## 3. Algorithms & Scopes

### Algorithms

| Term | Definition |
|---|---|
| **Algorithm A** | Primary algorithm: blame-based end-snapshot attribution — resolves origin revisions via `git blame`/`svn blame`, then joins with external metadata |
| **Algorithm B** | Alternative incremental-replay algorithm: reconstructs file state by replaying commit diffs forward, then computes metrics from the reconstructed line states |

### Scopes

| Term | Definition |
|---|---|
| **Scope A** | Default scope: pure source code only — counts only non-blank, non-comment lines in `SOURCE_EXTENSIONS` files |
| **Scope B** | Source code with comments — counts all non-blank lines (including comments) in source files |
| **Scope C** | Documentation text — counts all non-blank lines in `DOC_EXTENSIONS` files, using `docLines` protocol field |
| **Scope D** | All text — union of source and documentation files into a single combined aggregate |

### File Extension Sets

| Term | Definition |
|---|---|
| **SOURCE_EXTENSIONS** | File extensions recognized as source code: `.c`, `.cc`, `.cpp`, `.cxx`, `.go`, `.h`, `.hpp`, `.java`, `.js`, `.py`, `.rs`, `.ts` |
| **DOC_EXTENSIONS** | File extensions recognized as documentation: `.md`, `.rst`, `.txt` |

### Algorithm B TDD Stages

| Stage | Definition |
|---|---|
| **B0** | Contract lock |
| **B1** | Single-branch baseline |
| **B2** | Deletions/rewrites |
| **B3** | Rename |
| **B4** | Merge-aware |
| **B5** | SVN parity |
| **B6** | Scalability gate |

## 4. CLI Arguments

| Argument | Definition |
|---|---|
| `--repoURL` | Logical repository identity URL (or local absolute path for Git) |
| `--repoBranch` | Target branch (Git branch name or SVN branch/trunk path) |
| `--startTime` | Inclusive start of the analysis time window (ISO-8601 date) |
| `--endTime` | Inclusive end of the analysis time window (ISO-8601 date) |
| `--vcsType` | Version control system type: `git` or `svn` |
| `--algorithm` | Algorithm selector: `A` (blame-based) or `B` (replay-based) |
| `--metric` | Explicit metric selector (e.g., `live_changed_source_ratio`, `period_added_ai_ratio`) |
| `--scope` | Scope selector: `A`, `B`, `C`, or `D` |
| `--outputFile` | Path to write the JSON result (stdout if omitted) |
| `--outputFormat` | Output format (only `json` currently supported) |
| `--metadataSource` | Metadata source mode (only `genCodeDesc` currently supported) |
| `--genCodeDescSetDir` | Path to a local directory containing revision-level genCodeDesc JSON files (fixture-driven provider) |
| `--commitDiffSetDir` | Path to a local directory containing commit-diff patch files for Algorithm B offline replay |
| `--workingDir` | Path to a local Git checkout when `--repoURL` is a logical (non-local) URL |
| `--failOnMissingProtocol` | Error if any in-scope revision has no genCodeDesc record |
| `--warnOnMissingProtocol` | Warn (instead of silent skip) when a revision has no genCodeDesc record |
| `--includeBreakdown` | Breakdown granularity level (default `none`) |
| `--logLevel` | Logging verbosity: `quiet`, `info`, or `debug` |
| `--timeout` | Per-command execution timeout in seconds (default 30) |
| `--maxRuntime` | Overall analysis timeout in seconds (default 3600) |

## 5. Protocol Structure

### Top-Level Sections

| Section | Definition |
|---|---|
| **SUMMARY** | Aggregate line counts (`totalCodeLines`, `fullGeneratedCodeLines`, `partialGeneratedCodeLines`, or Doc equivalents) |
| **DETAIL** | Array of per-file entries, each containing `fileName` and `codeLines`/`docLines` arrays |
| **REPOSITORY** | Repository identity: `vcsType`, `repoURL`, `repoBranch`, `revisionId` |
| **CREDENTIAL** | Authentication tokens; treated as ignored envelope metadata by the analyzer |
| **WARNINGS** | Output-only: array of runtime warning messages emitted during analysis |

### DETAIL Sub-Fields

| Field | Definition |
|---|---|
| **fileName** | Relative file path within the repository |
| **codeLines** | Array of line-level AI attribution entries for source code files |
| **docLines** | Array of line-level AI attribution entries for documentation files |
| **lineLocation** | Exact single line number with attributed `genRatio` |
| **lineRange** | Contiguous range (`from`/`to`) of lines sharing one `genRatio` |
| **genMethod** | How a line was generated (e.g., `"codeCompletion"`, `"vibeCoding"`) |

### REPOSITORY Sub-Fields

| Field | Definition |
|---|---|
| **revisionId** | VCS commit hash (Git) or revision number (SVN) identifying one revision |
| **vcsType** | `"git"` or `"svn"` |
| **repoURL** | Canonical repository URL or local path |
| **repoBranch** | Branch name or SVN path where the revision was produced |
| **codeAgent** | AI coding agent that produced the genCodeDesc (e.g., `"HuayanCoder"`) |
| **protocolName** | Must be `"generatedTextDesc"` |
| **protocolVersion** | Schema version string (e.g., `"26.03"`) |

### Fixture Files

| File | Definition |
|---|---|
| **query.json** | Test fixture specifying Algorithm B query input (metric, includedRevisionIds, endRevisionId) |
| **expected_result.json** | Golden expected output used for acceptance test comparison |
| **`*_genCodeDesc.json`** | One revision's genCodeDesc metadata file in `genCodeDescSetDir` |
| **`*_commitDiff.patch`** | One revision's commit diff patch file in `commitDiffSetDir` |

## 6. Internal Implementation

### Data Classes

| Class | Definition |
|---|---|
| **BlameLine** | One parsed blame output entry: `revision_id`, `origin_file`, `origin_line`, `final_line`, `content` |
| **LineState** | One line tracked during Algorithm B replay: `content`, `origin_revision_id`, `gen_ratio` |
| **IndexedFileDetail** | Pre-indexed protocol detail for one file: `line_locations` (dict) and `line_ranges` (list of tuples) |
| **CommitDiffLine** | One parsed diff line: `kind` (`add`/`delete`/`context`), `content`, `old_line_number`, `new_line_number` |
| **CommitDiffHunk** | One parsed diff hunk: `old_start`, `old_length`, `new_start`, `new_length`, `lines` |
| **CommitDiffFile** | One parsed diff file section: `old_path`, `new_path`, `hunks` |
| **ParsedCommitDiff** | Full parsed result of one commit diff patch containing a list of `CommitDiffFile` |
| **RevisionCommitDiff** | One revision's diff: `revision_id`, `parsed_patch`, optional `base_file_lines_by_old_path`, `parent_revision_ids`, `final_file_lines_by_new_path` |
| **CommitDiffPatchFile** | Metadata for one `*_commitDiff.patch` file on disk: `path`, `revision_id`, `time_seq` |

### Provider Interfaces

| Class | Definition |
|---|---|
| **GenCodeDescProvider** | Abstract base: interface for fetching one revision-level genCodeDesc metadata record |
| **CommitDiffProvider** | Abstract base: interface for fetching one revision's raw commit diff patch |
| **GenCodeDescSetDirProvider** | Concrete: resolves genCodeDesc from a local directory of `*_genCodeDesc.json` files |
| **CommitDiffSetDirProvider** | Concrete: resolves commit diff patches from a local `commitDiffSet/` directory |
| **EmptyGenCodeDescProvider** | Concrete: returns empty metadata (treats all lines as human/unattributed) |
| **EmptyCommitDiffProvider** | Concrete: returns no diff (sentinel for when no `--commitDiffSetDir` is given) |

### Architectural Components

| Component | Definition |
|---|---|
| **RepositoryAnalyzer** | Resolves end snapshot, lists files, runs blame, discovers origin revisions |
| **AggregationEngine** | Joins blame-discovered origins with revision metadata, computes final summary |
| **ResultWriter** | Emits the final protocol-shaped aggregate result |
| **RuntimeLogger** | Structured stderr logger with levels `quiet`/`info`/`debug` and dedup via `warn_once` |

### Exception Hierarchy

| Exception | Definition |
|---|---|
| **AggregateGenCodeDescError** | Base exception class for all domain errors |
| **CommandExecutionError** | External command (git/svn) failure |
| **ProtocolValidationError** | Malformed or mismatched genCodeDesc metadata |
| **UnsupportedConfigurationError** | Requested combination not yet implemented |
| **RepositoryStateError** | Repository state prevents analysis (e.g., no revision found) |
| **InputValidationError** | Invalid CLI input |

### Exit Codes

| Code | Constant | Meaning |
|---|---|---|
| 0 | `EXIT_SUCCESS` | Analysis completed successfully |
| 1 | `EXIT_INPUT_ERROR` | Invalid CLI arguments |
| 2 | `EXIT_REPOSITORY_ERROR` | Repository state prevents analysis |
| 3 | `EXIT_PROTOCOL_ERROR` | Protocol validation failure |
| 4 | `EXIT_TIMEOUT` | Analysis exceeded `--maxRuntime` |

### Constants

| Constant | Definition |
|---|---|
| **COMMAND_TIMEOUT_SECONDS** | Default per-command timeout (30s) |
| **DEFAULT_MAX_RUNTIME_SECONDS** | Default overall analysis timeout (3600s) |
| **MAX_FILE_SIZE_BYTES** | Hard limit for single-file VCS output (100 MB) |

## 7. User Story Index

| ID | Title |
|---|---|
| US-1 | Calculate weighted AI ratio for live changed source code in a requested time window |
| US-2 | Human rewrite removes prior AI attribution |
| US-3 | AI rewrite replaces prior human ownership |
| US-4 | Deleted AI lines must not count |
| US-5 | Rename must preserve attribution lineage |
| US-6 | Calculate AI-added ratio during the requested period (period-added metric) |
| US-7 | Resolve mixed multi-commit history in one requested window |
| US-8 | Merge commit must preserve effective attribution |
| US-9 | Git and SVN must follow the same result contract |
| US-10 | Large repository snapshot must preserve result semantics |
| US-11 | Deep history must preserve latest effective attribution |
| US-12 | Many merged branches in one window must preserve per-line attribution |
| US-13 | Git production-scale local repository gate (Heavy) |
| US-14 | SVN production-scale local repository gate (Heavy) |
| US-15–19 | Algorithm B TDD expansion: single-branch baseline, deletions/rewrites, rename, merge-aware, SVN subset |
| US-20 | Scope B: source code with comments |
| US-21 | Scope C: documentation text lines |
| US-22 | Scope D: all text (source + documentation unified) |
| US-23 | Scope parity matrix verification |
| US-24–26 | Algorithm B scope broadening: B+Scope B, B+Scope C, B+Scope D |
| US-27 | Cross-algorithm × cross-scope parity matrix |
| US-28 | Production readiness audit fixes |
| US-29 | Info-level log must show initial load, per-line state transition, and final summary |
