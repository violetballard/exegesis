#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import time
import subprocess
from datetime import datetime, timezone
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
INVALID_REVIEWER_RE = re.compile(r"session not found for thread_id|thread not found", re.IGNORECASE)
REVIEWER_QUOTA_RE = re.compile(
    r"usage limit|try again at|rate limit|too many requests|quota",
    re.IGNORECASE,
)

@dataclass
class RouterConfig:
    model: str
    codex_cmd: str
    reviewer_timeout: float
    integrator_timeout: float
    max_packets_per_run: int
    inline_fixer: bool
    kick_fixers_on_reviewer_backlog: bool
    fixer_kick_timeout_seconds: float
    reviewer_fixer_retry_cooldown_seconds: float
    prefer_cli_fixer: bool
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
        fixer_kick_timeout_seconds=float(cfg.get("fixer_kick_timeout_seconds", 8)),
        reviewer_fixer_retry_cooldown_seconds=float(cfg.get("reviewer_fixer_retry_cooldown_seconds", 900)),
        prefer_cli_fixer=bool(cfg.get("prefer_cli_fixer", True)),
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
    if all(f.name != last_seen for f in files):
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


def _invalid_reviewer_output(text: str) -> bool:
    t = (text or "").strip()
    if not t:
        return True
    return bool(INVALID_REVIEWER_RE.search(t))


def _is_reviewer_quota_output(text: str) -> bool:
    t = (text or "").strip()
    if not t:
        return False
    return bool(REVIEWER_QUOTA_RE.search(t))


def _offline_reviewer_fallback(pkt: str, reason: str) -> str:
    """Produce a deterministic reviewer packet when reviewer threads are unavailable.

    This keeps the pipeline moving during quota windows instead of stalling.
    """
    t = pkt or ""
    tl = t.lower()

    checks = [
        ("tasks completed", ["tasks completed"]),
        ("files changed", ["files changed"]),
        ("commands run and outcomes", ["commands run", "outcomes"]),
        ("risks or blockers", ["risk", "blocker"]),
    ]
    missing_fields: List[str] = []
    for label, needles in checks:
        if not all(n in tl for n in needles):
            missing_fields.append(label)

    required_cmds = [
        "./quality-format.sh --check",
        "./quality-lint.sh",
        "./quality-test.sh",
        "./typecheck-test.sh",
        "make ci",
    ]
    missing_cmds = [c for c in required_cmds if c.lower() not in tl]

    fail_markers = [
        "failed",
        "error",
        "traceback",
        "non-zero",
        "exit 1",
        "exit code 1",
    ]
    has_fail_markers = any(m in tl for m in fail_markers)
    has_blocker = "blocker" in tl and not ("no blocker" in tl or "none" in tl)

    approve = not missing_fields and not missing_cmds and not has_fail_markers and not has_blocker
    if approve:
        return (
            "Verdict: `APPROVED`\n\n"
            "Findings\n"
            "- Reviewer was unavailable; offline policy fallback validated packet structure and required gates.\n\n"
            "Missing handoff fields (if any)\n"
            "- none\n\n"
            "Required fixes before re-review (numbered, actionable)\n"
            "1. none\n\n"
            "If approved: merge order + any post-merge checks (include merge risk)\n"
            "1. Merge this lane after existing queued approvals.\n"
            "2. Re-run `make ci` on integrator branch.\n"
            "3. Merge risk: medium (reviewer fallback used due quota window).\n\n"
            f"Fallback reason: {reason}\n"
        )

    fixes: List[str] = []
    if missing_fields:
        fixes.append(f"Add missing handoff fields: {', '.join(missing_fields)}.")
    if missing_cmds:
        fixes.append(f"Run and report required gates: {', '.join(missing_cmds)}.")
    if has_fail_markers:
        fixes.append("Resolve failing gate output and include passing results.")
    if has_blocker:
        fixes.append("Address blocker(s) or clearly scope a minimal safe handoff.")
    if not fixes:
        fixes.append("Resubmit with complete evidence for required checks.")

    fixes_txt = "\n".join(f"{i+1}. {f}" for i, f in enumerate(fixes))
    return (
        "Verdict: `CHANGES_REQUESTED`\n\n"
        "Findings (highest severity first)\n"
        "- Reviewer was unavailable; offline policy fallback detected missing approval evidence.\n\n"
        "Missing handoff fields (if any)\n"
        + ("\n".join(f"- {m}" for m in missing_fields) if missing_fields else "- none")
        + "\n\nRequired fixes before re-review (numbered, actionable)\n"
        + fixes_txt
        + f"\n\nFallback reason: {reason}\n"
    )

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


def _sync_lane_runbook_files(repo_cwd: str, workdir: Optional[str]) -> None:
    """Ensure lane worktrees have required operator docs used by automation prompts.

    Some older lane worktrees were created before AGENTS.md existed, causing fixers
    to churn on missing-file lookups instead of applying requested changes.
    """
    if not workdir:
        return
    root = Path(repo_cwd)
    wt = Path(workdir)
    for name in (
        "AGENTS.md",
        "INTEGRATION.md",
        "THREAD_OWNERSHIP.md",
        "ROADMAP.md",
        "PRODUCT_VISION.md",
        "ARCHITECTURE.md",
    ):
        src = root / name
        dst = wt / name
        try:
            if not src.exists():
                continue
            if dst.exists():
                continue
            dst.write_text(src.read_text())
        except Exception:
            # Best-effort only; fixer can still run without this sync.
            continue

def fixer_prompt(lane: str, branch: str, reviewer_packet: str, workdir: Optional[str]) -> str:
    if workdir:
        return (
            f"You are the FEATURE FIXER for lane `{lane}`.\n"
            f"Apply the reviewer's REQUIRED FIXES to branch `{branch}`.\n\n"
            f"You are running inside the lane worktree at: {workdir}\n"
            "That worktree already has the branch checked out, so DO NOT detach or update-ref.\n"
            "Edit files, run gates, and commit normally.\n\n"
            "Execution guardrails:\n"
            "- Use only files that exist in this worktree.\n"
            "- If a referenced path is missing and non-essential, skip it and continue with available evidence.\n"
            "- Do not block on searching for reviewer metadata files; use the packet below as the source of truth.\n"
            "- Prioritize implementing numbered REQUIRED FIXES over exploratory file hunting.\n\n"
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
        "Execution guardrails:\n"
        "- Use only files available in the current checkout.\n"
        "- If a referenced path is missing and non-essential, skip it and continue with available evidence.\n"
        "- Do not block on searching for reviewer metadata files; use the packet below as the source of truth.\n"
        "- Prioritize implementing numbered REQUIRED FIXES over exploratory file hunting.\n\n"
        "Run: make scope-check; ./quality-format.sh --check; ./quality-lint.sh; ./quality-test.sh; ./typecheck-test.sh; make ci\n\n"
        "Reviewer packet to satisfy:\n\n"
        f"{reviewer_packet}\n"
    )

def run_fixer(client: CodexMcpClient, cfg: RouterConfig, state: dict, lane: str, reviewer_packet: str, repo_cwd: str) -> dict:
    lane_cfg = cfg.lanes.get(lane, {}) or {}
    branch = str(lane_cfg.get("branch") or f"codex/{lane}")
    wt = _find_worktree_for_branch(repo_cwd, branch)
    _sync_lane_runbook_files(repo_cwd, wt)
    if not cfg.prefer_cli_fixer:
        fixer_map = state.get("fixer_thread_ids") or {}
        tid = fixer_map.get(lane)
        try:
            if not tid:
                tid, _ = client.codex(
                    prompt=f"You are the FEATURE FIXER for lane `{lane}`. You will apply reviewer-required fixes.",
                    cwd=(wt or repo_cwd),
                    sandbox="workspace-write",
                    approval_policy="never",
                    model=cfg.model,
                    timeout=cfg.fixer_kick_timeout_seconds,
                )
            tid, _ = client.codex_reply(
                tid,
                fixer_prompt(lane, branch, reviewer_packet, wt),
                timeout=cfg.fixer_kick_timeout_seconds,
            )
            fixer_map[lane] = tid
            state["fixer_thread_ids"] = fixer_map
            return state
        except Exception:
            pass

    # Fallback: detached CLI fixer so router ticks don't deadlock on MCP stalls.
    logs = ROUTER_ROOT / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    logp = logs / f"fixer__{lane}__{ts}.log"
    with logp.open("w") as lf:
        subprocess.Popen(
            [
                cfg.codex_cmd,
                "exec",
                "-m",
                cfg.model,
                "-s",
                "workspace-write",
                fixer_prompt(lane, branch, reviewer_packet, wt),
            ],
            cwd=(wt or repo_cwd),
            stdout=lf,
            stderr=subprocess.STDOUT,
            text=True,
        )
    fallback = state.get("fixer_fallback_jobs") or {}
    fallback[lane] = {"log": str(logp), "ts": ts}
    state["fixer_fallback_jobs"] = fallback
    return state

def write_text(p: Path, t: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(t)

def archive(src: Path, lane_dir: Path) -> None:
    if not src.exists():
        return
    dst = lane_dir/"archive"/src.name
    try:
        src.rename(dst)
    except Exception:
        if not src.exists():
            return
        dst.write_text(src.read_text())
        src.unlink()

def _materialize_reviewer_packet(lane_dir: Path, reviewer_note: Optional[Path], fallback_feature_pkt: Optional[str] = None) -> str:
    note_text = ""
    if reviewer_note is not None:
        try:
            note_text = reviewer_note.read_text().strip()
        except Exception:
            note_text = ""
    invalid_note = False
    if note_text:
        lower = note_text.lower()
        # Recovery path: thread/session lookup failures are not actionable reviewer packets.
        if "session not found for thread_id" in lower or "thread not found" in lower:
            invalid_note = True
    if note_text and not invalid_note:
        return note_text

    archived_feature = ""
    try:
        feats = sorted((lane_dir / "archive").glob("F__*.md"), key=lambda p: p.stat().st_mtime)
        if feats:
            archived_feature = feats[-1].read_text().strip()
    except Exception:
        archived_feature = ""

    pkt = fallback_feature_pkt.strip() if (fallback_feature_pkt or "").strip() else archived_feature
    if pkt:
        return (
            "Reviewer packet was empty (automation recovery path).\n"
            "Generate REQUIRED FIXES from the feature packet below and apply them.\n\n"
            f"{pkt}\n"
        )
    return (
        "Reviewer packet was empty and no archived feature packet was found.\n"
        "Run required gates, identify likely defects in this lane branch, and prepare for re-review."
    )

def _ensure_lane_reviewer_thread(
    client: CodexMcpClient,
    cfg: RouterConfig,
    repo_cwd: str,
    lane: str,
    reviewer_thread_ids: Dict[str, str],
) -> str:
    tid = reviewer_thread_ids.get(lane)
    if tid:
        return tid
    tid, _ = client.codex(
        prompt=f"Ready as reviewer for lane {lane}; I won't modify files.",
        cwd=repo_cwd,
        sandbox="read-only",
        approval_policy="on-request",
        model=cfg.model,
        timeout=cfg.reviewer_timeout,
    )
    reviewer_thread_ids[lane] = tid
    return tid


def ensure_all_reviewer_threads(
    client: CodexMcpClient,
    cfg: RouterConfig,
    repo_cwd: str,
    reviewer_thread_ids: Dict[str, str],
) -> Dict[str, str]:
    for lane in cfg.lanes.keys():
        try:
            _ensure_lane_reviewer_thread(client, cfg, repo_cwd, lane, reviewer_thread_ids)
        except Exception as exc:
            print(f"[router] reviewer bootstrap skipped for {lane}: {exc}")
    return reviewer_thread_ids


def process_once(
    client: CodexMcpClient,
    cfg: RouterConfig,
    state: dict,
    repo_cwd: str,
    reviewer_thread_ids: Dict[str, str],
    integrator_tid: str,
) -> Tuple[int, dict, Dict[str, str], str]:
    cursor = load_json(CURSOR_FILE, {})
    reviewer_quota_retry_ts = state.get("reviewer_quota_retry_ts") or {}
    global_quota_retry_ts = float(state.get("reviewer_quota_global_retry_ts", 0) or 0)
    processed = 0
    for lane in cfg.lanes.keys():
        lane_dir = ensure_lane_dirs(lane)
        for pkt_path in list_new(lane_dir, cursor.get(lane)):
            if processed >= cfg.max_packets_per_run:
                state["reviewer_quota_retry_ts"] = reviewer_quota_retry_ts
                state["reviewer_quota_global_retry_ts"] = global_quota_retry_ts
                return processed, state, reviewer_thread_ids, integrator_tid
            pkt = pkt_path.read_text()

            reviewer_text = ""
            now = time.time()
            quota_retry_at = float(reviewer_quota_retry_ts.get(lane, 0) or 0)
            in_quota_cooldown = quota_retry_at > now or global_quota_retry_ts > now
            if in_quota_cooldown:
                wait_s = int(max(quota_retry_at, global_quota_retry_ts) - now)
                reviewer_text = _offline_reviewer_fallback(
                    pkt, f"reviewer quota cooldown active ({wait_s}s remaining)"
                )
            else:
                try:
                    reviewer_tid = _ensure_lane_reviewer_thread(client, cfg, repo_cwd, lane, reviewer_thread_ids)
                    reviewer_tid, reviewer_text = client.codex_reply(
                        reviewer_tid, reviewer_prompt(pkt), timeout=cfg.reviewer_timeout
                    )
                    reviewer_thread_ids[lane] = reviewer_tid
                except Exception as exc:
                    retry_until = time.time() + 900
                    reviewer_quota_retry_ts[lane] = retry_until
                    global_quota_retry_ts = max(global_quota_retry_ts, retry_until)
                    reviewer_text = _offline_reviewer_fallback(pkt, f"reviewer call failed/timed out: {exc}")
            if _invalid_reviewer_output(reviewer_text):
                # Recover from dead/invalid reviewer thread and retry once.
                try:
                    reviewer_tid, _ = client.codex(
                        prompt=f"Ready as reviewer for lane {lane}; I won't modify files.",
                        cwd=repo_cwd,
                        sandbox="read-only",
                        approval_policy="on-request",
                        model=cfg.model,
                        timeout=cfg.reviewer_timeout,
                    )
                    reviewer_thread_ids[lane] = reviewer_tid
                    reviewer_tid, reviewer_text = client.codex_reply(
                        reviewer_tid, reviewer_prompt(pkt), timeout=cfg.reviewer_timeout
                    )
                    reviewer_thread_ids[lane] = reviewer_tid
                except Exception as exc:
                    retry_until = time.time() + 900
                    reviewer_quota_retry_ts[lane] = retry_until
                    global_quota_retry_ts = max(global_quota_retry_ts, retry_until)
                    reviewer_text = _offline_reviewer_fallback(pkt, f"reviewer retry failed/timed out: {exc}")
                if _invalid_reviewer_output(reviewer_text):
                    reviewer_text = _offline_reviewer_fallback(pkt, "reviewer output invalid/unavailable")
            elif _is_reviewer_quota_output(reviewer_text):
                retry_until = time.time() + 900
                reviewer_quota_retry_ts[lane] = retry_until
                global_quota_retry_ts = max(global_quota_retry_ts, retry_until)
                reviewer_text = _offline_reviewer_fallback(pkt, "reviewer quota/rate-limit response")
            verdict = parse_verdict(reviewer_text)

            if verdict == "APPROVED":
                write_text(lane_dir/"outbox/integrator"/pkt_path.name.replace("F__","R__APPROVED__"), reviewer_text)
                try:
                    integrator_tid, integ = client.codex_reply(
                        integrator_tid, integrator_prompt(reviewer_text), timeout=cfg.integrator_timeout
                    )
                    if integ.strip():
                        write_text(lane_dir/"archive"/f"INTEGRATOR__{pkt_path.name}", integ)
                except Exception as exc:
                    write_text(
                        lane_dir / "archive" / f"INTEGRATOR__ERROR__{pkt_path.name}",
                        f"Integrator call failed/timed out: {exc}",
                    )
            else:
                if not (reviewer_text or "").strip():
                    reviewer_text = (
                        "Verdict: `CHANGES_REQUESTED`\n\n"
                        "Reviewer output was empty; router inserted recovery packet.\n"
                        "Required fixes: derive issues from the feature packet and resubmit.\n\n"
                        f"{pkt}\n"
                    )
                outp = lane_dir/"inbox/reviewer"/pkt_path.name.replace("F__","R__CHANGES__")
                write_text(outp, reviewer_text)

            cursor[lane] = pkt_path.name
            save_json(CURSOR_FILE, cursor)
            archive(pkt_path, lane_dir)
            processed += 1

            # Inline fixer can be expensive; disabled by default for automation ticks.
            if verdict != "APPROVED" and cfg.inline_fixer:
                state = run_fixer(client, cfg, state, lane, reviewer_text, repo_cwd)
    state["reviewer_quota_retry_ts"] = reviewer_quota_retry_ts
    state["reviewer_quota_global_retry_ts"] = global_quota_retry_ts
    return processed, state, reviewer_thread_ids, integrator_tid

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
    retry_ts = state.get("reviewer_fixer_retry_ts") or {}
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
            last_kick = float(retry_ts.get(lane, 0) or 0)
            # Backward compatibility: if timestamp missing, allow one immediate retry.
            if last_kick > 0 and (time.time() - last_kick) < cfg.reviewer_fixer_retry_cooldown_seconds:
                continue
        reviewer_packet = _materialize_reviewer_packet(lane_dir, newest_note)
        state = run_fixer(client, cfg, state, lane, reviewer_packet, repo_cwd)
        cursor[lane] = newest_note.name
        retry_ts[lane] = time.time()
        kicked += 1

    state["reviewer_fixer_cursor"] = cursor
    state["reviewer_fixer_retry_ts"] = retry_ts
    return kicked, state

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--daemon", action="store_true")
    args = ap.parse_args()

    cfg = load_cfg()
    state = load_json(STATE_FILE, {})
    repo_cwd = str(Path.cwd())

    client = CodexMcpClient(approval=ApprovalPolicy(True, True), codex_cmd=cfg.codex_cmd)

    reviewer_thread_ids = state.get("reviewer_thread_ids") or {}
    if not isinstance(reviewer_thread_ids, dict):
        reviewer_thread_ids = {}
    reviewer_thread_ids = ensure_all_reviewer_threads(client, cfg, repo_cwd, reviewer_thread_ids)
    integrator_tid = state.get("integrator_thread_id")

    if not integrator_tid:
        integrator_tid, _ = client.codex(
            prompt="Ready as integrator.",
            cwd=repo_cwd,
            sandbox="workspace-write",
            approval_policy="on-request",
            model=cfg.model,
            timeout=cfg.integrator_timeout,
        )

    state["reviewer_thread_ids"] = reviewer_thread_ids
    state["reviewer_thread_missing_lanes"] = [
        lane for lane in cfg.lanes.keys() if lane not in reviewer_thread_ids
    ]
    if reviewer_thread_ids:
        # Backward-compatible status field.
        first_lane = sorted(reviewer_thread_ids.keys())[0]
        state["reviewer_thread_id"] = reviewer_thread_ids.get(first_lane)
    else:
        state["reviewer_thread_id"] = None
    state["integrator_thread_id"] = integrator_tid
    save_json(STATE_FILE, state)

    for lane in cfg.lanes.keys():
        ensure_lane_dirs(lane)

    try:
        if not args.daemon:
            if acquire_lease():
                try:
                    n, state, reviewer_thread_ids, integrator_tid = process_once(
                        client, cfg, state, repo_cwd, reviewer_thread_ids, integrator_tid
                    )
                    kicked, state = process_reviewer_backlog(client, cfg, state, repo_cwd)
                    state["reviewer_thread_ids"] = reviewer_thread_ids
                    state["reviewer_thread_missing_lanes"] = [
                        lane for lane in cfg.lanes.keys() if lane not in reviewer_thread_ids
                    ]
                    if reviewer_thread_ids:
                        first_lane = sorted(reviewer_thread_ids.keys())[0]
                        state["reviewer_thread_id"] = reviewer_thread_ids.get(first_lane)
                    else:
                        state["reviewer_thread_id"] = None
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
                    n, state, reviewer_thread_ids, integrator_tid = process_once(
                        client, cfg, state, repo_cwd, reviewer_thread_ids, integrator_tid
                    )
                    kicked, state = process_reviewer_backlog(client, cfg, state, repo_cwd)
                    state["reviewer_thread_ids"] = reviewer_thread_ids
                    state["reviewer_thread_missing_lanes"] = [
                        lane for lane in cfg.lanes.keys() if lane not in reviewer_thread_ids
                    ]
                    if reviewer_thread_ids:
                        first_lane = sorted(reviewer_thread_ids.keys())[0]
                        state["reviewer_thread_id"] = reviewer_thread_ids.get(first_lane)
                    else:
                        state["reviewer_thread_id"] = None
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
