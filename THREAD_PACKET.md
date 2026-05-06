## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Handoff type: high-risk retrieval handoff finalization for the FTS-first retrieval lane.
- Reviewed implementation base: `378cf9a74a3658058079a32f186fcd254c4a4034`.
- Reviewed implementation code head: final fixer commit SHA reported in the fixer response.
- Reviewed implementation range for re-review: `378cf9a74a3658058079a32f186fcd254c4a4034..FINAL_FIXER_HEAD_REPORTED_IN_RESPONSE`.
- Final fixer HEAD SHA is reported in the fixer response because the packet cannot self-record its own commit SHA before commit creation.
- Scope classification: high-risk because this lane includes the approved shared regression surface `tests/unit/test_unified_retrieval.py`.
- Lane-owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`.
- Approved shared regression path: `tests/unit/test_unified_retrieval.py`.
- Integrator-locked files changed: none.

## Scope Completed

This corrected packet supersedes the stale narrow-range handoff and makes all production and test changes through the final fixer commit part of the reviewed implementation range. The final fixer commit SHA is reported in the fixer response.

The retrieval lane keeps SQLite FTS as the authoritative MVP retrieval path. The branch adds deterministic FTS cache handling and cache audit metadata, normalizes retrieval payload snapshots and query constraints, preserves retrieval provenance for basket/context promotion flows, keeps PageIndex and embeddings as deferred compatibility surfaces, and makes date-range constraints fail fast when malformed or reversed before FTS execution.

Current finalization passes after `25f8d10c4b8f02c6d613af3300a5b7a02ec1c848` add canonical retrieval-query boundary validation so empty query text or scope fails before FTS execution, and caller whitespace is trimmed before scope matching, payload snapshots, and provenance fingerprints are produced.

This finalization pass after `78b6747f4827b5304204e26e42c99827f04d6481` surfaces normalized query constraints directly in citation, provenance, doc/excerpt bundle, and source-bundle snapshots. The engine payload compatibility shim preserves that source-bundle constraint snapshot while keeping the top-level downstream payload shape stable when source bundles are rehydrated for basket/context promotion flows.

This finalization pass after `c72c99cb27c5b23934314c551c904603fd4e4553` preserves normalized query constraints when sparse downstream payloads are rehydrated into citation bundles, keeping citation, provenance, and source-bundle consumers aligned on the same FTS-first query contract for basket/context promotion.

This finalization pass after `22df380914bce7606c83026492636d763a9e9c97` adds a deterministic `lookup_fingerprint` to canonical FTS excerpt lookup payloads, lookup provenance, and lookup audit metadata so fetched excerpts can be tied back to a stable FTS-only lookup event during basket/context promotion and later revise/apply flows.

This finalization pass after `c15473477f3b0469775183f36b970828b02be7ccc` adds the normalized query-constraint snapshot directly to retrieval evidence so basket/context promotion, revise, and apply flows can audit the exact FTS-first constraint boundary that produced the promoted material.

## Tasks Completed

1. Made SQLite FTS the primary retrieval path for document and excerpt retrieval, with PageIndex and embeddings retained as compatibility-only fallback/deferred surfaces.
2. Stabilized FTS retrieval cache behavior, including cache invalidation on document updates and cache audit metadata for payload/provenance consumers.
3. Normalized retrieval payloads, query snapshots, constraints, provenance fingerprints, source bundles, and basket/context promotion metadata for deterministic downstream engine use, including explicit query-constraint snapshots in bundle/provenance surfaces.
4. Validated date-range constraints and canonical query text/scope constraints at the retrieval boundary, preserved normalized query constraints during sparse citation-bundle rehydration, added stable FTS excerpt lookup fingerprints to payload/provenance/audit snapshots, and exposed normalized query constraints in retrieval evidence for basket/context promotion, with approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for the FTS-first retrieval behavior, payload normalization, cache metadata, facade exports, citation/provenance helpers, excerpt lookup, and date-range validation included in this task group.

## Files Changed

Reviewed implementation range for re-review: `378cf9a74a3658058079a32f186fcd254c4a4034..FINAL_FIXER_HEAD_REPORTED_IN_RESPONSE`.

From `git diff --name-status 378cf9a74a3658058079a32f186fcd254c4a4034..FINAL_FIXER_HEAD_REPORTED_IN_RESPONSE`:

- `M .codex/kickoff_packets/feat-retrieval-fts.md`
- `M .codex/lane_meta/feat-retrieval-fts.json`
- `M THREAD_PACKET.md`
- `M src/qual/engine/retrieval/fts_strategy.py`
- `M src/qual/engine/retrieval/payload.py`
- `M src/qual/retrieval/service.py`
- `M tests/unit/test_unified_retrieval.py`

Implementation files changed after `adfa8cdadd43747ffbcb612e4151e262b13e52ca` are included in this reviewed range:

- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

Additional current finalization diff after `c15473477f3b0469775183f36b970828b02be7ccc`:

- `M THREAD_PACKET.md` - handoff packet restamp.
- `M src/qual/retrieval/service.py` - adds normalized query-constraint evidence to the canonical FTS retrieval evidence snapshot.

From `git diff --stat 378cf9a74a3658058079a32f186fcd254c4a4034..FINAL_FIXER_HEAD_REPORTED_IN_RESPONSE`:

- `.codex/kickoff_packets/feat-retrieval-fts.md` - 36 lines changed.
- `.codex/lane_meta/feat-retrieval-fts.json` - 155 lines changed.
- `THREAD_PACKET.md` - 198 lines changed.
- `src/qual/engine/retrieval/fts_strategy.py` - 6 lines changed.
- `src/qual/engine/retrieval/payload.py` - 33 lines changed.
- `src/qual/retrieval/service.py` - 109 lines changed.
- `tests/unit/test_unified_retrieval.py` - 108 lines changed.

## Budget/Risk

- Task budget: `4` high-risk task groups, including the post-`adfa8cdadd43747ffbcb612e4151e262b13e52ca` date-range query-boundary validation changes and the post-`22df380914bce7606c83026492636d763a9e9c97` FTS excerpt lookup fingerprint finalization as task group 4.
- File count for reviewed implementation handoff: `7 files changed`.
- Size accounting: `509 insertions(+), 136 deletions(-)`; net `373` LOC for the full packet range, including regenerated handoff metadata.
- Implementation code/test size accounting: `209 insertions(+), 47 deletions(-)`; net `162` LOC across 4 implementation/test files.
- AGENTS file/size status: implementation code/test changes fit high-risk limits; full packet range exceeds the `<=300 net LOC` high-risk size limit because it includes required handoff metadata regeneration.
- Shared/integrator exception status: uses the approved shared regression surface `tests/unit/test_unified_retrieval.py`; no integrator-locked files changed.
- Routing/provider impact: none.
- PageIndex/embeddings impact: no PageIndex, embeddings, hybrid, or alternate retrieval path was added as a required MVP path.
- Remaining risks/blockers: sandbox blocks writes under `.codex/kickoff_packets` and `.codex/lane_meta` with `Operation not permitted`, so this fixer commit updates `THREAD_PACKET.md`, the writable handoff packet. The stale hidden metadata paths still require an environment with `.codex` write permission if reviewers require those artifacts to be restamped too.

Current finalization remains low blast radius: the final fixer commit updates the FTS retrieval evidence snapshot and this handoff packet. No integrator-locked file edits are added by this fixer pass.

## Traceability Correction

The earlier packet incorrectly claimed commits after `adfa8cdadd43747ffbcb612e4151e262b13e52ca` were metadata-only. That claim is withdrawn. Commits including `1696a088d`, `d31c231e`, `9792d439`, and `25f8d10c4` are code-bearing retrieval/test commits and are included in the corrected reviewed implementation range.

This handoff has one authoritative reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..FINAL_FIXER_HEAD_REPORTED_IN_RESPONSE`.

## Roadmap/Vision

- Roadmap items affected: `ROADMAP.md` Milestone 3 retrieval/search readiness and real workflow loop support.
- Product Vision capability affected: retrieval-first context handling.
- Architecture alignment: FTS remains the required local retrieval path. PageIndex and embeddings stay compatibility-only/deferred.
- Canonical demo-path mapping: advances `retrieve relevant material` by preventing invalid date filters and whitespace-only retrieval queries from producing misleading or unstable retrieval evidence, by making the normalized retrieval constraints visible and rehydratable in bundle/provenance/citation/evidence snapshots used for basket/context promotion, and by making fetched FTS excerpt payloads auditable through stable lookup fingerprints.
- Routing/provider impact note: none.
- Proposed `README.md` patch text: none.

## Commands Run

Commands run for this corrected packet on the branch-tip worktree state:

- `python -m unittest tests.unit.test_unified_retrieval` - passed 58 retrieval unit tests after adding query-constraint snapshots to retrieval evidence.
- `./quality-format.sh --check` - passed after adding query-constraint snapshots to retrieval evidence.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks after adding query-constraint snapshots to retrieval evidence.
- `./quality-test.sh` - passed smoke tests and 127 unit tests after adding query-constraint snapshots to retrieval evidence.
- `./typecheck-test.sh` - passed Python source compilation under `src/` after adding query-constraint snapshots to retrieval evidence.
- `make ci` - passed setup, scope-check, format, lint, compile/typecheck, smoke tests, and 127 unit tests after adding query-constraint snapshots to retrieval evidence.
- `python -m unittest tests.unit.test_unified_retrieval` - passed 58 retrieval unit tests after adding FTS excerpt lookup fingerprints.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - passed smoke tests and 127 unit tests.
- `./typecheck-test.sh` - passed Python source compilation under `src/`.
- `make ci` - passed setup, scope-check, format, lint, compile/typecheck, smoke tests, and 127 unit tests.
- `make scope-check` - passed for branch `codex/feat-retrieval-fts`.

- `make scope-check` - passed; no policy for branch `codex/feat-retrieval-fts`, scope-check skipped policy and passed.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - passed smoke tests and 127 unit tests.
- `./typecheck-test.sh` - passed Python source compilation under `src/`.
- `make ci` - passed setup, scope-check, format, lint, compile/typecheck, smoke tests, and 127 unit tests.
- `python -m unittest tests.unit.test_unified_retrieval` - passed 58 retrieval unit tests.
- `python -m pytest tests/unit/test_unified_retrieval.py` - not run; active Python reported `No module named pytest`.
- `./quality-test.sh` - first run failed 5 unified retrieval helper rehydration comparisons after adding `query_constraints`; fixed by normalizing source-bundle constraint snapshots in `src/qual/engine/retrieval/payload.py`.
- `make scope-check` - passed.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - passed smoke tests and 127 unit tests.
- `./typecheck-test.sh` - passed Python source compilation under `src/`.
- `make ci` - passed setup, scope-check, format, lint, compile/typecheck, smoke tests, and 127 unit tests.
- `python -m unittest tests.unit.test_unified_retrieval` - passed 58 retrieval unit tests after preserving sparse citation-bundle query constraints.
- `make scope-check` - passed after the final sparse citation-bundle constraint rehydration change.
