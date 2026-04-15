from __future__ import annotations

import json
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch


class CoordinatorRebootResumeTests(unittest.TestCase):
    def test_reconcile_marks_pruned_direct_exec_lane_for_forced_resume(self) -> None:
        from codex_packet_handoff.tools import agents_coordinator as coordinator

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
            ):
                summary = coordinator._reconcile_control_plane_state(coordinator_state)

        self.assertEqual(summary["feature_runner_removed"], ["feat-commands"])
        self.assertTrue(coordinator_state["lane_refill"]["feat-commands"]["force_resume_once"])
        self.assertEqual(
            coordinator_state["lane_refill"]["feat-commands"]["force_resume_reason"],
            "stale_direct_exec_pruned",
        )

    def test_launch_free_lanes_bypasses_cooldown_for_forced_resume(self) -> None:
        from codex_packet_handoff.tools import agents_coordinator as coordinator

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
            patch.object(coordinator, "run_cmd", side_effect=fake_run_cmd),
        ):
            launched = coordinator._launch_free_lanes(state_doc)

        self.assertEqual(launched, ["feat-commands"])
        self.assertEqual(commands[0][-2:], ["--lanes", "feat-commands"])
        lane_state = state_doc["lane_refill"]["feat-commands"]
        self.assertEqual(lane_state["last_launch_reason"], "stale_direct_exec_resume")
        self.assertNotIn("force_resume_once", lane_state)

    def test_launch_free_lanes_clears_forced_resume_when_lane_already_active(self) -> None:
        from codex_packet_handoff.tools import agents_coordinator as coordinator

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
            patch.object(coordinator, "run_cmd") as run_cmd,
        ):
            launched = coordinator._launch_free_lanes(state_doc)

        self.assertEqual(launched, [])
        run_cmd.assert_not_called()
        lane_state = state_doc["lane_refill"]["feat-commands"]
        self.assertNotIn("force_resume_once", lane_state)
        self.assertIn("force_resume_cleared_at", lane_state)

    def test_reconcile_terminates_malformed_apply_patch_loop(self) -> None:
        from codex_packet_handoff.tools import agents_coordinator as coordinator

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
                patch.object(coordinator, "_terminate_pid") as terminate_mock,
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

    def test_reconcile_terminates_reconnect_idle_timeout_loop(self) -> None:
        from codex_packet_handoff.tools import agents_coordinator as coordinator

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
                patch.object(coordinator, "_terminate_pid") as terminate_mock,
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

    def test_reconcile_terminates_repeated_malformed_tool_call_loop(self) -> None:
        from codex_packet_handoff.tools import agents_coordinator as coordinator

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
                patch.object(coordinator, "_terminate_pid") as terminate_mock,
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


if __name__ == "__main__":
    unittest.main()
