#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import time
from pathlib import Path
from typing import Any, Dict


def load_json(path: Path, default: Dict[str, Any]) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text())
    except Exception:
        return default


def save_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True))


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Detached local Codex CLI worker")
    ap.add_argument("--spec", required=True, help="Path to the JSON job spec")
    return ap.parse_args()


def _terminate_process_group(pid: int, sig: int) -> None:
    try:
        os.killpg(pid, sig)
    except OSError:
        try:
            os.kill(pid, sig)
        except OSError:
            pass


def main() -> int:
    args = parse_args()
    spec_path = Path(args.spec)
    spec = load_json(spec_path, {})
    cmd = [str(x) for x in list(spec.get("cmd") or [])]
    cwd = str(spec.get("cwd") or os.getcwd())
    timeout_seconds = float(spec.get("timeout_seconds") or 0) or None
    env = os.environ.copy()
    env.update({str(k): str(v) for k, v in dict(spec.get("env_overrides") or {}).items()})
    stdin_path_value = str(spec.get("stdin_path") or "").strip()
    stdin_path = Path(stdin_path_value) if stdin_path_value else None
    output_path = Path(str(spec.get("output_path") or spec_path.with_suffix(".out.log")))
    result_path = Path(str(spec.get("result_path") or spec_path.with_suffix(".result.json")))

    started_at = time.time()
    stdout_text = ""
    status = "error"
    rc = 1
    error = ""

    try:
        stdin_handle = open(stdin_path, "r", encoding="utf-8") if stdin_path else None
        try:
            proc = subprocess.Popen(
                cmd,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=stdin_handle if stdin_handle is not None else subprocess.DEVNULL,
                text=True,
                env=env,
                start_new_session=True,
            )
            try:
                stdout_text, _ = proc.communicate(timeout=timeout_seconds)
            except subprocess.TimeoutExpired as exc:
                _terminate_process_group(proc.pid, signal.SIGTERM)
                try:
                    stdout_text, _ = proc.communicate(timeout=5)
                except subprocess.TimeoutExpired:
                    _terminate_process_group(proc.pid, signal.SIGKILL)
                    stdout_text, _ = proc.communicate()
                partial = exc.stdout if isinstance(exc.stdout, str) else ""
                if partial and not stdout_text:
                    stdout_text = partial
                rc = 124
                status = "timeout"
                error = f"timed out after {timeout_seconds}s"
            else:
                stdout_text = stdout_text or ""
                rc = int(proc.returncode)
                status = "ok" if rc == 0 else "error"
        finally:
            if stdin_handle is not None:
                stdin_handle.close()
    except Exception as exc:
        rc = 1
        status = "error"
        error = f"{type(exc).__name__}: {exc}"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(stdout_text)
    save_json(
        result_path,
        {
            "status": status,
            "rc": rc,
            "error": error,
            "started_at": started_at,
            "ended_at": time.time(),
            "spec_path": str(spec_path),
            "output_path": str(output_path),
        },
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
