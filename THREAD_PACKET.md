## Thread Handoff Packet

- Branch/lane: `codex/feat-retrieval-fts` / `feat-retrieval-fts`
- Purpose: authoritative re-review packet for the actual branch-tip merge candidate.
- Reviewed range: `378cf9a7..HEAD`
- Merge candidate: current branch tip after this fixer commit. Final SHA is reported in the fixer response.
- Scope rule: review the full range above. Do not use `adfa8cdadd43747ffbcb612e4151e262b13e52ca` as the endpoint, and do not classify post-`adfa8cdadd43747ffbcb612e4151e262b13e52ca` retrieval-code changes as metadata-only.

## Required Fixes Addressed

1. The handoff is regenerated against one source of truth: `378cf9a7..HEAD`.
2. Runtime/test review scope includes `src/qual/engine/retrieval/fts_strategy.py`, `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`, and `tests/unit/test_unified_retrieval.py`, plus packet metadata files.
3. High-risk budget accounting is recomputed against the same actual branch-tip range.
4. Scope and task notes include FTS cache invalidation, FTS-first structured retrieval, basket/workflow promotion readiness, auditable provenance, and the canonical `context -> run` demo-path handoff.
5. Required gates are rerun against the corrected branch-tip merge candidate.

## Scope Completed

The branch delivers the FTS-first retrieval slice needed for the current MVP engine workflow loop. SQLite FTS stays the authoritative retrieval path, PageIndex and embeddings remain deferred/fallback-only, canonical excerpt lookup fails closed for PageIndex-only IDs, retrieval payloads are deterministic for downstream engine use, and stable document/excerpt/provenance refs are exposed for basket and workflow promotion.

## Tasks Completed

1. FTS-first retrieval contract: canonical SQLite FTS retrieval, fallback-only PageIndex behavior, FTS cache invalidation after document updates, and FTS-only excerpt lookup.
2. Deterministic structured payloads: normalized query constraints, source/context bundles, provenance/citation backfills, cache keys, and hit snapshots.
3. Basket/workflow promotion readiness: stable doc/excerpt refs, promotion candidates, fingerprints, ranked IDs, context status, and audit fields.
4. Regression and packet coverage: approved shared coverage for the canonical retrieval contract plus corrected packet metadata for the actual branch-tip review scope.

## Files Changed

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

## Budget

- Risk: high/shared because `tests/unit/test_unified_retrieval.py` is approved shared regression coverage.
- Task budget: `4/4`.
- File budget: `7/8`.
- Size budget: `7` files changed, 427 insertions, 130 deletions, net `+297` in `378cf9a7..HEAD` before the final commit SHA changes.
- Integrator-locked files: none.

## Roadmap / Vision

- Roadmap: current MVP engine-first plan for the Milestone 3 real workflow loop, with `feat-retrieval-fts` active in `ROADMAP.md` MVP focus and retrieval contracts feeding the canonical CLI/A2UI demo flow.
- Vision: Product Vision capabilities 2 and 3, retrieval-first context handling and auditable generation.
- Active MVP note: Engine stability, FTS-first retrieval, and A2UI contracts with CLI fallback.
- Routing/provider/UI/alternate retrieval impact: none; PageIndex and embeddings remain deferred/fallback-only.

## Canonical Demo Path

- Advances the canonical MVP flow `vault -> context -> run -> patch -> export` by making the `context -> run` retrieval handoff deterministic, structured, FTS-backed, and provenance-bearing.
- Keeps retrieved chunks auditable for generation and promotion flows through stable source, excerpt, provenance, and basket/workflow promotion refs.

## Commands Run

`make scope-check`: PASS. `./quality-format.sh --check`: PASS. `./quality-lint.sh`: PASS. `./quality-test.sh`: PASS (`124` tests). `./typecheck-test.sh`: PASS. `make ci`: PASS (`124` tests).

## Risks / Blockers

- Merge risk remains high because the actual reviewed range includes approved shared regression coverage.
- `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` are included in the reviewed range, but this sandbox rejects writes to those `.codex` paths with `Operation not permitted`; `THREAD_PACKET.md` is the corrected source of truth for re-review.
