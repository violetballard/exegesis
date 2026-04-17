# Thread Packet Pointer

This file exists for compatibility with older lane/fixer prompts.

Canonical handoff contract lives in `THREAD_PACKET.md`. This compatibility file
keeps a short reviewer-fix summary attached to an existing tracked path for
older lane/fixer prompts.

## Reviewer Fix Alignment

- Active implementation review target: `36a360a9464d2f08f55129bc70e1aafe4574721b`.
- AGENTS.md canonical demo-path mapping for this slice: the CLI operator
  surface that keeps the canonical engine loop callable and smoke-testable
  while Textual remains disabled.
- Concrete blocker removed: `command_cli_contract()` now rejects parser /
  catalog drift before the canonical command surface can silently change,
  preventing the CLI operator surface from becoming nondeterministic during the
  current Milestone 3 engine-first loop.
- Why this is in-scope now: the CLI is still the active operator surface, so a
  deterministic parser contract is a direct stability requirement for the
  current engine-first loop rather than follow-on UX work.
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
