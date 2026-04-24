# Handoff Packet: feat-commands

- Branch name: `codex/feat-commands`
- Scope completed: fail fast when the live CLI parser surface drifts from the declared command catalog, cover real `_CLI_ENTRYPOINTS` drift cases directly, and keep the handoff scoped to the single canonical demo-path step advanced by this slice.
- Canonical demo-path step advanced: `patch-review` (`diff-preview` on the public CLI surface)
- Demo-path mapping: this slice hardens the `patch-review` review entrypoint inside the current CLI smoke route `project-open -> retrieval -> patch-review -> apply-patch/reject-patch -> persist -> export-handoff` by keeping the operator-visible `diff-preview` parser surface catalog-locked, so alias-only drift, missing canonical tokens, reordered accepted tokens, or extra parser entrypoints fail closed before the operator reaches the review step.
- Roadmap item(s) affected: `ROADMAP.md` Milestone 3 `Product Readiness`, narrowed to locking a user-facing CLI contract intentionally for the `patch-review` parser surface.
- Vision capability affected: `PRODUCT_VISION.md` capability 4 `Operator-first control surface`, specifically that CLI remains a first-class control surface with deterministic, auditable command contracts.
- Routing/provider impact note: none; this slice does not touch model routing, provider configuration, or shared app entrypoints.
- Proposed `README.md` patch text: none.

## Tasks Completed
1. Tightened `command_cli_contract()` in [src/qual/commands/catalog.py](/Users/doctor-violet/.codex/worktrees/5494/qual/src/qual/commands/catalog.py:525) so the default contract validates the actual parser token surface, not only deduplicated canonical command names.
2. Re-exported the branch helper APIs already added in [src/qual/commands/__init__.py](/Users/doctor-violet/.codex/worktrees/5494/qual/src/qual/commands/__init__.py:147) so the package surface stays aligned with the command catalog additions on this branch.
3. Reworked shared regression coverage in [tests/unit/test_commands_catalog.py](/Users/doctor-violet/.codex/worktrees/5494/qual/tests/unit/test_commands_catalog.py:468) to patch `_CLI_ENTRYPOINTS` into drifted-but-still-resolvable shapes, including the exact `diff-preview` removed while `diff` still resolves to `diff-preview` case and the cache-warm helper path.
4. Regenerated this handoff packet so the reviewer-requested `patch-review` mapping, narrowed roadmap/vision alignment, shared-test approval source, and fresh gate rerun are explicit.

## Files Changed
- `src/qual/commands/__init__.py`
- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`
- `handoff_packets/feat-commands.md`

## Commands Run With Results
- `python -m unittest tests.unit.test_commands_catalog.CommandCatalogTests.test_command_cli_contract_matches_the_catalog_order` -> passed
- `python -m unittest tests.unit.test_commands_catalog.CommandCatalogTests.test_command_cli_contract_rejects_parser_surface_drift_when_diff_token_disappears` -> passed
- `python -m unittest tests.unit.test_commands_catalog.CommandCatalogTests.test_command_cli_tokens_rejects_parser_surface_drift_after_cache_warm` -> passed
- `make scope-check` -> passed
- `./quality-format.sh --check` -> passed
- `./quality-lint.sh` -> passed
- `./quality-test.sh` -> passed (`214` tests plus smoke)
- `./typecheck-test.sh` -> passed
- `make ci` -> passed
- Verification refresh note: rerun on branch tip `2026-04-23` local time / `2026-04-24` UTC before this packet refresh commit.

## Risks / Blockers
- Risks:
  - future command-surface changes must update `_CLI_ENTRYPOINTS` alongside the declared catalog projection and regression coverage, or the contract will fail fast by design
- Blockers:
  - none

## Shared-Test Approval Note
- Shared-by-approval edits: `yes`
- Shared path: `tests/unit/test_commands_catalog.py`
- Approval source: `THREAD_OWNERSHIP.md` marks non-owned paths approval-only, and `scripts/scope-check.sh` includes the `codex/feat-commands*` shared-test allowlist covering this file
- Scope-check allowance used: `not required`
- Integrator-locked edits: `none`
