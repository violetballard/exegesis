## Thread Handoff Packet

- Branch name: `codex/feat-a2ui-contract`
- Source commit(s): `bbbefceac6da4b0cf5c511c6c5e262b39377137c..030418b03a0f407cfd2bc89546a510c7bde7ead1`
- Review surface: actual implementation range, not metadata-only. The merge-base diff contains the A2UI contract/runtime/test files listed below.
- Scope goal: Stabilize the shared A2UI card/action/selection contract needed by the engine-first MVP loop while preserving the CLI fallback surface until Textual lanes are enabled.
- Scope completed: Added shared action selection materialization and validation helpers, exposed shared card/action contracts without terminal renderers, kept terminal/CLI materialization in `src/qual/ui/a2ui.py`, and covered fallback safety and selection behavior with focused tests.
- Roadmap item(s) affected (from `ROADMAP.md`): `Milestone 3: Real workflow loop`, specifically `feat-a2ui-contract`: shared card/action contracts and selection models; preserve CLI compatibility; move A2UI contracts into `shared` while keeping renderers outside `shared`.
- Vision capability affected (from `PRODUCT_VISION.md`): `Shared UI contract (A2UI)`, specifically client-agnostic cards/actions/selection types in shared, rendering adapters outside shared, unknown-card fallback, typed actions, validation, and patch apply/reject selection.
- Canonical demo-path step advanced: `preview and apply or reject a patch`.
- Shared/integrator-locked edits: `NO` for the corrected review surface. Current `main...HEAD` contains only lane-owned A2UI files; the prior `main..HEAD` control-plane drift for `THREAD_OWNERSHIP.md`, `packet_garden/tools/planner.py`, `scripts/scope-check.sh`, and `tests/unit/test_mvp_migration.py` has been aligned back to `main`.
- Routing/provider impact note: None. No provider routing, model routing, or core entrypoint behavior was touched.

## Files Changed

- `shared/src/exegesis_shared/contracts/__init__.py`
- `shared/src/exegesis_shared/contracts/actions.py`
- `shared/src/exegesis_shared/contracts/cards.py`
- `src/qual/ui/a2ui.py`
- `src/qual/ui/test_a2ui_fallback_safety.py`
- `tests/unit/test_a2ui_contract.py`

## Tasks Completed

1. Added versioned, one-based A2UI action selection materialization for CLI-consumable apply/reject choices.
2. Added canonical action ordering, identity, deduplication, validation, and selection resolution helpers in the shared contract layer.
3. Preserved the renderer boundary by exporting shared contracts from `shared` while keeping terminal rendering and terminal-specific materialization in `src/qual/ui/a2ui.py`.
4. Hardened CLI fallback behavior for unsupported cards, unsupported actions, duplicate actions, malformed selections, and ambiguous duplicate action IDs.
5. Added tests proving patch apply/reject actions remain selectable through the fallback surface used before Textual is enabled.

## Commands Run With Results

- `make scope-check` -> failed: scope policy rejects reviewer-required `THREAD_PACKET.md` edits on `codex/feat-a2ui-contract`
- `./quality-format.sh --check` -> passed
- `./quality-lint.sh` -> passed
- `./quality-test.sh` -> passed, 618 tests
- `./typecheck-test.sh` -> passed
- `make ci` -> failed: stops at the same `THREAD_PACKET.md` scope-check rejection

## Risks / Blockers

- Control-plane blocker: the reviewer required replacing `THREAD_PACKET.md`, but `make scope-check` treats `THREAD_PACKET.md` as a control-plane file and rejects it on feature branches.
- The corrected packet now describes the actual A2UI review surface and excludes feature-branch control-plane edits from the implementation surface.
