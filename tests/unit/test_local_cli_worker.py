from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from codex_packet_handoff.tools import local_cli_worker


class LocalCliWorkerTests(unittest.TestCase):
    def test_timeout_terminates_process_group(self) -> None:
        class FakeProc:
            pid = 5151
            returncode = None

            def __init__(self) -> None:
                self.calls = 0

            def communicate(self, timeout: float | None = None):
                self.calls += 1
                if self.calls == 1:
                    raise subprocess.TimeoutExpired(cmd="codex exec", timeout=timeout, output="partial")
                return "final", None

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec_path = root / "job.json"
            out_path = root / "job.out.log"
            result_path = root / "job.result.json"
            spec_path.write_text(
                json.dumps(
                    {
                        "cmd": ["codex", "exec", "prompt"],
                        "cwd": str(root),
                        "timeout_seconds": 1,
                        "output_path": str(out_path),
                        "result_path": str(result_path),
                    }
                ),
                encoding="utf-8",
            )
            fake_proc = FakeProc()
            with (
                mock.patch.object(sys, "argv", ["local_cli_worker.py", "--spec", str(spec_path)]),
                mock.patch.object(local_cli_worker.subprocess, "Popen", return_value=fake_proc) as popen_mock,
                mock.patch.object(local_cli_worker.os, "killpg") as killpg_mock,
            ):
                rc = local_cli_worker.main()

            self.assertEqual(rc, 0)
            self.assertEqual(out_path.read_text(encoding="utf-8"), "final")
            result = json.loads(result_path.read_text(encoding="utf-8"))
            self.assertEqual(result["status"], "timeout")
            self.assertEqual(result["rc"], 124)
            self.assertTrue(popen_mock.call_args.kwargs["start_new_session"])
            killpg_mock.assert_called_once_with(5151, local_cli_worker.signal.SIGTERM)


if __name__ == "__main__":
    unittest.main()
