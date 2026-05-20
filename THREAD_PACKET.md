## Thread Handoff Packet

- Branch name: `codex/feat-a2ui-contract`
- Source commit(s): `552fb38b5fed2e0c6fde4eb33ae4b5a3e0d5999f`
- Scope goal: Canonicalize terminal A2UI action slots for the CLI fallback contract so preview/apply/reject flows resolve deterministic one-based selections.
- Scope completed: Terminal A2UI action slots are sorted by materialized one-based slot order, and unit coverage verifies sorted materialized selection entries plus distinct apply/reject patch action slots.
- Roadmap item(s) affected (from `ROADMAP.md`): `Milestone 3: Real workflow loop` because deterministic terminal action selection supports the engine loop step to preview and apply or reject a patch.
- Vision capability affected (from `PRODUCT_VISION.md`): `Capability 4: Shared UI contract (A2UI)` because the source change stabilizes shared cards/actions/selection types while preserving CLI fallback renderers outside shared.
- Shared/integrator-locked edits: `NO`
- Review type: packet/control-plane maintenance reissue for the A2UI implementation review surface below.
- Approval note: This control-plane packet edit is made only to satisfy the reviewer-required fixes in `fixer__feat-a2ui-contract__20260520T003850Z`; the reviewed implementation changes remain limited to A2UI lane source/test files, with no shared or integrator-locked files in the reviewed implementation surface.
- Ownership note: the reviewed implementation is limited to `src/qual/ui/a2ui.py` and `tests/unit/test_a2ui_contract.py`.
## Reviewed source-range evidence
The reviewed implementation files for `552fb38b5fed2e0c6fde4eb33ae4b5a3e0d5999f` are:
  - `src/qual/ui/a2ui.py`
  - `tests/unit/test_a2ui_contract.py`
- Tasks completed:
  1. Canonicalized terminal A2UI action materialization so actions and `action_selection.order` follow materialized one-based slot order.
  2. Added unit coverage for sorted materialized selection entries and distinct patch apply/reject action slots.
  3. Advanced the canonical demo-path step: `preview and apply or reject a patch`.
  4. Preserved typed/allowlisted, engine-authoritative action handling; existing A2UI tests cover supported-action filtering, CLI fallback selection, and `test_engine_policy_gate_is_authoritative`.
  5. Mapped the work to `Milestone 3: Real workflow loop` and A2UI Capability 4 without claiming packet-planner or metadata-only implementation work.
## Files changed
- Packet/control-plane maintenance commit:
  - `THREAD_PACKET.md`
- Reviewed implementation files:
  - `src/qual/ui/a2ui.py`
  - `tests/unit/test_a2ui_contract.py`
- Commands run with results:
  - `make scope-check` -> failed: `THREAD_PACKET.md` is a disallowed control-plane file on `codex/feat-a2ui-contract`.
  - `SCOPE_ALLOW_SHARED=1 make scope-check` -> failed with the same `THREAD_PACKET.md` control-plane policy rejection.
  - `./quality-format.sh --check` -> passed
  - `./quality-lint.sh` -> passed
  - `./quality-test.sh` -> passed
  - `./typecheck-test.sh` -> passed
  - `make ci` -> failed at scope-check for the same `THREAD_PACKET.md` control-plane policy rejection.
- Scope-check / ownership note:
  - Shared/integrator-locked edits: `NO`
  - Ownership note: reviewed implementation edits are limited to A2UI lane source/test files.
- Routing/provider impact note: None. No model routing or provider configuration was touched.
- Risks / blockers:
  - Control-plane metadata fix required: `THREAD_PACKET.md` is the reviewer-required metadata correction, but feature-branch scope policy rejects control-plane files before quality gates can complete `make ci`.
  - The source-affecting commit is limited to terminal A2UI contract behavior and unit coverage.
