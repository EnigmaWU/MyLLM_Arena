"""Current CLI slice for AggregateGenCodeDesc.

This implementation is intentionally narrow:
- Git only
- Model A only
- Scope A only
- JSON output only
- external revision metadata resolved through the current genCodeDesc provider path

The tested story coverage now includes at least US-1 through US-5 on this runtime path.
"""

import argparse
import json
import subprocess
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, time, timezone
from pathlib import Path


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


class RuntimeLogger:
    def __init__(self, level: str):
        self.level = level

    def info(self, message: str) -> None:
        if self.level in {"info", "debug"}:
            print(f"[agg] {message}", file=sys.stderr)

    def debug(self, message: str) -> None:
        if self.level == "debug":
            print(f"[agg] {message}", file=sys.stderr)


class GenCodeDescProvider(ABC):
    @abstractmethod
    def get_revision_metadata(self, repo_url: str, repo_branch: str, revision_id: str, vcs_type: str) -> dict:
        raise NotImplementedError


class EmptyGenCodeDescProvider(GenCodeDescProvider):
    def __init__(self, fail_on_missing: bool, logger: RuntimeLogger):
        self.fail_on_missing = fail_on_missing
        self.logger = logger

    def get_revision_metadata(self, repo_url: str, repo_branch: str, revision_id: str, vcs_type: str) -> dict:
        if self.fail_on_missing:
            raise FileNotFoundError(f"Missing genCodeDesc provider data for revision {revision_id}")
        self.logger.debug(f"No external genCodeDesc found for revision {revision_id}; treating all lines as human/unattributed")
        return {}


class GenCodeDescSetDirProvider(GenCodeDescProvider):
    def __init__(self, base_dir: Path, fail_on_missing: bool, logger: RuntimeLogger):
        self.base_dir = base_dir
        self.fail_on_missing = fail_on_missing
        self.logger = logger

    def get_revision_metadata(self, repo_url: str, repo_branch: str, revision_id: str, vcs_type: str) -> dict:
        protocol_path = self.base_dir / f"{revision_id}_genCodeDesc.json"
        if not protocol_path.exists():
            if self.fail_on_missing:
                raise FileNotFoundError(f"Protocol file not found: {protocol_path}")
            self.logger.debug(f"No genCodeDesc file found at {protocol_path}; treating revision {revision_id} as human/unattributed")
            return {}
        protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
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
        if protocol_repo_branch and protocol_repo_branch != repo_branch:
            raise ValueError(
                f"Metadata repoBranch mismatch for revision {revision_id}: expected {repo_branch}, got {protocol_repo_branch}"
            )

        protocol_revision_id = repository.get("revisionId")
        if protocol_revision_id and protocol_revision_id != revision_id:
            raise ValueError(
                f"Metadata revisionId mismatch for revision {revision_id}: expected {revision_id}, got {protocol_revision_id}"
            )

        return protocol


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repoURL", required=True)
    parser.add_argument("--repoBranch", required=True)
    parser.add_argument("--startTime", required=True)
    parser.add_argument("--endTime", required=True)
    parser.add_argument("--vcsType", default="git")
    parser.add_argument("--model", default="A")
    parser.add_argument("--scope", default="A")
    parser.add_argument("--outputFile")
    parser.add_argument("--outputFormat", default="json")
    parser.add_argument("--metadataSource", default="genCodeDesc")
    parser.add_argument("--genCodeDescSetDir")
    parser.add_argument("--workingDir")
    parser.add_argument("--failOnMissingProtocol", action="store_true")
    parser.add_argument("--includeBreakdown", default="none")
    parser.add_argument("--logLevel", choices=["quiet", "info", "debug"], default="quiet")
    return parser.parse_args()


def run_git(repo_dir: Path, args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_dir,
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout.strip()


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


def resolve_end_revision(repo_dir: Path, branch: str, end_time: str) -> str:
    end_value = parse_day_end(end_time).isoformat()
    revision_id = run_git(repo_dir, ["rev-list", "-1", f"--before={end_value}", branch])
    if not revision_id:
        raise RuntimeError("No revision found at or before endTime")
    return revision_id


def list_source_files(repo_dir: Path, revision_id: str) -> list[str]:
    output = run_git(repo_dir, ["ls-tree", "-r", "--name-only", revision_id])
    files = [line for line in output.splitlines() if Path(line).suffix in SOURCE_EXTENSIONS]
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

    raise ValueError(f"Unsupported metadataSource: {args.metadataSource}. Only 'genCodeDesc' is supported in the current slice.")


def describe_ratio(ratio: int) -> str:
    if ratio == 100:
        return "100%-ai"
    if ratio > 0:
        return f"{ratio}%-ai"
    return "human/unattributed"


def resolve_parent_revision(repo_dir: Path, revision_id: str) -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", f"{revision_id}^"],
        cwd=repo_dir,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def best_effort_transition_hint(
    repo_dir: Path,
    provider: GenCodeDescProvider,
    logger: RuntimeLogger,
    args: argparse.Namespace,
    blame_line: BlameLine,
    current_ratio: int,
    protocols: dict[str, dict],
    parent_revisions: dict[str, str | None],
) -> str | None:
    if logger.level != "debug":
        return None

    parent_revision = parent_revisions.get(blame_line.revision_id)
    if parent_revision is None and blame_line.revision_id not in parent_revisions:
        parent_revision = resolve_parent_revision(repo_dir, blame_line.revision_id)
        parent_revisions[blame_line.revision_id] = parent_revision

    if not parent_revision:
        return None

    parent_protocol = protocols.get(parent_revision)
    if parent_protocol is None:
        parent_protocol = provider.get_revision_metadata(args.repoURL, args.repoBranch, parent_revision, args.vcsType)
        protocols[parent_revision] = parent_protocol

    parent_ratio = line_ratio(parent_protocol, blame_line.origin_file, blame_line.origin_line)
    if parent_ratio == current_ratio:
        return None
    return f"best_effort_transition={describe_ratio(parent_ratio)}->{describe_ratio(current_ratio)}"


def line_ratio(protocol: dict, origin_file: str, origin_line: int) -> int:
    for file_entry in protocol.get("DETAIL", []):
        if file_entry.get("fileName") != origin_file:
            continue
        for code_line in file_entry.get("codeLines", []):
            if code_line.get("lineLocation") == origin_line:
                return int(code_line.get("genRatio", 0))
            line_range = code_line.get("lineRange")
            if line_range and line_range.get("from") <= origin_line <= line_range.get("to"):
                return int(code_line.get("genRatio", 0))
    return 0


def build_result(args: argparse.Namespace) -> dict:
    if args.vcsType != "git":
        raise NotImplementedError("Only git is implemented in the current Git Model A slice")
    if args.model != "A":
        raise NotImplementedError("Only Model A is implemented in the current Git Model A slice")
    if args.scope != "A":
        raise NotImplementedError("Only Scope A is implemented in the current Git Model A slice")
    if args.outputFormat != "json":
        raise NotImplementedError("Only JSON output is implemented in the current Git Model A slice")

    logger = RuntimeLogger(args.logLevel)
    repo_dir = Path(args.workingDir or args.repoURL)
    provider = build_gen_code_desc_provider(args, logger)
    start_bound = parse_day_start(args.startTime)
    end_bound = parse_day_end(args.endTime)
    end_revision_id = resolve_end_revision(repo_dir, args.repoBranch, args.endTime)
    logger.info(
        f"Starting analysis for repo={repo_dir} branch={args.repoBranch} window={args.startTime}..{args.endTime} endRevision={end_revision_id}"
    )

    protocols: dict[str, dict] = {}
    parent_revisions: dict[str, str | None] = {}
    total_code_lines = 0
    full_generated_code_lines = 0
    partial_generated_code_lines = 0

    source_files = list_source_files(repo_dir, end_revision_id)
    logger.debug(f"Resolved {len(source_files)} source files in the end snapshot")

    for relative_path in source_files:
        logger.debug(f"Scanning file {relative_path}")
        for blame_line in parse_blame(repo_dir, end_revision_id, relative_path):
            if not is_code_line(blame_line.content):
                logger.debug(f"Skip non-code line {relative_path}:{blame_line.final_line}")
                continue

            commit_time = parse_git_timestamp(run_git(repo_dir, ["show", "-s", "--format=%cI", blame_line.revision_id]))
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
            else:
                logger.debug(f"Reuse cached genCodeDesc for revision {blame_line.revision_id}")

            ratio = line_ratio(protocol, blame_line.origin_file, blame_line.origin_line)
            transition_hint = best_effort_transition_hint(
                repo_dir,
                provider,
                logger,
                args,
                blame_line,
                ratio,
                protocols,
                parent_revisions,
            )
            line_message = (
                f"LiveLine {relative_path}:{blame_line.final_line} aggregate "
                f"origin={blame_line.origin_file}:{blame_line.origin_line}@{blame_line.revision_id} "
                f"classification={describe_ratio(ratio)}"
            )
            if transition_hint:
                logger.debug(f"{line_message} {transition_hint}")
            logger.info(line_message)

            if ratio == 100:
                full_generated_code_lines += 1
            elif ratio > 0:
                partial_generated_code_lines += 1

    logger.info(
        "Finished analysis with "
        f"totalCodeLines={total_code_lines} fullGeneratedCodeLines={full_generated_code_lines} "
        f"partialGeneratedCodeLines={partial_generated_code_lines}"
    )

    return {
        "protocolName": "generatedTextDesc",
        "protocolVersion": "26.03",
        "SUMMARY": {
            "totalCodeLines": total_code_lines,
            "fullGeneratedCodeLines": full_generated_code_lines,
            "partialGeneratedCodeLines": partial_generated_code_lines,
        },
        "REPOSITORY": {
            "vcsType": args.vcsType,
            "repoURL": str(repo_dir),
            "repoBranch": args.repoBranch,
            "revisionId": end_revision_id,
        },
    }


def main() -> None:
    args = parse_args()
    result = build_result(args)
    output = json.dumps(result, indent=2)
    if args.outputFile:
        Path(args.outputFile).write_text(output, encoding="utf-8")
    else:
        print(output)


if __name__ == "__main__":
    main()