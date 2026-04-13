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

### Do not spend time on
- UI-driven workflow behavior.
- Speculative orchestration layers before one path is clearly solid.
- Multiple alternate run modes before the core loop stands.

### Guardrails
- No UI-specific business logic in engine modules.
- Keep provider/policy decisions centralized.
- Prefer small, testable orchestration steps over broad refactors.
