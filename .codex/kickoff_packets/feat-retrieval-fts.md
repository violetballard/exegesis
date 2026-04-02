# Lane Kickoff: feat-retrieval-fts

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Handoff type: retrieval feature handoff for the FTS-first retrieval lane.
- Approved exception note: Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for the `feat-retrieval-fts` lane; it is the shared-by-approval regression surface for the lane and exercises the canonical retrieval contract. `THREAD_PACKET.md`, this kickoff packet, `.codex/lane_meta/feat-retrieval-fts.json`, `codex_packet_handoff/tools/planner.py`, and `tests/unit/test_packet_planner.py` are handoff alignment artifacts or packet-planner coordination artifacts used only to keep reviewed-head packet emission aligned with the reviewed retrieval range. The `a8743f18` planner edit was approved packet-emission bookkeeping only.
- Completed scope summary: The retrieval lane kept SQLite FTS authoritative, exported the canonical retrieval query constructor through both retrieval facades, exposed `RetrievalConstraints` on the public retrieval helpers, kept PageIndex and embeddings as compatibility-only shims that fail closed, hardened FTS cache isolation, backfilled sparse source-bundle and context-bundle payloads, normalized downstream retrieval payload, provenance, and hit snapshots so deterministic excerpt, provenance, and hit-snapshot bundles remained stable, canonicalized payload bundle snapshots for deterministic downstream rehydration, normalized direct doc/excerpt/context bundle helpers, added downstream doc-hit `source_strategy` attribution, tightened source-bundle fallback handling for provenance, citation, doc, excerpt, and downstream payload rehydration, and the follow-up query-normalization and bundle-helper hardening kept audit keys stable across whitespace variants. Constraint payloads remain mapping/dataclass-shaped; iterable `doc_types` and `date_range` values are normalized deterministically from those inputs, and the reviewed implementation head is pinned at `6afe533d735811f245a4d04322735935a09d2477`. Docs-only alignment artifacts are listed separately and are not counted as reviewed implementation files.

## Scope completed

The retrieval lane kept SQLite FTS authoritative, exported the canonical retrieval query constructor through both retrieval facades, exposed `RetrievalConstraints` on the public retrieval helpers, kept PageIndex and embeddings as compatibility-only shims that fail closed, hardened FTS cache isolation, backfilled sparse source-bundle and context-bundle payloads, normalized downstream retrieval payload, provenance, and hit snapshots so deterministic excerpt, provenance, and hit-snapshot bundles remained stable, canonicalized payload bundle snapshots for deterministic downstream rehydration, normalized direct doc/excerpt/context bundle helpers, added downstream doc-hit `source_strategy` attribution, tightened source-bundle fallback handling for provenance, citation, doc, excerpt, and downstream payload rehydration, and the follow-up query-normalization and bundle-helper hardening kept audit keys stable across whitespace variants. Constraint payloads remain mapping/dataclass-shaped; iterable `doc_types` and `date_range` values are normalized deterministically from those inputs, and the reviewed implementation head is pinned at `6afe533d735811f245a4d04322735935a09d2477`. Docs-only alignment artifacts are listed separately and are not counted as reviewed implementation files.

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
- Constraint payloads stay mapping/dataclass-shaped; iterable `doc_types` and `date_range` values are normalized deterministically from those inputs.
- Approved shared regression coverage remains in `tests/unit/test_unified_retrieval.py`; docs-only alignment artifacts are separated from reviewed implementation files and are not counted as lane-owned retrieval code.

### Guardrails
- Keep retrieval deterministic.
- Avoid speculative future retrieval abstractions that do not help the MVP.
- Any engine integration should stay narrowly scoped to retrieval orchestration.
