## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Handoff type: high-risk branch-tip retrieval handoff for the FTS-first retrieval lane.
- Reviewed implementation base: `378cf9a74a3658058079a32f186fcd254c4a4034`.
- Actual merge candidate before this packet fix: `b44a4cd1ed2fa32d36f52d8cca11f4fc8f72ff4e`.
- Reviewed implementation range for re-review: `378cf9a74a3658058079a32f186fcd254c4a4034..FINAL_BRANCH_TIP`.
- Final branch tip: reported in the final fixer response after commit creation.
- Scope classification: high-risk because this lane touches retrieval core/facade behavior and approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Lane-owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`.
- Approved shared regression path: `tests/unit/test_unified_retrieval.py`.
- Integrator-locked files: none.

## Scope Completed

This branch-tip handoff covers the full retrieval implementation currently present on `codex/feat-retrieval-fts`, including all production and test changes after `adfa8cdadd43747ffbcb612e4151e262b13e52ca`. SQLite FTS remains the authoritative retrieval path for MVP flows. PageIndex and embeddings remain compatibility-only/deferred surfaces that fail closed when they cannot be resolved through the canonical FTS path.

The branch hardens deterministic retrieval payloads, FTS candidate strategy identity, sparse-policy rehydration, sparse candidate-resolution rehydration, excerpt lookup provenance, bundle identity validation, and final hit rank/score ordering. Downstream citation bundles, context bundles, and basket promotion payloads now receive normalized, auditable retrieval snapshots tied to the FTS-first result order and candidate set the engine consumes.

Canonical demo-path step advanced: `retrieve relevant material`. This also supports `promote or gather context into the basket` because source bundles, context bundles, citations, and basket promotion items carry deterministic retrieval provenance.

## Tasks Completed

1. FTS-first retrieval and excerpt lookup: kept SQLite FTS authoritative, exported the canonical retrieval facades, removed PageIndex fallback from excerpt fetching, and enforced fail-closed behavior for PageIndex-only or non-FTS excerpt identifiers. Canonical demo-path step advanced: `retrieve relevant material`.
2. Deterministic retrieval payloads and provenance: normalized query snapshots, constraints, candidate/document identities, candidate-resolution snapshots, source bundles, context bundles, citation backfills, lookup fingerprints, and basket promotion metadata. Canonical demo-path steps advanced: `retrieve relevant material` and `promote or gather context into the basket`.
3. Retrieval policy and strategy hardening: preserved sparse retrieval policy identity, guarded deferred backend policy, validated bundle identity, stabilized FTS merge strategy identity, and kept engine retrieval exports aligned with the canonical retrieval implementation. Canonical demo-path step advanced: `retrieve relevant material`.
4. Final result ordering and regression coverage: re-ranked final deduplicated FTS hits after truncation so score/provenance rank match output order, and expanded approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for FTS-only behavior, payload identity, provenance, and promotion-ready outputs. Canonical demo-path steps advanced: `retrieve relevant material` and `promote or gather context into the basket`.

Required before-handoff demo-path statement: this work now makes the canonical demo-path step `retrieve relevant material` more real by keeping retrieval FTS-first, deterministic, auditable, and tied to final result order; it also makes `promote or gather context into the basket` more real by carrying citation and basket promotion metadata through the retrieval payloads.

## Files Changed

Reviewed implementation range for re-review: `378cf9a74a3658058079a32f186fcd254c4a4034..FINAL_BRANCH_TIP`.

- `.codex/kickoff_packets/feat-retrieval-fts.md` - branch-tip range includes stale lane metadata from earlier commits; sandbox permissions rejected direct `.codex/**` edits in this fixer pass, so the integration-facing root packet is the regenerated source of truth for re-review.
- `.codex/lane_meta/feat-retrieval-fts.json` - branch-tip range includes stale lane metadata from earlier commits; sandbox permissions rejected direct `.codex/**` edits in this fixer pass, so the integration-facing root packet is the regenerated source of truth for re-review.
- `THREAD_PACKET.md` - regenerated this authoritative handoff packet for the actual branch-tip scope.
- `src/qual/engine/retrieval/__init__.py` - aligned engine retrieval exports and compatibility facade wiring with the FTS-first retrieval surface.
- `src/qual/engine/retrieval/fts_strategy.py` - hardened FTS strategy identity and candidate/provenance behavior.
- `src/qual/engine/retrieval/payload.py` - normalized retrieval payload snapshots, source/context bundles, citation backfills, candidate-resolution rehydration, basket promotion metadata, and identifier/fingerprint fields.
- `src/qual/retrieval/__init__.py` - exported canonical retrieval helpers through the public retrieval facade.
- `src/qual/retrieval/service.py` - implemented FTS-only excerpt fetching, deterministic query/constraint/cache handling, sparse policy reconstruction, and final hit re-ranking.
- `tests/unit/test_unified_retrieval.py` - expanded approved shared regression coverage for FTS-first retrieval, fail-closed fallback behavior, payload/provenance normalization, candidate-resolution rehydration, and branch-tip hardening.

## Diff Evidence

Command: `git diff --stat 378cf9a74a3658058079a32f186fcd254c4a4034 --`

```text
 .codex/kickoff_packets/feat-retrieval-fts.md |   36 +-
 .codex/lane_meta/feat-retrieval-fts.json     |  155 ++-
 THREAD_PACKET.md                             |  203 ++--
 src/qual/engine/retrieval/__init__.py        |   86 +-
 src/qual/engine/retrieval/fts_strategy.py    |   59 +-
 src/qual/engine/retrieval/payload.py         | 1424 +++++++++++++++++++++++---
 src/qual/retrieval/__init__.py               |   11 +
 src/qual/retrieval/service.py                |  845 +++++++++++++--
 tests/unit/test_unified_retrieval.py         | 1203 +++++++++++++++++++++-
 9 files changed, 3636 insertions(+), 386 deletions(-)
```

Command: `git diff --stat adfa8cdadd43747ffbcb612e4151e262b13e52ca --`

```text
 .codex/kickoff_packets/feat-retrieval-fts.md |   36 +-
 .codex/lane_meta/feat-retrieval-fts.json     |  155 ++-
 THREAD_PACKET.md                             |  203 ++--
 src/qual/engine/retrieval/__init__.py        |   86 +-
 src/qual/engine/retrieval/fts_strategy.py    |   59 +-
 src/qual/engine/retrieval/payload.py         | 1424 +++++++++++++++++++++++---
 src/qual/retrieval/__init__.py               |   11 +
 src/qual/retrieval/service.py                |  824 ++++++++++++++-
 tests/unit/test_unified_retrieval.py         | 1181 +++++++++++++++++++++-
 9 files changed, 3616 insertions(+), 363 deletions(-)
```

Command: `git show --name-status --oneline 7124a25d35c390ee27d0ea07865323b6916ca5d4`

```text
7124a25d3 fix(retrieval): backfill sparse excerpt policy
M	src/qual/engine/retrieval/payload.py
```

## Budget/Risk

- Task budget: `4/4` high-risk task groups.
- File count for branch-tip handoff including this packet fix: `9 files changed`.
- Size accounting for branch-tip handoff before this packet fix: `3636 insertions(+), 386 deletions(-)`, net `3250 LOC`.
- Post-`adfa8cd` branch delta before this packet fix: `9 files changed, 3616 insertions(+), 363 deletions(-)`.
- AGENTS file/size status: exceeds high-risk size limits of `<=8 files` and `<=300 net LOC`; this is now explicitly disclosed for reviewer/integrator judgment instead of being hidden behind metadata-only wording.
- Shared/integrator exception status: `tests/unit/test_unified_retrieval.py` is approved shared regression coverage for the retrieval lane; no integrator-locked files changed.
- Routing/provider impact: none.
- PageIndex/embeddings impact: remain compatibility-only/deferred identifiers; no PageIndex, embeddings, hybrid, or alternate retrieval path was added.
- Remaining risks/blockers: the branch-tip change volume exceeds AGENTS high-risk size limits. The authoritative root packet no longer claims production/test commits after `adfa8cd` are metadata-only. Stale `.codex` metadata copies still contain old metadata-only wording and should not be treated as authoritative for this re-review.

## Roadmap/Vision

- Roadmap items affected: `ROADMAP.md` Milestone 3 generation provenance contract and Milestone 4 FTS-first retrieval orchestration/source-attribution/auditable deterministic retrieval.
- Vision capability affected: retrieval-backed context, retrieval-first context handling, auditable outputs, and reliable local-first state.
- Architecture alignment: FTS remains the required local retrieval path. PageIndex and embeddings stay compatibility-only/deferred.
- Canonical demo-path mapping: advances `retrieve relevant material` and supports `promote or gather context into the basket`.
- Routing/provider impact note: none.
- Proposed `README.md` patch text: none.

## Commands Run

- `make scope-check` - passed for branch `codex/feat-retrieval-fts`.
- `python -m pytest tests/unit/test_unified_retrieval.py -q` - not run; current interpreter has no installed `pytest` module.
- `python -m unittest tests.unit.test_unified_retrieval -v` - passed 81 unit tests.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - passed smoke tests and 150 unit tests.
- `./typecheck-test.sh` - passed Python source compilation under `src/`.
- `make ci` - passed setup, scope-check, format, lint, compile/typecheck, smoke tests, and 150 unit tests.

## Metadata Note

The root `THREAD_PACKET.md` is the authoritative regenerated handoff packet. No commit after `adfa8cdadd43747ffbcb612e4151e262b13e52ca` is described here as metadata-only unless `git show --name-status` for that commit contains only packet or lane metadata files. The reviewed implementation range intentionally covers `378cf9a74a3658058079a32f186fcd254c4a4034..FINAL_BRANCH_TIP` so the actual merge candidate is traceable.

The `.codex` lane metadata files are included in the branch-tip diff because earlier packet refresh commits changed them, but their stale narrow-range wording is superseded by this root packet for re-review. This fixer attempted to regenerate those `.codex` copies too; the sandbox rejected writes to `.codex/**` with `Operation not permitted`, while allowing this root packet update. Reviewers should use this root packet plus the final fixer response HEAD SHA as the source of truth for the merge candidate.
