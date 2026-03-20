# Lane Kickoff: feat-engine-runs

- Branch: `codex/feat-engine-runs`
- Lane/owned paths: `src/qual/engine/**`
- Scope goal: Nail the core run pipeline so planning, retrieval, patch proposals, provenance, and export all move through one stable engine flow for the CLI/A2UI MVP.

### Priority outcomes
1. Make run lifecycle and artifact production deterministic.
2. Keep patch/apply/reject and audit events coherent.
3. Ensure retrieval and export integrate cleanly into the engine flow.

### Guardrails
- No UI-specific business logic in engine modules.
- Keep provider/policy decisions centralized.
- Prefer small, testable orchestration steps over broad refactors.
