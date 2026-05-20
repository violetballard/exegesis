from __future__ import annotations

import subprocess
import signal
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from packet_garden.tools import daemon_ctl


class DaemonCtlTests(unittest.TestCase):
    def test_pid_alive_rejects_non_positive_pid(self) -> None:
        with mock.patch.object(daemon_ctl.os, "kill", side_effect=AssertionError("should not signal pid 0")):
            self.assertFalse(daemon_ctl._pid_alive(0))
            self.assertFalse(daemon_ctl._pid_alive(-1))

    def test_pid_match_allows_restricted_process_table(self) -> None:
        with mock.patch.object(subprocess, "run", side_effect=PermissionError("denied")):
            self.assertTrue(daemon_ctl._pid_matches_daemon(12345))

    def test_pid_match_allows_unavailable_process_report(self) -> None:
        completed = subprocess.CompletedProcess(args=[], returncode=1, stdout="")

        with mock.patch.object(subprocess, "run", return_value=completed):
            self.assertTrue(daemon_ctl._pid_matches_daemon(12345))

    def test_pid_match_rejects_known_wrong_process(self) -> None:
        completed = subprocess.CompletedProcess(args=[], returncode=0, stdout="/bin/zsh")

        with mock.patch.object(subprocess, "run", return_value=completed):
            self.assertFalse(daemon_ctl._pid_matches_daemon(12345))

    def test_is_running_uses_fresh_lease_when_process_command_unknown(self) -> None:
        with mock.patch.object(daemon_ctl, "_read_pid", return_value=12345), mock.patch.object(
            daemon_ctl, "_lease_state", return_value=(12345, 1000.0)
        ), mock.patch.object(daemon_ctl, "_pid_alive", return_value=True), mock.patch.object(
            daemon_ctl, "_pid_matches_daemon", return_value=True
        ), mock.patch.object(
            daemon_ctl.time, "time", return_value=1005.0
        ):
            self.assertTrue(daemon_ctl._is_running())

    def test_is_running_repairs_stale_pidfile_from_fresh_lease(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pid_file = Path(tmp) / "daemon.pid"
            pid_file.write_text("99999", encoding="utf-8")
            with mock.patch.object(daemon_ctl, "PID_FILE", pid_file), mock.patch.object(
                daemon_ctl, "_read_pid", return_value=99999
            ), mock.patch.object(
                daemon_ctl, "_lease_state", return_value=(12345, 1000.0)
            ), mock.patch.object(
                daemon_ctl, "_pid_alive", return_value=True
            ), mock.patch.object(
                daemon_ctl, "_pid_matches_daemon", return_value=True
            ), mock.patch.object(
                daemon_ctl.time, "time", return_value=1005.0
            ):
                self.assertTrue(daemon_ctl._is_running())

            self.assertEqual(pid_file.read_text(encoding="utf-8"), "12345")

    def test_stop_escalates_stale_matching_daemons(self) -> None:
        alive = {111, 222}
        signaled: list[tuple[int, int]] = []

        def fake_kill(pid: int, sig: int) -> None:
            signaled.append((pid, sig))
            if sig == signal.SIGKILL:
                alive.discard(pid)

        with tempfile.TemporaryDirectory() as tmp:
            pid_file = Path(tmp) / "daemon.pid"
            pid_file.write_text("111", encoding="utf-8")
            with mock.patch.object(daemon_ctl, "PID_FILE", pid_file), mock.patch.object(
                daemon_ctl, "_lease_state", return_value=(111, 1000.0)
            ), mock.patch.object(
                daemon_ctl, "_read_pid", return_value=111
            ), mock.patch.object(
                daemon_ctl, "_find_matching_pids", return_value=[111, 222]
            ), mock.patch.object(
                daemon_ctl, "_pid_alive", side_effect=lambda pid: pid in alive
            ), mock.patch.object(
                daemon_ctl.os, "getpgid", side_effect=OSError("no pgid")
            ), mock.patch.object(
                daemon_ctl.os, "kill", side_effect=fake_kill
            ), mock.patch.object(
                daemon_ctl, "_feature_runner_pids", return_value=[]
            ), mock.patch.object(
                daemon_ctl, "_find_automation_worker_pids", return_value=[]
            ), mock.patch.object(
                daemon_ctl, "_router_job_pids", return_value=[]
            ), mock.patch.object(
                daemon_ctl, "find_repo_owned_local_exec_pids", return_value=[]
            ), mock.patch.object(
                daemon_ctl, "find_stale_repo_test_runner_pids", return_value=[]
            ), mock.patch.object(
                daemon_ctl.time, "sleep", return_value=None
            ), mock.patch.object(
                daemon_ctl.time, "time", side_effect=[0, 10, 20, 30, 40, 50]
            ):
                self.assertEqual(daemon_ctl._stop(), 0)

        self.assertIn((111, signal.SIGTERM), signaled)
        self.assertIn((222, signal.SIGTERM), signaled)
        self.assertIn((111, signal.SIGKILL), signaled)
        self.assertIn((222, signal.SIGKILL), signaled)


if __name__ == "__main__":
    unittest.main()
