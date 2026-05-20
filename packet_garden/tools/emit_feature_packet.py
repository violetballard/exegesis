#!/usr/bin/env python3
from __future__ import annotations
import argparse
from datetime import datetime
from pathlib import Path

TEMPLATE = """# Feature → Review Packet

- Branch: {branch}
- Commit: {sha}
- Lane: {lane}

## Tasks completed
1. (fill)

## Files changed (paths)
- (fill)

## Commands run (required gates)
- ./quality-format.sh --check
- ./quality-lint.sh
- ./quality-test.sh
- ./typecheck-test.sh
- make ci

## Risks / notes
- (fill)
"""

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--lane", required=True)
    ap.add_argument("--branch", required=True)
    ap.add_argument("--sha", required=True)
    a=ap.parse_args()
    inbox=Path(".codex/packets/lanes")/a.lane/"inbox/feature"
    inbox.mkdir(parents=True, exist_ok=True)
    ts=datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    name=f"F__{a.branch.replace('/','-')}__{a.sha}__{ts}.md"
    p=inbox/name
    p.write_text(TEMPLATE.format(lane=a.lane, branch=a.branch, sha=a.sha))
    print(p)
