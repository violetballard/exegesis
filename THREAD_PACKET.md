## Thread Handoff Packet

- Branch name: `codex/feat-a2ui-contract`
- Scope goal: Canonicalize materialized A2UI action order in `src/qual/ui/a2ui.py` so CLI fallback rendering stays deterministic, and align packet planner defaults and review-facing packet text with the current Milestone 3 / capability 4 canon.

## Scope completed

- Canonicalized materialized A2UI action order in `src/qual/ui/a2ui.py` and covered it in `tests/unit/test_a2ui_contract.py` so CLI fallback rendering stays deterministic. Runtime change commit: `b929fe6c7a1159c7882acedd247aca31a93cd123`.
- Canonicalized stale `feat-a2ui-contract` handoff fields in the packet planner to the current Milestone 3 / capability 4 canon, removed the packet-planner fallback that invented a synthetic handback note for missing `tasks_completed`, added explicit `Scope completed` packet support, and updated the packet-planner regression coverage to the current Milestone 3 / capability 4 mapping.
- Current branch tip: `codex/feat-a2ui-contract` HEAD
- Handoff scope: runtime A2UI fix plus packet-planner follow-up aligned to `ROADMAP.md` Milestone 3 / `PRODUCT_VISION.md` Capability 4.
- Authoritative plan mapping: `ROADMAP.md` Milestone 3: Real workflow loop, specifically the `feat-a2ui-contract` lane mapping for shared card/action contracts and selection models; `PRODUCT_VISION.md` Capability 4: Shared UI contract (`A2UI`).
- Roadmap item(s) affected: `ROADMAP.md` Milestone 3: Real workflow loop (see `ROADMAP.md` lines 43-65), with lane mapping `feat-a2ui-contract`: shared card/action contracts and selection models
  - Scope bullet: `move A2UI contracts into shared while keeping renderers outside shared`
  - Exit criterion: the engine loop keeps the shared A2UI contract stable enough for CLI compatibility
- Vision capability affected: `PRODUCT_VISION.md` Capability 4: Shared UI contract (`A2UI`) (see `PRODUCT_VISION.md` lines 39-41)
  - Cards/actions/selection types live in a client-agnostic shared layer.
  - Rendering adapters stay outside shared.
- Reviewer fix status: required fix `#1` is satisfied by the runtime A2UI implementation in `src/qual/ui/a2ui.py` and `tests/unit/test_a2ui_contract.py`; required fixes `#2`-`#4` are satisfied by the packet-planner and handoff follow-up in this branch.
- Tasks completed:
  1. Updated `src/qual/ui/a2ui.py` to sort filtered actions by canonical JSON before terminal rendering, preserving deterministic CLI fallback output.
  2. Kept contract coverage in `tests/unit/test_a2ui_contract.py` for canonical action ordering and allowlisted fallback behavior.
  3. Updated `codex_packet_handoff/tools/planner.py` so missing `tasks_completed` values are surfaced explicitly instead of backfilled with a synthetic handback note.
  4. Added explicit `Scope completed` packet support and canonicalized the `feat-a2ui-contract` handoff mapping in `codex_packet_handoff/tools/planner.py`.
  5. Updated `tests/unit/test_packet_planner.py` to assert the current Milestone 3 / capability 4 mapping and the new `Scope completed` section.
  6. Rewrote this handoff packet so the review trail shows the runtime A2UI delta and the packet-planner follow-up together.

## Files changed

- `src/qual/ui/a2ui.py` (`b929fe6c7a1159c7882acedd247aca31a93cd123` runtime change)
- `tests/unit/test_a2ui_contract.py` (`b929fe6c7a1159c7882acedd247aca31a93cd123` runtime change)
- `codex_packet_handoff/tools/planner.py`
- `tests/unit/test_packet_planner.py`
- `THREAD_PACKET.md`
- `.codex/packets/lanes/feat-a2ui-contract/inbox/feature/F__codex-feat-a2ui-contract__aa875cd03ea2a8e092f527610640827baa7b7b5a__20260320T210541Z.md` (removed)

## Plan Alignment

- Roadmap item(s) affected: `ROADMAP.md` Milestone 3: Real workflow loop (see `ROADMAP.md` lines 43-65)
- Vision capability affected: `PRODUCT_VISION.md` Capability 4: Shared UI contract (`A2UI`) (see `PRODUCT_VISION.md` lines 39-41)
- Roadmap scope bullet: `move A2UI contracts into shared while keeping renderers outside shared`
- Audit mapping: the runtime A2UI ordering fix keeps CLI fallback rendering deterministic, and the packet-planner follow-up keeps the Milestone 3 / capability 4 handoff text aligned for re-review.

## Required Handoff Fields

- Roadmap item(s) affected: `ROADMAP.md` Milestone 3: Real workflow loop
  - Lane mapping: `feat-a2ui-contract`: shared card/action contracts and selection models
  - Scope bullet: `move A2UI contracts into shared while keeping renderers outside shared`
- Vision capability affected: `PRODUCT_VISION.md` Capability 4: Shared UI contract (`A2UI`)
  - Cards/actions/selection types live in a client-agnostic shared layer.
  - Rendering adapters stay outside shared.
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
