# Lane Kickoff: feat-retrieval-fts

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`
- Scope goal: Canonicalize FTS excerpt payloads in `src/qual/retrieval/service.py` so retrieval-backed fetches return stable payloads for downstream consumers.

### Priority outcomes
1. Normalize excerpt payloads and provenance fields in the retrieval service.
2. Keep section-scoped retrieval unsupported until the retrieval layer can resolve a concrete target.
3. Avoid widening the reviewed diff into PageIndex, embeddings, or doc-ranking work.

### Guardrails
- Keep the change limited to retrieval-owned paths.
- Preserve deterministic and auditable retrieval output.
- Separate source changes from handoff and lane metadata artifacts.
