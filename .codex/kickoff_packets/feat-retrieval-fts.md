# Lane Kickoff: feat-retrieval-fts

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Handoff type: retrieval feature handoff for the FTS-first retrieval lane.
- Approved exception note: Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for the `feat-retrieval-fts` lane; it is the sole shared-by-approval regression surface for the lane and exercises the canonical retrieval contract. No other shared-by-approval files are part of the reviewed retrieval implementation range.

## Scope completed

The retrieval lane shipped an FTS-first retrieval MVP: SQLite FTS remains authoritative, the canonical retrieval query constructor is exported through both retrieval facades, retrieval payloads and provenance snapshots are deterministic for downstream engine flows, sparse source and context bundles rehydrate deterministically, and the excerpt lookup surface now uses the canonical FTS-only path so PageIndex-only excerpt IDs fail closed under shared regression coverage. PageIndex plus embeddings remain compatibility-only fallback shims that fail closed. The only shared-by-approval edit is `tests/unit/test_unified_retrieval.py`; the docs-only alignment commits `f13324d206b41c134a96ff837eea6427c31aa981` and `edb36142cfe75ff8c65aee95865adb2de7ac19b0` only refreshed packet metadata and stay outside the reviewed implementation range.

## Budget note

This handoff includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, so it is shared/high-risk work and should be read against the 4-task cap. The detailed task summary in `THREAD_PACKET.md` folds the cumulative retrieval thread into four meaningful items, and the docs-only alignment commits are called out separately from the reviewed implementation range.

### Priority outcomes
1. Make SQLite FTS the primary retrieval path.
2. Return doc hits and excerpt hits with stable provenance.
3. Keep PageIndex and embeddings fallback-only behind the canonical retrieval facade.

### Source of truth
- Canonical retrieval logic remains in `src/qual/retrieval/**`.
- Engine-side retrieval exports, compatibility shims, and payload helpers remain in `src/qual/engine/retrieval/**`.
- Payload normalization keeps query, policy, provenance, and hit snapshots deterministic for downstream consumers.
- Constraint payloads stay mapping/dataclass-shaped; iterable `doc_types` and `date_range` values are normalized deterministically from those inputs.
- Approved shared regression coverage remains in `tests/unit/test_unified_retrieval.py`; no other shared or integrator-locked files are part of the reviewed retrieval implementation.

### Guardrails
- Keep retrieval deterministic.
- Avoid speculative future retrieval abstractions that do not help the MVP.
- Any engine integration should stay narrowly scoped to retrieval orchestration.
