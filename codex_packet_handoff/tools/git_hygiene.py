#!/usr/bin/env python3
from __future__ import annotations

import argparse
import contextlib
import os
import re
import shutil
import signal
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

try:
    from git_ops import run_git
except ImportError:  # pragma: no cover - package execution fallback
    from .git_ops import run_git

REPO_ROOT = Path(__file__).resolve().parents[2]
TMP_WORKTREE_ROOT = "/private/tmp/"
TMP_WORKTREE_PREFIXES = (
    "ctx-",
    "qual-feat-context-storage-",
)
STALE_GIT_HELPER_MIN_AGE_SECONDS = 300
STALE_GIT_READONLY_MIN_AGE_SECONDS = 900
STALE_INDEX_LOCK_MIN_AGE_SECONDS = 300
GIT_HELPER_RE = re.compile(r"(?:^|\s)\S*git (write-tree|read-tree|commit-tree|commit)(?:\s|$)")
GIT_READONLY_RE = re.compile(
    r"(?:^|\s)\S*git (status|diff(?:-index|-tree)?|show|ls-tree|rev-parse)(?:\s|$)"
)


@dataclass(frozen=True)
class GitProcess:
    pid: int
    ppid: int
    age_seconds: int
    command: str


@dataclass(frozen=True)
class WorktreeEntry:
    path: str
    head: str = ""
    branch: Optional[str] = None
    detached: bool = False
    locked_reason: Optional[str] = None


def parse_etime_seconds(raw: str) -> int:
    text = raw.strip()
    if not text:
        return 0
    days = 0
    if "-" in text:
        day_part, text = text.split("-", 1)
        days = int(day_part) * 86400
    parts = [int(part) for part in text.split(":")]
    if len(parts) == 3:
        hours, minutes, seconds = parts
        return days + hours * 3600 + minutes * 60 + seconds
    if len(parts) == 2:
        minutes, seconds = parts
        return days + minutes * 60 + seconds
    if len(parts) == 1:
        return days + parts[0]
    raise ValueError(f"Unsupported etime format: {raw!r}")


def parse_git_processes(ps_output: str) -> List[GitProcess]:
    out: List[GitProcess] = []
    for raw in ps_output.splitlines():
        line = raw.strip()
        if not line:
            continue
        parts = line.split(None, 3)
        if len(parts) != 4:
            continue
        try:
            pid = int(parts[0])
            ppid = int(parts[1])
            age_seconds = parse_etime_seconds(parts[2])
        except ValueError:
            continue
        out.append(GitProcess(pid=pid, ppid=ppid, age_seconds=age_seconds, command=parts[3]))
    return out


def find_stale_git_helpers(
    ps_output: str,
    *,
    min_age_seconds: int = STALE_GIT_HELPER_MIN_AGE_SECONDS,
    readonly_min_age_seconds: int = STALE_GIT_READONLY_MIN_AGE_SECONDS,
) -> List[GitProcess]:
    out: List[GitProcess] = []
    for proc in parse_git_processes(ps_output):
        if proc.age_seconds >= min_age_seconds and GIT_HELPER_RE.search(proc.command):
            out.append(proc)
            continue
        if proc.ppid == 1 and proc.age_seconds >= readonly_min_age_seconds and GIT_READONLY_RE.search(proc.command):
            out.append(proc)
    return out


def parse_worktree_porcelain(text: str) -> List[WorktreeEntry]:
    out: List[WorktreeEntry] = []
    current: Dict[str, object] = {}
    for raw in text.splitlines() + [""]:
        line = raw.rstrip()
        if not line:
            if current.get("path"):
                out.append(
                    WorktreeEntry(
                        path=str(current["path"]),
                        head=str(current.get("head") or ""),
                        branch=str(current.get("branch")) if current.get("branch") else None,
                        detached=bool(current.get("detached")),
                        locked_reason=str(current.get("locked_reason")) if current.get("locked_reason") else None,
                    )
                )
            current = {}
            continue
        if line.startswith("worktree "):
            current["path"] = line.split(" ", 1)[1].strip()
        elif line.startswith("HEAD "):
            current["head"] = line.split(" ", 1)[1].strip()
        elif line.startswith("branch "):
            current["branch"] = line.split(" ", 1)[1].strip()
        elif line == "detached":
            current["detached"] = True
        elif line.startswith("locked"):
            current["locked_reason"] = line.split(" ", 1)[1].strip() if " " in line else ""
    return out


def is_stale_temp_worktree(entry: WorktreeEntry) -> bool:
    if not entry.path.startswith(TMP_WORKTREE_ROOT):
        return False
    base = Path(entry.path).name
    if not any(base.startswith(prefix) for prefix in TMP_WORKTREE_PREFIXES):
        return False
    return entry.detached or bool(entry.locked_reason)


def _find_metadata_dir(repo_root: Path, worktree_path: Path) -> Optional[Path]:
    base = repo_root / ".git" / "worktrees"
    if not base.exists():
        return None
    target = str(worktree_path / ".git")
    for entry in base.iterdir():
        gitdir_file = entry / "gitdir"
        try:
            content = gitdir_file.read_text().strip()
        except Exception:
            continue
        if content == target:
            return entry
    return None


def reap_stale_git_helpers(
    repo_root: Path = REPO_ROOT,
    *,
    min_age_seconds: int = STALE_GIT_HELPER_MIN_AGE_SECONDS,
    readonly_min_age_seconds: int = STALE_GIT_READONLY_MIN_AGE_SECONDS,
) -> List[int]:
    proc = subprocess.run(
        ["ps", "-axo", "pid,ppid,etime,command"],
        cwd=str(repo_root),
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return []
    removed: List[int] = []
    for helper in find_stale_git_helpers(
        proc.stdout,
        min_age_seconds=min_age_seconds,
        readonly_min_age_seconds=readonly_min_age_seconds,
    ):
        with contextlib.suppress(ProcessLookupError):
            os.kill(helper.pid, signal.SIGTERM)
        time.sleep(0.02)
        try:
            os.kill(helper.pid, 0)
        except OSError:
            removed.append(helper.pid)
            continue
        with contextlib.suppress(ProcessLookupError):
            os.kill(helper.pid, signal.SIGKILL)
        removed.append(helper.pid)
    return sorted(set(removed))


def prune_stale_temp_worktrees(repo_root: Path = REPO_ROOT) -> List[str]:
    proc = run_git(["worktree", "list", "--porcelain"], cwd=repo_root, timeout=120)
    if proc.returncode != 0:
        return []
    removed: List[str] = []
    for entry in parse_worktree_porcelain(proc.stdout):
        if not is_stale_temp_worktree(entry):
            continue
        worktree_path = Path(entry.path)
        metadata_dir = _find_metadata_dir(repo_root, worktree_path)
        try:
            if worktree_path.exists():
                shutil.rmtree(worktree_path)
        except Exception:
            pass
        if metadata_dir is not None:
            try:
                shutil.rmtree(metadata_dir)
            except Exception:
                pass
        removed.append(entry.path)
    if removed:
        run_git(["worktree", "prune", "--expire", "now"], cwd=repo_root, timeout=120, write=True)
    return sorted(set(removed))


def prune_stale_index_locks(
    repo_root: Path = REPO_ROOT,
    *,
    min_age_seconds: int = STALE_INDEX_LOCK_MIN_AGE_SECONDS,
) -> List[str]:
    now = time.time()
    removed: List[str] = []
    patterns = [
        repo_root / ".git" / "index.lock",
        repo_root / ".git" / "worktrees",
    ]
    lock_paths: List[Path] = []
    if patterns[0].exists():
        lock_paths.append(patterns[0])
    if patterns[1].exists():
        lock_paths.extend(patterns[1].glob("*/index.lock"))
    for lock_path in lock_paths:
        try:
            age_seconds = now - lock_path.stat().st_mtime
        except FileNotFoundError:
            continue
        if age_seconds < min_age_seconds:
            continue
        try:
            lock_path.unlink()
        except FileNotFoundError:
            continue
        except Exception:
            continue
        removed.append(str(lock_path))
    return sorted(set(removed))


def run_hygiene(repo_root: Path = REPO_ROOT) -> Dict[str, object]:
    stale_git_pids = reap_stale_git_helpers(repo_root)
    stale_index_locks = prune_stale_index_locks(repo_root)
    temp_worktrees_removed = prune_stale_temp_worktrees(repo_root)
    return {
        "stale_git_pids": stale_git_pids,
        "stale_index_locks": stale_index_locks,
        "temp_worktrees_removed": temp_worktrees_removed,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Reap stale git helpers and prune stale temp worktrees.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    args = parser.parse_args()
    summary = run_hygiene(Path(args.repo_root))
    print(f"stale_git_pids={summary['stale_git_pids']}")
    print(f"stale_index_locks={summary['stale_index_locks']}")
    print(f"temp_worktrees_removed={summary['temp_worktrees_removed']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
