# Thread Packet Pointer

This file exists for compatibility with older lane/fixer prompts.

Canonical handoff contract lives in `THREAD_PACKET.md`. This compatibility file
keeps a short reviewer-fix summary attached to an existing tracked path for
older lane/fixer prompts.

## Reviewer Fix Alignment

- Active implementation review target: `36a360a9464d2f08f55129bc70e1aafe4574721b`.
- Current metadata refresh baseline: `9aca0235cd53fbbbc0dacf9712010739ae9b4a87`.
- Canonical demo-path step advanced: `open project/document` and `preview and
  apply or reject a patch` via the CLI-first operator surface;
  `command_cli_contract()` now rejects parser/catalog drift before the
  accepted command entrypoints can silently change.
- Product Vision scope: this reviewer-fix refresh only supports the canonical
  engine contract requirement for CLI compatibility and does not claim workflow,
  persistence, or auditability changes.
- Final gate refresh: `make scope-check`, `./quality-format.sh --check`,
  `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and
  `make ci` all passed again at the current branch tip.
- Approval artifact for the non-owned test path: the reviewer packet supplied
  to this fixer pass explicitly records `Approved shared-test exception for
  tests/unit/test_commands_catalog.py`.
- Approval basis: `scripts/scope-check.sh` is the active branch enforcement in
  this worktree, and its `codex/feat-commands*` allowlist explicitly permits
  `tests/unit/test_commands_catalog.py` as the one approved shared test path.
  No other non-owned implementation path is claimed.
- Scope boundary: this metadata refresh stays scoped to the command-catalog
  slice plus that one approved shared-test exception.
