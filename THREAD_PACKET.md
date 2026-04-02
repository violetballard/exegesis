## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Final HEAD SHA (reviewed implementation head): `6afe533d735811f245a4d04322735935a09d2477`
- Reviewed implementation range: `1d6057e9..6afe533d735811f245a4d04322735935a09d2477`
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
- `c2903c0dfeca3ceb0201455b1e58a71a612fa1e1` - improve retrieval source bundle fallbacks
- `78f173d5c45a9a59f5098b86d95a64aa48e9b627` - canonicalize query normalization
- `377300b94b26ed3ef28236012ddad50483ed49e8` - harden query constraint normalization
- `dc7b6e22ad025e84e2d8eda31c8e0aa3b0c8d833` - preserve canonical source bundle snapshots
- `5a4e6b622b52c5a7a84dcac118e3626de22e89b6` - accept iterable constraint values
- `f22391da7ac57f0f92346d96f783f7815e057b69` - align handoff packet and iterable contract
- `d08edc2bdb3a3c03911f21a0a5d08b26513ea562` - fail closed on deferred strategies
- `42820d4864f8b5137a6a9e05399ad68fe5b9d4ac` - reconstruct payload from source bundles
- `526fbe490f77ed63284fa8de6ddec8849c7c4944` - normalize bundle snapshot helpers
- `965396ea8ec8e26e175780601794b47598987068` - harden FTS cache isolation
- `a8efddde31b600eb123d0bea1eed22c8c863bef5` - backfill sparse retrieval source bundles
- `d951ed275be3ebffeaecb626b4b5049d85d7ba49` - add source bundle fingerprint
- `fe1e837b4af8ce95275bca6ac48e5c031c05931e` - add retrieval source bundle alias
- `6afe533d735811f245a4d04322735935a09d2477` - backfill sparse retrieval context payloads

## Docs-only alignment commit(s)

These alignment files and commits record the handoff bookkeeping work and are separate from the reviewed implementation diff above.

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
- `46f8d2f297bc12a3753479a6064746151ab1b0d0` - restamp handoff scope hash
- `a8743f187107c8b2268907731cee5595975a19b1` - anchor packet metadata to reviewed head
- `3707b35360b8c64b1fdafaaef38a00dede50eca3` - tighten handoff file list
- `bf979b9f4400212ed9b655855f10312069ac735f` - note approved metadata-only handoff artifacts
- `bf08637e50efe848841dc9e3ac1013acd1748cb0` - clarify reviewed-head handoff packet
- `6cdfeb57f76595bab6d912e81bd60ceb14fee3d0` - clarify handoff scope sections
- `f13522d7ce98393c1b72165a0313fe52fb6d0d14` - realign handoff packet to current head
- `652f5e3b1ab8cbb9293530eb259c5c1e29fbf91a` - realign handoff packet to current head

These alignment commits only restamp handoff metadata and packet-planner coordination artifacts. `a8743f187107c8b2268907731cee5595975a19b1` also touched `codex_packet_handoff/tools/planner.py` and `tests/unit/test_packet_planner.py` strictly to keep the planner/review packet aligned with the reviewed head.

## Completed scope summary

Completed the cumulative `1d6057e9..6afe533d735811f245a4d04322735935a09d2477` retrieval thread for the FTS-first retrieval MVP, with the reviewed implementation head pinned at `6afe533d735811f245a4d04322735935a09d2477`: SQLite FTS stayed authoritative, the canonical retrieval query constructor stayed exported through both retrieval facades, `RetrievalConstraints` stayed accepted by public helpers, FTS cache isolation was hardened, source-bundle and sparse context payloads backfilled deterministically, retrieval payload/provenance/hit snapshots normalized deterministically, payload bundle snapshots were canonicalized, direct doc/excerpt/context bundle helpers round-tripped through canonical bundle shapes, downstream doc hits carried source attribution, source-bundle fallbacks rehydrated provenance/citation/doc/excerpt/downstream payload bundles, and query-normalization plus source-bundle fingerprinting kept audit keys stable across whitespace variants.

## Scope completed

Shipped:
- SQLite FTS remains the authoritative retrieval path.
- The canonical retrieval query constructor is exported through both retrieval facades.
- The public `retrieve_*` helpers accept `RetrievalConstraints` objects as well as mapping payloads, and iterable constraint inputs normalize deterministically.
- Retrieval payload, citation, provenance, and hit snapshots normalize list-like and strategy fields deterministically, including the `retrieval_source_strategy` alias, downstream `source_strategy` attribution, list-like provenance rehydration, and source-bundle fallback rehydration for provenance/citation/doc/excerpt/downstream payload helpers.
- Payload bundle snapshots are canonicalized for deterministic downstream rehydration, and direct doc/excerpt/context bundle helpers round-trip through canonical bundle shapes.
- Regression coverage exercises the normalized payload snapshots, facade exports, FTS citation/provenance/source-attribution helpers, and the source-bundle-only downstream payload reconstruction path.
- Constraint payloads stay mapping/dataclass-shaped; iterable `doc_types` and `date_range` values are normalized deterministically from those inputs.
- Approved shared regression coverage remains in `tests/unit/test_unified_retrieval.py`; docs-only alignment artifacts are listed separately below and are not counted as reviewed implementation files.

Stayed fallback-only:
- PageIndex and embeddings remain compatibility-only shims and fallback-only plumbing behind the FTS-first policy, failing closed when deferred.

Did not ship:
- No unapproved shared or integrator-locked file edits in the reviewed retrieval implementation.
- No provider or routing configuration changes.
- No retrieval behavior beyond the FTS-first MVP, deterministic snapshot normalization, FTS cache isolation, sparse source/context backfill, doc-hit source attribution, source-bundle payload rehydration, and direct bundle helper normalization work in the reviewed range.

Reviewed range note:
- The handoff is cumulative, not tip-only; the reviewed implementation range ends at `6afe533d735811f245a4d04322735935a09d2477`, and the docs-only alignment commits above only restamp packet metadata or packet-planner coordination artifacts.

## Approved exception note

- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for the `feat-retrieval-fts` lane; it is the shared-by-approval regression surface for the lane and exercises the canonical retrieval contract.
- Approved metadata-only exception: `THREAD_PACKET.md`, `.codex/kickoff_packets/feat-retrieval-fts.md`, `.codex/lane_meta/feat-retrieval-fts.json`, `codex_packet_handoff/tools/planner.py`, and `tests/unit/test_packet_planner.py` are handoff alignment artifacts and packet-planner coordination artifacts used only to keep reviewed-head packet emission aligned with the reviewed retrieval range.

## Files changed

### Reviewed implementation files

These are the exact source files changed across the reviewed cumulative range `1d6057e9..6afe533d735811f245a4d04322735935a09d2477`.

- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/embeddings_strategy.py`
- `src/qual/engine/retrieval/pageindex_strategy.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/__init__.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py` (approved shared regression coverage)

### Docs-only alignment files

These files were changed only in metadata-only alignment commits and are not part of the reviewed retrieval implementation diff.

- `THREAD_PACKET.md`
- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`

### Approved metadata-only alignment artifacts

These files are included only under the explicit metadata-only exception above and are not lane-owned retrieval implementation files.

- `codex_packet_handoff/tools/planner.py` (approved metadata-only alignment artifact)
- `tests/unit/test_packet_planner.py` (approved metadata-only alignment artifact)

## Tasks completed

1. Added FTS provenance retrieval bundles and retrieval service support for deterministic excerpt/provenance output.
2. Canonicalized excerpt provenance so downstream payloads carry stable hashes and fingerprints.
3. Kept retrieval FTS-first, hardened FTS cache isolation, normalized retrieval constraints and query inputs through the public facades, and left PageIndex/embeddings fallback-only plumbing that fails closed.
4. Exported the canonical retrieval query constructor through both retrieval facades and hardened query normalization.
5. Added source bundle context regression coverage and deterministic rehydration helpers for sparse source and context bundles.
6. Tightened retrieval hit snapshots to carry the canonical `retrieval_source_strategy` alias, list-like provenance fields, and downstream `source_strategy` attribution.
7. Added regression coverage for the normalized payload snapshots, facade exports, citation/provenance helpers, and sparse context backfill path.
8. Canonicalized payload bundle snapshots for deterministic downstream rehydration, including source-bundle fallbacks, source-bundle-only downstream payload reconstruction, sparse context backfill, and direct doc/excerpt/context bundle helper normalization.

## Budget alignment

- The thread finished within the low-risk cap of 8 tasks.
- The reviewed range includes the approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Metadata-only handoff artifacts were updated under the approved exception note; no other shared or integrator-locked files were edited outside the approved `tests/unit/test_unified_retrieval.py` regression coverage.
- The reviewed range is cumulative; docs-only alignment commits in the range only adjust handoff artifacts or packet-planner coordination artifacts, and the retrieval commits from `c92025af` through `6afe533d735811f245a4d04322735935a09d2477` stay inside the FTS-first retrieval lane.

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
- Constraint inputs remain mapping/dataclass-shaped, and iterable `doc_types`/`date_range` values are normalized deterministically by the public retrieval helpers.

## Scope-check / ownership note

- Shared/integrator-locked edits: `YES` (approved `tests/unit/test_unified_retrieval.py` regression coverage only; approved metadata-only alignment artifacts are listed above and were touched only to keep reviewed-head packet emission aligned with the reviewed retrieval range).
