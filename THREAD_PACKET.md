## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Final HEAD SHA: `aacb9cc06f99cb149319da198d6c96cd9628735c`
- Reviewed implementation range: `1d6057e9..aacb9cc06f99cb149319da198d6c96cd9628735c`
- Handoff type: cumulative full-thread retrieval handoff

## Implementation commit(s)

These are the reviewed code commits that deliver the FTS-first retrieval lane across the cumulative range.

- `c92025af6e11c396f84356967cea704cadb20f5b` - add excerpt lookup audit context
- `c4944661a0a682821c486810918c2c1fabac1a41` - add source-bundle context regression
- `47b3977d271e3f7faacb6ba3082ab94a2d327fcb` - export canonical query constructor
- `23e4e4273b8808f5cc5a2f9adab1a7eb2d821b75` - normalize retrieval excerpt fallbacks
- `1cc160ff7a56f539b4726dd03cc477f714243e8d` - tighten retrieval hit snapshots
- `20bbc5502f4a5f4e8339faa25fd44d3d7caeecdc` - restore compatibility strategy shims
- `f511f4b5c53bae03aba746e9ceb5b1b27141f7e5` - export FTS citation bundle from engine
- `439af5c84a224d23c861e0206834bfd598d3836b` - refactor canonical retrieval provenance bundling
- `321616e11e58c16701c5d227bdf160abee41a648` - harden retrieval bundle normalization
- `06a0e06ba9c584e209840da92171a1882ccb5628` - accept constraint dataclasses in public helpers
- `c3716f77141bdee761377f0ee1b15cbcf285e02f` - widen package constraint contract
- `3c51e34bc54003b8fe4a28b8d3db58450f6d9ab6` - keep pageindex shim out of routing
- `1109cceba7d402d3e05c6d7ba59dac363b0d9ea6` - canonicalize payload bundle snapshots
- `aacb9cc06f99cb149319da198d6c96cd9628735c` - add doc citation source attribution

## Metadata-only alignment commit(s)

These metadata files record the handoff alignment work and are separate from the reviewed implementation diff above.

- `c160c47543da7a75e9a4e1886b7e43ffbb6b1a3d` - align handoff metadata
- `6e6db6c49c342fb3a3b707124c446204f200d073` - align handoff milestone mapping
- `1900aba540ad7590f24e97edca63b3fbfc121884` - correct handoff metadata
- `78b27dd3ce244e99e12a336c0719a6e0bfc99a77` - align handoff packet metadata
- `6e9853b24f1419b158102e1afd68b40496009bcf` - align handoff packet head sha
- `2c1d2737cd4e63ca0d03acc644242477a66e8647` - tighten handoff packet scope
- `91a78c3f528d8b76e39000f0aac18f87d5927629` - align handoff head sha
- `9fef8afea6cfb69a8127093af6488f6ab25534e4` - clarify metadata-only scope
- `6400c4554de89773357891a91e4c9e2e5e0057a0` - clarify metadata-only handoff
- `6969f9376160df1ed1fda88bce7c232e49dcb422` - align handoff traceability
- `a6ea3c8150ee8121b3a5efd0042e3204ae4f44c4` - stamp handoff head sha
- `9851fb47e930cd0df2b663264683cd4a3a6e0687` - align handoff metadata to current head
- `9f533914940b5a3f45859b0269909bbc11592030` - align handoff metadata
- `8e17a500af65e43d7255291807e2fbef9448a66f` - sync handoff packet head
- `0cff411ae4e4972707ac145ab46f002c11f38cea` - align handoff packet details
- `e4b895ddf767deb962d269c6801df364c432a3bb` - restamp handoff packet to current head
- `2836df72a27ba5e1803a99714a580648d7710061` - split handoff commit metadata (metadata-only)

## Completed scope summary

Completed the cumulative `1d6057e9..aacb9cc` retrieval thread for the FTS-first retrieval MVP: SQLite FTS is authoritative, the canonical retrieval query constructor is exported through both retrieval facades, `RetrievalConstraints` are accepted by public helpers, PageIndex and embeddings stay compatibility-only, retrieval payload/provenance/hit snapshots normalize deterministically, payload bundle snapshots are canonicalized, and downstream doc hits carry source attribution.

## Scope completed

Shipped:
- SQLite FTS remains the authoritative retrieval path.
- The canonical retrieval query constructor is exported through both retrieval facades.
- The public `retrieve_*` helpers accept `RetrievalConstraints` objects as well as mapping payloads.
- PageIndex and embeddings remain compatibility-only shims and fallback-only plumbing behind the FTS-first policy.
- Retrieval payload, citation, provenance, and hit snapshots normalize list-like and strategy fields deterministically, including the `retrieval_source_strategy` alias, downstream `source_strategy` attribution, and list-like provenance rehydration.
- Payload bundle snapshots are canonicalized for deterministic downstream rehydration.
- Regression coverage exercises the normalized payload snapshots, facade exports, and FTS citation/provenance/source-attribution helpers.

Did not ship:
- No shared or integrator-locked file edits.
- No provider or routing configuration changes.
- No retrieval behavior beyond the FTS-first MVP, deterministic snapshot normalization, and doc-hit source attribution work in the reviewed range.

Reviewed range note:
- The handoff is cumulative, not tip-only; the reviewed implementation range ends at `aacb9cc0`, and the metadata-only alignment commits above only restamp packet metadata.

## Files changed

### Reviewed implementation files

These are the exact source files changed across the reviewed cumulative range `1d6057e9..aacb9cc06f99cb149319da198d6c96cd9628735c`.

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
2. Canonicalized excerpt provenance so downstream payloads carry stable hashes and fingerprints.
3. Kept retrieval FTS-first and left PageIndex/embeddings fallback-only plumbing.
4. Exported the canonical retrieval query constructor through both retrieval facades and kept the auto path on the FTS-first implementation.
5. Added source bundle context regression coverage and deterministic rehydration helpers.
6. Tightened retrieval hit snapshots to carry the canonical `retrieval_source_strategy` alias, list-like provenance fields, and downstream `source_strategy` attribution.
7. Added regression coverage for the normalized payload snapshots, facade exports, and citation/provenance helpers.
8. Canonicalized payload bundle snapshots for deterministic downstream rehydration.

## Budget alignment

- The thread finished within the low-risk cap of 8 tasks.
- No shared or integrator-locked files were edited.
- The reviewed range is cumulative; metadata-only handoff commits in the range only adjust handoff artifacts, and the retrieval commits from `c92025af` through `aacb9cc0` stay inside the FTS-first retrieval lane.

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
