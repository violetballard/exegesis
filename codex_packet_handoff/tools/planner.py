#!/usr/bin/env python3
"""Planner (inference mode + worktree-safe detached checkout)

- No lane_meta.
- For each lane branch:
    - resolve branch -> SHA
    - detached checkout at SHA (avoids git worktree conflicts)
    - run make scope-check + gates
    - emit minimal packet into .codex/packets/...

"""
from __future__ import annotations
import json, os, subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PACKETS_ROOT = Path(".codex/packets/lanes")
PLANNER_ROOT = Path(".codex/packet_planner")
STATE_FILE = PLANNER_ROOT/"state.json"
CONFIG_FILE = Path(".codex/packet_router/config.json")

REQUIRED_GATES_DEFAULT = ["./quality-format.sh --check","./quality-lint.sh","./quality-test.sh","./typecheck-test.sh","make ci"]

LANE_OWNED_PATHS = {
  "feat-commands":["src/qual/commands/**"],
  "feat-context-storage":["src/qual/context/**","src/qual/storage/**"],
  "feat-ux-flow":["src/qual/ui/**","src/qual/drafting/**","src/qual/engine/**"],
  "feat-webconsole-core":["src/qual/webconsole/server/**","src/qual/webconsole/api/**","src/qual/webconsole/auth/**"],
  "feat-webconsole-ui":["src/qual/webconsole/render/**","src/qual/webconsole/templates/**","src/qual/webconsole/static/**"],
}

Json = Dict[str, Any]

def load_json(p: Path, default: Any)->Any:
    try: return json.loads(p.read_text())
    except Exception: return default

def save_json(p: Path, data: Any)->None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))

def run(cmd: str, cwd: str, env: Optional[Dict[str,str]]=None, timeout: int=3600)->Tuple[int,str]:
    p = subprocess.Popen(cmd, cwd=cwd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env or os.environ.copy())
    try:
        out,_ = p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        p.kill()
        out,_ = p.communicate()
        return 124, (out or "") + "\n[TIMEOUT]"
    return p.returncode, out or ""

def git(cmd: str, cwd: str)->str:
    rc,out = run(f"git {cmd}", cwd=cwd, timeout=600)
    if rc!=0: raise RuntimeError(out)
    return out.strip()

def ensure_lane_dirs(lane: str)->None:
    base=PACKETS_ROOT/lane
    (base/"inbox/feature").mkdir(parents=True, exist_ok=True)
    (base/"inbox/reviewer").mkdir(parents=True, exist_ok=True)
    (base/"outbox/integrator").mkdir(parents=True, exist_ok=True)
    (base/"archive").mkdir(parents=True, exist_ok=True)

def lane_is_busy(lane: str)->bool:
    base=PACKETS_ROOT/lane
    if any((base/"inbox/feature").glob("*.md")): return True
    reviewer=sorted((base/"inbox/reviewer").glob("*.md"), key=lambda p:p.stat().st_mtime, reverse=True)
    if not reviewer: return False
    archived=sorted((base/"archive").glob("F__*.md"), key=lambda p:p.stat().st_mtime, reverse=True)
    if not archived: return True
    return reviewer[0].stat().st_mtime > archived[0].stat().st_mtime

def compute_changed_files(cwd: str, base_ref: str)->List[str]:
    out = git(f"diff --name-only {base_ref}...HEAD", cwd=cwd)
    return [ln.strip() for ln in out.splitlines() if ln.strip()]

def build_packet(lane: str, branch: str, sha: str, files: List[str], gate_results: List[Tuple[str,int]])->str:
    def rcstr(rc:int)->str: return "PASS" if rc==0 else f"FAIL ({rc})"
    lines=[]
    lines += ["# Feature → Review Packet (minimal; reviewer infers plan mapping)",""]
    lines += [f"- Lane: `{lane}`", f"- Branch: `{branch}`", f"- Commit: `{sha}`",""]
    lines += ["## Lane/owned paths"] + [f"- `{p}`" for p in LANE_OWNED_PATHS.get(lane,[])] + [""]
    lines += ["## Files changed"] + ([f"- `{f}`" for f in files] if files else ["- (none detected)"]) + [""]
    lines += ["## Commands run with results"]
    for cmd,rc in gate_results:
        lines.append(f"- `{cmd}`: {rcstr(rc)}")
    lines += ["",
              "## Plan alignment (reviewer must infer & enforce)",
              "- Roadmap item(s) affected: (infer from ROADMAP.md)",
              "- Vision capability affected: (infer from PRODUCT_VISION.md)",
              "- Architectural alignment: (validate with ARCHITECTURE.md)",
              "- Routing/provider impact: (infer; default None unless evidence)",
              ""]
    if lane=="feat-webconsole-ui":
        lines += ["## Webconsole UI kickoff compliance (required)",
                  "- Reviewer must include explicit kickoff budget/limits compliance statement or request it.",
                  ""]
    return "\n".join(lines)

def main()->None:
    cfg=load_json(CONFIG_FILE,None)
    if not cfg or "lanes" not in cfg:
        raise SystemExit(f"Missing {CONFIG_FILE} (copy example.json).")
    planner_cfg=cfg.get("planner",{}) or {}
    base_ref=str(planner_cfg.get("base_ref","codex/integrator"))
    gates=list(planner_cfg.get("required_gates", REQUIRED_GATES_DEFAULT))
    state=load_json(STATE_FILE,{})
    lane_state=state.get("lanes",{})
    repo=str(Path.cwd())
    orig=git("rev-parse --abbrev-ref HEAD", cwd=repo)

    run("git fetch --all --prune", cwd=repo, timeout=600)

    for lane,lcfg in cfg["lanes"].items():
        ensure_lane_dirs(lane)
        if lane_is_busy(lane): 
            continue
        branch=str((lcfg or {}).get("branch") or f"codex/{lane}")

        try:
            sha = git(f"rev-parse {branch}", cwd=repo)
        except Exception as e:
            print(f"[planner] {lane}: cannot resolve {branch}: {e}")
            continue

        rc,out = run(f"git switch --detach {sha}", cwd=repo, timeout=300)
        if rc!=0:
            rc,out2 = run(f"git checkout --detach {sha}", cwd=repo, timeout=300)
            if rc!=0:
                print(f"[planner] {lane}: cannot detach at {sha}:\n{out}\n{out2}")
                continue

        if (lane_state.get(lane) or {}).get("last_submitted_sha")==sha:
            continue

        env=os.environ.copy()
        scope_rc,scope_out = run("make scope-check", cwd=repo, env=env, timeout=900)
        if scope_rc!=0:
            print(f"[planner] {lane}: scope-check FAIL:\n{scope_out}")
            continue

        files = compute_changed_files(repo, base_ref)
        results=[("make scope-check",0)]
        ok=True
        for cmd in gates:
            rc,out = run(cmd, cwd=repo, env=env, timeout=3600)
            results.append((cmd,rc))
            if rc!=0:
                ok=False
                print(f"[planner] {lane}: gate FAIL {cmd}\n{out}")
                break
        if not ok:
            continue

        ts=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        fn=f"F__{branch.replace('/','-')}__{sha}__{ts}.md"
        outp=PACKETS_ROOT/lane/"inbox/feature"/fn
        outp.write_text(build_packet(lane,branch,sha,files,results))
        print(f"[planner] emitted {outp}")
        lane_state[lane]={"last_submitted_sha":sha,"last_emitted_packet":fn}

    run(f"git switch {orig}", cwd=repo, timeout=300)
    state["lanes"]=lane_state
    save_json(STATE_FILE,state)

if __name__=="__main__":
    main()
