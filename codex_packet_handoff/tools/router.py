#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, re, time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional
from codex_mcp_client import ApprovalPolicy, CodexMcpClient
from event_accumulator import EventAccumulator

PACKETS_ROOT=Path(".codex/packets/lanes")
ROUTER_ROOT=Path(".codex/packet_router")
STATE_FILE=ROUTER_ROOT/"state.json"
CONFIG_FILE=ROUTER_ROOT/"config.json"
LEASE_FILE=ROUTER_ROOT/"lease.json"
CURSOR_FILE=ROUTER_ROOT/"cursor.json"
VERDICT_RE=re.compile(r"Verdict:\s*`(APPROVED|CHANGES_REQUESTED|CHANGES REQUESTED)`", re.IGNORECASE)

@dataclass
class RouterConfig:
    model: str
    codex_cmd: str
    idle_seconds: float
    reviewer_timeout: float
    integrator_timeout: float
    lanes: Dict[str, Dict[str, Any]]

def load_json(p:Path, default:Any)->Any:
    try: return json.loads(p.read_text())
    except Exception: return default
def save_json(p:Path, data:Any)->None:
    p.parent.mkdir(parents=True, exist_ok=True); p.write_text(json.dumps(data, indent=2))

def acquire_lease(ttl:int=20)->bool:
    now=time.time()
    if LEASE_FILE.exists():
        d=load_json(LEASE_FILE,{})
        if now-float(d.get("ts",0))<ttl: return False
    save_json(LEASE_FILE,{"ts":now,"pid":os.getpid()}); return True
def release_lease():
    if LEASE_FILE.exists():
        try: LEASE_FILE.unlink()
        except Exception: pass

def load_cfg()->RouterConfig:
    cfg=load_json(CONFIG_FILE,None)
    if not cfg: raise SystemExit(f"Missing {CONFIG_FILE} (copy example.json).")
    return RouterConfig(
        model=str(cfg.get("model","gpt-5.1-codex")),
        codex_cmd=str(cfg.get("codex_cmd","codex")),
        idle_seconds=float(cfg.get("idle_seconds",1.2)),
        reviewer_timeout=float(cfg.get("reviewer_timeout",180)),
        integrator_timeout=float(cfg.get("integrator_timeout",900)),
        lanes=dict(cfg.get("lanes",{})),
    )

def ensure_lane_dirs(lane:str)->Path:
    d=PACKETS_ROOT/lane
    (d/"inbox/feature").mkdir(parents=True, exist_ok=True)
    (d/"inbox/reviewer").mkdir(parents=True, exist_ok=True)
    (d/"outbox/integrator").mkdir(parents=True, exist_ok=True)
    (d/"archive").mkdir(parents=True, exist_ok=True)
    return d

def list_new(lane_dir:Path, last_seen:Optional[str])->List[Path]:
    files=sorted((lane_dir/"inbox/feature").glob("*.md"), key=lambda p:p.stat().st_mtime)
    if not last_seen: return files[-1:] if files else []
    out=[]; seen=False
    for f in files:
        if seen: out.append(f)
        if f.name==last_seen: seen=True
    return out

def parse_verdict(text:str)->str:
    m=VERDICT_RE.search(text or "")
    if not m: return "CHANGES_REQUESTED"
    v=m.group(1).upper().replace(" ","_")
    return "APPROVED" if v=="APPROVED" else "CHANGES_REQUESTED"

def reviewer_prompt(pkt:str)->str:
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

def integrator_prompt(approved:str)->str:
    return (
        "You are the INTEGRATOR. You may write to the workspace.\n"
        "Consume this APPROVED packet, perform merge order + post-merge checks, report blockers.\n\n"
        f"{approved}\n"
    )

def write_text(p:Path,t:str)->None:
    p.parent.mkdir(parents=True, exist_ok=True); p.write_text(t)

def archive(src:Path, lane_dir:Path)->None:
    dst=lane_dir/"archive"/src.name
    try: src.rename(dst)
    except Exception:
        dst.write_text(src.read_text()); src.unlink()

def process_once(client:CodexMcpClient, acc:EventAccumulator, cfg:RouterConfig, reviewer_id:str, integrator_id:str)->int:
    cursor=load_json(CURSOR_FILE,{})
    processed=0
    for lane in cfg.lanes.keys():
        lane_dir=ensure_lane_dirs(lane)
        for pkt_path in list_new(lane_dir, cursor.get(lane)):
            pkt=pkt_path.read_text()
            acc.clear(reviewer_id)
            reviewer_id = client.codex_reply(reviewer_id, reviewer_prompt(pkt))
            reviewer_text=acc.wait_for_idle_text(reviewer_id, cfg.idle_seconds, cfg.reviewer_timeout)
            verdict=parse_verdict(reviewer_text)
            if verdict=="APPROVED":
                write_text(lane_dir/"outbox/integrator"/pkt_path.name.replace("F__","R__APPROVED__"), reviewer_text)
                acc.clear(integrator_id)
                integrator_id = client.codex_reply(integrator_id, integrator_prompt(reviewer_text))
                integ=acc.wait_for_idle_text(integrator_id, cfg.idle_seconds, cfg.integrator_timeout)
                if integ.strip():
                    write_text(lane_dir/"archive"/f"INTEGRATOR__{pkt_path.name}", integ)
            else:
                write_text(lane_dir/"inbox/reviewer"/pkt_path.name.replace("F__","R__CHANGES__"), reviewer_text)
            cursor[lane]=pkt_path.name
            save_json(CURSOR_FILE,cursor)
            archive(pkt_path, lane_dir)
            processed += 1
    return processed

def main()->None:
    ap=argparse.ArgumentParser(); ap.add_argument("--daemon", action="store_true"); args=ap.parse_args()
    cfg=load_cfg()
    state=load_json(STATE_FILE,{})
    acc=EventAccumulator()
    client=CodexMcpClient(approval=ApprovalPolicy(True,True), on_notification=acc.on_notification, codex_cmd=cfg.codex_cmd)
    cwd=str(Path.cwd())
    try:
        reviewer_id=state.get("reviewer_conversation_id")
        integrator_id=state.get("integrator_conversation_id")
        if not reviewer_id:
            reviewer_id=client.codex(prompt="You are the REVIEWER. You are sandboxed read-only and MUST NOT modify files.", cwd=cwd, sandbox="read-only", approval_policy="on-request", model=cfg.model)
            print(f"[router] reviewer conversationId={reviewer_id}")
        if not integrator_id:
            integrator_id=client.codex(prompt="You are the INTEGRATOR. You may write to the workspace.", cwd=cwd, sandbox="workspace-write", approval_policy="on-request", model=cfg.model)
            print(f"[router] integrator conversationId={integrator_id}")
        state["reviewer_conversation_id"]=reviewer_id; state["integrator_conversation_id"]=integrator_id
        save_json(STATE_FILE,state)
        for lane in cfg.lanes.keys(): ensure_lane_dirs(lane)
        if not args.daemon:
            if acquire_lease():
                try:
                    n=process_once(client,acc,cfg,str(reviewer_id),str(integrator_id))
                    print(f"[router] processed {n} packet(s)")
                finally:
                    release_lease()
            return
        print("[router] daemon mode")
        while True:
            if acquire_lease():
                try:
                    n=process_once(client,acc,cfg,str(reviewer_id),str(integrator_id))
                    if n: print(f"[router] processed {n} packet(s)")
                finally:
                    release_lease()
            time.sleep(0.5)
    finally:
        client.close()

if __name__=="__main__":
    main()
