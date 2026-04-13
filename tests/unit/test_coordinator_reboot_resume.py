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


if __name__ == "__main__":
    unittest.main()
