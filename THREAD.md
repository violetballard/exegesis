# Thread Packet Pointer

This file exists for compatibility with older lane/fixer prompts.

Canonical handoff contract lives in `THREAD_PACKET.md`. This compatibility file
keeps a short reviewer-fix summary attached to an existing tracked path for
older lane/fixer prompts.

## Reviewer Fix Alignment

- Active implementation review target: `36a360a9464d2f08f55129bc70e1aafe4574721b`.
- Current metadata refresh baseline: `b533eba949d16746829d42f655a0b1e085f59d30`
  before this final verified packet refresh commit.
- This refresh explicitly satisfies the reviewer's REQUIRED FIXES by naming the
  canonical demo-path steps advanced and keeping the scope tied to the current
  Milestone 3 engine-first CLI loop only.
- This work explicitly advances the canonical demo path by making the CLI-first
  `project-open`, `retrieval`, `patch-review`, and `export-handoff` steps more
  real and smoke-testable.
- Runtime fix verification: this final fixer pass confirmed that branch tip
  `b533eba949d16746829d42f655a0b1e085f59d30` already includes the reviewer-
  required parser-surface implementation through runtime commit
  `36a360a9464d2f08f55129bc70e1aafe4574721b`.
- Canonical demo-path steps advanced: `project-open`, `retrieval`,
  `patch-review`, and `export-handoff` via the CLI-first operator surface;
  `command_cli_contract()` now rejects parser/catalog drift before those
  accepted CLI entrypoints can silently change.
- Explicit AGENTS.md handoff field: this compatibility pointer records exactly
  which canonical demo-path steps the slice advances before handoff.
- AGENTS.md canonical demo-path statement: this work makes the CLI-first
  `project-open`, `retrieval`, `patch-review`, and `export-handoff` steps more
  real by locking the accepted parser surface to the command catalog that
  defines the current MVP contract.
- Concrete blocker removed: parser/catalog drift could previously reorder,
  replace, or remove accepted CLI entrypoints across the current MVP command
  surface without failing the contract, which would destabilize the engine-side
  demo loop.
- Product Vision scope: this reviewer-fix refresh only supports the canonical
  engine contract requirement for CLI compatibility and does not claim workflow,
  persistence, or auditability changes.
- Merge risk: `LOW` because this remains a narrow lane-owned command-catalog
  change plus one approved shared test, not a broader shared/runtime change,
  and there are no routing/provider changes.
- Final gate refresh in this fixer pass: `make scope-check`, `./quality-format.sh --check`,
  `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and
  `make ci` all passed again in this feature-fixer pass before the final
  reviewer-fix commit.
- Fixer verification: this pass re-checked that the reviewer-required mapping
  stays narrowed to the CLI-first `project-open`, `retrieval`,
  `patch-review`, and `export-handoff` steps and that the packet scope remains
  command-catalog contract hardening only.
- Approval artifact for the non-owned test path: the reviewer packet supplied
  to this fixer pass explicitly records `Approved shared-test exception for
  tests/unit/test_commands_catalog.py`.
- Approval basis: `scripts/scope-check.sh` is the active branch enforcement in
  this worktree, and its `codex/feat-commands*` allowlist explicitly permits
  `tests/unit/test_commands_catalog.py` as the one approved shared test path.
  No other non-owned implementation path is claimed.
- Scope boundary: this metadata refresh stays scoped to the command-catalog
  slice for the CLI-first MVP path plus that one approved shared-test
  exception.
- Scope limit: this is CLI-first MVP contract hardening only, not broader
  command-surface expansion or handler work.
