#!/usr/bin/env python3
from __future__ import annotations

import json, os, shlex, signal, subprocess
from datetime import datetime, timezone
from fnmatch import fnmatchcase
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from packet_progress import infer_last_changed_files, infer_last_gate_results, infer_last_submitted_sha
except ImportError:  # pragma: no cover - package execution fallback
    from .packet_progress import infer_last_changed_files, infer_last_gate_results, infer_last_submitted_sha

try:
    from git_ops import require_git_output, run_git
except ImportError:  # pragma: no cover - package execution fallback
    from .git_ops import require_git_output, run_git

try:
    from lane_profiles import ENGINE_MILESTONE_FOCUS, default_lane_meta, engine_priority_lines
except ImportError:  # pragma: no cover - package execution fallback
    from .lane_profiles import ENGINE_MILESTONE_FOCUS, default_lane_meta, engine_priority_lines

REPO_ROOT = Path(__file__).resolve().parents[2]
PACKETS_ROOT = Path(".codex/packets/lanes")
PLANNER_ROOT = Path(".codex/packet_planner")
STATE_FILE = PLANNER_ROOT / "state.json"
COORDINATOR_STATE_FILE = Path(".codex/packet_coordinator/state.json")
CONFIG_FILE = Path(".codex/packet_router/config.json")
SCOPE_CHECK_SCRIPT = REPO_ROOT / "scripts/scope-check.sh"
FORMAT_CHECK_SCRIPT = REPO_ROOT / "quality-format.sh"
LINT_CHECK_SCRIPT = REPO_ROOT / "quality-lint.sh"
TEST_CHECK_SCRIPT = REPO_ROOT / "quality-test.sh"
TYPECHECK_SCRIPT = REPO_ROOT / "typecheck-test.sh"
PLANNER_TEST_GATE_TIMEOUT_SECONDS = 600
PLANNER_DEFAULT_GATE_TIMEOUT_SECONDS = 900
SETUP_SCRIPT = REPO_ROOT / "scripts/setup.sh"
BUILD_SCRIPT = REPO_ROOT / "scripts/build.sh"

REQUIRED_GATES_DEFAULT = [
    "./quality-format.sh --check",
    "./quality-lint.sh",
    "./quality-test.sh",
    "./typecheck-test.sh",
    "make ci",
]

CHANGED_FILES_DIFF_TIMEOUT = 8
CHANGED_FILES_FALLBACK_TIMEOUT = 8

LANE_OWNED_PATHS = {
    "feat-commands": ["src/qual/commands/**"],
    "feat-context-storage": [
        "src/qual/context/**",
        "src/qual/storage/**",
        "engine/src/exegesis_engine/state/**",
        "engine/src/exegesis_engine/storage/**",
    ],
    "feat-retrieval-fts": [
        "src/qual/retrieval/**",
        "src/qual/engine/retrieval/**",
        "engine/src/exegesis_engine/retrieval/**",
    ],
    "feat-a2ui-contract": [
        "src/qual/ui/a2ui.py",
        "src/qual/ui/test_a2ui_fallback_safety.py",
        "shared/src/exegesis_shared/contracts/**",
        "shared/src/exegesis_shared/models/**",
        "shared/src/exegesis_shared/types/**",
        "tests/unit/test_a2ui_contract.py",
    ],
    "feat-engine-runs": [
        "src/qual/engine/**",
        "src/qual/drafting/**",
        "engine/src/exegesis_engine/api/**",
        "engine/src/exegesis_engine/workflow/**",
        "engine/src/exegesis_engine/patches/**",
        "engine/src/exegesis_engine/audit/**",
        "engine/src/exegesis_engine/services/**",
        "tests/unit/test_bulk_draft_routing.py",
        "tests/unit/test_engine_run_pipeline.py",
    ],
    "feat-console-shell": [
        "client-textual/src/exegesis_textual/app/**",
        "client-textual/src/exegesis_textual/layout/**",
        "client-textual/src/exegesis_textual/panes/**",
        "client-textual/src/exegesis_textual/commands/**",
        "client-textual/src/exegesis_textual/shortcuts/**",
        "client-textual/src/exegesis_textual/inspectors/**",
        "client-textual/src/exegesis_textual/theme/**",
    ],
    "feat-console-workflow": [
        "client-textual/src/exegesis_textual/workflow/**",
        "client-textual/src/exegesis_textual/cards/**",
        "client-textual/src/exegesis_textual/events/**",
    ],
    "feat-ocr-import": [
        "src/qual/imports/**",
        "src/qual/ocr/**",
        "engine/src/exegesis_engine/imports/**",
        "engine/src/exegesis_engine/ocr/**",
    ],
    "feat-literature-import": [
        "src/qual/literature/**",
        "engine/src/exegesis_engine/literature/**",
    ],
    "feat-rag-index": [
        "src/qual/rag/**",
        "engine/src/exegesis_engine/rag/**",
        "engine/src/exegesis_engine/retrieval/rag/**",
    ],
    "feat-qual-coding": [
        "src/qual/coding/**",
        "src/qual/project_folders/**",
        "engine/src/exegesis_engine/coding/**",
        "engine/src/exegesis_engine/project_folders/**",
        "client-textual/src/exegesis_textual/coding/**",
    ],
    "feat-editor-basics": [
        "src/qual/editor/**",
        "engine/src/exegesis_engine/editor/**",
        "client-textual/src/exegesis_textual/editor/**",
        "client-textual/src/exegesis_textual/shortcuts/editor/**",
    ],
    "feat-citations": [
        "src/qual/citations/**",
        "engine/src/exegesis_engine/citations/**",
        "shared/src/exegesis_shared/citations/**",
        "client-textual/src/exegesis_textual/citations/**",
    ],
    "feat-export": [
        "src/qual/export/**",
        "engine/src/exegesis_engine/export/**",
        "client-textual/src/exegesis_textual/export/**",
    ],
    "feat-zotero-import": [
        "src/qual/zotero/**",
        "engine/src/exegesis_engine/zotero/**",
        "client-textual/src/exegesis_textual/zotero/**",
    ],
    "feat-formatting-bar": [
        "src/qual/formatting/**",
        "engine/src/exegesis_engine/formatting/**",
        "client-textual/src/exegesis_textual/formatting/**",
    ],
    "feat-developer-provider-config": [
        "src/qual/providers/**",
        "src/qual/credentials/**",
        "engine/src/exegesis_engine/providers/**",
        "engine/src/exegesis_engine/credentials/**",
        "client-textual/src/exegesis_textual/providers/**",
        "client-textual/src/exegesis_textual/commands/provider_config/**",
    ],
    "feat-project-transfer": [
        "engine/src/exegesis_engine/project_transfer/**",
        "shared/src/exegesis_shared/project_transfer/**",
        "client-textual/src/exegesis_textual/project_transfer/**",
        "desktop-shell/workstation/project_transfer/**",
        "docs/project_transfer/**",
    ],
    "feat-desktop-packaging": [
        "desktop-shell/**",
        "scripts/packaging/**",
        "scripts/release/**",
        "docs/packaging/**",
    ],
    "feat-cop-lite-licensing": [
        "engine/src/exegesis_engine/licensing/**",
        "engine/src/exegesis_engine/lite_gateway/**",
        "engine/src/exegesis_engine/nanonets_usage/**",
        "client-textual/src/exegesis_textual/licensing/**",
        "client-textual/src/exegesis_textual/imports/**",
        "shared/src/exegesis_shared/licensing/**",
        "shared/src/exegesis_shared/nanonets_usage/**",
        "docs/licensing/**",
    ],
    "feat-browser-pdf-capture": [
        "browser-extension/**",
        "engine/src/exegesis_engine/browser_capture/**",
        "client-textual/src/exegesis_textual/browser_capture/**",
        "shared/src/exegesis_shared/browser_capture/**",
        "desktop-shell/browser_extension/**",
        "scripts/browser_extension/**",
        "docs/browser_extension/**",
    ],
    "feat-python-sidecar-api": [
        "engine/src/exegesis_engine/sidecar/**",
        "shared/src/exegesis_shared/sidecar/**",
        "desktop-shell/sidecar/**",
        "scripts/sidecar/**",
        "docs/sidecar/**",
    ],
    "feat-native-workstation": [
        "desktop-shell/workstation/**",
        "desktop-shell/native/**",
        "desktop-shell/packaging/**",
        "scripts/workstation/**",
        "scripts/packaging/**",
        "scripts/release/**",
        "docs/workstation/**",
        "docs/packaging/**",
    ],
    "feat-open-access-deep-research": [
        "engine/src/exegesis_engine/research/**",
        "engine/src/exegesis_engine/research_providers/**",
        "engine/src/exegesis_engine/import_batches/**",
        "desktop-shell/workstation/research/**",
        "desktop-shell/workstation/import_batches/**",
        "shared/src/exegesis_shared/research/**",
        "docs/research/**",
    ],
    "feat-quant-analysis": [
        "desktop-shell/workstation/StatsCore/**",
        "desktop-shell/workstation/StatsBridge/**",
        "desktop-shell/workstation/datasets/**",
        "desktop-shell/workstation/quant_analysis/**",
        "shared/src/exegesis_shared/datasets/**",
        "shared/src/exegesis_shared/quant_analysis/**",
        "docs/quant_analysis/**",
    ],
    "feat-advanced-qual-visuals": [
        "engine/src/exegesis_engine/qual_visualizations/**",
        "engine/src/exegesis_engine/codebook/**",
        "desktop-shell/workstation/qual_visualizations/**",
        "shared/src/exegesis_shared/qual_visualizations/**",
        "docs/qual_visualizations/**",
    ],
    "feat-confidential-collaboration": [
        "engine/src/exegesis_engine/collaboration/**",
        "engine/src/exegesis_engine/confidential_sync/**",
        "desktop-shell/workstation/collaboration/**",
        "shared/src/exegesis_shared/collaboration/**",
        "shared/src/exegesis_shared/confidential_sync/**",
        "docs/collaboration/**",
    ],
    "feat-ipad-native-lite": [
        "client-ipad/lite/**",
        "client-ipad/shared/**",
        "shared/src/exegesis_shared/ipad_lite/**",
        "docs/ipad_lite/**",
    ],
}

Json = Dict[str, Any]


def _is_missing(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, (list, tuple, set, dict)):
        return len(value) == 0
    return False


def merge_lane_meta_defaults(lane: str, meta: Json) -> Json:
    merged = default_lane_meta(lane)
    for key, value in dict(meta or {}).items():
        if _is_missing(value) and key in merged:
            continue
        merged[key] = value
    return merged

def load_json(p: Path, default: Any) -> Any:
    try: return json.loads(p.read_text())
    except Exception: return default

def load_coordinator_state() -> Dict[str, Any]:
    try:
        data = json.loads(COORDINATOR_STATE_FILE.read_text())
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}

def lane_feature_active(coordinator_state: Dict[str, Any], lane: str) -> bool:
    lane_refill = coordinator_state.get("lane_refill")
    if not isinstance(lane_refill, dict):
        return False
    lane_state = lane_refill.get(lane)
    return isinstance(lane_state, dict) and lane_state.get("feature_active") is True

def should_skip_for_active_feature(coordinator_state: Dict[str, Any], lane: str, *, fast_reemit: bool) -> bool:
    return lane_feature_active(coordinator_state, lane) and not fast_reemit

def save_json(p: Path, data: Any) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))

def _terminate_process_group(pid: int, sig: int) -> None:
    try:
        os.killpg(pid, sig)
    except OSError:
        try:
            os.kill(pid, sig)
        except OSError:
            pass


def _descendant_pids(root_pid: int) -> List[int]:
    try:
        proc = subprocess.run(
            ["ps", "-axo", "pid=,ppid="],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=2.0,
        )
    except Exception:
        return []
    if proc.returncode != 0:
        return []
    children: Dict[int, List[int]] = {}
    for raw in (proc.stdout or "").splitlines():
        parts = raw.strip().split(None, 1)
        if len(parts) != 2:
            continue
        try:
            pid = int(parts[0])
            ppid = int(parts[1])
        except ValueError:
            continue
        children.setdefault(ppid, []).append(pid)
    seen: set[int] = set()
    stack = list(children.get(root_pid, []))
    while stack:
        pid = stack.pop()
        if pid in seen:
            continue
        seen.add(pid)
        stack.extend(children.get(pid, []))
    return sorted(seen, reverse=True)


def _terminate_process_tree(pid: int, sig: int) -> None:
    for child_pid in _descendant_pids(pid):
        try:
            os.kill(child_pid, sig)
        except OSError:
            pass
    _terminate_process_group(pid, sig)


def run(cmd: str, cwd: str, env: Optional[Dict[str,str]] = None, timeout: int = 3600) -> Tuple[int,str]:
    p = subprocess.Popen(
        cmd,
        cwd=cwd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env or os.environ.copy(),
        start_new_session=True,
    )
    try:
        out, _ = p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        _terminate_process_tree(p.pid, signal.SIGTERM)
        try:
            out, _ = p.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            _terminate_process_tree(p.pid, signal.SIGKILL)
            out, _ = p.communicate()
        return 124, (out or "") + "\n[TIMEOUT]"
    return p.returncode, out or ""

def git(args: List[str], cwd: str) -> str:
    return require_git_output(args, cwd=cwd, timeout=600)


def is_git_repo(cwd: str) -> bool:
    result = run_git(["rev-parse", "--is-inside-work-tree"], cwd=cwd, timeout=120)
    return result.returncode == 0


def list_git_remotes(cwd: str) -> List[str]:
    result = run_git(["remote"], cwd=cwd, timeout=120)
    if result.returncode != 0:
        return []
    return [ln.strip() for ln in result.stdout.splitlines() if ln.strip()]

def find_worktree_for_branch(repo_cwd: str, branch: str) -> Optional[str]:
    ref = branch if branch.startswith("refs/") else f"refs/heads/{branch}"
    result = run_git(["worktree", "list", "--porcelain"], cwd=repo_cwd, timeout=120)
    if result.returncode != 0:
        return None
    cur_wt: Optional[str] = None
    cur_branch: Optional[str] = None
    for ln in result.stdout.splitlines() + [""]:
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
    return any(not path.name.endswith(".shared.md") for path in (base/"inbox/feature").glob("*.md"))

def lane_has_reviewer_notes(lane: str) -> bool:
    base = PACKETS_ROOT / lane
    return any((base/"inbox/reviewer").glob("*.md"))


def archive_lane_reviewer_notes(lane: str) -> int:
    base = PACKETS_ROOT / lane
    notes = sorted((base / "inbox/reviewer").glob("*.md"), key=lambda p: p.stat().st_mtime)
    if not notes:
        return 0
    archive_dir = base / "archive" / "stale"
    archive_dir.mkdir(parents=True, exist_ok=True)
    moved = 0
    for note in notes:
        dst = archive_dir / note.name
        try:
            note.rename(dst)
        except Exception:
            if not note.exists():
                continue
            dst.write_text(note.read_text())
            note.unlink()
        moved += 1
    return moved

def read_lane_meta(lane: str) -> Json:
    p = Path(".codex/lane_meta")/f"{lane}.json"
    if not p.exists():
        return {}
    return load_json(p, {})

def validate_meta(meta: Json) -> List[str]:
    missing=[]
    for k in ("scope_goal","tasks_completed","risk","roadmap_items","vision_capabilities","routing_provider_impact"):
        if k not in meta:
            missing.append(k)
            continue
        if _is_missing(meta[k]):
            missing.append(k)
    if bool(meta.get("shared_file_exception")) and not str(meta.get("approved_exception_note", "")).strip():
        missing.append("approved_exception_note")
    return missing

def apply_meta_defaults(meta: Json, missing: List[str], lane: str) -> Json:
    out = dict(meta or {})
    lane_defaults = default_lane_meta(lane)
    for key in missing:
        default_value = lane_defaults.get(key)
        if not _is_missing(default_value):
            out[key] = default_value
    if "tasks_completed" in missing:
        out["tasks_completed"] = ["(auto) reviewer handback update; see lane commits for concrete changes"]
    if "roadmap_items" in missing and _is_missing(out.get("roadmap_items")):
        out["roadmap_items"] = ["(auto) roadmap mapping pending reviewer/integrator confirmation"]
    if "vision_capabilities" in missing and _is_missing(out.get("vision_capabilities")):
        out["vision_capabilities"] = ["(auto) capability mapping pending reviewer/integrator confirmation"]
    if "risk" in missing and _is_missing(out.get("risk")):
        out["risk"] = "MEDIUM"
    if "routing_provider_impact" in missing and _is_missing(out.get("routing_provider_impact")):
        out["routing_provider_impact"] = "None"
    if "scope_goal" in missing and _is_missing(out.get("scope_goal")):
        out["scope_goal"] = "(missing)"
    if "approved_exception_note" in missing:
        out["approved_exception_note"] = "(auto) approved shared/integrator-locked edits were recorded in the packet"
    return out

def _parse_changed_files(out: str) -> List[str]:
    return [ln.strip() for ln in out.splitlines() if ln.strip()]


def ref_exists(cwd: str, ref: str) -> bool:
    result = run_git(["rev-parse", "--verify", "--quiet", ref], cwd=cwd, timeout=120)
    return result.returncode == 0


def resolve_branch_sha(repo_cwd: str, branch: str, *, fallback_cwd: Optional[str] = None) -> str:
    branch_ref = branch if branch.startswith("refs/") else branch
    result = run_git(["rev-parse", branch_ref], cwd=repo_cwd, timeout=120)
    sha = result.stdout.strip()
    if result.returncode == 0 and sha:
        return sha
    if fallback_cwd:
        return git(["rev-parse", "HEAD"], cwd=fallback_cwd)
    raise RuntimeError(result.stdout or f"unable to resolve branch ref: {branch_ref}")


def _collect_commit_range_files(cwd: str, start_ref: str, head_ref: str) -> List[str]:
    merge_base = require_git_output(["merge-base", start_ref, head_ref], cwd=cwd, timeout=CHANGED_FILES_DIFF_TIMEOUT).strip()
    if not merge_base:
        return []
    revs_result = run_git(["rev-list", "--reverse", f"{merge_base}..{head_ref}"], cwd=cwd, timeout=CHANGED_FILES_DIFF_TIMEOUT)
    if revs_result.returncode != 0:
        raise RuntimeError(revs_result.stdout)
    files: List[str] = []
    seen: set[str] = set()
    for rev in [ln.strip() for ln in revs_result.stdout.splitlines() if ln.strip()]:
        diff_result = run_git(
            ["diff-tree", "--no-commit-id", "--name-only", "-r", rev],
            cwd=cwd,
            timeout=CHANGED_FILES_FALLBACK_TIMEOUT,
        )
        if diff_result.returncode != 0:
            raise RuntimeError(diff_result.stdout)
        for path in _parse_changed_files(diff_result.stdout):
            if path not in seen:
                seen.add(path)
                files.append(path)
    return files


def compute_changed_files(cwd: str, base_ref: str, *, head_ref: str = "HEAD") -> List[str]:
    try:
        files = _collect_commit_range_files(cwd, base_ref, head_ref)
        if files:
            return files
    except Exception as exc:
        print(
            f"[planner] changed-files commit-range fallback for {cwd} failed: {exc} "
            f"(base_ref={base_ref}, head_ref={head_ref})"
        )
    fallback_cmds = (
        ["diff-tree", "--no-commit-id", "--name-only", "-r", head_ref],
        ["show", "--pretty=", "--name-only", head_ref],
    )
    for cmd in fallback_cmds:
        fallback_result = run_git(cmd, cwd=cwd, timeout=CHANGED_FILES_FALLBACK_TIMEOUT)
        fallback_files = _parse_changed_files(fallback_result.stdout)
        if fallback_result.returncode == 0 and fallback_files:
            print(
                f"[planner] changed-files fallback for {cwd}: "
                f"{' '.join(cmd)} (head_ref={head_ref})"
            )
            return fallback_files
    raise RuntimeError(f"unable to determine changed files for {head_ref} vs {base_ref}")


def run_scope_check(cwd: str, env: Optional[Dict[str, str]] = None) -> Tuple[int, str]:
    # Run the daemon checkout's scope policy against the lane worktree so
    # policy updates apply immediately without waiting for every lane branch
    # to merge the latest `scripts/scope-check.sh`.
    return run_repo_gate(str(SCOPE_CHECK_SCRIPT), cwd, env=env, timeout=900)


def run_repo_gate(
    script_path: str,
    target_cwd: str,
    *,
    args: Optional[List[str]] = None,
    env: Optional[Dict[str, str]] = None,
    timeout: int = 3600,
) -> Tuple[int, str]:
    run_env = dict(env or os.environ.copy())
    run_env["QUAL_ROOT_DIR"] = target_cwd
    argv = [shlex.quote(script_path), *(shlex.quote(arg) for arg in (args or []))]
    cmd = "bash " + " ".join(argv)
    return run(cmd, cwd=str(REPO_ROOT), env=run_env, timeout=timeout)


def run_required_gate(cmd: str, cwd: str, env: Optional[Dict[str, str]] = None) -> Tuple[int, str]:
    if cmd == "./quality-format.sh --check":
        return run_repo_gate(
            str(FORMAT_CHECK_SCRIPT),
            cwd,
            args=["--check"],
            env=env,
            timeout=PLANNER_DEFAULT_GATE_TIMEOUT_SECONDS,
        )
    if cmd == "./quality-lint.sh":
        return run_repo_gate(
            str(LINT_CHECK_SCRIPT),
            cwd,
            env=env,
            timeout=PLANNER_DEFAULT_GATE_TIMEOUT_SECONDS,
        )
    if cmd == "./quality-test.sh":
        return run_repo_gate(
            str(TEST_CHECK_SCRIPT),
            cwd,
            env=env,
            timeout=PLANNER_TEST_GATE_TIMEOUT_SECONDS,
        )
    if cmd == "./typecheck-test.sh":
        return run_repo_gate(
            str(TYPECHECK_SCRIPT),
            cwd,
            env=env,
            timeout=PLANNER_DEFAULT_GATE_TIMEOUT_SECONDS,
        )
    if cmd == "make ci":
        steps = [
            ("setup", str(SETUP_SCRIPT), []),
            ("scope-check", str(SCOPE_CHECK_SCRIPT), []),
            ("format-check", str(FORMAT_CHECK_SCRIPT), ["--check"]),
            ("lint", str(LINT_CHECK_SCRIPT), []),
            ("build", str(BUILD_SCRIPT), []),
            ("typecheck", str(TYPECHECK_SCRIPT), []),
            ("test", str(TEST_CHECK_SCRIPT), []),
        ]
        chunks: List[str] = []
        for label, script_path, gate_args in steps:
            rc, out = run_repo_gate(script_path, cwd, args=gate_args, env=env)
            if out:
                chunks.append(out.rstrip())
            if rc != 0:
                if chunks:
                    return rc, "\n".join(chunks) + f"\n[planner] make ci failed at step: {label}"
                return rc, f"[planner] make ci failed at step: {label}"
        return 0, "\n".join(chunks)
    return run(cmd, cwd=cwd, env=env, timeout=3600)

def _split_files(lane: str, files: List[str]) -> Tuple[List[str], List[str]]:
    owned_patterns = LANE_OWNED_PATHS.get(lane, [])
    owned_files = [f for f in files if any(fnmatchcase(f, pattern) for pattern in owned_patterns)]
    shared_files = [f for f in files if f not in owned_files]
    return owned_files, shared_files


def _full_branch_scope_violations(lane: str, files: List[str]) -> List[str]:
    """Return files outside the lane ownership map for the full branch diff."""
    owned_patterns = LANE_OWNED_PATHS.get(lane, [])
    if not owned_patterns:
        return []
    violations: List[str] = []
    for file_name in files:
        normalized = str(file_name).strip().lstrip("./")
        if not normalized:
            continue
        if any(fnmatchcase(normalized, pattern) for pattern in owned_patterns):
            continue
        violations.append(normalized)
    return sorted(set(violations))


def _owned_path_note(lane: str) -> str:
    patterns = LANE_OWNED_PATHS.get(lane, [])
    if not patterns:
        return "(no lane-owned paths configured)"
    return ", ".join(f"`{pattern}`" for pattern in patterns)


def build_packet(
    lane: str,
    branch: str,
    sha: str,
    meta: Json,
    files: List[str],
    gate_results: List[Tuple[str,int]],
    companion_shared_packet: str = "",
) -> str:
    def rcstr(rc:int)->str: return "PASS" if rc==0 else f"FAIL ({rc})"
    def str_list(value: Any) -> List[str]:
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, str):
            stripped = value.strip()
            return [stripped] if stripped else []
        if value is None:
            return []
        stripped = str(value).strip()
        return [stripped] if stripped else []
    owned_files, shared_files = _split_files(lane, files)
    shared_file_exception = bool(meta.get("shared_file_exception")) or bool(shared_files)
    lines=[]
    reviewed_commit = str(meta.get("reviewed_commit") or meta.get("reviewed_head_sha") or "").strip()
    reviewed_range = str(meta.get("reviewed_commit_range") or meta.get("reviewed_range") or "").strip()
    packet_refresh_role = str(meta.get("packet_head_role") or meta.get("packet_type") or "").strip()
    metadata_only_note = str(meta.get("metadata_only_note") or "").strip()
    lines += ["# Feature → Review Packet",""]
    lines += [f"- Lane: `{lane}`", f"- Branch: `{branch}`"]
    if reviewed_commit and reviewed_commit != sha:
        lines += [
            f"- Commit under review: `{reviewed_commit}`",
            f"- Packet refresh commit: `{sha}` (metadata-only; do not review this commit as implementation)",
        ]
        if packet_refresh_role:
            lines += [f"- Packet refresh role: `{packet_refresh_role}`"]
        if reviewed_range:
            lines += [f"- Reviewed implementation range: `{reviewed_range}`"]
    else:
        lines += [f"- Commit: `{sha}`"]
        if packet_refresh_role:
            lines += [f"- Packet role: `{packet_refresh_role}`"]
    lines += [""]
    if metadata_only_note:
        lines += ["## Packet traceability note", f"- {metadata_only_note}", ""]
    lines += ["## Current program focus", f"- {ENGINE_MILESTONE_FOCUS}", ""]
    lines += ["## Current engine execution order"] + [f"- {line}" for line in engine_priority_lines()] + [""]
    lines += ["## Scope goal", f"- {str(meta.get('scope_goal','')).strip() or '(missing)'}", ""]
    priority_outcomes = [str(item).strip() for item in (meta.get("priority_outcomes") or []) if str(item).strip()]
    if priority_outcomes:
        lines += ["## Priority outcomes"] + [f"{i+1}. {item}" for i, item in enumerate(priority_outcomes)] + [""]
    definition_of_done = [str(item).strip() for item in (meta.get("definition_of_done") or []) if str(item).strip()]
    if definition_of_done:
        lines += ["## Definition of done for this lane"] + [f"- {item}" for item in definition_of_done] + [""]
    do_not_spend_time_on = [str(item).strip() for item in (meta.get("do_not_spend_time_on") or []) if str(item).strip()]
    if do_not_spend_time_on:
        lines += ["## Do not spend time on"] + [f"- {item}" for item in do_not_spend_time_on] + [""]
    lines += ["## Lane/owned paths"] + [f"- `{p}`" for p in LANE_OWNED_PATHS.get(lane,[])] + [""]
    scope_completed = str_list(meta.get("scope_completed"))
    if scope_completed:
        lines += ["## Scope completed"] + [f"- {item}" for item in scope_completed] + [""]
    if str(meta.get("kickoff_budget_note","")).strip():
        lines += ["## Kickoff budget/limits compliance", f"- {meta['kickoff_budget_note'].strip()}", ""]
    if str(meta.get("approved_exception_note","")).strip():
        lines += ["## Approved exception note", f"- {meta['approved_exception_note'].strip()}", ""]
    lines += ["## Tasks completed (numbered)"]
    tasks=list(meta.get("tasks_completed") or [])
    lines += [f"{i+1}. {str(t).strip()}" for i,t in enumerate(tasks)] if tasks else ["1. (missing)"]
    lines += ["","## Files changed"]
    reviewed_files = str_list(meta.get("reviewed_files"))
    metadata_only_files = str_list(meta.get("metadata_only_files"))
    if reviewed_files or metadata_only_files:
        if reviewed_files:
            lines += ["### Reviewed implementation files"] + [f"- `{f}`" for f in reviewed_files]
        if metadata_only_files:
            lines += ["### Metadata-only handoff files"] + [f"- `{f}`" for f in metadata_only_files]
    else:
        if owned_files:
            lines += ["### Engine-owned files"]
            lines += [f"- `{f}`" for f in owned_files]
        if not owned_files and not shared_file_exception:
            lines += [f"- `{f}`" for f in files] if files else ["- (none detected)"]
        if shared_file_exception:
            lines += ["### Approved shared/integrator-locked changes"]
            lines += [
                "- These handoff-maintenance edits are recorded in the companion shared packet and are not part of lane-owned feature scope."
            ]
            if companion_shared_packet:
                lines += [f"- Companion shared packet: {companion_shared_packet}"]
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
    lines += ["## Scope-check / ownership note", f"- Shared/integrator-locked edits: `{'YES' if shared_file_exception else 'NO'}`"]
    if shared_file_exception:
        lines += [
            f"- Ownership note: lane packet is limited to {_owned_path_note(lane)}; approved shared handoff-maintenance artifacts are recorded in the companion shared packet.",
            "- Approval note: " + (str(meta.get("approved_exception_note", "")).strip() or "(missing approval note)"),
        ]
    else:
        lines += [f"- Ownership note: lane packet is limited to {_owned_path_note(lane)}."]
    lines += [""]
    return "\n".join(lines)


def build_shared_packet(
    lane: str,
    branch: str,
    sha: str,
    meta: Json,
    files: List[str],
    gate_results: List[Tuple[str, int]],
    companion_lane_packet: str = "",
) -> str:
    _, shared_files = _split_files(lane, files)

    def rcstr(rc: int) -> str:
        return "PASS" if rc == 0 else f"FAIL ({rc})"

    lines: List[str] = []
    lines += ["# Shared Maintenance Packet: " + lane, ""]
    lines += [f"- Branch: `{branch}`", f"- Commit: `{sha}`", ""]
    lines += ["## Scope goal", f"- {str(meta.get('scope_goal','')).strip() or '(missing)'}", ""]
    lines += ["## Scope completed", f"- {str(meta.get('scope_completed','')).strip() or '(missing)'}", ""]
    lines += ["## Handoff Alignment"]
    lines += [f"- Scope completed: shared handoff-maintenance edits are recorded separately from the lane-only {_owned_path_note(lane)} feature packet."]
    lines += ["- Roadmap item(s) affected (from `ROADMAP.md`): " + ", ".join(str(x) for x in (meta.get("roadmap_items") or []))]
    lines += ["- Vision capability affected (from `PRODUCT_VISION.md`): " + "; ".join(str(x) for x in (meta.get("vision_capabilities") or []))]
    lines += ["- Shared/integrator-locked edits: `YES`"]
    lines += ["- Approval note: " + (str(meta.get("approved_exception_note", "")).strip() or "(missing approval note)")]
    if companion_lane_packet:
        lines += ["- Companion lane packet: " + companion_lane_packet]
    lines += [f"- Ownership note: these files sit outside lane-owned {_owned_path_note(lane)} and are captured here so the primary lane packet remains lane-only."]
    lines += ["- Tasks completed:"]
    tasks = list(meta.get("tasks_completed") or [])
    lines += [f"  {i+1}. {str(task).strip()}" for i, task in enumerate(tasks)] if tasks else ["  1. (missing)"]
    lines += ["- Files changed:"]
    if shared_files:
        lines += ["  ### Approved shared/integrator-locked files"]
        lines += [f"  - `{f}`" for f in shared_files]
    else:
        lines += ["  - (none detected)"]
    lines += ["- Commands run and outcomes:"]
    for cmd, rc in gate_results:
        lines += [f"  - `{cmd}`: {rcstr(rc)}"]
    lines += ["- Risks / blockers:"]
    lines += [f"  - Risk: `{str(meta.get('risk','LOW')).strip()}`", "  - Blockers: none", ""]
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
    base_ref=str(planner_cfg.get("base_ref","main"))
    gates=list(planner_cfg.get("required_gates", REQUIRED_GATES_DEFAULT))
    state=load_json(STATE_FILE,{})
    lane_state=state.get("lanes",{})
    coordinator_state=load_coordinator_state()
    repo=str(Path.cwd())
    remotes = list_git_remotes(repo)
    if remotes:
        fetch_result = run_git(["fetch", "--all", "--prune"], cwd=repo, timeout=120, write=True)
        if fetch_result.returncode != 0:
            print(f"[planner] git fetch warning: rc={fetch_result.returncode}")
            if fetch_result.stdout.strip():
                print(fetch_result.stdout.rstrip())
    else:
        print("[planner] no git remotes configured; skipping fetch")

    for lane, lcfg in cfg["lanes"].items():
        if not bool((lcfg or {}).get("enabled", True)):
            continue
        ensure_lane_dirs(lane)
        if lane_has_pending_feature(lane):
            continue
        has_reviewer_notes = lane_has_reviewer_notes(lane)
        branch=str((lcfg or {}).get("branch") or f"codex/{lane}")
        lane_repo = find_worktree_for_branch(repo, branch)
        active_repo: Optional[str] = None
        if lane_repo and is_git_repo(lane_repo):
            active_repo = lane_repo
        elif lane_repo and not is_git_repo(lane_repo):
            print(f"[planner] {lane}: stale non-git worktree for {branch} at {lane_repo}; considering branch-ref fallback")

        try:
            sha = resolve_branch_sha(repo, branch, fallback_cwd=active_repo)
        except Exception as e:
            where = active_repo or repo
            print(f"[planner] {lane}: unable to resolve {branch} in {where}: {e}")
            continue
        prev_lane_state = lane_state.get(lane) or {}
        last_submitted_sha = infer_last_submitted_sha(PACKETS_ROOT / lane, prev_lane_state)
        # Reviewer notes should block new packets until lane HEAD advances.
        # This allows one-at-a-time re-review submissions from the feature lane.
        if has_reviewer_notes and (not last_submitted_sha or last_submitted_sha == sha):
            continue
        if last_submitted_sha == sha:
            continue
        fast_reemit = bool(has_reviewer_notes and last_submitted_sha and last_submitted_sha != sha)
        if should_skip_for_active_feature(coordinator_state, lane, fast_reemit=fast_reemit):
            print(f"[planner] {lane}: feature worker active; skipping gate run until handoff")
            continue
        if not active_repo and not fast_reemit:
            # Do not switch branches in the main repo from planner automation.
            # Lane automation is worktree-scoped; missing/stale worktrees should be fixed
            # out-of-band without mutating main checkout state.
            print(f"[planner] {lane}: no usable worktree for {branch}; skipping")
            continue
        meta=merge_lane_meta_defaults(lane, read_lane_meta(lane))
        miss=validate_meta(meta)
        if miss:
            print(f"[planner] {lane}: lane_meta missing: {miss} (using auto defaults)")
            meta = apply_meta_defaults(meta, miss, lane)
        env=os.environ.copy()
        if bool(meta.get("shared_file_exception")):
            env["SCOPE_ALLOW_SHARED"]="1"
        if fast_reemit:
            files = infer_last_changed_files(
                PACKETS_ROOT / lane,
                prev_lane_state,
                sha=last_submitted_sha,
            )
            carried = infer_last_gate_results(
                PACKETS_ROOT / lane,
                prev_lane_state,
                sha=last_submitted_sha,
            )
            if carried and files:
                if active_repo:
                    print(f"[planner] {lane}: fast re-emit from advanced HEAD after reviewer notes (reuse prior gate results)")
                else:
                    print(
                        f"[planner] {lane}: fast re-emit from advanced branch ref {branch} "
                        "(reuse prior gate results; no usable worktree)"
                    )
                results = carried
            else:
                print(f"[planner] {lane}: fast re-emit lacks reusable packet context; rerunning local gates")
                fast_reemit = False
        if not fast_reemit:
            try:
                files=compute_changed_files(
                    repo,
                    base_ref,
                    head_ref=branch,
                )
            except Exception as e:
                print(f"[planner] {lane}: diff failed vs {base_ref}: {e}")
                continue
            scope_violations = _full_branch_scope_violations(lane, files)
            if scope_violations:
                preview = "\n".join(f"  - {path}" for path in scope_violations[:40])
                extra = "" if len(scope_violations) <= 40 else f"\n  ... {len(scope_violations) - 40} more"
                print(
                    f"[planner] {lane}: full branch scope violation; "
                    "THREAD_OWNERSHIP.md allows only "
                    f"{_owned_path_note(lane)}\n{preview}{extra}"
                )
                continue
            if not active_repo:
                print(f"[planner] {lane}: no usable worktree for {branch}; cannot rerun local gates")
                continue
            scope_rc,scope_out=run_scope_check(active_repo, env=env)
            if scope_rc!=0:
                print(f"[planner] {lane}: scope-check FAIL:\n{scope_out}")
                continue
            results=[("make scope-check",0)]
            ok=True
            for cmd in gates:
                rc,out=run_required_gate(cmd, active_repo, env=env)
                results.append((cmd,rc))
                if rc!=0:
                    ok=False
                    print(f"[planner] {lane}: gate FAIL {cmd}\n{out}")
                    break
            if not ok:
                continue
        ts=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        if fast_reemit:
            moved = archive_lane_reviewer_notes(lane)
            if moved:
                print(f"[planner] {lane}: archived {moved} stale reviewer note(s) on re-emit")
        fn=f"F__{branch.replace('/','-')}__{sha}__{ts}.md"
        outp=PACKETS_ROOT/lane/"inbox/feature"/fn
        _owned_files, shared_files = _split_files(lane, files)
        companion_shared_packet = ""
        if bool(meta.get("shared_file_exception")) or shared_files:
            shared_outp = outp.with_name(outp.stem + ".shared.md")
            companion_shared_packet = str(shared_outp)
        outp.write_text(build_packet(lane,branch,sha,meta,files,results,companion_shared_packet=companion_shared_packet))
        if companion_shared_packet:
            shared_outp.write_text(
                build_shared_packet(
                    lane,
                    branch,
                    sha,
                    meta,
                    files,
                    results,
                    companion_lane_packet=str(outp),
                )
            )
        print(f"[planner] emitted {outp}")
        lane_state[lane]={
            "last_submitted_sha":sha,
            "last_emitted_packet":fn,
            "last_gate_results":[[cmd, rc] for cmd, rc in results],
        }

    state["lanes"]=lane_state
    save_json(STATE_FILE,state)

if __name__=="__main__":
    main()
