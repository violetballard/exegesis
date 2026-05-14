from __future__ import annotations

import subprocess
import unittest
from unittest import mock

from codex_packet_handoff.tools import daemon_ctl


class DaemonCtlTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
