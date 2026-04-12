from __future__ import annotations

import re
from pathlib import Path
from typing import Mapping, Optional

PACKET_SHA_RE = re.compile(r"__([0-9a-f]{40})__\d{8}T\d{6}Z\.md$")


def packet_sha_from_name(name: str) -> Optional[str]:
    match = PACKET_SHA_RE.search(name)
    if not match:
        return None
    return match.group(1)


def _newest_packet(directory: Path) -> Optional[Path]:
    try:
        packets = sorted(directory.glob("*.md"), key=lambda path: path.stat().st_mtime, reverse=True)
    except Exception:
        return None
    return packets[0] if packets else None


def infer_last_submitted_sha(
    lane_dir: Optional[Path],
    planner_lane_state: Optional[Mapping[str, object]] = None,
) -> Optional[str]:
    state_value = None
    if isinstance(planner_lane_state, Mapping):
        state_value = planner_lane_state.get("last_submitted_sha")
    if isinstance(state_value, str) and state_value.strip():
        return state_value.strip()

    if lane_dir is None:
        return None

    for rel in ("inbox/reviewer", "inbox/feature", "outbox/reviewer", "archive"):
        pkt = _newest_packet(lane_dir / rel)
        if not pkt:
            continue
        sha = packet_sha_from_name(pkt.name)
        if sha:
            return sha
    return None
