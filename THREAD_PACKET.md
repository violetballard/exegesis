## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Reviewed source implementation range for this fixer pass: `e4f835c50..53829ae98`
- Reviewed source implementation head for this fixer pass: `53829ae98955c738d1fb3e8d16d3e8a6c853e840`
- Pre-fix packet head: `e4f835c50`
- Final branch tip: reported in the fixer deliverable after this packet-only commit is created.
- Scope classification: high-risk budget retained from the kickoff packet; this fixer pass itself changes only lane-owned retrieval paths.
- Packet type: retrieval feature handoff for the FTS-first retrieval lane.

## Scope Completed

This fixer pass adds stable basket-promotion fingerprints to the FTS-first retrieval payload surface. Retrieval-owned basket promotion refs now carry a deterministic `basket_item_fingerprint` derived from the excerpt identity, source hash, span, retrieval mode, query fingerprint, and result fingerprint. Sparse downstream/source-bundle reconstruction backfills the same fingerprint when only excerpt-hit snapshots survive.

The change keeps SQLite FTS as the only active retrieval path. It does not reintroduce PageIndex, embeddings, alternate routing, provider behavior, or Textual UI work. The demo-path improvement is narrow: retrieved excerpts promoted or gathered into context now have an auditable per-item fingerprint that downstream basket/revise/apply flows can compare without rehydrating the original retrieval result.

## Tasks Completed

1. Added deterministic basket-promotion item fingerprints to service-generated FTS retrieval context/source/evidence payload refs.
2. Added matching fingerprint backfill for sparse payload reconstruction from excerpt-hit snapshots.

## Canonical Demo Path

- Primary canonical demo-path step advanced: `retrieve relevant material` and `promote/gather context into the basket`.
- AGENTS.md narrowing language: this work targets the active MVP note for `FTS-first retrieval`.
- Basket promotion/gathering: limited to retrieval-owned payload/context metadata that supports later engine/demo gathering; no `feat-console` work is included.

## Files Changed

Reviewed source implementation files for `e4f835c50..53829ae98`:

- `src/qual/retrieval/service.py` - emits `basket_item_fingerprint` on canonical FTS basket-promotion refs and retrieval evidence refs.
- `src/qual/engine/retrieval/payload.py` - reconstructs the same fingerprint when sparse snapshots only preserve excerpt-hit payloads.

Reviewed source stat for this fixer pass: `2 files changed, 81 insertions(+), 30 deletions(-)`.

Lane-owned source files in this fixer pass:

- `src/qual/retrieval/service.py`
- `src/qual/engine/retrieval/payload.py`

Shared-by-approval files in this fixer pass:

- None.

Out-of-lane tooling files in this fixer pass:

- None.

Integrator-locked files in this fixer pass:

- None.

## Budget/Risk

- Task budget: `2/4` high-risk tasks.
- File budget: `2/8` high-risk files.
- Net source LOC budget: `+51` net LOC, within the `<=300` high-risk size guideline.
- Size exception required: no for this fixer pass.
- Shared-file approval note: no shared-by-approval files changed in this fixer pass.
- Routing/provider impact: none.
- PageIndex/embeddings impact: none; PageIndex and embeddings remain deferred/compatibility-only and are not active retrieval paths.
- Merge risk: low for this fixer pass; it is confined to retrieval-owned payload metadata and preserves existing contract tests.

## Roadmap/Vision

- Roadmap items affected: Milestone 4 retrieval layer; MVP focus for FTS-first retrieval.
- Vision capabilities affected: Retrieval-first context handling; auditable generation.
- Routing/provider impact note: none.
- Proposed `README.md` patch text: none.

## Commands Run

Required and focused gates for this fixer pass:

- `python -m unittest tests.unit.test_unified_retrieval` initially failed after the first edit because `RetrievalResult` called the new fingerprint helper as an instance method; fixed in the first focused attempt.
- `python -m unittest tests.unit.test_unified_retrieval` PASS, 57 tests.
- `./quality-format.sh --check` PASS.
- `git diff --check` PASS.
- `./quality-lint.sh` PASS.
- `./quality-test.sh` PASS, 126 tests.
- `./typecheck-test.sh` PASS, Python sources under `src/` compile.
- `make ci` PASS, 126 tests; includes scope-check, format, lint, typecheck, and test gates.

## Risks/Blockers

No remaining blocker for this fixer pass. The packet mirror files under `.codex` were not updated in this pass; `THREAD_PACKET.md` and the final fixer deliverable are the handoff record.
