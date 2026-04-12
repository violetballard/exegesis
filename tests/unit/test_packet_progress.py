from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from codex_packet_handoff.tools import agents_coordinator, packet_progress


class PacketProgressTests(unittest.TestCase):
    def test_infer_last_submitted_sha_prefers_planner_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            lane_dir = Path(tmpdir)
            reviewer_dir = lane_dir / "inbox" / "reviewer"
            reviewer_dir.mkdir(parents=True, exist_ok=True)
            (
                reviewer_dir
                / "R__CHANGES__codex-feat-a__1111111111111111111111111111111111111111__20260402T000000Z.md"
            ).write_text("note\n", encoding="utf-8")

            sha = packet_progress.infer_last_submitted_sha(
                lane_dir,
                {"last_submitted_sha": "2222222222222222222222222222222222222222"},
            )

        self.assertEqual(sha, "2222222222222222222222222222222222222222")

    def test_infer_last_submitted_sha_falls_back_to_latest_reviewer_packet(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            lane_dir = Path(tmpdir)
            reviewer_dir = lane_dir / "inbox" / "reviewer"
            reviewer_dir.mkdir(parents=True, exist_ok=True)
            (
                reviewer_dir
                / "R__CHANGES__codex-feat-a__1111111111111111111111111111111111111111__20260402T000000Z.md"
            ).write_text("older\n", encoding="utf-8")
            latest = (
                reviewer_dir
                / "R__CHANGES__codex-feat-a__3333333333333333333333333333333333333333__20260403T000000Z.md"
            )
            latest.write_text("newer\n", encoding="utf-8")

            sha = packet_progress.infer_last_submitted_sha(lane_dir, {})

        self.assertEqual(sha, "3333333333333333333333333333333333333333")


class WorktreeCleanupTests(unittest.TestCase):
    def test_repair_shadow_gitdir_repoints_worktree_and_preserves_backup(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            worktree = Path(tmpdir) / "wt"
            worktree.mkdir()
            shadow = worktree / ".git-local"
            shadow.mkdir()
            (shadow / "HEAD").write_text("ref: refs/heads/codex/feat-a\n", encoding="utf-8")
            (worktree / ".git").write_text(f"gitdir: {shadow}\n", encoding="utf-8")
            shared = Path(tmpdir) / "shared-gitdir"
            shared.mkdir()

            with mock.patch.object(agents_coordinator, "_shared_gitdir_for_worktree", return_value=shared):
                repaired, backup = agents_coordinator._repair_shadow_gitdir(worktree, "feat-a")

            self.assertTrue(repaired)
            self.assertIsNotNone(backup)
            self.assertEqual((worktree / ".git").read_text(encoding="utf-8"), f"gitdir: {shared}\n")
            self.assertTrue(Path(str(backup)).exists())

    def test_prune_generated_worktree_artifacts_removes_git_junk(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            worktree = Path(tmpdir) / "wt"
            (worktree / ".codex" / "packets").mkdir(parents=True, exist_ok=True)
            (worktree / ".git-alt-index").write_text("junk\n", encoding="utf-8")
            (worktree / ".git-local").mkdir()
            (worktree / "worktree-commit.txt").write_text("junk\n", encoding="utf-8")

            removed = agents_coordinator._prune_generated_worktree_artifacts(worktree)

            self.assertIn(".git-alt-index", removed)
            self.assertIn(".git-local", removed)
            self.assertIn("worktree-commit.txt", removed)
            self.assertIn(".codex/packets", removed)
            self.assertFalse((worktree / ".git-alt-index").exists())
            self.assertFalse((worktree / ".git-local").exists())
            self.assertFalse((worktree / ".codex" / "packets").exists())
