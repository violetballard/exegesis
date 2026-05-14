#!/usr/bin/env python3
from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import sys
import time
import traceback
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

TOOLS_DIR = Path(__file__).resolve().parent
REPO_ROOT = TOOLS_DIR.parent.parent
PLANNER_PATH = REPO_ROOT / "codex_packet_handoff/tools/planner.py"
ROUTER_PATH = REPO_ROOT / "codex_packet_handoff/tools/router.py"
INIT_META_PATH = REPO_ROOT / "codex_packet_handoff/tools/init_lane_meta.py"

PLANNER_CMD = [sys.executable, str(PLANNER_PATH)]
ROUTER_CMD = [sys.executable, str(ROUTER_PATH)]
INIT_META_CMD = [sys.executable, str(INIT_META_PATH)]

EMITTED_RE = re.compile(r"\[planner\] emitted (?P<path>\S+)")
ROUTER_RE = re.compile(
    r"\[router\]\s+processed\s+(?P<processed>\d+)\s+packet\(s\)"
    r"(?:,\s+kicked\s+(?P<kicked>\d+)\s+reviewer-fixer task\(s\))?"
    r"(?:,\s+integrated\s+(?P<integrated>\d+)\s+approval packet\(s\))?"
)
LANE_FILE_RE = re.compile(
    r"\.codex/packets/lanes/(?P<lane>[^/]+)/inbox/feature/(?P<filename>[^/\s]+\.md)"
)

COORD_ROOT = REPO_ROOT / ".codex/packet_coordinator"
RUNS_DIR = COORD_ROOT / "runs"
STATE_FILE = COORD_ROOT / "state.json"
LEASE_FILE = COORD_ROOT / "lease.json"
ROUTER_CONFIG_FILE = REPO_ROOT / ".codex/packet_router/config.json"
ROUTER_EXAMPLE_FILE = REPO_ROOT / ".codex/packet_router/example.json"
DEFAULT_LANES = [
    "feat-context-storage",
    "feat-ux-flow",
    "feat-commands",
    "feat-retrieval-fts",
    "feat-a2ui-contract",
    "feat-engine-runs",
    "feat-console",
]


@dataclass
class DirectRouterCtx:
    router_mod: object
    cfg: object
    state: Dict
    repo_cwd: str
    reviewer_client: object
    integrator_client: object
    reviewer_thread_ids: Dict[str, str]
    integrator_tid: str


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_cmd(cmd: List[str]) -> Tuple[int, str]:
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=str(REPO_ROOT))
    out = p.stdout or ""
    if out:
        print(out, end="" if out.endswith("\n") else "\n")
    return p.returncode, out


def _load_tool_module(module_name: str, relpath: str):
    path = Path(relpath)
    if not path.is_absolute():
        path = REPO_ROOT / path
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    return mod


def load_json(path: Path, default: Dict) -> Dict:
    try:
        return json.loads(path.read_text())
    except Exception:
        return default


def save_json(path: Path, data: Dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True))


def _all_configured_lanes() -> List[str]:
    cfg = load_json(ROUTER_CONFIG_FILE, {})
    lanes = cfg.get("lanes") if isinstance(cfg, dict) else {}
    if isinstance(lanes, dict) and lanes:
        return list(lanes.keys())
    return list(DEFAULT_LANES)


def _enabled_lanes() -> List[str]:
    cfg = load_json(ROUTER_CONFIG_FILE, {})
    lanes = cfg.get("lanes") if isinstance(cfg, dict) else {}
    if isinstance(lanes, dict) and lanes:
        return [name for name, lane_cfg in lanes.items() if bool((lane_cfg or {}).get("enabled", True))]
    return list(DEFAULT_LANES)


def acquire_lease(ttl_seconds: int) -> bool:
    now = time.time()
    if LEASE_FILE.exists():
        lease = load_json(LEASE_FILE, {})
        ts = float(lease.get("ts", 0))
        if now - ts < ttl_seconds:
            return False
    save_json(LEASE_FILE, {"ts": now, "pid": os.getpid(), "updated_at": utc_now()})
    return True


def touch_lease() -> None:
    save_json(LEASE_FILE, {"ts": time.time(), "pid": os.getpid(), "updated_at": utc_now()})


def release_lease() -> None:
    try:
        if LEASE_FILE.exists():
            LEASE_FILE.unlink()
    except Exception:
        pass


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description=(
            "Event-driven multi-agent coordinator for planner/reviewer/fixer/integrator handoff. "
            "No tick scheduler; reacts to lane and state changes."
        )
    )
    ap.add_argument("--daemon", action="store_true", help="Run continuously and react to events")
    ap.add_argument("--once", action="store_true", help="Run event-driven drain cycle once and exit")
    ap.add_argument("--poll-seconds", type=float, default=2.0, help="Polling interval for event detection (default: 2s)")
    ap.add_argument(
        "--idle-grace-seconds",
        type=float,
        default=6.0,
        help="In --once mode, idle time before exit after no changes (default: 6s)",
    )
    ap.add_argument("--max-cycles", type=int, default=200, help="Safety cap for cycles in --once mode")
    ap.add_argument("--stop-on-error", action="store_true", help="Exit immediately on planner/router error")
    ap.add_argument("--planner-retries", type=int, default=1, help="Planner retries per cycle (default: 1)")
    ap.add_argument("--router-retries", type=int, default=1, help="Router retries per cycle (default: 1)")
    ap.add_argument("--lease-ttl", type=int, default=300, help="Lease TTL in seconds (default: 300)")
    ap.add_argument("--preflight-only", action="store_true", help="Run preflight checks and exit")
    ap.add_argument(
        "--execution-mode",
        choices=("direct", "subprocess"),
        default="direct",
        help="Execution mode for planner/router runtime (default: direct)",
    )
    return ap.parse_args()


def _validate_inputs(args: argparse.Namespace) -> int:
    if args.poll_seconds <= 0:
        print("[error] --poll-seconds must be > 0")
        return 2
    if args.idle_grace_seconds < 0:
        print("[error] --idle-grace-seconds must be >= 0")
        return 2
    if args.max_cycles <= 0:
        print("[error] --max-cycles must be > 0")
        return 2
    if args.planner_retries < 0 or args.router_retries < 0:
        print("[error] retries must be >= 0")
        return 2
    if not PLANNER_PATH.exists():
        print(f"[error] Missing planner tool: {PLANNER_PATH}")
        return 2
    if not ROUTER_PATH.exists():
        print(f"[error] Missing router tool: {ROUTER_PATH}")
        return 2
    if not args.daemon and not args.once:
        args.once = True
    if args.daemon and args.once:
        print("[error] use only one of --daemon or --once")
        return 2
    return 0


def _collect_emissions(planner_output: str) -> List[Tuple[str, str]]:
    emissions: List[Tuple[str, str]] = []
    for line in planner_output.splitlines():
        m = EMITTED_RE.search(line)
        if not m:
            continue
        emitted_path = m.group("path")
        m2 = LANE_FILE_RE.search(emitted_path)
        if m2:
            emissions.append((m2.group("lane"), m2.group("filename")))
        else:
            emissions.append(("unknown", Path(emitted_path).name))
    return emissions


def _collect_router_stats(router_output: str) -> Dict[str, int]:
    out = {"processed": 0, "kicked": 0, "integrated": 0}
    for line in router_output.splitlines():
        m = ROUTER_RE.search(line)
        if not m:
            continue
        out["processed"] += int(m.group("processed"))
        kicked = m.group("kicked")
        if kicked:
            out["kicked"] += int(kicked)
        integrated = m.group("integrated")
        if integrated:
            out["integrated"] += int(integrated)
    return out


def _ensure_router_config() -> None:
    if ROUTER_CONFIG_FILE.exists():
        return
    if ROUTER_EXAMPLE_FILE.exists():
        ROUTER_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROUTER_EXAMPLE_FILE, ROUTER_CONFIG_FILE)
        print("[preflight] created .codex/packet_router/config.json from example")


def _load_lane_branches() -> Dict[str, str]:
    cfg = load_json(ROUTER_CONFIG_FILE, {})
    lanes = (cfg.get("lanes") or {}) if isinstance(cfg, dict) else {}
    out: Dict[str, str] = {}
    for lane in _enabled_lanes():
        lane_cfg = lanes.get(lane, {}) if isinstance(lanes, dict) else {}
        branch = str((lane_cfg or {}).get("branch") or f"codex/{lane}")
        out[lane] = branch
    return out


def _ensure_dirs() -> None:
    for lane in _all_configured_lanes():
        base = REPO_ROOT / ".codex/packets/lanes" / lane
        (base / "inbox/feature").mkdir(parents=True, exist_ok=True)
        (base / "inbox/reviewer").mkdir(parents=True, exist_ok=True)
        (base / "outbox/integrator").mkdir(parents=True, exist_ok=True)
        (base / "archive").mkdir(parents=True, exist_ok=True)
    (REPO_ROOT / ".codex/packet_router").mkdir(parents=True, exist_ok=True)
    (REPO_ROOT / ".codex/packet_planner").mkdir(parents=True, exist_ok=True)
    (REPO_ROOT / ".codex/lane_meta").mkdir(parents=True, exist_ok=True)


def _permission_probe() -> None:
    probe = REPO_ROOT / ".codex/packets/_coordinator_write_probe"
    probe.parent.mkdir(parents=True, exist_ok=True)
    probe.write_text("ok")
    probe.unlink()


def _preflight_bootstrap() -> Tuple[bool, str]:
    COORD_ROOT.mkdir(parents=True, exist_ok=True)
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    _ensure_dirs()
    rc, out = run_cmd(INIT_META_CMD)
    if rc != 0:
        return False, f"init_lane_meta failed: {rc}\n{out}"
    _ensure_router_config()
    try:
        _permission_probe()
    except Exception as exc:
        return False, f"filesystem write probe failed: {exc}"
    return True, "ok"


def _run_planner_subprocess(retries: int) -> Tuple[int, str, int]:
    attempts = 0
    while True:
        attempts += 1
        rc, out = run_cmd(PLANNER_CMD)
        if rc == 0:
            return rc, out, attempts
        if "Missing .codex/lane_meta/" in out:
            run_cmd(INIT_META_CMD)
        if attempts > retries + 1:
            return rc, out, attempts
        print(f"[planner] retry attempt {attempts}/{retries + 1}")
        time.sleep(1)


def _run_router_subprocess(retries: int) -> Tuple[int, str, int]:
    attempts = 0
    while True:
        attempts += 1
        rc, out = run_cmd(ROUTER_CMD)
        if rc == 0:
            return rc, out, attempts
        if attempts > retries + 1:
            return rc, out, attempts
        print(f"[router] retry attempt {attempts}/{retries + 1}")
        time.sleep(1)


def _run_planner_direct_once() -> Tuple[int, str]:
    buf = io.StringIO()
    rc = 0
    try:
        planner_mod = _load_tool_module("packet_planner_runtime", str(PLANNER_PATH))
        with contextlib.redirect_stdout(buf):
            planner_mod.main()
    except SystemExit as exc:
        code = exc.code
        rc = int(code) if isinstance(code, int) else 1
    except Exception:
        rc = 1
        traceback.print_exc(file=buf)
    out = buf.getvalue()
    if out:
        print(out, end="" if out.endswith("\n") else "\n")
    return rc, out


def _run_planner_direct(retries: int) -> Tuple[int, str, int]:
    attempts = 0
    while True:
        attempts += 1
        rc, out = _run_planner_direct_once()
        if rc == 0:
            return rc, out, attempts
        if "Missing .codex/lane_meta/" in out:
            run_cmd(INIT_META_CMD)
        if attempts > retries + 1:
            return rc, out, attempts
        print(f"[planner] retry attempt {attempts}/{retries + 1}")
        time.sleep(1)


def _init_direct_router_ctx() -> DirectRouterCtx:
    router_mod = _load_tool_module("packet_router_runtime", str(ROUTER_PATH))
    cfg = router_mod.load_cfg()
    state = router_mod.load_json(router_mod.STATE_FILE, {})
    repo_cwd = str(REPO_ROOT)
    reviewer_client = router_mod._build_mcp_client(
        router_mod._profile_for_role(cfg, "reviewer", local=False),
        router_mod.ApprovalPolicy(True, True),
    )
    integrator_client = router_mod._build_mcp_client(
        router_mod._profile_for_role(cfg, "integrator", local=False),
        router_mod.ApprovalPolicy(True, True),
    )

    reviewer_thread_ids = state.get("reviewer_thread_ids") or {}
    if not isinstance(reviewer_thread_ids, dict):
        reviewer_thread_ids = {}
    reviewer_thread_ids = router_mod.ensure_all_reviewer_threads(
        reviewer_client, cfg, repo_cwd, state, reviewer_thread_ids
    )
    integrator_tid = state.get("integrator_thread_id")
    if not integrator_tid and router_mod._runtime_mode(cfg, state) != "local_fallback":
        integrator_profile = router_mod._profile_for_role(cfg, "integrator", local=False)
        integrator_tid, _ = integrator_client.codex(
            prompt="Ready as integrator.",
            cwd=repo_cwd,
            sandbox="workspace-write",
            approval_policy="never",
            model=integrator_profile.model,
            timeout=cfg.integrator_timeout,
        )

    state["reviewer_thread_ids"] = reviewer_thread_ids
    if reviewer_thread_ids:
        first_lane = sorted(reviewer_thread_ids.keys())[0]
        state["reviewer_thread_id"] = reviewer_thread_ids.get(first_lane)
    else:
        state["reviewer_thread_id"] = None
    state["integrator_thread_id"] = integrator_tid
    router_mod.save_json(router_mod.STATE_FILE, state)
    for lane in cfg.lanes.keys():
        router_mod.ensure_lane_dirs(lane)

    return DirectRouterCtx(
        router_mod=router_mod,
        cfg=cfg,
        state=state,
        repo_cwd=repo_cwd,
        reviewer_client=reviewer_client,
        integrator_client=integrator_client,
        reviewer_thread_ids=reviewer_thread_ids,
        integrator_tid=integrator_tid,
    )


def _run_router_direct_once(ctx: DirectRouterCtx) -> Tuple[int, str]:
    try:
        n, ctx.state, ctx.reviewer_thread_ids, ctx.integrator_tid = ctx.router_mod.process_once(
            ctx.reviewer_client,
            ctx.integrator_client,
            ctx.cfg,
            ctx.state,
            ctx.repo_cwd,
            ctx.reviewer_thread_ids,
            ctx.integrator_tid,
        )
        kicked, ctx.state = ctx.router_mod.process_reviewer_backlog(
            ctx.reviewer_client,
            ctx.cfg,
            ctx.state,
            ctx.repo_cwd,
        )
        integrated, ctx.state, ctx.integrator_tid = ctx.router_mod.process_integrator_backlog(
            ctx.integrator_client,
            ctx.cfg,
            ctx.state,
            ctx.repo_cwd,
            ctx.integrator_tid,
        )
        ctx.state["reviewer_thread_ids"] = ctx.reviewer_thread_ids
        if ctx.reviewer_thread_ids:
            first_lane = sorted(ctx.reviewer_thread_ids.keys())[0]
            ctx.state["reviewer_thread_id"] = ctx.reviewer_thread_ids.get(first_lane)
        else:
            ctx.state["reviewer_thread_id"] = None
        ctx.state["integrator_thread_id"] = ctx.integrator_tid
        ctx.router_mod.save_json(ctx.router_mod.STATE_FILE, ctx.state)
        out = f"[router] processed {n} packet(s), kicked {kicked} reviewer-fixer task(s), integrated {integrated} approval packet(s)\n"
        print(out, end="")
        return 0, out
    except Exception:
        buf = io.StringIO()
        traceback.print_exc(file=buf)
        out = buf.getvalue()
        if out:
            print(out, end="" if out.endswith("\n") else "\n")
        return 1, out


def _run_router_direct(ctx: DirectRouterCtx, retries: int) -> Tuple[int, str, int]:
    attempts = 0
    while True:
        attempts += 1
        rc, out = _run_router_direct_once(ctx)
        if rc == 0:
            return rc, out, attempts
        if attempts > retries + 1:
            return rc, out, attempts
        print(f"[router] retry attempt {attempts}/{retries + 1}")
        time.sleep(1)


def _git_rev(branch: str) -> str:
    p = subprocess.run(["git", "rev-parse", branch], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    if p.returncode != 0:
        return ""
    return (p.stdout or "").strip()


def _lane_digest(lane: str) -> Dict[str, object]:
    base = REPO_ROOT / ".codex/packets/lanes" / lane
    feat = sorted((base / "inbox/feature").glob("*.md"))
    rev = sorted((base / "inbox/reviewer").glob("*.md"))
    appr = sorted((base / "outbox/integrator").glob("*.md"))
    arch = sorted((base / "archive").glob("*.md"))
    def newest_name(paths: List[Path]) -> str:
        if not paths:
            return ""
        return max(paths, key=lambda p: p.stat().st_mtime).name
    return {
        "pending_feature": len(feat),
        "reviewer_notes": len(rev),
        "approved": len(appr),
        "archive": len(arch),
        "latest_feature": newest_name(feat),
        "latest_review": newest_name(rev),
        "latest_approved": newest_name(appr),
    }


def _has_lane_backlog() -> bool:
    """Return True when any lane has packets waiting for reviewer/fixer/integrator."""
    for lane in _enabled_lanes():
        d = _lane_digest(lane)
        if int(d.get("pending_feature", 0)) > 0:
            return True
        if int(d.get("reviewer_notes", 0)) > 0:
            return True
        if int(d.get("approved", 0)) > 0:
            return True
    return False


def _compute_snapshot(branch_map: Dict[str, str]) -> str:
    planner_state = load_json(REPO_ROOT / ".codex/packet_planner/state.json", {})
    router_state = load_json(REPO_ROOT / ".codex/packet_router/state.json", {})
    payload: Dict[str, object] = {
        "planner_state": planner_state,
        "router_state_keys": sorted(router_state.keys()),
        "lanes": {},
        "heads": {},
    }
    lanes_payload: Dict[str, object] = {}
    heads: Dict[str, str] = {}
    for lane in _enabled_lanes():
        lanes_payload[lane] = _lane_digest(lane)
        heads[lane] = _git_rev(branch_map.get(lane, f"codex/{lane}"))
    payload["lanes"] = lanes_payload
    payload["heads"] = heads
    return json.dumps(payload, sort_keys=True)


def _run_cycle(
    args: argparse.Namespace,
    direct_ctx: Optional[DirectRouterCtx],
) -> Dict[str, object]:
    cycle_event: Dict[str, object] = {"started_at": utc_now()}

    print("[planner]")
    if args.execution_mode == "direct":
        planner_rc, planner_out, planner_attempts = _run_planner_direct(args.planner_retries)
    else:
        planner_rc, planner_out, planner_attempts = _run_planner_subprocess(args.planner_retries)
    emissions = _collect_emissions(planner_out)
    cycle_event["planner"] = {
        "rc": planner_rc,
        "attempts": planner_attempts,
        "emitted": [{"lane": lane, "file": fn} for lane, fn in emissions],
    }

    print("[router]")
    if args.execution_mode == "direct":
        assert direct_ctx is not None
        router_rc, router_out, router_attempts = _run_router_direct(direct_ctx, args.router_retries)
    else:
        router_rc, router_out, router_attempts = _run_router_subprocess(args.router_retries)
    router_stats = _collect_router_stats(router_out)
    cycle_event["router"] = {
        "rc": router_rc,
        "attempts": router_attempts,
        "processed": router_stats["processed"],
        "kicked": router_stats["kicked"],
        "integrated": router_stats["integrated"],
    }

    cycle_event["activity"] = bool(emissions or router_stats["processed"] or router_stats["kicked"] or router_stats["integrated"])
    cycle_event["ended_at"] = utc_now()
    return cycle_event


def main() -> int:
    args = parse_args()
    rc = _validate_inputs(args)
    if rc != 0:
        return rc

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_file = RUNS_DIR / f"run__{run_id}.json"
    direct_ctx: Optional[DirectRouterCtx] = None

    if not acquire_lease(args.lease_ttl):
        print("[coordinator] lease busy: another run is active")
        return 0

    try:
        ok, msg = _preflight_bootstrap()
        if not ok:
            print(f"[coordinator] preflight failed: {msg}")
            save_json(
                run_file,
                {
                    "run_id": run_id,
                    "started_at": utc_now(),
                    "status": "preflight_failed",
                    "error": msg,
                },
            )
            return 1
        if args.preflight_only:
            print("[coordinator] preflight ok")
            return 0

        branch_map = _load_lane_branches()
        if args.execution_mode == "direct":
            try:
                direct_ctx = _init_direct_router_ctx()
            except Exception as exc:
                print(f"[coordinator] direct router init failed; falling back to subprocess mode: {exc}")
                args.execution_mode = "subprocess"
                direct_ctx = None

        planner_errors = 0
        router_errors = 0
        emitted_all: List[Tuple[str, str]] = []
        router_processed_total = 0
        fixer_kicked_total = 0
        integrator_processed_total = 0
        cycle_events: List[Dict[str, object]] = []

        run_start = time.time()
        mode_label = f"event_driven_{args.execution_mode}"
        print(f"[coordinator] mode={mode_label}")

        prev_snapshot = ""
        idle_start = time.time()
        cycles = 0

        while True:
            touch_lease()
            snapshot = _compute_snapshot(branch_map)
            backlog_active = _has_lane_backlog()
            should_run = (snapshot != prev_snapshot) or (cycles == 0) or backlog_active

            if should_run:
                print(f"=== EVENT CYCLE {cycles + 1} START {utc_now()} ===")
                event = _run_cycle(args, direct_ctx)
                cycles += 1
                cycle_events.append(event)
                prev_snapshot = _compute_snapshot(branch_map)

                p = event.get("planner", {}) if isinstance(event.get("planner"), dict) else {}
                r = event.get("router", {}) if isinstance(event.get("router"), dict) else {}
                if int(p.get("rc", 0)) != 0:
                    planner_errors += 1
                    if args.stop_on_error:
                        break
                if int(r.get("rc", 0)) != 0:
                    router_errors += 1
                    if args.stop_on_error:
                        break

                for item in p.get("emitted", []):
                    if isinstance(item, dict):
                        emitted_all.append((str(item.get("lane", "unknown")), str(item.get("file", ""))))
                router_processed_total += int(r.get("processed", 0))
                fixer_kicked_total += int(r.get("kicked", 0))
                integrator_processed_total += int(r.get("integrated", 0))

                if bool(event.get("activity")):
                    idle_start = time.time()

                print(f"=== EVENT CYCLE {cycles} END ===")
            else:
                if args.once and (time.time() - idle_start) >= args.idle_grace_seconds:
                    break
                if args.once and cycles >= args.max_cycles:
                    print("[coordinator] max cycles reached in --once mode")
                    break
                if not args.daemon and args.once:
                    time.sleep(args.poll_seconds)
                else:
                    time.sleep(args.poll_seconds)
                    continue

            if args.once and cycles >= args.max_cycles:
                print("[coordinator] max cycles reached in --once mode")
                break
            if args.once and (time.time() - idle_start) >= args.idle_grace_seconds:
                break
            if args.daemon:
                time.sleep(args.poll_seconds)
                continue

        wall = int(time.time() - run_start)
        status = "ok" if (planner_errors == 0 and router_errors == 0) else "errors"

        run_doc: Dict[str, object] = {
            "run_id": run_id,
            "started_at": utc_now(),
            "status": status,
            "mode": mode_label,
            "planner_errors": planner_errors,
            "router_errors": router_errors,
            "router_processed_total": router_processed_total,
            "fixer_kicked_total": fixer_kicked_total,
            "integrator_processed_total": integrator_processed_total,
            "planner_emitted": [{"lane": lane, "file": fn} for lane, fn in emitted_all],
            "cycle_events": cycle_events,
            "cycles": cycles,
            "wall_seconds": wall,
        }
        save_json(run_file, run_doc)
        save_json(
            STATE_FILE,
            {
                "last_run_id": run_id,
                "last_status": status,
                "last_run_file": str(run_file),
                "last_updated_at": utc_now(),
                "last_mode": mode_label,
            },
        )

        print("=== COORDINATOR SUMMARY ===")
        print(f"[summary] mode: {mode_label}")
        if emitted_all:
            print("[summary] planner emitted packets:")
            for lane, fn in emitted_all:
                print(f"- lane={lane} file={fn}")
        else:
            print("[summary] planner emitted packets: none")
        print(f"[summary] router processed total packets: {router_processed_total}")
        print(f"[summary] fixer kicked total tasks: {fixer_kicked_total}")
        print(f"[summary] integrator processed total approvals: {integrator_processed_total}")
        if not emitted_all and router_processed_total == 0 and fixer_kicked_total == 0 and integrator_processed_total == 0:
            print("[summary] no activity this run")
        print(f"[summary] planner errors: {planner_errors}")
        print(f"[summary] router errors: {router_errors}")
        print(f"[summary] cycles: {cycles}")
        print(f"[summary] wall seconds: {wall}")
        print(f"[summary] run artifact: {run_file}")

        return 0 if status == "ok" else 1
    finally:
        if direct_ctx is not None:
            try:
                direct_ctx.reviewer_client.close()
            except Exception:
                pass
            try:
                if direct_ctx.integrator_client is not direct_ctx.reviewer_client:
                    direct_ctx.integrator_client.close()
            except Exception:
                pass
        release_lease()


if __name__ == "__main__":
    raise SystemExit(main())
