# Handoff Packet: feat-commands

- Branch name: `codex/feat-commands`
- Scope completed: fail fast when the live CLI parser surface drifts from the declared command catalog, keep direct regression coverage on `_CLI_ENTRYPOINTS`, and document the single canonical demo-path step this slice makes more real.
- Canonical demo-path step advanced: `project-open`
- Demo-path mapping: this change hardens the `project-open` bootstrap entrypoint by keeping the operator-visible parser surface catalog-locked at the start of the current CLI smoke route, so alias-only drift, dropped canonical tokens, reordered accepted tokens, or extra parser entrypoints fail closed before the operator enters retrieval, patch review, persist, and export handoff.
- Roadmap item(s) affected: `ROADMAP.md` Milestone 1 `Bootstrap Flow Stabilization`, narrowed to `Command and diff-preview behavior hardening` for the public CLI parser surface; this directly supports the active exit criterion that the manual CLI smoke flow remains stable.
- Vision capability affected: `PRODUCT_VISION.md` capability 4 `Operator-first control surface`, specifically that CLI remains a first-class control surface with deterministic, auditable command contracts.
- Routing/provider impact note: none; this slice does not touch model routing, provider configuration, or shared entrypoints.
- Proposed `README.md` patch text: none.

## Tasks Completed
1. Verified the command catalog contract against the live parser entrypoint projection in `src/qual/commands/catalog.py`.
2. Confirmed direct `_CLI_ENTRYPOINTS` regression coverage for alias substitution, canonical-token removal, parser-surface reordering, and extra accepted entrypoints, including the `diff-preview` removed / `diff` retained case.
3. Verified the stricter parser-surface drift tests pass against the checked-out branch state.
4. Regenerated this handoff packet with the explicit `project-open` demo-path mapping and narrowed roadmap/vision alignment required for re-review.
5. Ran the required gate suite for this lane.

## Files Changed
- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`
- `handoff_packets/feat-commands.md`

## Commands Run With Results
- `python -m unittest tests.unit.test_commands_catalog.CommandCatalogTests.test_command_cli_contract_rejects_parser_surface_drift_when_diff_token_disappears` -> passed
- `python -m unittest tests.unit.test_commands_catalog` -> passed
- `make scope-check` -> passed
- `./quality-format.sh --check` -> passed
- `./quality-lint.sh` -> passed
- `./quality-test.sh` -> passed (`211` tests)
- `./typecheck-test.sh` -> passed
- `make ci` -> passed

## Risks / Blockers
- The default parser surface now depends on `_CLI_ENTRYPOINTS` staying updated alongside command-catalog changes; that fail-fast coupling is intentional.
