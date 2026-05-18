---
name: daemon.resume_check
description: "Safely resume automation after a pause by starting daemon, verifying status, and printing the full pipeline dashboard."
---

Run from repo root:
- `python codex_packet_handoff/tools/launchd_ctl.py start all`
- `python codex_packet_handoff/tools/launchd_ctl.py status all`
- `python codex_packet_handoff/tools/daemon_resume_check.py`
- `python codex_packet_handoff/tools/daemon_ctl.py status`
- `python codex_packet_handoff/tools/remote_monitor_ctl.py status`
- `python codex_packet_handoff/tools/status.py`
- `python codex_packet_handoff/tools/daemon_monitor.py`
- `ps -axo pid,etime,command | rg "codex exec|codex_packet_handoff/tools/agents_coordinator.py" || true`
- `for f in $(ls -1t .codex/feature_runner/logs/*.log 2>/dev/null | head -n 3); do echo "FILE:$f"; tail -n 20 "$f"; done`
- `for f in $(ls -1t .codex/packet_router/logs/*.log 2>/dev/null | head -n 3); do echo "FILE:$f"; tail -n 30 "$f"; done`
- `tail -n 60 .codex/packet_coordinator/daemon.log 2>/dev/null || true`

Access path selection:
- If local scripts exist, use the direct resume/status workflow above.
- If this session is remote over VPN and local scripts are unavailable, use `python codex_packet_handoff/tools/remote_monitor_client.py start`, then `python codex_packet_handoff/tools/remote_monitor_client.py kick` if a fresh reconcile is needed, followed by `... status` or `... full`.
- Remote start and kick are the only remote equivalents; they do not run arbitrary local scripts.
- Local `remote_monitor_ctl.py status` only checks the phone/VPN monitor process. Launchd owns local daemon, monitor, and shell startup.

CLI-first note:
- assume the operator launched Codex CLI with `codex --oss --local-provider lmstudio -m gpt-oss-20b -C /Users/doctor-violet/projects/exegesis`
- use only the Python scripts above for resume/status control

This performs:
1. `launchd_ctl.py start all`
2. `launchd_ctl.py status all` (must show daemon, monitor, and shell loaded/running)
3. `daemon_ctl.py status` (must show running)
4. `remote_monitor_ctl.py status` (must show running for phone/VPN status access)
5. `daemon_monitor.py`
6. `status.py`

After running, report:
- whether the remote monitor is running, including PID and log path
- whether daemon resumed successfully
- the full queue truth from `status.py`
- whether the queue is idle or has work
- whether reviewer/integrator lanes are attached
- whether any manual feature sessions are also running
- the next blocking condition, if any
- the most relevant live-log evidence, clearly separated from queue truth

Reference:
- `PIPELINE_RUNBOOK.md`

Restart note:
- After relocation to `/Users/doctor-violet/projects/exegesis`, launchd owns daemon, remote monitor, and shell startup. Use `launchd_ctl.py start/status all` after a reboot if any service does not come back cleanly.
