#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

PLANNER_CMD = [sys.executable, "codex_packet_handoff/tools/planner.py"]
ROUTER_CMD = [sys.executable, "codex_packet_handoff/tools/router.py"]
INIT_META_CMD = [sys.executable, "codex_packet_handoff/tools/init_lane_meta.py"]

EMITTED_RE = re.compile(r"\[planner\] emitted (?P<path>\S+)")
ROUTER_RE = re.compile(
    r"\[router\]\s+processed\s+(?P<processed>\d+)\s+packet\(s\)(?:,\s+kicked\s+(?P<kicked>\d+)\s+reviewer-fixer task\(s\))?"
)
LANE_FILE_RE = re.compile(
    r"\.codex/packets/lanes/(?P<lane>[^/]+)/inbox/feature/(?P<filename>[^/\s]+\.md)"
)

COORD_ROOT = Path(".codex/packet_coordinator")
RUNS_DIR = COORD_ROOT / "runs"
STATE_FILE = COORD_ROOT / "state.json"
LEASE_FILE = COORD_ROOT / "lease.json"
LANES = ["feat-context-storage", "feat-webconsole-core", "feat-webconsole-ui", "feat-ux-flow", "feat-commands"]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_cmd(cmd: List[str]) -> Tuple[int, str]:
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    out = p.stdout or ""
    if out:
        print(out, end="" if out.endswith("\n") else "\n")
    return p.returncode, out


def load_json(path: Path, default: Dict) -> Dict:
    try:
        return json.loads(path.read_text())
    except Exception:
        return default


def save_json(path: Path, data: Dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True))


def acquire_lease(ttl_seconds: int) -> bool:
    now = time.time()
    if LEASE_FILE.exists():
        lease = load_json(LEASE_FILE, {})
        ts = float(lease.get("ts", 0))
        if now - ts < ttl_seconds:
            return False
    save_json(LEASE_FILE, {"ts": now, "pid": os.getpid()})
    return True


def release_lease() -> None:
    try:
        if LEASE_FILE.exists():
            LEASE_FILE.unlink()
    except Exception:
        pass


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description=(
            "Heavier coordinator runner for automation stability. "
            "Wraps planner/router with preflight, retries, lock, and persisted run artifacts."
        )
    )
    ap.add_argument("--ticks", type=int, default=50, help="Total number of ticks (default: 50)")
    ap.add_argument("--minutes", type=int, default=0, help="If set >0, override ticks with minutes")
    ap.add_argument(
        "--planner-interval",
        type=int,
        default=10,
        help="Run planner every N ticks starting at tick 1 (default: 10)",
    )
    ap.add_argument(
        "--tick-seconds",
        type=int,
        default=60,
        help="Target seconds per tick when sleeping (default: 60)",
    )
    ap.add_argument("--no-sleep", action="store_true", help="Do not sleep between ticks")
    ap.add_argument("--stop-on-error", action="store_true", help="Exit immediately on planner/router error")
    ap.add_argument("--planner-retries", type=int, default=1, help="Planner retries per tick (default: 1)")
    ap.add_argument("--router-retries", type=int, default=1, help="Router retries per tick (default: 1)")
    ap.add_argument("--lease-ttl", type=int, default=300, help="Lease TTL in seconds (default: 300)")
    ap.add_argument("--preflight-only", action="store_true", help="Run preflight checks and exit")
    return ap.parse_args()


def _validate_inputs(args: argparse.Namespace) -> int:
    if args.minutes > 0:
        args.ticks = args.minutes
    if args.ticks <= 0:
        print("[error] --ticks/--minutes must be > 0")
        return 2
    if args.planner_interval <= 0:
        print("[error] --planner-interval must be > 0")
        return 2
    if args.tick_seconds <= 0:
        print("[error] --tick-seconds must be > 0")
        return 2
    if args.planner_retries < 0 or args.router_retries < 0:
        print("[error] retries must be >= 0")
        return 2
    if not Path("codex_packet_handoff/tools/planner.py").exists():
        print("[error] Missing codex_packet_handoff/tools/planner.py in current cwd")
        return 2
    if not Path("codex_packet_handoff/tools/router.py").exists():
        print("[error] Missing codex_packet_handoff/tools/router.py in current cwd")
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
    out = {"processed": 0, "kicked": 0}
    for line in router_output.splitlines():
        m = ROUTER_RE.search(line)
        if not m:
            continue
        out["processed"] += int(m.group("processed"))
        kicked = m.group("kicked")
        if kicked:
            out["kicked"] += int(kicked)
    return out


def _ensure_router_config() -> None:
    cfg = Path(".codex/packet_router/config.json")
    example = Path(".codex/packet_router/example.json")
    if cfg.exists():
        return
    if example.exists():
        cfg.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(example, cfg)
        print("[preflight] created .codex/packet_router/config.json from example")

def _ensure_dirs() -> None:
    for lane in LANES:
        base = Path(".codex/packets/lanes") / lane
        (base / "inbox/feature").mkdir(parents=True, exist_ok=True)
        (base / "inbox/reviewer").mkdir(parents=True, exist_ok=True)
        (base / "outbox/integrator").mkdir(parents=True, exist_ok=True)
        (base / "archive").mkdir(parents=True, exist_ok=True)
    Path(".codex/packet_router").mkdir(parents=True, exist_ok=True)
    Path(".codex/packet_planner").mkdir(parents=True, exist_ok=True)
    Path(".codex/lane_meta").mkdir(parents=True, exist_ok=True)


def _permission_probe() -> None:
    probe = Path(".codex/packets/_coordinator_write_probe")
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


def _run_planner_with_retry(retries: int) -> Tuple[int, str, int]:
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


def _run_router_with_retry(retries: int) -> Tuple[int, str, int]:
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


def main() -> int:
    args = parse_args()
    rc = _validate_inputs(args)
    if rc != 0:
        return rc

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_file = RUNS_DIR / f"run__{run_id}.json"

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

        planner_emitted: List[Tuple[str, str]] = []
        planner_errors = 0
        router_errors = 0
        router_processed_total = 0
        fixer_kicked_total = 0
        tick_events: List[Dict[str, object]] = []

        run_start = time.time()
        print("[coordinator] phase=1 mode=legacy_subprocess_hardened")
        for tick in range(1, args.ticks + 1):
            tick_start = time.time()
            tick_event: Dict[str, object] = {
                "tick": tick,
                "started_at": utc_now(),
                "planner": None,
                "router": None,
            }
            print(f"=== TICK {tick} START {utc_now()} ===")

            if (tick - 1) % args.planner_interval == 0:
                print("[planner]")
                planner_rc, planner_out, planner_attempts = _run_planner_with_retry(args.planner_retries)
                emissions = _collect_emissions(planner_out)
                planner_emitted.extend(emissions)
                tick_event["planner"] = {
                    "rc": planner_rc,
                    "attempts": planner_attempts,
                    "emitted": [{"lane": lane, "file": fn} for lane, fn in emissions],
                }
                if planner_rc != 0:
                    planner_errors += 1
                    print(f"[planner] exit_code={planner_rc}")
                    if args.stop_on_error:
                        tick_events.append(tick_event)
                        break

            print("[router]")
            router_rc, router_out, router_attempts = _run_router_with_retry(args.router_retries)
            stats = _collect_router_stats(router_out)
            router_processed_total += stats["processed"]
            fixer_kicked_total += stats["kicked"]
            tick_event["router"] = {
                "rc": router_rc,
                "attempts": router_attempts,
                "processed": stats["processed"],
                "kicked": stats["kicked"],
            }
            if router_rc != 0:
                router_errors += 1
                print(f"[router] exit_code={router_rc}")
                if args.stop_on_error:
                    tick_events.append(tick_event)
                    break

            elapsed = time.time() - tick_start
            tick_event["duration_seconds"] = int(elapsed)
            tick_events.append(tick_event)

            sleep_for = int(args.tick_seconds - elapsed)
            if tick < args.ticks and not args.no_sleep and sleep_for > 0:
                print(f"[sleep] {sleep_for}s")
                time.sleep(sleep_for)

            print(f"=== TICK {tick} END ===")

        wall = int(time.time() - run_start)
        status = "ok" if (planner_errors == 0 and router_errors == 0) else "errors"

        run_doc: Dict[str, object] = {
            "run_id": run_id,
            "started_at": utc_now(),
            "status": status,
            "mode": "phase1_legacy_subprocess_hardened",
            "ticks": args.ticks,
            "planner_interval": args.planner_interval,
            "planner_errors": planner_errors,
            "router_errors": router_errors,
            "router_processed_total": router_processed_total,
            "fixer_kicked_total": fixer_kicked_total,
            "planner_emitted": [{"lane": lane, "file": fn} for lane, fn in planner_emitted],
            "tick_events": tick_events,
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
            },
        )

        print("=== COORDINATOR SUMMARY ===")
        print("[summary] mode: phase1_legacy_subprocess_hardened")
        if planner_emitted:
            print("[summary] planner emitted packets:")
            for lane, fn in planner_emitted:
                print(f"- lane={lane} file={fn}")
        else:
            print("[summary] planner emitted packets: none")
        print(f"[summary] router processed total packets: {router_processed_total}")
        print(f"[summary] fixer kicked total tasks: {fixer_kicked_total}")
        if not planner_emitted and router_processed_total == 0 and fixer_kicked_total == 0:
            print("[summary] no activity this cycle")
        print(f"[summary] planner errors: {planner_errors}")
        print(f"[summary] router errors: {router_errors}")
        print(f"[summary] wall seconds: {wall}")
        print(f"[summary] run artifact: {run_file}")

        return 0 if status == "ok" else 1
    finally:
        release_lease()


if __name__ == "__main__":
    raise SystemExit(main())
