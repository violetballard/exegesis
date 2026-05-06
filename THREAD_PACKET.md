## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Handoff type: high-risk branch-tip retrieval handoff for the FTS-first retrieval lane.
- Reviewed implementation base: `378cf9a74a3658058079a32f186fcd254c4a4034`.
- Actual merge candidate before this packet fix: `e49d7c2c34d1e8f3dd8ca1927e2efbef53d67f06`.
- Reviewed implementation range for re-review: `378cf9a74a3658058079a32f186fcd254c4a4034..FINAL_BRANCH_TIP`.
- Final branch tip: reported in the final fixer response after commit creation.
- Scope classification: high-risk because this lane touches retrieval core/facade behavior and approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Lane-owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`.
- Approved shared regression path: `tests/unit/test_unified_retrieval.py`.
- Integrator-locked files: none.

## Scope Completed

This branch-tip handoff covers the full retrieval implementation currently present on `codex/feat-retrieval-fts`, including all production and test changes after `adfa8cdadd43747ffbcb612e4151e262b13e52ca`. SQLite FTS remains the authoritative retrieval path for MVP flows. PageIndex and embeddings remain compatibility-only/deferred surfaces that fail closed when they cannot be resolved through the canonical FTS path.

The branch hardens deterministic retrieval payloads, FTS candidate strategy identity, sparse-policy rehydration, excerpt lookup provenance, bundle identity validation, and final hit rank/score ordering. Downstream citation bundles, context bundles, and basket promotion payloads now receive normalized, auditable retrieval snapshots tied to the FTS-first result order the engine consumes.

Canonical demo-path step advanced: `retrieve relevant material`. This also supports `promote or gather context into the basket` because source bundles, context bundles, citations, and basket promotion items carry deterministic retrieval provenance.

## Tasks Completed

1. FTS-first retrieval and excerpt lookup: kept SQLite FTS authoritative, exported the canonical retrieval facades, removed PageIndex fallback from excerpt fetching, and enforced fail-closed behavior for PageIndex-only or non-FTS excerpt identifiers.
2. Deterministic retrieval payloads and provenance: normalized query snapshots, constraints, candidate/document identities, source bundles, context bundles, citation backfills, lookup fingerprints, and basket promotion metadata.
3. Retrieval policy and strategy hardening: preserved sparse retrieval policy identity, guarded deferred backend policy, validated bundle identity, stabilized FTS merge strategy identity, and kept engine retrieval exports aligned with the canonical retrieval implementation.
4. Final result ordering and regression coverage: re-ranked final deduplicated FTS hits after truncation so score/provenance rank match output order, and expanded approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for FTS-only behavior, payload identity, provenance, and promotion-ready outputs.

Final demo-path statement: retrieval output remains FTS-first, deterministic, auditable, and promotion-ready, with citation and basket promotion metadata tied to the final result order.

## Files Changed

Reviewed implementation range for re-review: `378cf9a74a3658058079a32f186fcd254c4a4034..FINAL_BRANCH_TIP`.

- `.codex/kickoff_packets/feat-retrieval-fts.md` - branch-tip range includes this stale lane metadata from earlier commits; this fixer attempted to update it, but the sandbox rejected writes to hidden `.codex` paths with `Operation not permitted`.
- `.codex/lane_meta/feat-retrieval-fts.json` - branch-tip range includes this stale lane metadata from earlier commits; this fixer attempted to update it, but the sandbox rejected writes to hidden `.codex` paths with `Operation not permitted`.
- `THREAD_PACKET.md` - regenerated this authoritative handoff packet for the actual branch-tip scope.
- `src/qual/engine/retrieval/__init__.py` - aligned engine retrieval exports and compatibility facade wiring with the FTS-first retrieval surface.
- `src/qual/engine/retrieval/fts_strategy.py` - hardened FTS strategy identity and candidate/provenance behavior.
- `src/qual/engine/retrieval/payload.py` - normalized retrieval payload snapshots, source/context bundles, citation backfills, basket promotion metadata, and identifier/fingerprint fields.
- `src/qual/retrieval/__init__.py` - exported canonical retrieval helpers through the public retrieval facade.
- `src/qual/retrieval/service.py` - implemented FTS-only excerpt fetching, deterministic query/constraint/cache handling, sparse policy reconstruction, and final hit re-ranking.
- `tests/unit/test_unified_retrieval.py` - expanded approved shared regression coverage for FTS-first retrieval, fail-closed fallback behavior, payload/provenance normalization, and branch-tip hardening.

## Diff Evidence

Command: `git diff --stat 378cf9a74a3658058079a32f186fcd254c4a4034 --`

```text
 .codex/kickoff_packets/feat-retrieval-fts.md |   36 +-
 .codex/lane_meta/feat-retrieval-fts.json     |  155 ++-
 THREAD_PACKET.md                             |  203 ++--
 src/qual/engine/retrieval/__init__.py        |   86 +-
 src/qual/engine/retrieval/fts_strategy.py    |   59 +-
 src/qual/engine/retrieval/payload.py         | 1399 +++++++++++++++++++++++---
 src/qual/retrieval/__init__.py               |   11 +
 src/qual/retrieval/service.py                |  844 ++++++++++++++--
 tests/unit/test_unified_retrieval.py         | 1201 +++++++++++++++++++++-
 9 files changed, 3609 insertions(+), 385 deletions(-)
```

Command: `git diff --stat adfa8cdadd43747ffbcb612e4151e262b13e52ca --`

```text
 .codex/kickoff_packets/feat-retrieval-fts.md |   36 +-
 .codex/lane_meta/feat-retrieval-fts.json     |  155 ++-
 THREAD_PACKET.md                             |  203 ++--
 src/qual/engine/retrieval/__init__.py        |   86 +-
 src/qual/engine/retrieval/fts_strategy.py    |   59 +-
 src/qual/engine/retrieval/payload.py         | 1399 +++++++++++++++++++++++---
 src/qual/retrieval/__init__.py               |   11 +
 src/qual/retrieval/service.py                |  823 ++++++++++++++-
 tests/unit/test_unified_retrieval.py         | 1181 +++++++++++++++++++++-
 9 files changed, 3590 insertions(+), 363 deletions(-)
```

Command: `git show --name-status --oneline e49d7c2c34d1e8f3dd8ca1927e2efbef53d67f06`

```text
e49d7c2c3 Harden final retrieval hit ranks
M	THREAD_PACKET.md
M	src/qual/retrieval/service.py
```

## Budget/Risk

- Task budget: `4/4` high-risk task groups.
- File count for branch-tip handoff including this packet fix: `9 files changed`.
- Size accounting for branch-tip handoff including this packet fix: `3609 insertions(+), 385 deletions(-)`, net `3224 LOC`.
- Post-`adfa8cd` branch delta including this packet fix: `9 files changed, 3590 insertions(+), 363 deletions(-)`.
- AGENTS file/size status: exceeds high-risk size limits of `<=8 files` and `<=300 net LOC`; this is now explicitly disclosed for reviewer/integrator judgment instead of being hidden behind metadata-only wording.
- Shared/integrator exception status: `tests/unit/test_unified_retrieval.py` is approved shared regression coverage for the retrieval lane; no integrator-locked files changed.
- Routing/provider impact: none.
- PageIndex/embeddings impact: remain compatibility-only/deferred identifiers; no PageIndex, embeddings, hybrid, or alternate retrieval path was added.
- Remaining risks/blockers: the branch-tip change volume exceeds AGENTS high-risk size limits. The authoritative root packet no longer claims production/test commits after `adfa8cd` are metadata-only. Stale `.codex` metadata copies still contain old metadata-only wording because this sandbox rejected writes to those hidden paths.

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

## Metadata Write Note

The root `THREAD_PACKET.md` is the authoritative regenerated handoff packet. No commit after `adfa8cdadd43747ffbcb612e4151e262b13e52ca` is described here as metadata-only unless `git show --name-status` for that commit contains only packet or lane metadata files. The reviewed implementation range intentionally covers `378cf9a74a3658058079a32f186fcd254c4a4034..FINAL_BRANCH_TIP` so the actual merge candidate is traceable.

## Metadata Write Blocker

This fixer attempted to update `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` to remove stale metadata-only wording from those copies as well. Both writes failed with `PermissionError: [Errno 1] Operation not permitted` in this worktree sandbox. The root `THREAD_PACKET.md` is therefore the corrected source of truth for re-review, while the stale `.codex` metadata files remain an explicit blocker/risk if the reviewer treats them as authoritative.
