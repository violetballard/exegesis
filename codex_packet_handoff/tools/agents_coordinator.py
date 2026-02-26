#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

PLANNER_CMD = [sys.executable, "codex_packet_handoff/tools/planner.py"]
ROUTER_CMD = [sys.executable, "codex_packet_handoff/tools/router.py"]
EMITTED_RE = re.compile(r"\[planner\] emitted (?P<path>\S+)")
ROUTER_RE = re.compile(
    r"\[router\]\s+processed\s+(?P<processed>\d+)\s+packet\(s\)(?:,\s+kicked\s+(?P<kicked>\d+)\s+reviewer-fixer task\(s\))?"
)
LANE_FILE_RE = re.compile(
    r"\.codex/packets/lanes/(?P<lane>[^/]+)/inbox/feature/(?P<filename>[^/\s]+\.md)"
)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_cmd(cmd: List[str]) -> Tuple[int, str]:
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    out = p.stdout or ""
    if out:
        print(out, end="" if out.endswith("\n") else "\n")
    return p.returncode, out


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description=(
            "Phase 1 Agents SDK coordinator wrapper. "
            "Runs planner/router cadence while preserving packet/state compatibility."
        )
    )
    ap.add_argument("--ticks", type=int, default=50, help="Total number of ticks (default: 50)")
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
    ap.add_argument(
        "--no-sleep",
        action="store_true",
        help="Do not sleep between ticks (useful for dry/dev checks)",
    )
    ap.add_argument(
        "--stop-on-error",
        action="store_true",
        help="Exit immediately if planner/router returns non-zero",
    )
    return ap.parse_args()


def _validate_inputs(args: argparse.Namespace) -> int:
    if args.ticks <= 0:
        print("[error] --ticks must be > 0")
        return 2
    if args.planner_interval <= 0:
        print("[error] --planner-interval must be > 0")
        return 2
    if args.tick_seconds <= 0:
        print("[error] --tick-seconds must be > 0")
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


def main() -> int:
    args = parse_args()
    rc = _validate_inputs(args)
    if rc != 0:
        return rc

    planner_emitted: List[Tuple[str, str]] = []
    planner_errors = 0
    router_errors = 0
    router_processed_total = 0
    fixer_kicked_total = 0

    run_start = time.time()
    print("[coordinator] phase=1 mode=legacy_subprocess")
    for tick in range(1, args.ticks + 1):
        tick_start = time.time()
        print(f"=== TICK {tick} START {utc_now()} ===")

        if (tick - 1) % args.planner_interval == 0:
            print("[planner]")
            planner_rc, planner_out = run_cmd(PLANNER_CMD)
            planner_emitted.extend(_collect_emissions(planner_out))
            if planner_rc != 0:
                planner_errors += 1
                print(f"[planner] exit_code={planner_rc}")
                if args.stop_on_error:
                    return planner_rc

        print("[router]")
        router_rc, router_out = run_cmd(ROUTER_CMD)
        stats = _collect_router_stats(router_out)
        router_processed_total += stats["processed"]
        fixer_kicked_total += stats["kicked"]
        if router_rc != 0:
            router_errors += 1
            print(f"[router] exit_code={router_rc}")
            if args.stop_on_error:
                return router_rc

        elapsed = time.time() - tick_start
        sleep_for = int(args.tick_seconds - elapsed)
        if tick < args.ticks and not args.no_sleep and sleep_for > 0:
            print(f"[sleep] {sleep_for}s")
            time.sleep(sleep_for)

        print(f"=== TICK {tick} END ===")

    wall = int(time.time() - run_start)
    print("=== COORDINATOR SUMMARY ===")
    print("[summary] mode: phase1_legacy_subprocess")
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
    return 0 if (planner_errors == 0 and router_errors == 0) else 1


if __name__ == "__main__":
    raise SystemExit(main())

