# Thread Handoff Packet

- Lane: `feat-retrieval-fts`
- Branch: `codex/feat-retrieval-fts`
- Review target: current branch tip for `codex/feat-retrieval-fts`; final SHA is reported in the fixer handoff.
- Merge-facing base: `d7fd5d200358287fa42a18d39e2b277463b9b69f`
- Intended implementation anchor: `378cf9a7..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Handoff type: high-risk retrieval fixer re-review.

## Scope Goal

Keep excerpt lookup FTS-first by removing the PageIndex fallback from `fetch_excerpt`, with regression coverage for the fail-closed behavior.

## Scope Completed

The branch tip now contains only the narrowed retrieval slice plus handoff packet metadata. `fetch_excerpt` no longer falls back to PageIndex lookup when the FTS path cannot resolve an excerpt, and the shared retrieval regression test asserts PageIndex-only excerpt IDs fail closed. Later retrieval payload, engine facade, planner, and packet-tooling drift has been reverted out of the branch-tip merge result.

## Canonical Demo-Path Step Advanced

- Step: `retrieve relevant material`
- The change advances the canonical demo path by making excerpt retrieval honor the FTS-first retrieval contract. Material promoted or gathered into context must come from the canonical FTS path rather than a PageIndex-only fallback.

## Budget And Ownership

- Risk: `HIGH`
- High-risk reason: the reviewed range includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Task count: `1`
- Task budget: `4`
- Size accounting: `5 files changed, 281 insertions(+), 118 deletions(-)` in the merge-facing branch-tip diff before the final fixer commit is created.
- Owned runtime path touched: `src/qual/retrieval/service.py`
- Approved shared-by-approval edit: `tests/unit/test_unified_retrieval.py`
- Handoff metadata artifacts touched: `.codex/kickoff_packets/feat-retrieval-fts.md`, `.codex/lane_meta/feat-retrieval-fts.json`, `THREAD_PACKET.md`
- Integrator-locked files touched: none
- Removed from the branch-tip merge result: retrieval engine facade/payload drift, packet planner/tooling drift, and packet-planner test drift after `adfa8cda`.
- Packet-refresh note: code-touching commits are not described as metadata-only. Packet-only commits are metadata-only only when their diff is limited to packet metadata.

## Tasks Completed

1. Removed PageIndex fallback behavior from `fetch_excerpt` and covered the FTS-only excerpt contract with shared retrieval regression coverage.

## Complete Files Changed

```text
.codex/kickoff_packets/feat-retrieval-fts.md
.codex/lane_meta/feat-retrieval-fts.json
THREAD_PACKET.md
src/qual/retrieval/service.py
tests/unit/test_unified_retrieval.py
```

## Merge-Facing Diff / Stat

Command used for the corrected worktree scope before the final fixer commit:

```text
git diff --stat d7fd5d200358287fa42a18d39e2b277463b9b69f
```

Result:

```text
.codex/kickoff_packets/feat-retrieval-fts.md |  55 ++++++---
.codex/lane_meta/feat-retrieval-fts.json     | 162 ++++++++++++++++++++++++---
THREAD_PACKET.md                             | 127 +++++++++++----------
src/qual/retrieval/service.py                |  17 +--
tests/unit/test_unified_retrieval.py         |  38 +++++--
5 files changed, 281 insertions(+), 118 deletions(-)
```

## Commands Run And Outcomes

- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
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

## Risks / Blockers

- Remaining risk: shared regression coverage is included, so the handoff remains high-risk by ownership policy.
- Blockers: none.
