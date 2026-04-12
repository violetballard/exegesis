#!/usr/bin/env python3
from __future__ import annotations

import contextlib
import fcntl
import os
import signal
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Optional, Sequence

REPO_ROOT = Path(__file__).resolve().parents[2]
GIT_WRITE_LOCK = REPO_ROOT / ".codex/git_ops/write.lock"


@dataclass(frozen=True)
class GitRunResult:
    args: tuple[str, ...]
    returncode: int
    stdout: str
    timed_out: bool = False


def _kill_process_group(pid: int) -> None:
    with contextlib.suppress(ProcessLookupError):
        os.killpg(pid, signal.SIGTERM)
    time.sleep(0.1)
    with contextlib.suppress(ProcessLookupError):
        os.killpg(pid, signal.SIGKILL)


@contextlib.contextmanager
def git_write_lock(repo_root: Path = REPO_ROOT, *, timeout_seconds: float = 60.0):
    lock_path = repo_root / ".codex/git_ops/write.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+") as handle:
        deadline = time.time() + timeout_seconds
        while True:
            try:
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.time() >= deadline:
                    raise TimeoutError(f"Timed out waiting for git write lock at {lock_path}")
                time.sleep(0.1)
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def run_git(
    args: Sequence[str],
    *,
    cwd: str | Path = REPO_ROOT,
    timeout: float = 120.0,
    write: bool = False,
    repo_root: Path = REPO_ROOT,
    lock_timeout: float = 60.0,
    acquire_write_lock: bool = True,
    input_text: str | None = None,
    env: Optional[Mapping[str, str]] = None,
) -> GitRunResult:
    if not args:
        raise ValueError("git args must not be empty")

    def _invoke() -> GitRunResult:
        proc = subprocess.Popen(
            ["git", *args],
            cwd=str(cwd),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.PIPE if input_text is not None else subprocess.DEVNULL,
            text=True,
            env=dict(env or os.environ),
            start_new_session=True,
            close_fds=True,
        )
        try:
            out, _ = proc.communicate(input=input_text, timeout=timeout)
            return GitRunResult(tuple(str(x) for x in args), proc.returncode, out or "")
        except subprocess.TimeoutExpired:
            _kill_process_group(proc.pid)
            out, _ = proc.communicate()
            timeout_text = ((out or "").rstrip() + "\n[TIMEOUT]").strip()
            return GitRunResult(
                tuple(str(x) for x in args),
                124,
                timeout_text + ("\n" if timeout_text else ""),
                timed_out=True,
            )

    if write and acquire_write_lock:
        with git_write_lock(repo_root, timeout_seconds=lock_timeout):
            return _invoke()
    return _invoke()


def require_git_output(
    args: Sequence[str],
    *,
    cwd: str | Path = REPO_ROOT,
    timeout: float = 120.0,
    write: bool = False,
    repo_root: Path = REPO_ROOT,
    lock_timeout: float = 60.0,
    acquire_write_lock: bool = True,
    input_text: str | None = None,
    env: Optional[Mapping[str, str]] = None,
) -> str:
    result = run_git(
        args,
        cwd=cwd,
        timeout=timeout,
        write=write,
        repo_root=repo_root,
        lock_timeout=lock_timeout,
        acquire_write_lock=acquire_write_lock,
        input_text=input_text,
        env=env,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stdout.strip() or f"git {' '.join(result.args)} failed with rc={result.returncode}")
    return result.stdout.strip()


def _normalize_repo_relpaths(repo_root: Path, paths: Iterable[str | Path]) -> list[Path]:
    relpaths: list[Path] = []
    for raw in paths:
        path = Path(raw)
        if path.is_absolute():
            path = path.resolve().relative_to(repo_root.resolve())
        relpaths.append(path)
    return relpaths


def commit_paths_via_fast_import(
    repo_root: Path,
    *,
    message: str,
    paths: Iterable[str | Path],
    ref: str = "refs/heads/main",
) -> str:
    repo_root = repo_root.resolve()
    relpaths = _normalize_repo_relpaths(repo_root, paths)
    with git_write_lock(repo_root):
        parent = require_git_output(["rev-parse", ref], cwd=repo_root, repo_root=repo_root, acquire_write_lock=False)
        ident = require_git_output(["var", "GIT_COMMITTER_IDENT"], cwd=repo_root, repo_root=repo_root, acquire_write_lock=False)
        entries: list[tuple[str, str, str]] = []
        for relpath in relpaths:
            full = repo_root / relpath
            result = run_git(
                ["hash-object", "-w", "--", str(relpath)],
                cwd=repo_root,
                timeout=60.0,
                repo_root=repo_root,
                acquire_write_lock=False,
            )
            if result.returncode != 0:
                raise RuntimeError(result.stdout.strip() or f"Unable to hash {relpath}")
            mode = "100755" if os.access(full, os.X_OK) else "100644"
            entries.append((mode, result.stdout.strip(), relpath.as_posix()))

        stream_lines = [
            f"commit {ref}",
            f"committer {ident}",
            "data <<MSG",
            message,
            "MSG",
            f"from {parent}",
        ]
        for mode, blob, relpath in entries:
            stream_lines.append(f"M {mode} {blob} {relpath}")
        stream = "\n".join(stream_lines) + "\n"

        import_result = run_git(
            ["fast-import", "--quiet"],
            cwd=repo_root,
            timeout=120.0,
            repo_root=repo_root,
            acquire_write_lock=False,
            input_text=stream,
        )
        if import_result.returncode != 0:
            crash_report = next((repo_root / ".git").glob("fast_import_crash_*"), None)
            extra = f" crash={crash_report}" if crash_report else ""
            raise RuntimeError((import_result.stdout.strip() or "git fast-import failed") + extra)
        return require_git_output(["rev-parse", ref], cwd=repo_root, repo_root=repo_root, acquire_write_lock=False)
