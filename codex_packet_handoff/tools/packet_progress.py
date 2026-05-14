from __future__ import annotations

import re
from pathlib import Path
from typing import List, Mapping, Optional, Tuple

PACKET_SHA_RE = re.compile(r"__([0-9a-f]{40})__\d{8}T\d{6}Z\.md$")
GATE_RESULT_RE = re.compile(r"^- `(?P<cmd>.+)`: (?P<status>PASS|FAIL \((?P<rc>-?\d+)\))$")


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


def _normalize_gate_results(raw: object) -> List[Tuple[str, int]]:
    out: List[Tuple[str, int]] = []
    if not isinstance(raw, list):
        return out
    for item in raw:
        if not isinstance(item, (list, tuple)) or len(item) != 2:
            continue
        cmd = str(item[0]).strip()
        if not cmd:
            continue
        try:
            rc = int(item[1])
        except Exception:
            continue
        out.append((cmd, rc))
    return out


def _parse_gate_results_from_packet(packet: Path) -> List[Tuple[str, int]]:
    try:
        lines = packet.read_text(encoding="utf-8").splitlines()
    except Exception:
        return []
    in_section = False
    results: List[Tuple[str, int]] = []
    for line in lines:
        if line.strip() == "## Commands run and outcomes":
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if not in_section:
            continue
        match = GATE_RESULT_RE.match(line.strip())
        if not match:
            continue
        cmd = match.group("cmd").strip()
        rc_text = match.group("rc")
        rc = 0 if rc_text is None else int(rc_text)
        results.append((cmd, rc))
    return results


def _parse_changed_files_from_packet(packet: Path) -> List[str]:
    try:
        lines = packet.read_text(encoding="utf-8").splitlines()
    except Exception:
        return []
    in_section = False
    files: List[str] = []
    for line in lines:
        if line.strip() == "## Files changed":
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if not in_section:
            continue
        stripped = line.strip()
        if not stripped.startswith("- `") or not stripped.endswith("`"):
            continue
        files.append(stripped[3:-1])
    return files


def infer_last_gate_results(
    lane_dir: Optional[Path],
    planner_lane_state: Optional[Mapping[str, object]] = None,
    *,
    sha: Optional[str] = None,
) -> List[Tuple[str, int]]:
    state_results = None
    if isinstance(planner_lane_state, Mapping):
        state_results = planner_lane_state.get("last_gate_results")
    normalized = _normalize_gate_results(state_results)
    if normalized:
        return normalized
    if lane_dir is None:
        return []

    candidates: List[Path] = []
    for rel in ("inbox/feature", "archive"):
        directory = lane_dir / rel
        try:
            packets = sorted(
                directory.glob("F__*.md"),
                key=lambda path: path.stat().st_mtime,
                reverse=True,
            )
        except Exception:
            continue
        for packet in packets:
            packet_sha = packet_sha_from_name(packet.name)
            if sha and packet_sha != sha:
                continue
            candidates.append(packet)
    for packet in candidates:
        parsed = _parse_gate_results_from_packet(packet)
        if parsed:
            return parsed
    return []


def infer_last_changed_files(
    lane_dir: Optional[Path],
    planner_lane_state: Optional[Mapping[str, object]] = None,
    *,
    sha: Optional[str] = None,
) -> List[str]:
    del planner_lane_state  # reserved for future state-backed snapshots
    if lane_dir is None:
        return []

    candidates: List[Path] = []
    for rel in ("inbox/feature", "archive"):
        directory = lane_dir / rel
        try:
            packets = sorted(
                directory.glob("F__*.md"),
                key=lambda path: path.stat().st_mtime,
                reverse=True,
            )
        except Exception:
            continue
        for packet in packets:
            packet_sha = packet_sha_from_name(packet.name)
            if sha and packet_sha != sha:
                continue
            candidates.append(packet)
    for packet in candidates:
        parsed = _parse_changed_files_from_packet(packet)
        if parsed:
            return parsed
    return []
