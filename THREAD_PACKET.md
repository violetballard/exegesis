# Thread Handoff Packet

- Lane: `feat-retrieval-fts`
- Branch: `codex/feat-retrieval-fts`
- Commit: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Packet refresh commit: `reported in final fixer handoff`
- Packet refresh role: `metadata-only reviewer-fix finalization`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`

## Packet traceability note

- The current branch tip is a packet-refresh commit. Review the narrowed retrieval implementation range `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`; later packet-refresh commits remain metadata-only unless this handoff is regenerated.

## Current program focus

- Close the engine-side Milestone 3 workflow loop before activating any Textual UI lanes.

## Current engine execution order

1. `feat-context-storage` - Persistence floor for document, basket, vault, and session state.
2. `feat-commands` - Stable command surface for the CLI-first MVP loop.
3. `feat-retrieval-fts` - Authoritative FTS-first retrieval for engine runs.
4. `feat-engine-runs` - Close the plan, revise, patch, and apply loop in the engine.
5. `feat-a2ui-contract` - Support the engine loop with stable shared contracts, not UI ambition.

## Scope goal

- Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt and provenance output. This lane slice advances the canonical demo-path step `retrieve relevant material` and stays out of scope for basket promotion, plan/revise/apply flow work, and any PageIndex or embeddings runtime fallback behavior.

## Priority outcomes

1. Keep SQLite FTS as the primary retrieval path.
2. Return stable, structured hits suitable for basket promotion and downstream workflow use.
3. Keep provenance and excerpt payloads deterministic and auditable.

## Definition of done for this lane

- Retrieval is FTS-first by default.
- Results are structured and deterministic enough for basket promotion and workflow cards.
- Excerpt provenance is stable and auditable.
- Retrieval is reachable through the canonical engine surface.

## Do not spend time on

- Over-investing in embeddings or alternate retrieval modes.
- UI rendering concerns.
- Search features outside the core writing loop.

## Lane/owned paths

- `src/qual/retrieval/**`
- `src/qual/engine/retrieval/**`
- `engine/src/exegesis_engine/retrieval/**`

## Scope completed

- SQLite FTS remains the authoritative MVP retrieval path in this narrowed slice. The reviewed implementation commit makes excerpt lookup fail closed on the canonical FTS-only path by removing the PageIndex fallback from `fetch_excerpt`, while keeping approved shared regression coverage in `tests/unit/test_unified_retrieval.py` to prove PageIndex-only excerpt IDs now raise `KeyError`.
- PageIndex and embeddings remain non-required compatibility paths in this slice; excerpt lookup no longer promotes PageIndex as a runtime fallback path for the MVP contract. Basket promotion and plan/revise/apply flow work remain explicitly out of scope for this handoff.
- This re-review deliberately narrows scope from the earlier over-budget cumulative branch summary to the single implementation commit `adfa8cdadd43747ffbcb612e4151e262b13e52ca`, which stays within the high-risk size budget for shared-file work.

## Canonical demo-path step advanced

- `retrieve relevant material`
- This work advances `retrieve relevant material` by ensuring excerpt lookup stays on the canonical FTS-first path and fails closed for PageIndex-only IDs, keeping retrieval output deterministic and auditable.

## Explicitly out of scope for this lane slice

- Basket promotion remains out of scope.
- Plan, revise, patch, and apply workflow work remains out of scope.
- PageIndex or embeddings runtime fallback behavior remains out of scope beyond compatibility-only fail-closed handling.

## Kickoff budget/limits compliance

- This handoff includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, so the packet is shared/high-risk work and should be read against the 4-task cap. The narrowed reviewed slice changes 2 files with 59 lines touched in `adfa8cdadd43747ffbcb612e4151e262b13e52ca`, which fits the shared/high-risk size budget.

## Approved exception note

- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for the `feat-retrieval-fts` lane; it is the sole shared-by-approval regression surface for the lane and exercises the canonical retrieval contract.

## Tasks completed (numbered)

1. Removed the PageIndex fallback from `fetch_excerpt` so the public excerpt lookup surface now resolves through the canonical FTS-only path.
2. Added approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proving PageIndex-only excerpt IDs fail closed with `KeyError`.

## Files changed

### Reviewed implementation files

- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

### Metadata-only handoff files

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`
- `codex_packet_handoff/tools/planner.py`
- `tests/unit/test_packet_planner.py`

## Commands run and outcomes

- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

## Risks / blockers

- Risk: `HIGH`
- Blockers: none

## Required handoff fields

### Roadmap item(s) affected

- Milestone 3: Real workflow loop - FTS-first retrieval remains the authoritative context path for the engine loop.
- `feat-retrieval-fts` - authoritative FTS-first retrieval feeding the engine loop.

### Vision capability affected

- Retrieval-first context handling
- Auditable state and workflow

### Routing/provider impact note

- None

## Scope-check / ownership note

- Shared/integrator-locked edits: `YES`
