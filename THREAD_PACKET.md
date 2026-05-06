## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Handoff type: shared/high-risk retrieval feature hardening handoff for the FTS-first retrieval lane.
- Implementation base before this split: `3078e7d5d8d67605b8c8208383ecdcfa6310471f`.
- Final branch tip: reported in the final handoff after commit creation.
- Reviewed implementation range for this split: `3078e7d5d8d67605b8c8208383ecdcfa6310471f..FINAL_BRANCH_TIP`.
- Scope classification: high-risk under the retrieval kickoff packet because the lane handoff carries approved shared regression coverage history; this split itself changes only lane-owned implementation code plus this handoff packet.
- Integrator-locked files: none.

## Scope Completed

This split hardens direct engine-facing retrieval bundle normalization so explicit stale backend or mode fields fail closed at every canonical bundle boundary. Citation, doc, excerpt, summary, manifest, and evidence snapshots now validate any present top-level `retrieval_backend` and `retrieval_mode` values against the FTS-first MVP contract without adding missing fields or changing stable sparse snapshot shapes.

Canonical demo-path step advanced: `retrieve relevant material`. This also supports `promote or gather context into the basket` by preventing stale PageIndex or hybrid retrieval identities from surviving in sparse bundle snapshots that are later rebuilt into downstream payloads, context bundles, and basket promotion references.

## Tasks Completed

1. Bundle identity guard: added shared validation for explicit `retrieval_backend` and `retrieval_mode` fields on direct citation/doc/excerpt/summary/manifest/evidence snapshots.
2. Source-bundle fail-closed ordering: validates top-level sparse payload backend/mode before derived doc/excerpt bundles are rebuilt, preserving the existing source-bundle error contract.
3. Shape stability: kept absent sparse identity fields absent so existing deterministic bundle equality and fingerprints remain stable.
4. Verification and handoff: re-ran the unified retrieval suite and all required local gates, then refreshed this handoff packet.

Final demo-path statement: retrieval output remains FTS-first, deterministic, and promotion-ready, while explicit stale PageIndex, hybrid, or non-`sqlite_fts` bundle identities are rejected before engine consumers can treat them as canonical.

## Files Changed

Implementation base before this split: `3078e7d5d8d67605b8c8208383ecdcfa6310471f`.

- `src/qual/engine/retrieval/payload.py` - direct retrieval bundle snapshots now validate explicit backend/mode identity fields and sparse source payloads validate top-level backend/mode before rebuilding nested bundles.
- `THREAD_PACKET.md` - handoff packet refreshed with required `INTEGRATION.md` fields.

## Diff Evidence

Command: `git diff --stat HEAD -- src/qual/engine/retrieval/payload.py`

```text
 src/qual/engine/retrieval/payload.py | 42 ++++++++++++++++++++++++++++++++++++
 1 file changed, 42 insertions(+)
```

Command: `git diff --numstat HEAD -- src/qual/engine/retrieval/payload.py`

```text
42	0	src/qual/engine/retrieval/payload.py
```

## Budget/Risk

- Task budget: `4/4` high-risk task groups.
- File count for implementation change before packet refresh: `1 file changed`.
- Size accounting for implementation change before packet refresh: `42 insertions(+), 0 deletions(-)`, net `42 LOC`.
- AGENTS file/size status: fits high-risk limits of `<=8 files` and `<=300 net LOC`.
- Shared/integrator exception status: none needed; no shared regression or integrator-locked file changed in this split.
- Routing/provider impact: none.
- PageIndex/embeddings impact: remain compatibility-only/deferred identifiers; explicit stale PageIndex, hybrid, or non-FTS bundle identity values now fail closed at more direct bundle boundaries.
- Remaining risks/blockers: none known for this split.

## Roadmap/Vision

- Roadmap items affected: `ROADMAP.md` Milestone 3 generation provenance contract and Milestone 4 FTS-first retrieval orchestration/source-attribution/auditable deterministic retrieval.
- Vision capability affected: retrieval-backed context, retrieval-first context handling, auditable outputs, and reliable local-first state.
- Architecture alignment: FTS remains the required local retrieval path. PageIndex and embeddings stay compatibility-only/deferred and explicit stale backend/mode identities fail closed in engine-facing retrieval bundles.
- Canonical demo-path mapping: advances `retrieve relevant material` and supports `promote or gather context into the basket`.
- Routing/provider impact note: none.
- Proposed `README.md` patch text: none.

## Commands Run

- `python3 -m unittest tests.unit.test_unified_retrieval -v` - first run failed after the initial draft changed sparse bundle shapes; narrowed the implementation and re-ran.
- `python3 -m unittest tests.unit.test_unified_retrieval -v` - passed, 81 tests.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - passed smoke tests and 150 unit tests.
- `./typecheck-test.sh` - passed Python source compilation under `src/`.
- `make ci` - passed setup, scope-check, format, lint, build, typecheck, smoke tests, and 150 unit tests.

## Metadata Write Note

The root `THREAD_PACKET.md` is the authoritative regenerated handoff packet for this split. The final branch tip is intentionally reported in the final handoff after commit creation because embedding the commit SHA inside the commit would become stale immediately.
