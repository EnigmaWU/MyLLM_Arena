"""Current CLI slice for AggregateGenCodeDesc.

This implementation is intentionally narrow:
- Git and SVN
- Algorithm A production baseline plus active Algorithm B replay slices
- Scope A, B, C, and D
- JSON output only
- external revision metadata resolved through the current genCodeDesc provider path

The tested story coverage extends beyond the initial Git-only slice. The
runtime now includes fixture-driven and local-Git Algorithm B paths, while
some branch-heavy local-Git merge topologies remain explicitly guarded until
their replay semantics are proven.
"""

import argparse
import json
import re
import signal
import subprocess
import sys
import time as time_mod
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, time, timezone
from pathlib import Path


__version__ = "0.1.0"
PROTOCOL_VERSION = "26.03"

COMMAND_TIMEOUT_SECONDS = 30
DEFAULT_MAX_RUNTIME_SECONDS = 3600
MAX_FILE_SIZE_BYTES = 100 * 1024 * 1024  # 100 MB hard limit for single-file VCS output

_VALID_URL_SCHEMES = re.compile(r"^(https?://|svn://|svn\+ssh://|file://|/)", re.IGNORECASE)


SOURCE_EXTENSIONS = {
    ".c",
    ".cc",
    ".cpp",
    ".cxx",
    ".go",
    ".h",
    ".hpp",
    ".java",
    ".js",
    ".py",
    ".rs",
    ".ts",
}

DOC_EXTENSIONS = {
    ".md",
    ".rst",
    ".txt",
}


@dataclass
class BlameLine:
    revision_id: str
    origin_file: str
    origin_line: int
    final_line: int
    content: str


@dataclass
class IndexedFileDetail:
    line_locations: dict[int, int]
    line_ranges: list[tuple[int, int, int]]


@dataclass
class CommitDiffLine:
    kind: str
    content: str
    old_line_number: int | None
    new_line_number: int | None


@dataclass
class CommitDiffHunk:
    old_start: int
    old_length: int
    new_start: int
    new_length: int
    lines: list[CommitDiffLine]


@dataclass
class CommitDiffFile:
    old_path: str
    new_path: str
    hunks: list[CommitDiffHunk]


@dataclass
class ParsedCommitDiff:
    files: list[CommitDiffFile]


@dataclass
class RevisionCommitDiff:
    revision_id: str
    parsed_patch: ParsedCommitDiff
    base_file_lines_by_old_path: dict[str, list[str]] | None = None
    parent_revision_ids: list[str] | None = None
    final_file_lines_by_new_path: dict[str, list[str]] | None = None


@dataclass
class LineState:
    content: str
    origin_revision_id: str | None
    gen_ratio: int = 0


class AggregateGenCodeDescError(RuntimeError):
    pass


class CommandExecutionError(AggregateGenCodeDescError):
    pass


class ProtocolValidationError(AggregateGenCodeDescError):
    pass


class UnsupportedConfigurationError(AggregateGenCodeDescError):
    pass


class RepositoryStateError(AggregateGenCodeDescError):
    pass


class InputValidationError(AggregateGenCodeDescError):
    pass


def is_local_repository_path(value: str) -> bool:
    return Path(value).is_absolute()


class RuntimeLogger:
    _LEVELS = {"quiet": 0, "info": 1, "debug": 2}

    def __init__(self, level: str):
        self.level = level
        self._level_num = self._LEVELS.get(level, 0)
        self._warnings: list[str] = []
        self._warning_keys: set[str] = set()

    def _emit(self, severity: str, message: str) -> None:
        ts = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        print(f"{ts} [{severity}] [agg] {message}", file=sys.stderr)

    def error(self, message: str) -> None:
        self._emit("ERROR", message)

    def warn(self, message: str) -> None:
        self._warnings.append(message)
        if self._level_num >= 1:
            self._emit("WARN", message)

    def warn_once(self, key: str, message: str) -> None:
        if key in self._warning_keys:
            return
        self._warning_keys.add(key)
        self.warn(message)

    def info(self, message: str) -> None:
        if self._level_num >= 1:
            self._emit("INFO", message)

    def debug(self, message: str) -> None:
        if self._level_num >= 2:
            self._emit("DEBUG", message)

    def warnings(self) -> list[str]:
        return list(self._warnings)


class GenCodeDescProvider(ABC):
    @abstractmethod
    def get_revision_metadata(self, repo_url: str, repo_branch: str, revision_id: str, vcs_type: str) -> dict:
        raise NotImplementedError


class CommitDiffProvider(ABC):
    @abstractmethod
    def get_commit_diff_patch(self, repo_url: str, repo_branch: str, revision_id: str, vcs_type: str) -> str | None:
        raise NotImplementedError


class EmptyGenCodeDescProvider(GenCodeDescProvider):
    def __init__(self, fail_on_missing: bool, warn_on_missing: bool = False, logger: RuntimeLogger | None = None):
        self.fail_on_missing = fail_on_missing
        self.warn_on_missing = warn_on_missing
        self.logger = RuntimeLogger("quiet") if logger is None else logger

    def get_revision_metadata(self, repo_url: str, repo_branch: str, revision_id: str, vcs_type: str) -> dict:
        if self.fail_on_missing:
            raise ProtocolValidationError(f"Missing genCodeDesc provider data for revision {revision_id}")
        if self.warn_on_missing:
            self.logger.warn_once(
                f"missing-protocol:{repo_url}:{repo_branch}:{revision_id}:{vcs_type}",
                f"Missing genCodeDesc provider data for revision {revision_id}; treating affected lines as human/unattributed",
            )
        else:
            self.logger.debug(f"No external genCodeDesc found for revision {revision_id}; treating all lines as human/unattributed")
        return {}


class EmptyCommitDiffProvider(CommitDiffProvider):
    def __init__(self, logger: RuntimeLogger):
        self.logger = logger

    def get_commit_diff_patch(self, repo_url: str, repo_branch: str, revision_id: str, vcs_type: str) -> str | None:
        self.logger.debug(f"No external commit diff provider configured for revision {revision_id}")
        return None


class GenCodeDescSetDirProvider(GenCodeDescProvider):
    def __init__(self, base_dir: Path, fail_on_missing: bool, warn_on_missing: bool = False, logger: RuntimeLogger | None = None):
        self.base_dir = base_dir
        self.fail_on_missing = fail_on_missing
        self.warn_on_missing = warn_on_missing
        self.logger = RuntimeLogger("quiet") if logger is None else logger

    def _find_protocol_path(self, revision_id: str) -> Path | None:
        direct_path = self.base_dir / f"{revision_id}_genCodeDesc.json"
        if direct_path.exists():
            return direct_path

        for candidate_path in sorted(self.base_dir.glob("*_genCodeDesc.json")):
            try:
                candidate_protocol = load_json_document(candidate_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError, UnicodeDecodeError):
                continue
            candidate_revision_id = candidate_protocol.get("REPOSITORY", {}).get("revisionId")
            if candidate_revision_id == revision_id:
                return candidate_path

        return None

    def get_revision_metadata(self, repo_url: str, repo_branch: str, revision_id: str, vcs_type: str) -> dict:
        protocol_path = self._find_protocol_path(revision_id)
        if protocol_path is None:
            if self.fail_on_missing:
                raise ProtocolValidationError(
                    f"Protocol file not found for revision {revision_id} in {self.base_dir}"
                )
            if self.warn_on_missing:
                self.logger.warn_once(
                    f"missing-protocol:{repo_url}:{repo_branch}:{revision_id}:{vcs_type}",
                    f"Protocol file not found for revision {revision_id} in {self.base_dir}; treating affected lines as human/unattributed",
                )
            else:
                self.logger.debug(
                    f"No genCodeDesc file found for revision {revision_id} in {self.base_dir}; treating revision as human/unattributed"
                )
            return {}
        protocol = load_json_document(protocol_path.read_text(encoding="utf-8"))
        repository = protocol.get("REPOSITORY", {})
        self.logger.debug(f"Loaded genCodeDesc for revision {revision_id} from {protocol_path}")

        # WHY: genCodeDesc is external metadata, not repository content. We
        # validate identity fields here so the analyzer cannot silently join a
        # real repository revision with the wrong external record.
        protocol_vcs_type = repository.get("vcsType")
        if protocol_vcs_type and protocol_vcs_type != vcs_type:
            raise ProtocolValidationError(
                f"Metadata vcsType mismatch for revision {revision_id}: expected {vcs_type}, got {protocol_vcs_type}"
            )

        protocol_repo_url = repository.get("repoURL")
        if protocol_repo_url and protocol_repo_url != repo_url:
            raise ProtocolValidationError(
                f"Metadata repoURL mismatch for revision {revision_id}: expected {repo_url}, got {protocol_repo_url}"
            )

        protocol_repo_branch = repository.get("repoBranch")
        # WHY: repoBranch describes where that metadata record was produced, but
        # merged revisions can legitimately originate from a different branch
        # than the query branch while still being part of the end revision's
        # reachable history. Branch equality is therefore not a stable
        # revision-identity check for revision-scoped metadata.
        if protocol_repo_branch and protocol_repo_branch != repo_branch:
            self.logger.debug(
                f"Metadata repoBranch differs for revision {revision_id}: query={repo_branch} metadata={protocol_repo_branch}; accepting revision-scoped metadata"
            )

        protocol_revision_id = repository.get("revisionId")
        if protocol_revision_id and protocol_revision_id != revision_id:
            raise ProtocolValidationError(
                f"Metadata revisionId mismatch for revision {revision_id}: expected {revision_id}, got {protocol_revision_id}"
            )

        return protocol


class CommitDiffSetDirProvider(CommitDiffProvider):
    def __init__(self, base_dir: Path, logger: RuntimeLogger):
        self.base_dir = base_dir
        self.logger = logger

    def get_commit_diff_patch(self, repo_url: str, repo_branch: str, revision_id: str, vcs_type: str) -> str:
        patch_path = resolve_commit_diff_patch_path(self.base_dir, revision_id)
        if not patch_path.exists():
            raise ProtocolValidationError(f"Commit diff patch file not found: {patch_path}")

        patch_text = patch_path.read_text(encoding="utf-8")
        if not patch_text.strip():
            raise ProtocolValidationError(f"Commit diff patch file is empty: {patch_path}")

        self.logger.debug(f"Loaded commit diff patch for revision {revision_id} from {patch_path}")
        return patch_text


_HUNK_HEADER_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
_COMMIT_DIFF_FILE_RE = re.compile(r"^(?:(?P<time_seq>\d+)_)?(?P<revision_id>.+)_commitDiff\.patch$")


@dataclass(frozen=True)
class CommitDiffPatchFile:
    path: Path
    revision_id: str
    time_seq: int | None


def parse_commit_diff_patch_filename(file_name: str) -> tuple[int | None, str] | None:
    match = _COMMIT_DIFF_FILE_RE.match(file_name)
    if match is None:
        return None

    time_seq = match.group("time_seq")
    revision_id = match.group("revision_id")
    return (int(time_seq) if time_seq is not None else None, revision_id)


def list_commit_diff_patch_files(commit_diff_set_dir: Path, *, fail_on_empty: bool = True) -> list[CommitDiffPatchFile]:
    parsed_patch_files: list[CommitDiffPatchFile] = []
    has_time_seq_name = False
    has_legacy_name = False

    for patch_path in commit_diff_set_dir.glob("*_commitDiff.patch"):
        parsed_name = parse_commit_diff_patch_filename(patch_path.name)
        if parsed_name is None:
            continue
        time_seq, revision_id = parsed_name
        if time_seq is None:
            has_legacy_name = True
        else:
            has_time_seq_name = True
        parsed_patch_files.append(
            CommitDiffPatchFile(path=patch_path, revision_id=revision_id, time_seq=time_seq)
        )

    if not parsed_patch_files and fail_on_empty:
        raise ProtocolValidationError(f"No commit diff patch files found in {commit_diff_set_dir}")

    if has_time_seq_name and has_legacy_name:
        raise ProtocolValidationError(
            "Mixed commit diff patch naming styles are not supported in one commitDiffSetDir; "
            "use either all <timeSeq>_<revisionId>_commitDiff.patch files or all <revisionId>_commitDiff.patch files"
        )

    return parsed_patch_files


def resolve_commit_diff_patch_path(commit_diff_set_dir: Path, revision_id: str) -> Path:
    matches: list[tuple[int, Path]] = []
    for patch_file in list_commit_diff_patch_files(commit_diff_set_dir, fail_on_empty=False):
        if patch_file.revision_id != revision_id:
            continue
        matches.append((patch_file.time_seq if patch_file.time_seq is not None else sys.maxsize, patch_file.path))

    if not matches:
        return commit_diff_set_dir / f"{revision_id}_commitDiff.patch"

    matches.sort(key=lambda item: (item[0], item[1].name.lower()))
    if len(matches) > 1:
        raise ProtocolValidationError(
            f"Multiple commit diff patch files matched revision {revision_id} in {commit_diff_set_dir}"
        )
    return matches[0][1]


def parse_commit_diff_patch(patch_text: str) -> ParsedCommitDiff:
    lines = patch_text.splitlines()
    parsed_files: list[CommitDiffFile] = []
    current_file: CommitDiffFile | None = None
    current_hunk: CommitDiffHunk | None = None
    old_line_cursor: int | None = None
    new_line_cursor: int | None = None

    for raw_line in lines:
        if raw_line.startswith("diff --git "):
            if current_file is not None:
                parsed_files.append(current_file)
            header_parts = raw_line.split()
            old_path = ""
            new_path = ""
            if len(header_parts) >= 4:
                old_path = header_parts[2].removeprefix("a/")
                new_path = header_parts[3].removeprefix("b/")
            current_file = CommitDiffFile(old_path=old_path, new_path=new_path, hunks=[])
            current_hunk = None
            old_line_cursor = None
            new_line_cursor = None
            continue

        if current_file is None:
            if not raw_line.strip():
                continue
            raise ProtocolValidationError("Commit diff patch content must start with a diff --git file header")

        if raw_line.startswith("--- "):
            current_file.old_path = raw_line.removeprefix("--- ").removeprefix("a/")
            continue

        if raw_line.startswith("+++ "):
            current_file.new_path = raw_line.removeprefix("+++ ").removeprefix("b/")
            continue

        if raw_line.startswith("rename from "):
            current_file.old_path = raw_line.removeprefix("rename from ")
            continue

        if raw_line.startswith("rename to "):
            current_file.new_path = raw_line.removeprefix("rename to ")
            continue

        if raw_line.startswith("@@ "):
            hunk_match = _HUNK_HEADER_RE.match(raw_line)
            if hunk_match is None:
                raise ProtocolValidationError(f"Malformed commit diff hunk header: {raw_line}")
            old_start = int(hunk_match.group(1))
            old_length = int(hunk_match.group(2) or "1")
            new_start = int(hunk_match.group(3))
            new_length = int(hunk_match.group(4) or "1")
            current_hunk = CommitDiffHunk(
                old_start=old_start,
                old_length=old_length,
                new_start=new_start,
                new_length=new_length,
                lines=[],
            )
            current_file.hunks.append(current_hunk)
            old_line_cursor = old_start
            new_line_cursor = new_start
            continue

        if current_hunk is None:
            continue

        if raw_line.startswith("\\ No newline at end of file"):
            continue

        if raw_line.startswith("+"):
            current_hunk.lines.append(
                CommitDiffLine(
                    kind="add",
                    content=raw_line[1:],
                    old_line_number=None,
                    new_line_number=new_line_cursor,
                )
            )
            if new_line_cursor is None:
                raise ProtocolValidationError("Commit diff parser lost new-file line cursor state")
            new_line_cursor += 1
            continue

        if raw_line.startswith("-"):
            current_hunk.lines.append(
                CommitDiffLine(
                    kind="delete",
                    content=raw_line[1:],
                    old_line_number=old_line_cursor,
                    new_line_number=None,
                )
            )
            if old_line_cursor is None:
                raise ProtocolValidationError("Commit diff parser lost old-file line cursor state")
            old_line_cursor += 1
            continue

        if raw_line.startswith(" "):
            current_hunk.lines.append(
                CommitDiffLine(
                    kind="context",
                    content=raw_line[1:],
                    old_line_number=old_line_cursor,
                    new_line_number=new_line_cursor,
                )
            )
            if old_line_cursor is None or new_line_cursor is None:
                raise ProtocolValidationError("Commit diff parser lost line cursor state")
            old_line_cursor += 1
            new_line_cursor += 1
            continue

        raise ProtocolValidationError(f"Unsupported commit diff patch line: {raw_line}")

    if current_file is not None:
        parsed_files.append(current_file)

    if not parsed_files:
        raise ProtocolValidationError("Commit diff patch did not contain any diff --git file sections")

    for parsed_file in parsed_files:
        if not parsed_file.old_path or not parsed_file.new_path:
            raise ProtocolValidationError("Commit diff patch file section is missing ---/+++ path headers")

    return ParsedCommitDiff(files=parsed_files)


def load_commit_diff_sequence(
    provider: CommitDiffProvider,
    repo_url: str,
    repo_branch: str,
    revision_ids: list[str],
    vcs_type: str,
) -> list[RevisionCommitDiff]:
    loaded_sequence: list[RevisionCommitDiff] = []
    for revision_id in revision_ids:
        patch_text = provider.get_commit_diff_patch(repo_url, repo_branch, revision_id, vcs_type)
        if patch_text is None:
            raise ProtocolValidationError(f"Commit diff provider returned no patch for revision {revision_id}")
        loaded_sequence.append(
            RevisionCommitDiff(
                revision_id=revision_id,
                parsed_patch=parse_commit_diff_patch(patch_text),
            )
        )
    return loaded_sequence


def build_result_document(
    args: argparse.Namespace,
    summary: dict[str, int],
    revision_id: str,
    logger: RuntimeLogger,
    repo_url_override: str | None = None,
) -> dict:
    result = {
        "protocolName": "generatedTextDesc",
        "protocolVersion": PROTOCOL_VERSION,
        "SUMMARY": summary,
        "REPOSITORY": {
            "vcsType": args.vcsType,
            "repoURL": args.repoURL if repo_url_override is None else repo_url_override,
            "repoBranch": args.repoBranch,
            "revisionId": revision_id,
        },
    }
    warnings = logger.warnings()
    if warnings:
        result["WARNINGS"] = warnings
    return result


def resolve_algorithm_b_offline_revision_ids(args: argparse.Namespace) -> list[str]:
    query_document = load_algorithm_b_query(args)
    if query_document is not None:
        included_revision_ids = query_document.get("includedRevisionIds")
        if included_revision_ids is not None:
            if not isinstance(included_revision_ids, list) or not all(isinstance(value, str) and value for value in included_revision_ids):
                raise ProtocolValidationError("query.json includedRevisionIds must be a non-empty list of revision-id strings")
            return included_revision_ids

    return list_commit_diff_revision_ids(Path(args.commitDiffSetDir))


def resolve_added_line_gen_ratios(
    commit_diff_file: CommitDiffFile,
    hunk: CommitDiffHunk,
    protocol_index: dict[str, IndexedFileDetail] | None,
) -> list[int]:
    added_lines = [line for line in hunk.lines if line.kind == "add"]
    if not added_lines:
        return []
    if protocol_index is None:
        return [0 for _ in added_lines]

    direct_ratios = [
        line_ratio(protocol_index, commit_diff_file.new_path, added_line.new_line_number or 0)
        for added_line in added_lines
    ]
    indexed_file = protocol_index.get(commit_diff_file.new_path)
    if indexed_file is None or indexed_file.line_ranges:
        return direct_ratios

    if any(direct_ratios) and sum(1 for ratio in direct_ratios if ratio > 0) == len(indexed_file.line_locations):
        return direct_ratios

    if len(indexed_file.line_locations) == len(added_lines) and any(direct_ratios):
        return [ratio for _, ratio in sorted(indexed_file.line_locations.items())]

    return direct_ratios


def apply_commit_diff_file_to_line_states(
    current_lines: list[LineState],
    commit_diff_file: CommitDiffFile,
    revision_id: str,
    protocol_index: dict[str, IndexedFileDetail] | None = None,
) -> list[LineState]:
    updated_lines = list(current_lines)
    line_offset = 0

    for hunk in commit_diff_file.hunks:
        insertion_index = (0 if hunk.old_start == 0 else hunk.old_start - 1) + line_offset
        if insertion_index < 0 or insertion_index > len(updated_lines):
            raise ProtocolValidationError(
                f"Commit diff hunk starts outside current file bounds for {commit_diff_file.new_path}: {hunk.old_start}"
            )

        scan_index = insertion_index
        added_line_gen_ratios = resolve_added_line_gen_ratios(commit_diff_file, hunk, protocol_index)
        added_line_index = 0
        for diff_line in hunk.lines:
            if diff_line.kind == "context":
                if scan_index >= len(updated_lines) or updated_lines[scan_index].content != diff_line.content:
                    raise ProtocolValidationError(
                        f"Commit diff context mismatch for {commit_diff_file.new_path} at line {diff_line.old_line_number}"
                    )
                scan_index += 1
                continue

            if diff_line.kind == "delete":
                if scan_index >= len(updated_lines) or updated_lines[scan_index].content != diff_line.content:
                    raise ProtocolValidationError(
                        f"Commit diff delete mismatch for {commit_diff_file.new_path} at line {diff_line.old_line_number}"
                    )
                del updated_lines[scan_index]
                line_offset -= 1
                continue

            if diff_line.kind == "add":
                added_gen_ratio = added_line_gen_ratios[added_line_index] if added_line_index < len(added_line_gen_ratios) else 0
                updated_lines.insert(
                    scan_index,
                    LineState(content=diff_line.content, origin_revision_id=revision_id, gen_ratio=added_gen_ratio),
                )
                scan_index += 1
                line_offset += 1
                added_line_index += 1
                continue

            raise ProtocolValidationError(f"Unsupported commit diff line kind: {diff_line.kind}")

    return updated_lines


def apply_commit_diff_file_to_lines(current_lines: list[str], commit_diff_file: CommitDiffFile) -> list[str]:
    stateful_lines = [LineState(content=line, origin_revision_id=None, gen_ratio=0) for line in current_lines]
    replayed_lines = apply_commit_diff_file_to_line_states(stateful_lines, commit_diff_file, revision_id="<added>")
    return [line_state.content for line_state in replayed_lines]


def summarize_period_added_line_states(
    line_states: list[LineState],
    included_revision_ids: list[str],
    scope: str = "A",
) -> dict[str, int]:
    return summarize_live_changed_line_states_by_revision_ids(line_states, included_revision_ids, scope)


def _summary_field_names(scope: str) -> tuple[str, str, str]:
    if scope == "C":
        return "totalDocLines", "fullGeneratedDocLines", "partialGeneratedDocLines"
    return "totalCodeLines", "fullGeneratedCodeLines", "partialGeneratedCodeLines"


def summarize_live_changed_line_states_by_revision_ids(
    line_states: list[LineState],
    included_revision_ids: list[str],
    scope: str = "A",
) -> dict[str, int]:
    included_revision_id_set = set(included_revision_ids)
    total_code_lines = 0
    full_generated_code_lines = 0
    partial_generated_code_lines = 0

    for line_state in line_states:
        if line_state.origin_revision_id not in included_revision_id_set:
            continue
        if not is_code_line(line_state.content, scope):
            continue

        total_code_lines += 1
        if line_state.gen_ratio == 100:
            full_generated_code_lines += 1
        elif line_state.gen_ratio > 0:
            partial_generated_code_lines += 1

    total_key, full_key, partial_key = _summary_field_names(scope)
    return {
        total_key: total_code_lines,
        full_key: full_generated_code_lines,
        partial_key: partial_generated_code_lines,
    }


def list_commit_diff_revision_ids(commit_diff_set_dir: Path) -> list[str]:
    parsed_patch_files: list[tuple[tuple[int, list[object]], str]] = []
    for patch_file in list_commit_diff_patch_files(commit_diff_set_dir):
        time_seq = patch_file.time_seq
        revision_id = patch_file.revision_id
        sort_key = (0, [time_seq]) if time_seq is not None else (
            1,
            [int(part) if part.isdigit() else part.lower() for part in re.split(r"(\d+)", patch_file.path.name)],
        )
        parsed_patch_files.append((sort_key, revision_id))

    parsed_patch_files.sort(key=lambda item: item[0])
    revision_ids = [revision_id for _sort_key, revision_id in parsed_patch_files]
    return revision_ids


def is_source_file_path(path_value: str) -> bool:
    if not path_value or path_value == "/dev/null":
        return False
    return Path(path_value).suffix in SOURCE_EXTENSIONS


def is_doc_file_path(path_value: str) -> bool:
    if not path_value or path_value == "/dev/null":
        return False
    return Path(path_value).suffix in DOC_EXTENSIONS


def is_included_file_path(path_value: str, scope: str = "A") -> bool:
    if scope == "C":
        return is_doc_file_path(path_value)
    if scope == "D":
        return is_source_file_path(path_value) or is_doc_file_path(path_value)
    return is_source_file_path(path_value)


def list_git_source_paths_for_revision(repo_dir: Path, revision_id: str, scope: str = "A") -> list[str]:
    parent_revision = resolve_parent_revision("git", repo_dir, "", "", revision_id)
    if parent_revision is None:
        output = run_git(repo_dir, ["show", "--format=", "--name-status", "--find-renames", "--root", revision_id])
    else:
        output = run_git(repo_dir, ["diff", "--name-status", "--find-renames", parent_revision, revision_id])

    source_paths: list[str] = []
    for raw_line in output.splitlines():
        if not raw_line:
            continue
        parts = raw_line.split("\t")
        status = parts[0]
        candidate_paths: list[str]
        if status.startswith(("R", "C")) and len(parts) >= 3:
            candidate_paths = [parts[1], parts[2]]
        elif len(parts) >= 2:
            candidate_paths = [parts[1]]
        else:
            continue

        for relative_path in candidate_paths:
            if is_included_file_path(relative_path, scope) and relative_path not in source_paths:
                source_paths.append(relative_path)

    return source_paths


def build_git_source_patch_for_revision(repo_dir: Path, revision_id: str, source_paths: list[str]) -> str:
    if not source_paths:
        return ""

    parent_revision = resolve_parent_revision("git", repo_dir, "", "", revision_id)
    if parent_revision is None:
        return run_git(
            repo_dir,
            ["show", "--format=", "--find-renames", "--root", revision_id, "--", *source_paths],
        )

    return run_git(
        repo_dir,
        ["diff", "--find-renames", parent_revision, revision_id, "--", *source_paths],
    )


def resolve_local_git_repository_dir(args: argparse.Namespace) -> Path:
    candidate = Path(args.workingDir or args.repoURL)
    if not candidate.is_dir():
        raise UnsupportedConfigurationError(
            "Algorithm B local git replay requires a local repository via --workingDir or an absolute --repoURL when --commitDiffSetDir is not provided"
        )

    probe = run_command(["git", "rev-parse", "--is-inside-work-tree"], cwd=candidate, check=False)
    if probe.returncode != 0 or probe.stdout.strip() != "true":
        raise UnsupportedConfigurationError(
            "Algorithm B local git replay requires --workingDir or --repoURL to point at a git working tree"
        )

    return candidate


def resolve_algorithm_b_git_end_revision_id(args: argparse.Namespace, repo_dir: Path) -> str:
    query_document = load_algorithm_b_query(args)
    if query_document is not None:
        end_revision_id = query_document.get("endRevisionId")
        if end_revision_id is not None:
            if not isinstance(end_revision_id, str) or not end_revision_id:
                raise ProtocolValidationError("query.json endRevisionId must be a non-empty string when provided")
            return end_revision_id

    return resolve_end_revision(repo_dir, args.repoBranch, args.endTime)


def resolve_algorithm_b_git_revision_ids(args: argparse.Namespace, repo_dir: Path) -> tuple[list[str], str]:
    query_document = load_algorithm_b_query(args)
    if query_document is not None:
        included_revision_ids = query_document.get("includedRevisionIds")
        if included_revision_ids is not None:
            if not isinstance(included_revision_ids, list) or not all(isinstance(value, str) and value for value in included_revision_ids):
                raise ProtocolValidationError("query.json includedRevisionIds must be a non-empty list of revision-id strings")
            end_revision_id = resolve_algorithm_b_git_end_revision_id(args, repo_dir)
            return included_revision_ids, end_revision_id

    end_revision_id = resolve_algorithm_b_git_end_revision_id(args, repo_dir)
    revision_output = run_git(
        repo_dir,
        [
            "rev-list",
            "--reverse",
            "--topo-order",
            f"--since={parse_day_start(args.startTime).isoformat()}",
            f"--until={parse_day_end(args.endTime).isoformat()}",
            end_revision_id,
        ],
    )
    revision_ids = [revision_id for revision_id in revision_output.splitlines() if revision_id]
    return revision_ids, end_revision_id


def load_git_commit_diff_sequence_from_repository(repo_dir: Path, revision_ids: list[str], scope: str = "A") -> list[RevisionCommitDiff]:
    loaded_sequence: list[RevisionCommitDiff] = []

    for revision_id in revision_ids:
        parent_revision = resolve_parent_revision("git", repo_dir, "", "", revision_id)
        parent_revision_ids = list_git_parent_revisions(repo_dir, revision_id)
        source_paths = list_git_source_paths_for_revision(repo_dir, revision_id, scope)
        if not source_paths:
            continue

        patch_text = build_git_source_patch_for_revision(repo_dir, revision_id, source_paths)
        if not patch_text.strip():
            continue

        parsed_patch = parse_commit_diff_patch(patch_text)
        base_file_lines_by_old_path: dict[str, list[str]] = {}
        final_file_lines_by_new_path: dict[str, list[str]] = {}
        if parent_revision is not None:
            for commit_diff_file in parsed_patch.files:
                old_path = commit_diff_file.old_path
                if not is_included_file_path(old_path, scope) or old_path in base_file_lines_by_old_path:
                    continue
                base_file_lines = read_git_file_lines_at_revision(repo_dir, parent_revision, old_path)
                if base_file_lines is not None:
                    base_file_lines_by_old_path[old_path] = base_file_lines
        for commit_diff_file in parsed_patch.files:
            new_path = commit_diff_file.new_path
            if not is_included_file_path(new_path, scope) or new_path in final_file_lines_by_new_path:
                continue
            final_file_lines = read_git_file_lines_at_revision(repo_dir, revision_id, new_path)
            if final_file_lines is not None:
                final_file_lines_by_new_path[new_path] = final_file_lines

        loaded_sequence.append(
            RevisionCommitDiff(
                revision_id=revision_id,
                parsed_patch=parsed_patch,
                base_file_lines_by_old_path=base_file_lines_by_old_path or None,
                parent_revision_ids=parent_revision_ids or None,
                final_file_lines_by_new_path=final_file_lines_by_new_path or None,
            )
        )

    if not loaded_sequence:
        raise ProtocolValidationError("Algorithm B local git replay did not find any source-file commit diffs in the requested window")

    return loaded_sequence


def collect_git_revision_commit_times(repo_dir: Path, revision_ids: list[str]) -> dict[str, datetime]:
    return {
        revision_id: parse_git_timestamp(run_git(repo_dir, ["show", "-s", "--format=%cI", revision_id]))
        for revision_id in revision_ids
    }


def list_git_parent_revisions(repo_dir: Path, revision_id: str) -> list[str]:
    output = run_git(repo_dir, ["show", "-s", "--format=%P", revision_id])
    return [value for value in output.split() if value]


def read_git_file_lines_at_revision(repo_dir: Path, revision_id: str, relative_path: str) -> list[str] | None:
    if not revision_id or not relative_path or relative_path == "/dev/null":
        return None

    result = run_command(["git", "show", f"{revision_id}:{relative_path}"], cwd=repo_dir, check=False)
    if result.returncode != 0:
        return None
    if len(result.stdout) > MAX_FILE_SIZE_BYTES:
        raise RepositoryStateError(
            f"File {relative_path} at {revision_id} exceeds {MAX_FILE_SIZE_BYTES} byte limit "
            f"({len(result.stdout)} bytes) — possible binary or generated file"
        )
    return result.stdout.splitlines()


def reconstruct_base_line_states_from_lines(file_lines: list[str]) -> list[LineState]:
    return [LineState(content=line, origin_revision_id=None, gen_ratio=0) for line in file_lines]


def find_next_matching_line_state(line_states: list[LineState], content: str, start_index: int) -> int | None:
    for index in range(start_index, len(line_states)):
        if line_states[index].content == content:
            return index
    return None


def merge_commit_file_line_states(
    first_parent_lines: list[LineState],
    other_parent_lines: list[list[LineState]],
    final_file_lines: list[str],
    revision_id: str,
    target_path: str,
    protocol_index: dict[str, IndexedFileDetail] | None = None,
) -> list[LineState]:
    merged_lines: list[LineState] = []
    first_parent_cursor = 0
    other_parent_cursors = [0 for _ in other_parent_lines]

    for final_line_number, content in enumerate(final_file_lines, start=1):
        first_parent_match = find_next_matching_line_state(first_parent_lines, content, first_parent_cursor)
        other_parent_matches: list[tuple[int, int]] = []
        for parent_index, parent_lines in enumerate(other_parent_lines):
            match_index = find_next_matching_line_state(parent_lines, content, other_parent_cursors[parent_index])
            if match_index is not None:
                other_parent_matches.append((parent_index, match_index))

        if first_parent_match is not None and (
            not other_parent_matches or first_parent_match <= min(match_index for _parent_index, match_index in other_parent_matches)
        ):
            merged_lines.append(first_parent_lines[first_parent_match])
            first_parent_cursor = first_parent_match + 1
            continue

        if other_parent_matches:
            parent_index, match_index = min(other_parent_matches, key=lambda item: item[1])
            merged_lines.append(other_parent_lines[parent_index][match_index])
            other_parent_cursors[parent_index] = match_index + 1
            continue

        merged_lines.append(
            LineState(
                content=content,
                origin_revision_id=revision_id,
                gen_ratio=0 if protocol_index is None else line_ratio(protocol_index, target_path, final_line_number),
            )
        )

    return merged_lines


def reconstruct_base_line_states_from_patch(commit_diff_file: CommitDiffFile) -> list[LineState]:
    if len(commit_diff_file.hunks) != 1:
        raise UnsupportedConfigurationError(
            "Current Algorithm B offline slice only supports a single hunk in the first patch when reconstructing the base file"
        )

    first_hunk = commit_diff_file.hunks[0]
    if first_hunk.old_start not in {0, 1}:
        raise UnsupportedConfigurationError(
            "Current Algorithm B offline slice only supports first-patch base reconstruction starting at line 1 or from an empty file"
        )

    base_lines: list[LineState] = []
    for diff_line in first_hunk.lines:
        if diff_line.kind in {"context", "delete"}:
            base_lines.append(LineState(content=diff_line.content, origin_revision_id=None, gen_ratio=0))
    return base_lines


def reconstruct_final_line_states_from_commit_diff_sequence(
    commit_diff_sequence: list[RevisionCommitDiff],
    protocol_indexes: dict[str, dict[str, IndexedFileDetail]] | None = None,
) -> tuple[str, list[LineState]]:
    if len(commit_diff_sequence[0].parsed_patch.files) != 1:
        raise UnsupportedConfigurationError(
            "Current Algorithm B offline slice only supports a single file in the first patch sequence"
        )

    file_states = reconstruct_final_file_states_by_path_from_commit_diff_sequence(
        commit_diff_sequence,
        protocol_indexes,
    )
    if len(file_states) != 1:
        raise UnsupportedConfigurationError(
            "Current Algorithm B offline slice only supports a single replayed file path across the diff sequence"
        )

    target_file, current_lines = next(iter(file_states.items()))
    return target_file, current_lines


def reconstruct_final_file_states_by_path_from_commit_diff_sequence(
    commit_diff_sequence: list[RevisionCommitDiff],
    protocol_indexes: dict[str, dict[str, IndexedFileDetail]] | None = None,
    scope: str = "A",
) -> dict[str, list[LineState]]:
    if not commit_diff_sequence:
        raise ProtocolValidationError("Algorithm B replay requires at least one replayable commit diff patch")

    file_states: dict[str, list[LineState]] = {}
    revision_file_states: dict[str, dict[str, list[LineState]]] = {}

    for revision_diff in commit_diff_sequence:
        protocol_index = None if protocol_indexes is None else protocol_indexes.get(revision_diff.revision_id)
        parent_revision_ids = revision_diff.parent_revision_ids or []
        if parent_revision_ids:
            file_states = {
                path: list(line_states)
                for path, line_states in revision_file_states.get(parent_revision_ids[0], {}).items()
            }

        for commit_diff_file in revision_diff.parsed_patch.files:
            if not is_included_file_path(commit_diff_file.old_path, scope) and not is_included_file_path(commit_diff_file.new_path, scope):
                continue

            if len(parent_revision_ids) > 1 and revision_diff.final_file_lines_by_new_path is not None:
                final_file_lines = revision_diff.final_file_lines_by_new_path.get(commit_diff_file.new_path)
                if final_file_lines is not None:
                    first_parent_lines = revision_file_states.get(parent_revision_ids[0], {}).get(commit_diff_file.old_path)
                    if first_parent_lines is None:
                        first_parent_lines = revision_file_states.get(parent_revision_ids[0], {}).get(commit_diff_file.new_path, [])
                    other_parent_line_states: list[list[LineState]] = []
                    for parent_revision_id in parent_revision_ids[1:]:
                        parent_file_states = revision_file_states.get(parent_revision_id, {})
                        side_lines = parent_file_states.get(commit_diff_file.new_path)
                        if side_lines is None:
                            side_lines = parent_file_states.get(commit_diff_file.old_path)
                        if side_lines is not None:
                            other_parent_line_states.append(side_lines)
                    updated_lines = merge_commit_file_line_states(
                        first_parent_lines or [],
                        other_parent_line_states,
                        final_file_lines,
                        revision_diff.revision_id,
                        commit_diff_file.new_path,
                        protocol_index,
                    )
                    file_states.pop(commit_diff_file.old_path, None)
                    file_states[commit_diff_file.new_path] = updated_lines
                    continue

            current_lines = file_states.pop(commit_diff_file.old_path, None)
            if current_lines is None:
                current_lines = file_states.pop(commit_diff_file.new_path, None)
            if current_lines is None:
                base_file_lines_by_old_path = revision_diff.base_file_lines_by_old_path or {}
                base_file_lines = base_file_lines_by_old_path.get(commit_diff_file.old_path)
                if base_file_lines is not None:
                    current_lines = reconstruct_base_line_states_from_lines(base_file_lines)
                else:
                    current_lines = reconstruct_base_line_states_from_patch(commit_diff_file)

            updated_lines = apply_commit_diff_file_to_line_states(
                current_lines,
                commit_diff_file,
                revision_diff.revision_id,
                protocol_index,
            )
            file_states[commit_diff_file.new_path] = updated_lines

        revision_file_states[revision_diff.revision_id] = {
            path: list(line_states) for path, line_states in file_states.items()
        }

    if not file_states:
        raise ProtocolValidationError("Algorithm B replay did not produce any final file state")

    return file_states


def summarize_live_changed_file_states_by_revision_ids(
    file_states_by_path: dict[str, list[LineState]],
    included_revision_ids: list[str],
    scope: str = "A",
) -> dict[str, int]:
    total_key, full_key, partial_key = _summary_field_names(scope)
    total_code_lines = 0
    full_generated_code_lines = 0
    partial_generated_code_lines = 0

    for line_states in file_states_by_path.values():
        file_summary = summarize_live_changed_line_states_by_revision_ids(line_states, included_revision_ids, scope)
        total_code_lines += file_summary[total_key]
        full_generated_code_lines += file_summary[full_key]
        partial_generated_code_lines += file_summary[partial_key]

    return {
        total_key: total_code_lines,
        full_key: full_generated_code_lines,
        partial_key: partial_generated_code_lines,
    }


def summarize_live_snapshot_line_states(
    line_states: list[LineState],
    revision_commit_times: dict[str, datetime],
    start_bound: datetime,
    end_bound: datetime,
    scope: str = "A",
) -> dict[str, int]:
    total_code_lines = 0
    full_generated_code_lines = 0
    partial_generated_code_lines = 0

    for line_state in line_states:
        if not is_code_line(line_state.content, scope):
            continue

        origin_revision_id = line_state.origin_revision_id
        if origin_revision_id is None:
            continue

        commit_time = revision_commit_times.get(origin_revision_id)
        if commit_time is None:
            raise ProtocolValidationError(
                f"Missing commit time for replayed live-snapshot revision {origin_revision_id}"
            )
        if not (start_bound <= commit_time <= end_bound):
            continue

        total_code_lines += 1
        if line_state.gen_ratio == 100:
            full_generated_code_lines += 1
        elif line_state.gen_ratio > 0:
            partial_generated_code_lines += 1

    total_key, full_key, partial_key = _summary_field_names(scope)
    return {
        total_key: total_code_lines,
        full_key: full_generated_code_lines,
        partial_key: partial_generated_code_lines,
    }


def summarize_live_snapshot_file_states(
    file_states_by_path: dict[str, list[LineState]],
    revision_commit_times: dict[str, datetime],
    start_bound: datetime,
    end_bound: datetime,
    scope: str = "A",
) -> dict[str, int]:
    total_key, full_key, partial_key = _summary_field_names(scope)
    total_code_lines = 0
    full_generated_code_lines = 0
    partial_generated_code_lines = 0

    for line_states in file_states_by_path.values():
        file_summary = summarize_live_snapshot_line_states(
            line_states,
            revision_commit_times,
            start_bound,
            end_bound,
            scope,
        )
        total_code_lines += file_summary[total_key]
        full_generated_code_lines += file_summary[full_key]
        partial_generated_code_lines += file_summary[partial_key]

    return {
        total_key: total_code_lines,
        full_key: full_generated_code_lines,
        partial_key: partial_generated_code_lines,
    }


def _build_protocol_index_for_scope(protocol: dict, scope: str) -> dict[str, "IndexedFileDetail"]:
    if scope == "C":
        return build_doc_protocol_index(protocol)
    if scope == "D":
        return build_combined_protocol_index(protocol)
    return build_protocol_index(protocol)


def _log_algorithm_b_summary(logger: "RuntimeLogger", label: str, summary: dict, end_revision_id: str, scope: str) -> None:
    if scope == "C":
        logger.info(
            f"Finished Algorithm B {label} analysis with totalDocLines={summary['totalDocLines']} "
            f"fullGeneratedDocLines={summary['fullGeneratedDocLines']} "
            f"partialGeneratedDocLines={summary['partialGeneratedDocLines']} endRevision={end_revision_id}"
        )
    else:
        logger.info(
            f"Finished Algorithm B {label} analysis with totalCodeLines={summary['totalCodeLines']} "
            f"fullGeneratedCodeLines={summary['fullGeneratedCodeLines']} "
            f"partialGeneratedCodeLines={summary['partialGeneratedCodeLines']} endRevision={end_revision_id}"
        )


def build_result_algorithm_b_offline(args: argparse.Namespace, logger: RuntimeLogger) -> dict:
    if not args.commitDiffSetDir:
        raise UnsupportedConfigurationError("Current Algorithm B offline slice requires --commitDiffSetDir")

    provider = build_gen_code_desc_provider(args, logger)
    diff_provider = build_commit_diff_provider(args, logger)
    revision_ids = resolve_algorithm_b_offline_revision_ids(args)
    commit_diff_sequence = load_commit_diff_sequence(
        diff_provider,
        args.repoURL,
        args.repoBranch,
        revision_ids,
        args.vcsType,
    )
    if not commit_diff_sequence:
        raise ProtocolValidationError("Algorithm B offline slice requires at least one replayable commit diff patch")

    protocol_indexes = {
        revision_diff.revision_id: _build_protocol_index_for_scope(
            provider.get_revision_metadata(args.repoURL, args.repoBranch, revision_diff.revision_id, args.vcsType),
            args.scope,
        )
        for revision_diff in commit_diff_sequence
    }
    file_states_by_path = reconstruct_final_file_states_by_path_from_commit_diff_sequence(
        commit_diff_sequence,
        protocol_indexes,
        args.scope,
    )

    summary = summarize_live_changed_file_states_by_revision_ids(file_states_by_path, revision_ids, args.scope)
    end_revision_id = resolve_algorithm_b_end_revision_id(args, revision_ids)
    _log_algorithm_b_summary(logger, "offline", summary, end_revision_id, args.scope)
    return build_result_document(args, summary, end_revision_id, logger)


def build_result_algorithm_b_offline_local_git(args: argparse.Namespace, logger: RuntimeLogger) -> dict:
    if args.vcsType != "git":
        raise UnsupportedConfigurationError("Current Algorithm B local period-added replay only supports git")

    repo_dir = resolve_local_git_repository_dir(args)
    revision_ids, end_revision_id = resolve_algorithm_b_git_revision_ids(args, repo_dir)
    commit_diff_sequence = load_git_commit_diff_sequence_from_repository(repo_dir, revision_ids, args.scope)

    provider = build_gen_code_desc_provider(args, logger)
    protocol_indexes = {
        revision_diff.revision_id: _build_protocol_index_for_scope(
            provider.get_revision_metadata(args.repoURL, args.repoBranch, revision_diff.revision_id, args.vcsType),
            args.scope,
        )
        for revision_diff in commit_diff_sequence
    }
    file_states_by_path = reconstruct_final_file_states_by_path_from_commit_diff_sequence(
        commit_diff_sequence,
        protocol_indexes,
        args.scope,
    )
    replay_revision_ids = [revision_diff.revision_id for revision_diff in commit_diff_sequence]
    summary = summarize_live_changed_file_states_by_revision_ids(file_states_by_path, replay_revision_ids, args.scope)

    _log_algorithm_b_summary(logger, "local git period-added", summary, end_revision_id, args.scope)
    return build_result_document(args, summary, end_revision_id, logger)


def build_result_algorithm_b_live_snapshot_offline(args: argparse.Namespace, logger: RuntimeLogger) -> dict:
    if not args.commitDiffSetDir:
        raise UnsupportedConfigurationError("Current Algorithm B live-snapshot slice requires --commitDiffSetDir")

    provider = build_gen_code_desc_provider(args, logger)
    diff_provider = build_commit_diff_provider(args, logger)
    revision_ids = resolve_algorithm_b_offline_revision_ids(args)
    commit_diff_sequence = load_commit_diff_sequence(
        diff_provider,
        args.repoURL,
        args.repoBranch,
        revision_ids,
        args.vcsType,
    )
    if not commit_diff_sequence:
        raise ProtocolValidationError("Algorithm B live-snapshot slice requires at least one replayable commit diff patch")

    protocol_indexes = {
        revision_diff.revision_id: _build_protocol_index_for_scope(
            provider.get_revision_metadata(args.repoURL, args.repoBranch, revision_diff.revision_id, args.vcsType),
            args.scope,
        )
        for revision_diff in commit_diff_sequence
    }
    file_states_by_path = reconstruct_final_file_states_by_path_from_commit_diff_sequence(
        commit_diff_sequence,
        protocol_indexes,
        args.scope,
    )

    summary = summarize_live_changed_file_states_by_revision_ids(file_states_by_path, revision_ids, args.scope)
    end_revision_id = resolve_algorithm_b_end_revision_id(args, revision_ids)
    _log_algorithm_b_summary(logger, "live-snapshot", summary, end_revision_id, args.scope)
    return build_result_document(args, summary, end_revision_id, logger)


def build_result_algorithm_b_live_snapshot_local_git(args: argparse.Namespace, logger: RuntimeLogger) -> dict:
    if args.vcsType != "git":
        raise UnsupportedConfigurationError("Current Algorithm B local live-snapshot replay only supports git")

    repo_dir = resolve_local_git_repository_dir(args)
    revision_ids, end_revision_id = resolve_algorithm_b_git_revision_ids(args, repo_dir)
    commit_diff_sequence = load_git_commit_diff_sequence_from_repository(repo_dir, revision_ids, args.scope)

    provider = build_gen_code_desc_provider(args, logger)
    protocol_indexes = {
        revision_diff.revision_id: _build_protocol_index_for_scope(
            provider.get_revision_metadata(args.repoURL, args.repoBranch, revision_diff.revision_id, args.vcsType),
            args.scope,
        )
        for revision_diff in commit_diff_sequence
    }
    file_states_by_path = reconstruct_final_file_states_by_path_from_commit_diff_sequence(
        commit_diff_sequence,
        protocol_indexes,
        args.scope,
    )
    revision_commit_times = collect_git_revision_commit_times(
        repo_dir,
        [revision_diff.revision_id for revision_diff in commit_diff_sequence],
    )
    summary = summarize_live_snapshot_file_states(
        file_states_by_path,
        revision_commit_times,
        parse_day_start(args.startTime),
        parse_day_end(args.endTime),
        args.scope,
    )

    _log_algorithm_b_summary(logger, "local git live-snapshot", summary, end_revision_id, args.scope)
    return build_result_document(args, summary, end_revision_id, logger)


def strip_json_comments(raw_text: str) -> str:
    result: list[str] = []
    in_string = False
    escaped = False
    in_line_comment = False
    in_block_comment = False
    index = 0

    while index < len(raw_text):
        char = raw_text[index]
        next_char = raw_text[index + 1] if index + 1 < len(raw_text) else ""

        if in_line_comment:
            if char == "\n":
                in_line_comment = False
                result.append(char)
            index += 1
            continue

        if in_block_comment:
            if char == "*" and next_char == "/":
                in_block_comment = False
                index += 2
                continue
            if char == "\n":
                result.append(char)
            index += 1
            continue

        if in_string:
            result.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            index += 1
            continue

        if char == "/" and next_char == "/":
            in_line_comment = True
            index += 2
            continue

        if char == "/" and next_char == "*":
            in_block_comment = True
            index += 2
            continue

        result.append(char)
        if char == '"':
            in_string = True
        index += 1

    return "".join(result)


def load_json_document(raw_text: str) -> dict:
    return json.loads(strip_json_comments(raw_text))


def run_command(
    command: list[str],
    *,
    cwd: Path | None = None,
    timeout: int = COMMAND_TIMEOUT_SECONDS,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError as exc:
        raise CommandExecutionError(f"Required command not found: {command[0]}") from exc
    except subprocess.TimeoutExpired as exc:
        raise CommandExecutionError(
            f"Command timed out after {timeout}s: {' '.join(command)}"
        ) from exc

    if check and result.returncode != 0:
        error_output = (result.stderr or result.stdout or "command failed without output").strip()
        raise CommandExecutionError(
            f"Command failed ({result.returncode}): {' '.join(command)}\n{error_output}"
        )

    return result


def validate_url(value: str, label: str) -> None:
    if not _VALID_URL_SCHEMES.match(value):
        raise InputValidationError(
            f"{label} must start with a valid scheme (http://, https://, svn://, svn+ssh://, file://) or be an absolute path"
        )
    if ".." in value.split("//", 1)[-1]:
        raise InputValidationError(f"{label} must not contain path traversal sequences (..)")


def validate_directory(value: str, label: str) -> Path:
    resolved = Path(value).resolve()
    if not resolved.is_dir():
        raise InputValidationError(f"{label} does not exist or is not a directory: {value}")
    return resolved


def validate_iso_date(value: str, label: str) -> None:
    try:
        datetime.fromisoformat(value)
    except ValueError as exc:
        raise InputValidationError(f"{label} must be a valid ISO-8601 date: {value}") from exc


def validate_inputs(args: argparse.Namespace) -> None:
    validate_url(args.repoURL, "--repoURL")
    if not args.repoBranch or not args.repoBranch.strip():
        raise InputValidationError("--repoBranch must not be empty")
    if ".." in args.repoBranch:
        raise InputValidationError("--repoBranch must not contain path traversal sequences (..)")
    validate_iso_date(args.startTime, "--startTime")
    validate_iso_date(args.endTime, "--endTime")
    if parse_day_start(args.startTime) > parse_day_end(args.endTime):
        raise InputValidationError("--startTime must not be after --endTime")
    if args.vcsType not in {"git", "svn"}:
        raise InputValidationError("--vcsType must be one of: git, svn")
    if args.scope not in {"A", "B", "C", "D"}:
        raise InputValidationError("--scope must be one of: A, B, C, D")
    if args.commitDiffSetDir:
        validate_directory(args.commitDiffSetDir, "--commitDiffSetDir")
        if args.algorithm != "B":
            raise InputValidationError("--commitDiffSetDir is only supported with --algorithm B")
    if args.workingDir:
        validate_directory(args.workingDir, "--workingDir")
    elif args.vcsType == "git" and args.algorithm != "B" and not args.commitDiffSetDir and not is_local_repository_path(args.repoURL):
        raise InputValidationError(
            "--workingDir is required for git when --repoURL is a logical repository URL rather than a local absolute path"
        )
    if args.genCodeDescSetDir:
        validate_directory(args.genCodeDescSetDir, "--genCodeDescSetDir")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Aggregate AI-generated code ratio from VCS blame and genCodeDesc metadata.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__} (protocol {PROTOCOL_VERSION})")
    parser.add_argument("--repoURL", required=True)
    parser.add_argument("--repoBranch", required=True)
    parser.add_argument("--startTime", required=True)
    parser.add_argument("--endTime", required=True)
    parser.add_argument("--vcsType", default="git")
    parser.add_argument("--algorithm", default="A")
    parser.add_argument("--metric")
    parser.add_argument("--scope", default="A")
    parser.add_argument("--outputFile")
    parser.add_argument("--outputFormat", default="json")
    parser.add_argument("--metadataSource", default="genCodeDesc")
    parser.add_argument("--genCodeDescSetDir")
    parser.add_argument("--commitDiffSetDir")
    parser.add_argument("--workingDir")
    parser.add_argument("--failOnMissingProtocol", action="store_true")
    parser.add_argument("--warnOnMissingProtocol", action="store_true")
    parser.add_argument("--includeBreakdown", default="none")
    parser.add_argument("--logLevel", choices=["quiet", "info", "debug"], default="quiet")
    parser.add_argument("--timeout", type=int, default=COMMAND_TIMEOUT_SECONDS, help="Per-command timeout in seconds")
    parser.add_argument("--maxRuntime", type=int, default=DEFAULT_MAX_RUNTIME_SECONDS, help="Overall analysis timeout in seconds")
    return parser.parse_args()


def run_git(repo_dir: Path, args: list[str]) -> str:
    return run_command(["git", *args], cwd=repo_dir).stdout.strip()


def parse_day_start(value: str) -> datetime:
    # WHY: the current query contract is day-based, so the lower bound expands
    # to the start of that UTC day instead of treating the input as an instant.
    return datetime.combine(datetime.fromisoformat(value).date(), time.min, tzinfo=timezone.utc)


def parse_day_end(value: str) -> datetime:
    # WHY: endTime is inclusive for the current metric definition. Expanding to
    # the end of the UTC day avoids dropping commits made later that day.
    return datetime.combine(datetime.fromisoformat(value).date(), time.max, tzinfo=timezone.utc)


def parse_git_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def format_svn_date_bound(value: datetime) -> str:
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def resolve_end_revision(repo_dir: Path, branch: str, end_time: str) -> str:
    end_value = parse_day_end(end_time).isoformat()
    revision_id = run_git(repo_dir, ["rev-list", "-1", f"--before={end_value}", branch])
    if not revision_id:
        raise RepositoryStateError("No revision found at or before endTime")
    return revision_id


def build_svn_branch_target(repo_url: str, branch: str) -> str:
    return f"{repo_url.rstrip('/')}/{branch.strip('/')}"


def run_svn(args: list[str]) -> str:
    return run_command(["svn", *args]).stdout.strip()


def resolve_svn_end_revision(repo_url: str, branch: str, end_time: str) -> str:
    end_value = format_svn_date_bound(parse_day_end(end_time))
    log_xml = run_svn(["log", "--xml", "-r", f"{{{end_value}}}:1", build_svn_branch_target(repo_url, branch)])
    root = ET.fromstring(log_xml)
    log_entry = root.find("logentry")
    if log_entry is None:
        raise RepositoryStateError("No revision found at or before endTime")
    revision_id = log_entry.attrib.get("revision")
    if not revision_id:
        raise RepositoryStateError("Unable to resolve SVN end revision")
    return revision_id


def get_commit_time(repo_dir: Path, revision_id: str, commit_times: dict[str, datetime]) -> datetime:
    commit_time = commit_times.get(revision_id)
    if commit_time is None:
        commit_time = parse_git_timestamp(run_git(repo_dir, ["show", "-s", "--format=%cI", revision_id]))
        commit_times[revision_id] = commit_time
    return commit_time


def get_svn_commit_time(repo_url: str, branch: str, revision_id: str, commit_times: dict[str, datetime]) -> datetime:
    commit_time = commit_times.get(revision_id)
    if commit_time is None:
        log_xml = run_svn(["log", "--xml", "-r", revision_id, repo_url])
        root = ET.fromstring(log_xml)
        log_entry = root.find("logentry")
        if log_entry is None:
            raise RepositoryStateError(f"Unable to resolve SVN revision timestamp for revision {revision_id}")
        date_node = log_entry.find("date")
        if date_node is None or not date_node.text:
            raise RepositoryStateError(f"Missing SVN revision timestamp for revision {revision_id}")
        commit_time = parse_git_timestamp(date_node.text)
        commit_times[revision_id] = commit_time
    return commit_time


def list_source_files(repo_dir: Path, revision_id: str) -> list[str]:
    output = run_git(repo_dir, ["ls-tree", "-r", "--name-only", revision_id])
    files = [line for line in output.splitlines() if Path(line).suffix in SOURCE_EXTENSIONS]
    return files


def list_svn_source_files(repo_url: str, branch: str, revision_id: str) -> list[str]:
    output = run_svn(["ls", "-R", "-r", revision_id, build_svn_branch_target(repo_url, branch)])
    files = [line for line in output.splitlines() if line and not line.endswith("/") and Path(line).suffix in SOURCE_EXTENSIONS]
    return files


def list_doc_files(repo_dir: Path, revision_id: str) -> list[str]:
    output = run_git(repo_dir, ["ls-tree", "-r", "--name-only", revision_id])
    files = [line for line in output.splitlines() if Path(line).suffix in DOC_EXTENSIONS]
    return files


def list_svn_doc_files(repo_url: str, branch: str, revision_id: str) -> list[str]:
    output = run_svn(["ls", "-R", "-r", revision_id, build_svn_branch_target(repo_url, branch)])
    files = [line for line in output.splitlines() if line and not line.endswith("/") and Path(line).suffix in DOC_EXTENSIONS]
    return files


def parse_blame(repo_dir: Path, revision_id: str, relative_path: str) -> list[BlameLine]:
    output = run_git(repo_dir, ["blame", "--line-porcelain", revision_id, "--", relative_path])
    if len(output) > MAX_FILE_SIZE_BYTES:
        raise RepositoryStateError(
            f"Blame output for {relative_path} at {revision_id} exceeds {MAX_FILE_SIZE_BYTES} byte limit "
            f"({len(output)} bytes) — possible binary or generated file"
        )
    lines = output.splitlines()
    parsed: list[BlameLine] = []
    index = 0
    while index < len(lines):
        header = lines[index]
        header_parts = header.split()
        revision = header_parts[0]
        origin_line = int(header_parts[1])
        final_line = int(header_parts[2])
        index += 1

        origin_file = relative_path
        while index < len(lines) and not lines[index].startswith("\t"):
            meta_line = lines[index]
            if meta_line.startswith("filename "):
                # WHY: blame can report the historical filename after rename.
                # The metadata join needs that origin path rather than only the
                # final path shown in the end snapshot.
                origin_file = meta_line[len("filename "):]
            index += 1

        if index >= len(lines):
            break

        content = lines[index][1:]
        parsed.append(
            BlameLine(
                revision_id=revision,
                origin_file=origin_file,
                origin_line=origin_line,
                final_line=final_line,
                content=content,
            )
        )
        index += 1

    return parsed


def parse_svn_blame(repo_url: str, branch: str, revision_id: str, relative_path: str) -> list[BlameLine]:
    target = f"{build_svn_branch_target(repo_url, branch)}/{relative_path}"
    blame_xml = run_svn(["blame", "--xml", "-g", "-r", revision_id, target])
    file_content = run_svn(["cat", "-r", revision_id, target])
    content_lines = file_content.splitlines()
    root = ET.fromstring(blame_xml)
    target_node = root.find("target")
    if target_node is None:
        return []

    blame_entries = target_node.findall("entry")
    if len(blame_entries) != len(content_lines):
        raise RepositoryStateError(
            f"SVN blame/content line count mismatch for {relative_path} at revision {revision_id}: "
            f"blameEntries={len(blame_entries)} contentLines={len(content_lines)}"
        )

    parsed: list[BlameLine] = []
    origin_file = f"{branch.strip('/')}/{relative_path}"
    for final_line, (entry, content) in enumerate(zip(blame_entries, content_lines), start=1):
        commit_node = entry.find("commit")
        merged_node = entry.find("merged")
        merged_commit_node = merged_node.find("commit") if merged_node is not None else None
        revision_value = commit_node.attrib.get("revision") if commit_node is not None else None
        if not revision_value:
            continue
        merged_path = merged_node.attrib.get("path") if merged_node is not None else None
        joined_origin_file = origin_file
        merged_origin_file = merged_path.lstrip("/") if merged_path else None
        if merged_origin_file and merged_origin_file != origin_file and merged_commit_node is not None:
            joined_origin_file = merged_origin_file
            revision_value = merged_commit_node.attrib.get("revision", revision_value)
        parsed.append(
            BlameLine(
                revision_id=revision_value,
                # WHY: svn blame -g exposes both the visible commit and an
                # optional merged source. We only prefer the merged source when
                # it points at a different branch path; otherwise the commit
                # node already carries the effective originating revision.
                origin_file=joined_origin_file,
                # WHY: svn blame does not expose Git-style historical origin
                # line numbers. The current SVN slice starts with same-path,
                # no-line-shift scenarios where final line number is sufficient
                # to join external metadata.
                origin_line=final_line,
                final_line=final_line,
                content=content,
            )
        )

    return parsed


def is_code_line(content: str, scope: str = "A") -> bool:
    stripped = content.strip()
    if not stripped:
        return False
    if scope in ("B", "C", "D"):
        return True
    comment_prefixes = ("#", "//", "/*", "*", "*/")
    return not stripped.startswith(comment_prefixes)


def build_gen_code_desc_provider(args: argparse.Namespace, logger: RuntimeLogger) -> GenCodeDescProvider:
    if args.metadataSource == "genCodeDesc":
        if args.genCodeDescSetDir:
            return GenCodeDescSetDirProvider(
                Path(args.genCodeDescSetDir),
                args.failOnMissingProtocol,
                args.warnOnMissingProtocol,
                logger,
            )
        return EmptyGenCodeDescProvider(args.failOnMissingProtocol, args.warnOnMissingProtocol, logger)

    raise UnsupportedConfigurationError(
        f"Unsupported metadataSource: {args.metadataSource}. Only 'genCodeDesc' is supported in the current slice."
    )


def build_commit_diff_provider(args: argparse.Namespace, logger: RuntimeLogger) -> CommitDiffProvider:
    if args.commitDiffSetDir:
        return CommitDiffSetDirProvider(Path(args.commitDiffSetDir), logger)
    return EmptyCommitDiffProvider(logger)


def describe_ratio(ratio: int) -> str:
    if ratio == 100:
        return "100%-ai"
    if ratio > 0:
        return f"{ratio}%-ai"
    return "human/unattributed"


def require_int(value: object, context: str) -> int:
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ProtocolValidationError(f"{context} must be an integer") from exc


def validate_no_overlap(
    file_name: str,
    exact_lines: dict[int, int],
    ranges: list[tuple[int, int, int]],
    range_start: int,
    range_end: int,
) -> None:
    if range_start > range_end:
        raise ProtocolValidationError(
            f"Protocol DETAIL entry for {file_name} has lineRange.from greater than lineRange.to"
        )
    for line_number in exact_lines:
        if range_start <= line_number <= range_end:
            raise ProtocolValidationError(
                f"Protocol DETAIL entry for {file_name} has overlapping line coverage at line {line_number}"
            )
    for existing_start, existing_end, _ in ranges:
        if not (range_end < existing_start or range_start > existing_end):
            raise ProtocolValidationError(
                f"Protocol DETAIL entry for {file_name} has overlapping line ranges {range_start}-{range_end} and {existing_start}-{existing_end}"
            )


def build_protocol_index(protocol: dict) -> dict[str, IndexedFileDetail]:
    indexed_detail: dict[str, IndexedFileDetail] = {}
    detail_entries = protocol.get("DETAIL", [])
    if not isinstance(detail_entries, list):
        raise ProtocolValidationError("Protocol DETAIL must be a list")

    for file_entry in detail_entries:
        if not isinstance(file_entry, dict):
            raise ProtocolValidationError("Each Protocol DETAIL entry must be an object")

        file_name = file_entry.get("fileName")
        if not isinstance(file_name, str) or not file_name:
            raise ProtocolValidationError("Protocol DETAIL entry missing fileName")

        exact_lines: dict[int, int] = {}
        ranges: list[tuple[int, int, int]] = []
        code_lines = file_entry.get("codeLines", [])
        if code_lines is None:
            code_lines = []
        if not isinstance(code_lines, list):
            raise ProtocolValidationError(f"Protocol DETAIL entry for {file_name} has non-list codeLines")

        for code_line in code_lines:
            if not isinstance(code_line, dict):
                raise ProtocolValidationError(f"Protocol DETAIL entry for {file_name} contains a non-object codeLines item")

            gen_ratio = require_int(code_line.get("genRatio", 0), f"Protocol DETAIL entry for {file_name} genRatio")
            if not 0 <= gen_ratio <= 100:
                raise ProtocolValidationError(f"Protocol DETAIL entry for {file_name} has genRatio outside 0..100")

            line_location = code_line.get("lineLocation")
            if line_location is not None:
                line_number = require_int(line_location, f"Protocol DETAIL entry for {file_name} lineLocation")
                if line_number in exact_lines:
                    raise ProtocolValidationError(
                        f"Protocol DETAIL entry for {file_name} duplicates lineLocation {line_number}"
                    )
                for range_start, range_end, _ in ranges:
                    if range_start <= line_number <= range_end:
                        raise ProtocolValidationError(
                            f"Protocol DETAIL entry for {file_name} has overlapping line coverage at line {line_number}"
                        )
                exact_lines[line_number] = gen_ratio
                continue

            line_range = code_line.get("lineRange")
            if line_range:
                if not isinstance(line_range, dict):
                    raise ProtocolValidationError(f"Protocol DETAIL entry for {file_name} has non-object lineRange")
                range_start = require_int(line_range.get("from"), f"Protocol DETAIL entry for {file_name} lineRange.from")
                range_end = require_int(line_range.get("to"), f"Protocol DETAIL entry for {file_name} lineRange.to")
                validate_no_overlap(file_name, exact_lines, ranges, range_start, range_end)
                ranges.append((range_start, range_end, gen_ratio))
                continue

            raise ProtocolValidationError(
                f"Protocol DETAIL entry for {file_name} must define either lineLocation or lineRange"
            )

        indexed_detail[file_name] = IndexedFileDetail(
            line_locations=exact_lines,
            line_ranges=ranges,
        )
    return indexed_detail


def build_doc_protocol_index(protocol: dict) -> dict[str, IndexedFileDetail]:
    indexed_detail: dict[str, IndexedFileDetail] = {}
    detail_entries = protocol.get("DETAIL", [])
    if not isinstance(detail_entries, list):
        raise ProtocolValidationError("Protocol DETAIL must be a list")

    for file_entry in detail_entries:
        if not isinstance(file_entry, dict):
            raise ProtocolValidationError("Each Protocol DETAIL entry must be an object")

        file_name = file_entry.get("fileName")
        if not isinstance(file_name, str) or not file_name:
            raise ProtocolValidationError("Protocol DETAIL entry missing fileName")

        exact_lines: dict[int, int] = {}
        ranges: list[tuple[int, int, int]] = []
        doc_lines = file_entry.get("docLines", [])
        if doc_lines is None:
            doc_lines = []
        if not isinstance(doc_lines, list):
            raise ProtocolValidationError(f"Protocol DETAIL entry for {file_name} has non-list docLines")

        for doc_line in doc_lines:
            if not isinstance(doc_line, dict):
                raise ProtocolValidationError(f"Protocol DETAIL entry for {file_name} contains a non-object docLines item")

            gen_ratio = require_int(doc_line.get("genRatio", 0), f"Protocol DETAIL entry for {file_name} genRatio")
            if not 0 <= gen_ratio <= 100:
                raise ProtocolValidationError(f"Protocol DETAIL entry for {file_name} has genRatio outside 0..100")

            line_location = doc_line.get("lineLocation")
            if line_location is not None:
                line_number = require_int(line_location, f"Protocol DETAIL entry for {file_name} lineLocation")
                if line_number in exact_lines:
                    raise ProtocolValidationError(
                        f"Protocol DETAIL entry for {file_name} duplicates lineLocation {line_number}"
                    )
                for range_start, range_end, _ in ranges:
                    if range_start <= line_number <= range_end:
                        raise ProtocolValidationError(
                            f"Protocol DETAIL entry for {file_name} has overlapping line coverage at line {line_number}"
                        )
                exact_lines[line_number] = gen_ratio
                continue

            line_range = doc_line.get("lineRange")
            if line_range:
                if not isinstance(line_range, dict):
                    raise ProtocolValidationError(f"Protocol DETAIL entry for {file_name} has non-object lineRange")
                range_start = require_int(line_range.get("from"), f"Protocol DETAIL entry for {file_name} lineRange.from")
                range_end = require_int(line_range.get("to"), f"Protocol DETAIL entry for {file_name} lineRange.to")
                validate_no_overlap(file_name, exact_lines, ranges, range_start, range_end)
                ranges.append((range_start, range_end, gen_ratio))
                continue

            raise ProtocolValidationError(
                f"Protocol DETAIL entry for {file_name} must define either lineLocation or lineRange"
            )

        indexed_detail[file_name] = IndexedFileDetail(
            line_locations=exact_lines,
            line_ranges=ranges,
        )
    return indexed_detail


def build_combined_protocol_index(protocol: dict) -> dict[str, IndexedFileDetail]:
    code_idx = build_protocol_index(protocol)
    doc_idx = build_doc_protocol_index(protocol)
    combined: dict[str, IndexedFileDetail] = {}
    for file_name in set(code_idx) | set(doc_idx):
        if Path(file_name).suffix in SOURCE_EXTENSIONS:
            combined[file_name] = code_idx.get(file_name, IndexedFileDetail(line_locations={}, line_ranges=[]))
        elif Path(file_name).suffix in DOC_EXTENSIONS:
            combined[file_name] = doc_idx.get(file_name, IndexedFileDetail(line_locations={}, line_ranges=[]))
        else:
            combined[file_name] = code_idx.get(file_name, doc_idx.get(file_name, IndexedFileDetail(line_locations={}, line_ranges=[])))
    return combined


def resolve_parent_revision(vcs_type: str, repo_dir: Path, repo_url: str, branch: str, revision_id: str) -> str | None:
    if vcs_type == "git":
        result = run_command(["git", "rev-parse", f"{revision_id}^"], cwd=repo_dir, check=False)
        if result.returncode != 0:
            return None
        return result.stdout.strip() or None

    if vcs_type == "svn":
        if not revision_id.isdigit():
            return None
        parent_revision = int(revision_id) - 1
        return str(parent_revision) if parent_revision >= 1 else None

    return None


def best_effort_transition_hint(
    repo_dir: Path,
    provider: GenCodeDescProvider,
    logger: RuntimeLogger,
    args: argparse.Namespace,
    blame_line: BlameLine,
    current_ratio: int,
    protocols: dict[str, dict],
    protocol_indexes: dict[str, dict[str, IndexedFileDetail]],
    parent_revisions: dict[str, str | None],
) -> str | None:
    if logger.level != "debug":
        return None

    parent_revision = parent_revisions.get(blame_line.revision_id)
    if parent_revision is None and blame_line.revision_id not in parent_revisions:
        parent_revision = resolve_parent_revision(args.vcsType, repo_dir, args.repoURL, args.repoBranch, blame_line.revision_id)
        parent_revisions[blame_line.revision_id] = parent_revision

    if not parent_revision:
        return None

    parent_protocol = protocols.get(parent_revision)
    if parent_protocol is None:
        parent_protocol = provider.get_revision_metadata(args.repoURL, args.repoBranch, parent_revision, args.vcsType)
        protocols[parent_revision] = parent_protocol
        protocol_indexes[parent_revision] = build_protocol_index(parent_protocol)

    parent_ratio = line_ratio(protocol_indexes[parent_revision], blame_line.origin_file, blame_line.origin_line)
    if parent_ratio == current_ratio:
        return None
    return f"best_effort_transition={describe_ratio(parent_ratio)}->{describe_ratio(current_ratio)}"


def line_ratio(protocol_index: dict[str, IndexedFileDetail], origin_file: str, origin_line: int) -> int:
    indexed_file = protocol_index.get(origin_file)
    if indexed_file is None:
        return 0
    exact_ratio = indexed_file.line_locations.get(origin_line)
    if exact_ratio is not None:
        return exact_ratio
    for range_start, range_end, ratio in indexed_file.line_ranges:
        if range_start <= origin_line <= range_end:
            return ratio
    return 0


def resolve_algorithm_b_metric(args: argparse.Namespace) -> str:
    explicit_metric = args.metric
    inferred_metric = None
    query_document = load_algorithm_b_query(args)
    if query_document is not None:
        query_metric = query_document.get("metric")
        if isinstance(query_metric, str) and query_metric:
            inferred_metric = query_metric

    if explicit_metric and inferred_metric and explicit_metric != inferred_metric:
        raise InputValidationError(
            f"--metric {explicit_metric} does not match query.json metric {inferred_metric} in --genCodeDescSetDir"
        )

    resolved_metric = explicit_metric or inferred_metric or "live_changed_source_ratio"

    return resolved_metric


def load_algorithm_b_query(args: argparse.Namespace) -> dict | None:
    if not args.genCodeDescSetDir:
        return None

    query_path = Path(args.genCodeDescSetDir) / "query.json"
    if not query_path.exists():
        return None

    try:
        query_document = load_json_document(query_path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ProtocolValidationError(f"Failed to read Algorithm B query from {query_path}: {exc}") from exc

    if not isinstance(query_document, dict):
        raise ProtocolValidationError(f"Algorithm B query at {query_path} must be a JSON object")

    return query_document


def resolve_algorithm_b_end_revision_id(args: argparse.Namespace, revision_ids: list[str]) -> str:
    query_document = load_algorithm_b_query(args)
    if query_document is not None:
        end_revision_id = query_document.get("endRevisionId")
        if end_revision_id is not None:
            if not isinstance(end_revision_id, str) or not end_revision_id:
                raise ProtocolValidationError("query.json endRevisionId must be a non-empty string when provided")
            return end_revision_id
    return revision_ids[-1]


def build_result(args: argparse.Namespace) -> dict:
    logger = RuntimeLogger(args.logLevel)
    if args.algorithm == "B":
        resolved_metric = resolve_algorithm_b_metric(args)
        if resolved_metric == "live_changed_source_ratio" and args.commitDiffSetDir:
            return build_result_algorithm_b_live_snapshot_offline(args, logger)
        if resolved_metric == "live_changed_source_ratio":
            return build_result_algorithm_b_live_snapshot_local_git(args, logger)
        if resolved_metric == "period_added_ai_ratio":
            if args.commitDiffSetDir:
                return build_result_algorithm_b_offline(args, logger)
            return build_result_algorithm_b_offline_local_git(args, logger)
        raise UnsupportedConfigurationError(
            "Current Algorithm B routing only supports metrics: live_changed_source_ratio, period_added_ai_ratio"
        )
    if args.algorithm != "A":
        raise UnsupportedConfigurationError("Only Algorithm A is implemented in the current Git/SVN Algorithm A slice")
    if args.scope not in ("A", "B", "C", "D"):
        raise UnsupportedConfigurationError("Only Scope A, B, C, and D are implemented in the current Git/SVN Algorithm A slice")
    if args.outputFormat != "json":
        raise UnsupportedConfigurationError("Only JSON output is implemented in the current Git/SVN Algorithm A slice")
    if args.vcsType not in {"git", "svn"}:
        raise UnsupportedConfigurationError("Only git and svn are implemented in the current Algorithm A slice")

    analysis_start = time_mod.monotonic()
    logical_repo_url = args.repoURL
    repo_dir = Path(args.workingDir or args.repoURL)
    provider = build_gen_code_desc_provider(args, logger)
    start_bound = parse_day_start(args.startTime)
    end_bound = parse_day_end(args.endTime)
    if args.vcsType == "git":
        end_revision_id = resolve_end_revision(repo_dir, args.repoBranch, args.endTime)
        if args.scope == "C":
            source_files = list_doc_files(repo_dir, end_revision_id)
        elif args.scope == "D":
            source_files = list_source_files(repo_dir, end_revision_id) + list_doc_files(repo_dir, end_revision_id)
        else:
            source_files = list_source_files(repo_dir, end_revision_id)
        repo_identity_url = logical_repo_url
    else:
        end_revision_id = resolve_svn_end_revision(args.repoURL, args.repoBranch, args.endTime)
        if args.scope == "C":
            source_files = list_svn_doc_files(args.repoURL, args.repoBranch, end_revision_id)
        elif args.scope == "D":
            source_files = list_svn_source_files(args.repoURL, args.repoBranch, end_revision_id) + list_svn_doc_files(args.repoURL, args.repoBranch, end_revision_id)
        else:
            source_files = list_svn_source_files(args.repoURL, args.repoBranch, end_revision_id)
        repo_identity_url = logical_repo_url
    logger.info(
        f"Starting analysis for repo={repo_identity_url} branch={args.repoBranch} window={args.startTime}..{args.endTime} endRevision={end_revision_id}"
    )

    protocols: dict[str, dict] = {}
    protocol_indexes: dict[str, dict[str, IndexedFileDetail]] = {}
    parent_revisions: dict[str, str | None] = {}
    commit_times: dict[str, datetime] = {}
    total_code_lines = 0
    full_generated_code_lines = 0
    partial_generated_code_lines = 0

    logger.debug(f"Resolved {len(source_files)} source files in the end snapshot")

    for relative_path in source_files:
        logger.debug(f"Scanning file {relative_path}")
        blame_lines = (
            parse_blame(repo_dir, end_revision_id, relative_path)
            if args.vcsType == "git"
            else parse_svn_blame(args.repoURL, args.repoBranch, end_revision_id, relative_path)
        )
        for blame_line in blame_lines:
            if not is_code_line(blame_line.content, args.scope):
                logger.debug(f"Skip non-code line {relative_path}:{blame_line.final_line}")
                continue

            commit_time = (
                get_commit_time(repo_dir, blame_line.revision_id, commit_times)
                if args.vcsType == "git"
                else get_svn_commit_time(args.repoURL, args.repoBranch, blame_line.revision_id, commit_times)
            )
            # WHY: the current primary metric is defined over live lines whose
            # current form originated within the query window. Blame gives that
            # origin revision, so the time filter must be applied to the
            # blame-resolved commit rather than only to the end snapshot.
            if not (start_bound <= commit_time <= end_bound):
                logger.debug(
                    f"Skip out-of-window line {relative_path}:{blame_line.final_line} origin={blame_line.revision_id} commitTime={commit_time.isoformat()}"
                )
                continue

            total_code_lines += 1
            protocol = protocols.get(blame_line.revision_id)
            if protocol is None:
                # WHY: metadata is revision-scoped. Many lines can share one
                # origin revision, so caching keeps lookup cost aligned with the
                # revision model instead of repeating the same fetch per line.
                protocol = provider.get_revision_metadata(args.repoURL, args.repoBranch, blame_line.revision_id, args.vcsType)
                protocols[blame_line.revision_id] = protocol
                if args.scope == "C":
                    protocol_indexes[blame_line.revision_id] = build_doc_protocol_index(protocol)
                elif args.scope == "D":
                    protocol_indexes[blame_line.revision_id] = build_combined_protocol_index(protocol)
                else:
                    protocol_indexes[blame_line.revision_id] = build_protocol_index(protocol)
            else:
                logger.debug(f"Reuse cached genCodeDesc for revision {blame_line.revision_id}")

            ratio = line_ratio(protocol_indexes[blame_line.revision_id], blame_line.origin_file, blame_line.origin_line)
            transition_hint = best_effort_transition_hint(
                repo_dir,
                provider,
                logger,
                args,
                blame_line,
                ratio,
                protocols,
                protocol_indexes,
                parent_revisions,
            )
            line_message = (
                f"LiveLine {relative_path}:{blame_line.final_line} aggregate "
                f"origin={blame_line.origin_file}:{blame_line.origin_line}@{blame_line.revision_id} "
                f"classification={describe_ratio(ratio)}"
            )
            if transition_hint:
                logger.debug(
                    f"TransitionHint {relative_path}:{blame_line.final_line} "
                    f"origin={blame_line.origin_file}:{blame_line.origin_line}@{blame_line.revision_id} "
                    f"{transition_hint}"
                )
            logger.info(line_message)

            if ratio == 100:
                full_generated_code_lines += 1
            elif ratio > 0:
                partial_generated_code_lines += 1

    elapsed = time_mod.monotonic() - analysis_start
    logger.info(
        "Finished analysis with "
        f"totalCodeLines={total_code_lines} fullGeneratedCodeLines={full_generated_code_lines} "
        f"partialGeneratedCodeLines={partial_generated_code_lines} "
        f"elapsed={elapsed:.2f}s"
    )

    if args.scope == "C":
        summary = {
            "totalDocLines": total_code_lines,
            "fullGeneratedDocLines": full_generated_code_lines,
            "partialGeneratedDocLines": partial_generated_code_lines,
        }
    else:
        summary = {
            "totalCodeLines": total_code_lines,
            "fullGeneratedCodeLines": full_generated_code_lines,
            "partialGeneratedCodeLines": partial_generated_code_lines,
        }

    return build_result_document(
        args,
        summary,
        end_revision_id,
        logger,
        repo_url_override=repo_identity_url,
    )


# Exit codes for distinct failure categories.
EXIT_SUCCESS = 0
EXIT_INPUT_ERROR = 1
EXIT_REPOSITORY_ERROR = 2
EXIT_PROTOCOL_ERROR = 3
EXIT_TIMEOUT = 4


def main() -> None:
    args = None
    try:
        args = parse_args()
        validate_inputs(args)

        def _timeout_handler(signum: int, frame: object) -> None:
            raise SystemExit(EXIT_TIMEOUT)

        if hasattr(signal, "SIGALRM"):
            signal.signal(signal.SIGALRM, _timeout_handler)
            signal.alarm(args.maxRuntime)
        else:
            print("WARNING: --maxRuntime timeout not supported on this platform", file=sys.stderr)

        result = build_result(args)
        output = json.dumps(result, indent=2)
        if args.outputFile:
            Path(args.outputFile).write_text(output, encoding="utf-8")
        else:
            print(output)
    except InputValidationError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(EXIT_INPUT_ERROR) from exc
    except UnsupportedConfigurationError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(EXIT_INPUT_ERROR) from exc
    except RepositoryStateError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(EXIT_REPOSITORY_ERROR) from exc
    except ProtocolValidationError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(EXIT_PROTOCOL_ERROR) from exc
    except CommandExecutionError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(EXIT_REPOSITORY_ERROR) from exc
    except json.JSONDecodeError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(EXIT_PROTOCOL_ERROR) from exc
    finally:
        if hasattr(signal, "SIGALRM"):
            signal.alarm(0)


if __name__ == "__main__":
    main()