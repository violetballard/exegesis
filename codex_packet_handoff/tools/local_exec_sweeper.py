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

CODEX_EXEC_RE = re.compile(r"\bcodex\b.*\bexec\b", re.IGNORECASE)
LOCAL_EXEC_MARKERS = ("--skip-git-repo-check", "workspace-write", "--local-provider", "lmstudio")
PROMPT_ROOT_SUFFIXES = (
    Path(".codex/feature_runner/prompts"),
    Path(".codex/packet_router/logs"),
    Path(".codex/packet_router/local_jobs"),
)


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


def _repo_prompt_roots(repo_root: Path) -> List[Path]:
    resolved_repo = repo_root.resolve()
    roots: List[Path] = []
    for suffix in PROMPT_ROOT_SUFFIXES:
        roots.append((resolved_repo / suffix).resolve())
    return roots


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


def find_repo_owned_local_exec_processes(repo_root: Path) -> Dict[int, Dict[str, str]]:
    try:
        proc = subprocess.run(
            ["ps", "-axo", "pid=,command="],
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
        parts = row.split(None, 1)
        if len(parts) != 2 or not parts[0].isdigit():
            continue
        pid = int(parts[0])
        cmd = parts[1]
        if pid == os.getpid():
            continue
        if not CODEX_EXEC_RE.search(cmd):
            continue
        if not all(marker in cmd for marker in LOCAL_EXEC_MARKERS):
            continue
        stdin_path = _stdin_path_for_pid(pid)
        if not (
            _is_repo_owned_prompt_path(repo_root, stdin_path)
            or _is_repo_owned_prompt_reference(repo_root, cmd)
        ):
            continue
        owned[pid] = {"command": cmd, "stdin_path": stdin_path}
    return owned


def find_orphaned_repo_local_exec_pids(repo_root: Path, tracked_pids: Iterable[int]) -> List[int]:
    tracked = {int(pid) for pid in tracked_pids if int(pid) > 0}
    owned = find_repo_owned_local_exec_processes(repo_root)
    return sorted(pid for pid in owned if pid not in tracked)


def terminate_local_exec_pids(pids: Iterable[int], *, grace_seconds: float = 1.0) -> List[int]:
    target_pids = sorted({int(pid) for pid in pids if int(pid) > 0})
    terminated: List[int] = []
    for pid in target_pids:
        try:
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
            os.kill(pid, signal.SIGKILL)
        except OSError:
            pass
    return terminated
