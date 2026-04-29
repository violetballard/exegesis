# Thread Handoff Packet

- Lane: `feat-retrieval-fts`
- Branch: `codex/feat-retrieval-fts`
- Reviewed base: `d7fd5d200358287fa42a18d39e2b277463b9b69f`
- Reviewed tip: current branch tip after this fixer commit; final SHA is reported in the fixer handoff.
- Reviewed implementation range: `d7fd5d200358287fa42a18d39e2b277463b9b69f..HEAD`
- Handoff type: branch-tip re-review packet for the full `feat-retrieval-fts` state.

## Scope Goal

Complete the FTS-first retrieval MVP for engine flows with deterministic query, hit, provenance, excerpt, and basket-promotion payloads while keeping PageIndex and embeddings out of the required MVP retrieval path.

## Scope Completed

The full branch-tip diff keeps SQLite FTS as the authoritative retrieval path. It exports canonical retrieval query and helper surfaces through both retrieval facades, hardens FTS strategy validation and cache normalization, adds compatibility-only PageIndex and embeddings shims that fail closed, normalizes retrieval payload/provenance/source/context/basket snapshots, and makes excerpt lookup resolve through FTS-only evidence. Shared regression coverage in `tests/unit/test_unified_retrieval.py` verifies FTS-first diagnostics, deterministic snapshots, fail-closed non-FTS hits, FTS-only excerpt lookup, and deferred PageIndex/embeddings behavior.

## Canonical Demo-Path Step Advanced

- Step: `retrieve relevant material`
- This branch makes that step more real by turning retrieved material into deterministic FTS-derived evidence bundles that downstream basket promotion can consume without depending on PageIndex or embeddings.
- No PageIndex or embeddings path is required for the MVP retrieval contract: FTS is the only active strategy, PageIndex and embeddings are deferred compatibility shims, and tests assert non-FTS/source-strategy inputs fail closed.

## Budget And Ownership

- Risk: `HIGH`
- High-risk reason: the branch includes shared regression coverage in `tests/unit/test_unified_retrieval.py` and broad retrieval facade/payload changes.
- Task budget: read as 4 high-risk tasks.
- Size accounting for the final branch-tip diff: 12 files changed, 12,797 insertions, 902 deletions.
- Owned runtime paths touched: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`.
- Approved shared-by-approval edit: `tests/unit/test_unified_retrieval.py`, used only for retrieval contract regression coverage.
- Handoff metadata artifacts touched: `.codex/kickoff_packets/feat-retrieval-fts.md`, `.codex/lane_meta/feat-retrieval-fts.json`, `THREAD_PACKET.md`.
- Integrator-locked files touched: none.
- Removed from the final branch-tip diff: `codex_packet_handoff/tools/init_lane_meta.py`, `codex_packet_handoff/tools/planner.py`, `docs/gate_passed.txt`, `docs/retrieval_post_adfa_commit_accounting.md`, and `tests/unit/test_packet_planner.py`.

## Tasks Completed

1. Kept retrieval FTS-first by making `retrieve_auto` and `retrieve_fts` share canonical query normalization, active strategy reporting, FTS-only hit provenance, and fail-closed unsupported scopes.
2. Stabilized engine retrieval strategy behavior by validating canonical FTS query payloads, normalizing cache keys and candidate doc IDs, isolating cached hit snapshots, and leaving PageIndex/embeddings as importable deferred shims.
3. Normalized retrieval payloads for downstream engine flows, including source bundles, context bundles, citation/provenance bundles, basket-promotion snapshots, fingerprints, date ranges, ranked IDs, and sparse backfill/reconstruction paths.
4. Added approved shared regression coverage for the full FTS-first retrieval contract, including facade exports, payload determinism, FTS-only excerpt lookup, failed lookup audit shape, basket-promotion evidence, and fail-closed non-FTS strategy inputs.

## Complete Files Changed

```text
.codex/kickoff_packets/feat-retrieval-fts.md
.codex/lane_meta/feat-retrieval-fts.json
THREAD_PACKET.md
src/qual/engine/retrieval/__init__.py
src/qual/engine/retrieval/embeddings_strategy.py
src/qual/engine/retrieval/fts_strategy.py
src/qual/engine/retrieval/interface.py
src/qual/engine/retrieval/pageindex_strategy.py
src/qual/engine/retrieval/payload.py
src/qual/retrieval/__init__.py
src/qual/retrieval/service.py
tests/unit/test_unified_retrieval.py
```

## Diff Stat

```text
.codex/kickoff_packets/feat-retrieval-fts.md     |   55 +-
.codex/lane_meta/feat-retrieval-fts.json         |  162 +-
THREAD_PACKET.md                                 |  168 +-
src/qual/engine/retrieval/__init__.py            |  175 +-
src/qual/engine/retrieval/embeddings_strategy.py |   25 +
src/qual/engine/retrieval/fts_strategy.py        |  394 +-
src/qual/engine/retrieval/interface.py           |    2 +-
src/qual/engine/retrieval/pageindex_strategy.py  |   34 +
src/qual/engine/retrieval/payload.py             | 4114 ++++++++++++++++-
src/qual/retrieval/__init__.py                   |  330 +-
src/qual/retrieval/service.py                    | 3111 ++++++++++++-
tests/unit/test_unified_retrieval.py             | 5129 ++++++++++++++++++++--
12 files changed, 12797 insertions(+), 902 deletions(-)
```

## Commands Run And Outcomes

- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

## Roadmap Items Affected

- `ROADMAP.md`: Milestone 3 product-readiness work for generation provenance and the engine workflow loop.
- `ROADMAP.md`: MVP focus through 2026-05-04, specifically `feat-retrieval-fts`.

## Vision Capabilities Affected

- `PRODUCT_VISION.md`: retrieval-backed context, FTS-first for the current MVP.
- `PRODUCT_VISION.md`: Retrieval-first context handling.
- `PRODUCT_VISION.md`: Auditable state and workflow.

## Routing / Provider Impact

None. This branch changes retrieval behavior and payload normalization only; it does not touch model routing or provider configuration.

## Risks / Blockers

- Remaining risk: high review surface because the branch-tip diff is large and includes broad retrieval payload normalization.
- Blockers: none after non-owned tool/docs drift was removed from the final branch-tip diff.
