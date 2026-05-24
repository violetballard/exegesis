from __future__ import annotations

import json
import tempfile
import time
import unittest
from types import SimpleNamespace
from pathlib import Path
from unittest.mock import patch


class CoordinatorRebootResumeTests(unittest.TestCase):
    def test_lane_queue_empty_ignores_shared_feature_packets(self) -> None:
        from packet_garden.tools import agents_coordinator as coordinator

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            feature_dir = root / ".codex/packets/lanes/feat-retrieval-fts/inbox/feature"
            feature_dir.mkdir(parents=True)
            (feature_dir / "F__codex-feat-retrieval-fts__abc123__20260517T000000Z.shared.md").write_text(
                "# shared packet\n",
                encoding="utf-8",
            )

            with patch.object(coordinator, "REPO_ROOT", root):
                self.assertTrue(coordinator._lane_queue_empty("feat-retrieval-fts"))

            (feature_dir / "F__codex-feat-retrieval-fts__def456__20260517T000001Z.md").write_text(
                "# actionable packet\n",
                encoding="utf-8",
            )

            with patch.object(coordinator, "REPO_ROOT", root):
                self.assertFalse(coordinator._lane_queue_empty("feat-retrieval-fts"))

    def test_reconcile_marks_pruned_direct_exec_lane_for_forced_resume(self) -> None:
        from packet_garden.tools import agents_coordinator as coordinator

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            feature_state = root / "feature_runner_state.json"
            router_state = root / "router_state.json"
            feature_state.write_text(
                json.dumps(
                    {
                        "lanes": {
                            "feat-commands": {"status": "direct_exec_running", "pid": 4242},
                        }
                    }
                ),
                encoding="utf-8",
            )
            router_state.write_text(json.dumps({}), encoding="utf-8")
            coordinator_state = {"lane_refill": {}}

            with (
                patch.object(coordinator, "FEATURE_RUNNER_STATE_FILE", feature_state),
                patch.object(coordinator, "ROUTER_STATE_FILE", router_state),
                patch.object(coordinator, "_pid_alive", return_value=False),
                patch.object(coordinator, "_lane_head_advanced_since_handoff", return_value=False),
                patch.object(coordinator, "_lane_scope_violations", return_value=[]),
                patch.object(coordinator, "_reconcile_lane_worktrees", return_value={
                    "gitdir_repaired": [],
                    "gitdir_backups": [],
                    "artifacts_removed": {},
                    "health_failures": {},
                    "rebuilt": {},
                    "rebuild_backups": {},
                    "rebuild_failures": {},
                }),
                patch.object(coordinator, "run_hygiene", return_value={
                    "stale_git_pids": [],
                    "temp_worktrees_removed": [],
                    "stale_commit_locks_removed": [],
                    "stale_worktree_index_locks_removed": [],
                }),
                patch.object(coordinator, "find_stale_repo_local_exec_pids", return_value=[]),
                patch.object(coordinator, "find_stale_repo_test_runner_pids", return_value=[]),
                patch.object(coordinator, "_reconcile_duplicate_feature_exec_processes", return_value={}),
            ):
                summary = coordinator._reconcile_control_plane_state(coordinator_state)

        self.assertEqual(summary["feature_runner_removed"], ["feat-commands"])
        self.assertTrue(coordinator_state["lane_refill"]["feat-commands"]["force_resume_once"])
        self.assertEqual(
            coordinator_state["lane_refill"]["feat-commands"]["force_resume_reason"],
            "stale_direct_exec_pruned",
        )

    def test_reconcile_holds_scope_invalid_feature_lane_without_forced_resume(self) -> None:
        from packet_garden.tools import agents_coordinator as coordinator

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            feature_state = root / "feature_runner_state.json"
            router_state = root / "router_state.json"
            feature_state.write_text(
                json.dumps(
                    {
                        "lanes": {
                            "feat-context-storage": {"status": "direct_exec_running", "pid": 4242},
                        }
                    }
                ),
                encoding="utf-8",
            )
            router_state.write_text(json.dumps({}), encoding="utf-8")
            coordinator_state = {"lane_refill": {}}

            with (
                patch.object(coordinator, "FEATURE_RUNNER_STATE_FILE", feature_state),
                patch.object(coordinator, "ROUTER_STATE_FILE", router_state),
                patch.object(coordinator, "_pid_alive", return_value=True),
                patch.object(coordinator, "_terminate_pid_tree") as terminate_mock,
                patch.object(
                    coordinator,
                    "_lane_scope_violations",
                    return_value=["src/qual/retrieval/service.py"],
                ),
                patch.object(coordinator, "_auto_revert_scope_violations", return_value=(False, "restore_failed")),
                patch.object(coordinator, "_reconcile_lane_worktrees", return_value={
                    "gitdir_repaired": [],
                    "gitdir_backups": [],
                    "artifacts_removed": {},
                    "health_failures": {},
                    "rebuilt": {},
                    "rebuild_backups": {},
                    "rebuild_failures": {},
                }),
                patch.object(coordinator, "run_hygiene", return_value={
                    "stale_git_pids": [],
                    "temp_worktrees_removed": [],
                    "stale_commit_locks_removed": [],
                    "stale_worktree_index_locks_removed": [],
                }),
                patch.object(coordinator, "find_stale_repo_local_exec_pids", return_value=[]),
                patch.object(coordinator, "find_stale_repo_test_runner_pids", return_value=[]),
                patch.object(coordinator, "_reconcile_duplicate_feature_exec_processes", return_value={}),
            ):
                summary = coordinator._reconcile_control_plane_state(coordinator_state)

        terminate_mock.assert_called_once_with(4242)
        self.assertEqual(summary["feature_runner_removed"], ["feat-context-storage"])
        self.assertEqual(summary["feature_runner_scope_invalid"], {"feat-context-storage": 1})
        lane_state = coordinator_state["lane_refill"]["feat-context-storage"]
        self.assertFalse(lane_state["force_resume_once"])
        self.assertEqual(lane_state["force_resume_reason"], "full_branch_scope_violation")

    def test_reconcile_auto_reverts_scope_invalid_feature_lane_and_resumes(self) -> None:
        from packet_garden.tools import agents_coordinator as coordinator

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            feature_state = root / "feature_runner_state.json"
            router_state = root / "router_state.json"
            feature_state.write_text(
                json.dumps({"lanes": {"feat-context-storage": {"status": "direct_exec_running", "pid": 4242}}}),
                encoding="utf-8",
            )
            router_state.write_text(json.dumps({}), encoding="utf-8")
            coordinator_state = {"lane_refill": {}}

            with (
                patch.object(coordinator, "FEATURE_RUNNER_STATE_FILE", feature_state),
                patch.object(coordinator, "ROUTER_STATE_FILE", router_state),
                patch.object(coordinator, "_pid_alive", return_value=True),
                patch.object(coordinator, "_terminate_pid_tree") as terminate_mock,
                patch.object(coordinator, "_lane_scope_violations", return_value=["THREAD_PACKET.md"]),
                patch.object(coordinator, "_auto_revert_scope_violations", return_value=(True, "auto_reverted")),
                patch.object(coordinator, "_reconcile_lane_worktrees", return_value={
                    "gitdir_repaired": [],
                    "gitdir_backups": [],
                    "artifacts_removed": {},
                    "health_failures": {},
                    "rebuilt": {},
                    "rebuild_backups": {},
                    "rebuild_failures": {},
                }),
                patch.object(coordinator, "run_hygiene", return_value={
                    "stale_git_pids": [],
                    "temp_worktrees_removed": [],
                    "stale_commit_locks_removed": [],
                    "stale_worktree_index_locks_removed": [],
                }),
                patch.object(coordinator, "find_stale_repo_local_exec_pids", return_value=[]),
                patch.object(coordinator, "find_stale_repo_test_runner_pids", return_value=[]),
                patch.object(coordinator, "_reconcile_duplicate_feature_exec_processes", return_value={}),
            ):
                summary = coordinator._reconcile_control_plane_state(coordinator_state)

        terminate_mock.assert_called_once_with(4242)
        self.assertEqual(summary["feature_runner_scope_invalid"], {})
        self.assertEqual(summary["feature_runner_scope_auto_reverted"], {"feat-context-storage": "auto_reverted"})
        lane_state = coordinator_state["lane_refill"]["feat-context-storage"]
        self.assertTrue(lane_state["force_resume_once"])
        self.assertEqual(lane_state["force_resume_reason"], "full_branch_scope_violation_auto_reverted")

    def test_lane_scope_violations_include_dirty_worktree_changes(self) -> None:
        from packet_garden.tools import agents_coordinator as coordinator

        with (
            patch.object(coordinator, "_lane_branch_map", return_value={"feat-commands": "codex/feat-commands"}),
            patch.object(
                coordinator,
                "_branch_changed_files",
                return_value=["src/qual/commands/catalog.py"],
            ),
            patch.object(
                coordinator,
                "_lane_worktree_changed_files",
                return_value=[
                    "src/qual/commands/dirty_owned.py",
                    ".codex/packet_planner/state.json",
                    "packet_garden/tools/agents_coordinator.py",
                ],
            ),
        ):
            violations = coordinator._lane_scope_violations("feat-commands")

        self.assertEqual(
            violations,
            [".codex/packet_planner/state.json", "packet_garden/tools/agents_coordinator.py"],
        )

    def test_launch_free_lanes_bypasses_cooldown_for_forced_resume(self) -> None:
        from packet_garden.tools import agents_coordinator as coordinator

        commands: list[list[str]] = []

        def fake_run_cmd(cmd: list[str]) -> tuple[int, str]:
            commands.append(cmd)
            return 0, ""

        state_doc = {
            "lane_refill": {
                "feat-commands": {
                    "queue_empty": True,
                    "last_launch_attempt_ts": time.time(),
                    "force_resume_once": True,
                    "force_resume_reason": "stale_direct_exec_pruned",
                }
            }
        }

        with (
            patch.object(coordinator, "_enabled_lanes", return_value=["feat-commands"]),
            patch.object(coordinator, "_lane_queue_empty", return_value=True),
            patch.object(coordinator, "_lane_has_active_feature_session", return_value=False),
            patch.object(coordinator, "_lane_has_current_head_integrated", return_value=False),
            patch.object(coordinator, "_lane_scope_violations", return_value=[]),
            patch.object(coordinator, "_local_lms_feature_launch_slots", return_value=1),
            patch.object(coordinator, "_has_router_priority_backlog", return_value=False),
            patch.object(coordinator, "run_cmd", side_effect=fake_run_cmd),
        ):
            launched = coordinator._launch_free_lanes(state_doc)

        self.assertEqual(launched, ["feat-commands"])
        self.assertEqual(commands[0][-2:], ["--lanes", "feat-commands"])
        lane_state = state_doc["lane_refill"]["feat-commands"]
        self.assertEqual(lane_state["last_launch_reason"], "stale_direct_exec_resume")
        self.assertNotIn("force_resume_once", lane_state)

    def test_launch_free_lanes_clears_forced_resume_when_lane_already_active(self) -> None:
        from packet_garden.tools import agents_coordinator as coordinator

        state_doc = {
            "lane_refill": {
                "feat-commands": {
                    "queue_empty": True,
                    "force_resume_once": True,
                    "force_resume_reason": "stale_direct_exec_pruned",
                }
            }
        }

        with (
            patch.object(coordinator, "_enabled_lanes", return_value=["feat-commands"]),
            patch.object(coordinator, "_lane_queue_empty", return_value=True),
            patch.object(coordinator, "_lane_has_active_feature_session", return_value=True),
            patch.object(coordinator, "_lane_scope_violations", return_value=[]),
            patch.object(coordinator, "run_cmd") as run_cmd,
        ):
            launched = coordinator._launch_free_lanes(state_doc)

        self.assertEqual(launched, [])
        run_cmd.assert_not_called()
        lane_state = state_doc["lane_refill"]["feat-commands"]
        self.assertNotIn("force_resume_once", lane_state)
        self.assertIn("force_resume_cleared_at", lane_state)

    def test_launch_free_lanes_does_not_resume_scope_invalid_branch(self) -> None:
        from packet_garden.tools import agents_coordinator as coordinator

        state_doc = {
            "lane_refill": {
                "feat-context-storage": {
                    "queue_empty": True,
                    "force_resume_once": True,
                    "force_resume_reason": "stale_direct_exec_pruned",
                }
            }
        }

        with (
            patch.object(coordinator, "_enabled_lanes", return_value=["feat-context-storage"]),
            patch.object(coordinator, "_lane_queue_empty", return_value=True),
            patch.object(coordinator, "_lane_has_active_feature_session", return_value=False),
            patch.object(
                coordinator,
                "_lane_scope_violations",
                return_value=["src/qual/retrieval/service.py"],
            ),
            patch.object(coordinator, "_auto_revert_scope_violations", return_value=(False, "restore_failed")),
            patch.object(coordinator, "run_cmd") as run_cmd,
        ):
            launched = coordinator._launch_free_lanes(state_doc)

        self.assertEqual(launched, [])
        run_cmd.assert_not_called()
        lane_state = state_doc["lane_refill"]["feat-context-storage"]
        self.assertTrue(lane_state["scope_invalid"])
        self.assertEqual(lane_state["scope_violation_count"], 1)
        self.assertNotIn("force_resume_once", lane_state)

    def test_launch_free_lanes_reserves_last_local_slot_for_reviewer_fixers(self) -> None:
        from packet_garden.tools import agents_coordinator as coordinator

        state_doc = {"lane_refill": {"feat-commands": {"queue_empty": True}}}

        with (
            patch.object(coordinator, "_enabled_lanes", return_value=["feat-commands"]),
            patch.object(coordinator, "_lane_queue_empty", return_value=True),
            patch.object(coordinator, "_lane_has_active_feature_session", return_value=False),
            patch.object(coordinator, "_local_lms_feature_launch_slots", return_value=1),
            patch.object(coordinator, "_active_local_router_jobs", return_value=0),
            patch.object(coordinator, "_has_router_priority_backlog", return_value=True),
            patch.object(coordinator, "_has_lane_backlog", return_value=True),
            patch.object(coordinator, "_cloud_feature_launch_slots", return_value=0),
            patch.object(coordinator, "run_cmd") as run_cmd,
        ):
            launched = coordinator._launch_free_lanes(state_doc)

        self.assertEqual(launched, [])
        run_cmd.assert_not_called()

    def test_reconcile_terminates_malformed_apply_patch_loop(self) -> None:
        from packet_garden.tools import agents_coordinator as coordinator

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            log_path = root / "feat-context.log"
            log_path.write_text(
                ("\n".join(["Usage: apply_patch 'PATCH'"] * 6))
                + "\nfailed to parse function arguments: invalid type: sequence, expected a string\n"
                + '<|channel|>functions.exec_command{"cmd":"apply_patch"}\n',
                encoding="utf-8",
            )
            feature_state = root / "feature_runner_state.json"
            router_state = root / "router_state.json"
            feature_state.write_text(
                json.dumps(
                    {
                        "lanes": {
                            "feat-context-storage": {
                                "status": "direct_exec_running",
                                "pid": 56167,
                                "log_path": str(log_path),
                                "last_launch_at": "20260415T150000Z",
                            },
                        }
                    }
                ),
                encoding="utf-8",
            )
            router_state.write_text(json.dumps({}), encoding="utf-8")
            coordinator_state = {"lane_refill": {}}

            with (
                patch.object(coordinator, "FEATURE_RUNNER_STATE_FILE", feature_state),
                patch.object(coordinator, "ROUTER_STATE_FILE", router_state),
                patch.object(coordinator, "_pid_alive", side_effect=lambda pid: pid == 56167),
                patch.object(coordinator, "_terminate_pid_tree") as terminate_mock,
                patch.object(coordinator, "_reconcile_lane_worktrees", return_value={
                    "gitdir_repaired": [],
                    "gitdir_backups": [],
                    "artifacts_removed": {},
                    "health_failures": {},
                    "rebuilt": {},
                    "rebuild_backups": {},
                    "rebuild_failures": {},
                }),
                patch.object(coordinator, "run_hygiene", return_value={
                    "stale_git_pids": [],
                    "temp_worktrees_removed": [],
                    "stale_commit_locks_removed": [],
                    "stale_worktree_index_locks_removed": [],
                }),
                patch.object(coordinator, "find_stale_repo_local_exec_pids", return_value=[]),
                patch.object(coordinator, "find_stale_repo_test_runner_pids", return_value=[]),
                patch.object(coordinator, "_reconcile_duplicate_feature_exec_processes", return_value={}),
                patch.object(coordinator, "_lane_scope_violations", return_value=[]),
                patch.object(coordinator, "_lane_head_advanced_since_handoff", return_value=False),
                patch.object(coordinator, "time") as time_mod,
            ):
                time_mod.time.return_value = 1_776_272_400.0
                time_mod.sleep.return_value = None
                summary = coordinator._reconcile_control_plane_state(coordinator_state)

        terminate_mock.assert_called_once_with(56167)
        self.assertEqual(summary["feature_runner_removed"], ["feat-context-storage"])
        self.assertIn("feat-context-storage", summary["feature_runner_terminated"])
        self.assertEqual(
            coordinator_state["lane_refill"]["feat-context-storage"]["force_resume_reason"],
            "feature_tool_loop_detected",
        )

    def test_reconcile_terminates_feature_runner_past_autonomy_window(self) -> None:
        from packet_garden.tools import agents_coordinator as coordinator

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            feature_state = root / "feature_runner_state.json"
            router_state = root / "router_state.json"
            feature_state.write_text(
                json.dumps(
                    {
                        "lanes": {
                            "feat-retrieval-fts": {
                                "status": "direct_exec_running",
                                "pid": 7301,
                                "last_launch_at": "20260415T150000Z",
                            },
                        }
                    }
                ),
                encoding="utf-8",
            )
            router_state.write_text(json.dumps({}), encoding="utf-8")
            coordinator_state = {"lane_refill": {}}

            with (
                patch.object(coordinator, "FEATURE_RUNNER_STATE_FILE", feature_state),
                patch.object(coordinator, "ROUTER_STATE_FILE", router_state),
                patch.object(coordinator, "FEATURE_MAX_RUNTIME_SECONDS", 60.0),
                patch.object(coordinator, "_pid_alive", side_effect=lambda pid: pid == 7301),
                patch.object(coordinator, "_descendant_process_rows", return_value=[]),
                patch.object(coordinator, "_terminate_pid_tree") as terminate_mock,
                patch.object(coordinator, "_reconcile_lane_worktrees", return_value={
                    "gitdir_repaired": [],
                    "gitdir_backups": [],
                    "artifacts_removed": {},
                    "health_failures": {},
                    "rebuilt": {},
                    "rebuild_backups": {},
                    "rebuild_failures": {},
                }),
                patch.object(coordinator, "run_hygiene", return_value={
                    "stale_git_pids": [],
                    "temp_worktrees_removed": [],
                    "stale_commit_locks_removed": [],
                    "stale_worktree_index_locks_removed": [],
                }),
                patch.object(coordinator, "find_stale_repo_local_exec_pids", return_value=[]),
                patch.object(coordinator, "find_stale_repo_test_runner_pids", return_value=[]),
                patch.object(coordinator, "_reconcile_duplicate_feature_exec_processes", return_value={}),
                patch.object(coordinator, "_lane_scope_violations", return_value=[]),
                patch.object(coordinator, "_lane_head_advanced_since_handoff", return_value=False),
                patch.object(coordinator, "time") as time_mod,
            ):
                time_mod.time.return_value = 1_779_170_600.0
                time_mod.sleep.return_value = None
                summary = coordinator._reconcile_control_plane_state(coordinator_state)

        terminate_mock.assert_called_once_with(7301)
        self.assertEqual(summary["feature_runner_removed"], ["feat-retrieval-fts"])
        self.assertIn(
            "feature autonomy window exceeded",
            summary["feature_runner_terminated"]["feat-retrieval-fts"],
        )
        self.assertEqual(
            coordinator_state["lane_refill"]["feat-retrieval-fts"]["force_resume_reason"],
            "feature_time_budget_exceeded",
        )

    def test_reconcile_terminates_reconnect_idle_timeout_loop(self) -> None:
        from packet_garden.tools import agents_coordinator as coordinator

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            log_path = root / "feat-a2ui.log"
            log_path.write_text(
                "\n".join(
                    [
                        "WARN codex_core::codex: stream disconnected - retrying sampling request (1/5 in 193ms)...",
                        "WARN codex_core::codex: stream disconnected - retrying sampling request (2/5 in 379ms)...",
                        "WARN codex_core::codex: stream disconnected - retrying sampling request (3/5 in 749ms)...",
                        "WARN codex_core::codex: stream disconnected - retrying sampling request (4/5 in 1.711s)...",
                        "ERROR: stream disconnected before completion: idle timeout waiting for SSE",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            feature_state = root / "feature_runner_state.json"
            router_state = root / "router_state.json"
            feature_state.write_text(
                json.dumps(
                    {
                        "lanes": {
                            "feat-a2ui-contract": {
                                "status": "direct_exec_running",
                                "pid": 24298,
                                "log_path": str(log_path),
                                "last_launch_at": "20260415T150000Z",
                            },
                        }
                    }
                ),
                encoding="utf-8",
            )
            router_state.write_text(json.dumps({}), encoding="utf-8")
            coordinator_state = {"lane_refill": {}}

            with (
                patch.object(coordinator, "FEATURE_RUNNER_STATE_FILE", feature_state),
                patch.object(coordinator, "ROUTER_STATE_FILE", router_state),
                patch.object(coordinator, "_pid_alive", side_effect=lambda pid: pid == 24298),
                patch.object(coordinator, "_terminate_pid_tree") as terminate_mock,
                patch.object(coordinator, "_reconcile_lane_worktrees", return_value={
                    "gitdir_repaired": [],
                    "gitdir_backups": [],
                    "artifacts_removed": {},
                    "health_failures": {},
                    "rebuilt": {},
                    "rebuild_backups": {},
                    "rebuild_failures": {},
                }),
                patch.object(coordinator, "run_hygiene", return_value={
                    "stale_git_pids": [],
                    "temp_worktrees_removed": [],
                    "stale_commit_locks_removed": [],
                    "stale_worktree_index_locks_removed": [],
                }),
                patch.object(coordinator, "find_stale_repo_local_exec_pids", return_value=[]),
                patch.object(coordinator, "find_stale_repo_test_runner_pids", return_value=[]),
                patch.object(coordinator, "_reconcile_duplicate_feature_exec_processes", return_value={}),
                patch.object(coordinator, "_lane_scope_violations", return_value=[]),
                patch.object(coordinator, "_lane_head_advanced_since_handoff", return_value=False),
                patch.object(coordinator, "time") as time_mod,
            ):
                time_mod.time.return_value = 1_776_272_400.0
                time_mod.sleep.return_value = None
                summary = coordinator._reconcile_control_plane_state(coordinator_state)

        terminate_mock.assert_called_once_with(24298)
        self.assertEqual(summary["feature_runner_removed"], ["feat-a2ui-contract"])
        self.assertIn("feat-a2ui-contract", summary["feature_runner_terminated"])
        self.assertEqual(
            coordinator_state["lane_refill"]["feat-a2ui-contract"]["force_resume_reason"],
            "feature_tool_loop_detected",
        )

    def test_reconcile_terminates_feature_startup_with_no_tool_activity(self) -> None:
        from packet_garden.tools import agents_coordinator as coordinator

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            log_path = root / "feat-commands.log"
            log_path.write_text(
                '{"action":"direct_exec_local_fallback","lane":"feat-commands"}\n'
                "\nLocal fallback launched as direct exec.\n"
                "\n> build · gemma-4-31b-it\n",
                encoding="utf-8",
            )
            feature_state = root / "feature_runner_state.json"
            router_state = root / "router_state.json"
            feature_state.write_text(
                json.dumps(
                    {
                        "lanes": {
                            "feat-commands": {
                                "status": "direct_exec_running",
                                "pid": 9194,
                                "log_path": str(log_path),
                                "last_launch_at": "20260415T150000Z",
                            },
                        }
                    }
                ),
                encoding="utf-8",
            )
            router_state.write_text(json.dumps({}), encoding="utf-8")
            coordinator_state = {"lane_refill": {}}

            with (
                patch.object(coordinator, "FEATURE_RUNNER_STATE_FILE", feature_state),
                patch.object(coordinator, "ROUTER_STATE_FILE", router_state),
                patch.object(coordinator, "_pid_alive", side_effect=lambda pid: pid == 9194),
                patch.object(coordinator, "_terminate_pid_tree") as terminate_mock,
                patch.object(coordinator, "_reconcile_lane_worktrees", return_value={
                    "gitdir_repaired": [],
                    "gitdir_backups": [],
                    "artifacts_removed": {},
                    "health_failures": {},
                    "rebuilt": {},
                    "rebuild_backups": {},
                    "rebuild_failures": {},
                }),
                patch.object(coordinator, "run_hygiene", return_value={
                    "stale_git_pids": [],
                    "temp_worktrees_removed": [],
                    "stale_commit_locks_removed": [],
                    "stale_worktree_index_locks_removed": [],
                }),
                patch.object(coordinator, "find_stale_repo_local_exec_pids", return_value=[]),
                patch.object(coordinator, "find_stale_repo_test_runner_pids", return_value=[]),
                patch.object(coordinator, "_reconcile_duplicate_feature_exec_processes", return_value={}),
                patch.object(coordinator, "_lane_scope_violations", return_value=[]),
                patch.object(coordinator, "_lane_head_advanced_since_handoff", return_value=False),
                patch.object(coordinator, "time") as time_mod,
            ):
                time_mod.time.return_value = 1_776_272_400.0
                time_mod.sleep.return_value = None
                summary = coordinator._reconcile_control_plane_state(coordinator_state)

        terminate_mock.assert_called_once_with(9194)
        self.assertEqual(summary["feature_runner_removed"], ["feat-commands"])
        self.assertIn("feat-commands", summary["feature_runner_terminated"])
        self.assertIn(
            "feature startup/no tool activity",
            summary["feature_runner_terminated"]["feat-commands"],
        )
        self.assertEqual(
            coordinator_state["lane_refill"]["feat-commands"]["force_resume_reason"],
            "feature_tool_loop_detected",
        )

    def test_reconcile_terminates_feature_runner_after_handoff_output(self) -> None:
        from packet_garden.tools import agents_coordinator as coordinator

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            log_path = root / "feat-engine-runs.log"
            log_path.write_text(
                "The commit landed. Here is the handoff summary:\n"
                "\n**Handoff: feat-engine-runs**\n"
                "\n**Branch:** `codex/feat-engine-runs`\n"
                "**Commit:** `9eb8217f`\n"
                "\n**Gate results:**\n- 8 new tests pass\n"
                "\n**No control-plane files modified.**\n",
                encoding="utf-8",
            )
            feature_state = root / "feature_runner_state.json"
            router_state = root / "router_state.json"
            feature_state.write_text(
                json.dumps(
                    {
                        "lanes": {
                            "feat-engine-runs": {
                                "status": "direct_exec_running",
                                "pid": 9917,
                                "log_path": str(log_path),
                                "last_launch_at": "20260415T150000Z",
                            },
                        }
                    }
                ),
                encoding="utf-8",
            )
            router_state.write_text(json.dumps({}), encoding="utf-8")
            coordinator_state = {"lane_refill": {}}

            with (
                patch.object(coordinator, "FEATURE_RUNNER_STATE_FILE", feature_state),
                patch.object(coordinator, "ROUTER_STATE_FILE", router_state),
                patch.object(coordinator, "_pid_alive", side_effect=lambda pid: pid == 9917),
                patch.object(coordinator, "_terminate_pid_tree") as terminate_mock,
                patch.object(coordinator, "_reconcile_lane_worktrees", return_value={
                    "gitdir_repaired": [],
                    "gitdir_backups": [],
                    "artifacts_removed": {},
                    "health_failures": {},
                    "rebuilt": {},
                    "rebuild_backups": {},
                    "rebuild_failures": {},
                }),
                patch.object(coordinator, "run_hygiene", return_value={
                    "stale_git_pids": [],
                    "temp_worktrees_removed": [],
                    "stale_commit_locks_removed": [],
                    "stale_worktree_index_locks_removed": [],
                }),
                patch.object(coordinator, "find_stale_repo_local_exec_pids", return_value=[]),
                patch.object(coordinator, "find_stale_repo_test_runner_pids", return_value=[]),
                patch.object(coordinator, "_reconcile_duplicate_feature_exec_processes", return_value={}),
                patch.object(coordinator, "_lane_scope_violations", return_value=[]),
                patch.object(coordinator, "_lane_head_advanced_since_handoff", return_value=True),
                patch.object(coordinator, "time") as time_mod,
            ):
                time_mod.time.return_value = 1_776_272_400.0
                time_mod.sleep.return_value = None
                summary = coordinator._reconcile_control_plane_state(coordinator_state)

        terminate_mock.assert_called_once_with(9917)
        self.assertEqual(summary["feature_runner_removed"], ["feat-engine-runs"])
        self.assertIn("feature handoff detected", summary["feature_runner_terminated"]["feat-engine-runs"])
        self.assertEqual(
            coordinator_state["lane_refill"]["feat-engine-runs"]["force_resume_reason"],
            "branch_advanced_ready_for_review",
        )

    def test_reconcile_keeps_feature_startup_inside_no_tool_grace_window(self) -> None:
        from packet_garden.tools import agents_coordinator as coordinator

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            log_path = root / "feat-commands.log"
            log_path.write_text(
                "\nLocal fallback launched as direct exec.\n"
                "\n> build · gemma-4-31b-it\n",
                encoding="utf-8",
            )
            feature_state = root / "feature_runner_state.json"
            router_state = root / "router_state.json"
            feature_state.write_text(
                json.dumps(
                    {
                        "lanes": {
                            "feat-commands": {
                                "status": "direct_exec_running",
                                "pid": 9195,
                                "log_path": str(log_path),
                                "last_launch_at": "20260519T070000Z",
                            },
                        }
                    }
                ),
                encoding="utf-8",
            )
            router_state.write_text(json.dumps({}), encoding="utf-8")
            coordinator_state = {"lane_refill": {}}

            with (
                patch.object(coordinator, "FEATURE_RUNNER_STATE_FILE", feature_state),
                patch.object(coordinator, "ROUTER_STATE_FILE", router_state),
                patch.object(coordinator, "_pid_alive", side_effect=lambda pid: pid == 9195),
                patch.object(coordinator, "_terminate_pid_tree") as terminate_mock,
                patch.object(coordinator, "_reconcile_lane_worktrees", return_value={
                    "gitdir_repaired": [],
                    "gitdir_backups": [],
                    "artifacts_removed": {},
                    "health_failures": {},
                    "rebuilt": {},
                    "rebuild_backups": {},
                    "rebuild_failures": {},
                }),
                patch.object(coordinator, "run_hygiene", return_value={
                    "stale_git_pids": [],
                    "temp_worktrees_removed": [],
                    "stale_commit_locks_removed": [],
                    "stale_worktree_index_locks_removed": [],
                }),
                patch.object(coordinator, "find_stale_repo_local_exec_pids", return_value=[]),
                patch.object(coordinator, "find_stale_repo_test_runner_pids", return_value=[]),
                patch.object(coordinator, "_reconcile_duplicate_feature_exec_processes", return_value={}),
                patch.object(coordinator, "_lane_scope_violations", return_value=[]),
                patch.object(coordinator, "time") as time_mod,
            ):
                time_mod.time.return_value = 1_779_170_600.0
                time_mod.sleep.return_value = None
                summary = coordinator._reconcile_control_plane_state(coordinator_state)

        terminate_mock.assert_not_called()
        self.assertEqual(summary["feature_runner_removed"], [])

    def test_reconcile_terminates_repeated_malformed_tool_call_loop(self) -> None:
        from packet_garden.tools import agents_coordinator as coordinator

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            log_path = root / "feat-context.log"
            log_path.write_text(
                "\n".join(
                    [
                        "ERROR codex_core::tools::router: error=failed to parse function arguments: invalid type: sequence, expected a string at line 1 column 7",
                        "ERROR codex_core::tools::router: error=failed to parse function arguments: missing field `cmd` at line 1 column 2",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            feature_state = root / "feature_runner_state.json"
            router_state = root / "router_state.json"
            feature_state.write_text(
                json.dumps(
                    {
                        "lanes": {
                            "feat-context-storage": {
                                "status": "direct_exec_running",
                                "pid": 9193,
                                "log_path": str(log_path),
                                "last_launch_at": "20260415T150000Z",
                            },
                        }
                    }
                ),
                encoding="utf-8",
            )
            router_state.write_text(json.dumps({}), encoding="utf-8")
            coordinator_state = {"lane_refill": {}}

            with (
                patch.object(coordinator, "FEATURE_RUNNER_STATE_FILE", feature_state),
                patch.object(coordinator, "ROUTER_STATE_FILE", router_state),
                patch.object(coordinator, "_pid_alive", side_effect=lambda pid: pid == 9193),
                patch.object(coordinator, "_terminate_pid_tree") as terminate_mock,
                patch.object(coordinator, "_reconcile_lane_worktrees", return_value={
                    "gitdir_repaired": [],
                    "gitdir_backups": [],
                    "artifacts_removed": {},
                    "health_failures": {},
                    "rebuilt": {},
                    "rebuild_backups": {},
                    "rebuild_failures": {},
                }),
                patch.object(coordinator, "run_hygiene", return_value={
                    "stale_git_pids": [],
                    "temp_worktrees_removed": [],
                    "stale_commit_locks_removed": [],
                    "stale_worktree_index_locks_removed": [],
                }),
                patch.object(coordinator, "find_stale_repo_local_exec_pids", return_value=[]),
                patch.object(coordinator, "find_stale_repo_test_runner_pids", return_value=[]),
                patch.object(coordinator, "_reconcile_duplicate_feature_exec_processes", return_value={}),
                patch.object(coordinator, "_lane_scope_violations", return_value=[]),
                patch.object(coordinator, "_lane_head_advanced_since_handoff", return_value=False),
                patch.object(coordinator, "time") as time_mod,
            ):
                time_mod.time.return_value = 1_776_272_400.0
                time_mod.sleep.return_value = None
                summary = coordinator._reconcile_control_plane_state(coordinator_state)

        terminate_mock.assert_called_once_with(9193)
        self.assertEqual(summary["feature_runner_removed"], ["feat-context-storage"])
        self.assertIn("feat-context-storage", summary["feature_runner_terminated"])
        self.assertEqual(
            coordinator_state["lane_refill"]["feat-context-storage"]["force_resume_reason"],
            "feature_tool_loop_detected",
        )

    def test_reconcile_terminates_orphan_local_exec_processes(self) -> None:
        from packet_garden.tools import agents_coordinator as coordinator

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            feature_state = root / "feature_runner_state.json"
            router_state = root / "router_state.json"
            feature_state.write_text(json.dumps({"lanes": {}}), encoding="utf-8")
            router_state.write_text(json.dumps({}), encoding="utf-8")
            coordinator_state = {"lane_refill": {}}

            with (
                patch.object(coordinator, "FEATURE_RUNNER_STATE_FILE", feature_state),
                patch.object(coordinator, "ROUTER_STATE_FILE", router_state),
                patch.object(coordinator, "_reconcile_lane_worktrees", return_value={
                    "gitdir_repaired": [],
                    "gitdir_backups": [],
                    "artifacts_removed": {},
                    "health_failures": {},
                    "rebuilt": {},
                    "rebuild_backups": {},
                    "rebuild_failures": {},
                }),
                patch.object(coordinator, "run_hygiene", return_value={
                    "stale_git_pids": [],
                    "temp_worktrees_removed": [],
                    "stale_commit_locks_removed": [],
                    "stale_worktree_index_locks_removed": [],
                }),
                patch.object(coordinator, "find_stale_repo_local_exec_pids", return_value=[111, 222]),
                patch.object(coordinator, "terminate_local_exec_pids", return_value=[111, 222]) as terminate_mock,
                patch.object(coordinator, "find_stale_repo_test_runner_pids", return_value=[]),
                patch.object(coordinator, "_reconcile_duplicate_feature_exec_processes", return_value={}),
            ):
                summary = coordinator._reconcile_control_plane_state(coordinator_state)

        terminate_mock.assert_called_once_with([111, 222])
        self.assertEqual(summary["orphan_local_exec_pids_removed"], [111, 222])

    def test_reconcile_terminates_stale_repo_test_runners(self) -> None:
        from packet_garden.tools import agents_coordinator as coordinator

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            feature_state = root / "feature_runner_state.json"
            router_state = root / "router_state.json"
            feature_state.write_text(json.dumps({"lanes": {}}), encoding="utf-8")
            router_state.write_text(json.dumps({}), encoding="utf-8")
            coordinator_state = {"lane_refill": {}}

            with (
                patch.object(coordinator, "FEATURE_RUNNER_STATE_FILE", feature_state),
                patch.object(coordinator, "ROUTER_STATE_FILE", router_state),
                patch.object(coordinator, "_reconcile_lane_worktrees", return_value={
                    "gitdir_repaired": [],
                    "gitdir_backups": [],
                    "artifacts_removed": {},
                    "health_failures": {},
                    "rebuilt": {},
                    "rebuild_backups": {},
                    "rebuild_failures": {},
                }),
                patch.object(coordinator, "run_hygiene", return_value={
                    "stale_git_pids": [],
                    "temp_worktrees_removed": [],
                    "stale_commit_locks_removed": [],
                    "stale_worktree_index_locks_removed": [],
                }),
                patch.object(coordinator, "find_stale_repo_local_exec_pids", return_value=[]),
                patch.object(coordinator, "find_stale_repo_test_runner_pids", return_value=[333, 444]),
                patch.object(coordinator, "_reconcile_duplicate_feature_exec_processes", return_value={}),
                patch.object(coordinator, "terminate_process_groups", return_value=[333, 444]) as terminate_mock,
            ):
                summary = coordinator._reconcile_control_plane_state(coordinator_state)

        terminate_mock.assert_called_once_with([333, 444])
        self.assertEqual(summary["stale_test_runner_pids_removed"], [333, 444])

    def test_reconcile_router_state_prunes_missing_packet_jobs_and_expired_retries(self) -> None:
        from packet_garden.tools import agents_coordinator as coordinator

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            router_state = root / "router_state.json"
            packets_root = root / "packets"
            existing_lane = packets_root / "feat-engine-runs" / "outbox" / "integrator"
            existing_lane.mkdir(parents=True, exist_ok=True)
            (existing_lane / "R__APPROVED__keep.md").write_text("ok", encoding="utf-8")
            router_state.write_text(
                json.dumps(
                    {
                        "cloud_integrator_jobs": {
                            "feat-engine-runs:R__APPROVED__keep.md": {
                                "lane": "feat-engine-runs",
                                "packet_name": "R__APPROVED__keep.md",
                                "pid": 501,
                                "resume_epoch": "epoch-2",
                            },
                            "feat-engine-runs:R__APPROVED__drop.md": {
                                "lane": "feat-engine-runs",
                                "packet_name": "R__APPROVED__drop.md",
                                "pid": 0,
                                "resume_epoch": "epoch-1",
                            },
                        },
                        "cloud_integrator_retry_ts": {
                            "feat-engine-runs:R__APPROVED__keep.md": 1_999_999_999,
                            "feat-engine-runs:R__APPROVED__drop.md": 1_999_999_999,
                        },
                        "reviewer_fixer_retry_ts": {
                            "feat-commands": 10.0,
                        },
                        "reviewer_quota_global_retry_ts": 10.0,
                    }
                ),
                encoding="utf-8",
            )

            with (
                patch.object(coordinator, "ROUTER_STATE_FILE", router_state),
                patch.object(coordinator, "PACKETS_ROOT", packets_root),
                patch.object(coordinator, "_pid_alive", side_effect=lambda pid: pid == 501),
                patch.object(coordinator, "_lane_scope_violations", return_value=[]),
                patch.object(coordinator, "time") as time_mod,
            ):
                time_mod.time.return_value = 100.0
                removed = coordinator._reconcile_router_state({"current_resume_epoch": "epoch-2"})

            saved = json.loads(router_state.read_text())

        self.assertIn("feat-engine-runs:R__APPROVED__drop.md", removed["cloud_integrator_jobs"])
        self.assertIn("feat-engine-runs:R__APPROVED__drop.md", removed["cloud_integrator_retry_ts"])
        self.assertNotIn("feat-commands", removed.get("reviewer_fixer_retry_ts", []))
        self.assertEqual(removed["reviewer_quota_global_retry_ts"], ["expired"])
        self.assertIn("feat-engine-runs:R__APPROVED__keep.md", saved["cloud_integrator_jobs"])
        self.assertNotIn("feat-engine-runs:R__APPROVED__drop.md", saved["cloud_integrator_jobs"])
        self.assertEqual(saved["reviewer_fixer_retry_ts"], {"feat-commands": 10.0})
        self.assertEqual(saved["reviewer_quota_global_retry_ts"], 0)

    def test_reconcile_router_state_terminates_scope_invalid_router_job(self) -> None:
        from packet_garden.tools import agents_coordinator as coordinator

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            router_state = root / "router_state.json"
            packets_root = root / "packets"
            approved_dir = packets_root / "feat-a2ui-contract" / "outbox" / "integrator"
            approved_dir.mkdir(parents=True, exist_ok=True)
            (approved_dir / "R__APPROVED__a2ui.md").write_text("ok", encoding="utf-8")
            router_state.write_text(
                json.dumps(
                    {
                        "cloud_integrator_jobs": {
                            "feat-a2ui-contract:R__APPROVED__a2ui.md": {
                                "lane": "feat-a2ui-contract",
                                "packet_name": "R__APPROVED__a2ui.md",
                                "pid": 57027,
                            },
                        },
                    }
                ),
                encoding="utf-8",
            )

            with (
                patch.object(coordinator, "ROUTER_STATE_FILE", router_state),
                patch.object(coordinator, "PACKETS_ROOT", packets_root),
                patch.object(coordinator, "_pid_alive", side_effect=lambda pid: pid == 57027),
                patch.object(coordinator, "_lane_scope_violations", return_value=["THREAD_PACKET.md"]),
                patch.object(coordinator, "_auto_revert_scope_violations", return_value=(False, "restore_failed")),
                patch.object(coordinator, "_terminate_pid_tree") as terminate_mock,
            ):
                removed = coordinator._reconcile_router_state({"current_resume_epoch": "epoch-2"})

            saved = json.loads(router_state.read_text())

        terminate_mock.assert_called_once_with(57027)
        self.assertIn("feat-a2ui-contract:R__APPROVED__a2ui.md", removed["cloud_integrator_jobs"][0])
        self.assertEqual(saved["cloud_integrator_jobs"], {})

    def test_reconcile_router_state_terminates_reconnect_looping_fixer(self) -> None:
        from packet_garden.tools import agents_coordinator as coordinator

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            router_state = root / "router_state.json"
            packets_root = root / "packets"
            reviewer_dir = packets_root / "feat-retrieval-fts" / "inbox" / "reviewer"
            reviewer_dir.mkdir(parents=True, exist_ok=True)
            (reviewer_dir / "R__CHANGES__keep.md").write_text("changes", encoding="utf-8")
            log_path = root / "fixer.log"
            log_path.write_text(
                "\n".join(
                    [
                        "WARN codex_core::session::turn: stream disconnected - retrying sampling request (1/5 in 200ms)...",
                        "WARN codex_core::session::turn: stream disconnected - retrying sampling request (2/5 in 400ms)...",
                        "WARN codex_core::session::turn: stream disconnected - retrying sampling request (3/5 in 800ms)...",
                        "WARN codex_core::session::turn: stream disconnected - retrying sampling request (4/5 in 1600ms)...",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            router_state.write_text(
                json.dumps(
                    {
                        "fixer_fallback_jobs": {
                            "feat-retrieval-fts": {
                                "lane": "feat-retrieval-fts",
                                "packet_name": "R__CHANGES__keep.md",
                                "pid": 27223,
                                "local": True,
                                "log": str(log_path),
                                "ts": "20260415T150000Z",
                            },
                        }
                    }
                ),
                encoding="utf-8",
            )

            with (
                patch.object(coordinator, "ROUTER_STATE_FILE", router_state),
                patch.object(coordinator, "PACKETS_ROOT", packets_root),
                patch.object(coordinator, "_pid_alive", side_effect=lambda pid: pid == 27223),
                patch.object(coordinator, "_terminate_pid_tree") as terminate_mock,
                patch.object(coordinator, "time") as time_mod,
            ):
                time_mod.time.return_value = 1_776_272_400.0
                removed = coordinator._reconcile_router_state({"current_resume_epoch": ""})

            saved = json.loads(router_state.read_text())

        terminate_mock.assert_called_once_with(27223)
        self.assertIn("feat-retrieval-fts", removed["fixer_fallback_jobs"][0])
        self.assertEqual(saved["fixer_fallback_jobs"], {})

    def test_reconcile_router_state_terminates_no_tool_fixer_and_marks_cloud_retry(self) -> None:
        from packet_garden.tools import agents_coordinator as coordinator

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            router_state = root / "router_state.json"
            packets_root = root / "packets"
            reviewer_dir = packets_root / "feat-engine-runs" / "inbox" / "reviewer"
            reviewer_dir.mkdir(parents=True, exist_ok=True)
            (reviewer_dir / "R__CHANGES__keep.md").write_text("changes", encoding="utf-8")
            log_path = root / "fixer.log"
            log_path.write_text("\x1b[0m\n> build · gemma-4-31b-it\n\x1b[0m\n", encoding="utf-8")
            router_state.write_text(
                json.dumps(
                    {
                        "fixer_fallback_jobs": {
                            "feat-engine-runs": {
                                "lane": "feat-engine-runs",
                                "packet_name": "R__CHANGES__keep.md",
                                "pid": 7030,
                                "local": True,
                                "log": str(log_path),
                                "ts": "20260518T235458Z",
                            },
                        }
                    }
                ),
                encoding="utf-8",
            )

            with (
                patch.object(coordinator, "ROUTER_STATE_FILE", router_state),
                patch.object(coordinator, "PACKETS_ROOT", packets_root),
                patch.object(coordinator, "_pid_alive", side_effect=lambda pid: pid == 7030),
                patch.object(coordinator, "_terminate_pid_tree") as terminate_mock,
                patch.object(coordinator, "_lane_scope_violations", return_value=[]),
                patch.object(coordinator, "time") as time_mod,
            ):
                time_mod.time.return_value = 1_779_148_800.0
                removed = coordinator._reconcile_router_state({"current_resume_epoch": ""})

            saved = json.loads(router_state.read_text())

        terminate_mock.assert_called_once_with(7030)
        self.assertIn("fixer startup/no tool activity", removed["fixer_fallback_jobs"][0])
        self.assertEqual(saved["fixer_fallback_jobs"], {})
        self.assertIn("feat-engine-runs", saved["fixer_prefer_cloud_once"])

    def test_reconcile_router_state_keeps_reparented_tracked_router_job(self) -> None:
        from packet_garden.tools import agents_coordinator as coordinator

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            router_state = root / "router_state.json"
            packets_root = root / "packets"
            reviewer_dir = packets_root / "feat-retrieval-fts" / "inbox" / "reviewer"
            reviewer_dir.mkdir(parents=True, exist_ok=True)
            (reviewer_dir / "R__CHANGES__keep.md").write_text("changes", encoding="utf-8")
            router_state.write_text(
                json.dumps(
                    {
                        "fixer_fallback_jobs": {
                            "feat-retrieval-fts": {
                                "lane": "feat-retrieval-fts",
                                "packet_name": "R__CHANGES__keep.md",
                                "pid": 55357,
                                "local": True,
                                "log": str(root / "fixer.log"),
                                "ts": "20260504T041021Z",
                            },
                        }
                    }
                ),
                encoding="utf-8",
            )

            with (
                patch.object(coordinator, "ROUTER_STATE_FILE", router_state),
                patch.object(coordinator, "PACKETS_ROOT", packets_root),
                patch.object(coordinator, "_pid_alive", side_effect=lambda pid: pid == 55357),
                patch.object(coordinator, "_parent_pid", return_value=1),
                patch.object(coordinator, "_lane_scope_violations", return_value=[]),
                patch.object(coordinator, "_terminate_pid_tree") as terminate_mock,
            ):
                removed = coordinator._reconcile_router_state({"current_resume_epoch": ""})

            saved = json.loads(router_state.read_text())

        terminate_mock.assert_not_called()
        self.assertNotIn("fixer_fallback_jobs", removed)
        self.assertIn("feat-retrieval-fts", saved["fixer_fallback_jobs"])

    def test_reconcile_terminates_runaway_feature_child_process_tree(self) -> None:
        from packet_garden.tools import agents_coordinator as coordinator

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            feature_state = root / "feature_runner_state.json"
            router_state = root / "router_state.json"
            feature_state.write_text(
                json.dumps(
                    {
                        "lanes": {
                            "feat-a2ui-contract": {
                                "status": "direct_exec_running",
                                "pid": 7000,
                                "last_launch_at": "20260415T150000Z",
                            },
                        }
                    }
                ),
                encoding="utf-8",
            )
            router_state.write_text(json.dumps({}), encoding="utf-8")
            coordinator_state = {"lane_refill": {}}

            with (
                patch.object(coordinator, "FEATURE_RUNNER_STATE_FILE", feature_state),
                patch.object(coordinator, "ROUTER_STATE_FILE", router_state),
                patch.object(coordinator, "_pid_alive", side_effect=lambda pid: pid == 7000),
                patch.object(
                    coordinator,
                    "_descendant_process_rows",
                    return_value=[
                        (
                            7001,
                            7000,
                            7000,
                            coordinator.FEATURE_CHILD_RSS_LIMIT_KB + 1,
                            "Python -m unittest tests.unit.test_a2ui_contract",
                        )
                    ],
                ),
                patch.object(coordinator, "_terminate_pid_tree") as terminate_mock,
                patch.object(coordinator, "_reconcile_lane_worktrees", return_value={
                    "gitdir_repaired": [],
                    "gitdir_backups": [],
                    "artifacts_removed": {},
                    "health_failures": {},
                    "rebuilt": {},
                    "rebuild_backups": {},
                    "rebuild_failures": {},
                }),
                patch.object(coordinator, "run_hygiene", return_value={
                    "stale_git_pids": [],
                    "temp_worktrees_removed": [],
                    "stale_commit_locks_removed": [],
                    "stale_worktree_index_locks_removed": [],
                }),
                patch.object(coordinator, "find_stale_repo_local_exec_pids", return_value=[]),
                patch.object(coordinator, "find_stale_repo_test_runner_pids", return_value=[]),
                patch.object(coordinator, "_reconcile_duplicate_feature_exec_processes", return_value={}),
                patch.object(coordinator, "_lane_scope_violations", return_value=[]),
                patch.object(coordinator, "time") as time_mod,
            ):
                time_mod.time.return_value = 1_776_272_400.0
                time_mod.sleep.return_value = None
                summary = coordinator._reconcile_control_plane_state(coordinator_state)

        terminate_mock.assert_called_once_with(7000)
        self.assertEqual(summary["feature_runner_removed"], ["feat-a2ui-contract"])
        self.assertIn("runaway child process", summary["feature_runner_terminated"]["feat-a2ui-contract"])

    def test_reconcile_duplicate_feature_exec_processes_keeps_current_lane_pid(self) -> None:
        from packet_garden.tools import agents_coordinator as coordinator

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            feature_state = root / "feature_runner_state.json"
            feature_state.write_text(
                json.dumps(
                    {
                        "lanes": {
                            "feat-context-storage": {
                                "status": "direct_exec_running",
                                "pid": 1001,
                            },
                            "feat-a2ui-contract": {
                                "status": "direct_exec_running",
                                "pid": 2001,
                            },
                        }
                    }
                ),
                encoding="utf-8",
            )

            with (
                patch.object(coordinator, "FEATURE_RUNNER_STATE_FILE", feature_state),
                patch.object(
                    coordinator,
                    "_manual_feature_exec_processes",
                    return_value={
                        "feat-context-storage": [1001, 1002],
                        "feat-a2ui-contract": [2001],
                    },
                ),
                patch.object(coordinator, "_terminate_pid_tree") as terminate_mock,
            ):
                removed = coordinator._reconcile_duplicate_feature_exec_processes()

        terminate_mock.assert_called_once_with(1002)
        self.assertEqual(removed, {"feat-context-storage": [1002]})

    def test_manual_feature_exec_processes_detects_codex_and_opencode_workers(self) -> None:
        from packet_garden.tools import agents_coordinator as coordinator

        ps_output = "\n".join(
            [
                "1001 /Applications/Codex.app/Contents/Resources/codex exec You are the feature lane agent for feat-commands.",
                "1002 /opt/homebrew/bin/opencode run --model lmstudio/gemma-4-31b-it You are the feature lane agent for feat-retrieval-fts.",
                "1003 /opt/homebrew/bin/opencode run --model lmstudio/gemma-4-31b-it unrelated prompt",
            ]
        )

        with patch.object(
            coordinator.subprocess,
            "run",
            return_value=SimpleNamespace(returncode=0, stdout=ps_output),
        ):
            detected = coordinator._manual_feature_exec_processes()

        self.assertEqual(detected["feat-commands"], [1001])
        self.assertEqual(detected["feat-retrieval-fts"], [1002])
        self.assertNotIn("unrelated", detected)


if __name__ == "__main__":
    unittest.main()
