---
name: daemon.monitor
description: Show live daemon state, last run summary, lane queue counts, cooldowns, and daemon log tail.
---

Run from repo root:
- `python codex_packet_handoff/tools/daemon_monitor.py`

If daemon is not running, also run:
- `python codex_packet_handoff/tools/daemon_ctl.py status`
