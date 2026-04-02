#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

try:
    from lane_profiles import default_lane_meta
except ImportError:  # pragma: no cover - package execution fallback
    from .lane_profiles import default_lane_meta

LANES = [
    'feat-context-storage',
    'feat-commands',
    'feat-retrieval-fts',
    'feat-a2ui-contract',
    'feat-engine-runs',
    'feat-console-shell',
    'feat-console-workflow',
]

if __name__ == "__main__":
    base = Path(".codex/lane_meta")
    base.mkdir(parents=True, exist_ok=True)
    for lane in LANES:
        p = base / f"{lane}.json"
        if not p.exists():
            p.write_text(json.dumps(default_lane_meta(lane), indent=2))
            print(p)
