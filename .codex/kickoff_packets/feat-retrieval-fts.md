# Lane Kickoff: feat-retrieval-fts

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/engine/retrieval/**`, `src/qual/retrieval/service.py`
- Scope goal: Centralize the FTS-first retrieval policy in engine/retrieval and propagate policy metadata through retrieval service diagnostics, provenance, and audit records.
- Scope completed: The reviewed commit `d050e4016bb446424a031b3c0b9c21b26220c5a9` centralizes the FTS-first policy, re-exports the active engine strategy surface, and threads policy metadata into retrieval-service diagnostics, provenance, and audit records for auditable behavior.

### Priority outcomes
1. Keep the policy definition in one engine-level place and expose the active retrieval strategy surface from there.
2. Carry retrieval policy metadata into diagnostics, audit metadata, and provenance so FTS-first behavior is auditable.
3. Avoid implying new PageIndex, ingestion, or provider-routing work in this promotion.

### Guardrails
- Keep the change limited to retrieval orchestration policy and metadata plumbing.
- Preserve commit accuracy between the packet, lane metadata, and git history.
- Do not reference unreviewed retrieval source files or unrelated retrieval MVP scope.
