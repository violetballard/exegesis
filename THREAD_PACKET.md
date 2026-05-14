# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Merge candidate: branch tip after this handoff.
- Reviewed implementation commit: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` (`feat(commands): lock CLI contract to command catalog`).
- Scope completed: command-catalog contract hardening that keeps `command_cli_contract().canonical_names` aligned with `command_names()` and rejects drift from the approved parser entrypoint order.
- Canonical demo-path steps advanced: stable CLI command contract for `open project/document`, `retrieve relevant material and gather context into the basket`, and `preview and apply or reject a patch` command routing while Textual remains disabled.
- Deterministic CLI contract mapping: the active operator command surface stays stable while Textual remains disabled, so the engine-first MVP loop can reliably reach open-document, retrieval/context, and patch-review routing through approved parser entrypoints.
- Roadmap item affected: Milestone 3 (Real workflow loop) - CLI compatibility and migration-safe entrypoints for `open project/document`, `retrieve relevant material and gather context into the basket`, and `preview and apply or reject a patch`, aligned with `ROADMAP.md:51-75`.
- Vision capability affected: canonical engine contract and CLI compatibility for open-document, retrieval/context, and patch-review command routing while Textual remains disabled, aligned with `PRODUCT_VISION.md:35-55`.
- Active lane order alignment: `feat-commands` provides the stable CLI control surface for the engine-first MVP loop, aligned with `AGENTS.md:195-205`.
- Routing/provider impact note: none.
- Proposed `README.md` patch text: none.

## Tasks Completed

1. Hardened `command_cli_contract()` so canonical command names are derived from `command_names()` and validated against the approved parser entrypoint order. Canonical demo-path steps supported: `open project/document`, `retrieve relevant material and gather context into the basket`, and `preview and apply or reject a patch`.
2. Added focused catalog-order coverage proving `command_cli_contract().canonical_names` remains aligned with `command_names()`. Canonical demo-path steps supported: `open project/document`, `retrieve relevant material and gather context into the basket`, and `preview and apply or reject a patch`.
3. Added drift-rejection coverage proving the CLI contract raises when canonical names diverge from the approved parser surface. Canonical demo-path steps supported: `open project/document`, `retrieve relevant material and gather context into the basket`, and `preview and apply or reject a patch`.

## Files Changed For This Scope

- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`
- `THREAD_PACKET.md`

## Ownership And Scope

- Lane-owned implementation paths changed: `src/qual/commands/catalog.py`.
- Shared-by-approval files changed: `tests/unit/test_commands_catalog.py`.
- Approved shared-test exception: `tests/unit/test_commands_catalog.py` is shared-by-approval under `THREAD_OWNERSHIP.md:12-16`; this slice keeps the edit limited to focused command-catalog coverage for the reviewed implementation.
- Integrator-locked files changed: none.
- Routing/provider/config files changed: none.
- Metadata-only fixer update: `THREAD_PACKET.md` was regenerated to describe the reviewed command-catalog implementation only.

## Commands Run

- `make scope-check`: passed.
- `./quality-format.sh --check`: passed.
- `./quality-lint.sh`: passed.
- `./quality-test.sh`: passed; 476 tests, 1 skipped.
- `./typecheck-test.sh`: passed.
- `make ci`: passed.

## Risks And Blockers

- No blockers. All gates are green.
- The implementation intentionally narrows to the command catalog; it does not change command handler behavior, routing, provider selection, or core engine entrypoints.
- The shared test edit is covered by the explicit shared-test approval note above.

## Canonical Demo-Path Step Advanced

This lane makes the canonical demo-path steps `open project/document`, `retrieve relevant material and gather context into the basket`, and `preview and apply or reject a patch` more real by preserving a deterministic CLI command catalog for command routing while Textual remains disabled. The concrete blocker removed is silent drift between the operator-facing command catalog and the approved parser entrypoints used to exercise open-document, retrieval/context, and patch-review commands in the engine-first MVP loop.

This supports the Milestone 3 CLI demo loop while Textual remains disabled:

- open project/document (existing command surface)
- retrieve relevant material and gather context into the basket (catalog stability for retrieval commands)
- preview and apply or reject a patch (existing command surface)
- persist and continue (existing command surface)

## Final Readiness Statement

The reviewed command-catalog slice at `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` keeps the CLI contract aligned with the command catalog and rejects drift from approved parser entrypoints for `open project/document`, `retrieve relevant material and gather context into the basket`, and `preview and apply or reject a patch` command routing while Textual remains disabled. The packet now describes only this command-catalog implementation, includes the shared-test approval for `tests/unit/test_commands_catalog.py`, and preserves the roadmap/product-vision mapping required for `feat-commands`. All gates are green. Ready for integration.
