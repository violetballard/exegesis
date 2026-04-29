#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

LANES = [
    'feat-context-storage',
    'feat-ux-flow',
    'feat-commands',
    'feat-retrieval-fts',
    'feat-a2ui-contract',
    'feat-engine-runs',
    'feat-console',
]
TEMPLATE = {
  "scope_goal": "",
  "tasks_completed": [],
  "risk": "LOW",
  "roadmap_items": [],
  "vision_capabilities": [],
  "routing_provider_impact": "None",
  "proposed_readme_patch": "",
  "shared_file_exception": False,
  "kickoff_budget_note": "",
  "approved_exception_note": ""
}

if __name__ == "__main__":
    base = Path(".codex/lane_meta")
    base.mkdir(parents=True, exist_ok=True)
    for lane in LANES:
        p = base / f"{lane}.json"
        if not p.exists():
            p.write_text(json.dumps(TEMPLATE, indent=2))
            print(p)
