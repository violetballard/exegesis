# Thread Handoff Packet

- Lane: `feat-retrieval-fts`
- Branch: `codex/feat-retrieval-fts`
- Review target: current branch tip after this fixer commit; final SHA is reported in the fixer response.
- Reviewed implementation range: `378cf9a74..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Corrected merge-candidate rule: non-metadata files at the final branch tip are restored to the reviewed implementation state from `adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
- Handoff type: high-risk retrieval fixer re-review.

## Scope Goal

Keep excerpt lookup FTS-first by removing the PageIndex fallback from `fetch_excerpt`, with regression coverage for fail-closed behavior.

## Scope Completed

This fixer removes the unreviewed post-`adfa8cda` branch-tip drift from the merge result. The final candidate keeps only the reviewed FTS-only excerpt lookup slice plus packet metadata. `fetch_excerpt` no longer falls back to PageIndex lookup when the FTS path cannot resolve an excerpt, and shared retrieval coverage asserts PageIndex-only excerpt IDs fail closed.

## Canonical Demo-Path Step Advanced

- Step: `retrieve relevant material`
- The change advances the canonical demo path by making excerpt retrieval honor the FTS-first retrieval contract. Material promoted or gathered into context must come from the canonical FTS path rather than a PageIndex-only fallback.

## Budget And Ownership

- Risk: `HIGH`
- High-risk reason: the reviewed range includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Task count: `1`
- Task budget: `4`
- Size accounting for the corrected candidate against `378cf9a74`: `5 files changed, 272 insertions(+), 106 deletions(-)`.
- Owned runtime path touched: `src/qual/retrieval/service.py`
- Approved shared-by-approval edit: `tests/unit/test_unified_retrieval.py`
- Handoff metadata artifacts touched: `.codex/kickoff_packets/feat-retrieval-fts.md`, `.codex/lane_meta/feat-retrieval-fts.json`, `THREAD_PACKET.md`
- Integrator-locked files touched: none
- Restored/retained modules and tests: `src/qual/engine/retrieval/embeddings_strategy.py`, `src/qual/engine/retrieval/pageindex_strategy.py`, and `tests/unit/test_packet_planner.py` are present in the corrected final tree.
- Removed from the merge result: basket promotion context/fingerprint payload changes, retrieval strategy module deletions, packet planner drift, and packet-planner test deletion after `adfa8cda`.

## Tasks Completed

1. Removed PageIndex fallback behavior from `fetch_excerpt` and covered the FTS-only excerpt contract with shared retrieval regression coverage.

## Complete Files Changed

Corrected review range `378cf9a74..final branch tip`:

```text
.codex/kickoff_packets/feat-retrieval-fts.md
.codex/lane_meta/feat-retrieval-fts.json
THREAD_PACKET.md
src/qual/retrieval/service.py
tests/unit/test_unified_retrieval.py
```

Post-`adfa8cda` implementation work kept for review:

```text
none
```

Post-`adfa8cda` implementation drift explicitly removed from the merge result:

```text
codex_packet_handoff/tools/planner.py
src/qual/engine/retrieval/__init__.py
src/qual/engine/retrieval/embeddings_strategy.py
src/qual/engine/retrieval/fts_strategy.py
src/qual/engine/retrieval/pageindex_strategy.py
src/qual/engine/retrieval/payload.py
src/qual/retrieval/__init__.py
src/qual/retrieval/service.py
tests/unit/test_packet_planner.py
tests/unit/test_unified_retrieval.py
```

## Merge-Facing Diff / Stat

Corrected candidate stat against the reviewer-stated range base:

```text
git diff --stat 378cf9a74 -- .
```

Expected result after the fixer commit:

```text
.codex/kickoff_packets/feat-retrieval-fts.md |  36 ++++++-
.codex/lane_meta/feat-retrieval-fts.json     | 155 ++++++++++++++++++++++++---
THREAD_PACKET.md                             | 128 ++++++++++++----------
src/qual/retrieval/service.py                |  21 ++------------------
tests/unit/test_unified_retrieval.py         |  38 ++++++++++++++++++++++++------------
5 files changed, 272 insertions(+), 106 deletions(-)
```

## Commands Run And Outcomes

- `make scope-check`: rerun required for this corrected final candidate.
- `./quality-format.sh --check`: rerun required for this corrected final candidate.
- `./quality-lint.sh`: rerun required for this corrected final candidate.
- `./quality-test.sh`: rerun required for this corrected final candidate.
- `./typecheck-test.sh`: rerun required for this corrected final candidate.
- `make ci`: rerun required for this corrected final candidate.

## Roadmap Items Affected

- `ROADMAP.md`: MVP focus on FTS-first retrieval.
- `ROADMAP.md`: Milestone 3 retrieval context handling for the real workflow loop.

## Vision Capabilities Affected

- `PRODUCT_VISION.md`: retrieval-first context handling.
- `PRODUCT_VISION.md`: auditable state and workflow.

## Routing / Provider Impact

None. This handoff does not touch model routing, provider configuration, or core provider entrypoints.

## Risks / Blockers

- Remaining risk: shared regression coverage is included, so the handoff remains high-risk by ownership policy.
- Public retrieval payload/API changes for basket promotion are not included in the corrected merge result.
- Blockers: none.
