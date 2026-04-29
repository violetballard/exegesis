# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review target: branch tip `codex/feat-commands`, including this fixer commit.
- Review basis: full branch-tip diff from `f8d860ed9f6299f0169c4f21321ac5f37c949fd3..HEAD`.
- Files in target: `THREAD.md`, `THREAD_PACKET.md`, `src/qual/cli.py`, `src/qual/commands/__init__.py`, `src/qual/commands/catalog.py`, `tests/unit/test_commands_catalog.py`.
- Parser-surface fix: `command_cli_contract()` validates against the actual argparse subparser choices from `src/qual/cli.py`.
- Demo-path mapping: task-by-task details in `THREAD_PACKET.md` explicitly use `retrieve relevant material`, `gather context`, `apply/reject patch`, and `save/continue`.
- Final readiness: this branch tip makes `retrieve relevant material` more real because live CLI command parsing and catalog metadata can no longer silently drift.
- Lane-owned files: `src/qual/commands/**`.
- Shared-by-approval files: `tests/unit/test_commands_catalog.py`; `src/qual/cli.py`.
- Integrator-locked files touched: `src/qual/cli.py` only.
- Fixer prompt satisfied: `20260429T152044Z`; canonical packet details live in `THREAD_PACKET.md`.
