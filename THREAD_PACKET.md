## Thread Handoff Packet

- Branch/lane: `codex/feat-retrieval-fts` / `feat-retrieval-fts`
- Packet purpose: corrected branch-tip re-review packet for the actual merge candidate.
- Pre-fix branch tip: `6b8bfc9633b0812d5e6d497fbd94cd9d1427361d`.
- Merge candidate: the branch tip after this fixer commit; final HEAD SHA is reported in the fixer final response.
- Authoritative reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD`.
- Reviewed scope rule: review the full branch-tip range above. Do not use `adfa8cdadd43747ffbcb612e4151e262b13e52ca` as the merge-candidate endpoint.

## Required Reviewer Fixes Addressed

1. Regenerated this handoff packet so the branch tip is no longer described as metadata-only when the reviewed range contains retrieval code changes. The packet mirrors remain blocked by filesystem permissions, as noted under Risks / Blockers.
2. Included all post-`adfa8cdadd43747ffbcb612e4151e262b13e52ca` retrieval code changes in the reviewed implementation range by using `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD`.
3. Updated scope, files changed, and risks to match the actual branch-tip range.
4. Re-ran the required gates against the corrected merge candidate; results are recorded below.

## Scope Completed

The branch keeps SQLite FTS as the MVP retrieval authority, removes the PageIndex fallback from canonical excerpt lookup, and preserves deterministic retrieval payloads for downstream engine flows. The reviewed branch-tip range also includes the post-`adfa8cd` retrieval work: stable document and excerpt refs for basket promotion, normalized `retrieval_basket_promotion_refs` in source/context bundles and downstream reconstruction, and deep-copy isolation for FTS strategy hit snapshots so callers cannot mutate cached retrieval evidence.

PageIndex and embeddings remain deferred/fallback-only compatibility surfaces. No routing, provider, CLI entrypoint, `README.md`, `INTEGRATION.md`, `src/main.py`, `src/qual/cli.py`, or `src/qual/app.py` changes are included.

The canonical demo path advanced by this range is:

1. Retrieve relevant material through the FTS-first retrieval path.
2. Promote or gather retrieved docs/excerpts into the basket using stable refs.
3. Carry retrieved context forward to later draft/revise/apply steps through deterministic payloads.

## Code-Bearing Scope In Reviewed Range

- FTS-only excerpt lookup and deterministic retrieval payload behavior.
- Stable document and excerpt references for basket promotion in retrieval evidence.
- Normalized basket-promotion refs through retrieval source/context bundles and downstream payload reconstruction.
- Deep-copy isolation around FTS strategy runner output, cache storage, and returned `StrategyRun` hits.

Packet/documentation commits are also present in `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD`, but they are not used to narrow or exclude the runtime retrieval changes above.

## Tasks Completed

1. Made FTS-only excerpt retrieval the branch-tip retrieval contract and preserved deterministic query/result fingerprints, citation snapshots, and provenance on FTS hits.
2. Normalized retrieval payloads, source bundles, provenance bundles, sparse backfills, and missing-value handling so downstream engine flows rehydrate canonical retrieval context deterministically.
3. Kept basket promotion reference work in reviewed scope: stable doc/excerpt refs are built from FTS hits, normalized in retrieval evidence, exposed as `retrieval_basket_promotion_refs`, and preserved through source-bundle/downstream reconstruction.
4. Added and maintained approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for the FTS-first retrieval contract, sparse payload reconstruction, citation/provenance helpers, FTS-only excerpt behavior, and FTS strategy snapshot isolation.

## Files Changed In Reviewed Branch-Tip Range

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

Current branch-tip diff from `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD` before this fixer commit: 7 files changed, 451 insertions, 120 deletions.

Runtime/test subset in that range before this fixer commit:

- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

Runtime/test subset stat before this fixer commit: 4 files changed, 154 insertions, 33 deletions.

## Budget / Size Accounting

- Risk: high/shared because the reviewed range includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Task budget: `4/4` under the AGENTS high-risk/shared cap.
- File budget: `7/8` high-risk files changed in the actual branch-tip range before this fixer commit.
- Shared-file edits: approved regression coverage in `tests/unit/test_unified_retrieval.py`.
- Integrator-locked files: none.
- Scope remains tight to Milestone 3/4 retrieval: FTS-first retrieval, structured/auditable basket promotion refs, and no required PageIndex/embeddings path.

## Roadmap / Vision

- Roadmap items affected:
  - `ROADMAP.md` Milestone 3: output contract readiness and generation provenance contract.
  - `ROADMAP.md` Milestone 4: FTS-first retrieval orchestration, source attribution, deterministic auditable retrieval, and deferred PageIndex/embeddings.
- Vision capabilities affected:
  - Product Vision capability 2, Retrieval-first context handling.
  - Product Vision capability 3, Auditable generation.
  - Product Vision capability 5, Agent-to-UI protocol, for stable retrieval payloads consumable by CLI/A2UI fallback flows.
- Routing/provider impact: none.
- Textual/UI impact: none.
- Alternate retrieval-mode impact: none. PageIndex and embeddings remain deferred/fallback-only.
- Proposed `README.md` patch text: none.

## Commands Run

Corrected merge-candidate gates, rerun after regenerating this packet:

- `make scope-check`: PASS; scope-check passed for branch `codex/feat-retrieval-fts`.
- `./quality-format.sh --check`: PASS.
- `./quality-lint.sh`: PASS; shell syntax and trailing whitespace checks passed.
- `./quality-test.sh`: PASS; smoke plus 124 unit tests passed.
- `./typecheck-test.sh`: PASS; Python sources in `src/` compile.
- `make ci`: PASS; setup verification, scope-check, format, lint, compileall/typecheck, smoke, and 124 unit tests passed.

## Risks / Blockers

- Merge risk is high only because the handoff includes approved shared regression coverage; there are no integrator-locked file edits.
- `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` still contain stale narrowed-range metadata because both patch-tool and direct file writes are blocked by the sandbox with `Operation not permitted`. `THREAD_PACKET.md` is the regenerated handoff packet for the actual branch-tip candidate.
- The branch intentionally does not add embeddings, PageIndex requirements, UI rendering behavior, alternate retrieval modes, routing changes, or provider changes.
- Final HEAD SHA is reported in the fixer final response after commit creation.
