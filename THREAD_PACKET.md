## Thread Handoff Packet

- Branch/lane: `codex/feat-retrieval-fts` / `feat-retrieval-fts`
- Packet purpose: reviewer-fix re-review packet correcting branch-tip traceability.
- Merge candidate: the current branch tip after this metadata-only fixer commit.
- Authoritative review range for this merge candidate: `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD` on `codex/feat-retrieval-fts`.
- Code-bearing implementation head in that range: `67b69048f63bfd646611f97c92c2c9a9066d0479`.
- Packet-fix commits after the code-bearing head, including `a1c0a08f686f46c7c101f4f6a23c23e2b1430255` and this fixer commit, are metadata-only but remain inside the proposed merge range.
- Earlier narrowed-slice packet text for `adfa8cdadd43747ffbcb612e4151e262b13e52ca` is superseded. This handoff submits the full branch-tip range, not the narrowed slice.
- Final proposed merge HEAD SHA: reported in the fixer response after commit creation.

## Scope Completed

This handoff covers the full branch-tip implementation surface from `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD`, including every code-bearing commit proposed for merge.

SQLite FTS remains the MVP-authoritative retrieval path. PageIndex and embeddings remain compatibility-only fallback shims and are not reintroduced as required retrieval paths. The branch makes the engine retrieval payload more deterministic and auditable by using FTS-only excerpt lookup, backfilling provenance/citation/context-bundle snapshots, and exposing basket-promotion candidate payloads for downstream CLI/A2UI flows.

The actual full work makes the canonical demo-path steps "retrieve relevant material" and "promote or gather context into the basket" more real: retrieval returns deterministic source evidence, excerpt/citation context, and basket-promotion candidates that can be carried forward without hidden fallback behavior.

## Tasks Completed

1. Changed `RetrievalService.fetch_excerpt` and the engine retrieval facade to use the canonical FTS excerpt lookup path and fail closed for unknown or non-FTS excerpt IDs, with shared regression coverage in `tests/unit/test_unified_retrieval.py`.
   - Roadmap mapping: `ROADMAP.md` Milestone 4 FTS-first retrieval orchestration and auditable deterministic retrieval.
   - Product vision mapping: capability 2, Retrieval-first context handling.
   - Demo-path step: retrieve relevant material.
2. Stabilized retrieval provenance and payload backfill in `src/qual/engine/retrieval/payload.py`, including deterministic query, policy, citation, document-hit, excerpt-hit, context-bundle, and retrieval-summary snapshots.
   - Roadmap mapping: `ROADMAP.md` Milestone 3 generation provenance contract and Milestone 4 source-attribution model for retrieved chunks.
   - Product vision mapping: capability 3, Auditable generation.
   - Demo-path step: retrieve relevant material with auditable source evidence.
3. Exposed retrieval basket-promotion candidates from `src/qual/retrieval/service.py` and normalized those candidates in `src/qual/engine/retrieval/payload.py`.
   - Roadmap mapping: `ROADMAP.md` Milestone 3 output contract readiness and Milestone 4 retrieval orchestration before drafting/diff generation.
   - Product vision mapping: capability 2, Retrieval-first context handling, and capability 5, A2UI-compatible structured artifacts.
   - Demo-path step: promote or gather context into the basket.
4. Regenerated branch handoff metadata so `Scope completed`, `Tasks completed`, `Files changed`, roadmap/product-vision mapping, budget accounting, and gate reporting describe the actual branch-tip merge candidate instead of the earlier narrowed `adfa8cd...` slice.
   - Roadmap mapping: `ROADMAP.md` sprint cadence and review-first promotion into integrator.
   - Product vision mapping: handoff alignment rule requiring roadmap and vision mapping.
   - Demo-path step: makes the review packet traceable for the full retrieval work being promoted.

## Files Changed

Code and test files in the authoritative review range:

- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

Packet/metadata files in the authoritative review range:

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`

No integrator-owned `README.md`, `INTEGRATION.md`, `src/main.py`, `src/qual/cli.py`, or `src/qual/app.py` changes are included.

## Budget

- Risk: high, because the range includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Task budget: `4/4` under AGENTS high-risk rules.
- File budget for the authoritative range: `6/8`.
- Current net LOC for the authoritative range after this metadata-only fixer edit: `+468/-169` across 6 files.
- Shared-file approval note: `tests/unit/test_unified_retrieval.py` is the only shared-by-approval regression surface in this handoff.
- Integrator-locked files: none.

## Roadmap / Vision

- Roadmap items affected:
  - `ROADMAP.md` Milestone 3 Product Readiness: generation provenance contract and output contract readiness.
  - `ROADMAP.md` Milestone 4 Retrieval Layer: FTS-first retrieval orchestration, source attribution, deterministic auditable retrieval, and deferred PageIndex/embeddings.
- Vision capabilities affected:
  - Product Vision capability 2, Retrieval-first context handling.
  - Product Vision capability 3, Auditable generation.
  - Product Vision capability 5, Agent-to-UI protocol, for basket-promotion candidate payloads consumable by CLI/A2UI flows.
- Canonical demo-path step advanced: "retrieve relevant material" and "promote or gather context into the basket."
- Routing/provider impact: none.
- Textual/UI impact: none.
- Alternate retrieval-mode impact: none. PageIndex and embeddings remain deferred/fallback-only.
- Proposed `README.md` patch text: none.

## Reviewer Required Fixes Addressed

1. The handoff now has one authoritative merge-review range: `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD` on `codex/feat-retrieval-fts`.
2. `Scope completed`, `Tasks completed`, and `Files changed` include every code-bearing commit in the proposed merge range, including retrieval provenance backfill and basket-promotion candidate work.
3. Each actual task is mapped to `ROADMAP.md` Milestone 3 / Milestone 4 and `PRODUCT_VISION.md` capabilities, including basket-promotion candidate payloads.
4. Budget compliance is restated against the actual full range.
5. Required gates are rerun after this final metadata-only packet correction; outcomes are reported below and in the fixer response.

## Commands Run

Required gates rerun after correcting the handoff packet:

- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS, including smoke plus 124 unit tests
- `./typecheck-test.sh`: PASS
- `make ci`: PASS, including scope-check, format, lint, compileall, and smoke plus 124 unit tests

## Risks / Blockers

- The branch history contains prior packet-refresh commits with stale narrowed-slice descriptions. This packet supersedes those descriptions and submits the actual branch-tip range for re-review.
- `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` still contain older mirror text because this sandbox returns `Operation not permitted` when writing those paths. Treat this `THREAD_PACKET.md` as the regenerated source of truth for re-review.
- No current blockers.
