# Lane Kickoff: feat-retrieval-fts

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`
- Handoff type: retrieval feature handoff for the FTS-first retrieval lane.
- Scope goal: Keep the FTS-first retrieval lane scoped to deterministic excerpt/provenance output and the reviewed retrieval-owned files only.

## Scope completed

This lane now keeps the FTS-first retrieval path authoritative, returns deterministic excerpt and provenance payloads for engine generation flows, and leaves PageIndex and embeddings as fallback-only plumbing behind the canonical retrieval package.

## Budget note

This handoff stayed within the low-risk `8`-task cap. It did not rely on the sprint-mode `10`-task allowance or the high-risk `4`-task budget.

### Priority outcomes
1. Make SQLite FTS the primary retrieval path.
2. Return doc hits and excerpt hits with stable provenance.
3. Defer PageIndex, embeddings, and multi-strategy retrieval behavior.

### Definition of done
- Retrieval is FTS-first by default.
- Results are structured and deterministic enough for basket promotion and workflow use.
- Excerpt provenance is stable and auditable.
- Retrieval is reachable through the canonical engine surface.

### Do not spend time on
- Over-investing in embeddings or alternate retrieval modes.
- UI rendering concerns.
- Search features outside the core writing loop.

### Source of truth
- Canonical retrieval logic remains in `src/qual/retrieval/**`.
- Engine-side retrieval files are compatibility/export shims that route the FTS-first path:
  - `src/qual/engine/retrieval/__init__.py`
  - `src/qual/engine/retrieval/embeddings_strategy.py`
  - `src/qual/engine/retrieval/fts_strategy.py`
  - `src/qual/engine/retrieval/pageindex_strategy.py`
  - `src/qual/engine/retrieval/payload.py`
  - `src/qual/engine/retrieval/policy.py`

### Guardrails
- Keep retrieval deterministic and auditable.
- Avoid speculative future retrieval abstractions that do not help the MVP.
- Any engine integration should stay narrowly scoped to retrieval orchestration.
