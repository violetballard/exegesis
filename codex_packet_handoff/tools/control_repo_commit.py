#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

try:
    from git_ops import commit_paths_via_fast_import
except ImportError:  # pragma: no cover - package execution fallback
    from .git_ops import commit_paths_via_fast_import

REPO_ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    ap = argparse.ArgumentParser(description="Commit selected control-plane files using the isolated fast-import path.")
    ap.add_argument("--repo-root", default=str(REPO_ROOT))
    ap.add_argument("--ref", default="refs/heads/main")
    ap.add_argument("--message", required=True)
    ap.add_argument("paths", nargs="+")
    args = ap.parse_args()
    commit_sha = commit_paths_via_fast_import(
        Path(args.repo_root),
        message=args.message,
        paths=args.paths,
        ref=str(args.ref),
    )
    print(commit_sha)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
