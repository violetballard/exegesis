## Thread Handoff Packet

- Branch/lane: `codex/feat-retrieval-fts` / `feat-retrieval-fts`
- Packet purpose: branch-tip re-review packet for the actual merge candidate, including FTS-first retrieval, basket-promotion reference plumbing, and FTS strategy snapshot isolation.
- Merge candidate: the branch tip after this fixer commit.
- Authoritative merge-review range: `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD`.
- Pre-fix packet HEAD: `6da82ca9157bb1b95cbdcd654df3d932eabf415b`.
- Reviewed scope rule: review the full branch tip range above. Do not use `adfa8cdadd43747ffbcb612e4151e262b13e52ca` as the merge-candidate endpoint.

## Branch-Tip Scope Summary

The branch keeps SQLite FTS as the MVP retrieval authority, removes the PageIndex fallback from canonical excerpt lookup, and preserves deterministic retrieval payloads for downstream engine flows. It also keeps the post-`adfa8cd` implementation work in reviewed scope: retrieval evidence now carries stable document and excerpt refs, source/context bundles normalize `retrieval_basket_promotion_refs`, downstream payload reconstruction rehydrates those refs for the context basket path, and FTS strategy hits are deep-copied around cache storage and return paths so callers cannot mutate cached retrieval evidence.

PageIndex and embeddings remain deferred/fallback-only compatibility surfaces. No routing, provider, CLI entrypoint, `README.md`, `INTEGRATION.md`, `src/main.py`, `src/qual/cli.py`, or `src/qual/app.py` changes are included.

The canonical demo path advanced by this range is:

1. Retrieve relevant material through the FTS-first retrieval path.
2. Promote or gather retrieved docs/excerpts into the basket using stable refs.
3. Carry retrieved context forward to later draft/revise/apply steps through deterministic payloads.

This advances: retrieve relevant material. The FTS-only excerpt contract makes canonical retrieval evidence deterministic and fail-closed, while stable basket-promotion refs let downstream workflow steps promote the retrieved docs/excerpts without relying on PageIndex-only fallbacks or mutable hit snapshots.

Reviewer-required traceability fix: this packet intentionally reviews `f26b3a6de39492e288fbdf8c2338dab64a6e61e5` as implementation scope in the actual branch-tip merge candidate; it is not classified as a metadata-only packet refresh.

## Code-Bearing Commits In Reviewed Scope

- `adfa8cdadd43747ffbcb612e4151e262b13e52ca`: FTS-only excerpt lookup and deterministic retrieval payload behavior.
- `6d3ca5d75d517b508fd6dfb954ac83bcc8c85591`: stable document and excerpt references for basket promotion in retrieval evidence.
- `3f09ca2f4132eff22bd3faa0e8a3e1f5411482f5`: exposes normalized basket-promotion refs through retrieval source/context/downstream payload reconstruction.
- `f26b3a6de39492e288fbdf8c2338dab64a6e61e5`: isolates FTS strategy hit snapshots with deep copies around runner output, cache storage, and returned `StrategyRun` hits.

Packet/documentation commits after `f26b3a6de39492e288fbdf8c2338dab64a6e61e5`, including this fixer commit, update packet metadata only. Runtime code changes through `f26b3a6de39492e288fbdf8c2338dab64a6e61e5` remain inside the reviewed branch-tip range. The mirrored kickoff packet and lane metadata still contain stale narrowed-target language because this sandbox rejects writes to those packet mirrors; this `THREAD_PACKET.md` remains the authoritative regenerated packet for the actual branch-tip target.

## Tasks Completed

1. Made FTS-only excerpt retrieval the branch-tip retrieval contract and preserved deterministic query/result fingerprints, citation snapshots, and provenance on FTS hits.
   - Canonical demo-path step: retrieve relevant material.
   - Roadmap mapping: `ROADMAP.md` Milestone 3 output contract readiness and Milestone 4 FTS-first retrieval/source attribution.
   - Vision mapping: capability 2, Retrieval-first context handling, and capability 3, Auditable generation.
2. Normalized retrieval payloads, source bundles, provenance bundles, sparse backfills, and missing-value handling so downstream engine flows rehydrate canonical retrieval context deterministically.
   - Canonical demo-path step: carry retrieved context forward to later draft/revise/apply steps.
   - Roadmap mapping: `ROADMAP.md` Milestone 4 retrieval orchestration and deterministic auditable retrieval.
   - Vision mapping: capability 5, Agent-to-UI protocol, because CLI/A2UI fallback consumers receive stable structured payloads.
3. Kept the post-`adfa8cd` basket promotion reference work in reviewed scope: stable doc/excerpt refs are built from FTS hits, normalized in retrieval evidence, exposed as `retrieval_basket_promotion_refs`, and preserved through source-bundle/downstream reconstruction.
   - Canonical demo-path step: promote or gather retrieved docs/excerpts into the basket.
   - Roadmap mapping: `ROADMAP.md` Milestone 3 generation provenance contract and Milestone 4 source-attribution model for retrieved chunks.
   - Vision mapping: capability 2, Retrieval-first context handling, and capability 3, Auditable generation.
4. Added and maintained approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for the FTS-first retrieval contract, sparse payload reconstruction, citation/provenance helpers, FTS-only excerpt behavior, and FTS strategy snapshot isolation.
   - Canonical demo-path step: verify the FTS-first retrieval and basket-context payload path is reproducible for the canonical demo.
   - Roadmap mapping: MVP engine stability and retrieval contract readiness.
   - Vision mapping: auditable, deterministic workflow state.

## Files Changed In Reviewed Branch-Tip Range

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

## Budget / Size Accounting

- Risk: high/shared because the reviewed range includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Task budget: `4/4` under the AGENTS high-risk/shared cap.
- File budget: `7/8` high-risk files changed in the actual branch-tip range.
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

Required gates rerun against the actual branch-tip merge candidate after this packet regeneration:

- `make scope-check`: PASS; scope-check passed for branch `codex/feat-retrieval-fts`.
- `./quality-format.sh --check`: PASS.
- `./quality-lint.sh`: PASS; shell syntax and trailing whitespace checks passed.
- `./quality-test.sh`: PASS; smoke plus 124 unit tests.
- `./typecheck-test.sh`: PASS; Python sources in `src/` compile.
- `make ci`: PASS; setup verification, scope-check, format, lint, compileall/typecheck, smoke, and 124 unit tests completed.

Fallback-review fixer gate rerun against pre-fix branch head `d564761748b01f6b96e2bc3a329556032d604f5e`:

- `make scope-check`: PASS; scope-check passed for branch `codex/feat-retrieval-fts`.
- `./quality-format.sh --check`: PASS.
- `./quality-lint.sh`: PASS; shell syntax and trailing whitespace checks passed.
- `./quality-test.sh`: PASS; smoke plus 124 unit tests.
- `./typecheck-test.sh`: PASS; Python sources in `src/` compile.
- `make ci`: PASS; setup verification, scope-check, format, lint, compileall/typecheck, smoke, and 124 unit tests completed.

## Risks / Blockers

- `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` still contain stale `adfa8cd` endpoint language because this sandbox rejects writes to those packet mirrors. This `THREAD_PACKET.md` is the authoritative regenerated packet for the actual branch tip.
- Merge risk is high only because the handoff includes approved shared regression coverage; there are no integrator-locked file edits.
- The branch intentionally does not add embeddings, PageIndex requirements, UI rendering behavior, alternate retrieval modes, routing changes, or provider changes.
- Final HEAD SHA is reported in the fixer final response after commit creation.
