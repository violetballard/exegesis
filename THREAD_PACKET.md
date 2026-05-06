## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Handoff type: high-risk split handoff for the FTS-first retrieval lane.
- Authoritative reviewed implementation range: `f2649eade7c028d46452a81ccf8b1a585a028ba8..69b3ca51841e749c604d00d6cdc6c03a09b1519b`.
- Packet refresh commits after `69b3ca51841e749c604d00d6cdc6c03a09b1519b` are handoff metadata only and are not part of the reviewed implementation range.
- Scope classification: high-risk because this split includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Approved shared-file note: `tests/unit/test_unified_retrieval.py` is approved shared-by-approval regression coverage for this retrieval lane.
- Integrator-locked files: none.

## Scope Completed

This packet supersedes earlier `feat-retrieval-fts` handoff packets. Re-review should use only the authoritative reviewed implementation range above for implementation file lists, diff stats, task accounting, and ownership/risk accounting.

This split keeps FTS retrieval promotion identity deterministic without introducing PageIndex or embeddings as required retrieval paths. Sparse citation bundles and excerpt-hit snapshots now rehydrate promotion-ready basket refs with stable `basket_item_id` aliases and document-rank provenance. Direct FTS excerpt lookup audit events carry ordered basket item IDs and fingerprints for downstream basket/context promotion auditability.

Canonical demo-path step advanced: `retrieve relevant material`. This split also supports `promote or gather context into the basket` by preserving auditable FTS lookup identity and promotion-ready basket references.

## Tasks Completed

1. Direct FTS excerpt audit identity: advances `retrieve relevant material` by carrying canonical `basket_item_ids` and `basket_item_fingerprints` in direct `retrieve_fts_excerpt`/`fetch_excerpt` audit records.
2. Sparse basket alias rehydration: advances `retrieve relevant material` and supports `promote or gather context into the basket` by restoring explicit `basket_item_id` aliases when sparse context bundles retain only canonical item identity.
3. Document-rank promotion provenance: advances `retrieve relevant material` and supports `promote or gather context into the basket` by preserving `doc_rank` when basket refs rebuild from surviving doc-hit or doc-citation snapshots.
4. Shared regression coverage: advances `retrieve relevant material` by adding approved shared tests for direct FTS excerpt audit identity, sparse basket alias rehydration, citation-bundle basket ref reconstruction, and document-rank preservation.

Final demo-path statement: this work makes `retrieve relevant material` more real by keeping FTS lookup identity deterministic and promotion-ready for basket/context flows.

## Files Changed

Authoritative reviewed implementation range: `f2649eade7c028d46452a81ccf8b1a585a028ba8..69b3ca51841e749c604d00d6cdc6c03a09b1519b`.

- `THREAD_PACKET.md` - handoff packet refreshed for this split.
- `src/qual/engine/retrieval/payload.py` - sparse citation and excerpt-hit basket ref reconstruction preserves promotion identity and document rank.
- `src/qual/retrieval/service.py` - direct FTS excerpt lookup audit events include ordered basket item IDs and fingerprints.
- `tests/unit/test_unified_retrieval.py` - approved shared regression coverage for FTS lookup identity and basket promotion rehydration.

Excluded from reviewed implementation scope:

- `codex_packet_handoff/tools/planner.py` and `tests/unit/test_packet_planner.py` are not in this split range and are not classified as metadata-only handoff artifacts.
- Earlier cumulative retrieval commits are outside this split handoff and require separate review packets if they are to be reviewed.
- Packet refresh commits after `69b3ca51841e749c604d00d6cdc6c03a09b1519b` change handoff metadata only and do not expand the reviewed implementation range.

## Diff Evidence

Command: `git diff --stat f2649eade7c028d46452a81ccf8b1a585a028ba8..69b3ca51841e749c604d00d6cdc6c03a09b1519b`

```text
 THREAD_PACKET.md                     | 137 +++++++++++++++++++++++++----------
 src/qual/engine/retrieval/payload.py |  72 +++++++++++++++++-
 src/qual/retrieval/service.py        |   2 +
 tests/unit/test_unified_retrieval.py |  93 +++++++++++++++++-------
 4 files changed, 235 insertions(+), 69 deletions(-)
```

Command: `git diff --numstat f2649eade7c028d46452a81ccf8b1a585a028ba8..69b3ca51841e749c604d00d6cdc6c03a09b1519b`

```text
97	40	THREAD_PACKET.md
71	1	src/qual/engine/retrieval/payload.py
2	0	src/qual/retrieval/service.py
65	28	tests/unit/test_unified_retrieval.py
```

## Budget/Risk

- Task budget: `4/4` high-risk task groups.
- File count for authoritative reviewed implementation range: `4 files changed`.
- Size accounting for authoritative reviewed implementation range: `235 insertions(+), 69 deletions(-)`, net `+166 LOC`.
- AGENTS high-risk file/size status: fits `<=8 files` and `<=300 net LOC`.
- Integrator exception status: no exception needed for this split handoff.
- Routing/provider impact: none.
- PageIndex/embeddings impact: remain compatibility-only fallback behavior; no active non-FTS retrieval path is introduced.
- Remaining risks/blockers: none known for this split. Earlier cumulative branch work is intentionally excluded from this reviewed implementation range.

## Roadmap/Vision

- Roadmap items affected: `ROADMAP.md` Milestone 3 generation provenance contract and Milestone 4 retrieval source-attribution/auditable deterministic retrieval.
- Vision capability affected: retrieval-backed context, retrieval-first context handling, auditable outputs, and reliable local-first state.
- Architecture alignment: FTS remains the required local retrieval path. PageIndex and embeddings stay compatibility-only/deferred and fail closed.
- Canonical demo-path mapping: advances `retrieve relevant material` and supports `promote or gather context into the basket`.
- Routing/provider impact note: none.
- Proposed `README.md` patch text: none.

## Commands Run

- `make scope-check` - passed for branch `codex/feat-retrieval-fts`.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - passed smoke tests and 148 unit tests.
- `./typecheck-test.sh` - passed Python source compilation under `src/`.
- `make ci` - passed setup, scope-check, format, lint, typecheck, smoke tests, and 148 unit tests.

## Metadata Write Note

The root `THREAD_PACKET.md` is the authoritative regenerated handoff packet for this fixer pass. The `.codex` kickoff and lane metadata mirrors are best-effort summaries only; this packet is the source of truth for the reviewed implementation range and split accounting.
