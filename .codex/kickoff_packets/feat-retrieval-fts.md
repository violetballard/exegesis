# Lane Kickoff: feat-retrieval-fts

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`
- Handoff type: retrieval feature handoff for the FTS-first retrieval lane.
- Scope goal: Keep the FTS-first retrieval lane scoped to deterministic excerpt/provenance/hit-snapshot output, public package-level `RetrievalConstraints` support, compatibility shims for legacy retrieval imports, and the reviewed retrieval-owned files only.

## Scope completed

The cumulative retrieval thread now keeps SQLite FTS as the authoritative retrieval path, exports the canonical retrieval query constructor through both facades, exposes `RetrievalConstraints` on the public retrieval helpers, keeps PageIndex and embeddings as compatibility-only shims, and normalizes downstream retrieval payload, provenance, and hit snapshots so excerpt and provenance bundles stay deterministic.

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
- Keep retrieval deterministic and auditable.
- Avoid speculative future retrieval abstractions that do not help the MVP.
- Any engine integration should stay narrowly scoped to retrieval orchestration.
