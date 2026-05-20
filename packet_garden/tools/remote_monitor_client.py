#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict

DEFAULT_URL = "http://127.0.0.1:8765"
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = REPO_ROOT / ".codex" / "remote_monitor" / "config.json"


def _load_default_config() -> Dict[str, Any]:
    try:
        payload = json.loads(DEFAULT_CONFIG.read_text())
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _default_base_url() -> str:
    env_url = os.environ.get("QUAL_MONITOR_URL")
    if env_url:
        return env_url.rstrip("/")

    config = _load_default_config()
    host = str(config.get("host") or "127.0.0.1")
    port = int(config.get("port") or 8765)
    return f"http://{host}:{port}"


def _default_token() -> str:
    env_token = os.environ.get("QUAL_MONITOR_TOKEN")
    if env_token:
        return env_token

    config = _load_default_config()
    token_path = config.get("token_file")
    if not isinstance(token_path, str) or not token_path:
        return ""

    path = Path(token_path)
    if not path.is_absolute():
        path = REPO_ROOT / path
    try:
        return path.read_text().strip()
    except OSError:
        return ""


def _request(method: str, path: str, *, body: Dict[str, Any] | None = None) -> Dict[str, Any]:
    base = _default_base_url()
    token = _default_token()
    data = None
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(f"{base}{path}", data=data, method=method, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as response:  # noqa: S310 - operator-configured URL
        return json.loads(response.read().decode("utf-8"))


def _request_text(method: str, path: str, *, accept: str = "text/plain") -> str:
    base = _default_base_url()
    token = _default_token()
    headers = {"Accept": accept}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(f"{base}{path}", method=method, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as response:  # noqa: S310 - operator-configured URL
        return response.read().decode("utf-8")


def _print_summary(payload: Dict[str, Any]) -> None:
    pause = payload.get("pause") if isinstance(payload.get("pause"), dict) else {}
    git = payload.get("git") if isinstance(payload.get("git"), dict) else {}
    memory = payload.get("memory_pressure") if isinstance(payload.get("memory_pressure"), dict) else {}
    print(f"generated_at={payload.get('generated_at', '-')}")
    print(f"daemon_running={payload.get('daemon_running', '-')}")
    print(f"paused={pause.get('paused', False)}")
    if pause.get("paused"):
        print(f"pause_reason={pause.get('reason', '-')}")
    print(f"runtime_mode={payload.get('runtime_mode', '-')}")
    print(f"cloud_available={payload.get('cloud_available', '-')}")
    print(f"local_lms_jobs={payload.get('local_lms_jobs', '-')}")
    print(f"cloud_jobs={payload.get('cloud_jobs', '-')}")
    print(f"pending_feature={payload.get('pending_feature', 0)}")
    print(f"reviewer_notes={payload.get('reviewer_notes', 0)}")
    print(f"approved_for_integrator={payload.get('approved_for_integrator', 0)}")
    print(f"active_blocker={payload.get('active_blocker', '-')}")
    if git:
        print(f"git_clean_tracked={git.get('clean_tracked', '-')}")
        print(f"git_tracked_change_count={git.get('tracked_change_count', '-')}")
    if memory:
        summary = memory.get("summary") if isinstance(memory.get("summary"), list) else []
        if summary:
            print("memory=" + " | ".join(str(line) for line in summary[:2]))


def main() -> int:
    parser = argparse.ArgumentParser(description="Remote client for qual daemon monitor/control.")
    parser.add_argument(
        "action",
        choices=["status", "text", "html", "full", "health", "start", "stop", "kick"],
        nargs="?",
        default="status",
    )
    parser.add_argument("--operator", default=os.environ.get("QUAL_MONITOR_OPERATOR", "codex-remote"))
    parser.add_argument("--reason", default="")
    args = parser.parse_args()

    try:
        if args.action == "status":
            print(_request_text("GET", "/api/status/text"), end="")
        elif args.action == "text":
            print(_request_text("GET", "/api/status/text"), end="")
        elif args.action == "html":
            print(_request_text("GET", "/api/status/html", accept="text/html"), end="")
        elif args.action == "health":
            print(json.dumps(_request("GET", "/healthz"), indent=2, sort_keys=True))
        elif args.action == "full":
            print(json.dumps(_request("GET", "/api/status"), indent=2, sort_keys=True))
        else:
            payload = _request(
                "POST",
                f"/api/control/{args.action}",
                body={"operator": args.operator, "reason": args.reason},
            )
            print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    except urllib.error.HTTPError as exc:
        sys.stderr.write(f"remote monitor HTTP {exc.code}: {exc.read().decode('utf-8', errors='replace')}\n")
        return 1
    except Exception as exc:
        sys.stderr.write(f"remote monitor error: {type(exc).__name__}: {exc}\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
