#!/usr/bin/env python3
from __future__ import annotations
import subprocess, time
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
RUN_FOR_SECONDS = 25*60
ROUTER_EVERY = 60
PLANNER_EVERY = 10*60

def run_cmd(args:list[str])->int:
    return subprocess.run(args, cwd=str(REPO)).returncode

def main()->None:
    start=time.time()
    next_router=start
    next_planner=start
    while (time.time()-start) < RUN_FOR_SECONDS:
        now=time.time()
        if now >= next_planner:
            run_cmd(["python","codex_packet_handoff/tools/planner.py"])
            next_planner += PLANNER_EVERY
        if now >= next_router:
            run_cmd(["python","codex_packet_handoff/tools/router.py"])
            next_router += ROUTER_EVERY
        time.sleep(1)

if __name__=="__main__":
    main()
