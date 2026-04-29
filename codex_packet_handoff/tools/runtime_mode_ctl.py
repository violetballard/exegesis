#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CFG_FILE = REPO_ROOT / ".codex/packet_router/config.json"
STATE_FILE = REPO_ROOT / ".codex/packet_router/state.json"


def load_json(path: Path, default):
    try:
        return json.loads(path.read_text())
    except Exception:
        return default


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n")


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Inspect or set router runtime mode.")
    ap.add_argument("mode", nargs="?", choices=["cloud_primary", "local_fallback", "status"], default="status")
    ap.add_argument("--retry-seconds", type=int, default=None, help="Cloud retry cooldown seconds when entering local_fallback")
    ap.add_argument("--reason", default="", help="Reason to record in router state")
    return ap.parse_args()


def main() -> int:
    args = parse_args()
    cfg = load_json(CFG_FILE, {})
    state = load_json(STATE_FILE, {})
    if args.mode == "status":
        print(
            json.dumps(
                {
                    "runtime_mode": state.get("runtime_mode") or cfg.get("runtime_mode_default") or "cloud_primary",
                    "cloud_retry_at": state.get("cloud_retry_at", 0),
                    "last_quota_reason": state.get("last_quota_reason", ""),
                    "last_mode_switch_at": state.get("last_mode_switch_at", 0),
                },
                indent=2,
            )
        )
        return 0
    state["runtime_mode"] = args.mode
    state["last_mode_switch_at"] = time.time()
    if args.reason:
        state["last_quota_reason"] = args.reason
    if args.mode == "local_fallback":
        retry_seconds = args.retry_seconds
        if retry_seconds is None:
            retry_seconds = int(cfg.get("cloud_probe_cooldown_seconds", 300))
        state["cloud_retry_at"] = time.time() + retry_seconds
    else:
        state["cloud_retry_at"] = 0
    save_json(STATE_FILE, state)
    print(
        json.dumps(
            {
                "runtime_mode": state["runtime_mode"],
                "cloud_retry_at": state.get("cloud_retry_at", 0),
                "last_quota_reason": state.get("last_quota_reason", ""),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
