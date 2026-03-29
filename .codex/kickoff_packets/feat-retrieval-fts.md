# Lane Kickoff: feat-retrieval-fts

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`
- Handoff type: retrieval feature handoff for the FTS-first retrieval lane.
- Completed scope summary: The retrieval lane kept SQLite FTS authoritative, exported the canonical retrieval query constructor through both retrieval facades, exposed `RetrievalConstraints` on the public retrieval helpers, kept PageIndex and embeddings as compatibility-only shims, normalized downstream retrieval payload, provenance, and hit snapshots so deterministic excerpt, provenance, and hit-snapshot bundles remained stable, canonicalized payload bundle snapshots for deterministic downstream rehydration, added downstream doc-hit `source_strategy` attribution, and tightened source-bundle fallback handling for provenance, citation, doc, and excerpt rehydration.

## Scope completed

The retrieval lane kept SQLite FTS authoritative, exported the canonical retrieval query constructor through both retrieval facades, exposed `RetrievalConstraints` on the public retrieval helpers, kept PageIndex and embeddings as compatibility-only shims, normalized downstream retrieval payload, provenance, and hit snapshots so deterministic excerpt, provenance, and hit-snapshot bundles remained stable, canonicalized payload bundle snapshots for deterministic downstream rehydration, added downstream doc-hit `source_strategy` attribution, and tightened source-bundle fallback handling for provenance, citation, doc, and excerpt rehydration.

## Budget note

This handoff stayed within the low-risk `8`-task cap. It did not rely on the sprint-mode `10`-task allowance or the high-risk `4`-task budget.

### Priority outcomes
1. Make SQLite FTS the primary retrieval path.
2. Return doc hits and excerpt hits with stable provenance.
3. Keep PageIndex and embeddings fallback-only behind the canonical retrieval facade.

### Source of truth
- Canonical retrieval logic remains in `src/qual/retrieval/**`.
- Engine-side retrieval exports, compatibility shims, and payload helpers remain in `src/qual/engine/retrieval/**`.
- Payload normalization keeps query, policy, provenance, and hit snapshots deterministic for downstream consumers.

### Guardrails
- Keep retrieval deterministic.
- Avoid speculative future retrieval abstractions that do not help the MVP.
- Any engine integration should stay narrowly scoped to retrieval orchestration.
