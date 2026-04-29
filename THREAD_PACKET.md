## Thread Handoff Packet

- Branch/lane: `codex/feat-retrieval-fts` / `feat-retrieval-fts`
- Purpose: authoritative re-review packet for the actual branch-tip merge candidate.
- Reviewed range: `378cf9a7..HEAD`
- Merge candidate: current `HEAD` after this packet-fixer commit; final SHA is reported by the fixer.
- Scope rule: review the full range above. Do not use `adfa8cdadd43747ffbcb612e4151e262b13e52ca` as the endpoint, and do not call post-`adfa8cdadd43747ffbcb612e4151e262b13e52ca` retrieval-code commits metadata-only.
- Mirror blocker: this sandbox rejects writes to `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json`; this file is the corrected source of truth.

## Required Fixes

1. Handoff is regenerated against one source of truth: `378cf9a7..HEAD`.
2. Runtime/test files in that range are listed below and included in review scope.
3. Budget numbers are recomputed from the actual branch-tip range. This packet trim brings the expected final net LOC below the high-risk `<=300` limit.
4. Required gates are re-run against the corrected branch-tip merge candidate.
5. Roadmap/vision mapping is limited to Milestone 3 FTS-first retrieval, basket promotion, and downstream engine use.

## Scope And Tasks

The branch keeps SQLite FTS as the MVP retrieval authority, removes PageIndex fallback from canonical excerpt lookup, preserves deterministic retrieval payloads for downstream engine flows, and exposes stable document/excerpt refs for basket promotion.

1. FTS-first retrieval contract: canonical SQLite FTS retrieval, fallback-only PageIndex behavior, and FTS-only excerpt lookup.
2. Deterministic retrieval payloads: normalized query constraints, source/context bundles, provenance/citation backfills, cache keys, and hit snapshots.
3. Basket promotion and audit refs: stable doc/excerpt promotion refs, promotion candidates, fingerprints, ranked IDs, context status, and audit fields.
4. Regression and packet coverage: approved shared coverage plus packet metadata that states the full branch-tip review scope.

## Files Changed

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

Runtime/test files:

- `src/qual/engine/retrieval/fts_strategy.py`: FTS behavior alignment for deterministic retrieval.
- `src/qual/engine/retrieval/payload.py`: retrieval payload, provenance, context bundle, and promotion metadata normalization.
- `src/qual/retrieval/service.py`: FTS-first service behavior, FTS-only excerpt lookup, and stable facade outputs.
- `tests/unit/test_unified_retrieval.py`: approved shared regression coverage for the canonical retrieval contract.

## Budget

- Risk: high/shared because `tests/unit/test_unified_retrieval.py` is approved shared regression coverage.
- Task budget: `4/4`.
- File budget before this fixer commit: `7/8`.
- Size before this fixer commit: 451 insertions, 127 deletions, net `+324`.
- Runtime/test subset before this fixer commit: 195 insertions, 43 deletions, net `+152`.
- Final reviewed size after this packet trim: 428 insertions, 130 deletions, net `+298`.
- Integrator-locked files: none.

## Roadmap / Vision

- Roadmap: `ROADMAP.md` Milestone 3 FTS-first retrieval, basket promotion, and downstream engine context use.
- Vision: retrieval-first context handling, auditable generation, and A2UI-compatible stable retrieval payloads.
- Routing/provider/UI/alternate retrieval impact: none; PageIndex and embeddings remain deferred/fallback-only.

## Commands Run

- `make scope-check`: PASS.
- `./quality-format.sh --check`: PASS.
- `./quality-lint.sh`: PASS.
- `./quality-test.sh`: PASS.
- `./typecheck-test.sh`: PASS.
- `make ci`: PASS.

## Risks / Blockers

- Merge risk remains high because the actual range includes approved shared regression coverage.
- The `.codex` mirror files remain stale because writes are sandbox-blocked; use this packet as authoritative.
- Final HEAD SHA is reported by the fixer after commit creation.
