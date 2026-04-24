# Handoff Packet: feat-commands

- Branch name: `codex/feat-commands`
- Scope completed: tightened `command_cli_contract()` so it validates the full grouped CLI parser surface reconstructed from the contract lookup table, not just canonical command order, and added regression coverage for alias-level drift.
- Canonical demo-path mapping sentence: this slice makes `preview and apply or reject a patch` more real because the patch-review CLI surface for `diff-preview` now fails fast if the parser or contract surface drops or mutates the `diff` alias while the canonical command sequence still appears unchanged.

## Tasks Completed
1. Hardened `src/qual/commands/catalog.py` so `command_cli_contract()` reconstructs grouped entrypoints from `lookup_table` and verifies that full surface against both the catalog-defined and live parser projections.
2. Added a regression in `tests/unit/test_commands_catalog.py` proving `_validate_command_cli_contract()` raises when the `diff` alias disappears from the contract surface while `canonical_names` stays unchanged.
3. Refreshed the lane handoff metadata so the canonical demo-path step is stated explicitly as `preview and apply or reject a patch`.
4. Re-ran the required gates for the updated command-catalog slice.

## Files Changed
- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`
- `THREAD.md`
- `THREAD_PACKET.md`
- `handoff_packets/feat-commands.md`

## Commands Run With Results
- `python3 -m unittest tests.unit.test_commands_catalog.CommandCatalogTests.test_command_cli_contract_validation_rejects_alias_drift_with_stable_canonical_names` -> passed
- `python3 -m unittest tests.unit.test_commands_catalog.CommandCatalogTests -k command_cli_contract` -> passed
- `make scope-check` -> passed
- `./quality-format.sh --check` -> passed
- `./quality-lint.sh` -> passed
- `./quality-test.sh` -> passed
- `./typecheck-test.sh` -> passed
- `make ci` -> passed

## Risks / Blockers
- Risks: future command-surface edits still need to keep `_CLI_ENTRYPOINTS`, command specs, and shared contract tests aligned.
- Blockers: none.

## Roadmap Item(s) Affected
- `ROADMAP.md` Milestone 5 `A2UI Presentation Layer (In Progress)`
- `ROADMAP.md` exit criterion: `CLI can execute the MVP flow (vault -> context -> run -> patch -> export) against the same engine PolicyGate`
- `ROADMAP.md` active lane: `feat-commands`

## Vision Capability Affected
- `PRODUCT_VISION.md`: `CLI remains a first-class surface for development and reliability.`
- `PRODUCT_VISION.md`: `Artifacts must be consumable by CLI first, then Exegesis Console, then future Studio UI.`
- `PRODUCT_VISION.md`: `Current MVP emphasis is on Engine output contracts, FTS-backed retrieval, and A2UI cards/actions that can be rendered in CLI now and Exegesis Console next.`

## Routing / Provider Impact Note
- None. This change does not touch routing or provider configuration.

## Scope / Ownership Note
- Lane-owned implementation path: `src/qual/commands/catalog.py`
- Approved shared-by-approval exception: `tests/unit/test_commands_catalog.py`
- Integrator-locked edits: none
