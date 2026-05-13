---
name: daemon.stop
description: "Stop the event-driven coordinator daemon and clear stale pidfile."
---

Run from repo root:
- `python codex_packet_handoff/tools/daemon_ctl.py stop`

Access path selection:
- If this session is local to the development machine and `daemon_ctl.py` exists, stop with the direct local command above.
- If this session is remote over VPN and local scripts are unavailable, use `python codex_packet_handoff/tools/remote_monitor_client.py stop`.
- Remote stop uses the same daemon stop semantics as local stop, but no arbitrary remote commands are allowed.

Then verify:
- `python codex_packet_handoff/tools/daemon_ctl.py status`
- Remote verification fallback: `python codex_packet_handoff/tools/remote_monitor_client.py status`

CLI-first note:
- run this from a Codex CLI session launched with `codex --oss --local-provider lmstudio -m gpt-oss-20b -C /Users/doctor-violet/Library/CloudStorage/Box-Box/projects/qual`
