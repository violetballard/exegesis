---
name: status.report
description: "Show the real full status report for daemon, reviewer lanes, integrator, and feature-lane activity."
---

Run from repo root:
- `./codex_packet_handoff/tools/status_report.sh`

Access path selection:
- First check whether this Codex session is running on the development machine with this repo mounted locally.
- If `codex_packet_handoff/tools/daemon_ctl.py` exists locally, use the direct scripts in this skill. Local direct access remains the authoritative path.
- If local scripts are unavailable but `QUAL_MONITOR_URL` and `QUAL_MONITOR_TOKEN` are set, use `python codex_packet_handoff/tools/remote_monitor_client.py status` for compact status or `... full` for the sanitized full snapshot.
- Remote monitor access is only for VPN/home access; do not use it as a replacement for direct local scripts when working on the machine.
- Remote monitor output is sanitized and narrower than local script output, so say when a report is remote-derived.
- Local `remote_monitor_ctl.py status` is allowed only as a process-health check for the phone/VPN monitor. It is not the HTTP/network status path.

Manual breakdown if you need to inspect each step:
- `python codex_packet_handoff/tools/remote_monitor_ctl.py status`
- `python codex_packet_handoff/tools/daemon_ctl.py status`
- `python codex_packet_handoff/tools/status.py`
- `python codex_packet_handoff/tools/daemon_monitor.py`
- `ps -axo pid,etime,command | rg "codex exec|opencode run|codex_packet_handoff/tools/agents_coordinator.py" || true`
- `for f in $(ls -1t .codex/feature_runner/logs/*.log 2>/dev/null | head -n 5); do echo "FILE:$f"; tail -n 20 "$f"; done`
- `for f in $(ls -1t .codex/packet_router/logs/*.log 2>/dev/null | head -n 5); do echo "FILE:$f"; tail -n 40 "$f"; done`
- `tail -n 80 .codex/packet_coordinator/daemon.log 2>/dev/null || true`

CLI-first note:
- assume the operator launched Codex CLI with `codex --oss --local-provider lmstudio -m gpt-oss-20b -C /Users/doctor-violet/projects/exegesis`
- use the Python scripts above as the authoritative status sources
- when the controller itself is local `gpt-oss-20b`, prefer showing the full script outputs first and then summarize them; do not rely on memory or prior chat context for status

Then summarize:
- local remote monitor process running/stopped state, PID, and whether phone/VPN status access should be available
- daemon running/stopped state from `daemon_ctl.py status`
- filesystem truth per lane (`status.py`)
- daemon state, reviewer/integrator queues, `active_blocker`, and latest lane discussion (`daemon_monitor.py`)
- manual feature-lane Codex activity from process list / feature runner logs
- the freshest packet-router and daemon-log evidence, but only after labeling whether it agrees with queue truth
- whether the pipeline is actively progressing, idle, or blocked
- whether any stale fixer/log noise should be ignored because the queue is clean

Reading order:
1. Start with `status_report.sh`; within it, treat `remote_monitor_ctl.py status` as only a local process-health precheck.
2. Use `daemon_monitor.py` to read `bottleneck`, `active_blocker`, heartbeat, and live lane discussion.
3. Only then read process list, feature-runner logs, packet-router logs, and daemon-log tail.
4. If logs conflict with queue truth, say so explicitly and prefer `status.py` for queue state.
5. If `scope-check` appears only in log tail, call it stale unless queue state points to a current scope-driven stop.
6. When reporting back to the user, include the whole status picture, not just a one-line summary.

Reference:
- `PIPELINE_RUNBOOK.md`
- `ROADMAP.md`
- `PRODUCT_VISION.md`
- `ARCHITECTURE.md`
