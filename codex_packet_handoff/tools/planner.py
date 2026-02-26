#!/usr/bin/env python3
from __future__ import annotations

import json, os, subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PACKETS_ROOT = Path(".codex/packets/lanes")
PLANNER_ROOT = Path(".codex/packet_planner")
STATE_FILE = PLANNER_ROOT / "state.json"
CONFIG_FILE = Path(".codex/packet_router/config.json")

REQUIRED_GATES_DEFAULT = [
    "./quality-format.sh --check",
    "./quality-lint.sh",
    "./quality-test.sh",
    "./typecheck-test.sh",
    "make ci",
]

LANE_OWNED_PATHS = {
    "feat-commands": ["src/qual/commands/**"],
    "feat-context-storage": ["src/qual/context/**", "src/qual/storage/**"],
    "feat-ux-flow": ["src/qual/ui/**", "src/qual/drafting/**", "src/qual/engine/**"],
    "feat-webconsole-core": ["src/qual/webconsole/server/**", "src/qual/webconsole/api/**", "src/qual/webconsole/auth/**"],
    "feat-webconsole-ui": ["src/qual/webconsole/render/**", "src/qual/webconsole/templates/**", "src/qual/webconsole/static/**"],
}

Json = Dict[str, Any]

def load_json(p: Path, default: Any) -> Any:
    try: return json.loads(p.read_text())
    except Exception: return default

def save_json(p: Path, data: Any) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))

def run(cmd: str, cwd: str, env: Optional[Dict[str,str]] = None, timeout: int = 3600) -> Tuple[int,str]:
    p = subprocess.Popen(cmd, cwd=cwd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env or os.environ.copy())
    try:
        out, _ = p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        p.kill()
        out, _ = p.communicate()
        return 124, (out or "") + "\n[TIMEOUT]"
    return p.returncode, out or ""

def git(cmd: str, cwd: str) -> str:
    rc, out = run(f"git {cmd}", cwd=cwd, timeout=600)
    if rc != 0:
        raise RuntimeError(out)
    return out.strip()

def find_worktree_for_branch(repo_cwd: str, branch: str) -> Optional[str]:
    ref = branch if branch.startswith("refs/") else f"refs/heads/{branch}"
    rc, out = run("git worktree list --porcelain", cwd=repo_cwd, timeout=120)
    if rc != 0:
        return None
    cur_wt: Optional[str] = None
    cur_branch: Optional[str] = None
    for ln in out.splitlines() + [""]:
        if ln.startswith("worktree "):
            cur_wt = ln[len("worktree "):].strip()
        elif ln.startswith("branch "):
            cur_branch = ln[len("branch "):].strip()
        elif not ln.strip():
            if cur_wt and cur_branch == ref:
                return cur_wt
            cur_wt = None
            cur_branch = None
    return None

def ensure_lane_dirs(lane: str) -> None:
    base = PACKETS_ROOT / lane
    (base/"inbox/feature").mkdir(parents=True, exist_ok=True)
    (base/"inbox/reviewer").mkdir(parents=True, exist_ok=True)
    (base/"outbox/integrator").mkdir(parents=True, exist_ok=True)
    (base/"archive").mkdir(parents=True, exist_ok=True)

def lane_has_pending_feature(lane: str) -> bool:
    base = PACKETS_ROOT / lane
    return any((base/"inbox/feature").glob("*.md"))

def lane_has_reviewer_notes(lane: str) -> bool:
    base = PACKETS_ROOT / lane
    return any((base/"inbox/reviewer").glob("*.md"))

def read_lane_meta(lane: str) -> Json:
    p = Path(".codex/lane_meta")/f"{lane}.json"
    if not p.exists():
        return {}
    return load_json(p, {})

def validate_meta(meta: Json) -> List[str]:
    missing=[]
    for k in ("tasks_completed","risk","roadmap_items","vision_capabilities","routing_provider_impact"):
        if k not in meta: missing.append(k); continue
        v=meta[k]
        if isinstance(v,list) and len(v)==0: missing.append(k)
        if isinstance(v,str) and not v.strip(): missing.append(k)
    return missing

def apply_meta_defaults(meta: Json, missing: List[str]) -> Json:
    out = dict(meta or {})
    if "tasks_completed" in missing:
        out["tasks_completed"] = ["(auto) reviewer handback update; see lane commits for concrete changes"]
    if "roadmap_items" in missing:
        out["roadmap_items"] = ["(auto) roadmap mapping pending reviewer/integrator confirmation"]
    if "vision_capabilities" in missing:
        out["vision_capabilities"] = ["(auto) capability mapping pending reviewer/integrator confirmation"]
    if "risk" in missing:
        out["risk"] = "MEDIUM"
    if "routing_provider_impact" in missing:
        out["routing_provider_impact"] = "None"
    return out

def compute_changed_files(cwd: str, base_ref: str) -> List[str]:
    out = git(f"diff --name-only {base_ref}...HEAD", cwd=cwd)
    return [ln.strip() for ln in out.splitlines() if ln.strip()]

def build_packet(lane: str, branch: str, sha: str, meta: Json, files: List[str], gate_results: List[Tuple[str,int]]) -> str:
    def rcstr(rc:int)->str: return "PASS" if rc==0 else f"FAIL ({rc})"
    lines=[]
    lines += ["# Feature → Review Packet",""]
    lines += [f"- Lane: `{lane}`", f"- Branch: `{branch}`", f"- Commit: `{sha}`",""]
    lines += ["## Scope goal", f"- {str(meta.get('scope_goal','')).strip() or '(missing)'}", ""]
    lines += ["## Lane/owned paths"] + [f"- `{p}`" for p in LANE_OWNED_PATHS.get(lane,[])] + [""]
    if str(meta.get("kickoff_budget_note","")).strip():
        lines += ["## Kickoff budget/limits compliance", f"- {meta['kickoff_budget_note'].strip()}", ""]
    if str(meta.get("approved_exception_note","")).strip():
        lines += ["## Approved exception note", f"- {meta['approved_exception_note'].strip()}", ""]
    lines += ["## Tasks completed (numbered)"]
    tasks=list(meta.get("tasks_completed") or [])
    lines += [f"{i+1}. {str(t).strip()}" for i,t in enumerate(tasks)] if tasks else ["1. (missing)"]
    lines += ["","## Files changed"]
    lines += [f"- `{f}`" for f in files] if files else ["- (none detected)"]
    lines += ["","## Commands run with results"]
    for cmd,rc in gate_results:
        lines.append(f"- `{cmd}`: {rcstr(rc)}")
    lines += ["","## Risks / blockers", f"- Risk: `{str(meta.get('risk','LOW')).strip()}`","- Blockers: none",""]
    lines += ["## Required handoff fields","### Roadmap item(s) affected"] + [f"- {x}" for x in (meta.get("roadmap_items") or [])]
    lines += ["### Vision capability affected"] + [f"- {x}" for x in (meta.get("vision_capabilities") or [])]
    lines += ["### Routing/provider impact note", f"- {str(meta.get('routing_provider_impact','None')).strip()}", ""]
    prp=str(meta.get("proposed_readme_patch","")).strip()
    if prp:
        lines += ["### Proposed README patch text","```diff",prp,"```",""]
    lines += ["## Scope-check / ownership note", f"- Shared/integrator-locked edits: `{'YES' if bool(meta.get('shared_file_exception')) else 'NO'}`",""]
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
        if lane_has_pending_feature(lane):
            continue
        branch=str((lcfg or {}).get("branch") or f"codex/{lane}")
        lane_repo = find_worktree_for_branch(repo, branch)
        if lane_repo:
            active_repo = lane_repo
        else:
            active_repo = repo
            rc,out=run(f"git switch {branch}", cwd=repo, timeout=300)
            if rc!=0:
                rc,out2=run(f"git checkout {branch}", cwd=repo, timeout=300)
                if rc!=0:
                    print(f"[planner] {lane}: cannot switch to {branch}:\n{out}\n{out2}")
                    continue
        sha=git("rev-parse HEAD", cwd=active_repo)
        last_submitted_sha = (lane_state.get(lane) or {}).get("last_submitted_sha")
        # Reviewer notes should block new packets until lane HEAD advances.
        # This allows one-at-a-time re-review submissions from the feature lane.
        if lane_has_reviewer_notes(lane) and (not last_submitted_sha or last_submitted_sha == sha):
            continue
        if last_submitted_sha == sha:
            continue
        meta=read_lane_meta(lane)
        miss=validate_meta(meta)
        if miss:
            print(f"[planner] {lane}: lane_meta missing: {miss} (using auto defaults)")
            meta = apply_meta_defaults(meta, miss)
        try:
            files=compute_changed_files(active_repo, base_ref)
        except Exception as e:
            print(f"[planner] {lane}: diff failed vs {base_ref}: {e}")
            continue
        env=os.environ.copy()
        if bool(meta.get("shared_file_exception")):
            env["SCOPE_ALLOW_SHARED"]="1"
        scope_rc,scope_out=run("make scope-check", cwd=active_repo, env=env, timeout=900)
        if scope_rc!=0:
            print(f"[planner] {lane}: scope-check FAIL:\n{scope_out}")
            continue
        results=[("make scope-check",0)]
        ok=True
        for cmd in gates:
            rc,out=run(cmd, cwd=active_repo, env=env, timeout=3600)
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
        outp.write_text(build_packet(lane,branch,sha,meta,files,results))
        print(f"[planner] emitted {outp}")
        lane_state[lane]={"last_submitted_sha":sha,"last_emitted_packet":fn}

    run(f"git switch {orig}", cwd=repo, timeout=300)
    state["lanes"]=lane_state
    save_json(STATE_FILE,state)

if __name__=="__main__":
    main()
