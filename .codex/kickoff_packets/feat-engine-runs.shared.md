# Shared Maintenance Packet: feat-engine-runs

- Branch: `codex/feat-engine-runs`
- Source commit(s): `1879a1d34103ea5dfb9c438fae17901ab4c3addd..6c0c026a1be5fd3b793e8777e06fdc62f846ae1a`
- Scope: local control-plane metadata repair for stale handoff evidence.
- Reason: cloud metadata repair jobs cannot reliably write `.codex/**` under workspace-write sandboxing.
