# Thread Handoff Packet

- Lane: `feat-retrieval-fts`
- Branch: `codex/feat-retrieval-fts`
- Prior reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation head: `22a56fce70167ddd4c7708fd4a1ee18fad7b8ffe`
- Packet refresh role: `reviewer-fix handoff regeneration`
- Reviewed implementation range: `adfa8cdadd43747ffbcb612e4151e262b13e52ca..22a56fce70167ddd4c7708fd4a1ee18fad7b8ffe`

## Packet traceability note

- The prior packet was incorrect: branch tip `22a56fce70167ddd4c7708fd4a1ee18fad7b8ffe` is not metadata-only.
- This re-review packet intentionally covers the cumulative post-`adfa8cdadd` runtime, test, and packet/tooling changes now present at branch tip.
- The reviewer should read the runtime/test scope against the reviewed implementation range above, not against an older narrowed excerpt-only description.
- Within that range, `22a56fce70167ddd4c7708fd4a1ee18fad7b8ffe` changes the public engine retrieval surface by exporting the canonical query dataclasses, and earlier commits in the same range add `retrieve_fts_provenance_bundle`, `retrieve_auto_provenance_bundle`, `fetch_fts_excerpt`, FTS-only strategy enforcement, and the matching regression coverage.

## Current program focus

- Keep the engine-first MVP on the canonical FTS-first retrieval path before any later UI work.

## Scope goal

- Tighten the post-`adfa8cdadd` retrieval lane follow-up so the engine-facing retrieval contract stays FTS-first, structured, and auditable for the `retrieve relevant material` step.

## Scope completed

- `fetch_excerpt` and the new `fetch_fts_excerpt` / `retrieve_auto_excerpt` aliases now resolve through the canonical FTS-backed lookup path, so PageIndex-only excerpt IDs fail closed while lookup audit payloads stay deterministic.
- Retrieval hit, doc-hit, citation, provenance, source-bundle, and basket-promotion payloads are normalized and copied defensively so downstream engine consumers receive structured, mutation-safe snapshots with stable fingerprints, ranked IDs, query context, and source-strategy metadata.
- The retrieval service and engine retrieval facade now expose the provenance/source/doc/excerpt bundle helpers plus the canonical `RetrievalConstraints` and `RetrievalQuery` types on the owned engine surface, giving engine callers one public FTS-first contract instead of ad hoc shim-only construction.
- FTS strategy helpers and related compatibility shims were tightened so cache keys, scope/query normalization, and strategy metadata remain deterministic while PageIndex and embeddings stay fallback-only and never become required paths.
- Shared regression coverage in `tests/unit/test_unified_retrieval.py` and packet/planner coverage in `tests/unit/test_packet_planner.py` were broadened to lock the payload, provenance, export, and handoff-trace behavior now included in this reviewed range.

## Canonical demo-path step advanced

- `retrieve relevant material`
- Canonical demo-path statement: This work makes `retrieve relevant material` more real by ensuring the engine loop reads one deterministic FTS-first retrieval contract, one deterministic excerpt lookup path, and one auditable provenance/source bundle shape.
- Basket-promotion statement: The normalized retrieval payload and provenance/source bundle work is what makes later basket promotion safe, because the engine now receives stable ranked IDs, source fingerprints, and strategy metadata instead of sparse or mutably aliased snapshots.

## Scope-tightening note

- `src/qual/retrieval/service.py`: the non-`fetch_excerpt` changes are in scope because they enforce FTS-only `source_strategy`, normalize excerpt/provenance/audit payloads, and keep basket-promotion fields aligned with the engine-facing retrieval result consumed by the canonical demo path.
- `src/qual/engine/retrieval/payload.py` and `src/qual/engine/retrieval/fts_strategy.py`: the added normalization, cache-key, and sparse-bundle rehydration work is in scope because Milestone 3 needs structured deterministic search results that can be promoted downstream without shape drift.
- `src/qual/retrieval/__init__.py` and `src/qual/engine/retrieval/__init__.py`: the provenance/export/helper additions remain in scope because this lane owns both retrieval facades, and the engine-first MVP needs one clean engine-facing contract for retrieval bundles and query construction.
- `tests/unit/test_unified_retrieval.py`: the broader shared regression coverage is the approved shared-by-approval surface that proves the exported helpers, normalized payloads, and FTS-only excerpt path all stay tied to the same demo-path contract.
- Packet/tooling files in this range are traceability work only; they do not expand product scope, but they are part of the reviewed branch-tip range and are listed explicitly below so the packet matches reality.

## Reviewer fix reconciliation

- The reviewed implementation range now matches the actual branch-tip scope under review: `adfa8cdadd43747ffbcb612e4151e262b13e52ca..22a56fce70167ddd4c7708fd4a1ee18fad7b8ffe`.
- `Scope completed`, `Tasks completed`, and `Files changed` now describe the real post-`adfa8cdadd` work, including provenance/export/helper additions and packet/tooling artifacts inside the same reviewed range.
- The packet now states exactly why each non-`fetch_excerpt` change remains in-plan for the canonical `retrieve relevant material` step instead of leaving the extra API surface unexplained.
- The traceability note now explicitly says `22a56fce70167ddd4c7708fd4a1ee18fad7b8ffe` contains runtime code and shared regression updates.

## Kickoff budget/limits compliance

- This handoff includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, so the packet is shared/high-risk work and should be read against the 4-task cap.
- The reviewed runtime/test implementation remains inside lane-owned retrieval paths plus the approved shared regression file.
- Packet/tooling artifacts are listed separately from runtime/test implementation so review scope stays readable.

## Approved exception note

- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for the `feat-retrieval-fts` lane; it is the sole shared-by-approval regression surface for the lane and exercises the canonical retrieval contract.

## Tasks completed (numbered)

1. Kept excerpt lookup on the canonical FTS-only path and added the engine-facing excerpt helper aliases and audit normalization needed for fail-closed lookup behavior.
2. Normalized retrieval payload, provenance, source-bundle, and basket-promotion snapshots so the engine loop receives deterministic structured search results suitable for basket promotion.
3. Exposed the owned engine/retrieval facade helpers and canonical query dataclasses needed for one clean engine-facing retrieval contract, while enforcing FTS-only strategy behavior.
4. Regenerated packet/planner traceability and expanded regression coverage so the reviewed branch-tip range, exported helpers, and demo-path mapping are all locked to the actual implementation under review.

## Files changed

### Runtime and test implementation in the reviewed range

- `src/qual/retrieval/service.py`
- `src/qual/retrieval/__init__.py`
- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/embeddings_strategy.py`
- `src/qual/engine/retrieval/pageindex_strategy.py`
- `src/qual/engine/retrieval/interface.py`
- `tests/unit/test_unified_retrieval.py`

### Packet and tooling artifacts also present in the reviewed branch-tip range

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`
- `docs/gate_passed.txt`
- `docs/retrieval_post_adfa_commit_accounting.md`
- `codex_packet_handoff/tools/init_lane_meta.py`
- `codex_packet_handoff/tools/planner.py`
- `tests/unit/test_packet_planner.py`

## Commands run and outcomes

- `python -m unittest tests.unit.test_unified_retrieval -q`: PASS
- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

## Risks / blockers

- Residual risk: the owned engine retrieval facade now carries more canonical helpers, so future retrieval changes must keep facade exports, payload normalization, and shared regression coverage aligned.
- Residual risk: packet/planner artifacts are still numerous in this lane history, so later handoff refreshes should avoid restating the scope as a narrower slice than the reviewed range actually contains.
- Blockers: none

## Required handoff fields

### Roadmap item(s) affected

- `ROADMAP.md`: Milestone 3: Real workflow loop
- `ROADMAP.md`: Milestone 4: Retrieval Layer
- `feat-retrieval-fts`: authoritative FTS-first retrieval feeding the engine loop

### Vision capability affected

- Retrieval-first context handling
- Auditable state and workflow

### Routing/provider impact note

- None

## Scope-check / ownership note

- Shared/integrator-locked edits: `YES`
