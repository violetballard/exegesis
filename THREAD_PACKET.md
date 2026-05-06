## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Handoff type: high-risk branch-tip retrieval handoff for the FTS-first retrieval lane.
- Reviewed implementation base: `378cf9a74a3658058079a32f186fcd254c4a4034`.
- Actual implementation candidate before this packet fix: `760f0e2cc74dbc5a8b7586d97a05cc6635cdca0d`.
- Reviewed implementation range for re-review: `378cf9a74a3658058079a32f186fcd254c4a4034..760f0e2cc74dbc5a8b7586d97a05cc6635cdca0d`, plus the final fixer delta after `ffa91fdf8605c53c0f0857b6ab1d42dd69d31ec5`.
- Current branch-tip anchor before this final fixer commit: `ffa91fdf8605c53c0f0857b6ab1d42dd69d31ec5`.
- Final fixer commit: reported in the final fixer response after this packet is committed.
- Scope classification: high-risk because this lane touches retrieval core/facade behavior and approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Lane-owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`.
- Approved shared regression path: `tests/unit/test_unified_retrieval.py`.
- Integrator-locked files: none.

## Scope Completed

This branch-tip handoff covers the full retrieval implementation currently present on `codex/feat-retrieval-fts`, including all production and test changes after `adfa8cdadd43747ffbcb612e4151e262b13e52ca`. SQLite FTS remains the authoritative retrieval path for MVP flows. PageIndex and embeddings remain compatibility-only/deferred surfaces that fail closed when they cannot be resolved through the canonical FTS path.

The branch hardens deterministic retrieval payloads, FTS candidate strategy identity, sparse-policy rehydration, sparse candidate-resolution rehydration, excerpt lookup provenance, bundle identity validation, final hit rank/score ordering, basket-promotion strategy aliases, and basket-promotion match evidence. This final fixer pass also makes direct FTS excerpt lookup promotion refs carry the `retrieval_source_strategy: fts` alias used by result-derived promotion refs, so basket promotion consumers see consistent strategy identity whether an excerpt comes from a retrieval result or a canonical excerpt lookup. Downstream citation bundles, context bundles, excerpt lookup audit events, and basket promotion payloads now receive normalized, auditable retrieval snapshots tied to the FTS-first result order, matched terms, and candidate set the engine consumes.

Canonical demo-path step advanced: `retrieve relevant material`. This work makes the canonical demo-path step `retrieve relevant material` more real by making FTS excerpt lookup deterministic, provenance-backed, and fail-closed for PageIndex-only IDs; it also supports later `promote or gather context into the basket` by keeping excerpt provenance deterministic.

## Tasks Completed

1. FTS-first retrieval and excerpt lookup: kept SQLite FTS authoritative, exported the canonical retrieval facades, removed PageIndex fallback from excerpt fetching, and enforced fail-closed behavior for PageIndex-only or non-FTS excerpt identifiers. Canonical demo-path step advanced: `retrieve relevant material`.
2. Deterministic retrieval payloads and provenance: normalized query snapshots, constraints, candidate/document identities, candidate-resolution snapshots, source bundles, context bundles, citation backfills, lookup fingerprints, excerpt lookup audit hashes, and basket promotion metadata, including explicit `retrieval_source_strategy` aliases plus `matched_terms`/`match_count` evidence on promotion refs. The final fixer pass extends that alias to direct FTS excerpt lookup promotion refs. Canonical demo-path steps advanced: `retrieve relevant material` and `promote or gather context into the basket`.
3. Retrieval policy and strategy hardening: preserved sparse retrieval policy identity, guarded deferred backend policy, validated bundle identity, stabilized FTS merge strategy identity, and kept engine retrieval exports aligned with the canonical retrieval implementation. Canonical demo-path step advanced: `retrieve relevant material`.
4. Final result ordering and regression coverage: re-ranked final deduplicated FTS hits after truncation so score/provenance rank match output order, and expanded approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for FTS-only behavior, payload identity, provenance, and promotion-ready outputs. Canonical demo-path steps advanced: `retrieve relevant material` and `promote or gather context into the basket`.

AGENTS.md narrowing statement: This work makes the canonical demo-path step `retrieve relevant material` more real by making FTS excerpt lookup deterministic, provenance-backed, and fail-closed for PageIndex-only IDs. It also makes `promote or gather context into the basket` more real by carrying citation, matched-term evidence, and basket promotion metadata through the retrieval payloads.

## Files Changed

Reviewed implementation range for re-review: `378cf9a74a3658058079a32f186fcd254c4a4034..760f0e2cc74dbc5a8b7586d97a05cc6635cdca0d`, plus the final fixer delta after `ffa91fdf8605c53c0f0857b6ab1d42dd69d31ec5`.

- `.codex/kickoff_packets/feat-retrieval-fts.md` - branch-tip range includes stale lane metadata from earlier commits; attempted update in this fixer pass was blocked by sandbox filesystem permissions (`Operation not permitted` under `.codex`).
- `.codex/lane_meta/feat-retrieval-fts.json` - branch-tip range includes stale lane metadata from earlier commits; attempted update in this fixer pass was blocked by sandbox filesystem permissions (`Operation not permitted` under `.codex`).
- `THREAD_PACKET.md` - regenerated this authoritative handoff packet for the actual implementation scope through `760f0e2cc74dbc5a8b7586d97a05cc6635cdca0d` plus the final fixer delta after `ffa91fdf8605c53c0f0857b6ab1d42dd69d31ec5`.
- `src/qual/engine/retrieval/__init__.py` - aligned engine retrieval exports and compatibility facade wiring with the FTS-first retrieval surface.
- `src/qual/engine/retrieval/fts_strategy.py` - hardened FTS strategy identity and candidate/provenance behavior.
- `src/qual/engine/retrieval/payload.py` - normalized retrieval payload snapshots, source/context bundles, citation backfills, candidate-resolution rehydration, basket promotion metadata, FTS strategy aliases, matched-term promotion fingerprints, and identifier/fingerprint fields.
- `src/qual/retrieval/__init__.py` - exported canonical retrieval helpers through the public retrieval facade.
- `src/qual/retrieval/service.py` - implemented FTS-only excerpt fetching, deterministic query/constraint/cache handling, sparse policy reconstruction, final hit re-ranking, explicit FTS strategy aliases and matched-term evidence for basket promotion items, and canonical `excerpt_text_hash` audit recording for excerpt lookups.
- `tests/unit/test_unified_retrieval.py` - expanded approved shared regression coverage for FTS-first retrieval, fail-closed fallback behavior, payload/provenance normalization, candidate-resolution rehydration, branch-tip hardening, matched-term basket promotion evidence, and canonical excerpt lookup audit identity.

Final fixer delta after `ffa91fdf8605c53c0f0857b6ab1d42dd69d31ec5`:

- `src/qual/retrieval/service.py` - direct FTS excerpt lookup basket-promotion items now include `retrieval_source_strategy: fts`.
- `tests/unit/test_unified_retrieval.py` - approved shared regression coverage asserts the canonical excerpt lookup promotion ref exposes the FTS strategy alias.

## Diff Evidence

Command: `git diff --stat 378cf9a74a3658058079a32f186fcd254c4a4034..760f0e2cc74dbc5a8b7586d97a05cc6635cdca0d`

```text
 .codex/kickoff_packets/feat-retrieval-fts.md |   36 +-
 .codex/lane_meta/feat-retrieval-fts.json     |  155 ++-
 THREAD_PACKET.md                             |  218 ++--
 src/qual/engine/retrieval/__init__.py        |   86 +-
 src/qual/engine/retrieval/fts_strategy.py    |   59 +-
 src/qual/engine/retrieval/payload.py         | 1429 +++++++++++++++++++++++---
 src/qual/retrieval/__init__.py               |   11 +
 src/qual/retrieval/service.py                |  854 +++++++++++++--
 tests/unit/test_unified_retrieval.py         | 1261 ++++++++++++++++++++++-
 9 files changed, 3702 insertions(+), 407 deletions(-)
```

Command: `git diff --stat adfa8cdadd43747ffbcb612e4151e262b13e52ca..760f0e2cc74dbc5a8b7586d97a05cc6635cdca0d`

```text
 .codex/kickoff_packets/feat-retrieval-fts.md |   36 +-
 .codex/lane_meta/feat-retrieval-fts.json     |  155 ++-
 THREAD_PACKET.md                             |  218 ++--
 src/qual/engine/retrieval/__init__.py        |   86 +-
 src/qual/engine/retrieval/fts_strategy.py    |   59 +-
 src/qual/engine/retrieval/payload.py         | 1429 +++++++++++++++++++++++---
 src/qual/retrieval/__init__.py               |   11 +
 src/qual/retrieval/service.py                |  833 ++++++++++++++-
 tests/unit/test_unified_retrieval.py         | 1181 ++++++++++++++++++++-
 9 files changed, 3653 insertions(+), 355 deletions(-)
```

Command: `git show --name-status --oneline b44a4cd1ed2fa32d36f52d8cca11f4fc8f72ff4e`

```text
b44a4cd1e fix(retrieval): preserve fts rank in basket provenance
M	src/qual/engine/retrieval/payload.py
M	src/qual/retrieval/service.py
```

Command: `git show --name-status --oneline 7124a25d35c390ee27d0ea07865323b6916ca5d4`

```text
7124a25d3 fix(retrieval): backfill sparse excerpt policy
M	src/qual/engine/retrieval/payload.py
```

Current implementation delta before this packet refresh:

```text
src/qual/engine/retrieval/payload.py |  2 ++
src/qual/retrieval/service.py        |  6 ++++++
tests/unit/test_unified_retrieval.py | 16 ++++++++++++++++
3 files changed, 24 insertions(+)
```

Final fixer delta after `ffa91fdf8605c53c0f0857b6ab1d42dd69d31ec5`:

```text
 src/qual/retrieval/service.py        | 1 +
 tests/unit/test_unified_retrieval.py | 1 +
 2 files changed, 2 insertions(+)
```

## Budget/Risk

- Task budget: `4/4` high-risk task groups.
- File count for reviewed implementation handoff: `9 files changed`.
- Size accounting for reviewed implementation handoff: `3702 insertions(+), 407 deletions(-)`, net `3295 LOC`.
- Post-`adfa8cd` implementation delta now included in the reviewed range: `9 files changed, 3653 insertions(+), 355 deletions(-)`.
- Final fixer delta after `ffa91fdf8605c53c0f0857b6ab1d42dd69d31ec5`: `2 files changed, 2 insertions(+)`.
- AGENTS file/size status: exceeds high-risk size limits of `<=8 files` and `<=300 net LOC`; this is now explicitly disclosed for reviewer/integrator judgment instead of being hidden behind metadata-only wording.
- Shared/integrator exception status: `tests/unit/test_unified_retrieval.py` is approved shared regression coverage for the retrieval lane; no integrator-locked files changed.
- Routing/provider impact: none.
- PageIndex/embeddings impact: remain compatibility-only/deferred identifiers; no PageIndex, embeddings, hybrid, or alternate retrieval path was added.
- Remaining risks/blockers: the reviewed implementation change volume exceeds AGENTS high-risk size limits. The authoritative root packet no longer claims production/test commits after `adfa8cd` are metadata-only; those commits are included in the corrected reviewed implementation range. `.codex` metadata copies still contain old narrow-range wording because this sandbox refuses writes under `.codex`; reviewer-required metadata synchronization remains blocked until that directory is writable or regenerated outside this sandbox.

## Roadmap/Vision

- Roadmap items affected: `ROADMAP.md` Milestone 3 generation provenance contract and Milestone 4 FTS-first retrieval orchestration/source-attribution/auditable deterministic retrieval.
- Vision capability affected: retrieval-backed context, retrieval-first context handling, auditable outputs, and reliable local-first state.
- Architecture alignment: FTS remains the required local retrieval path. PageIndex and embeddings stay compatibility-only/deferred.
- Canonical demo-path mapping: advances `retrieve relevant material` and supports `promote or gather context into the basket`.
- Routing/provider impact note: none.
- Proposed `README.md` patch text: none.

## Commands Run

- `make scope-check` - passed for branch `codex/feat-retrieval-fts`.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - passed smoke tests and 150 unit tests.
- `./typecheck-test.sh` - passed Python source compilation under `src/`.
- `make ci` - passed setup, scope-check, format, lint, compile/typecheck, smoke tests, and 150 unit tests.
- `python3 -m unittest tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_retrieve_fts_excerpt_returns_canonical_fts_payload` - passed the targeted canonical FTS excerpt lookup promotion-alias regression.
- `make scope-check` - passed for branch `codex/feat-retrieval-fts` after the final fixer delta.
- `./quality-format.sh --check` - passed after the final fixer delta.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks after the final fixer delta.
- `./quality-test.sh` - passed smoke tests and 150 unit tests after the final fixer delta.
- `./typecheck-test.sh` - passed Python source compilation under `src/` after the final fixer delta.
- `make ci` - passed setup, scope-check, format, lint, compile/typecheck, smoke tests, and 150 unit tests after the final fixer delta.
- `python3 -m unittest tests.unit.test_unified_retrieval` - passed 81 focused retrieval tests before the audit hash fix.
- `python3 -m unittest tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_retrieve_fts_excerpt_audit_records_stable_lookup_identity tests.unit.test_unified_retrieval` - passed the targeted audit regression plus the full retrieval suite, 82 test executions total.
- `python3 -m unittest tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_downstream_payload_exposes_policy_and_diagnostics_snapshot` - passed the targeted basket-promotion match evidence regression.
- `python3 -m unittest tests.unit.test_unified_retrieval` - passed 81 focused retrieval tests after the basket-promotion match evidence change.

## Metadata Note

The root `THREAD_PACKET.md` is the authoritative regenerated handoff packet. No commit after `adfa8cdadd43747ffbcb612e4151e262b13e52ca` is described here as metadata-only unless `git show --name-status` for that commit contains only packet or lane metadata files. The reviewed implementation range intentionally covers `378cf9a74a3658058079a32f186fcd254c4a4034..760f0e2cc74dbc5a8b7586d97a05cc6635cdca0d` plus the final fixer delta after `ffa91fdf8605c53c0f0857b6ab1d42dd69d31ec5` so the actual implementation candidate is traceable.

Current fixer blocker: this sandbox refuses all writes under `.codex` with `Operation not permitted`, including overwriting `.codex/kickoff_packets/feat-retrieval-fts.md`, overwriting `.codex/lane_meta/feat-retrieval-fts.json`, removing their `com.apple.provenance` extended attribute, and creating `.codex/write-test`. Because of that filesystem denial, reviewer required fix 5 cannot be completed inside this worktree even though root `THREAD_PACKET.md` names the corrected implementation range.
