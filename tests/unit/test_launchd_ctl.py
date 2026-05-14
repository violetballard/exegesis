from __future__ import annotations

import unittest

from codex_packet_handoff.tools import launchd_ctl


class LaunchdCtlTests(unittest.TestCase):
    def test_plist_dict_points_to_launchd_run(self) -> None:
        payload = launchd_ctl._plist_dict()
        self.assertEqual(payload["Label"], launchd_ctl.LABEL)
        self.assertEqual(payload["ProgramArguments"][0], "/bin/zsh")
        self.assertEqual(payload["ProgramArguments"][1], str(launchd_ctl.LAUNCHD_WRAPPER))
        self.assertEqual(payload["WorkingDirectory"], str(launchd_ctl.LAUNCHD_RUNTIME_DIR))
        self.assertEqual(payload["StandardOutPath"], str(launchd_ctl.LOG_FILE))
        self.assertEqual(payload["StandardErrorPath"], str(launchd_ctl.ERR_FILE))
        self.assertTrue(payload["KeepAlive"])
        self.assertTrue(payload["RunAtLoad"])


if __name__ == "__main__":
    unittest.main()
