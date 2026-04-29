## Thread Handoff Packet

- Branch/lane: `codex/feat-retrieval-fts` / `feat-retrieval-fts`
- Packet purpose: reviewer-fix re-review packet for the actual branch tip proposed for merge.
- Merge base used for the current merge-candidate range: `d7fd5d200358287fa42a18d39e2b277463b9b69f`
- Actual branch tip when this fixer started: `1567f4d909c60008c77534d1f713f4da369eb6d5`
- Actual reviewed branch-tip range before this fixer commit: `d7fd5d200358287fa42a18d39e2b277463b9b69f..1567f4d909c60008c77534d1f713f4da369eb6d5`
- Reviewer-referenced implementation anchor: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Post-`adfa8c` delta included for explicit review: `adfa8cdadd43747ffbcb612e4151e262b13e52ca..1567f4d909c60008c77534d1f713f4da369eb6d5`
- Final proposed merge HEAD after this fixer commit: reported in the fixer response.

## Scope Completed

This handoff covers the real branch-tip Milestone 3 retrieval objective: FTS-first structured retrieval for basket and workflow use. SQLite FTS remains the authoritative MVP retrieval path. PageIndex and embeddings remain compatibility-only fallback shims and are not reintroduced as required paths. Retrieval payloads now carry deterministic source, context, citation, query-scope, section-hint, date-range, fingerprint, and basket-promotion metadata so downstream workflow outputs can preserve auditable provenance.

No Textual/UI work, provider routing change, command surface expansion, hidden alternate retrieval mode, or PageIndex/embedding-first path is included.

## Tasks Completed

1. Added FTS-first retrieval facade/export behavior, canonical query construction, and deterministic excerpt/provenance output while keeping PageIndex and embeddings fallback-only.
2. Added engine retrieval strategy/payload support for normalized query, policy, provenance, hit, source, and context snapshots.
3. Included all post-`adfa8c` basket-promotion/context-bundle behavior at branch tip, including stable source IDs, fingerprints, citation status, query scope, intent, doc type, section hints, date-range metadata, and sparse bundle rehydration.
4. Added shared regression coverage for packet planning, facade exports, payload normalization, provenance helpers, FTS-only excerpt backfill, and basket-promotion snapshots.

## Files Changed

The actual reviewed range `d7fd5d200358287fa42a18d39e2b277463b9b69f..1567f4d909c60008c77534d1f713f4da369eb6d5` changes:

- `.codex/kickoff_packets/feat-retrieval-fts.md` (`42` insertions, `13` deletions)
- `.codex/lane_meta/feat-retrieval-fts.json` (`146` insertions, `16` deletions)
- `THREAD_PACKET.md` (`86` insertions, `61` deletions)
- `codex_packet_handoff/tools/planner.py` (`34` insertions, `15` deletions)
- `src/qual/engine/retrieval/__init__.py` (`48` insertions, `8` deletions)
- `src/qual/engine/retrieval/embeddings_strategy.py` (`24` insertions, `0` deletions)
- `src/qual/engine/retrieval/fts_strategy.py` (`57` insertions, `0` deletions)
- `src/qual/engine/retrieval/pageindex_strategy.py` (`33` insertions, `0` deletions)
- `src/qual/engine/retrieval/payload.py` (`716` insertions, `77` deletions)
- `src/qual/retrieval/__init__.py` (`76` insertions, `18` deletions)
- `src/qual/retrieval/service.py` (`200` insertions, `38` deletions)
- `tests/unit/test_packet_planner.py` (`72` insertions, `0` deletions)
- `tests/unit/test_unified_retrieval.py` (`552` insertions, `13` deletions)

Range total before this fixer edit: `13 files changed, 2086 insertions(+), 259 deletions(-)`.

Runtime/test files in the actual reviewed range:

- `codex_packet_handoff/tools/planner.py`
- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/embeddings_strategy.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/pageindex_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/__init__.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_packet_planner.py`
- `tests/unit/test_unified_retrieval.py`

Files changed after `adfa8cdadd43747ffbcb612e4151e262b13e52ca` and included in this branch-tip review:

- `.codex/kickoff_packets/feat-retrieval-fts.md` (`34` insertions, `2` deletions)
- `.codex/lane_meta/feat-retrieval-fts.json` (`141` insertions, `14` deletions)
- `THREAD_PACKET.md` (`99` insertions, `67` deletions)
- `src/qual/engine/retrieval/payload.py` (`58` insertions, `0` deletions)
- `src/qual/retrieval/service.py` (`83` insertions, `0` deletions)
- `tests/unit/test_unified_retrieval.py` (`76` insertions, `0` deletions)

Post-`adfa8c` total with this fixer edit staged for commit: `6 files changed, 491 insertions(+), 83 deletions(-)`.

## Post-`adfa8c` Behavior Included

The post-`adfa8c` runtime/test changes are not metadata-only and are explicitly included for review. They add basket-promotion and context-bundle behavior to the retrieval payload path: compact source/context snapshots can rehydrate deterministic payloads, source references expose stable IDs and fingerprints, retrieval responses carry query scope and citation status, and sparse downstream basket-promotion inputs retain section hints and date-range constraints. The shared regression coverage in `tests/unit/test_unified_retrieval.py` verifies those branch-tip behaviors.

## Budget

- Risk: high, because the actual reviewed range touches retrieval payload behavior, packet planner behavior, and shared-by-approval test files.
- Task budget: `4/4` under AGENTS high-risk rules.
- File budget for the actual reviewed range before this fixer edit: `13/8`, exceeding the high-risk `<=8 files` guide.
- Strict AGENTS size accounting for the actual reviewed range before this fixer edit: `2086 insertions, 259 deletions` (`+1827` net LOC), exceeding the high-risk `<=300` net LOC guide.
- Post-`adfa8c` size accounting with this fixer edit staged for commit: `491 insertions, 83 deletions` (`+408` net LOC), also exceeding the high-risk `<=300` net LOC guide.
- Shared-file approval note: `tests/unit/test_unified_retrieval.py` and `tests/unit/test_packet_planner.py` are shared regression coverage in this branch-tip range; no integrator-locked files are edited.

This packet does not claim budget compliance through a narrowed slice. The actual branch-tip range is intentionally exposed for reviewer/integrator decision. Because the branch exceeds high-risk size limits, integration requires either explicit integrator authorization documented by the integrator or a follow-up split before approval.

## Roadmap / Vision

- Roadmap item: `ROADMAP.md` Milestone 3 Product Readiness, specifically generation provenance and retrieval evidence attached to workflow outputs.
- Roadmap status line: retrieval paths must be auditable and deterministic for MVP readiness.
- Vision capabilities: `PRODUCT_VISION.md` retrieval-backed context, SQLite FTS as the current MVP retrieval path, auditable outputs, and auditable state/workflow.
- Exact branch-tip mapping: FTS-first retrieval is the MVP evidence path; structured retrieval results support basket promotion and context-bundle rehydration; provenance, citation, fingerprint, query-scope, section-hint, and date-range fields make downstream workflow outputs auditable.
- Routing/provider impact: none.
- Textual/UI impact: none.
- Alternate retrieval-mode impact: none; PageIndex and embeddings stay fallback-only and deferred for the MVP.
- Proposed `README.md` patch text: none.

## Reviewer Required Fixes Addressed

1. The handoff is regenerated against the actual merge candidate present when this fixer started: `d7fd5d200358287fa42a18d39e2b277463b9b69f..1567f4d909c60008c77534d1f713f4da369eb6d5`.
2. The packet includes all post-`adfa8c` runtime/test changes for review instead of reducing the branch to the `adfa8c` slice.
3. High-risk budget and size accounting are recomputed for the actual branch-tip range and the post-`adfa8c` delta, including shared-by-approval test edits.
4. The packet explicitly documents that the branch exceeds high-risk file and net LOC limits and therefore needs integrator authorization or splitting before approval.
5. Roadmap/vision mapping is restated for the exact branch-tip changes: FTS-first retrieval, structured results for basket promotion/context bundles, and auditable provenance, with no hidden Textual/UI or alternate retrieval-mode expansion.

## Commands Run

Required gates rerun in this fixer pass after the metadata update:

- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS, including smoke plus 126 unit tests
- `./typecheck-test.sh`: PASS
- `make ci`: PASS, including scope-check, format, lint, compileall, and smoke plus 126 unit tests

## Risks / Blockers

- Budget risk: the actual branch-tip range exceeds high-risk file and net LOC guides. This is now explicitly disclosed instead of hidden behind a narrowed packet slice.
- Review risk: the post-`adfa8c` basket-promotion/context-bundle changes require explicit review as runtime/test behavior.
- Shared-file note: shared regression files are limited to `tests/unit/test_unified_retrieval.py` and `tests/unit/test_packet_planner.py`.
