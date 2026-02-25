#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import json
LANES = ['feat-context-storage', 'feat-webconsole-core', 'feat-webconsole-ui', 'feat-ux-flow', 'feat-commands']
def ensure_dirs():
    for lane in LANES:
        base = Path(".codex/packets/lanes")/lane
        (base/"inbox/feature").mkdir(parents=True, exist_ok=True)
        (base/"inbox/reviewer").mkdir(parents=True, exist_ok=True)
        (base/"outbox/lane").mkdir(parents=True, exist_ok=True)
        (base/"outbox/integrator").mkdir(parents=True, exist_ok=True)
        (base/"archive").mkdir(parents=True, exist_ok=True)
    Path(".codex/packet_router").mkdir(parents=True, exist_ok=True)
    Path(".codex/packet_planner").mkdir(parents=True, exist_ok=True)
def write_example():
    lanes_cfg={lane:{"branch":f"codex/{lane}"} for lane in LANES}
    example={
        "model":"gpt-5.1-codex",
        "codex_cmd":"codex",
        "idle_seconds":1.2,
        "reviewer_timeout":180,
        "integrator_timeout":900,
        "lanes":lanes_cfg,
        "planner":{"base_ref":"codex/integrator","required_gates":[
            "./quality-format.sh --check","./quality-lint.sh","./quality-test.sh","./typecheck-test.sh","make ci"
        ]}
    }
    out=Path(".codex/packet_router/example.json")
    out.write_text(json.dumps(example, indent=2))
    print(out)
def ensure_gitignore():
    gi=Path(".gitignore"); line=".codex/"
    if gi.exists():
        if line not in gi.read_text().splitlines():
            gi.write_text(gi.read_text().rstrip()+"\n"+line+"\n")
    else:
        gi.write_text(line+"\n")
if __name__=="__main__":
    ensure_dirs(); write_example(); ensure_gitignore(); print("[setup] done")
