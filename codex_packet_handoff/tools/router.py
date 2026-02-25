#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import time
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from codex_mcp_client import ApprovalPolicy, CodexMcpClient

PACKETS_ROOT = Path(".codex/packets/lanes")
ROUTER_ROOT = Path(".codex/packet_router")
STATE_FILE = ROUTER_ROOT / "state.json"
CONFIG_FILE = ROUTER_ROOT / "config.json"
CURSOR_FILE = ROUTER_ROOT / "cursor.json"
LEASE_FILE = ROUTER_ROOT / "lease.json"

VERDICT_RE = re.compile(r"Verdict:\s*`(APPROVED|CHANGES_REQUESTED|CHANGES REQUESTED)`", re.IGNORECASE)

@dataclass
class RouterConfig:
    model: str
    codex_cmd: str
    reviewer_timeout: float
    integrator_timeout: float
    max_packets_per_run: int
    inline_fixer: bool
    kick_fixers_on_reviewer_backlog: bool
    lanes: Dict[str, Dict[str, Any]]

def load_json(p: Path, default: Any) -> Any:
    try:
        return json.loads(p.read_text())
    except Exception:
        return default

def save_json(p: Path, data: Any) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))

def acquire_lease(ttl: int = 20) -> bool:
    now = time.time()
    if LEASE_FILE.exists():
        d = load_json(LEASE_FILE, {})
        if now - float(d.get("ts", 0)) < ttl:
            return False
    save_json(LEASE_FILE, {"ts": now, "pid": os.getpid()})
    return True

def release_lease() -> None:
    try:
        if LEASE_FILE.exists():
            LEASE_FILE.unlink()
    except Exception:
        pass

def load_cfg() -> RouterConfig:
    cfg = load_json(CONFIG_FILE, None)
    if not cfg:
        raise SystemExit(f"Missing {CONFIG_FILE} (copy example.json).")
    return RouterConfig(
        model=str(cfg.get("model", "gpt-5.1-codex")),
        codex_cmd=str(cfg.get("codex_cmd", "codex")),
        reviewer_timeout=float(cfg.get("reviewer_timeout", 180)),
        integrator_timeout=float(cfg.get("integrator_timeout", 900)),
        max_packets_per_run=int(cfg.get("max_packets_per_run", 1)),
        inline_fixer=bool(cfg.get("inline_fixer", False)),
        kick_fixers_on_reviewer_backlog=bool(cfg.get("kick_fixers_on_reviewer_backlog", True)),
        lanes=dict(cfg.get("lanes", {})),
    )

def ensure_lane_dirs(lane: str) -> Path:
    d = PACKETS_ROOT / lane
    (d/"inbox/feature").mkdir(parents=True, exist_ok=True)
    (d/"inbox/reviewer").mkdir(parents=True, exist_ok=True)
    (d/"outbox/integrator").mkdir(parents=True, exist_ok=True)
    (d/"archive").mkdir(parents=True, exist_ok=True)
    return d

def list_new(lane_dir: Path, last_seen: Optional[str]) -> List[Path]:
    files = sorted((lane_dir/"inbox/feature").glob("*.md"), key=lambda p: p.stat().st_mtime)
    if not last_seen:
        return files[-1:] if files else []
    out: List[Path] = []
    seen = False
    for f in files:
        if seen:
            out.append(f)
        if f.name == last_seen:
            seen = True
    return out

def parse_verdict(text: str) -> str:
    m = VERDICT_RE.search(text or "")
    if not m:
        return "CHANGES_REQUESTED"
    v = m.group(1).upper().replace(" ", "_")
    return "APPROVED" if v == "APPROVED" else "CHANGES_REQUESTED"

def reviewer_prompt(pkt: str) -> str:
    return (
        "You are the REVIEWER. You are sandboxed read-only and MUST NOT modify files.\n"
        "You MUST enforce plan alignment by reading: ROADMAP.md, PRODUCT_VISION.md, ARCHITECTURE.md, INTEGRATION.md, AGENTS.md.\n"
        "If roadmap/vision mapping is unclear or off-plan, output CHANGES_REQUESTED with concrete scope-tightening.\n\n"
        "Output exactly one markdown packet with sections:\n"
        "1. Verdict: `APPROVED` or `CHANGES_REQUESTED`\n"
        "2. Findings (highest severity first)\n"
        "3. Missing handoff fields (if any)\n"
        "4. Required fixes before re-review (numbered, actionable)\n"
        "5. If approved: merge order + any post-merge checks (include merge risk)\n\n"
        f"Review this feature packet:\n\n{pkt}\n"
    )

def integrator_prompt(approved: str) -> str:
    return (
        "You are the INTEGRATOR. You may write to the workspace.\n"
        "Consume this APPROVED packet, perform merge order + post-merge checks, report blockers.\n\n"
        f"{approved}\n"
    )

def _find_worktree_for_branch(repo_cwd: str, branch: str) -> Optional[str]:
    # Normalize to refs/heads/...
    ref = branch
    if ref.startswith("refs/heads/"):
        want = ref
    else:
        want = f"refs/heads/{ref}"
    p = subprocess.run(["git","worktree","list","--porcelain"], cwd=repo_cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if p.returncode != 0:
        return None
    blocks = p.stdout.split("\n\n")
    for b in blocks:
        wt = None
        br = None
        for ln in [x.strip() for x in b.splitlines() if x.strip()]:
            if ln.startswith("worktree "):
                wt = ln.split(" ",1)[1].strip()
            elif ln.startswith("branch "):
                br = ln.split(" ",1)[1].strip()
        if wt and br and br == want:
            return wt
    return None

def fixer_prompt(lane: str, branch: str, reviewer_packet: str, workdir: Optional[str]) -> str:
    if workdir:
        return (
            f"You are the FEATURE FIXER for lane `{lane}`.\n"
            f"Apply the reviewer's REQUIRED FIXES to branch `{branch}`.\n\n"
            f"You are running inside the lane worktree at: {workdir}\n"
            "That worktree already has the branch checked out, so DO NOT detach or update-ref.\n"
            "Edit files, run gates, and commit normally.\n\n"
            "Run: make scope-check; ./quality-format.sh --check; ./quality-lint.sh; ./quality-test.sh; ./typecheck-test.sh; make ci\n\n"
            "Deliverable: a new commit that addresses the numbered required fixes, plus the final HEAD SHA.\n\n"
            "Reviewer packet to satisfy:\n\n"
            f"{reviewer_packet}\n"
        )
    return (
        f"You are the FEATURE FIXER for lane `{lane}`.\n"
        f"Apply the reviewer's REQUIRED FIXES to branch `{branch}`.\n\n"
        "Fallback: branch is checked out elsewhere.\n"
        "Resolve branch -> SHA, detach at SHA, make changes, commit, then update local branch ref:\n"
        "  git update-ref refs/heads/<branch> HEAD\n\n"
        "Run: make scope-check; ./quality-format.sh --check; ./quality-lint.sh; ./quality-test.sh; ./typecheck-test.sh; make ci\n\n"
        "Reviewer packet to satisfy:\n\n"
        f"{reviewer_packet}\n"
    )

def run_fixer(client: CodexMcpClient, cfg: RouterConfig, state: dict, lane: str, reviewer_packet: str, repo_cwd: str) -> dict:
    lane_cfg = cfg.lanes.get(lane, {}) or {}
    branch = str(lane_cfg.get("branch") or f"codex/{lane}")
    wt = _find_worktree_for_branch(repo_cwd, branch)
    fixer_map = state.get("fixer_thread_ids") or {}
    tid = fixer_map.get(lane)
    if not tid:
        tid, _ = client.codex(
            prompt=f"You are the FEATURE FIXER for lane `{lane}`. You will apply reviewer-required fixes.",
            cwd=(wt or repo_cwd),
            sandbox="workspace-write",
            approval_policy="on-request",
            model=cfg.model,
            timeout=cfg.integrator_timeout,
        )
    tid, _ = client.codex_reply(tid, fixer_prompt(lane, branch, reviewer_packet, wt), timeout=cfg.integrator_timeout)
    fixer_map[lane] = tid
    state["fixer_thread_ids"] = fixer_map
    return state

def write_text(p: Path, t: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(t)

def archive(src: Path, lane_dir: Path) -> None:
    dst = lane_dir/"archive"/src.name
    try:
        src.rename(dst)
    except Exception:
        dst.write_text(src.read_text())
        src.unlink()

def process_once(client: CodexMcpClient, cfg: RouterConfig, state: dict, repo_cwd: str, reviewer_tid: str, integrator_tid: str) -> Tuple[int, dict, str, str]:
    cursor = load_json(CURSOR_FILE, {})
    processed = 0
    for lane in cfg.lanes.keys():
        lane_dir = ensure_lane_dirs(lane)
        for pkt_path in list_new(lane_dir, cursor.get(lane)):
            if processed >= cfg.max_packets_per_run:
                return processed, state, reviewer_tid, integrator_tid
            pkt = pkt_path.read_text()

            reviewer_tid, reviewer_text = client.codex_reply(reviewer_tid, reviewer_prompt(pkt), timeout=cfg.reviewer_timeout)
            verdict = parse_verdict(reviewer_text)

            if verdict == "APPROVED":
                write_text(lane_dir/"outbox/integrator"/pkt_path.name.replace("F__","R__APPROVED__"), reviewer_text)
                integrator_tid, integ = client.codex_reply(integrator_tid, integrator_prompt(reviewer_text), timeout=cfg.integrator_timeout)
                if integ.strip():
                    write_text(lane_dir/"archive"/f"INTEGRATOR__{pkt_path.name}", integ)
            else:
                outp = lane_dir/"inbox/reviewer"/pkt_path.name.replace("F__","R__CHANGES__")
                write_text(outp, reviewer_text)

            cursor[lane] = pkt_path.name
            save_json(CURSOR_FILE, cursor)
            archive(pkt_path, lane_dir)
            processed += 1

            # Inline fixer can be expensive; disabled by default for automation ticks.
            if verdict != "APPROVED" and cfg.inline_fixer:
                state = run_fixer(client, cfg, state, lane, reviewer_text, repo_cwd)
    return processed, state, reviewer_tid, integrator_tid

def process_reviewer_backlog(
    client: CodexMcpClient,
    cfg: RouterConfig,
    state: dict,
    repo_cwd: str,
) -> Tuple[int, dict]:
    """If inline fixer is enabled, kick feature fixers for reviewer backlog packets.

    This handles the "stuck in reviewer notes with no new feature packet" state.
    One kick per lane per newest reviewer packet filename.
    """
    if not cfg.inline_fixer or not cfg.kick_fixers_on_reviewer_backlog:
        return 0, state

    cursor = state.get("reviewer_fixer_cursor") or {}
    kicked = 0
    for lane in cfg.lanes.keys():
        lane_dir = ensure_lane_dirs(lane)
        # Do not interfere if there are fresh feature packets waiting for reviewer.
        if any((lane_dir / "inbox/feature").glob("*.md")):
            continue
        notes = sorted((lane_dir / "inbox/reviewer").glob("*.md"), key=lambda p: p.stat().st_mtime)
        if not notes:
            continue
        newest_note = notes[-1]
        if cursor.get(lane) == newest_note.name:
            continue
        try:
            reviewer_packet = newest_note.read_text()
        except Exception:
            continue
        state = run_fixer(client, cfg, state, lane, reviewer_packet, repo_cwd)
        cursor[lane] = newest_note.name
        kicked += 1

    state["reviewer_fixer_cursor"] = cursor
    return kicked, state

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--daemon", action="store_true")
    args = ap.parse_args()

    cfg = load_cfg()
    state = load_json(STATE_FILE, {})
    repo_cwd = str(Path.cwd())

    client = CodexMcpClient(approval=ApprovalPolicy(True, True), codex_cmd=cfg.codex_cmd)

    reviewer_tid = state.get("reviewer_thread_id")
    integrator_tid = state.get("integrator_thread_id")

    if not reviewer_tid:
        reviewer_tid, _ = client.codex(
            prompt="Ready as reviewer; I won't modify files.",
            cwd=repo_cwd,
            sandbox="read-only",
            approval_policy="on-request",
            model=cfg.model,
            timeout=cfg.reviewer_timeout,
        )
    if not integrator_tid:
        integrator_tid, _ = client.codex(
            prompt="Ready as integrator.",
            cwd=repo_cwd,
            sandbox="workspace-write",
            approval_policy="on-request",
            model=cfg.model,
            timeout=cfg.integrator_timeout,
        )

    state["reviewer_thread_id"] = reviewer_tid
    state["integrator_thread_id"] = integrator_tid
    save_json(STATE_FILE, state)

    for lane in cfg.lanes.keys():
        ensure_lane_dirs(lane)

    try:
        if not args.daemon:
            if acquire_lease():
                try:
                    n, state, reviewer_tid, integrator_tid = process_once(client, cfg, state, repo_cwd, reviewer_tid, integrator_tid)
                    kicked, state = process_reviewer_backlog(client, cfg, state, repo_cwd)
                    state["reviewer_thread_id"] = reviewer_tid
                    state["integrator_thread_id"] = integrator_tid
                    save_json(STATE_FILE, state)
                    print(f"[router] processed {n} packet(s), kicked {kicked} reviewer-fixer task(s)")
                finally:
                    release_lease()
            return

        print("[router] daemon mode")
        while True:
            if acquire_lease():
                try:
                    n, state, reviewer_tid, integrator_tid = process_once(client, cfg, state, repo_cwd, reviewer_tid, integrator_tid)
                    kicked, state = process_reviewer_backlog(client, cfg, state, repo_cwd)
                    state["reviewer_thread_id"] = reviewer_tid
                    state["integrator_thread_id"] = integrator_tid
                    save_json(STATE_FILE, state)
                    if n or kicked:
                        print(f"[router] processed {n} packet(s), kicked {kicked} reviewer-fixer task(s)")
                finally:
                    release_lease()
            time.sleep(0.5)
    finally:
        client.close()

if __name__ == "__main__":
    main()
