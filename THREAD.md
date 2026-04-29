# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review target: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
- Review basis: `git show --stat --oneline --name-status f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
- Scope: deterministic MVP command catalog coverage for parser/catalog compatibility.
- Demo-path mapping: task-by-task details in `THREAD_PACKET.md` explicitly use the canonical steps `retrieve material`, `gather/promote context`, `preview/apply/reject patch`, and `persist/save`.
- Final readiness: this slice makes `retrieve material` more real because retrieval command parsing and catalog metadata can no longer silently drift.
- Lane-owned file in reviewed slice: `src/qual/commands/catalog.py`.
- Shared-by-approval test exception in reviewed slice: `tests/unit/test_commands_catalog.py`.
- Integrator-locked edits in reviewed slice: none.
- Current fixer slice: `20260429T151533Z`; corrects handoff metadata only.
- Fixer prompt satisfied: `20260429T151533Z`; canonical packet details live in `THREAD_PACKET.md`.
