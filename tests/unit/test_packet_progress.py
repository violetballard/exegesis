from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from packet_garden.tools import agents_coordinator, packet_progress


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

    def test_infer_last_gate_results_recovers_from_latest_feature_packet(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            lane_dir = Path(tmpdir)
            feature_dir = lane_dir / "archive"
            feature_dir.mkdir(parents=True, exist_ok=True)
            packet = (
                feature_dir
                / "F__codex-feat-a__3333333333333333333333333333333333333333__20260403T000000Z.md"
            )
            packet.write_text(
                "\n".join(
                    [
                        "# Feature → Review Packet",
                        "",
                        "## Commands run and outcomes",
                        "- `make scope-check`: PASS",
                        "- `./quality-test.sh`: FAIL (1)",
                        "",
                        "## Risks / blockers",
                        "- Risk: `MEDIUM`",
                    ]
                ),
                encoding="utf-8",
            )

            gate_results = packet_progress.infer_last_gate_results(
                lane_dir,
                {},
                sha="3333333333333333333333333333333333333333",
            )

        self.assertEqual(
            gate_results,
            [("make scope-check", 0), ("./quality-test.sh", 1)],
        )

    def test_infer_last_changed_files_recovers_from_latest_feature_packet(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            lane_dir = Path(tmpdir)
            feature_dir = lane_dir / "archive"
            feature_dir.mkdir(parents=True, exist_ok=True)
            packet = (
                feature_dir
                / "F__codex-feat-a__3333333333333333333333333333333333333333__20260403T000000Z.md"
            )
            packet.write_text(
                "\n".join(
                    [
                        "# Feature → Review Packet",
                        "",
                        "## Files changed",
                        "- `THREAD_PACKET.md`",
                        "- `.codex/lane_meta/feat-a.json`",
                        "",
                        "## Commands run and outcomes",
                        "- `make scope-check`: PASS",
                    ]
                ),
                encoding="utf-8",
            )

            changed_files = packet_progress.infer_last_changed_files(
                lane_dir,
                {},
                sha="3333333333333333333333333333333333333333",
            )

        self.assertEqual(
            changed_files,
            ["THREAD_PACKET.md", ".codex/lane_meta/feat-a.json"],
        )

    def test_infer_last_changed_files_reads_reviewed_and_metadata_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            lane_dir = Path(tmpdir)
            feature_dir = lane_dir / "archive"
            feature_dir.mkdir(parents=True, exist_ok=True)
            packet = (
                feature_dir
                / "F__codex-feat-a__4444444444444444444444444444444444444444__20260403T010000Z.md"
            )
            packet.write_text(
                "\n".join(
                    [
                        "# Feature → Review Packet",
                        "",
                        "## Files changed",
                        "### Reviewed implementation files",
                        "- `src/qual/retrieval/service.py`",
                        "- `tests/unit/test_unified_retrieval.py`",
                        "### Metadata-only handoff files",
                        "- `THREAD_PACKET.md`",
                        "",
                        "## Commands run and outcomes",
                        "- `make scope-check`: PASS",
                    ]
                ),
                encoding="utf-8",
            )

            changed_files = packet_progress.infer_last_changed_files(
                lane_dir,
                {},
                sha="4444444444444444444444444444444444444444",
            )

        self.assertEqual(
            changed_files,
            [
                "src/qual/retrieval/service.py",
                "tests/unit/test_unified_retrieval.py",
                "THREAD_PACKET.md",
            ],
        )


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
