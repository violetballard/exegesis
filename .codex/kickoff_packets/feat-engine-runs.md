# Lane Kickoff: feat-engine-runs

- Branch: `codex/feat-engine-runs`
- Lane/owned paths: `src/qual/engine/**`
- Scope goal: Nail the core run pipeline so planning, retrieval, patch proposals, provenance, and export all move through one stable engine flow for the CLI/A2UI MVP.

### Priority outcomes
1. Make the engine run lifecycle deterministic and testable.
2. Keep patch proposal, apply, reject, and audit behavior coherent.
3. Provide one explicit engine-side acceptance path for the Milestone 3 loop.

### Definition of done
- Plan-from-context works through the engine contract.
- Revise-selection or draft-from-context works through the engine contract.
- Patch proposal shape is stable.
- Apply and reject update document state consistently.
- One explicit engine-side acceptance flow proves the loop end to end.

### Milestone 3 closure focus
- Canonical demo-path step advanced by this lane:
  - produce a plan or revision
  - preview and apply or reject a patch
  - continue working without breaking document state
- Optimize for one believable acceptance path, not broader engine ambition.
- Prefer mergeable, integrator-friendly closure over more branch-local refinement.
- If the core loop already works for one path, stop widening scope and prove it with tests and handoff evidence.
- Treat review/integration closure as the current priority once the run path is coherent.

### Current intervention guidance
1. Minimize changes outside the core run loop needed for the canonical demo path.
2. Favor deterministic apply/reject behavior and explicit acceptance evidence over new run modes.
3. If a change does not directly make the retrieve -> revise/apply loop more real, defer it.
4. Handoff should state exactly which engine-side loop is now standing and which post-merge checks prove it.

### Current stale-approval recovery plan
- The previously approved packet rooted at `45f0c73e` is stale against current `main`.
- Do not try to re-integrate that commit as-is:
  - `src/qual/engine/run_pipeline.py` no longer exists on current `main`
  - `src/qual/engine/service.py` is now a thin compatibility surface
  - the canonical engine API now lives in `engine/src/exegesis_engine/api/app_service.py`
- Regenerate this lane from current `main`, not from the stale approval packet.
- First decision:
  - decide whether the explicit `accept_patch_flow` alias is still needed for the canonical demo path
  - if it is needed, forward-port it into the canonical API instead of resurrecting deleted compatibility modules
  - if it is not needed, close the lane by proving the current canonical `apply_patch` / `reject_patch` path already satisfies the demo loop
- Preferred implementation target for regeneration:
  - `engine/src/exegesis_engine/api/app_service.py`
- Avoid re-expanding scope back into the deleted pre-migration files unless a compatibility shim is truly required.
- Required regression coverage for the regenerated handoff:
  - extend `tests/unit/test_mvp_migration.py` to prove the canonical service exposes the accepted patch path needed by Milestone 3
  - keep the reviewed slice narrow and current-main-based
- Re-review packet requirements for the regenerated pass:
  - explicitly mark `45f0c73e` as obsolete/stale against current `main`
  - point review at the new current-main implementation commit only
  - state whether the lane closed by forward-porting the alias or by proving the alias is unnecessary
  - name the exact canonical demo-path step that is now more real

### Do not spend time on
- UI-driven workflow behavior.
- Speculative orchestration layers before one path is clearly solid.
- Multiple alternate run modes before the core loop stands.

### Guardrails
- No UI-specific business logic in engine modules.
- Keep provider/policy decisions centralized.
- Prefer small, testable orchestration steps over broad refactors.
