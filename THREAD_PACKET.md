## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Reviewed source/test implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..cc084f05c58c8c3c0613dded69109fdf7ce03708`
- Reviewed source/test implementation head: `cc084f05c58c8c3c0613dded69109fdf7ce03708`
- Authoritative branch-tip merge/review range: `378cf9a74a3658058079a32f186fcd254c4a4034..FINAL_HEAD_SHA_REPORTED_BY_FIXER_DELIVERABLE`
- Pre-fix packet refresh tip: `1483db4a5bfe8a71906d65e33c97e3224bdaf5fe` (metadata-only after `cc084f05c58c8c3c0613dded69109fdf7ce03708`).
- Final branch tip: reported in the fixer deliverable after this packet commit is created; this final fixer commit is metadata-only.
- Scope classification: high-risk because this branch-tip packet includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Packet type: branch-tip re-review packet for the FTS-first retrieval lane.

## Scope Completed

This packet has been regenerated against the actual branch tip to be submitted. The source/test implementation surface is `378cf9a74a3658058079a32f186fcd254c4a4034..cc084f05c58c8c3c0613dded69109fdf7ce03708`; every commit after `cc084f05c58c8c3c0613dded69109fdf7ce03708` through the final fixer HEAD changes packet metadata only. `git diff --name-status cc084f05c58c8c3c0613dded69109fdf7ce03708..1483db4a5bfe8a71906d65e33c97e3224bdaf5fe -- src/qual/engine/retrieval src/qual/retrieval/service.py tests/unit/test_unified_retrieval.py` is empty, so this source/test range covers every retrieval implementation and test change present at the pre-fix branch tip. The authoritative merge/review range for re-review is therefore the full base-to-final-HEAD range reported in the fixer deliverable, with the source/test implementation files listed below.

The reviewed branch-tip work strengthens the active MVP target of FTS-first retrieval. SQLite FTS remains the canonical retrieval path; engine and service facades expose canonical query construction, `retrieve_auto`, and excerpt lookup; retrieval payload snapshots, sparse source/context bundles, provenance, fingerprints, and basket-promotion references are normalized deterministically for downstream engine flows; and PageIndex-only excerpt IDs fail closed instead of backfilling through non-FTS paths.

Canonical demo-path step advanced: this makes `retrieve relevant material` and `promote/gather context into the basket` more real by returning deterministic FTS-backed excerpts, provenance, and retrieval-owned context references suitable for basket promotion. Basket promotion/gathering is represented only as retrieval-owned payload/context metadata in this branch-tip packet; Textual console work remains out of scope.

Packet mirror note: `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` still contain older packet text in this sandbox, but attempts to edit them in this fixer pass were rejected as outside the writable project boundary. Treat this writable `THREAD_PACKET.md` plus the final fixer deliverable as the authoritative handoff packet for this re-review.

## Tasks Completed

1. Exported the canonical FTS retrieval surface through the service and engine facades, including query construction, `retrieve_auto`, excerpt lookup, rank fields, and query type exports.
2. Hardened deterministic retrieval payloads by normalizing query snapshots, constraints, dates, booleans, sparse source/context bundles, citation backfills, provenance fingerprints, and copy-safe snapshot reconstruction.
3. Kept retrieval FTS-first by tightening cache scope invalidation, candidate document handling, section/date/confidentiality filtering, FTS-only excerpt resolution, and fail-closed PageIndex/embedding compatibility behavior.
4. Added approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for facade exports, normalized payload snapshots, source/context bundle rehydration, citation/provenance helpers, basket-promotion/context references, cache behavior, and FTS-only excerpt lookup.

## Canonical Demo Path

- Primary canonical demo-path step advanced: `retrieve relevant material` and `promote/gather context into the basket`.
- AGENTS.md narrowing language: this work targets the active MVP note for `FTS-first retrieval`.
- Basket promotion/gathering: limited to retrieval-owned payload/context metadata that supports later engine/demo gathering; no `feat-console` work is included.

## Files Changed

Reviewed source/test implementation files for `378cf9a74a3658058079a32f186fcd254c4a4034..cc084f05c58c8c3c0613dded69109fdf7ce03708`:

- `src/qual/engine/retrieval/__init__.py` - engine retrieval facade exports for canonical query, auto retrieval, excerpt lookup, payload, and ranking surfaces.
- `src/qual/engine/retrieval/fts_strategy.py` - FTS strategy snapshot normalization and deterministic hit/ranking behavior.
- `src/qual/engine/retrieval/payload.py` - deterministic payload, provenance, sparse bundle, citation, fingerprint, and basket-promotion/context reference helpers.
- `src/qual/retrieval/service.py` - canonical FTS-first retrieval service behavior, excerpt lookup, cache scope normalization, filtering, and fail-closed compatibility paths.
- `tests/unit/test_unified_retrieval.py` - approved shared-by-approval regression coverage for the branch-tip retrieval contract.

Reviewed source/test stat: `5 files changed, 492 insertions(+), 119 deletions(-)`.

Full branch-tip reviewed file surface, including packet metadata files, is the same 8 paths shown by `git diff --name-status 378cf9a74a3658058079a32f186fcd254c4a4034..HEAD`: `.codex/kickoff_packets/feat-retrieval-fts.md`, `.codex/lane_meta/feat-retrieval-fts.json`, `THREAD_PACKET.md`, `src/qual/engine/retrieval/__init__.py`, `src/qual/engine/retrieval/fts_strategy.py`, `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`, and `tests/unit/test_unified_retrieval.py`. At pre-fix tip `1483db4a5bfe8a71906d65e33c97e3224bdaf5fe`, that full range was `8 files changed, 756 insertions(+), 207 deletions(-)`; the final fixer deliverable reports the final HEAD SHA after this metadata-only packet update.

Lane-owned source/test files in the reviewed implementation range:

- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/service.py`

Shared-by-approval files in the reviewed implementation range:

- `tests/unit/test_unified_retrieval.py`

Out-of-lane tooling files in the reviewed branch-tip range:

- None.
- `codex_packet_handoff/tools/planner.py` is excluded from this retrieval handoff.
- `tests/unit/test_packet_planner.py` is excluded from this retrieval handoff.

Integrator-locked files in the reviewed branch-tip range:

- None.

## Budget/Risk

- Task budget: `4/4` high-risk tasks.
- File budget: `5/8` high-risk source/test files.
- Net source/test LOC budget: `+373` net LOC, above the default `<=300` high-risk size guideline because this packet now truthfully covers all branch-tip retrieval implementation work requested by the reviewer.
- Full branch-tip packet LOC: exceeds the high-risk metadata-inclusive size guideline because the branch includes packet regeneration commits; the merge surface is listed explicitly above.
- Size exception required: yes; this branch-tip re-review packet corrects prior traceability drift instead of narrowing away source/test changes that are already present on the branch tip. No integrator-approved exception is recorded in this worktree, so re-review should treat this as an explicit requested exception for the truthful branch-tip surface rather than as a claimed in-budget high-risk handoff.
- Shared-file approval note: Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for the `feat-retrieval-fts` lane; it exercises the canonical retrieval contract.
- Routing/provider impact: none.
- PageIndex/embeddings impact: PageIndex and embeddings remain compatibility-only fallback shims; PageIndex-only excerpt IDs fail closed for the canonical excerpt lookup path.
- Merge risk: high because the corrected packet now exposes all branch-tip retrieval source/test changes for re-review.

## Roadmap/Vision

- Roadmap items affected: MVP focus for FTS-first retrieval.
- Vision capabilities affected: Retrieval-first context handling; auditable state and workflow.
- Proposed `README.md` patch text: none.

## Commands Run

Required gates for this fixer pass:

- `make scope-check` PASS for branch `codex/feat-retrieval-fts`.
- `./quality-format.sh --check` PASS.
- `./quality-lint.sh` PASS.
- `./quality-test.sh` PASS, 125 tests.
- `./typecheck-test.sh` PASS, Python sources under `src/` compile.
- `make ci` PASS, 125 tests; includes scope-check, format, lint, typecheck, and test gates.

## Risks/Blockers

Remaining risk is review scope size: this corrected packet intentionally includes every branch-tip source/test change through `cc084f05c58c8c3c0613dded69109fdf7ce03708`. It does not touch model routing/provider configuration and does not include Textual UI console work.
