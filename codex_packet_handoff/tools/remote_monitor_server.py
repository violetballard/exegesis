#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import hmac
import ipaddress
import json
import os
import socket
import subprocess
import sys
import threading
import time
import uuid
from datetime import datetime, timezone
from html import escape
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, Mapping

try:
    from remote_monitor_snapshot import _sanitize_text, build_snapshot, compact_summary
except ImportError:  # pragma: no cover - package execution fallback
    from .remote_monitor_snapshot import _sanitize_text, build_snapshot, compact_summary

REPO_ROOT = Path(__file__).resolve().parents[2]
REMOTE_ROOT = REPO_ROOT / ".codex/remote_monitor"
DEFAULT_CONFIG = REMOTE_ROOT / "config.json"
DEFAULT_TOKEN_FILE = REMOTE_ROOT / "token"
COORD_ROOT = REPO_ROOT / ".codex/packet_coordinator"
KICK_FILE = COORD_ROOT / "kick.json"
DAEMON_CTL = [sys.executable, "codex_packet_handoff/tools/daemon_ctl.py"]
COORDINATOR_ONCE = [sys.executable, "codex_packet_handoff/tools/agents_coordinator.py", "--once", "--max-cycles", "1"]
CONTROL_TIMEOUT_SECONDS = 30.0
SNAPSHOT_TTL_SECONDS = 10.0

CONTROL_ROUTES = {
    "/api/control/start": "start",
    "/api/control/stop": "stop",
    "/api/control/kick": "kick",
}

_control_lock = threading.Lock()
_snapshot_lock = threading.Lock()
_cached_snapshot: Dict[str, Any] | None = None
_cached_snapshot_ts = 0.0


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def human_timestamp(value: Any) -> str:
    raw = str(value or "").strip()
    if not raw:
        return "-"
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return raw
    local = parsed.astimezone()
    return local.strftime("%b %-d, %Y at %-I:%M %p %Z")


def load_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text())
    except Exception:
        return default


def write_json(path: Path, data: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(data), indent=2, sort_keys=True) + "\n")


def load_config(path: Path = DEFAULT_CONFIG) -> Dict[str, Any]:
    config = load_json(path, {}) if path.exists() else {}
    return {
        "host": str(config.get("host") or "127.0.0.1"),
        "port": int(config.get("port") or 8765),
        "token_file": str(config.get("token_file") or DEFAULT_TOKEN_FILE),
        "token_env": str(config.get("token_env") or "QUAL_MONITOR_TOKEN"),
        "allowed_remote_cidrs": list(config.get("allowed_remote_cidrs") or []),
        "operator_label": str(config.get("operator_label") or "remote-monitor"),
        "snapshot_ttl_seconds": float(config.get("snapshot_ttl_seconds") or SNAPSHOT_TTL_SECONDS),
    }


def load_token(config: Mapping[str, Any]) -> str:
    env_name = str(config.get("token_env") or "QUAL_MONITOR_TOKEN")
    if os.environ.get(env_name):
        return str(os.environ[env_name])
    token_file = Path(str(config.get("token_file") or DEFAULT_TOKEN_FILE)).expanduser()
    if not token_file.is_absolute():
        token_file = REPO_ROOT / token_file
    try:
        return token_file.read_text().strip()
    except FileNotFoundError:
        return ""


def validate_bind_config(config: Mapping[str, Any]) -> None:
    host = str(config.get("host") or "127.0.0.1")
    try:
        addr = ipaddress.ip_address(socket.gethostbyname(host))
    except Exception as exc:  # pragma: no cover - platform resolver detail
        raise ValueError(f"Cannot resolve remote monitor host {host!r}: {exc}") from exc
    if addr.is_unspecified or addr.is_multicast:
        raise ValueError("Remote monitor host must be loopback or a specific VPN interface address; 0.0.0.0 is forbidden")
    if not addr.is_loopback and not config.get("allowed_remote_cidrs"):
        raise ValueError("Non-loopback remote monitor host requires allowed_remote_cidrs")


def client_allowed(client_ip: str, config: Mapping[str, Any]) -> bool:
    try:
        addr = ipaddress.ip_address(client_ip)
    except ValueError:
        return False
    if addr.is_loopback:
        return True
    for cidr in config.get("allowed_remote_cidrs") or []:
        try:
            if addr in ipaddress.ip_network(str(cidr), strict=False):
                return True
        except ValueError:
            continue
    return False


def authorize(headers: Mapping[str, str], token: str) -> bool:
    auth = str(headers.get("Authorization") or "")
    prefix = "Bearer "
    if auth.startswith(prefix):
        supplied = auth[len(prefix) :].strip()
        return bool(token) and (
            hmac.compare_digest(supplied, token)
            or hmac.compare_digest(supplied, monitor_session_cookie(token))
        )
    cookie = str(headers.get("Cookie") or "")
    expected = monitor_session_cookie(token)
    if not expected:
        return False
    for part in cookie.split(";"):
        name, _, value = part.strip().partition("=")
        if name == "qual_monitor_session" and hmac.compare_digest(value, expected):
            return True
    return False


def monitor_session_cookie(token: str) -> str:
    if not token:
        return ""
    return hmac.new(token.encode("utf-8"), b"qual-remote-monitor-session-v1", hashlib.sha256).hexdigest()


def _run_control_command(args: list[str], *, timeout: float = CONTROL_TIMEOUT_SECONDS) -> Dict[str, Any]:
    try:
        proc = subprocess.run(
            args,
            cwd=REPO_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout,
        )
        output = _sanitize_text(proc.stdout or "", max_lines=80, max_chars=12000).splitlines()
        return {"rc": proc.returncode, "output": output, "timed_out": False}
    except subprocess.TimeoutExpired as exc:
        output = exc.stdout if isinstance(exc.stdout, str) else ""
        safe_output = _sanitize_text(output, max_lines=80, max_chars=12000).splitlines()
        return {"rc": 124, "output": safe_output, "timed_out": True}
    except Exception as exc:
        return {"rc": 1, "output": [f"{type(exc).__name__}: {exc}"], "timed_out": False}


def _fresh_snapshot(config: Mapping[str, Any], *, full: bool = False) -> Dict[str, Any]:
    global _cached_snapshot, _cached_snapshot_ts
    ttl = float(config.get("snapshot_ttl_seconds") or SNAPSHOT_TTL_SECONDS)
    now = time.time()
    with _snapshot_lock:
        needs_full_rebuild = full and (
            _cached_snapshot is None or "safe_command_output" not in _cached_snapshot
        )
        if _cached_snapshot is None or (now - _cached_snapshot_ts) > ttl or needs_full_rebuild:
            _cached_snapshot = build_snapshot(include_monitor_output=full)
            _cached_snapshot_ts = now
        snapshot = dict(_cached_snapshot)
    snapshot["age_seconds"] = max(0, int(now - _cached_snapshot_ts))
    return snapshot if full else compact_summary(snapshot)


def summary_text(payload: Mapping[str, Any]) -> str:
    pause = payload.get("pause") if isinstance(payload.get("pause"), dict) else {}
    git = payload.get("git") if isinstance(payload.get("git"), dict) else {}
    memory = payload.get("memory_pressure") if isinstance(payload.get("memory_pressure"), dict) else {}
    lanes = payload.get("lanes") if isinstance(payload.get("lanes"), list) else []
    daemon = "RUNNING" if payload.get("daemon_running") else "STOPPED"
    paused = "PAUSED" if pause.get("paused") else "active"
    cloud = "available" if str(payload.get("cloud_available", "")).lower() == "true" else str(
        payload.get("cloud_available", "-")
    )
    lines = [
        "Exegesis daemon",
        "===============",
        f"Generated: {human_timestamp(payload.get('generated_at'))}",
        f"Daemon:    {daemon} ({paused})",
        f"Runtime:   {payload.get('runtime_mode', '-')}",
        f"Cloud:     {cloud}",
        "",
        "Capacity",
        "--------",
        f"Local LMS: {payload.get('local_lms_jobs', '-')}",
        f"Cloud:     {payload.get('cloud_jobs', '-')}",
        "",
        "Queue",
        "-----",
        f"Feature packets:       {payload.get('pending_feature', 0)}",
        f"Reviewer notes:        {payload.get('reviewer_notes', 0)}",
        f"Ready for integrator:  {payload.get('approved_for_integrator', 0)}",
        f"Blocker:               {payload.get('active_blocker', '-')}",
    ]
    if pause.get("paused"):
        lines.append(f"Pause reason:          {pause.get('reason', '-')}")
    if lanes:
        lines.extend(["", "Lanes", "-----"])
        for lane in lanes[:12]:
            if not isinstance(lane, dict):
                continue
            running = _format_lane_running(lane)
            lines.append(
                f"{lane.get('lane', '-')}: {lane.get('state', '-')} "
                f"(feature {lane.get('pending_feature', 0)}, review {lane.get('reviewer_notes', 0)}, "
                f"integrator {lane.get('approved_for_integrator', 0)}) [{running}]"
            )
    if git:
        lines.extend(
            [
                "",
                "Repo",
                "----",
                f"Tracked clean: {git.get('clean_tracked', '-')}",
                f"Tracked changes: {git.get('tracked_change_count', '-')}",
            ]
        )
    if memory:
        summary = memory.get("summary") if isinstance(memory.get("summary"), list) else []
        if summary:
            lines.extend(["", "Memory", "------"])
            lines.extend(str(line) for line in summary[:3])
    return "\n".join(lines) + "\n"


def _format_lane_running(lane: Mapping[str, Any]) -> str:
    running = lane.get("running")
    if not isinstance(running, list) or not running:
        return "not running"
    labels: list[str] = []
    for item in running:
        if not isinstance(item, dict):
            continue
        provider = str(item.get("provider") or "unknown")
        role = str(item.get("role") or "job")
        labels.append(f"{provider} {role}")
    return ", ".join(labels) if labels else "not running"


def summary_html(payload: Mapping[str, Any], *, session_token: str = "") -> str:
    pause = payload.get("pause") if isinstance(payload.get("pause"), dict) else {}
    git = payload.get("git") if isinstance(payload.get("git"), dict) else {}
    memory = payload.get("memory_pressure") if isinstance(payload.get("memory_pressure"), dict) else {}
    lanes = payload.get("lanes") if isinstance(payload.get("lanes"), list) else []
    daemon_running = bool(payload.get("daemon_running"))
    daemon_label = "RUNNING" if daemon_running else "STOPPED"
    daemon_class = "ok" if daemon_running else "bad"
    cloud_value = str(payload.get("cloud_available", "-"))
    cloud_class = "ok" if cloud_value.lower() == "true" else "warn"
    blocker = str(payload.get("active_blocker", "-"))
    blocker_class = "ok" if blocker in {"-", "", "none", "None"} else "warn"
    memory_lines = memory.get("summary") if isinstance(memory.get("summary"), list) else []
    toggle_action = "stop" if daemon_running else "start"
    toggle_label = "Stop daemon" if daemon_running else "Start daemon"
    toggle_class = "danger" if daemon_running else "primary"
    rows = [
        ("Runtime", payload.get("runtime_mode", "-"), ""),
        ("Cloud", cloud_value, cloud_class),
        ("Local LMS", payload.get("local_lms_jobs", "-"), ""),
        ("Cloud jobs", payload.get("cloud_jobs", "-"), ""),
        ("Feature packets", payload.get("pending_feature", 0), ""),
        ("Reviewer notes", payload.get("reviewer_notes", 0), ""),
        ("Ready for integrator", payload.get("approved_for_integrator", 0), ""),
        ("Blocker", blocker, blocker_class),
    ]
    if pause.get("paused"):
        rows.append(("Pause reason", pause.get("reason", "-"), "warn"))
    if git:
        rows.extend(
            [
                ("Tracked clean", git.get("clean_tracked", "-"), "ok" if git.get("clean_tracked") else "warn"),
                ("Tracked changes", git.get("tracked_change_count", "-"), ""),
            ]
        )
    row_html = "\n".join(
        f"<div class='row'><span>{escape(str(label))}</span><strong class='{escape(str(css))}'>{escape(str(value))}</strong></div>"
        for label, value, css in rows
    )
    memory_html = ""
    if memory_lines:
        memory_html = "<section><h2>Memory</h2><pre>" + escape("\n".join(str(line) for line in memory_lines[:4])) + "</pre></section>"
    lane_html = ""
    lane_rows: list[str] = []
    for lane in lanes[:12]:
        if not isinstance(lane, dict):
            continue
        pending = int(lane.get("pending_feature", 0) or 0)
        review = int(lane.get("reviewer_notes", 0) or 0)
        approved = int(lane.get("approved_for_integrator", 0) or 0)
        state = str(lane.get("state", "-"))
        css = "ok"
        if approved:
            css = "warn"
        elif review:
            css = "warn"
        elif pending:
            css = ""
        lane_rows.append(
            "<div class='lane-row'>"
            f"<strong>{escape(str(lane.get('lane', '-')))}</strong>"
            f"<span class='{escape(css)}'>{escape(state)}</span>"
            f"<small>{escape(_format_lane_running(lane))} · feature {pending} · review {review} · integrator {approved}</small>"
            "</div>"
        )
    if lane_rows:
        lane_html = "<section><h2>Lanes</h2><div class='lanes'>" + "\n".join(lane_rows) + "</div></section>"
    generated = human_timestamp(payload.get("generated_at"))
    safe_session_token = json.dumps(session_token)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Exegesis Status</title>
  <style>
    :root {{
      color-scheme: dark;
      --bg: #0d1f31;
      --panel: #152d45;
      --line: #18d17f;
      --text: #e8f1ff;
      --muted: #a7bad0;
      --ok: #5dff9b;
      --warn: #ffd16a;
      --bad: #ff7d7d;
    }}
    body {{
      margin: 0;
      padding: 22px;
      background: radial-gradient(circle at top, #193a58 0, var(--bg) 46%);
      color: var(--text);
      font: 16px/1.45 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    }}
    main {{
      max-width: 720px;
      margin: 0 auto;
      border: 1px solid var(--line);
      background: color-mix(in srgb, var(--panel) 92%, black);
      box-shadow: 0 0 0 1px #0a1623, 0 18px 50px rgb(0 0 0 / 35%);
      padding: 20px;
    }}
    h1 {{ margin: 0 0 4px; font-size: 22px; color: var(--line); }}
    h2 {{ margin: 22px 0 10px; font-size: 15px; color: #1a96ff; }}
    .stamp {{ color: var(--muted); margin-bottom: 18px; }}
    .pill {{
      display: inline-block;
      margin: 8px 0 10px;
      padding: 7px 11px;
      border: 1px solid color-mix(in srgb, var(--line) 70%, white);
      background: #0e8ce3;
      color: white;
      font-weight: 700;
    }}
    .controls {{
      display: flex;
      gap: 10px;
      margin: 0 0 18px;
      flex-wrap: wrap;
    }}
    button {{
      appearance: none;
      border: 1px solid color-mix(in srgb, var(--line) 70%, white);
      background: #0e8ce3;
      color: white;
      font: inherit;
      font-weight: 700;
      padding: 10px 13px;
      min-width: 130px;
      cursor: pointer;
    }}
    button:hover {{ background: #0768ab; }}
    button.danger {{
      background: #dba057;
      color: #06111d;
      border-color: #ffd193;
    }}
    button.danger:hover {{ background: #bd8542; }}
    #control-status {{
      min-height: 1.3em;
      margin: -8px 0 14px;
      color: var(--muted);
      font-size: 14px;
    }}
    .row {{
      display: flex;
      justify-content: space-between;
      gap: 18px;
      border-top: 1px solid rgb(255 255 255 / 8%);
      padding: 11px 0;
    }}
    .row span {{ color: var(--muted); }}
    .lanes {{
      display: grid;
      gap: 8px;
    }}
    .lane-row {{
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 4px 12px;
      padding: 10px;
      background: #10263a;
      border: 1px solid rgb(255 255 255 / 10%);
    }}
    .lane-row strong {{ text-align: left; color: var(--text); }}
    .lane-row span {{ text-align: right; }}
    .lane-row small {{ grid-column: 1 / -1; color: var(--muted); }}
    strong {{ text-align: right; }}
    .ok {{ color: var(--ok); }}
    .warn {{ color: var(--warn); }}
    .bad {{ color: var(--bad); }}
    pre {{
      white-space: pre-wrap;
      background: #10263a;
      border: 1px solid rgb(255 255 255 / 10%);
      padding: 12px;
      color: var(--text);
    }}
  </style>
</head>
<body>
  <main>
    <h1>Exegesis Status</h1>
    <div class="stamp">{escape(generated)}</div>
    <div class="pill {daemon_class}">Daemon: {daemon_label}</div>
    <div class="controls">
      <button class="{toggle_class}" data-action="{toggle_action}">{toggle_label}</button>
      <button class="primary" data-action="kick">Kick</button>
    </div>
    <div id="control-status" aria-live="polite"></div>
    <section>{row_html}</section>
    {lane_html}
    {memory_html}
  </main>
  <script>
    const statusLine = document.getElementById("control-status");
    const monitorSessionToken = {safe_session_token};
    async function runControl(action) {{
      statusLine.textContent = `Sending ${{action}}...`;
      try {{
        const headers = {{ "Content-Type": "application/json", "Accept": "application/json" }};
        if (monitorSessionToken) {{
          headers.Authorization = `Bearer ${{monitorSessionToken}}`;
        }}
        const response = await fetch(`/api/control/${{action}}`, {{
          method: "POST",
          credentials: "same-origin",
          headers,
          body: JSON.stringify({{ operator: "status-page", reason: `${{action}} from status page` }})
        }});
        if (!response.ok) {{
          const text = await response.text();
          throw new Error(`${{response.status}} ${{text}}`);
        }}
        statusLine.textContent = `${{action}} complete; refreshing...`;
        setTimeout(() => window.location.reload(), 650);
      }} catch (error) {{
        statusLine.textContent = `Control failed: ${{error.message}}`;
      }}
    }}
    for (const button of document.querySelectorAll("button[data-action]")) {{
      button.addEventListener("click", () => runControl(button.dataset.action));
    }}
  </script>
</body>
</html>
"""


def _invalidate_snapshot() -> None:
    global _cached_snapshot, _cached_snapshot_ts
    with _snapshot_lock:
        _cached_snapshot = None
        _cached_snapshot_ts = 0.0


def _kick(operator: str, reason: str) -> Dict[str, Any]:
    write_json(
        KICK_FILE,
        {
            "operator": operator,
            "reason": reason or "remote kick requested",
            "requested_at": utc_now(),
            "action": "kick",
        },
    )
    return {"rc": 0, "output": ["kick requested"], "timed_out": False}


def run_control_action(action: str, *, operator: str, reason: str = "") -> Dict[str, Any]:
    if action not in {"start", "stop", "kick"}:
        return {"rc": 2, "output": ["unsupported action"], "timed_out": False}
    with _control_lock:
        if action == "start":
            result = _run_control_command([*DAEMON_CTL, "start"])
        elif action == "stop":
            result = _run_control_command([*DAEMON_CTL, "stop"], timeout=60.0)
        else:
            result = _kick(operator, reason)
        _invalidate_snapshot()
        return result


def _read_json_body(handler: BaseHTTPRequestHandler) -> Dict[str, Any]:
    raw_len = handler.headers.get("Content-Length") or "0"
    try:
        size = int(raw_len)
    except ValueError:
        size = 0
    if size <= 0:
        return {}
    if size > 8192:
        raise ValueError("request body too large")
    raw = handler.rfile.read(size)
    if not raw:
        return {}
    data = json.loads(raw.decode("utf-8"))
    if not isinstance(data, dict):
        raise ValueError("request body must be a JSON object")
    return data


class RemoteMonitorHandler(BaseHTTPRequestHandler):
    server_version = "QualRemoteMonitor/1"

    @property
    def monitor_config(self) -> Mapping[str, Any]:
        return getattr(self.server, "monitor_config")  # type: ignore[attr-defined]

    @property
    def monitor_token(self) -> str:
        return getattr(self.server, "monitor_token")  # type: ignore[attr-defined]

    def log_message(self, format: str, *args: object) -> None:  # noqa: A003 - stdlib override
        # Keep access logging minimal and avoid leaking auth headers or paths with data.
        sys.stderr.write(f"{utc_now()} {self.client_address[0]} {format % args}\n")

    def _send_json(self, status: int, payload: Mapping[str, Any]) -> None:
        body = json.dumps(dict(payload), indent=2, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _send_text(self, status: int, body: str) -> None:
        encoded = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(encoded)

    def _send_html(self, status: int, body: str, *, session_cookie: str = "") -> None:
        encoded = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Cache-Control", "no-store")
        if session_cookie:
            self.send_header(
                "Set-Cookie",
                f"qual_monitor_session={session_cookie}; Path=/; Max-Age=86400; HttpOnly; SameSite=Strict",
            )
        self.end_headers()
        self.wfile.write(encoded)

    def _guard(self, *, auth: bool = True) -> bool:
        if not client_allowed(self.client_address[0], self.monitor_config):
            self._send_json(HTTPStatus.FORBIDDEN, {"error": "remote address not allowed"})
            return False
        if auth and not authorize(self.headers, self.monitor_token):
            self._send_json(HTTPStatus.UNAUTHORIZED, {"error": "missing or invalid bearer token"})
            return False
        return True

    def do_GET(self) -> None:  # noqa: N802 - stdlib API
        if self.path == "/healthz":
            if not self._guard(auth=False):
                return
            self._send_json(HTTPStatus.OK, {"status": "ok"})
            return
        if self.path == "/api/status/summary":
            if not self._guard():
                return
            self._send_json(HTTPStatus.OK, _fresh_snapshot(self.monitor_config, full=False))
            return
        if self.path == "/api/status/text":
            if not self._guard():
                return
            self._send_text(HTTPStatus.OK, summary_text(_fresh_snapshot(self.monitor_config, full=False)))
            return
        if self.path == "/api/status/html":
            if not self._guard():
                return
            session = monitor_session_cookie(self.monitor_token)
            self._send_html(
                HTTPStatus.OK,
                summary_html(_fresh_snapshot(self.monitor_config, full=False), session_token=session),
                session_cookie=session,
            )
            return
        if self.path == "/api/status":
            if not self._guard():
                return
            self._send_json(HTTPStatus.OK, _fresh_snapshot(self.monitor_config, full=True))
            return
        self._send_json(HTTPStatus.NOT_FOUND, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802 - stdlib API
        action = CONTROL_ROUTES.get(self.path)
        if not action:
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "not found"})
            return
        if not self._guard():
            return
        try:
            body = _read_json_body(self)
        except Exception as exc:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
            return
        operator = str(body.get("operator") or self.monitor_config.get("operator_label") or "remote-monitor")
        reason = str(body.get("reason") or "")
        action_id = str(uuid.uuid4())
        result = run_control_action(action, operator=operator, reason=reason)
        status_code = HTTPStatus.OK if int(result.get("rc", 1)) == 0 else HTTPStatus.INTERNAL_SERVER_ERROR
        self._send_json(
            status_code,
            {
                "action_id": action_id,
                "action": action,
                "operator": operator,
                "updated_at": utc_now(),
                "result": result,
                "summary": _fresh_snapshot(self.monitor_config, full=False),
            },
        )


def run_server(config_path: Path = DEFAULT_CONFIG) -> int:
    config = load_config(config_path)
    validate_bind_config(config)
    token = load_token(config)
    if not token:
        raise SystemExit("remote monitor token missing; set QUAL_MONITOR_TOKEN or token_file")
    server = ThreadingHTTPServer((str(config["host"]), int(config["port"])), RemoteMonitorHandler)
    server.monitor_config = config  # type: ignore[attr-defined]
    server.monitor_token = token  # type: ignore[attr-defined]
    print(json.dumps({"status": "listening", "host": config["host"], "port": config["port"]}, sort_keys=True))
    try:
        server.serve_forever(poll_interval=0.5)
    finally:
        server.server_close()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Authenticated remote monitor/control server for qual daemon.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    args = parser.parse_args()
    return run_server(args.config)


if __name__ == "__main__":
    raise SystemExit(main())
