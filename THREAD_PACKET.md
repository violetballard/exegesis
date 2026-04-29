## Thread Handoff Packet

- Branch/lane: `codex/feat-retrieval-fts` / `feat-retrieval-fts`
- Merge candidate: current branch tip after this packet-fix commit.
- Pre-fixer branch-tip SHA: `798639e001a074a4a369149ca67f8b5c02175fc9`
- Reviewed implementation range for actual branch-tip scope: `378cf9a74a3658058079a32f186fcd254c4a4034..798639e001a074a4a369149ca67f8b5c02175fc9`
- Branch-tip diff summary before this packet-fix commit: `6 files changed, 369 insertions(+), 117 deletions(-)`.
- Handoff classification: high-risk/shared because the branch includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Shared-file approval provenance: reviewer packet `fixer__feat-retrieval-fts__20260429T202122Z.prompt.txt`, finding 2, identifies `tests/unit/test_unified_retrieval.py` as the approved shared surface for `feat-retrieval-fts`.

## Required Fixes Addressed

1. This packet is regenerated against the actual branch tip `798639e001a074a4a369149ca67f8b5c02175fc9`, not the stale narrowed `adfa8cd` slice.
2. The post-`adfa8cd` retrieval payload and basket-promotion work is described below as implementation scope, with tasks, files, roadmap mapping, vision mapping, canonical demo-path step, and risk assessment.
3. Required gates are re-run against the branch-tip merge candidate after this packet is corrected and recorded below.
4. The file list and diff summary match `git diff 378cf9a74a3658058079a32f186fcd254c4a4034..798639e001a074a4a369149ca67f8b5c02175fc9`; non-metadata retrieval changes are included for review.

## Scope Completed

The actual merge candidate keeps the FTS-first excerpt lookup work and adds implementation scope for promotion-ready retrieval payloads. SQLite FTS remains authoritative for excerpt lookup. Retrieval results now expose deterministic basket-promotion excerpt references through downstream payloads, retrieval source bundles, and retrieval context bundles so the canonical demo path can promote retrieved excerpts into later context-basket workflows without re-querying or rebuilding provenance.

PageIndex and embeddings remain compatibility-only fallback surfaces outside the required excerpt path. Unsupported excerpt scopes still fail closed.

## Tasks Completed

1. Canonical demo-path step `retrieve relevant material`: make document excerpt lookup use FTS lookup results only and fail closed for unsupported document scopes.
2. Canonical demo-path step `retrieve relevant material`: normalize document IDs, query text, max-result handling, and shared regression coverage for FTS-only excerpt behavior.
3. Canonical demo-path step `promote retrieved material into context basket`: add deterministic `basket_promotion_items` and `basket_item_ids` to retrieval result context/source/downstream payloads.
4. Canonical demo-path step `promote retrieved material into context basket`: backfill basket-promotion fields through sparse retrieval source/context bundles while preserving excerpt provenance, ranks, hashes, spans, query scope, and result fingerprints.

## Files Changed

Actual branch-tip file list for `378cf9a74a3658058079a32f186fcd254c4a4034..798639e001a074a4a369149ca67f8b5c02175fc9`:

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

Implementation files in the actual branch-tip diff:

- `src/qual/retrieval/service.py`: FTS-only excerpt lookup hardening plus basket-promotion item construction on retrieval results, source bundles, and context bundles.
- `src/qual/engine/retrieval/payload.py`: downstream payload normalization/backfill for `basket_promotion_items` and `basket_item_ids`.
- `tests/unit/test_unified_retrieval.py`: approved shared regression coverage for FTS-only excerpt behavior.

Metadata/handoff files in the actual branch-tip diff:

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`

No `codex_packet_handoff/tools/planner.py` or `tests/unit/test_packet_planner.py` changes are part of this actual branch-tip diff.

## Branch-Tip Diff Summary

`git diff --stat 378cf9a74a3658058079a32f186fcd254c4a4034..798639e001a074a4a369149ca67f8b5c02175fc9`:

- `.codex/kickoff_packets/feat-retrieval-fts.md`: `36` changed lines.
- `.codex/lane_meta/feat-retrieval-fts.json`: `155` changed lines.
- `THREAD_PACKET.md`: `157` changed lines.
- `src/qual/engine/retrieval/payload.py`: `20` insertions.
- `src/qual/retrieval/service.py`: `80` changed lines.
- `tests/unit/test_unified_retrieval.py`: `38` changed lines.
- Total: `6 files changed, 369 insertions(+), 117 deletions(-)`.

## Budget / Risk

- Risk: high/shared.
- Task budget: `4/4`; within the high-risk task cap.
- Actual branch-tip file count: `6`; within the high-risk 8-file guideline.
- Actual branch-tip size: `369 insertions(+), 117 deletions(-)`, net `+252`; within the high-risk `<=300` net LOC guideline.
- Integrator-locked files: none.
- Shared-by-approval files: `tests/unit/test_unified_retrieval.py`.
- Routing/provider impact: none.
- Risk assessment: basket-promotion fields expand retrieval payload shape and are live implementation scope. Risk is bounded to retrieval-owned modules plus the already-approved shared retrieval regression file; downstream consumers receive additive fields and existing PageIndex/embedding fallback posture is unchanged.

## Roadmap / Vision Mapping

- Roadmap items affected: `ROADMAP.md` Milestone 3 Product Readiness and Milestone 4 Retrieval Layer.
- Vision capabilities affected: `PRODUCT_VISION.md` capability 2, Retrieval-first context handling, and capability 6, Auditable state and workflow.
- Canonical demo-path step advanced: `retrieve relevant material` and `promote retrieved material into context basket`.
- Proposed `README.md` patch text: none.

## Commands Run

- `make scope-check`: PASS; no branch policy was found for `codex/feat-retrieval-fts`, then scope-check passed.
- `./quality-format.sh --check`: PASS.
- `./quality-lint.sh`: PASS.
- `./quality-test.sh`: PASS; smoke passed and 124 unit tests passed.
- `./typecheck-test.sh`: PASS; Python sources under `src/` compile.
- `make ci`: PASS; scope-check, format, lint, typecheck, smoke, and 124 unit tests completed successfully.

## Risks / Blockers

- No implementation blocker is known.
- Re-review should use the actual branch-tip scope above and should not exclude the non-metadata retrieval code changes from review.
- Packet mirror files under `.codex/` remain stale because this sandbox rejects writes to `.codex/kickoff_packets/feat-retrieval-fts.md` with `PermissionError: [Errno 1] Operation not permitted`. `THREAD_PACKET.md` is the corrected handoff source of truth for this fixer pass.
