from __future__ import annotations

import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from unittest import mock

from codex_packet_handoff.tools import agents_coordinator, remote_monitor_server, remote_monitor_snapshot


class RemoteMonitorSnapshotTests(unittest.TestCase):
    def test_sanitize_text_redacts_secrets_and_user_paths(self) -> None:
        raw = "api_key=sk-secretvalue1234567890 /Users/doctor-violet/project/file.txt"

        scrubbed = remote_monitor_snapshot._sanitize_text(raw)

        self.assertIn("api_key=<redacted>", scrubbed)
        self.assertIn("<path>", scrubbed)
        self.assertNotIn("sk-secretvalue", scrubbed)
        self.assertNotIn("doctor-violet", scrubbed)

    def test_process_view_does_not_return_full_commands(self) -> None:
        ps_output = (
            " 111 2048 00:01 codex exec --dangerous secret-token\n"
            " 222 4096 00:02 /usr/bin/python codex_packet_handoff/tools/agents_coordinator.py --daemon\n"
        )
        completed = mock.Mock(returncode=0, stdout=ps_output)

        with mock.patch.object(remote_monitor_snapshot.subprocess, "run", return_value=completed):
            view = remote_monitor_snapshot._process_view()

        self.assertEqual(view["counts"]["codex_exec"], 1)
        self.assertEqual(view["counts"]["daemon"], 1)
        self.assertNotIn("command", view["processes"][0])


class RemoteMonitorServerTests(unittest.TestCase):
    def test_authorize_requires_bearer_token(self) -> None:
        self.assertTrue(remote_monitor_server.authorize({"Authorization": "Bearer abc"}, "abc"))
        self.assertFalse(remote_monitor_server.authorize({}, "abc"))
        self.assertFalse(remote_monitor_server.authorize({"Authorization": "Basic abc"}, "abc"))
        self.assertFalse(remote_monitor_server.authorize({"Authorization": "Bearer wrong"}, "abc"))

    def test_client_allowed_requires_loopback_or_configured_cidr(self) -> None:
        cfg = {"allowed_remote_cidrs": ["100.64.0.0/10"]}

        self.assertTrue(remote_monitor_server.client_allowed("127.0.0.1", cfg))
        self.assertTrue(remote_monitor_server.client_allowed("100.64.12.3", cfg))
        self.assertFalse(remote_monitor_server.client_allowed("192.168.1.40", cfg))

    def test_validate_bind_rejects_unspecified_host(self) -> None:
        with self.assertRaises(ValueError):
            remote_monitor_server.validate_bind_config({"host": "0.0.0.0", "allowed_remote_cidrs": ["100.64.0.0/10"]})

    def test_pause_resume_and_kick_use_state_files_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pause = Path(tmp) / "pause.json"
            kick = Path(tmp) / "kick.json"
            with mock.patch.object(remote_monitor_server, "PAUSE_FILE", pause), mock.patch.object(
                remote_monitor_server, "KICK_FILE", kick
            ):
                pause_result = remote_monitor_server.run_control_action("pause", operator="test", reason="sleep")
                self.assertEqual(pause_result["rc"], 0)
                self.assertTrue(pause.exists())
                self.assertEqual(json.loads(pause.read_text())["reason"], "sleep")

                kick_result = remote_monitor_server.run_control_action("kick", operator="test", reason="wake")
                self.assertEqual(kick_result["rc"], 0)
                self.assertTrue(kick.exists())
                self.assertEqual(json.loads(kick.read_text())["action"], "kick")

                resume_result = remote_monitor_server.run_control_action("resume", operator="test", reason="resume")
                self.assertEqual(resume_result["rc"], 0)
                self.assertFalse(pause.exists())
                self.assertEqual(json.loads(kick.read_text())["action"], "resume")

    def test_control_command_output_is_sanitized(self) -> None:
        completed = mock.Mock(
            returncode=0,
            stdout="api_key=sk-secretvalue1234567890 /Users/doctor-violet/project/file.txt\n",
        )

        with mock.patch.object(remote_monitor_server.subprocess, "run", return_value=completed):
            result = remote_monitor_server._run_control_command(["daemon_ctl", "status"])

        joined = "\n".join(result["output"])
        self.assertIn("api_key=<redacted>", joined)
        self.assertIn("<path>", joined)
        self.assertNotIn("sk-secretvalue", joined)
        self.assertNotIn("doctor-violet", joined)

    def test_status_endpoint_requires_auth(self) -> None:
        config = {"allowed_remote_cidrs": [], "snapshot_ttl_seconds": 0}
        server = remote_monitor_server.ThreadingHTTPServer(("127.0.0.1", 0), remote_monitor_server.RemoteMonitorHandler)
        server.monitor_config = config  # type: ignore[attr-defined]
        server.monitor_token = "token"  # type: ignore[attr-defined]
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = f"http://127.0.0.1:{server.server_address[1]}"
        try:
            with mock.patch.object(
                remote_monitor_server,
                "_fresh_snapshot",
                return_value={"daemon_running": True, "generated_at": "now"},
            ):
                with self.assertRaises(urllib.error.HTTPError) as ctx:
                    urllib.request.urlopen(f"{base}/api/status/summary", timeout=5)
                self.assertEqual(ctx.exception.code, 401)

                req = urllib.request.Request(
                    f"{base}/api/status/summary",
                    headers={"Authorization": "Bearer token"},
                )
                with urllib.request.urlopen(req, timeout=5) as response:
                    payload = json.loads(response.read().decode("utf-8"))
                self.assertTrue(payload["daemon_running"])
        finally:
            server.shutdown()
            thread.join(timeout=5)
            server.server_close()


class RemoteMonitorCoordinatorStateTests(unittest.TestCase):
    def test_consume_kick_request_records_and_deletes_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            kick = Path(tmp) / "kick.json"
            kick.write_text(json.dumps({"action": "kick", "operator": "test", "reason": "nudge"}))
            state: dict[str, object] = {}
            with mock.patch.object(agents_coordinator, "KICK_FILE", kick):
                request = agents_coordinator._consume_kick_request(state)

            self.assertIsNotNone(request)
            self.assertFalse(kick.exists())
            self.assertEqual(state["last_remote_kick"], request)
            self.assertEqual(request["reason"], "nudge")

    def test_record_pause_state_marks_daemon_paused(self) -> None:
        state: dict[str, object] = {}

        agents_coordinator._record_pause_state(state, {"paused": True, "operator": "test", "reason": "pause"})

        self.assertTrue(state["paused"])
        self.assertEqual(state["pause"], {"paused": True, "operator": "test", "reason": "pause"})


if __name__ == "__main__":
    unittest.main()
