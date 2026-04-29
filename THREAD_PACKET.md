## Thread Handoff Packet

- Branch/lane: `codex/feat-retrieval-fts` / `feat-retrieval-fts`
- Packet purpose: branch-tip retrieval feature handoff for FTS-first retrieval and auditable basket promotion references.
- Merge candidate: current branch tip after this fixer commit.
- Authoritative merge-review range: `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD` on `codex/feat-retrieval-fts`.
- Previous rejected packet issue: earlier packet text narrowed review to `adfa8cdadd43747ffbcb612e4151e262b13e52ca` while branch tip also contained implementation commits `6d3ca5d75d517b508fd6dfb954ac83bcc8c85591` and `3f09ca2f4132eff22bd3faa0e8a3e1f5411482f5`. This packet corrects that by treating the actual branch tip as the review candidate.
- Packet refresh rule for this submission: packet refresh commits after the reviewed implementation commits are metadata-only relative to `378cf9a..HEAD`; if any later commit changes retrieval code or shared regression tests, this packet must be regenerated before re-review.
- Final proposed merge HEAD SHA: reported in the final fixer response after commit creation.

## Branch-Tip Scope Completed

This branch implements the FTS-first retrieval MVP for engine flows. SQLite FTS remains the authoritative retrieval path, PageIndex and embeddings stay deferred/fallback-only compatibility surfaces, and `fetch_excerpt` now fails closed for excerpt IDs that are not available through the canonical FTS lookup path.

The actual branch tip also includes basket promotion reference work. Retrieval evidence now carries stable document and excerpt refs, retrieval source/context/downstream payloads preserve normalized `retrieval_basket_promotion_refs`, and downstream consumers can rehydrate those refs without requiring PageIndex or embeddings.

The branch-tip implementation range changes six files:

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

No integrator-owned `README.md`, `INTEGRATION.md`, `src/main.py`, `src/qual/cli.py`, or `src/qual/app.py` changes are included.

## Completed Tasks

1. Made FTS-only excerpt retrieval the branch-tip retrieval contract by removing PageIndex fallback from `RetrievalService.fetch_excerpt` and preserving deterministic query/result fingerprints, citation snapshots, and provenance on FTS hits.
   - Canonical demo-path step advanced: retrieve relevant material.
   - Roadmap mapping: `ROADMAP.md` Milestone 3 output contract readiness and Milestone 4 FTS-first retrieval/source attribution.
   - Product vision mapping: capability 2, Retrieval-first context handling, and capability 3, Auditable generation.
2. Normalized retrieval payloads, source bundles, provenance bundles, sparse backfills, and missing-value handling so downstream engine flows rehydrate canonical retrieval context deterministically.
   - Canonical demo-path step advanced: carry retrieved context forward to later draft/revise/apply steps.
   - Roadmap mapping: `ROADMAP.md` Milestone 4 retrieval orchestration and deterministic auditable retrieval.
   - Product vision mapping: capability 5, Agent-to-UI protocol, because CLI/A2UI fallback consumers receive stable structured payloads.
3. Added basket promotion reference behavior as reviewed branch-tip scope. Stable doc/excerpt refs are built from FTS hits, normalized in retrieval evidence, exposed as `retrieval_basket_promotion_refs`, and preserved through source-bundle, context-bundle, and downstream payload reconstruction.
   - Canonical demo-path step advanced: promote or gather context into the basket.
   - Roadmap mapping: `ROADMAP.md` Milestone 3 generation provenance contract and Milestone 4 source-attribution model for retrieved chunks.
   - Product vision mapping: capability 2, Retrieval-first context handling, and capability 3, Auditable generation.
4. Added and maintained approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for the FTS-first retrieval contract, sparse payload reconstruction, citation/provenance helpers, basket promotion refs, and FTS-only excerpt behavior.
   - Canonical demo-path step advanced: verify retrieve relevant material and promote/gather context into the basket for the canonical demo.
   - Roadmap mapping: MVP engine stability and retrieval contract readiness.
   - Product vision mapping: auditable, deterministic workflow state.

## Budget / Size Accounting

- Risk: high/shared because the branch-tip range includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Task budget: `4/4` under the AGENTS high-risk/shared cap.
- File budget: `6/8` high-risk files changed in this branch-tip packet.
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

Required branch-tip gates for this fixer pass:

- `make scope-check`: PASS; scope-check passed for branch `codex/feat-retrieval-fts`.
- `./quality-format.sh --check`: PASS.
- `./quality-lint.sh`: PASS, shell syntax and trailing whitespace checks passed.
- `./quality-test.sh`: PASS, smoke plus 124 unit tests.
- `./typecheck-test.sh`: PASS, Python sources in `src/` compile.
- `make ci`: PASS, including setup verification, scope-check, format, lint, compileall/typecheck, smoke, and 124 unit tests.

These outcomes are re-run after this packet correction before the final fixer commit.

## Risks / Blockers

- No current runtime blocker.
- `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` still contain stale pre-fix text because this sandbox rejected direct writes under `.codex` with `writing outside of the project; rejected by user approval settings`. This `THREAD_PACKET.md` is the regenerated packet source for the actual branch-tip candidate.
- Merge risk is high only because the handoff includes approved shared regression coverage; there are no integrator-locked file edits.
- The branch intentionally does not add embeddings, PageIndex requirements, UI rendering behavior, alternate retrieval modes, or routing/provider changes.
