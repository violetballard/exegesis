#!/usr/bin/env python3
"""status.py — pipeline queue truth (local filesystem state only)

Prints per-lane:
- pending feature packets
- reviewer feedback packets
- approved integrator packets
- latest integrator output (if any)

This script does not inspect live Codex sessions. Pair it with:
  python packet_garden/tools/daemon_monitor.py
for reviewer/integrator live state and manual feature-session activity.

Run:
  python packet_garden/tools/status.py
"""

from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

try:
    from packet_progress import infer_last_submitted_sha
except ImportError:  # pragma: no cover - package execution fallback
    from .packet_progress import infer_last_submitted_sha

ROOT = Path('.codex/packets/lanes')
CONFIG_FILE = Path('.codex/packet_router/config.json')
PLANNER_STATE_FILE = Path('.codex/packet_planner/state.json')
FEATURE_STATE_FILE = Path('.codex/feature_runner/state.json')

@dataclass
class LaneStatus:
    lane: str
    pending_feature: List[Path]
    reviewer_notes: List[Path]
    approved_integrator: List[Path]
    integrator_outputs: List[Path]
    branch: Optional[str]
    head_sha: Optional[str]
    last_submitted_sha: Optional[str]
    state: str
    note: str
    integration_blockers: List[str]

def newest(paths: List[Path]) -> Optional[Path]:
    if not paths:
        return None
    return sorted(paths, key=lambda p: p.stat().st_mtime, reverse=True)[0]

def fmt(p: Optional[Path]) -> str:
    if not p:
        return "-"
    return p.name

def _load_json(path: Path, default: Dict) -> Dict:
    try:
        return json.loads(path.read_text())
    except Exception:
        return default

def _branch_head_sha(branch: Optional[str]) -> Optional[str]:
    if not branch:
        return None
    try:
        out = subprocess.check_output(["git", "rev-parse", branch], text=True, stderr=subprocess.DEVNULL).strip()
        return out or None
    except Exception:
        return None


def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _feature_thread_state() -> Dict[str, Dict]:
    state = _load_json(FEATURE_STATE_FILE, {})
    lanes = state.get("lanes") if isinstance(state, dict) else {}
    return lanes if isinstance(lanes, dict) else {}


def _feature_session_active(lane: str) -> bool:
    lane_state = _feature_thread_state().get(lane)
    if isinstance(lane_state, dict):
        status = str(lane_state.get("status") or "")
        if status in {"managed_thread", "launching"}:
            return True
        if status == "direct_exec_running":
            return _pid_alive(int(lane_state.get("pid") or 0))
    return False


def _integrator_dependency_blockers(lane_dir: Path, approval_packet: Path) -> List[str]:
    """Return integration dependency blockers using the router's merge policy."""
    try:
        try:
            from router import (  # type: ignore
                _integration_dependency_blockers,
                _reviewed_files_for_integrator_packet,
                load_cfg,
            )
        except ImportError:  # pragma: no cover - package execution fallback
            from .router import (  # type: ignore
                _integration_dependency_blockers,
                _reviewed_files_for_integrator_packet,
                load_cfg,
            )
        approved_text = approval_packet.read_text(errors="ignore")
        reviewed_files = _reviewed_files_for_integrator_packet(lane_dir, approval_packet, approved_text)
        return _integration_dependency_blockers(
            load_cfg(),
            str(Path.cwd()),
            lane_dir.name,
            reviewed_files=reviewed_files,
        )
    except Exception:
        return []


def _derive_lane_state(
    pending: List[Path],
    reviewer: List[Path],
    approved: List[Path],
    head_sha: Optional[str],
    last_submitted_sha: Optional[str],
    feature_active: bool = False,
    integration_blockers: Optional[List[str]] = None,
) -> tuple[str, str]:
    if approved:
        if integration_blockers:
            return (
                "integration_blocked",
                "approved packet held for prerequisite lane(s): " + ", ".join(integration_blockers),
            )
        return ("ready_for_integrator", "approved packet waiting for integrator")
    if pending:
        return ("pending_review", "feature packet waiting for reviewer")
    if reviewer:
        if head_sha and last_submitted_sha and head_sha != last_submitted_sha:
            return ("ready_for_reemit", "review notes present, lane advanced, planner should re-emit")
        return ("waiting_feature_update", "review notes present, lane has not advanced yet")
    if feature_active:
        return ("feature_in_progress", "feature lane is actively working on the next handoff")
    return ("idle", "no pending/review/approved packets")

def scan_lane(lane_dir: Path, lane_cfg: Dict, planner_lane_state: Dict) -> LaneStatus:
    lane = lane_dir.name
    pending = sorted(p for p in (lane_dir/'inbox/feature').glob('*.md') if not p.name.endswith('.shared.md'))
    reviewer = sorted((lane_dir/'inbox/reviewer').glob('*.md'))
    approved = sorted((lane_dir/'outbox/integrator').glob('*.md'))
    integ = sorted((lane_dir/'archive').glob('INTEGRATOR__*.md'))
    branch = (lane_cfg or {}).get("branch")
    head_sha = _branch_head_sha(branch)
    last_submitted_sha = infer_last_submitted_sha(lane_dir, planner_lane_state)
    if not bool((lane_cfg or {}).get("enabled", True)):
        state, note = ("disabled", "lane disabled in router config")
    else:
        integration_blockers = sorted(
            {
                blocker
                for approval_packet in approved
                for blocker in _integrator_dependency_blockers(lane_dir, approval_packet)
            }
        )
        state, note = _derive_lane_state(
            pending,
            reviewer,
            approved,
            head_sha,
            last_submitted_sha,
            _feature_session_active(lane),
            integration_blockers,
        )
    if not bool((lane_cfg or {}).get("enabled", True)):
        integration_blockers = []
    return LaneStatus(
        lane,
        pending,
        reviewer,
        approved,
        integ,
        branch,
        head_sha,
        last_submitted_sha,
        state,
        note,
        integration_blockers,
    )

def main() -> None:
    if not ROOT.exists():
        print('No .codex/packets/lanes found. Run setup.py first.')
        return

    cfg = _load_json(CONFIG_FILE, {})
    lane_cfg_map = (cfg.get("lanes") or {}) if isinstance(cfg, dict) else {}
    configured_names = list(lane_cfg_map.keys()) if isinstance(lane_cfg_map, dict) and lane_cfg_map else []
    if configured_names:
        lanes = [ROOT / name for name in configured_names]
    else:
        lanes = sorted([p for p in ROOT.iterdir() if p.is_dir()], key=lambda p: p.name)
    if not lanes:
        print('No lanes found under .codex/packets/lanes.')
        return

    inline_fixer = bool(cfg.get("inline_fixer", False)) if isinstance(cfg, dict) else False
    backlog_fixer = bool(cfg.get("kick_fixers_on_reviewer_backlog", True)) if isinstance(cfg, dict) else True
    max_packets_per_run = int(cfg.get("max_packets_per_run", 1)) if isinstance(cfg, dict) else 1
    planner_state = _load_json(PLANNER_STATE_FILE, {})
    planner_lane_state_map = (planner_state.get("lanes") or {}) if isinstance(planner_state, dict) else {}

    statuses = [
        scan_lane(ld, lane_cfg_map.get(ld.name, {}), planner_lane_state_map.get(ld.name, {}))
        for ld in lanes
    ]

    # Header
    print('PIPELINE STATUS (filesystem truth only)\n')
    total_pending = sum(len(s.pending_feature) for s in statuses)
    total_review = sum(len(s.reviewer_notes) for s in statuses)
    total_approved = sum(len(s.approved_integrator) for s in statuses)
    total_waiting_feature = sum(1 for s in statuses if s.state == "waiting_feature_update")
    total_ready_reemit = sum(1 for s in statuses if s.state == "ready_for_reemit")
    print(
        "Totals: "
        f"pending_feature={total_pending}  "
        f"reviewer_notes={total_review}  "
        f"approved_for_integrator={total_approved}  "
        f"waiting_feature_update={total_waiting_feature}  "
        f"ready_for_reemit={total_ready_reemit}\n"
    )
    print(
        f"Router config: inline_fixer={inline_fixer}  "
        f"kick_fixers_on_reviewer_backlog={backlog_fixer}  "
        f"max_packets_per_run={max_packets_per_run}\n"
    )

    # Table-ish output
    print(
        f"{'lane':22}  {'pending':7}  {'review':6}  {'approved':8}  "
        f"{'state':20}  {'head':8}  {'last_sub':8}  "
        f"{'latest review':34}  {'latest integrator':34}"
    )
    print('-' * 190)
    for s in statuses:
        lr = newest(s.reviewer_notes)
        li = newest(s.integrator_outputs)
        head_short = (s.head_sha or "-")[:8]
        last_short = (s.last_submitted_sha or "-")[:8]
        print(
            f"{s.lane:22}  {len(s.pending_feature):7d}  {len(s.reviewer_notes):6d}  {len(s.approved_integrator):8d}  "
            f"{s.state:20}  {head_short:8}  {last_short:8}  "
            f"{fmt(lr):34}  {fmt(li):34}"
        )
        if s.note:
            print(f"{'':22}  note: {s.note}")

    print('\nHints:')
    print('- If pending>0 and review=0: router likely hasn\'t run recently or is blocked waiting on Codex.')
    print('- If state=feature_in_progress: no queue packet is waiting because the feature lane is actively working.')
    print('- If state=waiting_feature_update: lane branch has not advanced since reviewer notes.')
    print('- If state=ready_for_reemit: lane advanced and planner should emit a new feature packet.')
    print('- If approved>0 and state=ready_for_integrator: integrator run should fire; check INTEGRATOR__ outputs in archive.')
    print('- If approved>0 and state=integration_blocked: approved packet is waiting for prerequisite lane integration, not a stuck integrator.')
    print('- Queue truth beats daemon-log chatter: stale scope-check text in older logs does not mean a live scope-check blocker.')
    print('- This script ignores live reviewer/integrator sessions and manual feature-lane sessions by design.')
    print('- For the full dashboard, also run daemon_monitor.py.')
    if total_waiting_feature > 0 and (not inline_fixer or not backlog_fixer):
        print('- auto-fixer handback is disabled by router config; reviewer notes may wait for manual feature commits.')

if __name__ == '__main__':
    main()
