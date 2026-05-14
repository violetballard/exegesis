## Thread Handoff Packet

- Branch name: `codex/feat-a2ui-contract`
- Scope goal: Make materialized A2UI patch actions deterministic for CLI fallback rendering without changing routing, provider behavior, or non-A2UI planner automation.
- Reviewed runtime commit: `b929fe6c7a1159c7882acedd247aca31a93cd123`.
- Review scope: Review only the runtime implementation in `b929fe6c7a1159c7882acedd247aca31a93cd123`. Later branch-tip commits are handoff packet corrections only and are not submitted as source/runtime implementation work for this review.
- Scope completed: `b929fe6c7a1159c7882acedd247aca31a93cd123` updates A2UI materialized action filtering so supported actions are normalized, deduplicated, and emitted in deterministic canonical JSON order while preserving invalid-action filtering and CLI fallback compatibility.
- Canonical demo-path step advanced: `preview and apply or reject a patch`. This work makes that step more real by ensuring materialized A2UI patch actions render deterministically for CLI fallback previews and action selection.
- Shared/integrator-locked edits: `NO` for the reviewed runtime implementation commit. The reviewed files stay in `src/qual/ui/a2ui.py` and `tests/unit/test_a2ui_contract.py`; no shared-by-approval or integrator-locked files are included in this handoff scope.

### Tasks Completed

1. Canonicalized supported materialized A2UI action output by normalizing, deduplicating, and sorting actions with stable JSON semantics.
2. Added/updated unit coverage for deterministic canonical action ordering while preserving invalid-action filtering behavior.

### Files Changed

Reviewed runtime implementation commit `b929fe6c7a1159c7882acedd247aca31a93cd123`:

- `src/qual/ui/a2ui.py`
- `tests/unit/test_a2ui_contract.py`

Packet-only correction files after the reviewed runtime commit:

- `THREAD_PACKET.md`

Planner, packet-planner test, and broad packet-maintenance changes are not part of this handoff scope. They are intentionally excluded from `Scope completed`, `Tasks completed`, and `Files changed` for this re-review.

### Budget/Limit Compliance

- Risk mode: standard lane-owned runtime slice.
- Task budget: `2` of `8` used.
- Time budget: within `45m`.
- Size limits: `2` reviewed runtime files, within `<=12 files`; runtime change is within `<=500 net LOC`.
- High-risk/shared cap: not applicable because the reviewed runtime implementation does not claim shared or integrator-locked edits.

### Commands Run

- `make scope-check` -> passed.
- `./quality-format.sh --check` -> passed.
- `./quality-lint.sh` -> passed.
- `./quality-test.sh` -> passed.
- `./typecheck-test.sh` -> passed.
- `make ci` -> passed.

### Risks/Blockers

- None known for the reviewed runtime slice.
- This packet intentionally makes no planner, packet-planner, retrieval, provider-routing, shared-package, or branch-tip runtime claims beyond `b929fe6c7a1159c7882acedd247aca31a93cd123`.

### Roadmap/Vision Mapping

- Roadmap item affected: active MVP work item `A2UI contracts with CLI fallback`.
- Vision capability affected: deterministic, engine-authoritative A2UI action contracts that can be rendered by CLI fallback clients.
- Canonical demo-path step advanced: `preview and apply or reject a patch`.

### Routing/Provider Impact

None. No model routing, provider configuration, or core entrypoint behavior is included in the reviewed runtime scope.

### Proposed `README.md` Patch Text

None.
