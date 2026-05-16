#!/usr/bin/env python3
from __future__ import annotations

import argparse
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
PAUSE_FILE = COORD_ROOT / "pause.json"
KICK_FILE = COORD_ROOT / "kick.json"
DAEMON_CTL = [sys.executable, "codex_packet_handoff/tools/daemon_ctl.py"]
COORDINATOR_ONCE = [sys.executable, "codex_packet_handoff/tools/agents_coordinator.py", "--once", "--max-cycles", "1"]
CONTROL_TIMEOUT_SECONDS = 30.0
SNAPSHOT_TTL_SECONDS = 10.0

CONTROL_ROUTES = {
    "/api/control/start": "start",
    "/api/control/stop": "stop",
    "/api/control/pause": "pause",
    "/api/control/resume": "resume",
    "/api/control/kick": "kick",
}

_control_lock = threading.Lock()
_snapshot_lock = threading.Lock()
_cached_snapshot: Dict[str, Any] | None = None
_cached_snapshot_ts = 0.0


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


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
    if not auth.startswith(prefix):
        return False
    supplied = auth[len(prefix) :].strip()
    return bool(token) and hmac.compare_digest(supplied, token)


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
    lines = [
        f"generated_at={payload.get('generated_at', '-')}",
        f"daemon_running={payload.get('daemon_running', '-')}",
        f"paused={pause.get('paused', False)}",
    ]
    if pause.get("paused"):
        lines.append(f"pause_reason={pause.get('reason', '-')}")
    lines.extend(
        [
            f"runtime_mode={payload.get('runtime_mode', '-')}",
            f"cloud_available={payload.get('cloud_available', '-')}",
            f"local_lms_jobs={payload.get('local_lms_jobs', '-')}",
            f"cloud_jobs={payload.get('cloud_jobs', '-')}",
            f"pending_feature={payload.get('pending_feature', 0)}",
            f"reviewer_notes={payload.get('reviewer_notes', 0)}",
            f"approved_for_integrator={payload.get('approved_for_integrator', 0)}",
            f"active_blocker={payload.get('active_blocker', '-')}",
        ]
    )
    if git:
        lines.append(f"git_clean_tracked={git.get('clean_tracked', '-')}")
        lines.append(f"git_tracked_change_count={git.get('tracked_change_count', '-')}")
    if memory:
        summary = memory.get("summary") if isinstance(memory.get("summary"), list) else []
        if summary:
            lines.append("memory=" + " | ".join(str(line) for line in summary[:2]))
    return "\n".join(lines) + "\n"


def _invalidate_snapshot() -> None:
    global _cached_snapshot, _cached_snapshot_ts
    with _snapshot_lock:
        _cached_snapshot = None
        _cached_snapshot_ts = 0.0


def _pause(operator: str, reason: str) -> Dict[str, Any]:
    payload = {
        "paused": True,
        "operator": operator,
        "reason": reason or "remote pause requested",
        "updated_at": utc_now(),
    }
    write_json(PAUSE_FILE, payload)
    return {"rc": 0, "output": ["paused"], "timed_out": False}


def _resume(operator: str, reason: str) -> Dict[str, Any]:
    if PAUSE_FILE.exists():
        PAUSE_FILE.unlink()
    write_json(
        KICK_FILE,
        {
            "operator": operator,
            "reason": reason or "remote resume requested",
            "requested_at": utc_now(),
            "action": "resume",
        },
    )
    return {"rc": 0, "output": ["resumed", "kick requested"], "timed_out": False}


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
    if action not in {"start", "stop", "pause", "resume", "kick"}:
        return {"rc": 2, "output": ["unsupported action"], "timed_out": False}
    with _control_lock:
        if action == "start":
            result = _run_control_command([*DAEMON_CTL, "start"])
        elif action == "stop":
            result = _run_control_command([*DAEMON_CTL, "stop"], timeout=60.0)
        elif action == "pause":
            result = _pause(operator, reason)
        elif action == "resume":
            result = _resume(operator, reason)
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
