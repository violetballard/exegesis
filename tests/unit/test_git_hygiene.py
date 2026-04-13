from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from codex_packet_handoff.tools import git_hygiene


class GitHygieneTests(unittest.TestCase):
    def test_parse_etime_seconds(self) -> None:
        self.assertEqual(git_hygiene.parse_etime_seconds("59"), 59)
        self.assertEqual(git_hygiene.parse_etime_seconds("05:04"), 304)
        self.assertEqual(git_hygiene.parse_etime_seconds("01:02:03"), 3723)
        self.assertEqual(git_hygiene.parse_etime_seconds("2-03:04:05"), 183845)

    def test_find_stale_git_helpers_filters_old_plumbing(self) -> None:
        ps_output = "\n".join(
            [
                "100 1 00:30 /Library/Developer/CommandLineTools/usr/bin/git status --short",
                "101 1 10:00 /Library/Developer/CommandLineTools/usr/bin/git write-tree",
                "102 1 06:00 /Library/Developer/CommandLineTools/usr/bin/git read-tree refs/heads/main",
                "103 1 04:59 /Library/Developer/CommandLineTools/usr/bin/git commit -m test",
                "104 1 20:00 /Library/Developer/CommandLineTools/usr/bin/git diff --name-only HEAD",
                "105 99 20:00 /Library/Developer/CommandLineTools/usr/bin/git diff --name-only HEAD",
            ]
        )
        stale = git_hygiene.find_stale_git_helpers(ps_output, min_age_seconds=300)
        self.assertEqual([proc.pid for proc in stale], [101, 102, 104])

    def test_parse_worktree_porcelain_and_stale_selection(self) -> None:
        text = "\n".join(
            [
                "worktree /Users/example/repo",
                "HEAD deadbeef",
                "branch refs/heads/main",
                "",
                "worktree /private/tmp/ctx-clean-1234",
                "HEAD abcdef01",
                "detached",
                "",
                "worktree /private/tmp/qual-feat-context-storage-fix",
                "HEAD abcdef02",
                "detached",
                "locked initializing",
                "",
                "worktree /private/tmp/not-ours",
                "HEAD abcdef03",
                "detached",
                "",
            ]
        )
        entries = git_hygiene.parse_worktree_porcelain(text)
        stale = [entry.path for entry in entries if git_hygiene.is_stale_temp_worktree(entry)]
        self.assertEqual(
            stale,
            [
                "/private/tmp/ctx-clean-1234",
                "/private/tmp/qual-feat-context-storage-fix",
            ],
        )

    def test_find_metadata_dir_matches_gitdir_target(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td) / "repo"
            worktree = Path(td) / "wt"
            meta = repo / ".git" / "worktrees" / "ctxsqual"
            meta.mkdir(parents=True)
            worktree.mkdir(parents=True)
            (meta / "gitdir").write_text(str(worktree / ".git"))
            found = git_hygiene._find_metadata_dir(repo, worktree)
            self.assertEqual(found, meta)


if __name__ == "__main__":
    unittest.main()
