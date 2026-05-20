from __future__ import annotations

import unittest

from packet_garden.tools import launchd_ctl


class LaunchdCtlTests(unittest.TestCase):
    def test_plist_dict_points_to_launchd_run(self) -> None:
        service = launchd_ctl.SERVICES["daemon"]
        payload = launchd_ctl._plist_dict(service)
        self.assertEqual(payload["Label"], service.label)
        self.assertEqual(payload["ProgramArguments"][0], "/bin/zsh")
        self.assertEqual(payload["ProgramArguments"][1], str(service.wrapper_path))
        self.assertEqual(payload["WorkingDirectory"], str(service.runtime_dir))
        self.assertEqual(payload["StandardOutPath"], str(service.stdout_path))
        self.assertEqual(payload["StandardErrorPath"], str(service.stderr_path))
        self.assertIn("packet_garden/tools/daemon_ctl.py", service.wrapper_text)
        self.assertTrue(payload["KeepAlive"])
        self.assertTrue(payload["RunAtLoad"])


if __name__ == "__main__":
    unittest.main()
