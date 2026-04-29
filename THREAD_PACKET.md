## Thread Handoff Packet

- Branch/lane: `codex/feat-retrieval-fts` / `feat-retrieval-fts`
- Packet purpose: branch-tip retrieval feature handoff for basket-promotion provenance.
- Merge candidate: the current branch tip after this code-bearing fixer commit.
- Authoritative review range for this intervention: `a4ec24861f4fd7aa6c0ca0653b882ffd402d72d1..HEAD` on `codex/feat-retrieval-fts`.
- Code-bearing implementation head in that range: reported in the final fixer response after commit creation.
- Final proposed merge HEAD SHA: reported in the final fixer response after commit creation.

## Scope Completed

This handoff keeps the FTS-first retrieval path authoritative and narrows the branch-tip change to retrieval-owned source files only. Basket-promotion candidates now carry stable query/result fingerprints, document typing hints, and a compact citation snapshot copied from the FTS excerpt provenance. Sparse payload reconstruction builds the same candidate shape when downstream engine flows rehydrate excerpt bundles from payload snapshots.

The demo-path steps advanced by this pass are "retrieve relevant material" and "promote or gather context into the basket": an engine consumer can now promote an excerpt candidate while retaining the retrieval fingerprint and citation facts needed by later revise/apply provenance.

## Tasks Completed

1. Enriched `RetrievalResult.retrieval_excerpt_bundle()` basket candidates with query fingerprint, result fingerprint, doc type/title hints, and an embedded citation snapshot.
   - Roadmap mapping: `ROADMAP.md` Milestone 3 generation provenance contract and Milestone 4 source-attribution model for retrieved chunks.
   - Product vision mapping: capability 2, Retrieval-first context handling, and capability 3, Auditable generation.
   - Demo-path step: promote or gather retrieved context into the basket.
2. Updated engine retrieval payload normalization so basket candidates reconstructed from excerpt-hit payloads retain the same citation-bearing shape.
   - Roadmap mapping: `ROADMAP.md` Milestone 4 retrieval orchestration before drafting/diff generation.
   - Product vision mapping: capability 5, Agent-to-UI protocol, because the structured payload remains consumable by CLI/A2UI flows.
   - Demo-path step: carry retrieval context forward to later revise/apply steps.

## Files Changed

- `src/qual/retrieval/service.py`
- `src/qual/engine/retrieval/payload.py`
- `THREAD_PACKET.md`

No integrator-owned `README.md`, `INTEGRATION.md`, `src/main.py`, `src/qual/cli.py`, or `src/qual/app.py` changes are included.

## Budget

- Risk: low for this intervention; source edits are inside lane-owned retrieval paths.
- Task budget: `2/8` under AGENTS default rules.
- File budget for this intervention: `3/12`.
- Current net LOC for this intervention before commit: `+73/-59` across 3 files.
- Shared-file edits: none in this intervention.
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

## Commands Run

- `python -m pytest tests/unit/test_unified_retrieval.py`: FAIL, `No module named pytest`; the repo does not require pytest for this suite.
- `python -m unittest tests.unit.test_unified_retrieval`: PASS, 55 tests.
- `python -m compileall -q src/qual/retrieval src/qual/engine/retrieval`: PASS.
- `./quality-format.sh --check`: PASS.
- `./quality-lint.sh`: PASS.
- `./quality-test.sh`: PASS, including smoke plus 124 unit tests.
- `./typecheck-test.sh`: PASS.
- `make scope-check`: PASS.
- `make ci`: PASS, including scope-check, format, lint, compileall, and smoke plus 124 unit tests.

## Risks / Blockers

- No current blockers.
- This pass intentionally does not add embeddings, PageIndex requirements, UI rendering behavior, or alternate retrieval modes.
