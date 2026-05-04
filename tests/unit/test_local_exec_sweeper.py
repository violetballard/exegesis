from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from codex_packet_handoff.tools import local_exec_sweeper


class LocalExecSweeperTests(unittest.TestCase):
    def test_find_orphaned_repo_local_exec_pids_filters_by_repo_prompt_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            (repo_root / ".codex/feature_runner/prompts").mkdir(parents=True, exist_ok=True)
            owned_prompt = repo_root / ".codex/feature_runner/prompts" / "lane.prompt.md"
            owned_prompt.write_text("prompt", encoding="utf-8")
            foreign_prompt = Path(tmp) / "foreign.prompt.md"
            foreign_prompt.write_text("prompt", encoding="utf-8")
            ps_output = "\n".join(
                [
                    f"101 77 101 /Applications/Codex.app/Contents/Resources/codex --oss --local-provider lmstudio exec --skip-git-repo-check -m gpt-oss-120b -s workspace-write Read and follow the exact instructions in {owned_prompt}. Treat that file as the full user prompt and obey it completely.",
                    "202 77 202 /Applications/Codex.app/Contents/Resources/codex --oss --local-provider lmstudio exec --skip-git-repo-check -m gpt-oss-20b -s workspace-write -",
                    "303 77 303 /Applications/Codex.app/Contents/Resources/codex exec hello",
                ]
            )

            def fake_run(args, **kwargs):
                if args[:2] == ["ps", "-axo"]:
                    return mock.Mock(returncode=0, stdout=ps_output)
                if args[:3] == ["lsof", "-a", "-p"] and args[3] == "101":
                    return mock.Mock(returncode=0, stdout=f"p101\nf0\nn{owned_prompt}\n")
                if args[:3] == ["lsof", "-a", "-p"] and args[3] == "202":
                    return mock.Mock(returncode=0, stdout=f"p202\nf0\nn{foreign_prompt}\n")
                return mock.Mock(returncode=1, stdout="")

            with mock.patch.object(local_exec_sweeper.subprocess, "run", side_effect=fake_run):
                orphaned = local_exec_sweeper.find_orphaned_repo_local_exec_pids(repo_root, tracked_pids=[303])

        self.assertEqual(orphaned, [101])

    def test_find_stale_repo_local_exec_pids_includes_tracked_reparented_jobs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            (repo_root / ".codex/packet_router/logs").mkdir(parents=True, exist_ok=True)
            prompt = repo_root / ".codex/packet_router/logs" / "fixer.prompt.txt"
            prompt.write_text("prompt", encoding="utf-8")
            ps_output = "\n".join(
                [
                    f"101 1 101 /Applications/Codex.app/Contents/Resources/codex --oss --local-provider lmstudio exec --skip-git-repo-check -m gpt-oss-120b -s workspace-write Read and follow the exact instructions in {prompt}.",
                    f"202 77 202 /Applications/Codex.app/Contents/Resources/codex --oss --local-provider lmstudio exec --skip-git-repo-check -m gpt-oss-120b -s workspace-write Read and follow the exact instructions in {prompt}.",
                ]
            )

            def fake_run(args, **kwargs):
                if args[:2] == ["ps", "-axo"]:
                    return mock.Mock(returncode=0, stdout=ps_output)
                if args[:3] == ["lsof", "-a", "-p"]:
                    return mock.Mock(returncode=0, stdout=f"p{args[3]}\nf0\nn{prompt}\n")
                return mock.Mock(returncode=1, stdout="")

            with mock.patch.object(local_exec_sweeper.subprocess, "run", side_effect=fake_run):
                stale = local_exec_sweeper.find_stale_repo_local_exec_pids(repo_root, tracked_pids=[101, 202])

        self.assertEqual(stale, [101])

    def test_find_stale_repo_local_exec_pids_allows_tracked_detached_feature_jobs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            (repo_root / ".codex/feature_runner/logs").mkdir(parents=True, exist_ok=True)
            prompt = repo_root / ".codex/feature_runner/logs" / "feat-commands.prompt.md"
            prompt.write_text("prompt", encoding="utf-8")
            ps_output = (
                "101 1 101 /Applications/Codex.app/Contents/Resources/codex --oss "
                "--local-provider lmstudio exec --skip-git-repo-check -m gpt-oss-120b "
                f"-s workspace-write Read {prompt.resolve()}."
            )

            def fake_run(args, **kwargs):
                if args[:2] == ["ps", "-axo"]:
                    return mock.Mock(returncode=0, stdout=ps_output)
                if args[:3] == ["lsof", "-a", "-p"]:
                    return mock.Mock(returncode=0, stdout=f"p{args[3]}\nf0\nn{prompt}\n")
                return mock.Mock(returncode=1, stdout="")

            with mock.patch.object(local_exec_sweeper.subprocess, "run", side_effect=fake_run):
                stale = local_exec_sweeper.find_stale_repo_local_exec_pids(
                    repo_root,
                    tracked_pids=[101],
                    detached_ok_pids=[101],
                )

        self.assertEqual(stale, [])

    def test_find_stale_repo_local_exec_pids_recognizes_feature_log_prompts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            (repo_root / ".codex/feature_runner/logs").mkdir(parents=True, exist_ok=True)
            prompt = repo_root / ".codex/feature_runner/logs" / "feat-commands.prompt.md"
            prompt.write_text("prompt", encoding="utf-8")
            ps_output = (
                "404 1 404 /Applications/Codex.app/Contents/Resources/codex exec --oss "
                "--local-provider lmstudio --skip-git-repo-check -m gpt-oss-120b "
                f"--add-dir {prompt.parent.resolve()} -s workspace-write Read {prompt.resolve()}."
            )

            def fake_run(args, **kwargs):
                if args[:2] == ["ps", "-axo"]:
                    return mock.Mock(returncode=0, stdout=ps_output)
                if args[:3] == ["lsof", "-a", "-p"]:
                    return mock.Mock(returncode=1, stdout="")
                return mock.Mock(returncode=1, stdout="")

            with mock.patch.object(local_exec_sweeper.subprocess, "run", side_effect=fake_run):
                stale = local_exec_sweeper.find_stale_repo_local_exec_pids(repo_root, tracked_pids=[404])

        self.assertEqual(stale, [404])

    def test_find_stale_repo_local_exec_pids_recognizes_opencode_prompts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            (repo_root / ".codex/feature_runner/logs").mkdir(parents=True, exist_ok=True)
            prompt = repo_root / ".codex/feature_runner/logs" / "feat-commands.prompt.md"
            prompt.write_text("prompt", encoding="utf-8")
            ps_output = (
                "505 1 505 /opt/homebrew/bin/opencode run --model lmstudio/qwen3.6-27b "
                f"--dir {repo_root} --dangerously-skip-permissions Read {prompt.resolve()}."
            )

            def fake_run(args, **kwargs):
                if args[:2] == ["ps", "-axo"]:
                    return mock.Mock(returncode=0, stdout=ps_output)
                if args[:3] == ["lsof", "-a", "-p"]:
                    return mock.Mock(returncode=1, stdout="")
                return mock.Mock(returncode=1, stdout="")

            with mock.patch.object(local_exec_sweeper.subprocess, "run", side_effect=fake_run):
                stale = local_exec_sweeper.find_stale_repo_local_exec_pids(repo_root, tracked_pids=[505])

        self.assertEqual(stale, [505])

    def test_find_stale_repo_test_runner_pids_filters_by_repo_cwd_and_age(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp) / "qual"
            repo_root.mkdir()
            foreign_root = Path(tmp) / "other"
            foreign_root.mkdir()
            ps_output = "\n".join(
                [
                    "101 1 101 40:00 12000 /bin/sh ./quality-test.sh",
                    "202 1 202 01:00 12000 /bin/sh ./quality-test.sh",
                    "303 1 303 45:00 12000 /bin/sh ./quality-test.sh",
                    "404 1 404 02:00 2000000 python -m unittest discover -s tests/unit -p test_*.py -v",
                ]
            )

            def fake_run(args, **kwargs):
                if args[:2] == ["ps", "-axo"]:
                    return mock.Mock(returncode=0, stdout=ps_output)
                if args[:3] == ["lsof", "-a", "-p"] and args[3] == "101":
                    return mock.Mock(returncode=0, stdout=f"p101\nfcwd\nn{repo_root}\n")
                if args[:3] == ["lsof", "-a", "-p"] and args[3] == "202":
                    return mock.Mock(returncode=0, stdout=f"p202\nfcwd\nn{repo_root}\n")
                if args[:3] == ["lsof", "-a", "-p"] and args[3] == "303":
                    return mock.Mock(returncode=0, stdout=f"p303\nfcwd\nn{foreign_root}\n")
                if args[:3] == ["lsof", "-a", "-p"] and args[3] == "404":
                    return mock.Mock(returncode=0, stdout=f"p404\nfcwd\nn{repo_root / 'tests'}\n")
                return mock.Mock(returncode=1, stdout="")

            with (
                mock.patch.object(local_exec_sweeper.subprocess, "run", side_effect=fake_run),
                mock.patch.object(local_exec_sweeper, "ORPHAN_TEST_RUNNER_MIN_AGE_SECONDS", 1800),
                mock.patch.object(local_exec_sweeper, "ORPHAN_TEST_RUNNER_RSS_LIMIT_KB", 1500000),
            ):
                stale = local_exec_sweeper.find_stale_repo_test_runner_pids(repo_root, tracked_pids=[])

        self.assertEqual(stale, [101, 404])

    def test_find_stale_repo_test_runner_pids_accepts_managed_worktree_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp) / "qual"
            repo_root.mkdir()
            worktree_root = Path(tmp) / "worktrees"
            managed_cwd = worktree_root / "feat-retrieval-fts" / "qual"
            managed_cwd.mkdir(parents=True)
            ps_output = "505 1 505 35:00 12000 /bin/sh /tmp/qual/quality-test.sh"

            def fake_run(args, **kwargs):
                if args[:2] == ["ps", "-axo"]:
                    return mock.Mock(returncode=0, stdout=ps_output)
                if args[:3] == ["lsof", "-a", "-p"] and args[3] == "505":
                    return mock.Mock(returncode=0, stdout=f"p505\nfcwd\nn{managed_cwd}\n")
                return mock.Mock(returncode=1, stdout="")

            with (
                mock.patch.object(local_exec_sweeper.subprocess, "run", side_effect=fake_run),
                mock.patch.object(local_exec_sweeper, "MANAGED_WORKTREE_ROOT", worktree_root),
                mock.patch.object(local_exec_sweeper, "ORPHAN_TEST_RUNNER_MIN_AGE_SECONDS", 1800),
            ):
                stale = local_exec_sweeper.find_stale_repo_test_runner_pids(repo_root, tracked_pids=[])

        self.assertEqual(stale, [505])


if __name__ == "__main__":
    unittest.main()
