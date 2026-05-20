## Thread Handoff Packet

- Branch name: `codex/feat-a2ui-contract`
- Source commit(s): `e0db5f3e^..481503db`
- Scope goal: Corrected handoff packet for the actual Milestone 3 A2UI contract implementation range. The reviewed range keeps A2UI renderer behavior out of `shared` while exposing shared card/action contracts and a CLI-consumable action selection model for the engine-first demo loop.
- Scope completed: The reviewed source range adds versioned A2UI card/action/selection contracts under `shared`, wires CLI fallback materialization through those contracts, preserves unknown-card fallback behavior, and proves deterministic apply/reject action slots for previewed patch cards.
- Roadmap item(s) affected (from `ROADMAP.md`): `Milestone 3: Real workflow loop`, specifically `feat-a2ui-contract`: shared card/action contracts and selection models, with CLI MVP compatibility while Textual remains disabled.
- Vision capability affected (from `PRODUCT_VISION.md`): `Shared UI contract (A2UI)`: shared cards/actions/selection types live in a client-agnostic shared layer, renderers remain outside `shared`, and CLI compatibility is preserved while Textual remains disabled.
- Shared/integrator-locked edits: `YES`
- Approval note: This packet declares the reviewed source range honestly because it includes shared contract files. No `.codex` kickoff packet or control-plane metadata file is claimed as part of this reviewed range.
- Ownership note: The reviewed range touches `shared/src/exegesis_shared/contracts/**`, `src/qual/ui/a2ui.py`, and A2UI tests only; it does not add Textual implementation or renderer behavior to `shared`.

## Reviewed Source-Range Evidence

The reviewed implementation range is `e0db5f3e^..481503db`.

- Tasks completed:
  1. Added versioned shared A2UI action selection contracts with deterministic one-based action slots.
  2. Added shared card/action materialization helpers for supported and unknown cards without exporting terminal renderer behavior from `shared`.
  3. Wired CLI fallback materialization through the shared selection contract so terminal users can choose apply/reject actions while Textual remains disabled.
  4. Canonicalized patch action ordering so previewed proposed edits expose stable `apply_patch` and `reject_patch` slots.
  5. Added unit coverage proving shared exports, CLI fallback selection, unknown-card fallback, policy-gated actions, and deterministic terminal action ordering.

## Files Changed

- `shared/src/exegesis_shared/contracts/__init__.py`
- `shared/src/exegesis_shared/contracts/actions.py`
- `shared/src/exegesis_shared/contracts/cards.py`
- `src/qual/ui/a2ui.py`
- `src/qual/ui/test_a2ui_fallback_safety.py`
- `tests/unit/test_a2ui_contract.py`

## A2UI-Specific Gate Evidence

- CLI rendering fallback: `src/qual/ui/a2ui.py` materializes terminal patch previews through the shared selection contract, and `src/qual/ui/test_a2ui_fallback_safety.py` plus `tests/unit/test_a2ui_contract.py` cover CLI fallback selection and unknown-card fallback.
- Typed/allowlisted actions: `shared/src/exegesis_shared/contracts/actions.py` defines typed action descriptors and deterministic action slots; tests cover policy-gated actions and stable `apply_patch` / `reject_patch` ordering.
- Engine-authoritative handling: the reviewed range exposes declarative selection metadata only. It does not execute actions in `shared` or add renderer-owned behavior; selected actions remain resolved by the engine/CLI control surface.
- Renderer boundary: shared contracts define cards/actions/selection types, while rendering and terminal fallback stay in `src/qual/ui/a2ui.py`.

## Canonical Demo-Path Step Advanced

- Step: `preview and apply or reject a patch`
- Impact: Proposed-edit cards now carry stable shared action-selection metadata that CLI fallback can render and resolve, so an engine-produced patch can be previewed and then explicitly applied or rejected without depending on Textual or placing renderer behavior in `shared`.

## Commands Run With Results

- `make scope-check` -> failed: `THREAD_PACKET.md` is disallowed on `codex/feat-a2ui-contract`; this fixer edit is the reviewer-required handoff correction.
- `./quality-format.sh --check` -> passed
- `./quality-lint.sh` -> passed
- `./quality-test.sh` -> passed, 617 tests
- `./typecheck-test.sh` -> passed
- `make ci` -> failed at scope-check with the same `THREAD_PACKET.md` policy rejection before downstream CI steps ran.

## Scope-Check / Ownership Note

- Shared/integrator-locked edits: `YES`, because the reviewed source range includes `shared/src/exegesis_shared/contracts/**`.
- Routing/provider impact note: None. No model routing or provider configuration was touched.

## Risks / Blockers

- `make scope-check` and `make ci` are blocked by the required `THREAD_PACKET.md` edit on this feature branch. The corrected handoff packet now makes the reviewed commit/range, file list, roadmap/product-vision mapping, and A2UI lane gate evidence describe the same `feat-a2ui-contract` work.
