import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from tests.cli_test_support import SvnRepoHarness, load_json, run_cli, write_revision_protocol
from tests.log_assertions import assert_live_line_log, assert_log_contains_all, assert_log_contains_none


FIXTURE_DIR = Path(__file__).resolve().parent.parent / "testdata" / "us12_many_merged_branches_preserve_attribution"


def _protocol(*, repo_branch: str, file_name: str, full_lines: list[int] | None = None, partial_lines: dict[int, int] | None = None) -> dict:
    full_lines = full_lines or []
    partial_lines = partial_lines or {}
    code_lines = [
        {"lineLocation": line_number, "genRatio": 100, "genMethod": "codeCompletion"}
        for line_number in full_lines
    ]
    code_lines.extend(
        {
            "lineLocation": line_number,
            "genRatio": ratio,
            "genMethod": "vibeCoding",
        }
        for line_number, ratio in sorted(partial_lines.items())
    )
    return {
        "protocolName": "generatedTextDesc",
        "protocolVersion": "26.03",
        "codeAgent": "Us12SvnVariantAgent",
        "SUMMARY": {
            "totalCodeLines": len(full_lines) + len(partial_lines),
            "fullGeneratedCodeLines": len(full_lines),
            "partialGeneratedCodeLines": len(partial_lines),
        },
        "DETAIL": [
            {
                "fileName": file_name,
                "codeLines": code_lines,
            }
        ],
        "REPOSITORY": {
            "vcsType": "svn",
            "repoURL": "https://example.local/repo/us12-svn-variant",
            "repoBranch": repo_branch,
            "revisionId": "placeholder",
        },
    }


@unittest.skipUnless(shutil.which("svn") and shutil.which("svnadmin"), "svn tooling not installed")
class TestUs12ManyMergedBranchesPreserveAttributionSvnTdd(unittest.TestCase):
    maxDiff = None

    def _query(self) -> dict:
        query = load_json(FIXTURE_DIR / "query.json")
        query["vcsType"] = "svn"
        query["repoBranch"] = "trunk"
        return query

    def _run(self, command: list[str]) -> str:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        return result.stdout.strip()

    def _remote_copy_branch(self, repo: SvnRepoHarness, branch_name: str, date: str) -> None:
        result = subprocess.run(
            ["svn", "copy", repo.trunk_url, f"{repo.repo_url}/branches/{branch_name}", "-m", f"copy {branch_name}"],
            check=True,
            capture_output=True,
            text=True,
        )
        committed_line = next(line for line in result.stdout.splitlines() if line.startswith("Committed revision "))
        revision_id = committed_line.removeprefix("Committed revision ").removesuffix(".")
        self._run(["svn", "propset", "--revprop", "-r", revision_id, "svn:date", date, repo.repo_url])

    def _switch_working_trunk(self, repo: SvnRepoHarness, target_url: str) -> None:
        self._run(["svn", "switch", target_url, str(repo.working_copy_dir / "trunk")])

    def _merge_branch_into_trunk(self, repo: SvnRepoHarness, branch_name: str, branch_revision_id: str) -> None:
        self._run(["svn", "update", str(repo.working_copy_dir)])
        self._run(
            [
                "svn",
                "merge",
                "-c",
                branch_revision_id,
                f"{repo.repo_url}/branches/{branch_name}",
                str(repo.working_copy_dir / "trunk"),
            ]
        )

    def _build_history(self, root_dir: Path) -> tuple[SvnRepoHarness, Path, Path, dict[str, str]]:
        repo_dir = root_dir / "repo"
        working_copy_dir = root_dir / "wc"
        protocol_dir = root_dir / "protocols"
        output_file = root_dir / "out.json"
        protocol_dir.mkdir()

        repo = SvnRepoHarness(repo_dir, working_copy_dir)

        (repo.working_copy_dir / "branches").mkdir()
        self._run(["svn", "add", str(repo.working_copy_dir / "branches")])
        repo.commit_all("create branches", "2026-02-25T09:00:00.000000Z")

        baseline_files = {
            "trunk/src/main_human.py": "main_human = base + 1",
            "trunk/src/alpha_branch.py": "alpha_branch = base + 2",
            "trunk/src/beta_branch.py": "beta_branch = base + 3",
            "trunk/src/gamma_branch.py": "gamma_branch = base + 4",
            "trunk/src/delta_branch.py": "delta_branch = base + 5",
            "trunk/src/epsilon_branch.py": "epsilon_branch = base + 6",
            "trunk/src/main_tail.py": "main_tail = base + 8",
        }
        for relative_path, middle_line in baseline_files.items():
            repo.write(
                relative_path,
                "carry_pre_window = base\n"
                f"{middle_line}\n"
                "stable_pre_window = base + 2\n",
            )
            repo.add(relative_path)
        revision_id_r1 = repo.commit_all("us12-svn-r1", "2026-02-24T09:00:00.000000Z")

        repo.write(
            "trunk/src/main_human.py",
            "carry_pre_window = base\n"
            "main_human = sanitize(base + 1)\n"
            "stable_pre_window = base + 2\n",
        )
        revision_id_r2 = repo.commit_all("us12-svn-r2", "2026-03-02T09:00:00.000000Z")

        for offset, branch_name in enumerate(["feature-alpha", "feature-beta", "feature-gamma", "feature-delta", "feature-epsilon"], start=4):
            self._remote_copy_branch(repo, branch_name, f"2026-03-04T{offset:02d}:00:00.000000Z")

        self._switch_working_trunk(repo, f"{repo.repo_url}/branches/feature-alpha")
        repo.write(
            "trunk/src/alpha_branch.py",
            "carry_pre_window = base\n"
            "alpha_branch = helper(base + 2)\n"
            "stable_pre_window = base + 2\n",
        )
        revision_id_r3 = repo.commit_all("us12-svn-r3", "2026-03-05T09:00:00.000000Z")
        self._switch_working_trunk(repo, repo.trunk_url)
        self._merge_branch_into_trunk(repo, "feature-alpha", revision_id_r3)
        repo.commit_all("us12-svn-r4", "2026-03-07T09:00:00.000000Z")

        self._switch_working_trunk(repo, f"{repo.repo_url}/branches/feature-beta")
        repo.write(
            "trunk/src/beta_branch.py",
            "carry_pre_window = base\n"
            "beta_branch = suggest(base + 3)\n"
            "stable_pre_window = base + 2\n",
        )
        revision_id_r5 = repo.commit_all("us12-svn-r5", "2026-03-09T09:00:00.000000Z")
        self._switch_working_trunk(repo, repo.trunk_url)
        self._merge_branch_into_trunk(repo, "feature-beta", revision_id_r5)
        repo.commit_all("us12-svn-r6", "2026-03-11T09:00:00.000000Z")

        self._switch_working_trunk(repo, f"{repo.repo_url}/branches/feature-gamma")
        repo.write(
            "trunk/src/gamma_branch.py",
            "carry_pre_window = base\n"
            "gamma_branch = synthesize(base + 4)\n"
            "stable_pre_window = base + 2\n",
        )
        revision_id_r7 = repo.commit_all("us12-svn-r7", "2026-03-13T09:00:00.000000Z")
        self._switch_working_trunk(repo, repo.trunk_url)

        repo.write(
            "trunk/src/main_tail.py",
            "carry_pre_window = base\n"
            "main_tail = clamp(base + 8)\n"
            "stable_pre_window = base + 2\n",
        )
        revision_id_r8 = repo.commit_all("us12-svn-r8", "2026-03-15T09:00:00.000000Z")
        self._merge_branch_into_trunk(repo, "feature-gamma", revision_id_r7)
        repo.commit_all("us12-svn-r9", "2026-03-17T09:00:00.000000Z")

        self._switch_working_trunk(repo, f"{repo.repo_url}/branches/feature-delta")
        repo.write(
            "trunk/src/delta_branch.py",
            "carry_pre_window = base\n"
            "delta_branch = blend(base + 5)\n"
            "stable_pre_window = base + 2\n",
        )
        revision_id_r10 = repo.commit_all("us12-svn-r10", "2026-03-19T09:00:00.000000Z")
        self._switch_working_trunk(repo, repo.trunk_url)
        self._merge_branch_into_trunk(repo, "feature-delta", revision_id_r10)
        repo.commit_all("us12-svn-r11", "2026-03-20T09:00:00.000000Z")

        self._switch_working_trunk(repo, f"{repo.repo_url}/branches/feature-epsilon")
        repo.write(
            "trunk/src/epsilon_branch.py",
            "carry_pre_window = base\n"
            "epsilon_branch = complete(base + 6)\n"
            "stable_pre_window = base + 2\n",
        )
        revision_id_r12 = repo.commit_all("us12-svn-r12", "2026-03-21T09:00:00.000000Z")
        self._switch_working_trunk(repo, repo.trunk_url)
        self._merge_branch_into_trunk(repo, "feature-epsilon", revision_id_r12)
        repo.commit_all("us12-svn-r13", "2026-03-22T09:00:00.000000Z")

        repo.write(
            "trunk/src/epsilon_branch.py",
            "carry_pre_window = base\n"
            "epsilon_branch = manual_override(base + 6)\n"
            "stable_pre_window = base + 2\n",
        )
        revision_id_r14 = repo.commit_all("us12-svn-r14", "2026-03-23T09:00:00.000000Z")

        repo.write("trunk/README.md", "us12 docs update\n")
        repo.add("trunk/README.md")
        revision_id_r15 = repo.commit_all("us12-svn-r15", "2026-03-25T09:00:00.000000Z")

        write_revision_protocol(protocol_dir, _protocol(repo_branch="trunk", file_name="trunk/src/main_human.py"), repo.repo_dir, revision_id_r1, repo_url_override=repo.repo_url)
        write_revision_protocol(protocol_dir, _protocol(repo_branch="trunk", file_name="trunk/src/main_human.py"), repo.repo_dir, revision_id_r2, repo_url_override=repo.repo_url)
        write_revision_protocol(protocol_dir, _protocol(repo_branch="branches/feature-alpha", file_name="branches/feature-alpha/src/alpha_branch.py", full_lines=[2]), repo.repo_dir, revision_id_r3, repo_url_override=repo.repo_url)
        write_revision_protocol(protocol_dir, _protocol(repo_branch="branches/feature-beta", file_name="branches/feature-beta/src/beta_branch.py", partial_lines={2: 70}), repo.repo_dir, revision_id_r5, repo_url_override=repo.repo_url)
        write_revision_protocol(protocol_dir, _protocol(repo_branch="branches/feature-gamma", file_name="branches/feature-gamma/src/gamma_branch.py", full_lines=[2]), repo.repo_dir, revision_id_r7, repo_url_override=repo.repo_url)
        write_revision_protocol(protocol_dir, _protocol(repo_branch="trunk", file_name="trunk/src/main_tail.py"), repo.repo_dir, revision_id_r8, repo_url_override=repo.repo_url)
        write_revision_protocol(protocol_dir, _protocol(repo_branch="branches/feature-delta", file_name="branches/feature-delta/src/delta_branch.py", partial_lines={2: 40}), repo.repo_dir, revision_id_r10, repo_url_override=repo.repo_url)
        write_revision_protocol(protocol_dir, _protocol(repo_branch="branches/feature-epsilon", file_name="branches/feature-epsilon/src/epsilon_branch.py", full_lines=[2]), repo.repo_dir, revision_id_r12, repo_url_override=repo.repo_url)
        write_revision_protocol(protocol_dir, _protocol(repo_branch="trunk", file_name="trunk/src/epsilon_branch.py"), repo.repo_dir, revision_id_r14, repo_url_override=repo.repo_url)

        return repo, protocol_dir, output_file, {
            "r2": revision_id_r2,
            "r3": revision_id_r3,
            "r5": revision_id_r5,
            "r7": revision_id_r7,
            "r8": revision_id_r8,
            "r10": revision_id_r10,
            "r14": revision_id_r14,
            "r15": revision_id_r15,
        }

    def test_cli_matches_us12_expected_result_with_many_merged_branches(self) -> None:
        query = self._query()
        expected_result = load_json(FIXTURE_DIR / "expected_result.json")

        with tempfile.TemporaryDirectory() as temp_dir:
            repo, protocol_dir, output_file, revision_ids = self._build_history(Path(temp_dir))

            run_cli(repo.repo_dir, output_file, protocol_dir, query, repo_url_override=repo.repo_url)

            actual_result = json.loads(output_file.read_text(encoding="utf-8"))
            expected_result["REPOSITORY"]["vcsType"] = "svn"
            expected_result["REPOSITORY"]["repoURL"] = repo.repo_url
            expected_result["REPOSITORY"]["repoBranch"] = "trunk"
            expected_result["REPOSITORY"]["revisionId"] = revision_ids["r15"]

            self.assertEqual(actual_result, expected_result)

    def test_cli_emits_debug_logs_for_us12_branch_heavy_history(self) -> None:
        query = self._query()

        with tempfile.TemporaryDirectory() as temp_dir:
            repo, protocol_dir, output_file, revision_ids = self._build_history(Path(temp_dir))

            result = run_cli(
                repo.repo_dir,
                output_file,
                protocol_dir,
                query,
                extra_args=["--logLevel", "debug"],
                repo_url_override=repo.repo_url,
            )

            assert_log_contains_all(
                self,
                result.stderr,
                [
                    "Starting analysis",
                    "Finished analysis with totalCodeLines=7 fullGeneratedCodeLines=2 partialGeneratedCodeLines=2",
                    "Metadata repoBranch differs",
                    "Skip out-of-window line src/main_human.py:1",
                    "Skip out-of-window line src/alpha_branch.py:1",
                    "Skip out-of-window line src/main_tail.py:3",
                ],
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/main_human.py",
                final_line=2,
                origin_file="trunk/src/main_human.py",
                origin_line=2,
                revision_id=revision_ids["r2"],
                classification="human/unattributed",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/alpha_branch.py",
                final_line=2,
                origin_file="branches/feature-alpha/src/alpha_branch.py",
                origin_line=2,
                revision_id=revision_ids["r3"],
                classification="100%-ai",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/beta_branch.py",
                final_line=2,
                origin_file="branches/feature-beta/src/beta_branch.py",
                origin_line=2,
                revision_id=revision_ids["r5"],
                classification="70%-ai",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/gamma_branch.py",
                final_line=2,
                origin_file="branches/feature-gamma/src/gamma_branch.py",
                origin_line=2,
                revision_id=revision_ids["r7"],
                classification="100%-ai",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/delta_branch.py",
                final_line=2,
                origin_file="branches/feature-delta/src/delta_branch.py",
                origin_line=2,
                revision_id=revision_ids["r10"],
                classification="40%-ai",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/epsilon_branch.py",
                final_line=2,
                origin_file="trunk/src/epsilon_branch.py",
                origin_line=2,
                revision_id=revision_ids["r14"],
                classification="human/unattributed",
            )
            assert_live_line_log(
                self,
                result.stderr,
                relative_path="src/main_tail.py",
                final_line=2,
                origin_file="trunk/src/main_tail.py",
                origin_line=2,
                revision_id=revision_ids["r8"],
                classification="human/unattributed",
            )
            assert_log_contains_none(
                self,
                result.stderr,
                [
                    "LiveLine src/main_human.py:1 aggregate",
                    "LiveLine src/alpha_branch.py:1 aggregate",
                ],
            )

    def test_cli_info_logging_focuses_on_live_line_aggregation_progress_for_us12(self) -> None:
        query = self._query()

        with tempfile.TemporaryDirectory() as temp_dir:
            repo, protocol_dir, output_file, _revision_ids = self._build_history(Path(temp_dir))

            result = run_cli(
                repo.repo_dir,
                output_file,
                protocol_dir,
                query,
                extra_args=["--logLevel", "info"],
                repo_url_override=repo.repo_url,
            )

            assert_log_contains_all(
                self,
                result.stderr,
                [
                    "Starting analysis",
                    "LiveLine src/main_human.py:2 aggregate",
                    "LiveLine src/alpha_branch.py:2 aggregate",
                    "LiveLine src/beta_branch.py:2 aggregate",
                    "LiveLine src/gamma_branch.py:2 aggregate",
                    "LiveLine src/delta_branch.py:2 aggregate",
                    "LiveLine src/epsilon_branch.py:2 aggregate",
                    "LiveLine src/main_tail.py:2 aggregate",
                ],
            )
            assert_log_contains_none(
                self,
                result.stderr,
                [
                    "Loaded genCodeDesc for revision",
                    "best_effort_transition=",
                ],
            )


if __name__ == "__main__":
    unittest.main()