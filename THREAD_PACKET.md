## Thread Handoff Packet

- Branch/lane: `codex/feat-retrieval-fts` / `feat-retrieval-fts`
- Packet purpose: authoritative branch-tip re-review packet for the actual merge candidate.
- Merge candidate: current `HEAD` after this packet-only fixer commit; final HEAD SHA is reported by the fixer.
- Authoritative reviewed range: `d7fd5d200358287fa42a18d39e2b277463b9b69f..HEAD`.
- Scope rule: review the full range above. Do not use `adfa8cdadd43747ffbcb612e4151e262b13e52ca` as the endpoint, and do not treat later retrieval-code commits as metadata-only.
- Packet mirror note: `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` still contain older narrowed-slice wording. This sandbox rejects writes to those mirrored `.codex` paths as outside the writable project scope, so this `THREAD_PACKET.md` file is the authoritative branch-tip handoff packet.

## Required Reviewer Fixes Addressed

1. Regenerated the handoff packet against the actual merge candidate range, `d7fd5d200358287fa42a18d39e2b277463b9b69f..HEAD`.
2. Included every non-metadata branch-tip change in the reviewed implementation scope, including post-`adfa8cdadd43747ffbcb612e4151e262b13e52ca` retrieval changes.
3. Re-ran the required gates at the reviewed branch tip; outcomes are recorded below.
4. Tightened roadmap and vision mapping to the canonical demo path steps `retrieve relevant material`, `promote/gather context into the basket`, and carry retrieved context forward.
5. Kept the shared test-file exception explicit for `tests/unit/test_unified_retrieval.py` and applies the high-risk 4-task budget to the complete reviewed slice.

## Scope Completed

The branch keeps SQLite FTS as the MVP retrieval authority, removes PageIndex fallback from canonical excerpt lookup, preserves deterministic retrieval payloads for downstream engine flows, and exposes stable document/excerpt refs for basket promotion. The actual branch-tip range also includes canonical retrieval facade exports, compatibility-only PageIndex/embeddings shims, query and constraint normalization, source/context bundle reconstruction, provenance/citation backfills, cache/snapshot isolation, retrieval promotion fingerprints, and packet-planner support for demo-path metadata.

Canonical demo path advanced:

1. `retrieve relevant material`: FTS-first retrieval and FTS-only excerpt lookup return deterministic hit, provenance, citation, and query snapshots.
2. `promote/gather context into the basket`: retrieved docs/excerpts carry stable basket promotion refs, candidate refs, fingerprints, and audit metadata.
3. Carry retrieved context forward: source/context bundles and sparse payload reconstruction preserve retrieval evidence for later draft/revise/apply steps.

## Tasks Completed

1. FTS-first retrieval contract: made SQLite FTS the canonical retrieval path, kept PageIndex/embeddings fallback-only, exported canonical query/facade helpers, and made excerpt lookup fail closed outside the FTS contract.
2. Deterministic retrieval payloads: normalized query constraints, date ranges, booleans, section hints, provenance/citation/source bundles, sparse backfills, cache keys, and hit snapshots for downstream engine reconstruction.
3. Basket promotion and audit refs: exposed stable doc/excerpt promotion refs, promotion candidates, fingerprints, ranked IDs, context status, and audit fields for gathered retrieval evidence.
4. Regression and packet coverage: maintained approved shared coverage in `tests/unit/test_unified_retrieval.py` and updated packet-planner tests/metadata so handoff packets can state the demo-path mapping.

## Files Changed In Reviewed Range

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`
- `codex_packet_handoff/tools/planner.py`
- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/embeddings_strategy.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/pageindex_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/__init__.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_packet_planner.py`
- `tests/unit/test_unified_retrieval.py`

Runtime/test files in retrieval scope:

- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/embeddings_strategy.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/pageindex_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/__init__.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

## Budget / Size Accounting

- Risk: high/shared because the reviewed range includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Task budget: `4/4` under the AGENTS high-risk/shared cap.
- Shared-file exception: `tests/unit/test_unified_retrieval.py` is approved shared regression coverage for this lane.
- Integrator-locked files: none.
- File budget with this packet refresh applied: `13/8` high-risk files changed in the actual branch-tip range.
- Size budget with this packet refresh applied: 13 files changed, 2017 insertions, 271 deletions, net `+1746`.
- Runtime/test retrieval subset with this packet refresh applied: 8 files changed, 1650 insertions, 160 deletions, net `+1490`; this exceeds the high-risk file and net LOC budget and is called out here for reviewer/integrator decision instead of hidden behind a narrowed slice.
- Budget status: high-risk task count is within cap, but file and size budgets are exceeded by the accumulated branch-tip merge candidate.

## Roadmap / Vision

- Roadmap items affected: `ROADMAP.md` Milestone 3 output/provenance contract readiness; Milestone 4 FTS-first retrieval orchestration, source attribution, deterministic auditable retrieval, and deferred PageIndex/embeddings.
- Vision capabilities affected: Product Vision capability 2, retrieval-first context handling; capability 3, auditable generation; capability 5, A2UI-compatible stable retrieval payloads.
- Routing/provider impact: none.
- Textual/UI impact: none.
- Alternate retrieval-mode impact: none. PageIndex and embeddings remain deferred/fallback-only.
- Proposed `README.md` patch text: none.

## Commands Run

Required final gates against the corrected merge candidate:

- `make scope-check`: PASS.
- `./quality-format.sh --check`: PASS.
- `./quality-lint.sh`: PASS.
- `./quality-test.sh`: PASS.
- `./typecheck-test.sh`: PASS.
- `make ci`: PASS.

## Risks / Blockers

- Merge risk remains high because the actual range includes approved shared regression coverage and exceeds the high-risk file/size budgets.
- The reviewed range intentionally includes post-`adfa8cdadd43747ffbcb612e4151e262b13e52ca` retrieval code-bearing commits. They are part of the merge candidate and must be reviewed.
- The `.codex` packet mirror files are stale and write-blocked in this sandbox; this `THREAD_PACKET.md` packet is the authoritative branch-tip handoff source.
- The branch intentionally does not add required embeddings, required PageIndex routing, UI rendering behavior, alternate retrieval modes, model routing changes, or provider changes.
- Final HEAD SHA is reported by the fixer after commit creation.
