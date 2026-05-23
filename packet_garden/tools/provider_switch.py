#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_FILE = REPO_ROOT / ".codex/packet_router/config.json"
STATE_FILE = REPO_ROOT / ".codex/packet_router/state.json"
PROVIDERS_DIR = REPO_ROOT / "packet_garden/config/providers"
LAUNCHD_CTL = REPO_ROOT / "packet_garden/tools/launchd_ctl.py"

CLOUD_PROFILE_KEYS = {
    "worker_cloud",
    "worker_cloud_standard_medium",
    "integrator_cloud",
}
CLOUD_ROLE_KEYS = {
    "cloud_probe",
    "feature_cloud",
    "reviewer_cloud",
    "fixer_cloud",
    "integrator_cloud",
}


def load_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text())
    except FileNotFoundError:
        return default


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n")


def provider_path(name: str) -> Path:
    path = PROVIDERS_DIR / f"{name}_cloud.json"
    if not path.exists():
        available = ", ".join(sorted(p.name.removesuffix("_cloud.json") for p in PROVIDERS_DIR.glob("*_cloud.json")))
        raise SystemExit(f"Unknown provider {name!r}. Available: {available or 'none'}")
    return path


def provider_summary(cfg: Dict[str, Any], state: Dict[str, Any] | None = None) -> Dict[str, Any]:
    state = state if isinstance(state, dict) else {}
    profiles = cfg.get("profiles") if isinstance(cfg.get("profiles"), dict) else {}
    roles = cfg.get("role_profiles") if isinstance(cfg.get("role_profiles"), dict) else {}
    out: Dict[str, Any] = {
        "cloud_provider": state.get("cloud_provider") or cfg.get("cloud_provider", "unknown"),
        "cloud_provider_order": state.get("cloud_provider_order") or cfg.get("cloud_provider_order", []),
        "provider_state": state.get("cloud_providers", {}),
        "roles": {},
    }
    for role in sorted(CLOUD_ROLE_KEYS):
        profile_name = str(roles.get(role) or "")
        profile = profiles.get(profile_name) if profile_name else None
        if isinstance(profile, dict):
            out["roles"][role] = {
                "profile": profile_name,
                "harness": profile.get("harness", "codex"),
                "cmd": profile.get("codex_cmd", ""),
                "model": profile.get("model", ""),
                "args": profile.get("model_args", []),
            }
        else:
            out["roles"][role] = {"profile": profile_name or "unset"}
    return out


def apply_provider(cfg: Dict[str, Any], provider_cfg: Dict[str, Any]) -> Dict[str, Any]:
    next_cfg = dict(cfg)
    top_level = provider_cfg.get("top_level") if isinstance(provider_cfg.get("top_level"), dict) else {}
    for key, value in top_level.items():
        next_cfg[str(key)] = value
    next_cfg["cloud_provider"] = str(provider_cfg.get("provider") or "unknown")

    profiles = dict(next_cfg.get("profiles") or {})
    provider_profiles = provider_cfg.get("profiles") if isinstance(provider_cfg.get("profiles"), dict) else {}
    missing = sorted(CLOUD_PROFILE_KEYS - set(provider_profiles))
    if missing:
        raise SystemExit(f"Provider template is missing cloud profiles: {', '.join(missing)}")
    for key in CLOUD_PROFILE_KEYS:
        profiles[key] = provider_profiles[key]
    next_cfg["profiles"] = profiles

    role_profiles = dict(next_cfg.get("role_profiles") or {})
    provider_roles = provider_cfg.get("role_profiles") if isinstance(provider_cfg.get("role_profiles"), dict) else {}
    for key in CLOUD_ROLE_KEYS:
        if key in provider_roles:
            role_profiles[key] = provider_roles[key]
    next_cfg["role_profiles"] = role_profiles
    return next_cfg


def reset_cloud_state(
    provider: str,
    order: list[str] | None = None,
    *,
    unavailable: Dict[str, tuple[float, str]] | None = None,
) -> None:
    state = load_json(STATE_FILE, {})
    if not isinstance(state, dict):
        state = {}
    providers = state.get("cloud_providers")
    if not isinstance(providers, dict):
        providers = {}
    providers.setdefault(provider, {})
    providers[provider].update({"available": True, "retry_at": 0})
    for unavailable_provider, (retry_at, reason) in (unavailable or {}).items():
        if unavailable_provider == provider:
            continue
        providers.setdefault(unavailable_provider, {})
        providers[unavailable_provider].update(
            {
                "available": False,
                "retry_at": retry_at,
                "reason": reason,
            }
        )
    state["runtime_mode"] = "hybrid"
    state["cloud_available"] = True
    state["cloud_retry_at"] = 0
    state["last_mode_switch_at"] = time.time()
    state["last_quota_reason"] = f"cloud provider switched to {provider}"
    state["cloud_provider"] = provider
    state["cloud_providers"] = providers
    if order:
        state["cloud_provider_order"] = order
    save_json(STATE_FILE, state)


def mark_provider_unavailable(provider: str, *, retry_seconds: float, reason: str) -> Dict[str, Any]:
    state = load_json(STATE_FILE, {})
    if not isinstance(state, dict):
        state = {}
    providers = state.get("cloud_providers")
    if not isinstance(providers, dict):
        providers = {}
    retry_at = time.time() + max(1.0, float(retry_seconds))
    providers.setdefault(provider, {})
    providers[provider].update(
        {
            "available": False,
            "retry_at": retry_at,
            "reason": reason,
        }
    )
    state["cloud_providers"] = providers
    if str(state.get("cloud_provider") or "") == provider:
        state["cloud_available"] = False
        state["cloud_retry_at"] = retry_at
    state["last_quota_reason"] = reason
    save_json(STATE_FILE, state)
    return state


def restart_daemon() -> None:
    subprocess.run([sys.executable, str(LAUNCHD_CTL), "stop", "daemon"], cwd=REPO_ROOT, check=False)
    subprocess.run([sys.executable, str(LAUNCHD_CTL), "start", "daemon"], cwd=REPO_ROOT, check=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Switch Packet Garden cloud worker provider profiles.")
    parser.add_argument("provider", nargs="?", choices=["codex", "claude", "status", "mark-unavailable"], default="status")
    parser.add_argument("--order", nargs="+", choices=["claude", "codex"], help="Preferred cloud provider order for quota failover.")
    parser.add_argument("--provider", choices=["claude", "codex"], dest="mark_provider", help="Provider to mark unavailable.")
    parser.add_argument("--mark-codex-unavailable", action="store_true", help="When switching providers, mark Codex unavailable for the retry cooldown.")
    parser.add_argument("--retry-seconds", type=float, default=None, help="Provider-unavailable cooldown in seconds.")
    parser.add_argument("--reason", default="", help="Reason stored in provider state.")
    parser.add_argument("--dry-run", action="store_true", help="Show the provider mapping without writing config/state.")
    parser.add_argument("--restart-daemon", action="store_true", help="Restart the launchd-managed daemon after switching.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    cfg = load_json(CONFIG_FILE, {})
    if not isinstance(cfg, dict) or not cfg:
        raise SystemExit(f"Missing or invalid config: {CONFIG_FILE}")

    if args.provider == "status":
        print(json.dumps(provider_summary(cfg, load_json(STATE_FILE, {})), indent=2))
        return 0

    cooldown = float(args.retry_seconds or cfg.get("cloud_probe_cooldown_seconds") or 1800)
    if args.provider == "mark-unavailable":
        target = args.mark_provider
        if not target:
            raise SystemExit("mark-unavailable requires --provider claude|codex")
        reason = args.reason or f"{target} manually marked unavailable"
        state = mark_provider_unavailable(target, retry_seconds=cooldown, reason=reason)
        print(json.dumps(provider_summary(cfg, state), indent=2))
        if args.restart_daemon:
            restart_daemon()
        return 0

    order = list(dict.fromkeys(args.order or cfg.get("cloud_provider_order") or []))
    if not order:
        order = [args.provider]
    if args.provider not in order:
        order.append(args.provider)

    provider_cfg = load_json(provider_path(args.provider), {})
    if not isinstance(provider_cfg, dict):
        raise SystemExit(f"Invalid provider template for {args.provider}")
    next_cfg = apply_provider(cfg, provider_cfg)
    next_cfg["cloud_provider_order"] = order

    if args.dry_run:
        print(json.dumps(provider_summary(next_cfg), indent=2))
        return 0

    unavailable: Dict[str, tuple[float, str]] = {}
    if args.mark_codex_unavailable and args.provider != "codex":
        unavailable["codex"] = (
            time.time() + max(1.0, cooldown),
            args.reason or "codex manually marked unavailable during provider switch",
        )
    save_json(CONFIG_FILE, next_cfg)
    reset_cloud_state(args.provider, order, unavailable=unavailable)
    print(json.dumps(provider_summary(next_cfg, load_json(STATE_FILE, {})), indent=2))
    if args.restart_daemon:
        restart_daemon()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
