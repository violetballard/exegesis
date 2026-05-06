## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Handoff type: high-risk split handoff for the FTS-first retrieval lane.
- Authoritative reviewed implementation range: `2dbe7796388d7fc5a706798e23aca579ec46b071..ca9fd136c478d43b48161569709fa52ed9ff1503`.
- Reviewed implementation head: `ca9fd136c478d43b48161569709fa52ed9ff1503`.
- Packet refresh commits after `ca9fd136c478d43b48161569709fa52ed9ff1503` are handoff metadata only and are not part of the reviewed implementation range.
- Scope classification: high-risk because this split includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Approved shared-file note: `tests/unit/test_unified_retrieval.py` is approved shared-by-approval regression coverage for this retrieval lane.
- Integrator-locked files: none.

## Scope Completed

This split keeps sparse FTS context rehydration self-describing when downstream engine flows rebuild basket promotion refs from excerpt-hit snapshots. Rebuilt basket refs now inherit the enclosing FTS policy/backend/mode snapshot when thin excerpt hits no longer carry those fields directly, so basket/context promotion remains deterministic, auditable, and explicitly FTS-first.

Canonical demo-path step advanced: `retrieve relevant material`. This split also supports `promote or gather context into the basket` by keeping promotion-ready basket refs tied to `sqlite_fts` / `fts_first` policy identity even from sparse context bundles.

## Tasks Completed

1. Sparse policy fallback: advances `retrieve relevant material` by deriving rebuilt basket ref `retrieval_backend`, `retrieval_mode`, and `retrieval_policy` from the enclosing FTS snapshot when excerpt-hit fields are absent.
2. Shared regression coverage: advances `retrieve relevant material` by proving sparse context bundle basket rehydration still emits `sqlite_fts`, `fts_first`, and active `fts` policy identity after excerpt-hit policy fields are stripped.
3. Handoff metadata refresh: records the reviewed implementation range, files changed, commands run, roadmap/vision mapping, and remaining risk status for this split.

Final demo-path statement: this work keeps sparse retrieval outputs promotion-ready for basket/context flows without introducing PageIndex or embeddings as active retrieval paths.

## Files Changed

Authoritative reviewed implementation range: `2dbe7796388d7fc5a706798e23aca579ec46b071..ca9fd136c478d43b48161569709fa52ed9ff1503`.

- `src/qual/engine/retrieval/payload.py` - sparse excerpt-hit basket ref reconstruction now falls back to the enclosing normalized FTS retrieval policy/backend/mode.
- `tests/unit/test_unified_retrieval.py` - approved shared regression coverage for sparse basket ref policy identity after excerpt-hit policy fields are stripped.

Metadata-only packet refresh after reviewed implementation head:

- `THREAD_PACKET.md` - handoff packet refreshed for this split.

## Diff Evidence

Command: `git diff --stat 2dbe7796388d7fc5a706798e23aca579ec46b071..ca9fd136c478d43b48161569709fa52ed9ff1503`

```text
 src/qual/engine/retrieval/payload.py | 39 +++++++++++++++++++++++++++++++++---
 tests/unit/test_unified_retrieval.py | 21 +++++++++++++++++++
 2 files changed, 57 insertions(+), 3 deletions(-)
```

Command: `git diff --numstat 2dbe7796388d7fc5a706798e23aca579ec46b071..ca9fd136c478d43b48161569709fa52ed9ff1503`

```text
36	3	src/qual/engine/retrieval/payload.py
21	0	tests/unit/test_unified_retrieval.py
```

## Budget/Risk

- Task budget: `3/4` high-risk task groups.
- File count for authoritative reviewed implementation range: `2 files changed`.
- Size accounting for authoritative reviewed implementation range: `57 insertions(+), 3 deletions(-)`, net `+54 LOC`.
- AGENTS high-risk file/size status: fits `<=8 files` and `<=300 net LOC`.
- Integrator exception status: approved shared regression coverage in `tests/unit/test_unified_retrieval.py`; no integrator-locked files changed.
- Routing/provider impact: none.
- PageIndex/embeddings impact: remain compatibility-only/deferred; no active non-FTS retrieval path is introduced.
- Remaining risks/blockers: none known for this split.

## Roadmap/Vision

- Roadmap items affected: `ROADMAP.md` Milestone 3 generation provenance contract and Milestone 4 retrieval source-attribution/auditable deterministic retrieval.
- Vision capability affected: retrieval-backed context, retrieval-first context handling, auditable outputs, and reliable local-first state.
- Architecture alignment: FTS remains the required local retrieval path. PageIndex and embeddings stay compatibility-only/deferred and fail closed.
- Canonical demo-path mapping: advances `retrieve relevant material` and supports `promote or gather context into the basket`.
- Routing/provider impact note: none.
- Proposed `README.md` patch text: none.

## Commands Run

- `python -m pytest tests/unit/test_unified_retrieval.py -q` - not run because `pytest` is not installed in this environment.
- `python -m unittest tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_retrieval_context_bundle_helper_rebuilds_sparse_basket_refs_from_excerpt_hits` - passed.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - passed smoke tests and 148 unit tests.
- `./typecheck-test.sh` - passed Python source compilation under `src/`.
- `make ci` - passed setup, scope-check, format, lint, typecheck, smoke tests, and 148 unit tests.

## Metadata Write Note

The root `THREAD_PACKET.md` is the authoritative regenerated handoff packet for this split. Re-review should anchor implementation scope to `ca9fd136c478d43b48161569709fa52ed9ff1503` and range `2dbe7796388d7fc5a706798e23aca579ec46b071..ca9fd136c478d43b48161569709fa52ed9ff1503`; packet refresh commits after that reviewed implementation head are metadata only unless they change retrieval code or the approved shared regression file.
