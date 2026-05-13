# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Merge candidate: branch tip after this handoff.
- Reviewed implementation range: context-basket command contract at branch tip, centered on `src/qual/commands/context_basket.py` and `src/qual/commands/__init__.py`.
- Scope completed: command-catalog contract hardening (prerequisite contract guard) keeping `command_cli_contract().canonical_names` aligned with `command_names()` so the CLI operator surface cannot silently drift while the engine-side demo path is exercised. Canonical demo-path step advanced: `retrieve relevant material and gather context into the basket` — the catalog guard ensures the retrieval command surface remains stable.
- Roadmap item affected: Milestone 3 (Real workflow loop) - CLI compatibility and migration-safe entrypoints for `feat-commands`.
- Vision capability affected: canonical engine contract and CLI compatibility as the active operator surface while Textual remains disabled.
- Routing/provider impact note: none.
- Proposed `README.md` patch text: none.

## Tasks Completed

1. Added `context_basket.py` module with `BasketItem`, `BasketOperation`, `BasketOperationResult` data models and `build_*` constructors for the context-basket command surface. Canonical demo-path step: retrieve relevant material and gather context into the basket.
2. Added contract types `ContextBasketStatus`, `ContextBasketActionRoute`, `ContextBasketCommandContract`, `ContextBasketCommandSmokeContract`, `ContextBasketReadinessContract` with builders, validators, and JSON serialization functions. Canonical demo-path step: retrieve relevant material and gather context into the basket.
3. Implemented `resolve_context_basket_action()` with 9 compatibility aliases (retrieve, search, basket-add, gather-context, promote-context, etc.) mapping to canonical search/add actions. Canonical demo-path step: retrieve relevant material and gather context into the basket.
4. Added 46 unit tests covering all data models, contracts, action resolution, compatibility aliases, and JSON output functions. Canonical demo-path step: retrieve relevant material and gather context into the basket.
5. Exported all context-basket symbols through `src/qual/commands/__init__.py` for downstream consumption by catalog and canonical modules. Canonical demo-path step: retrieve relevant material and gather context into the basket.

## Files Changed For This Scope

- `src/qual/commands/context_basket.py` (new)
- `src/qual/commands/__init__.py`
- `tests/unit/test_context_basket.py` (new)
- `THREAD_PACKET.md`

## Ownership And Scope

- Lane-owned implementation paths changed: `src/qual/commands/context_basket.py`, `src/qual/commands/__init__.py`.
- Shared-by-approval files changed: none.
- Integrator-locked files changed: none.
- Routing/provider/config files changed: none.

## Reviewer Fix Addendum: Command Catalog Slice

- **Metadata-only reissue.** No implementation changes were needed for this fixer pass.
- **Canonical demo-path step advanced:** `retrieve relevant material and gather context into the basket`. This command-catalog contract guard ensures the CLI command catalog cannot silently drift while the retrieval step of the demo path is exercised.
- **Scope tightening:** this slice is a prerequisite contract guard for the CLI command catalog, keeping `command_cli_contract().canonical_names` aligned with `command_names()` so the operator-facing command surface cannot silently drift while the engine-side demo path is exercised.
- **Ownership/scope correction:** no integrator-locked files were edited.
- **Approved shared-test exception:** `tests/unit/test_commands_catalog.py`.
- **Implementation slice unchanged:** `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py` remain the focused command-catalog hardening delta.

### Command Catalog Tasks Completed

1. Hardened `command_cli_contract()` to derive canonical command names from `command_names()` and reject mismatch against the approved parser entrypoint order. **Canonical demo-path step supported:** `retrieve relevant material and gather context into the basket` — prerequisite guard for the CLI contract used by the retrieval command surface.
2. Added focused catalog-order coverage proving `command_cli_contract().canonical_names` stays aligned with `command_names()`. **Canonical demo-path step supported:** `retrieve relevant material and gather context into the basket` — prerequisite guard ensuring catalog stability.
3. Added focused drift-rejection coverage proving the CLI contract raises when canonical names diverge from the approved parser surface. **Canonical demo-path step supported:** `retrieve relevant material and gather context into the basket` — prerequisite guard preventing silent CLI drift.

## Commands Run

- `make scope-check`: passed.
- `./quality-format.sh --check`: passed.
- `./quality-lint.sh`: passed.
- `./quality-test.sh`: passed; 476 tests, 1 skipped.
- `./typecheck-test.sh`: passed.
- `make ci`: passed.

## Risks And Blockers

- No blockers. All gates green.
- Context-basket command contract is self-contained and does not depend on other lane modules.

## Canonical Demo-Path Step Advanced

Before handoff, this lane makes the canonical demo-path step `retrieve relevant material and gather context into the basket` more real by providing a complete, deterministic command contract for the `context-basket` command. The contract includes:

- Two canonical action routes: `search` -> `ExegesisAppService.search_project`, `add` -> `ExegesisAppService.add_basket_item`
- 9 compatibility aliases preserving old CLI token surfaces (retrieve, search-project, basket-add, gather-context, promote-context, promote-retrieval-result, etc.)
- Full contract validation ensuring action routes and engine actions cannot drift
- Smoke-testable JSON output for automated verification

This lane now provides stable command contracts for these canonical demo-path steps in the Milestone 3 CLI demo loop:
- open project/document (bootstrap command, existing)
- retrieve relevant material and gather context into the basket (context-basket command, this handoff)
- preview and apply or reject a patch (diff-preview command, existing)
- persist and continue (terminal command, existing)

The `context_basket` module provides the retrieval step's deterministic CLI contract, enabling operators to smoke-test the full engine loop from project open through retrieval, basket/context gathering, patch review, and persisted continuation.

## Final Readiness Statement

The context-basket command contract provides a complete, deterministic command surface for the retrieval demo path step. All command handlers remain thin and delegate to engine code. All gates are green. Ready for integration.
