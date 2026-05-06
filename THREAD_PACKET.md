## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Handoff type: corrected high-risk retrieval handoff for the FTS-first retrieval lane.
- Reviewed implementation base: `378cf9a74a3658058079a32f186fcd254c4a4034`.
- Reviewed implementation code head: `25f8d10c4b8f02c6d613af3300a5b7a02ec1c848`.
- Reviewed implementation range for re-review: `378cf9a74a3658058079a32f186fcd254c4a4034..25f8d10c4b8f02c6d613af3300a5b7a02ec1c848`.
- Packet refresh commit after this file is metadata-only; final branch HEAD SHA is reported in the fixer response.
- Scope classification: high-risk because this lane includes the approved shared regression surface `tests/unit/test_unified_retrieval.py`.
- Lane-owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`.
- Approved shared regression path: `tests/unit/test_unified_retrieval.py`.
- Integrator-locked files changed: none.

## Scope Completed

This corrected packet supersedes the stale narrow-range handoff and makes all production and test changes through `25f8d10c4b8f02c6d613af3300a5b7a02ec1c848` part of the reviewed implementation range.

The retrieval lane keeps SQLite FTS as the authoritative MVP retrieval path. The branch adds deterministic FTS cache handling and cache audit metadata, normalizes retrieval payload snapshots and query constraints, preserves retrieval provenance for basket/context promotion flows, keeps PageIndex and embeddings as deferred compatibility surfaces, and makes date-range constraints fail fast when malformed or reversed before FTS execution.

## Tasks Completed

1. Made SQLite FTS the primary retrieval path for document and excerpt retrieval, with PageIndex and embeddings retained as compatibility-only fallback/deferred surfaces.
2. Stabilized FTS retrieval cache behavior, including cache invalidation on document updates and cache audit metadata for payload/provenance consumers.
3. Normalized retrieval payloads, query snapshots, constraints, provenance fingerprints, source bundles, and basket/context promotion metadata for deterministic downstream engine use.
4. Validated date-range constraints at the canonical query and FTS retrieval boundaries so malformed or reversed filters fail fast instead of producing misleading empty evidence.
5. Added and maintained approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for FTS-first retrieval behavior, payload normalization, cache metadata, facade exports, citation/provenance helpers, excerpt lookup, and date-range validation.

## Files Changed

Reviewed implementation range for re-review: `378cf9a74a3658058079a32f186fcd254c4a4034..25f8d10c4b8f02c6d613af3300a5b7a02ec1c848`.

From `git diff --name-status 378cf9a74a3658058079a32f186fcd254c4a4034..25f8d10c4b8f02c6d613af3300a5b7a02ec1c848`:

- `M .codex/kickoff_packets/feat-retrieval-fts.md`
- `M .codex/lane_meta/feat-retrieval-fts.json`
- `M THREAD_PACKET.md`
- `M src/qual/engine/retrieval/fts_strategy.py`
- `M src/qual/engine/retrieval/payload.py`
- `M src/qual/retrieval/service.py`
- `M tests/unit/test_unified_retrieval.py`

From `git diff --stat 378cf9a74a3658058079a32f186fcd254c4a4034..25f8d10c4b8f02c6d613af3300a5b7a02ec1c848`:

- `.codex/kickoff_packets/feat-retrieval-fts.md` - 36 lines changed.
- `.codex/lane_meta/feat-retrieval-fts.json` - 155 lines changed.
- `THREAD_PACKET.md` - 115 lines changed.
- `src/qual/engine/retrieval/fts_strategy.py` - 6 lines changed.
- `src/qual/engine/retrieval/payload.py` - 27 lines changed.
- `src/qual/retrieval/service.py` - 53 lines changed.
- `tests/unit/test_unified_retrieval.py` - 96 lines changed.

## Budget/Risk

- Task budget: `4` high-risk task groups in the original thread, with this corrected packet summarizing the cumulative branch-level retrieval work as five traceability items.
- File count for reviewed implementation handoff: `7 files changed`.
- Size accounting: `367 insertions(+), 121 deletions(-)`; net `246` LOC.
- AGENTS file/size status: fits high-risk size limits of `<=8 files` and `<=300 net LOC`.
- Shared/integrator exception status: uses the approved shared regression surface `tests/unit/test_unified_retrieval.py`; no integrator-locked files changed.
- Routing/provider impact: none.
- PageIndex/embeddings impact: no PageIndex, embeddings, hybrid, or alternate retrieval path was added as a required MVP path.
- Remaining risks/blockers: none.

## Traceability Correction

The earlier packet incorrectly claimed commits after `adfa8cdadd43747ffbcb612e4151e262b13e52ca` were metadata-only. That claim is withdrawn. Commits including `1696a088d`, `d31c231e`, `9792d439`, and `25f8d10c4` are code-bearing retrieval/test commits and are included in the corrected reviewed implementation range.

This handoff has one authoritative reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..25f8d10c4b8f02c6d613af3300a5b7a02ec1c848`.

## Roadmap/Vision

- Roadmap items affected: `ROADMAP.md` Milestone 4 FTS-first retrieval orchestration/source-attribution/auditable deterministic retrieval; Milestone 3 generation provenance contract clarity for retrieved evidence.
- Vision capability affected: retrieval-backed context, retrieval-first context handling, auditable outputs, and deterministic operator controls.
- Architecture alignment: FTS remains the required local retrieval path. PageIndex and embeddings stay compatibility-only/deferred.
- Canonical demo-path mapping: advances `retrieve relevant material` and supports `promote or gather context into the basket` by preventing invalid date filters from producing misleading empty retrieval evidence.
- Routing/provider impact note: none.
- Proposed `README.md` patch text: none.

## Commands Run

Commands run for this corrected packet on the branch-tip worktree state:

- `make scope-check` - passed.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - passed smoke tests and 127 unit tests.
- `./typecheck-test.sh` - passed Python source compilation under `src/`.
- `make ci` - passed setup, scope-check, format, lint, compile/typecheck, smoke tests, and 127 unit tests.
