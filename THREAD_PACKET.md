## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Handoff type: high-risk retrieval handoff for the FTS-first retrieval lane.
- Canonical demo-path step advanced before handoff: `retrieve relevant material`; deterministic payload/provenance output also strengthens `promote or gather context into the basket`.
- Risk reason: approved shared regression surface `tests/unit/test_unified_retrieval.py`.
- Lane-owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`.
- Approved shared regression path: `tests/unit/test_unified_retrieval.py`.
- Integrator-locked files changed: none.
- Authoritative reviewed implementation base: `378cf9a74a3658058079a32f186fcd254c4a4034`.
- Reviewed implementation head: `51ee03de162297cce0dfafb2435fb33a7189807d`.
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..51ee03de162297cce0dfafb2435fb33a7189807d`.
- Current packet refresh head before this fixer edit: `c3a393e8a2f74d0d579d76dd9d144bb19ca71254`.
- Current packet refresh role: packet-only traceability update after the source-bearing basket-promotion normalizer fix.

## Traceability Correction

This packet supersedes earlier handoffs that described `adfa8cdadd43747ffbcb612e4151e262b13e52ca` as the final reviewed implementation head or described later source/test-changing commits as metadata-only.

The actual source-bearing merge candidate for this branch is:

`378cf9a74a3658058079a32f186fcd254c4a4034..51ee03de162297cce0dfafb2435fb33a7189807d`

That range includes every intended retrieval source/test change through `51ee03de162297cce0dfafb2435fb33a7189807d`, including the reviewer-cited post-`adfa8cdadd43747ffbcb612e4151e262b13e52ca` changes in `src/qual/engine/retrieval/__init__.py`, `src/qual/engine/retrieval/fts_strategy.py`, `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/__init__.py`, `src/qual/retrieval/service.py`, and `tests/unit/test_unified_retrieval.py`.

`beed411ecb15821f0cf145bd3ad68d59c996801c` is source-bearing. It modifies `src/qual/engine/retrieval/__init__.py`, `src/qual/retrieval/service.py`, and `THREAD_PACKET.md`. It must not be treated as metadata-only.

`51ee03de162297cce0dfafb2435fb33a7189807d` is also source-bearing. It modifies `src/qual/engine/retrieval/payload.py` so basket-promotion item rehydration normalizes item-level `query_date_range` and `matched_terms` values before promotion-item fingerprinting.

Packet-only commits after `51ee03de162297cce0dfafb2435fb33a7189807d` refresh traceability and gate evidence only.

Re-review should not use `adfa8cdadd43747ffbcb612e4151e262b13e52ca` as the implementation head. It is an intermediate implementation commit only.

## Files Changed

Source and shared regression implementation surface in the corrected source-bearing range:

- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/__init__.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

Packet/artifact surface in the corrected source-bearing range:

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`

Packet-only refresh surface after the reviewed implementation head:

- `THREAD_PACKET.md`

## Scope Completed

SQLite FTS remains the required MVP retrieval path. PageIndex and embeddings remain deferred or compatibility-only fallback surfaces and are not reintroduced as required paths.

The branch makes FTS retrieval deterministic and auditable across query construction, cache keys, fresh-run cache snapshots, query snapshots, result payloads, excerpt lookup, citation/provenance bundles, sparse source/context bundle rehydration, date-range propagation, shortlist query fingerprints, matched-term provenance, result fingerprints, doc identity, doc rank, doc type, strategy aliases, query constraints, retrieval manifest fingerprints, and basket-promotion evidence. The final source-bearing pass additionally normalizes rehydrated basket-promotion item date ranges and matched-term lists before item fingerprinting.

The corrected branch-tip implementation also tightens the canonical engine and service query normalization paths so malformed, unordered, or scalar-shaped `date_range` inputs fail closed before FTS execution.

Canonical demo path advanced: `vault/context material -> FTS retrieval -> retrieval evidence -> context basket promotion -> engine revise/apply`.

Before-handoff canonical demo-path statement: this work advances `retrieve relevant material` by keeping retrieval FTS-first, deterministic, and auditable; it also supports `promote or gather context into the basket` by preserving provenance and query evidence on promotion bundles/items.

## Tasks Completed

1. Canonical demo-path step advanced: `retrieve relevant material`. Made SQLite FTS the authoritative MVP retrieval path while keeping PageIndex and embeddings fallback-only/deferred.
2. Canonical demo-path step advanced: `retrieve relevant material`. Stabilized FTS query, cache, constraint, date-range, shortlist, doc-type, scope, and fresh-run behavior for deterministic retrieval.
3. Canonical demo-path steps advanced: `retrieve relevant material` and `promote or gather context into the basket`. Normalized retrieval payloads, provenance, citation/source/context bundles, evidence snapshots, sparse bundle rehydration, retrieval manifest fingerprints, and basket-promotion evidence, including item-level date-range and matched-term normalization before basket-promotion fingerprinting.
4. Canonical demo-path steps advanced: `retrieve relevant material` and `promote or gather context into the basket`. Added fail-closed and audit-focused regression coverage for malformed/reversed date ranges, empty inputs, unresolved scopes, FTS-only excerpt lookup and payload normalization, excerpt lookup fingerprints, cache/query snapshots, facade/export availability, and basket-promotion fingerprint propagation.

Task accounting: `4` high-risk task groups completed, matching the high-risk task cap.

## Kickoff Budget/Limits Compliance

- Task budget: `4` high-risk task groups; completed as the four groups above.
- File count: the corrected source-bearing range changes `6` source/test files plus `3` packet/artifact files.
- Size accounting: the corrected source-bearing range `378cf9a74a3658058079a32f186fcd254c4a4034..51ee03de162297cce0dfafb2435fb33a7189807d` is `9 files changed, 1384 insertions(+), 211 deletions(-)`. The source/test-only surface is `6 files changed, 1284 insertions(+), 81 deletions(-)`.
- Size limit status: exceeds the high-risk `<=8 files` and `<=300 net LOC` limits.
- Explicit exception status: no integrator-approved size exception is recorded in this worktree. Because the full source-bearing range remains together, this is a known blocker for approval until the integrator grants an exception or requests a branch split.
- Shared-file exception status: `tests/unit/test_unified_retrieval.py` is the sole approved shared regression surface; no integrator-locked files changed.
- Routing/provider impact: none.

## Required Fixes Applied

1. Regenerated this review packet with the real source-bearing implementation head: `51ee03de162297cce0dfafb2435fb33a7189807d`.
2. Removed the stale metadata-only framing for `beed411ecb15821f0cf145bd3ad68d59c996801c`; it is explicitly identified as source-bearing.
3. Updated the reviewed implementation range to include all intended source/test changes in the branch-tip source-bearing candidate.
4. Updated files changed, task accounting, command outcomes, risks, and roadmap/vision mapping to match the corrected range.
5. Documented that no explicit integrator-approved size exception is present for the high-risk size overage.

## Commands Run

Required gates for this corrected merge candidate were re-run on 2026-05-07 against branch `codex/feat-retrieval-fts`.

- `make scope-check` - passed for branch `codex/feat-retrieval-fts`.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - passed smoke tests and 132 unit tests.
- `./typecheck-test.sh` - passed Python source compilation under `src/`.
- `make ci` - passed setup, scope-check, format, lint, compile/typecheck, smoke tests, and 132 unit tests.

Additional focused retrieval checks run earlier in this lane:

- `python3 -m unittest tests.unit.test_unified_retrieval -k basket_promotion` - passed 2 focused basket-promotion tests after the final source-bearing basket item normalization fix.
- `python3 -m unittest tests.unit.test_unified_retrieval` - passed after unordered date-range containers were rejected in facade/service normalization.
- `python3 - <<'PY' ... build_retrieval_query(...) ... RetrievalConstraints(...) ... PY` - passed; unordered set-shaped date ranges fail closed in both the engine facade and service constraints, scalar string date ranges remain rejected, and ordered list-shaped date ranges still normalize to the canonical tuple.
- `python -m pytest tests/unit/test_unified_retrieval.py` - blocked because the active Python interpreter had no `pytest` module installed.

## Remaining Risks Or Blockers

- The corrected cumulative source-bearing range exceeds the high-risk size/file limits. No explicit integrator-approved size exception is present in the worktree.
- All source-bearing work is now included in the reviewed implementation range; there is no longer a metadata-only branch-tip claim hiding source/test changes after `adfa8cdadd43747ffbcb612e4151e262b13e52ca`.

## Roadmap/Vision

- Roadmap items affected: `ROADMAP.md` Milestone 3 Product Readiness generation provenance and Milestone 4 Retrieval Layer FTS-first retrieval orchestration/source attribution.
- Product Vision capabilities affected: `2. Retrieval-first context handling` and `3. Auditable generation`.
- Architecture alignment: retrieval stays in `src/qual/retrieval/**` and `src/qual/engine/retrieval/**`; no provider/routing/core app entrypoints are touched.
- Routing/provider impact: none.
- Proposed `README.md` patch text: none.
