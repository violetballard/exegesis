from __future__ import annotations

import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from unittest import mock

from packet_garden.tools import agents_coordinator, remote_monitor_ctl, remote_monitor_server, remote_monitor_snapshot


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
            " 222 4096 00:02 /usr/bin/python packet_garden/tools/agents_coordinator.py --daemon\n"
        )
        completed = mock.Mock(returncode=0, stdout=ps_output)

        with mock.patch.object(remote_monitor_snapshot.subprocess, "run", return_value=completed):
            view = remote_monitor_snapshot._process_view()

        self.assertEqual(view["counts"]["codex_exec"], 1)
        self.assertEqual(view["counts"]["daemon"], 1)
        self.assertNotIn("command", view["processes"][0])

    def test_compact_summary_filters_disabled_lanes(self) -> None:
        payload = remote_monitor_snapshot.compact_summary(
            {
                "summary": {},
                "lane_placements": {
                    "feat-engine-runs": [{"provider": "local", "role": "feature", "pid": "123"}],
                },
                "pipeline": {
                    "lanes": [
                        {"lane": "feat-engine-runs", "state": "feature_in_progress"},
                        {"lane": "feat-console-shell", "state": "disabled"},
                    ]
                },
            }
        )

        lanes = payload["lanes"]
        self.assertEqual([lane["lane"] for lane in lanes], ["feat-engine-runs"])
        self.assertEqual(lanes[0]["running"][0]["provider"], "local")


class RemoteMonitorServerTests(unittest.TestCase):
    def test_authorize_requires_bearer_token(self) -> None:
        self.assertTrue(remote_monitor_server.authorize({"Authorization": "Bearer abc"}, "abc"))
        self.assertFalse(remote_monitor_server.authorize({}, "abc"))
        self.assertFalse(remote_monitor_server.authorize({"Authorization": "Basic abc"}, "abc"))
        self.assertFalse(remote_monitor_server.authorize({"Authorization": "Bearer wrong"}, "abc"))

    def test_authorize_accepts_monitor_session_cookie(self) -> None:
        cookie = remote_monitor_server.monitor_session_cookie("abc")

        self.assertTrue(remote_monitor_server.authorize({"Cookie": f"qual_monitor_session={cookie}"}, "abc"))
        self.assertFalse(remote_monitor_server.authorize({"Cookie": "qual_monitor_session=wrong"}, "abc"))

    def test_client_allowed_requires_loopback_or_configured_cidr(self) -> None:
        cfg = {"allowed_remote_cidrs": ["100.64.0.0/10"]}

        self.assertTrue(remote_monitor_server.client_allowed("127.0.0.1", cfg))
        self.assertTrue(remote_monitor_server.client_allowed("100.64.12.3", cfg))
        self.assertFalse(remote_monitor_server.client_allowed("192.168.1.40", cfg))

    def test_validate_bind_rejects_unspecified_host(self) -> None:
        with self.assertRaises(ValueError):
            remote_monitor_server.validate_bind_config({"host": "0.0.0.0", "allowed_remote_cidrs": ["100.64.0.0/10"]})

    def test_kick_uses_state_file_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            kick = Path(tmp) / "kick.json"
            with mock.patch.object(remote_monitor_server, "KICK_FILE", kick):
                kick_result = remote_monitor_server.run_control_action("kick", operator="test", reason="wake")
                self.assertEqual(kick_result["rc"], 0)
                self.assertTrue(kick.exists())
                self.assertEqual(json.loads(kick.read_text())["action"], "kick")
                self.assertEqual(json.loads(kick.read_text())["reason"], "wake")

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

    def test_summary_text_is_phone_readable(self) -> None:
        payload = {
            "generated_at": "2026-05-17T01:10:00Z",
            "daemon_running": True,
            "runtime_mode": "hybrid",
            "cloud_available": True,
            "local_lms_jobs": "2/4",
            "cloud_jobs": "1/4",
            "pending_feature": 1,
            "reviewer_notes": 0,
            "approved_for_integrator": 0,
            "active_blocker": "-",
            "pause": {"paused": False},
            "lanes": [
                {
                    "lane": "feat-engine-runs",
                    "pending_feature": 1,
                    "reviewer_notes": 0,
                    "approved_for_integrator": 0,
                    "state": "active",
                    "running": [{"provider": "local", "role": "feature", "pid": "123"}],
                }
            ],
        }

        text = remote_monitor_server.summary_text(payload)

        self.assertIn("Exegesis daemon", text)
        self.assertIn("Generated: ", text)
        self.assertIn("Daemon:    RUNNING", text)
        self.assertIn("Runtime:   hybrid", text)
        self.assertIn("feat-engine-runs: active", text)
        self.assertIn("[local feature]", text)
        self.assertTrue(text.endswith("\n"))

    def test_human_timestamp_formats_iso_timestamp(self) -> None:
        formatted = remote_monitor_server.human_timestamp("2026-05-17T01:10:00Z")

        self.assertIn("2026", formatted)
        self.assertIn(" at ", formatted)

    def test_summary_html_is_small_status_view(self) -> None:
        payload = {
            "generated_at": "2026-05-17T01:10:00Z",
            "daemon_running": True,
            "runtime_mode": "hybrid",
            "cloud_available": True,
            "local_lms_jobs": "2/4",
            "cloud_jobs": "1/4",
            "pending_feature": 1,
            "reviewer_notes": 0,
            "approved_for_integrator": 0,
            "active_blocker": "<none>",
            "pause": {"paused": False},
            "lanes": [
                {
                    "lane": "feat-engine-runs",
                    "pending_feature": 1,
                    "reviewer_notes": 0,
                    "approved_for_integrator": 0,
                    "state": "active",
                    "running": [{"provider": "cloud", "role": "integrator", "pid": "123"}],
                }
            ],
        }

        html = remote_monitor_server.summary_html(payload)

        self.assertIn("<title>Exegesis Status</title>", html)
        self.assertIn("Daemon: RUNNING", html)
        self.assertIn("&lt;none&gt;", html)
        self.assertIn('data-action="stop"', html)
        self.assertIn("Kick", html)
        self.assertIn("feat-engine-runs", html)
        self.assertIn("cloud integrator", html)
        self.assertIn("feature 1", html)

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

    def test_text_status_endpoint_requires_auth_and_returns_text(self) -> None:
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
                return_value={
                    "daemon_running": True,
                    "generated_at": "now",
                    "pause": {"paused": False},
                },
            ):
                req = urllib.request.Request(
                    f"{base}/api/status/text",
                    headers={"Authorization": "Bearer token"},
                )
                with urllib.request.urlopen(req, timeout=5) as response:
                    body = response.read().decode("utf-8")
                    content_type = response.headers.get("Content-Type", "")
                self.assertIn("text/plain", content_type)
                self.assertIn("Daemon:    RUNNING", body)
        finally:
            server.shutdown()
            thread.join(timeout=5)
            server.server_close()

    def test_html_status_endpoint_requires_auth_and_returns_html(self) -> None:
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
                return_value={
                    "daemon_running": True,
                    "generated_at": "now",
                    "runtime_mode": "hybrid",
                    "cloud_available": True,
                    "pause": {"paused": False},
                },
            ):
                req = urllib.request.Request(
                    f"{base}/api/status/html",
                    headers={"Authorization": "Bearer token"},
                )
                with urllib.request.urlopen(req, timeout=5) as response:
                    body = response.read().decode("utf-8")
                    content_type = response.headers.get("Content-Type", "")
                    cookie = response.headers.get("Set-Cookie", "")
                self.assertIn("text/html", content_type)
                self.assertIn("Exegesis Status", body)
                self.assertIn("qual_monitor_session=", cookie)
        finally:
            server.shutdown()
            thread.join(timeout=5)
            server.server_close()

    def test_control_endpoint_accepts_html_session_cookie(self) -> None:
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
                "run_control_action",
                return_value={"rc": 0, "output": ["kick requested"], "timed_out": False},
            ), mock.patch.object(
                remote_monitor_server,
                "_fresh_snapshot",
                return_value={"daemon_running": True, "generated_at": "now"},
            ):
                cookie = remote_monitor_server.monitor_session_cookie("token")
                req = urllib.request.Request(
                    f"{base}/api/control/kick",
                    data=b'{"operator":"test"}',
                    method="POST",
                    headers={
                        "Cookie": f"qual_monitor_session={cookie}",
                        "Content-Type": "application/json",
                    },
                )
                with urllib.request.urlopen(req, timeout=5) as response:
                    payload = json.loads(response.read().decode("utf-8"))
                self.assertEqual(payload["action"], "kick")
        finally:
            server.shutdown()
            thread.join(timeout=5)
            server.server_close()

    def test_get_kick_endpoint_accepts_bearer_for_shortcuts(self) -> None:
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
                "run_control_action",
                return_value={"rc": 0, "output": ["kick requested"], "timed_out": False},
            ) as run_action, mock.patch.object(
                remote_monitor_server,
                "_fresh_snapshot",
                return_value={"daemon_running": True, "generated_at": "now"},
            ):
                req = urllib.request.Request(
                    f"{base}/api/control/kick?operator=iphone&reason=shortcut",
                    headers={"Authorization": "Bearer token"},
                    method="GET",
                )
                with urllib.request.urlopen(req, timeout=5) as response:
                    payload = json.loads(response.read().decode("utf-8"))
                self.assertEqual(payload["action"], "kick")
                run_action.assert_called_once_with("kick", operator="iphone", reason="shortcut")
        finally:
            server.shutdown()
            thread.join(timeout=5)
            server.server_close()


class RemoteMonitorCtlTests(unittest.TestCase):
    def test_init_config_writes_chmod_600_token_and_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = root / "config.json"
            token_file = root / "token"

            rc = remote_monitor_ctl.init_config(
                config,
                host="127.0.0.1",
                port=8765,
                allowed_cidr=["100.64.0.0/10"],
                token_file=token_file,
                force=False,
                print_token=False,
            )

            self.assertEqual(rc, 0)
            payload = json.loads(config.read_text())
            self.assertEqual(payload["host"], "127.0.0.1")
            self.assertEqual(payload["allowed_remote_cidrs"], ["100.64.0.0/10"])
            self.assertTrue(token_file.read_text().strip())
            self.assertEqual(token_file.stat().st_mode & 0o777, 0o600)


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
