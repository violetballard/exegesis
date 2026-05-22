# Lane Kickoff: feat-retrieval-fts

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`, `tests/unit/test_retrieval*.py`, `tests/unit/test_unified_retrieval.py`
- Scope goal: Keep FTS-first retrieval authoritative for the engine-first MVP and return structured, provenance-rich results that can be promoted into the basket.

### Priority outcomes
1. Preserve literal FTS search as the default retrieval path.
2. Return stable retrieval payloads with document identity, source type, snippets, spans, hashes, and basket-promotion provenance.
3. Keep retrieval usable by engine runs without requiring vector/RAG infrastructure.

### Definition of done
- Search/retrieval calls are deterministic and test-covered.
- Results are structured enough for basket promotion and A2UI/retrieval cards.
- Sparse/FTS provenance rejects incomplete or stale source records.
- The canonical demo path can retrieve relevant material and gather/promote context.

### Milestone 3 closure focus
- Canonical demo-path step advanced:
  - retrieve relevant material
  - promote or gather context into the basket with deterministic FTS provenance
- Prefer closing one reliable retrieval-to-basket path over adding alternate retrieval modes.

### Do not spend time on
- Embeddings/vector search.
- RAG indexing.
- UI card polish beyond payload contracts.
- Literature/OCR import.

### Guardrails
- Stay lane-owned.
- Feature-lane unit tests for retrieval are allowed.
- Do not edit control-plane metadata, packet files, or ownership policy.
