from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from packet_garden.tools.git_ops import (
    commit_paths_via_fast_import,
    commit_tracked_changes_via_fast_import,
    run_git,
)


class GitOpsTests(unittest.TestCase):
    def test_run_git_returns_output(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            result = run_git(["rev-parse", "--is-inside-work-tree"], cwd=repo, timeout=5.0)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout.strip(), "true")

    def test_commit_paths_via_fast_import_commits_selected_paths(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
            (repo / "one.txt").write_text("one\n")
            subprocess.run(["git", "add", "one.txt"], cwd=repo, check=True)
            subprocess.run(["git", "commit", "-m", "initial"], cwd=repo, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            (repo / "one.txt").write_text("two\n")
            (repo / "tool.sh").write_text("#!/bin/sh\necho ok\n")
            (repo / "tool.sh").chmod(0o755)
            commit_sha = commit_paths_via_fast_import(
                repo,
                message="control repo update",
                paths=["one.txt", "tool.sh"],
            )
            self.assertEqual(subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip(), commit_sha)
            tree = subprocess.check_output(["git", "ls-tree", "HEAD"], cwd=repo, text=True)
            self.assertIn("100644 blob", tree)
            self.assertIn("one.txt", tree)
            self.assertIn("100755 blob", tree)
            self.assertIn("tool.sh", tree)

    def test_commit_paths_via_fast_import_targets_current_branch_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
            (repo / "one.txt").write_text("one\n")
            subprocess.run(["git", "add", "one.txt"], cwd=repo, check=True)
            subprocess.run(["git", "commit", "-m", "initial"], cwd=repo, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["git", "checkout", "-b", "codex/test-lane"], cwd=repo, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            (repo / "one.txt").write_text("lane\n")

            commit_sha = commit_paths_via_fast_import(
                repo,
                message="lane update",
                paths=["one.txt"],
            )

            self.assertEqual(
                subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip(),
                commit_sha,
            )
            self.assertEqual(
                subprocess.check_output(["git", "rev-parse", "codex/test-lane"], cwd=repo, text=True).strip(),
                commit_sha,
            )
            self.assertNotEqual(
                subprocess.check_output(["git", "rev-parse", "main"], cwd=repo, text=True).strip(),
                commit_sha,
            )

    def test_commit_tracked_changes_via_fast_import_handles_deletes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
            (repo / "keep.txt").write_text("one\n")
            (repo / "gone.txt").write_text("gone\n")
            subprocess.run(["git", "add", "keep.txt", "gone.txt"], cwd=repo, check=True)
            subprocess.run(["git", "commit", "-m", "initial"], cwd=repo, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            (repo / "keep.txt").write_text("two\n")
            (repo / "gone.txt").unlink()

            commit_sha = commit_tracked_changes_via_fast_import(repo, message="update tracked files")

            self.assertEqual(subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip(), commit_sha)
            tree = subprocess.check_output(["git", "ls-tree", "HEAD"], cwd=repo, text=True)
            self.assertIn("keep.txt", tree)
            self.assertNotIn("gone.txt", tree)


if __name__ == "__main__":
    unittest.main()
