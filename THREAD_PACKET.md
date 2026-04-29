## Thread Handoff Packet

- Branch/lane: `codex/feat-retrieval-fts` / `feat-retrieval-fts`
- Packet purpose: reviewer-fix re-review packet after correcting branch-tip traceability.
- Merge candidate: current branch tip after this metadata-only fixer commit.
- Reviewer base/range: `378cf9a74a3658058079a32f186fcd254c4a4034..67b69048f`
- Reviewed implementation head before this metadata-only fixer commit: `67b69048f`
- Final proposed merge HEAD after this fixer commit: reported in the fixer response.

## Scope Completed

This handoff covers the full branch-tip implementation surface, not only the earlier narrowed `adfa8cdadd43747ffbcb612e4151e262b13e52ca` slice. The final code-bearing head is `67b69048f`, which includes the FTS-only excerpt lookup work, the `a983d89af` retrieval provenance payload backfill, and the later basket-promotion candidate payload/service additions.

SQLite FTS remains the MVP-authoritative retrieval path. PageIndex and embeddings remain compatibility-only fallback shims and are not reintroduced as required retrieval paths. Retrieval payloads now carry deterministic provenance, citation, context-bundle, and basket-candidate snapshots so downstream engine and CLI/A2UI flows can retrieve relevant material and promote or gather context into the basket without relying on hidden fallback behavior.

## Tasks Completed

1. Changed `RetrievalService.fetch_excerpt` to use the canonical FTS excerpt lookup path and fail closed for unknown or non-FTS excerpt IDs, with shared regression coverage in `tests/unit/test_unified_retrieval.py`.
2. Stabilized retrieval provenance and payload backfill in `src/qual/engine/retrieval/payload.py`, including deterministic query, policy, citation, doc-hit, excerpt-hit, context-bundle, and retrieval-summary snapshots. Roadmap mapping: `ROADMAP.md` Milestone 3 generation provenance contract and Milestone 4 auditable deterministic retrieval. Product vision mapping: Retrieval-first context handling and auditable generation.
3. Exposed retrieval basket-promotion candidates from `src/qual/retrieval/service.py` and normalized them in `src/qual/engine/retrieval/payload.py`, advancing the canonical demo path steps "retrieve relevant material" and "promote or gather context into the basket."
4. Corrected the handoff packet so reviewed implementation range, files changed, task accounting, roadmap/product-vision mapping, and gate reporting match the actual code-bearing branch tip.

## Files Changed

Code and test files in the reviewed implementation range:

- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

Packet/metadata files in the reviewed range:

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`

No integrator-owned `README.md` changes are included.

## Budget

- Risk: high, because the handoff includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Task budget: `4/4` under AGENTS high-risk rules.
- File budget for the true branch-tip diff versus reviewer base: `6/8`.
- Shared-file approval note: `tests/unit/test_unified_retrieval.py` is the only shared-by-approval regression surface in this handoff.
- Integrator-locked files: none.

## Roadmap / Vision

- Roadmap items: `ROADMAP.md` Milestone 3 Product Readiness generation provenance contract; `ROADMAP.md` Milestone 4 Retrieval Layer FTS-first ingestion/retrieval orchestration/source attribution.
- Vision capabilities: Product Vision capability 2, Retrieval-first context handling; Product Vision capability 3, Auditable generation.
- Canonical demo-path step advanced: "retrieve relevant material" and "promote or gather context into the basket."
- Routing/provider impact: none.
- Textual/UI impact: none.
- Alternate retrieval-mode impact: none. PageIndex and embeddings remain deferred/fallback-only.
- Proposed `README.md` patch text: none.

## Reviewer Required Fixes Addressed

1. The reviewed implementation range now includes every code-bearing commit through the actual branch-tip implementation head `67b69048f`, including `a983d89af`.
2. Files changed are separated into code/test files and packet/metadata files.
3. Task 2 explicitly covers the `src/qual/engine/retrieval/payload.py` provenance backfill change with roadmap and product vision mapping.
4. Required gates are rerun after the final code-bearing commit and this metadata-only packet correction; outcomes are reported below.
5. The canonical demo-path step is explicitly stated as "retrieve relevant material" and "promote or gather context into the basket."

## Commands Run

Required gates rerun after correcting the handoff packet:

- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS, including smoke plus 124 unit tests
- `./typecheck-test.sh`: PASS
- `make ci`: PASS, including scope-check, format, lint, compileall, and smoke plus 124 unit tests

## Risks / Blockers

- The branch history contains prior packet-refresh commits with stale descriptions. This packet supersedes those descriptions and should be reviewed against the actual branch-tip implementation range above.
- No current blockers.
