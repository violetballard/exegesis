# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Merge candidate: branch tip after this handoff.
- Reviewed implementation commit: branch tip after this handoff (`feat(commands): complete CLI handoff replay`).
- Scope completed: reviewer-facing CLI handoff replay now defaults to the canonical MVP smoke command argv sequence and validates the exact demo action argv sequence, so command, action, transcript, route, resume, and checkpoint payloads agree.
- Canonical demo-path steps advanced: `open project/document`, `retrieve relevant material and gather context into the basket`, `preview and apply or reject a patch`, and `persist and continue`.
- Deterministic CLI contract mapping: the active operator command surface now exposes a self-contained handoff replay proving both command-level smoke coverage and exact action coverage while Textual remains disabled.
- Roadmap item affected: Milestone 3 (Real workflow loop) - CLI compatibility and migration-safe entrypoints for open, retrieve/basket, patch review, and persist/continue, aligned with `ROADMAP.md:51-75`.
- Vision capability affected: canonical engine contract and CLI compatibility for the engine-first command surface while Textual remains disabled, aligned with `PRODUCT_VISION.md:35-55`.
- Active lane order alignment: `feat-commands` provides the stable CLI control surface for the engine-first MVP loop, aligned with `AGENTS.md:195-205`.
- Routing/provider impact note: none.
- Proposed `README.md` patch text: none.

## Tasks Completed

1. Made `build_mvp_demo_cli_handoff_payload()` default to the canonical MVP command smoke argv sequence when no observed argv list is supplied. Canonical demo-path steps supported: `open project/document`, `retrieve relevant material and gather context into the basket`, `preview and apply or reject a patch`, and `persist and continue`.
2. Added handoff-only exact-action argv replay derived from the smoke matrix, so nested checkpoint, completion, transcript, route, resume, and replay payloads validate exact engine actions instead of reporting false missing action coverage. Canonical demo-path steps supported: `open project/document`, `retrieve relevant material and gather context into the basket`, `preview and apply or reject a patch`, and `persist and continue`.
3. Tightened the catalog handoff packet validator so every task completed entry names the canonical demo-path step it advances. Canonical demo-path steps supported: `open project/document`, `retrieve relevant material and gather context into the basket`, `preview and apply or reject a patch`, and `persist and continue`.

## Files Changed For This Scope

- `src/qual/commands/__init__.py`
- `src/qual/commands/catalog.py`
- `THREAD_PACKET.md`

## Ownership And Scope

- Lane-owned implementation paths changed: `src/qual/commands/__init__.py`, `src/qual/commands/catalog.py`.
- Shared-by-approval files changed: none.
- Integrator-locked files changed: none.
- Routing/provider/config files changed: none.
- Handoff metadata updated: `THREAD_PACKET.md` describes this branch-tip implementation and gate results.

## Commands Run

- `python -m pytest tests/unit/test_commands_catalog.py tests/unit/test_context_basket.py tests/unit/test_diff_preview.py`: passed; 134 tests.
- `python -m compileall -q src/qual/commands`: passed.
- handoff payload assertion script: passed; default handoff replay reports ready/complete nested command and exact-action coverage.
- `make scope-check`: passed.
- `./quality-format.sh --check`: passed.
- `./quality-lint.sh`: passed.
- `./quality-test.sh`: passed; 476 tests, 1 skipped.
- `./typecheck-test.sh`: passed.
- `make ci`: passed.

## Risks And Blockers

- No blockers. All gates are green.
- The implementation intentionally narrows to command handoff/readiness payloads; it does not change command handler behavior, routing, provider selection, or core engine entrypoints.

## Canonical Demo-Path Step Advanced

This lane makes the canonical demo-path steps `open project/document`, `retrieve relevant material and gather context into the basket`, `preview and apply or reject a patch`, and `persist and continue` more real by making the reviewer-facing CLI handoff replay self-contained and internally complete. The concrete blocker removed is false missing coverage in the default handoff payload when no observed argv list is supplied.

This supports the Milestone 3 CLI demo loop while Textual remains disabled:

- open project/document (exact bootstrap action replay)
- retrieve relevant material and gather context into the basket (context-basket search/add action replay)
- preview and apply or reject a patch (diff-preview revise/apply/reject action replay)
- persist and continue (terminal save-document action replay)

## Final Readiness Statement

The branch-tip command slice makes `build_mvp_demo_cli_handoff_payload()` emit a deterministic, complete replay for command smoke coverage and exact demo action coverage. It preserves thin command handlers, avoids routing/provider/core entrypoint changes, and keeps the roadmap/product-vision mapping required for `feat-commands`. All gates are green. Ready for integration.
