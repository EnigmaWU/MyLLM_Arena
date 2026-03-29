import os
import subprocess
import tempfile
import unittest
from pathlib import Path


class GitRepoHarness:
    def __init__(self, repo_dir: Path):
        self.repo_dir = repo_dir
        self.commit_ids: dict[str, str] = {}
        self._run(["git", "init", "-b", "main"])
        self._run(["git", "config", "user.name", "AggregateGenCodeDesc Tests"])
        self._run(["git", "config", "user.email", "tests@example.local"])

    def _run(self, command: list[str], env: dict[str, str] | None = None) -> str:
        merged_env = os.environ.copy()
        if env:
            merged_env.update(env)
        result = subprocess.run(
            command,
            cwd=self.repo_dir,
            env=merged_env,
            text=True,
            capture_output=True,
            check=True,
        )
        return result.stdout.strip()

    def write(self, relative_path: str, content: str) -> None:
        file_path = self.repo_dir / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")

    def delete(self, relative_path: str) -> None:
        file_path = self.repo_dir / relative_path
        if file_path.exists():
            file_path.unlink()

    def rename(self, old_path: str, new_path: str) -> None:
        new_file_path = self.repo_dir / new_path
        new_file_path.parent.mkdir(parents=True, exist_ok=True)
        self._run(["git", "mv", old_path, new_path])

    def commit_all(self, label: str, date: str) -> str:
        env = {
            "GIT_AUTHOR_DATE": date,
            "GIT_COMMITTER_DATE": date,
        }
        self._run(["git", "add", "-A"], env=env)
        self._run(["git", "commit", "-m", label], env=env)
        commit_id = self._run(["git", "rev-parse", "HEAD"])
        self.commit_ids[label] = commit_id
        return commit_id

    def blame_commits(self, relative_path: str) -> list[str]:
        output = self._run(["git", "blame", "--line-porcelain", "HEAD", "--", relative_path])
        commits: list[str] = []
        for line in output.splitlines():
            if line.startswith("\t"):
                continue
            if line.startswith("author ") or line.startswith("summary "):
                continue
            if line.startswith("filename "):
                continue
            if len(line) >= 40 and all(ch in "0123456789abcdef" for ch in line[:40]):
                commits.append(line.split()[0])
        return commits

    def file_lines(self, relative_path: str) -> list[str]:
        return (self.repo_dir / relative_path).read_text(encoding="utf-8").splitlines()


class TestRealGitModelAScenarios(unittest.TestCase):
    def make_repo(self) -> GitRepoHarness:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        return GitRepoHarness(Path(temp_dir.name))

    def test_human_overwrites_ai_resets_blame(self) -> None:
        repo = self.make_repo()
        repo.write("src/case.py", "def calc(x):\n    value = x + 1\n    return value\n")
        repo.commit_all("human-base", "2026-03-01T09:00:00Z")

        repo.write("src/case.py", "def calc(x):\n    value = x * 2\n    return value\n")
        repo.commit_all("ai-rewrite", "2026-03-10T09:00:00Z")

        repo.write("src/case.py", "def calc(x):\n    value = max(x, 0)\n    return value\n")
        repo.commit_all("human-rewrite", "2026-03-20T09:00:00Z")

        commits = repo.blame_commits("src/case.py")
        self.assertEqual(commits[1], repo.commit_ids["human-rewrite"])
        self.assertEqual(commits[2], repo.commit_ids["human-base"])

    def test_ai_overwrites_human_takes_latest_origin(self) -> None:
        repo = self.make_repo()
        repo.write("src/case.py", "def calc(x):\n    value = x + 1\n    return value\n")
        repo.commit_all("human-base", "2026-03-01T09:00:00Z")

        repo.write("src/case.py", "def calc(x):\n    value = x * 2\n    return max(value, 0)\n")
        repo.commit_all("ai-rewrite", "2026-03-15T09:00:00Z")

        commits = repo.blame_commits("src/case.py")
        self.assertEqual(commits[1], repo.commit_ids["ai-rewrite"])
        self.assertEqual(commits[2], repo.commit_ids["ai-rewrite"])

    def test_deleted_lines_do_not_survive_final_snapshot(self) -> None:
        repo = self.make_repo()
        repo.write("src/case.py", "def calc(x):\n    first = x + 1\n    second = x * 2\n    return first + second\n")
        repo.commit_all("ai-lines", "2026-03-05T09:00:00Z")

        repo.write("src/case.py", "def calc(x):\n    first = x + 1\n    return first\n")
        repo.commit_all("delete-line", "2026-03-18T09:00:00Z")

        self.assertEqual(
            repo.file_lines("src/case.py"),
            ["def calc(x):", "    first = x + 1", "    return first"],
        )
        self.assertEqual(len(repo.blame_commits("src/case.py")), 3)

    def test_rename_preserves_lineage_under_git_blame(self) -> None:
        repo = self.make_repo()
        repo.write("src/old_name.py", "def calc(x):\n    value = x * 2\n    return value\n")
        repo.commit_all("ai-base", "2026-03-08T09:00:00Z")

        repo.rename("src/old_name.py", "src/new_name.py")
        repo.commit_all("rename-only", "2026-03-12T09:00:00Z")

        commits = repo.blame_commits("src/new_name.py")
        self.assertEqual(commits[1], repo.commit_ids["ai-base"])
        self.assertEqual(commits[2], repo.commit_ids["ai-base"])

    def test_merge_commit_keeps_effective_line_origin(self) -> None:
        repo = self.make_repo()
        repo.write(
            "src/merge_case.py",
            "def calc(x):\n    base = x\n    spacer = x\n    value = x + 1\n    return base + value + spacer\n",
        )
        repo.commit_all("base", "2026-03-01T09:00:00Z")

        repo._run(["git", "checkout", "-b", "feature-ai"])
        repo.write(
            "src/merge_case.py",
            "def calc(x):\n    base = x\n    spacer = x\n    value = x * 2\n    return base + value + spacer\n",
        )
        repo.commit_all("feature-ai", "2026-03-10T09:00:00Z")

        repo._run(["git", "checkout", "main"])
        repo.write(
            "src/merge_case.py",
            "def calc(x):\n    base = max(x, 0)\n    spacer = x\n    value = x + 1\n    return base + value + spacer\n",
        )
        repo.commit_all("main-human", "2026-03-12T09:00:00Z")

        repo._run(["git", "merge", "--no-ff", "feature-ai", "-m", "merge-feature"], env={
            "GIT_AUTHOR_DATE": "2026-03-20T09:00:00Z",
            "GIT_COMMITTER_DATE": "2026-03-20T09:00:00Z",
        })
        repo.commit_ids["merge-feature"] = repo._run(["git", "rev-parse", "HEAD"])

        commits = repo.blame_commits("src/merge_case.py")
        self.assertEqual(commits[1], repo.commit_ids["main-human"])
        self.assertEqual(commits[3], repo.commit_ids["feature-ai"])
        self.assertEqual(commits[2], repo.commit_ids["base"])
        self.assertEqual(commits[4], repo.commit_ids["base"])
        self.assertNotEqual(commits[1], repo.commit_ids["merge-feature"])
        self.assertNotEqual(commits[3], repo.commit_ids["merge-feature"])


if __name__ == "__main__":
    unittest.main()
