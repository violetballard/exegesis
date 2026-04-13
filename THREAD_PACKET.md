## Thread Handoff Packet

- Branch name: `codex/feat-a2ui-contract`
- Scope goal: Canonicalize materialized A2UI action order in `src/qual/ui/a2ui.py` so CLI fallback rendering stays deterministic.

## Traceability

- Runtime implementation commit(s): `76d066f50d0c00f87e66fe7d33a1d6d3c594c3f5` and `b929fe6c7a1159c7882acedd247aca31a93cd123`.
- Metadata-only resubmission support: this packet rewrite only. No packet-planner or tooling files are claimed as feature scope in this handoff.

## Scope completed

- Canonicalized materialized A2UI action order in `src/qual/ui/a2ui.py` and covered it in `tests/unit/test_a2ui_contract.py` so CLI fallback rendering stays deterministic.
- This work advances the canonical demo-path step: preview unsupported A2UI cards through deterministic CLI fallback before apply/reject decisions.
- The handoff now claims only the runtime A2UI change and its focused test; packet-planner and tooling follow-up are out of scope for this feature packet.

## Files changed

- `src/qual/ui/a2ui.py`
- `tests/unit/test_a2ui_contract.py` (approved shared regression coverage)
- `THREAD_PACKET.md`

## Plan Alignment

- Roadmap item(s) affected: `ROADMAP.md` Milestone 3: Real workflow loop
  - Lane mapping: `feat-a2ui-contract`: shared card/action contracts and selection models
  - Scope bullet: `move A2UI contracts into shared while keeping renderers outside shared`
- Vision capability affected: `PRODUCT_VISION.md` Capability 4: Shared UI contract (`A2UI`)
  - Cards/actions/selection types live in a client-agnostic shared layer.
  - Rendering adapters stay outside shared.

## Tasks completed

1. Updated `src/qual/ui/a2ui.py` to sort filtered actions by canonical JSON before terminal rendering, preserving deterministic CLI fallback output.
2. Kept contract coverage in `tests/unit/test_a2ui_contract.py` for canonical ordering behavior.
3. Rewrote the handoff packet so it no longer claims packet-planner or tooling work as feature scope, separates runtime and metadata-only traceability, and names the canonical demo-path step this change advances.

## Required Handoff Fields

- Roadmap item(s) affected: `ROADMAP.md` Milestone 3: Real workflow loop
- Vision capability affected: `PRODUCT_VISION.md` Capability 4: Shared UI contract (`A2UI`)
- Routing/provider impact note: None

## Commands Run And Outcomes

- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

## Risks / blockers

- Risk: `LOW`
- Blockers: none
