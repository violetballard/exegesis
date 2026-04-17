# Thread Packet Pointer

This file exists for compatibility with older lane/fixer prompts.

Canonical handoff contract lives in `THREAD_PACKET.md`. This compatibility file
keeps a short reviewer-fix summary attached to an existing tracked path for
older lane/fixer prompts.

## Reviewer Fix Alignment

- Active implementation review target: `8333cbed4288faef14592230bd551cd26574e23a`.
- Exact canonical demo-path step advanced: the CLI-first route slice for
  `open project/document -> retrieve relevant material -> preview and apply or
  reject a patch -> export handoff`.
- Concrete Milestone 3 mapping: `command_cli_contract()` now rejects parser /
  catalog drift before the canonical command surface can silently change,
  keeping the CLI-first command contract deterministic for the engine-first MVP
  loop while Textual remains disabled.
- Product Vision scope: this reviewer-fix refresh only supports the canonical
  engine contract requirement for CLI compatibility and does not claim workflow,
  persistence, or auditability changes.
- Approval artifact for the non-owned test path: the reviewer packet supplied
  to this fixer pass explicitly records `Approved shared-test exception for
  tests/unit/test_commands_catalog.py`.
- Approval basis: `scripts/scope-check.sh` is the active branch enforcement in
  this worktree, and its `codex/feat-commands*` allowlist explicitly permits
  `tests/unit/test_commands_catalog.py` as the one approved shared test path.
  No other non-owned implementation path is claimed.
- Scope boundary: this metadata refresh stays scoped to the command-catalog
  slice plus that one approved shared-test exception.
