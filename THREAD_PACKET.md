## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Final HEAD SHA: `321616e11e58c16701c5d227bdf160abee41a648`
- Reviewed implementation commit(s):
  - `f8a32d372301be4a7c67b97a66ddc8e04f36011f`
  - `c7ca5bcdb3a1b829712c4b3d2f3a39e2bd26c14f`
  - `98ec3f4c0f475308b3ebb528551de923cba549ad`
  - `1c01a74b58888f408e9fa1134a10a29478c6f39a`
  - `cc16c21692b7ca4af9e7866a659b45fc18b87f63`
  - `23e4e4273b8808f5cc5a2f9adab1a7eb2d821b75`
  - `06a0e06ba9c584e209840da92171a1882ccb5628`
  - `c3716f77141bdee761377f0ee1b15cbcf285e02f`
  - `321616e11e58c16701c5d227bdf160abee41a648`

## Scope goal

Build the FTS-first retrieval MVP with deterministic excerpt and provenance output for engine generation flows, aligned to ROADMAP.md Milestone 3: Real workflow loop and PRODUCT_VISION.md capability 2, and expose `RetrievalConstraints` through the public retrieval helpers.

## Scope completed

Shipped:
- SQLite FTS remains the authoritative retrieval path.
- The canonical retrieval query constructor is exported through both retrieval facades.
- The public `retrieve_*` helpers now accept `RetrievalConstraints` objects as well as mapping payloads.
- Retrieval payload snapshots, citation bundles, and excerpt fallback rehydration are normalized so excerpt and provenance bundles stay deterministic.

Did not ship:
- No new shared or integrator-locked file edits.
- No provider or routing configuration changes.
- No retrieval behavior beyond the FTS-first MVP and deterministic payload, citation, and excerpt normalization work in the reviewed commits.

Packet-only handoff commits:
These are metadata/alignment commits only; the reviewed source tip is `321616e11e58c16701c5d227bdf160abee41a648`.
- `6400c4554de89773357891a91e4c9e2e5e0057a0`
- `a6ea3c8150ee8121b3a5efd0042e3204ae4f44c4`
- `6969f9376160df1ed1fda88bce7c232e49dcb422`

## Files changed

### Source changes

These are the exact source files changed across the reviewed retrieval implementation commits through `321616e11e58c16701c5d227bdf160abee41a648`.

- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/__init__.py`
- `src/qual/retrieval/service.py`

### Handoff artifacts

These files record the handoff metadata for the lane and are separated from the source diff above.

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`

## Tasks completed

1. Added FTS provenance retrieval bundles and retrieval service support for deterministic excerpt/provenance output.
2. Exported the canonical retrieval query constructor through the engine and package facades, and widened the public retrieval helpers to accept `RetrievalConstraints` objects.
3. Enforced FTS-only hit strategies while keeping PageIndex and embeddings as fallback-only plumbing.
4. Normalized downstream retrieval payload snapshots so tuple-shaped query and policy data rehydrates deterministically.
5. Hardened citation bundle normalization so deterministic excerpt and provenance bundles survive payload rehydration.
6. Added regression coverage for the normalized payload snapshots and retrieval facade exports.

## Budget alignment

- The thread finished within the low-risk cap of 8 tasks.
- No shared or integrator-locked files were edited.
- Packet-only handoff commits are metadata/alignment only; they do not change retrieval behavior and are excluded from the reviewed implementation scope.

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
