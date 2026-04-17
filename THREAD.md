# Thread Packet Pointer

This file exists for compatibility with older lane/fixer prompts.

Canonical handoff contract lives in `THREAD_PACKET.md`. This compatibility file
keeps a short reviewer-fix summary attached to an existing tracked path for
older lane/fixer prompts.

## Reviewer Fix Alignment

- Active implementation review target: `36a360a9464d2f08f55129bc70e1aafe4574721b`.
- Current metadata refresh baseline: `db752f9937b99170855f948f3079431253a96713`.
- Canonical demo-path step advanced: `open project/document` via the CLI-first
  operator surface; `command_cli_contract()` now rejects parser/catalog drift
  before the accepted bootstrap entrypoint can silently change.
- Concrete blocker removed: parser/catalog drift could previously reorder,
  replace, or remove accepted CLI entrypoints for the `bootstrap` MVP surface
  without failing the contract, which would destabilize the first step of the
  engine-side demo loop.
- Product Vision scope: this reviewer-fix refresh only supports the canonical
  engine contract requirement for CLI compatibility and does not claim workflow,
  persistence, or auditability changes.
- Merge risk: `LOW` because this remains a narrow command-catalog contract
  change in one owned file plus one approved shared test, with no
  routing/provider changes.
- Final gate refresh: `make scope-check`, `./quality-format.sh --check`,
  `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and
  `make ci` all passed again in this feature-fixer pass at branch tip
  `db752f9937b99170855f948f3079431253a96713`.
- Fixer verification: this pass re-checked that the reviewer-required mapping
  stays narrowed to the CLI-first `open project/document` step and that the
  packet scope remains command-catalog contract hardening only.
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
