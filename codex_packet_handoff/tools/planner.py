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
    "feat-retrieval-fts": ["src/qual/retrieval/**", "src/qual/engine/retrieval/**"],
    "feat-a2ui-contract": ["src/qual/ui/**"],
    "feat-engine-runs": ["src/qual/engine/**"],
    "feat-console": ["src/qual/console/**"],
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


def is_git_repo(cwd: str) -> bool:
    rc, _ = run("git rev-parse --is-inside-work-tree", cwd=cwd, timeout=120)
    return rc == 0

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

def resolve_reviewed_head_sha(meta: Json, fallback_sha: str) -> str:
    final_head_sha = str(meta.get("final_head_sha", "")).strip()
    if final_head_sha:
        return final_head_sha
    reviewed_range = str(meta.get("reviewed_implementation_range", "")).strip()
    if reviewed_range:
        reviewed_head_sha = reviewed_range.rsplit("..", 1)[-1].strip()
        if reviewed_head_sha:
            return reviewed_head_sha
    return fallback_sha

def compute_changed_files(cwd: str, base_ref: str, head_ref: str) -> List[str]:
    out = git(f"diff --name-only {base_ref}...{head_ref}", cwd=cwd)
    return [ln.strip() for ln in out.splitlines() if ln.strip()]

def build_packet(lane: str, branch: str, sha: str, meta: Json, files: List[str], gate_results: List[Tuple[str,int]]) -> str:
    def rcstr(rc:int)->str: return "PASS" if rc==0 else f"FAIL ({rc})"
    reviewed_range = str(meta.get("reviewed_implementation_range", "")).strip()
    scope_completed = str(meta.get("scope_completed", "")).strip()
    is_cumulative = bool(reviewed_range or scope_completed)
    lines=[]
    lines += ["# Feature → Review Packet",""]
    lines += [f"- Lane: `{lane}`", f"- Branch: `{branch}`", f"- Commit: `{sha}`",""]
    if reviewed_range:
        lines += [f"- Reviewed implementation range: `{reviewed_range}`"]
    lines += ["## Scope goal", f"- {str(meta.get('scope_goal','')).strip() or '(missing)'}", ""]
    if scope_completed:
        lines += ["## Scope completed", f"- {scope_completed}", ""]
    lines += ["## Lane/owned paths"] + [f"- `{p}`" for p in LANE_OWNED_PATHS.get(lane,[])] + [""]
    if str(meta.get("kickoff_budget_note","")).strip():
        lines += ["## Kickoff budget/limits compliance", f"- {meta['kickoff_budget_note'].strip()}", ""]
    if str(meta.get("approved_exception_note","")).strip():
        lines += ["## Approved exception note", f"- {meta['approved_exception_note'].strip()}", ""]
    lines += ["## Tasks completed (numbered)"]
    tasks=list(meta.get("tasks_completed") or [])
    lines += [f"{i+1}. {str(t).strip()}" for i,t in enumerate(tasks)] if tasks else ["1. (missing)"]
    lines += ["", "## Files changed (cumulative range)" if is_cumulative else "## Files changed"]
    lines += [f"- `{f}`" for f in files] if files else ["- (none detected)"]
    lines += ["","## Commands run and outcomes"]
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


def _normalize_gate_results(raw: Any) -> List[Tuple[str, int]]:
    out: List[Tuple[str, int]] = []
    if not isinstance(raw, list):
        return out
    for item in raw:
        if not isinstance(item, (list, tuple)) or len(item) != 2:
            continue
        cmd = str(item[0]).strip()
        try:
            rc = int(item[1])
        except Exception:
            continue
        if not cmd:
            continue
        out.append((cmd, rc))
    return out

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
    run("git fetch --all --prune", cwd=repo, timeout=600)

    for lane, lcfg in cfg["lanes"].items():
        if not bool((lcfg or {}).get("enabled", True)):
            continue
        ensure_lane_dirs(lane)
        if lane_has_pending_feature(lane):
            continue
        has_reviewer_notes = lane_has_reviewer_notes(lane)
        branch=str((lcfg or {}).get("branch") or f"codex/{lane}")
        lane_repo = find_worktree_for_branch(repo, branch)
        if lane_repo and is_git_repo(lane_repo):
            active_repo = lane_repo
        else:
            # Do not switch branches in the main repo from planner automation.
            # Lane automation is worktree-scoped; missing/stale worktrees should be fixed
            # out-of-band without mutating main checkout state.
            if lane_repo and not is_git_repo(lane_repo):
                print(f"[planner] {lane}: stale non-git worktree for {branch} at {lane_repo}; skipping")
            else:
                print(f"[planner] {lane}: no usable worktree for {branch}; skipping")
            continue
        try:
            sha=git("rev-parse HEAD", cwd=active_repo)
        except Exception as e:
            print(f"[planner] {lane}: unable to resolve HEAD in {active_repo}: {e}")
            continue
        prev_lane_state = lane_state.get(lane) or {}
        meta=read_lane_meta(lane)
        miss=validate_meta(meta)
        if miss:
            print(f"[planner] {lane}: lane_meta missing: {miss} (using auto defaults)")
            meta = apply_meta_defaults(meta, miss)
        packet_sha = resolve_reviewed_head_sha(meta, sha)
        last_submitted_sha = prev_lane_state.get("last_submitted_sha")
        # Reviewer notes should block new packets until the reviewed head advances.
        # This allows one-at-a-time re-review submissions from the feature lane.
        if has_reviewer_notes and (not last_submitted_sha or last_submitted_sha == packet_sha):
            continue
        if last_submitted_sha == packet_sha:
            continue
        fast_reemit = bool(has_reviewer_notes and last_submitted_sha and last_submitted_sha != packet_sha)
        try:
            files=compute_changed_files(active_repo, base_ref, packet_sha)
        except Exception as e:
            print(f"[planner] {lane}: diff failed vs {base_ref}: {e}")
            continue
        env=os.environ.copy()
        if bool(meta.get("shared_file_exception")):
            env["SCOPE_ALLOW_SHARED"]="1"
        if fast_reemit:
            carried = _normalize_gate_results(prev_lane_state.get("last_gate_results"))
            if carried:
                print(f"[planner] {lane}: fast re-emit from advanced HEAD after reviewer notes (reuse prior gate results)")
                results = carried
            else:
                print(f"[planner] {lane}: fast re-emit has no prior gate results; rerunning local gates")
                fast_reemit = False
        if not fast_reemit:
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
        fn=f"F__{branch.replace('/','-')}__{packet_sha}__{ts}.md"
        outp=PACKETS_ROOT/lane/"inbox/feature"/fn
        outp.write_text(build_packet(lane,branch,packet_sha,meta,files,results))
        print(f"[planner] emitted {outp}")
        lane_state[lane]={
            "last_submitted_sha":packet_sha,
            "last_emitted_packet":fn,
            "last_gate_results":[[cmd, rc] for cmd, rc in results],
        }

    state["lanes"]=lane_state
    save_json(STATE_FILE,state)

if __name__=="__main__":
    main()
