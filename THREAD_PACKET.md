## Thread Handoff Packet

- Branch/lane: `codex/feat-retrieval-fts` / `feat-retrieval-fts`
- Packet purpose: branch-tip retrieval feature handoff for FTS-first retrieval and basket-promotion provenance.
- Merge candidate: the current branch tip after this fixer commit.
- Authoritative merge-review range: `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD` on `codex/feat-retrieval-fts`.
- Code-bearing commits included in the range: all retrieval code and shared regression commits after `378cf9a74a3658058079a32f186fcd254c4a4034`, including the FTS-only excerpt contract at `adfa8cdadd43747ffbcb612e4151e262b13e52ca`, the basket candidate/provenance work through `cd9b940636674db4c97c811a5c31ba21e5b2a1ac`, and the later retrieval evidence traceability change at `3a03c2a15f675c690fe42f89a5692c5b3f258315`.
- Final proposed merge HEAD SHA: reported in the final fixer response after commit creation.

## Scope Completed

This branch-tip handoff keeps SQLite FTS authoritative for MVP retrieval. It adds deterministic FTS-only excerpt lookup behavior, stable retrieval query/result fingerprints, deterministic source/provenance/citation payloads, and fail-closed handling for unsupported non-FTS excerpt paths. It also exposes retrieval excerpt candidates that can be promoted into the context basket while preserving query fingerprint, result fingerprint, document hints, citation facts, and FTS provenance.

Sparse engine payload reconstruction now rebuilds the same citation-bearing candidate shape from excerpt-hit snapshots, so downstream engine, CLI, and A2UI fallback flows can carry retrieved context forward without reinterpreting retrieval internals. PageIndex and embeddings remain deferred/fallback-only compatibility surfaces; they are not required paths for this handoff.

The canonical demo path advanced by this range is:

1. Retrieve relevant material through the FTS-first retrieval path.
2. Gather or promote retrieved excerpts into the context basket with citation-bearing provenance.
3. Carry retrieval context forward to later draft/revise/apply steps through deterministic payloads.

## Tasks Completed

1. Made FTS-only excerpt retrieval the branch-tip retrieval contract and preserved deterministic query/result fingerprints, citation snapshots, and provenance on FTS hits.
   - Demo-path step advanced: retrieve relevant material.
   - Roadmap mapping: `ROADMAP.md` Milestone 3 real workflow loop and Milestone 4 FTS-first retrieval/source attribution.
   - Product vision mapping: capability 2, Retrieval-first context handling, and capability 3, Auditable generation.
2. Normalized retrieval payloads, source bundles, provenance bundles, sparse backfills, and missing-value handling so downstream engine flows rehydrate canonical retrieval context deterministically.
   - Demo-path step advanced: carry retrieval context forward to later draft/revise/apply steps.
   - Roadmap mapping: `ROADMAP.md` Milestone 4 retrieval orchestration and deterministic auditable retrieval.
   - Product vision mapping: capability 5, Agent-to-UI protocol, because CLI/A2UI fallback consumers receive stable structured payloads.
3. Added basket-promotion candidate payloads to excerpt bundles, including query/result fingerprints, doc type/title hints, rank/span/hash fields, and compact citation snapshots copied from FTS excerpt provenance.
   - Demo-path step advanced: gather or promote retrieved excerpts into the context basket.
   - Roadmap mapping: `ROADMAP.md` Milestone 3 generation provenance contract and Milestone 4 source attribution model for retrieved chunks.
   - Product vision mapping: capability 2, Retrieval-first context handling, and capability 3, Auditable generation.
4. Added and maintained approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for the FTS-first retrieval contract, sparse payload reconstruction, citation/provenance helpers, and basket-promotion candidate shape.
   - Demo-path step advanced: verifies the retrieval and basket-promotion path is reproducible for the canonical demo.
   - Roadmap mapping: MVP engine stability and retrieval contract readiness.
   - Product vision mapping: auditable, deterministic workflow state.

## Files Changed

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

No integrator-owned `README.md`, `INTEGRATION.md`, `src/main.py`, `src/qual/cli.py`, or `src/qual/app.py` changes are included.

## Budget / Size Accounting

- Risk: high/shared because the actual merge-review range includes the approved shared regression file `tests/unit/test_unified_retrieval.py`.
- Task budget: `4/4` under the AGENTS high-risk/shared cap.
- File budget: `6/8` high-risk files changed.
- Implementation-only delta, excluding packet metadata files: `3 files changed, 344 insertions(+), 89 deletions(-)`.
- Packet-inclusive delta before this final metadata refresh: `6 files changed, 601 insertions(+), 179 deletions(-)`.
- This final fixer commit changes packet metadata only; the final packet-inclusive shortstat is reported with the final HEAD SHA after commit creation.
- Shared-file edits: approved regression coverage in `tests/unit/test_unified_retrieval.py`.
- Integrator-locked files: none.

## Roadmap / Vision

- Roadmap items affected:
  - `ROADMAP.md` Milestone 3: real workflow loop, generation provenance contract, and output contract readiness.
  - `ROADMAP.md` Milestone 4: FTS-first retrieval orchestration, source attribution, deterministic auditable retrieval, and deferred PageIndex/embeddings.
- Vision capabilities affected:
  - Product Vision capability 2, Retrieval-first context handling.
  - Product Vision capability 3, Auditable generation.
  - Product Vision capability 5, Agent-to-UI protocol, for basket-promotion candidate payloads consumable by CLI/A2UI fallback flows.
- Routing/provider impact: none.
- Textual/UI impact: none.
- Alternate retrieval-mode impact: none. PageIndex and embeddings remain deferred/fallback-only.
- Proposed `README.md` patch text: none.

## Commands Run

- `make scope-check`: PASS; scope-check reported no branch policy for `codex/feat-retrieval-fts` and passed for the branch.
- `./quality-format.sh --check`: PASS.
- `./quality-lint.sh`: PASS, shell syntax and trailing whitespace checks passed.
- `./quality-test.sh`: PASS, smoke plus 124 unit tests.
- `./typecheck-test.sh`: PASS, Python sources in `src/` compile.
- `make ci`: PASS, including setup verification, scope-check, format, lint, compileall/typecheck, smoke, and 124 unit tests.

Prior useful local checks in this range:

- `python -m pytest tests/unit/test_unified_retrieval.py`: FAIL, `No module named pytest`; the repo does not require pytest for this suite.
- `python -m unittest tests.unit.test_unified_retrieval`: PASS, 55 tests.
- `python -m compileall -q src/qual/retrieval src/qual/engine/retrieval`: PASS.

## Risks / Blockers

- No current blockers.
- Merge risk is high only because the handoff includes approved shared regression coverage; there are no integrator-locked file edits.
- The branch intentionally does not add embeddings, PageIndex requirements, UI rendering behavior, or alternate retrieval modes.
