#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

try:
    from git_ops import commit_paths_via_fast_import, commit_tracked_changes_via_fast_import
except ImportError:  # pragma: no cover - package execution fallback
    from .git_ops import commit_paths_via_fast_import, commit_tracked_changes_via_fast_import


def main() -> int:
    ap = argparse.ArgumentParser(description="Commit lane worktree changes using the isolated fast-import path.")
    ap.add_argument("--cwd", default=".")
    ap.add_argument("--message", required=True)
    ap.add_argument("paths", nargs="*")
    args = ap.parse_args()
    cwd = Path(args.cwd).resolve()
    if args.paths:
        commit_sha = commit_paths_via_fast_import(cwd, message=args.message, paths=args.paths)
    else:
        commit_sha = commit_tracked_changes_via_fast_import(cwd, message=args.message)
    print(commit_sha)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
