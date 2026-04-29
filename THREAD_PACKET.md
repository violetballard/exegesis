## Thread Handoff Packet

- Branch/lane: `codex/feat-retrieval-fts` / `feat-retrieval-fts`
- Purpose: authoritative re-review packet for the actual branch-tip merge candidate.
- Reviewed range: `378cf9a7..HEAD`
- Reviewed implementation range: `378cf9a7..HEAD`
- Pre-fix rejected branch tip: `289f571e6`
- Merge candidate: current branch tip after this fixer pass. Final SHA is reported in the fixer response.
- Scope rule: review the full range above. Do not use `adfa8cdadd43747ffbcb612e4151e262b13e52ca` as the endpoint, and do not classify post-`adfa8cdadd43747ffbcb612e4151e262b13e52ca` retrieval-code changes as metadata-only.

## Required Fixes Addressed

Scope is regenerated against one source of truth, `378cf9a7..HEAD`; all post-`adfa8cdadd43747ffbcb612e4151e262b13e52ca` implementation changes are in scope; files, size budget, and gates are recalculated for the branch-tip merge candidate; canonical demo-path step advanced is `retrieve relevant material`; `.codex` packet mirrors remain sandbox-blocked because `touch .codex/.write_test` fails with `Operation not permitted`.

## Scope Completed

The branch delivers the FTS-first retrieval slice for the current MVP engine workflow loop: SQLite FTS is authoritative, PageIndex/embeddings remain deferred fallback shims, canonical excerpt lookup fails closed for PageIndex-only IDs, payloads are deterministic, and document/excerpt/provenance refs are stable for basket and workflow promotion.

## Tasks Completed

1. FTS-first retrieval contract: canonical SQLite FTS retrieval, fallback-only PageIndex behavior, document-update cache invalidation, and FTS-only excerpt lookup.
2. Deterministic payloads: normalized constraints, source/context bundles, provenance/citation backfills, cache keys, and hit snapshots.
3. Basket/workflow promotion readiness: stable refs, promotion candidates, fingerprints, ranked IDs, context status, and audit fields.
4. Regression and packet coverage: shared canonical retrieval coverage plus corrected branch-tip packet metadata.

## Post-`adfa8cd` Retrieval Changes In Scope

- `src/qual/engine/retrieval/fts_strategy.py`: adds one-slot cache invalidation and deep-copies fresh runner hits before returning/caching them.
- `src/qual/engine/retrieval/payload.py`: normalizes basket promotion refs across payload snapshots, backfills missing primary provenance from citations, and exposes `retrieval_basket_promotion_refs`.
- `src/qual/retrieval/service.py`: clears the FTS cache after document upserts, computes result fingerprints before evidence construction, and emits stable doc/excerpt promotion refs.

## Non-Retrieval Tooling / Test Scope

No `codex_packet_handoff/tools/planner.py` or `tests/unit/test_packet_planner.py` changes are part of this merge candidate. They are not metadata-only files, they are not listed as metadata-only handoff files, and they are outside the reviewed range diff for `378cf9a7..HEAD`.

## Files Changed

`.codex/kickoff_packets/feat-retrieval-fts.md`, `.codex/lane_meta/feat-retrieval-fts.json`, `THREAD_PACKET.md`, `src/qual/engine/retrieval/fts_strategy.py`, `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`.

## Budget

- Risk: high/shared because `tests/unit/test_unified_retrieval.py` is approved shared regression coverage.
- Task budget: `4/4`.
- File budget: `7/8`.
- Size budget after this fixer pass: `7` files, `443` insertions, `143` deletions, net `+300` in `378cf9a7..HEAD`; at the high-risk `<=300` net LOC cap.
- Integrator-locked files: none.

## Roadmap / Vision

Current MVP focus: engine stability, FTS-first retrieval, and A2UI contracts with CLI fallback. This advances Product Vision capabilities 2 and 3; routing/provider/UI impact is none.

## Canonical Demo Path

- Explicit AGENTS.md canonical demo-path step advanced: `retrieve relevant material`.
- Task mapping: task 1 makes retrieval FTS-first and fail-closed; task 2 makes retrieved material deterministic for engine context; task 3 makes retrieved material promotable into basket/workflow state; task 4 locks behavior with regression coverage and corrected metadata.
- Advances `vault -> context -> run -> patch -> export` by making the `context -> run` retrieval handoff deterministic, structured, FTS-backed, and provenance-bearing.

## Commands Run

Fresh fixer pass on the corrected branch-tip merge candidate: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh` (`124` tests), `./typecheck-test.sh`, and `make ci` (`124` tests): PASS.

## Risks / Blockers

- Merge risk remains high because the reviewed range includes approved shared regression coverage.
- Packet mirror blocker: `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` remain stale because this sandbox rejects `.codex` writes; both tracked files carry `com.apple.provenance`.
- `THREAD_PACKET.md` is the corrected writable source of truth for re-review: range `378cf9a7..HEAD`, post-`adfa8cdadd43747ffbcb612e4151e262b13e52ca` retrieval code in scope, high-risk/shared under the 4-task cap.
