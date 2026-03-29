## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Final HEAD SHA: `1109cceba7d402d3e05c6d7ba59dac363b0d9ea6`
- Reviewed implementation range: `1d6057e9..1109cceba7d402d3e05c6d7ba59dac363b0d9ea6`
- Handoff type: cumulative full-thread retrieval handoff

## Implementation commit(s)

- `3c51e34bc54003b8fe4a28b8d3db58450f6d9ab6` - keep pageindex shim out of routing
- `1109cceba7d402d3e05c6d7ba59dac363b0d9ea6` - canonicalize payload bundle snapshots

## Docs-only alignment commit(s)

- `0cff411ae4e4972707ac145ab46f002c11f38cea` - align handoff packet details
- `8e17a500af65e43d7255291807e2fbef9448a66f` - sync handoff packet head
- `9f533914940b5a3f45859b0269909bbc11592030` - align handoff metadata
- `9851fb47e930cd0df2b663264683cd4a3a6e0687` - align handoff metadata to current head
- `e4b895ddf767deb962d269c6801df364c432a3bb` - restamp handoff packet to current head

## Scope goal

Build the FTS-first retrieval MVP with deterministic excerpt, provenance, and hit-snapshot output for engine generation flows, aligned to ROADMAP.md Milestone 3: Real workflow loop and PRODUCT_VISION.md capability 2, while keeping PageIndex and embeddings fallback-only and exposing `RetrievalConstraints` through the public retrieval helpers.

## Scope completed

Shipped:
- SQLite FTS remains the authoritative retrieval path.
- The canonical retrieval query constructor is exported through both retrieval facades.
- The public `retrieve_*` helpers accept `RetrievalConstraints` objects as well as mapping payloads.
- PageIndex and embeddings remain compatibility-only shims and fallback-only plumbing behind the FTS-first policy.
- Retrieval payload, citation, provenance, and hit snapshots normalize list-like and strategy fields deterministically, including the `retrieval_source_strategy` alias and list-like provenance rehydration.
- Payload bundle snapshots are canonicalized for deterministic downstream rehydration.
- Regression coverage exercises the normalized payload snapshots, facade exports, and FTS citation/provenance helpers.

Did not ship:
- No shared or integrator-locked file edits.
- No provider or routing configuration changes.
- No retrieval behavior beyond the FTS-first MVP and deterministic snapshot normalization work in the reviewed range.

Reviewed range note:
- The handoff is cumulative, not tip-only; the reviewed implementation range ends at `1109cce`, and the docs-only alignment commits above only restamp packet metadata.

## Files changed

### Reviewed implementation files

These are the exact source files changed across the reviewed cumulative range `1d6057e9..1109cceba7d402d3e05c6d7ba59dac363b0d9ea6`.

- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/embeddings_strategy.py`
- `src/qual/engine/retrieval/pageindex_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/__init__.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

## Docs-only alignment files

These metadata files record the handoff alignment work and are separate from the reviewed implementation diff above.

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`

## Tasks completed

1. Added FTS provenance retrieval bundles and retrieval service support for deterministic excerpt/provenance output.
2. Exported the canonical retrieval query constructor through both retrieval facades.
3. Widened the public retrieval helpers to accept `RetrievalConstraints` objects.
4. Added PageIndex and embeddings compatibility shims without changing the FTS-first active path.
5. Normalized retrieval payload, citation, provenance, and source snapshots for deterministic rehydration and canonical payload bundle snapshots.
6. Tightened retrieval hit snapshots to carry the canonical `retrieval_source_strategy` alias and list-like provenance fields.
7. Added regression coverage for the normalized payload snapshots, facade exports, and citation/provenance helpers.
8. Canonicalized payload bundle snapshots for deterministic downstream rehydration.

## Budget alignment

- The thread finished within the low-risk cap of 8 tasks.
- No shared or integrator-locked files were edited.
- The reviewed range is cumulative; metadata-only handoff commits in the range only adjust handoff artifacts, and the `3c51e34b` / `1109cce` retrieval commits stay inside the FTS-first retrieval lane.

## Commands run with results

- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

## Risks/blockers

- Risk: `LOW`
- Blockers: none

## Roadmap item(s) affected

- `ROADMAP.md`: `Milestone 3: Real workflow loop`

## Vision capability affected

- 2. Retrieval-first context handling
- 6. Auditable state and workflow

## Routing/provider impact note

- None

## Compatibility note

- PageIndex and embeddings remain fallback-only plumbing behind the FTS-first policy for this MVP; they are not required retrieval paths.

## Scope-check / ownership note

- Shared/integrator-locked edits: `NO`
