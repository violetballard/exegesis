#!/usr/bin/env python3
from __future__ import annotations

import errno
import os
import re
import signal
import subprocess
import time
from pathlib import Path
from typing import Dict, Iterable, List

LOCAL_AGENT_RE = re.compile(r"(?:\bcodex\b.*\bexec\b|\bopencode\b.*\brun\b)", re.IGNORECASE)
LOCAL_EXEC_MARKERS = ("--skip-git-repo-check", "workspace-write", "--local-provider", "lmstudio")
OPENCODE_LOCAL_MARKERS = ("--model", "lmstudio/qwen3.6-27b")
TEST_RUNNER_RE = re.compile(
    r"(^|/|\s)(quality-test\.sh|typecheck-test\.sh|python(?:\d+(?:\.\d+)?)?\s+-m\s+(unittest|pytest)\b|pytest\b)",
    re.IGNORECASE,
)
PROMPT_ROOT_SUFFIXES = (
    Path(".codex/feature_runner/prompts"),
    Path(".codex/feature_runner/logs"),
    Path(".codex/packet_router/logs"),
    Path(".codex/packet_router/local_jobs"),
)
MANAGED_WORKTREE_ROOT = Path.home() / ".codex/worktrees"
ORPHAN_TEST_RUNNER_MIN_AGE_SECONDS = int(os.environ.get("ORPHAN_TEST_RUNNER_MIN_AGE_SECONDS", "1800"))
ORPHAN_TEST_RUNNER_RSS_LIMIT_KB = int(os.environ.get("ORPHAN_TEST_RUNNER_RSS_LIMIT_KB", "1500000"))
CONTEXT_EXHAUSTION_MARKERS = (
    'Error: "Context size has been exceeded."',
    "Error: Context size has been exceeded.",
    "Context size has been exceeded",
    "ERROR: stream disconnected before completion: Context size has been exceeded",
    "ERROR: stream disconnected before completion: context size has been exceeded",
    "ERROR: stream disconnected before completion: Context length exceeded",
    "ERROR: stream disconnected before completion: context length exceeded",
    "Error: context length exceeded",
    "error: context length exceeded",
)
CONTEXT_EXHAUSTION_TAIL_BYTES = int(os.environ.get("CONTEXT_EXHAUSTION_TAIL_BYTES", "65536"))


def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError as exc:
        if getattr(exc, "errno", None) == errno.EPERM:
            return True
        return False


def _pgid_alive(pgid: int) -> bool:
    if pgid <= 0:
        return False
    try:
        os.killpg(pgid, 0)
        return True
    except OSError as exc:
        if getattr(exc, "errno", None) == errno.EPERM:
            return True
        return False


def _stdin_path_for_pid(pid: int) -> str:
    try:
        proc = subprocess.run(
            ["lsof", "-a", "-p", str(pid), "-d", "0", "-Fn"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=2.0,
        )
    except Exception:
        return ""
    if proc.returncode != 0:
        return ""
    for raw in (proc.stdout or "").splitlines():
        if raw.startswith("n"):
            return raw[1:].strip()
    return ""


def _cwd_path_for_pid(pid: int) -> str:
    try:
        proc = subprocess.run(
            ["lsof", "-a", "-p", str(pid), "-d", "cwd", "-Fn"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=2.0,
        )
    except Exception:
        return ""
    if proc.returncode != 0:
        return ""
    for raw in (proc.stdout or "").splitlines():
        if raw.startswith("n"):
            return raw[1:].strip()
    return ""


def _elapsed_seconds(token: str) -> int:
    text = str(token or "").strip()
    if not text:
        return 0
    days = 0
    if "-" in text:
        day_token, text = text.split("-", 1)
        try:
            days = int(day_token)
        except ValueError:
            return 0
    parts = text.split(":")
    try:
        values = [int(part) for part in parts]
    except ValueError:
        return 0
    if len(values) == 3:
        hours, minutes, seconds = values
    elif len(values) == 2:
        hours = 0
        minutes, seconds = values
    else:
        return 0
    return days * 86400 + hours * 3600 + minutes * 60 + seconds


def _repo_prompt_roots(repo_root: Path) -> List[Path]:
    resolved_repo = repo_root.resolve()
    roots: List[Path] = []
    for suffix in PROMPT_ROOT_SUFFIXES:
        roots.append((resolved_repo / suffix).resolve())
    return roots


def _tail_contains_context_exhaustion(path_value: str) -> bool:
    if not path_value:
        return False
    try:
        path = Path(path_value).expanduser().resolve(strict=False)
        if not path.exists() or not path.is_file():
            return False
        size = path.stat().st_size
        with path.open("rb") as handle:
            if size > CONTEXT_EXHAUSTION_TAIL_BYTES:
                handle.seek(max(0, size - CONTEXT_EXHAUSTION_TAIL_BYTES))
            text = handle.read().decode("utf-8", errors="replace")
    except OSError:
        return False
    return any(marker in text for marker in CONTEXT_EXHAUSTION_MARKERS)


def _is_repo_owned_prompt_path(repo_root: Path, prompt_path: str) -> bool:
    if not prompt_path:
        return False
    try:
        path = Path(prompt_path).expanduser().resolve(strict=False)
    except Exception:
        return False
    if ".prompt." not in path.name:
        return False
    for root in _repo_prompt_roots(repo_root):
        try:
            path.relative_to(root)
            return True
        except ValueError:
            continue
    return False


def _is_repo_owned_prompt_reference(repo_root: Path, cmd: str) -> bool:
    if ".prompt." not in cmd:
        return False
    for root in _repo_prompt_roots(repo_root):
        if str(root) in cmd:
            return True
    return False


def _is_repo_or_managed_worktree_cwd(repo_root: Path, cwd_path: str) -> bool:
    if not cwd_path:
        return False
    try:
        cwd = Path(cwd_path).expanduser().resolve(strict=False)
        resolved_repo = repo_root.resolve()
        cwd.relative_to(resolved_repo)
        return True
    except ValueError:
        pass
    except Exception:
        return False

    try:
        worktree_root = MANAGED_WORKTREE_ROOT.resolve(strict=False)
        rel = cwd.relative_to(worktree_root)
    except ValueError:
        return False
    except Exception:
        return False
    parts = rel.parts
    if len(parts) < 2:
        return False
    return parts[1] == repo_root.name


def find_repo_owned_local_exec_processes(repo_root: Path) -> Dict[int, Dict[str, str]]:
    try:
        proc = subprocess.run(
            ["ps", "-axo", "pid=,ppid=,pgid=,command="],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=2.0,
        )
    except Exception:
        return {}
    if proc.returncode != 0:
        return {}

    owned: Dict[int, Dict[str, str]] = {}
    for raw in (proc.stdout or "").splitlines():
        row = raw.strip()
        if not row:
            continue
        parts = row.split(None, 3)
        if len(parts) != 4 or not parts[0].isdigit():
            continue
        pid = int(parts[0])
        ppid = parts[1]
        pgid = parts[2]
        cmd = parts[3]
        if pid == os.getpid():
            continue
        if not LOCAL_AGENT_RE.search(cmd):
            continue
        is_codex_local = all(marker in cmd for marker in LOCAL_EXEC_MARKERS)
        is_opencode_local = all(marker in cmd for marker in OPENCODE_LOCAL_MARKERS)
        if not (is_codex_local or is_opencode_local):
            continue
        stdin_path = _stdin_path_for_pid(pid)
        if not (
            _is_repo_owned_prompt_path(repo_root, stdin_path)
            or _is_repo_owned_prompt_reference(repo_root, cmd)
        ):
            continue
        owned[pid] = {
            "command": cmd,
            "stdin_path": stdin_path,
            "ppid": ppid,
            "pgid": pgid,
        }
    return owned


def find_repo_owned_local_exec_pids(repo_root: Path) -> List[int]:
    return sorted(find_repo_owned_local_exec_processes(repo_root))


def find_stale_repo_test_runner_pids(repo_root: Path, tracked_pids: Iterable[int]) -> List[int]:
    tracked = {int(pid) for pid in tracked_pids if int(pid) > 0}
    try:
        proc = subprocess.run(
            ["ps", "-axo", "pid=,ppid=,pgid=,etime=,rss=,command="],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=2.0,
        )
    except Exception:
        return []
    if proc.returncode != 0:
        return []

    stale: List[int] = []
    for raw in (proc.stdout or "").splitlines():
        parts = raw.strip().split(None, 5)
        if len(parts) < 6:
            continue
        try:
            pid = int(parts[0])
            ppid = int(parts[1])
            pgid = int(parts[2])
            elapsed = _elapsed_seconds(parts[3])
            rss = int(parts[4])
        except ValueError:
            continue
        cmd = parts[5]
        if pid == os.getpid() or pid in tracked:
            continue
        if not TEST_RUNNER_RE.search(cmd):
            continue
        if elapsed < ORPHAN_TEST_RUNNER_MIN_AGE_SECONDS and rss < ORPHAN_TEST_RUNNER_RSS_LIMIT_KB:
            continue
        cwd_path = _cwd_path_for_pid(pid)
        if not _is_repo_or_managed_worktree_cwd(repo_root, cwd_path):
            continue
        # Prefer terminating the whole process group so shell wrappers and their
        # large unittest children are reaped together.
        stale.append(pgid if pgid > 0 else pid)
        if ppid > 1 and ppid not in tracked:
            stale.append(ppid)
    return sorted({pid for pid in stale if pid > 0})


def find_orphaned_repo_local_exec_pids(repo_root: Path, tracked_pids: Iterable[int]) -> List[int]:
    tracked = {int(pid) for pid in tracked_pids if int(pid) > 0}
    owned = find_repo_owned_local_exec_processes(repo_root)
    return sorted(pid for pid in owned if pid not in tracked)


def find_stale_repo_local_exec_pids(
    repo_root: Path,
    tracked_pids: Iterable[int],
    *,
    detached_ok_pids: Iterable[int] = (),
) -> List[int]:
    """Find repo-owned local Codex execs that should not keep consuming LMS slots.

    Feature direct-exec jobs are launched by a short-lived helper, so they may
    normally be reparented to PID 1 while still being the current tracked lane
    worker. Router-owned local jobs should stay parented to the daemon; if one
    becomes reparented, it is stale and can keep an LMS prompt queued forever.
    """
    tracked = {int(pid) for pid in tracked_pids if int(pid) > 0}
    detached_ok = {int(pid) for pid in detached_ok_pids if int(pid) > 0}
    owned = find_repo_owned_local_exec_processes(repo_root)
    stale: List[int] = []
    for pid, meta in owned.items():
        try:
            ppid = int(meta.get("ppid") or 0)
        except ValueError:
            ppid = 0
        if ppid in tracked:
            continue
        if pid not in tracked or (ppid == 1 and pid not in detached_ok):
            stale.append(pid)
    return sorted(stale)


def find_context_exhausted_repo_local_exec_pids(pid_to_log_path: Dict[int, str]) -> List[int]:
    """Find tracked local execs whose current log shows terminal context exhaustion."""

    exhausted: List[int] = []
    for raw_pid, log_path in pid_to_log_path.items():
        try:
            pid = int(raw_pid)
        except (TypeError, ValueError):
            continue
        if pid <= 0 or not _pid_alive(pid):
            continue
        if _tail_contains_context_exhaustion(str(log_path or "")):
            exhausted.append(pid)
    return sorted(set(exhausted))


def terminate_local_exec_pids(pids: Iterable[int], *, grace_seconds: float = 1.0) -> List[int]:
    target_pids = sorted({int(pid) for pid in pids if int(pid) > 0})
    terminated: List[int] = []
    for pid in target_pids:
        try:
            pgid = os.getpgid(pid)
        except OSError:
            pgid = 0
        try:
            if pgid > 0 and pgid != os.getpgrp():
                os.killpg(pgid, signal.SIGTERM)
            else:
                os.kill(pid, signal.SIGTERM)
            terminated.append(pid)
        except OSError:
            continue
    deadline = time.time() + grace_seconds
    while time.time() < deadline:
        alive = [pid for pid in terminated if _pid_alive(pid)]
        if not alive:
            break
        time.sleep(0.1)
    for pid in terminated:
        if not _pid_alive(pid):
            continue
        try:
            pgid = os.getpgid(pid)
        except OSError:
            pgid = 0
        try:
            if pgid > 0 and pgid != os.getpgrp():
                os.killpg(pgid, signal.SIGKILL)
            else:
                os.kill(pid, signal.SIGKILL)
        except OSError:
            pass
    return terminated


def terminate_process_groups(pids_or_pgids: Iterable[int], *, grace_seconds: float = 1.0) -> List[int]:
    targets = sorted({int(pid) for pid in pids_or_pgids if int(pid) > 0})
    terminated: List[int] = []
    for target in targets:
        try:
            os.killpg(target, signal.SIGTERM)
            terminated.append(target)
            continue
        except OSError:
            pass
        try:
            os.kill(target, signal.SIGTERM)
            terminated.append(target)
        except OSError:
            continue
    deadline = time.time() + grace_seconds
    while time.time() < deadline:
        alive = [pid for pid in terminated if _pgid_alive(pid) or _pid_alive(pid)]
        if not alive:
            break
        time.sleep(0.1)
    for target in terminated:
        if not (_pgid_alive(target) or _pid_alive(target)):
            continue
        try:
            os.killpg(target, signal.SIGKILL)
            continue
        except OSError:
            pass
        try:
            os.kill(target, signal.SIGKILL)
        except OSError:
            pass
    return terminated
