## Thread Handoff Packet

- Branch/lane: `codex/feat-retrieval-fts` / `feat-retrieval-fts`
- Merge candidate: current branch tip after this fixer pass.
- Reviewed range: `378cf9a7..HEAD`
- Reviewed implementation range: `378cf9a7..HEAD`
- Review choice: review branch tip, not the narrowed `adfa8cdadd43747ffbcb612e4151e262b13e52ca` slice.
- Pre-fix rejected branch tip: `289f571e6`
- Pre-fix reviewer-cited branch tip: `f69a8c15127dd48a6cb327b0ac3ee94b33c82d06`

## Required Fixes Addressed

1. The merge candidate is branch tip. The packet no longer presents `adfa8cdadd43747ffbcb612e4151e262b13e52ca` as the implementation endpoint.
2. The reviewed implementation range covers all branch-tip code changes after `adfa8cdadd43747ffbcb612e4151e262b13e52ca`, including `src/qual/engine/retrieval/fts_strategy.py`, `src/qual/engine/retrieval/payload.py`, and `src/qual/retrieval/service.py`.
3. Tasks, files, risk, and budget are recomputed for `378cf9a7..HEAD`.
4. Required gates are rerun on the exact branch-tip candidate and recorded below.
5. Canonical demo-path impact is stated explicitly.

## Scope Completed

The branch delivers the FTS-first retrieval slice for the MVP engine workflow loop: SQLite FTS is authoritative, PageIndex and embeddings remain fallback shims, canonical excerpt lookup fails closed for unsupported IDs, FTS cache state is invalidated after document writes, payload snapshots are deterministic, and retrieved doc/excerpt/provenance refs are stable for basket and workflow promotion.

## Tasks Completed

1. FTS-first retrieval contract: canonical SQLite FTS retrieval, fallback-only PageIndex behavior, document-update cache invalidation, and FTS-only excerpt lookup.
2. Deterministic payloads: normalized constraints, source/context bundles, provenance/citation backfills, cache keys, and hit snapshots.
3. Basket/workflow promotion readiness: stable refs, promotion candidates, fingerprints, ranked IDs, context status, and audit fields.
4. Regression and handoff coverage: shared canonical retrieval coverage plus corrected branch-tip packet metadata.

## Branch-Tip Retrieval Changes In Scope

- `src/qual/engine/retrieval/fts_strategy.py`: cache isolation and copied hit snapshots.
- `src/qual/engine/retrieval/payload.py`: deterministic payload normalization, provenance backfills, and basket promotion refs.
- `src/qual/retrieval/service.py`: cache invalidation after document updates, stable fingerprints, and doc/excerpt promotion refs.
- `tests/unit/test_unified_retrieval.py`: approved shared regression coverage for the canonical retrieval contract.

## Files Changed

`.codex/kickoff_packets/feat-retrieval-fts.md`, `.codex/lane_meta/feat-retrieval-fts.json`, `THREAD_PACKET.md`, `src/qual/engine/retrieval/fts_strategy.py`, `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`.

## Budget / Risk

- Risk: high/shared because `tests/unit/test_unified_retrieval.py` is approved shared regression coverage.
- Task budget: `4/4`.
- File budget: `7/8`.
- Size budget: `7` files, `438` insertions, `143` deletions, net `+295` in `378cf9a7..HEAD`; within the high-risk `<=300` net LOC cap.
- Integrator-locked files: none.

## Canonical Demo Path

The final reviewed work makes `retrieve relevant material` and `promote/gather context into the basket` more real by making retrieved context deterministic, FTS-backed, provenance-bearing, and promotable into workflow state.

## Commands Run

Fresh fixer pass on the branch-tip merge candidate: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh` (`124` tests), `./typecheck-test.sh`, and `make ci` (`124` tests): PASS.

## Risks / Blockers

- Merge risk remains high because the branch-tip reviewed range includes shared regression coverage.
- The branch-tip range includes retrieval implementation after `adfa8cdadd43747ffbcb612e4151e262b13e52ca`; reviewers should evaluate `378cf9a7..HEAD` as the merge candidate.
- Packet mirror blocker: `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` still carry stale `adfa8cdadd43747ffbcb612e4151e262b13e52ca` packet text because this sandbox rejects writes to those protected `.codex` files (`com.apple.provenance`, `Operation not permitted`).
