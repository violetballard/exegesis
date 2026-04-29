## Thread Handoff Packet

- Branch: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Review target: final branch tip created by this fixer pass; final SHA is reported in the fixer response.
- Reviewed range: `378cf9a74a3658058079a32f186fcd254c4a4034..final fixer commit`
- Handoff type: high-risk re-review because the range includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`
- Integrator-locked files: none.
- Shared-by-approval files: `tests/unit/test_unified_retrieval.py`.

## Scope Completed

The full branch-tip merge candidate keeps retrieval FTS-first and includes all runtime/test changes from the reviewed range. It adds FTS-only excerpt lookup through `fetch_excerpt`, deterministic `retrieval_basket_promotion` context bundles, deterministic source-bundle fingerprints, and engine payload rehydration for sparse downstream/source-bundle inputs. PageIndex-only excerpt IDs fail closed under regression coverage; PageIndex and embeddings remain deferred compatibility paths, not required MVP retrieval paths.

## Completed Tasks

1. Added FTS-first excerpt lookup that backfills excerpt hits from SQLite FTS and fails closed for PageIndex-only IDs.
2. Added deterministic basket-promotion/source-bundle snapshots with stable IDs, fingerprints, citation status, query scope, intent, and date-range context.
3. Added engine retrieval payload rehydration so downstream engine flows can consume compact source/context bundles without losing provenance.
4. Added shared regression coverage for FTS excerpt backfill, facade exports, payload normalization, provenance helpers, and basket-promotion snapshots.

## Files Changed

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

## Budget Accounting

- High-risk task budget: `4`; used `4`.
- High-risk file limit: `<=8`; reviewed range changes `6` files.
- High-risk net LOC limit: `<=300`; current reviewed range before this metadata fix is `431 insertions`, `132 deletions`, net `299`.
- This fixer commit changes handoff metadata only and keeps the reviewed branch-tip range within the high-risk limits.

## Roadmap And Vision Mapping

- `ROADMAP.md` Milestone 3 Product Readiness: supports the real workflow loop by making retrieved evidence deterministic for generation provenance.
- `ROADMAP.md` Milestone 4 Retrieval Layer: implements FTS-first retrieval, source attribution for chunks, and keeps PageIndex/embeddings deferred after the demo push.
- `PRODUCT_VISION.md` capability 2, Retrieval-first context handling: generation consumes retrieved chunks instead of raw document piles.
- `PRODUCT_VISION.md` capability 6, Auditable state and workflow: payloads expose stable provenance, fingerprints, and citation state.
- Routing/provider impact: none.

## Canonical Demo Path

The basket-promotion changes advance the canonical `vault -> context -> run -> patch -> export` path at the `context -> run` boundary. They are not second-order work because the MVP run step needs compact, deterministic references to promote retrieved chunks into the context basket and preserve source attribution for generation provenance.

## Commands Run

- `make scope-check` PASS
- `./quality-format.sh --check` PASS
- `./quality-lint.sh` PASS
- `./quality-test.sh` PASS
- `./typecheck-test.sh` PASS
- `make ci` PASS

## Risks And Blockers

- Blocker: `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` could not be edited in this sandboxed fixer pass because writes were rejected as outside the writable project. This `THREAD_PACKET.md` is the authoritative corrected handoff surface for re-review.
- Residual risk: basket-promotion snapshots are compact references only; broader promotion orchestration remains separate high-risk work.
