#!/usr/bin/env python3
"""status.py — quick pipeline status summary (local filesystem truth)

Prints per-lane:
- pending feature packets
- reviewer feedback packets
- lane action packets
- approved integrator packets
- latest integrator output (if any)

Run:
  python codex_packet_handoff/tools/status.py
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

ROOT = Path('.codex/packets/lanes')

@dataclass
class LaneStatus:
    lane: str
    pending_feature: List[Path]
    reviewer_notes: List[Path]
    lane_actions: List[Path]
    approved_integrator: List[Path]
    integrator_outputs: List[Path]

def newest(paths: List[Path]) -> Optional[Path]:
    if not paths:
        return None
    return sorted(paths, key=lambda p: p.stat().st_mtime, reverse=True)[0]

def fmt(p: Optional[Path]) -> str:
    if not p:
        return "-"
    return p.name

def scan_lane(lane_dir: Path) -> LaneStatus:
    lane = lane_dir.name
    pending = sorted((lane_dir/'inbox/feature').glob('*.md'))
    reviewer = sorted((lane_dir/'inbox/reviewer').glob('*.md'))
    lane_actions = sorted((lane_dir/'outbox/lane').glob('*.md'))
    approved = sorted((lane_dir/'outbox/integrator').glob('*.md'))
    integ = sorted((lane_dir/'archive').glob('INTEGRATOR__*.md'))
    return LaneStatus(lane, pending, reviewer, lane_actions, approved, integ)

def main() -> None:
    if not ROOT.exists():
        print('No .codex/packets/lanes found. Run setup.py first.')
        return

    lanes = sorted([p for p in ROOT.iterdir() if p.is_dir()], key=lambda p: p.name)
    if not lanes:
        print('No lanes found under .codex/packets/lanes.')
        return

    statuses = [scan_lane(ld) for ld in lanes]

    # Header
    print('PIPELINE STATUS (filesystem truth)\n')
    total_pending = sum(len(s.pending_feature) for s in statuses)
    total_review = sum(len(s.reviewer_notes) for s in statuses)
    total_lane_actions = sum(len(s.lane_actions) for s in statuses)
    total_approved = sum(len(s.approved_integrator) for s in statuses)
    print(
        "Totals: "
        f"pending_feature={total_pending}  "
        f"reviewer_notes={total_review}  "
        f"lane_actions={total_lane_actions}  "
        f"approved_for_integrator={total_approved}\n"
    )

    # Table-ish output
    print(
        f"{'lane':28}  {'pending':7}  {'review':6}  {'action':6}  "
        f"{'approved':8}  {'latest pending':34}  {'latest review':34}  "
        f"{'latest action':34}  {'latest approved':34}  {'latest integrator':34}"
    )
    print('-'*180)
    for s in statuses:
        lp = newest(s.pending_feature)
        lr = newest(s.reviewer_notes)
        lx = newest(s.lane_actions)
        la = newest(s.approved_integrator)
        li = newest(s.integrator_outputs)
        print(
            f"{s.lane:28}  {len(s.pending_feature):7d}  {len(s.reviewer_notes):6d}  "
            f"{len(s.lane_actions):6d}  {len(s.approved_integrator):8d}  {fmt(lp):34}  "
            f"{fmt(lr):34}  {fmt(lx):34}  {fmt(la):34}  {fmt(li):34}"
        )

    print('\nHints:')
    print('- If pending>0 and review=0: router likely hasn\'t run recently or is blocked waiting on Codex.')
    print('- If review>0 or action>0: lane needs changes (or reviewer is asking for clarification).')
    print('- If approved>0: integrator run should fire; check for INTEGRATOR__ outputs in archive.')

if __name__ == '__main__':
    main()
