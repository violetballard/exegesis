# Thread Handoff Packet

- Lane: `feat-retrieval-fts`
- Branch: `codex/feat-retrieval-fts`
- Commit: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Packet refresh role: `metadata-only reviewer-fix finalization`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`

## Packet traceability note

- The current branch tip is a packet-refresh commit.
- Re-review should stay anchored to the narrowed retrieval implementation range `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
- Later packet-refresh commits are metadata-only unless this handoff is explicitly regenerated to move the reviewed implementation range.

## Current program focus

- Close the engine-side Milestone 3 workflow loop before activating any Textual UI lanes.

## Scope goal

- Tighten the compatibility-layer excerpt lookup path so the MVP stays FTS-first and auditable for the canonical `retrieve relevant material` step.

## Scope completed

- Removed the PageIndex fallback from `fetch_excerpt` in `src/qual/retrieval/service.py`, so the public excerpt lookup surface now resolves through the canonical FTS-only path.
- Added approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proving PageIndex-only excerpt IDs now fail closed with `KeyError`.
- PageIndex and embeddings remain compatibility-only paths in this reviewed slice; excerpt lookup no longer promotes PageIndex as a runtime fallback for the MVP contract.

## Canonical demo-path step advanced

- `retrieve relevant material`
- Canonical demo-path statement: This work makes `retrieve relevant material` more real by ensuring excerpt lookup stays on one deterministic FTS-only path with auditable failure behavior.
- Basket-promotion statement: Fail-closed FTS-only excerpt lookup strengthens downstream basket promotion by preventing PageIndex-only IDs from appearing as valid provenance.

## Scope-tightening note

- This packet intentionally covers only the narrowed compatibility-layer `fetch_excerpt` change plus the approved shared regression needed to prove it.
- It does not claim that this metadata refresh completes the broader `feat-retrieval-fts` MVP or canonical engine-surface exposure beyond the reviewed implementation range above.

## Reviewer fix reconciliation

- Scope language is narrowed to the actual reviewed slice: removal of the PageIndex fallback from `fetch_excerpt`, plus shared regression coverage proving PageIndex-only excerpt IDs fail closed.
- Broader lane-completion language was removed so this packet does not overstate the reviewed slice as the full retrieval MVP.
- The handoff now explicitly states which canonical demo-path step it advances: `retrieve relevant material`.
- The ownership note now distinguishes the approved shared test edit from integrator-locked files.

## Kickoff budget/limits compliance

- This handoff includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, so it is shared/high-risk work and should be read against the 4-task cap.
- The narrowed reviewed slice changes 2 files with 59 lines touched in `adfa8cdadd43747ffbcb612e4151e262b13e52ca`, which fits the shared/high-risk size budget.

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

- Milestone 3: Real workflow loop
- `feat-retrieval-fts`: authoritative FTS-first retrieval feeding the engine loop

### Vision capability affected

- Retrieval-first context handling
- Auditable state and workflow

### Routing/provider impact note

- None

## Scope-check / ownership note

- Approved shared-by-approval edit: `tests/unit/test_unified_retrieval.py`
- Integrator-locked edits: `NO`
