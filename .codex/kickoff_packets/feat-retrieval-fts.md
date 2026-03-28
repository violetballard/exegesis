# Lane Kickoff: feat-retrieval-fts

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`
- Handoff type: retrieval feature handoff for the FTS-first retrieval lane.
- Scope goal: Keep the FTS-first retrieval lane scoped to deterministic excerpt/provenance output and the reviewed retrieval-owned files only.

### Priority outcomes
1. Make SQLite FTS the primary retrieval path.
2. Return doc hits and excerpt hits with stable provenance.
3. Defer PageIndex, embeddings, and multi-strategy retrieval behavior.

### Guardrails
- Keep retrieval deterministic and auditable.
- Avoid speculative future retrieval abstractions that do not help the MVP.
- Any engine integration should stay narrowly scoped to retrieval orchestration.
