# Lane Kickoff: feat-context-storage

- Branch: `codex/feat-context-storage`
- Lane/owned paths: `src/qual/context/**`, `src/qual/storage/**`
- Scope goal: Harden vault, excerpt, and context-set persistence for the engine-first MVP so retrieval, patching, and export flows can rely on stable local state.

### Priority outcomes
1. Keep vault and context persistence deterministic and recoverable.
2. Make excerpt/context-set storage easy to audit and resilient to malformed local state.
3. Support the engine-side workflow loop without introducing UI-specific state semantics.

### Definition of done
- Document state persists cleanly.
- Basket and context state persist cleanly.
- Malformed or partial local state is recovered or quarantined safely.
- Engine flows can rely on storage without defensive one-off repair logic.

### Do not spend time on
- UI-facing basket semantics or interaction patterns.
- Speculative sync or collaboration features.
- Storage abstractions that do not improve determinism or recovery.

### Guardrails
- Shared file edits require explicit approval.
- Favor test-covered recovery and persistence behavior over new surface area.
- No UI-specific logic in storage/context modules.
