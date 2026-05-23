# Lane Kickoff: feat-engine-runs

- Branch: `codex/feat-engine-runs`
- Lane/owned paths: `src/qual/engine/**`, `src/qual/drafting/**`, `engine/src/exegesis_engine/api/**`, `engine/src/exegesis_engine/workflow/**`, `engine/src/exegesis_engine/patches/**`, `engine/src/exegesis_engine/audit/**`, `engine/src/exegesis_engine/services/**`, `engine/src/exegesis_engine/state/models.py`, `tests/unit/test_engine*.py`, `tests/unit/test_draft*.py`, `tests/unit/test_workflow*.py`, `tests/unit/test_patch*.py`, `tests/unit/test_audit*.py`, `tests/unit/test_policy_gate.py`
- Scope goal: Close the engine-side plan, draft, revise, patch, apply, and reject loop through canonical services so the MVP can run without Textual wiring.

### Priority outcomes
1. Keep plan/revise/patch/apply flows reachable through the canonical app service.
2. Preserve patch-first revision behavior with explicit apply/reject decisions.
3. Record enough request/result/proposal state for later dogfooding and provenance work.

### Definition of done
- Engine can produce a plan or revision from gathered context.
- Patch proposals can be previewed and resolved through canonical service calls.
- Apply/reject updates document/session state deterministically.
- The canonical demo path can continue after a resolved patch without hand-editing state.

### Milestone 3 closure focus
- Canonical demo-path step advanced:
  - produce a plan or revision
  - preview and apply or reject a patch
  - persist updated document/session state
- Prefer one believable end-to-end service path over broader engine surface area.

### Do not spend time on
- Textual UI implementation.
- Alternative model/provider routing.
- Speculative collaboration/sync.
- Full provenance substrate beyond what the current loop needs.

### Guardrails
- Stay lane-owned.
- Do not edit control-plane metadata, packet files, or ownership policy.
- Keep CLI/client compatibility through engine contracts, not UI shortcuts.
