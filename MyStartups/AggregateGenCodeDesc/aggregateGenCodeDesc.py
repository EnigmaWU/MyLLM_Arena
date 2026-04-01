"""Current CLI slice for AggregateGenCodeDesc.

This implementation is intentionally narrow:
- Git and SVN
- Algorithm A only
- Scope A only
- JSON output only
- external revision metadata resolved through the current genCodeDesc provider path

The tested story coverage extends beyond the initial Git-only slice, but the
runtime still intentionally implements only the current Scope A path.
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

    def _emit(self, severity: str, message: str) -> None:
        ts = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        print(f"{ts} [{severity}] [agg] {message}", file=sys.stderr)

    def error(self, message: str) -> None:
        self._emit("ERROR", message)

    def warn(self, message: str) -> None:
        if self._level_num >= 1:
            self._emit("WARN", message)

    def info(self, message: str) -> None:
        if self._level_num >= 1:
            self._emit("INFO", message)

    def debug(self, message: str) -> None:
        if self._level_num >= 2:
            self._emit("DEBUG", message)


class GenCodeDescProvider(ABC):
    @abstractmethod
    def get_revision_metadata(self, repo_url: str, repo_branch: str, revision_id: str, vcs_type: str) -> dict:
        raise NotImplementedError


class CommitDiffProvider(ABC):
    @abstractmethod
    def get_commit_diff_patch(self, repo_url: str, repo_branch: str, revision_id: str, vcs_type: str) -> str | None:
        raise NotImplementedError


class EmptyGenCodeDescProvider(GenCodeDescProvider):
    def __init__(self, fail_on_missing: bool, logger: RuntimeLogger):
        self.fail_on_missing = fail_on_missing
        self.logger = logger

    def get_revision_metadata(self, repo_url: str, repo_branch: str, revision_id: str, vcs_type: str) -> dict:
        if self.fail_on_missing:
            raise ProtocolValidationError(f"Missing genCodeDesc provider data for revision {revision_id}")
        self.logger.debug(f"No external genCodeDesc found for revision {revision_id}; treating all lines as human/unattributed")
        return {}


class EmptyCommitDiffProvider(CommitDiffProvider):
    def __init__(self, logger: RuntimeLogger):
        self.logger = logger

    def get_commit_diff_patch(self, repo_url: str, repo_branch: str, revision_id: str, vcs_type: str) -> str | None:
        self.logger.debug(f"No external commit diff provider configured for revision {revision_id}")
        return None


class GenCodeDescSetDirProvider(GenCodeDescProvider):
    def __init__(self, base_dir: Path, fail_on_missing: bool, logger: RuntimeLogger):
        self.base_dir = base_dir
        self.fail_on_missing = fail_on_missing
        self.logger = logger

    def get_revision_metadata(self, repo_url: str, repo_branch: str, revision_id: str, vcs_type: str) -> dict:
        protocol_path = self.base_dir / f"{revision_id}_genCodeDesc.json"
        if not protocol_path.exists():
            if self.fail_on_missing:
                raise ProtocolValidationError(f"Protocol file not found: {protocol_path}")
            self.logger.debug(f"No genCodeDesc file found at {protocol_path}; treating revision {revision_id} as human/unattributed")
            return {}
        protocol = load_json_document(protocol_path.read_text(encoding="utf-8"))
        repository = protocol.get("REPOSITORY", {})
        self.logger.debug(f"Loaded genCodeDesc for revision {revision_id} from {protocol_path}")

        # WHY: genCodeDesc is external metadata, not repository content. We
        # validate identity fields here so the analyzer cannot silently join a
        # real repository revision with the wrong external record.
        protocol_vcs_type = repository.get("vcsType")
        if protocol_vcs_type and protocol_vcs_type != vcs_type:
            raise ValueError(
                f"Metadata vcsType mismatch for revision {revision_id}: expected {vcs_type}, got {protocol_vcs_type}"
            )

        protocol_repo_url = repository.get("repoURL")
        if protocol_repo_url and protocol_repo_url != repo_url:
            raise ValueError(
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
            raise ValueError(
                f"Metadata revisionId mismatch for revision {revision_id}: expected {revision_id}, got {protocol_revision_id}"
            )

        return protocol


class CommitDiffSetDirProvider(CommitDiffProvider):
    def __init__(self, base_dir: Path, logger: RuntimeLogger):
        self.base_dir = base_dir
        self.logger = logger

    def get_commit_diff_patch(self, repo_url: str, repo_branch: str, revision_id: str, vcs_type: str) -> str:
        patch_path = self.base_dir / f"{revision_id}_commitDiff.patch"
        if not patch_path.exists():
            raise ProtocolValidationError(f"Commit diff patch file not found: {patch_path}")

        patch_text = patch_path.read_text(encoding="utf-8")
        if not patch_text.strip():
            raise ProtocolValidationError(f"Commit diff patch file is empty: {patch_path}")

        self.logger.debug(f"Loaded commit diff patch for revision {revision_id} from {patch_path}")
        return patch_text


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
    validate_iso_date(args.startTime, "--startTime")
    validate_iso_date(args.endTime, "--endTime")
    if args.commitDiffSetDir:
        validate_directory(args.commitDiffSetDir, "--commitDiffSetDir")
        if args.algorithm != "B":
            raise InputValidationError("--commitDiffSetDir is only supported with --algorithm B")
    if args.workingDir:
        validate_directory(args.workingDir, "--workingDir")
    elif args.vcsType == "git" and not args.commitDiffSetDir and not is_local_repository_path(args.repoURL):
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
    parser.add_argument("--scope", default="A")
    parser.add_argument("--outputFile")
    parser.add_argument("--outputFormat", default="json")
    parser.add_argument("--metadataSource", default="genCodeDesc")
    parser.add_argument("--genCodeDescSetDir")
    parser.add_argument("--commitDiffSetDir")
    parser.add_argument("--workingDir")
    parser.add_argument("--failOnMissingProtocol", action="store_true")
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


def parse_blame(repo_dir: Path, revision_id: str, relative_path: str) -> list[BlameLine]:
    output = run_git(repo_dir, ["blame", "--line-porcelain", revision_id, "--", relative_path])
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


def is_code_line(content: str) -> bool:
    stripped = content.strip()
    if not stripped:
        return False
    comment_prefixes = ("#", "//", "/*", "*", "*/")
    return not stripped.startswith(comment_prefixes)


def build_gen_code_desc_provider(args: argparse.Namespace, logger: RuntimeLogger) -> GenCodeDescProvider:
    if args.metadataSource == "genCodeDesc":
        if args.genCodeDescSetDir:
            return GenCodeDescSetDirProvider(Path(args.genCodeDescSetDir), args.failOnMissingProtocol, logger)
        return EmptyGenCodeDescProvider(args.failOnMissingProtocol, logger)

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


def build_result(args: argparse.Namespace) -> dict:
    if args.algorithm == "B" and args.commitDiffSetDir:
        raise UnsupportedConfigurationError(
            "Algorithm B offline diff mode via --commitDiffSetDir is not implemented in the current slice"
        )
    if args.algorithm != "A":
        raise UnsupportedConfigurationError("Only Algorithm A is implemented in the current Git/SVN Algorithm A slice")
    if args.scope != "A":
        raise UnsupportedConfigurationError("Only Scope A is implemented in the current Git/SVN Algorithm A slice")
    if args.outputFormat != "json":
        raise UnsupportedConfigurationError("Only JSON output is implemented in the current Git/SVN Algorithm A slice")
    if args.vcsType not in {"git", "svn"}:
        raise UnsupportedConfigurationError("Only git and svn are implemented in the current Algorithm A slice")

    logger = RuntimeLogger(args.logLevel)
    analysis_start = time_mod.monotonic()
    logical_repo_url = args.repoURL
    repo_dir = Path(args.workingDir or args.repoURL)
    provider = build_gen_code_desc_provider(args, logger)
    start_bound = parse_day_start(args.startTime)
    end_bound = parse_day_end(args.endTime)
    if args.vcsType == "git":
        end_revision_id = resolve_end_revision(repo_dir, args.repoBranch, args.endTime)
        source_files = list_source_files(repo_dir, end_revision_id)
        repo_identity_url = logical_repo_url
    else:
        end_revision_id = resolve_svn_end_revision(args.repoURL, args.repoBranch, args.endTime)
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
            if not is_code_line(blame_line.content):
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

    return {
        "protocolName": "generatedTextDesc",
        "protocolVersion": PROTOCOL_VERSION,
        "SUMMARY": {
            "totalCodeLines": total_code_lines,
            "fullGeneratedCodeLines": full_generated_code_lines,
            "partialGeneratedCodeLines": partial_generated_code_lines,
        },
        "REPOSITORY": {
            "vcsType": args.vcsType,
            "repoURL": repo_identity_url,
            "repoBranch": args.repoBranch,
            "revisionId": end_revision_id,
        },
    }


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
    except (ProtocolValidationError, ValueError) as exc:
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