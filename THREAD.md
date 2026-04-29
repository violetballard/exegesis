# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review target: branch tip `codex/feat-commands`, including the latest fixer commit.
- Review basis: full branch-tip diff from `f8d860ed9f6299f0169c4f21321ac5f37c949fd3..HEAD`.
- Files in target: `THREAD.md`, `THREAD_PACKET.md`, `src/qual/cli.py`, `src/qual/commands/__init__.py`, `src/qual/commands/catalog.py`, `tests/unit/test_commands_catalog.py`.
- Parser-surface fix: `command_cli_contract()` validates against the actual argparse subparser choices from `src/qual/cli.py`.
- Demo-path mapping: task-by-task details in `THREAD_PACKET.md` identify the command surfaces for `open project/document`, `retrieve relevant material`, `gather context`, `preview/apply/reject patch`, and `persist session state`.
- Concrete blocker removed: live CLI command parsing and catalog metadata can no longer silently drift, so the canonical retrieval command surface is discoverable and parseable from the same contract.
- Lane-owned files: `src/qual/commands/**`.
- Shared-by-approval files: `tests/unit/test_commands_catalog.py`; `src/qual/cli.py`.
- Integrator-locked files touched: `src/qual/cli.py` only.
- Fixer prompts satisfied: `20260429T152044Z`, `20260429T152842Z`, `20260429T154016Z`, `20260429T154607Z`, `20260429T155155Z`; canonical packet details live in `THREAD_PACKET.md`.
