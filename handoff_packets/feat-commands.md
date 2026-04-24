# Handoff Packet: feat-commands

- Branch name: `codex/feat-commands`
- Scope completed: fail fast when the live CLI parser surface drifts from the declared command catalog, keep direct regression coverage on `_CLI_ENTRYPOINTS`, and document the narrowed demo-path step this slice advances.
- Canonical demo-path step advanced: `patch`
- Demo-path mapping: this change hardens the `patch` step's CLI-first contract by ensuring the operator-visible parser tokens for `diff-preview` stay backward-compatible and deterministic before A2UI or Console consumers build on the same command surface.
- Roadmap item(s) affected: `ROADMAP.md` Milestone 3 Product Readiness, narrowed to locking the CLI compatibility contract for the manual smoke surface; supports the existing exit criterion that the manual CLI smoke flow remains stable.
- Vision capability affected: `PRODUCT_VISION.md` operator-first control surface and A2UI protocol, specifically that CLI remains a first-class surface and artifacts/contracts stay consumable by CLI first.
- Routing/provider impact note: none; this slice does not touch model routing, provider configuration, or shared entrypoints.
- Proposed `README.md` patch text: none.

## Tasks Completed
1. Verified the command catalog contract against the live parser entrypoint projection in `src/qual/commands/catalog.py`.
2. Confirmed and retained direct `_CLI_ENTRYPOINTS` regression coverage for alias substitution, token removal, reorder drift, and extra accepted entrypoints.
3. Added an explicit happy-path assertion that the default CLI contract mirrors the live parser surface.
4. Ran focused command-catalog unit coverage for the live parser-surface drift cases.
5. Ran the required gate suite for this lane.

## Files Changed
- `tests/unit/test_commands_catalog.py`
- `handoff_packets/feat-commands.md`

## Commands Run With Results
- `python -m unittest tests.unit.test_commands_catalog.CommandCatalogTests.test_command_cli_contract_rejects_missing_canonical_token_when_alias_still_resolves tests.unit.test_commands_catalog.CommandCatalogTests.test_command_cli_contract_rejects_reordered_parser_surface tests.unit.test_commands_catalog.CommandCatalogTests.test_command_cli_contract_rejects_extra_alias_entrypoint_when_canonical_order_still_matches tests.unit.test_commands_catalog.CommandCatalogTests.test_command_cli_contract_rejects_alias_substitution_in_live_parser_entrypoints` -> passed
- `python -m unittest tests.unit.test_commands_catalog.CommandCatalogTests.test_command_cli_contract_matches_the_catalog_order tests.unit.test_commands_catalog.CommandCatalogTests.test_command_cli_contract_rejects_parser_surface_drift_when_diff_token_disappears tests.unit.test_commands_catalog.CommandCatalogTests.test_command_cli_contract_rejects_missing_canonical_token_when_alias_still_resolves tests.unit.test_commands_catalog.CommandCatalogTests.test_command_cli_contract_rejects_reordered_parser_surface tests.unit.test_commands_catalog.CommandCatalogTests.test_command_cli_contract_rejects_extra_alias_entrypoint_when_canonical_order_still_matches tests.unit.test_commands_catalog.CommandCatalogTests.test_command_cli_contract_rejects_alias_substitution_in_live_parser_entrypoints` -> passed
- `make scope-check` -> passed
- `./quality-format.sh --check` -> passed
- `./quality-lint.sh` -> passed
- `./quality-test.sh` -> passed (`211` tests)
- `./typecheck-test.sh` -> passed
- `make ci` -> passed

## Risks / Blockers
- None identified in lane-owned paths.
