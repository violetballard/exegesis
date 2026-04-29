# Thread Handoff Packet

- Lane: `feat-retrieval-fts`
- Branch: `codex/feat-retrieval-fts`
- Review target: final fixer commit reported in the fixer response.
- Pre-fix branch tip: `306dd8c0fb9230392cddc36e06008235148f7b45`
- Corrected reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Corrected reviewed implementation range: `378cf9a74..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Correction strategy: regenerate the merge-facing branch tip so non-packet implementation files match the narrowed reviewed implementation ending at `adfa8cda`.
- Handoff type: high-risk retrieval fixer re-review.

## Scope Goal

Keep excerpt lookup FTS-first by removing the PageIndex fallback from `fetch_excerpt`, with regression coverage for fail-closed behavior.

## Scope Completed

This fixer removes unreviewed post-`adfa8cda` branch-tip drift from the merge result. The corrected final candidate keeps only the reviewed FTS-only excerpt lookup slice plus packet metadata. `fetch_excerpt` no longer falls back to PageIndex lookup when the FTS path cannot resolve an excerpt, and shared retrieval coverage asserts PageIndex-only excerpt IDs fail closed.

## Canonical Demo-Path Step Advanced

- Step: `retrieve relevant material`
- The change advances the canonical demo path by making excerpt retrieval honor the FTS-first retrieval contract. Material promoted or gathered into context must come from the canonical FTS path rather than a PageIndex-only fallback.

## Budget And Ownership

- Risk: `HIGH`
- High-risk reason: the reviewed range includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Task count: `1`
- Task budget: `4`
- Owned runtime path touched: `src/qual/retrieval/service.py`
- Approved shared-by-approval edit: `tests/unit/test_unified_retrieval.py`
- Handoff metadata artifact touched: `THREAD_PACKET.md`
- Integrator-locked files touched: none
- Restored/retained modules and tests: `src/qual/engine/retrieval/embeddings_strategy.py`, `src/qual/engine/retrieval/pageindex_strategy.py`, and `tests/unit/test_packet_planner.py` are present in the corrected final tree.
- Removed from the merge result: basket promotion context/fingerprint payload changes, retrieval strategy module deletions, packet planner drift, retrieval facade/package drift, FTS cache drift, and packet-planner test deletion after `adfa8cda`.

## Tasks Completed

1. Removed PageIndex fallback behavior from `fetch_excerpt` and covered the FTS-only excerpt contract with shared retrieval regression coverage.

## Complete Files Changed

Corrected merge-facing implementation diff `378cf9a74..adfa8cdadd43747ffbcb612e4151e262b13e52ca`:

```text
src/qual/retrieval/service.py
tests/unit/test_unified_retrieval.py
```

Final fixer commit files:

```text
THREAD_PACKET.md
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

Post-`adfa8cda` implementation work kept for review:

```text
none
```

Post-`adfa8cda` implementation drift explicitly removed from the merge result:

```text
codex_packet_handoff/tools/planner.py
src/qual/engine/retrieval/__init__.py
src/qual/engine/retrieval/fts_strategy.py
src/qual/engine/retrieval/payload.py
src/qual/retrieval/__init__.py
src/qual/retrieval/service.py
tests/unit/test_unified_retrieval.py
```

Files restored because later branch-tip drift deleted them:

```text
src/qual/engine/retrieval/embeddings_strategy.py
src/qual/engine/retrieval/pageindex_strategy.py
tests/unit/test_packet_planner.py
```

## Merge-Facing Diff / Stat

Corrected implementation stat:

```text
git diff --stat 378cf9a74 adfa8cdadd43747ffbcb612e4151e262b13e52ca -- src/qual/retrieval/service.py tests/unit/test_unified_retrieval.py
```

Result:

```text
src/qual/retrieval/service.py        | 21 ++------------------
tests/unit/test_unified_retrieval.py | 38 ++++++++++++++++++++++++------------
2 files changed, 28 insertions(+), 31 deletions(-)
```

## Commands Run And Outcomes

- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS (`124` unit tests plus smoke)
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

## Roadmap Items Affected

- `ROADMAP.md`: MVP focus on FTS-first retrieval.
- `ROADMAP.md`: Milestone 3 retrieval context handling for the real workflow loop.

## Vision Capabilities Affected

- `PRODUCT_VISION.md`: retrieval-first context handling.
- `PRODUCT_VISION.md`: auditable state and workflow.

## Routing / Provider Impact

None. This handoff does not touch model routing, provider configuration, or core provider entrypoints.

## Metadata-Only Claim Correction

The reviewer-referenced `306dd8c0fb9230392cddc36e06008235148f7b45` commit changed source files and is not metadata-only. This fixer does not rely on that claim. It removes the source drift from the final merge result instead of expanding the reviewed scope through `306dd8c0`.

## Risks / Blockers

- Remaining risk: shared regression coverage is included, so the handoff remains high-risk by ownership policy.
- Public retrieval payload/API changes for basket promotion are not included in the corrected merge result.
- Blockers: none.
