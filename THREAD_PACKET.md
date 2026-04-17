# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet refresh role: `metadata-only reviewer-fix finalization`
- Packet refresh trace anchor before this commit: `6d532146b627c148129f0f4aad391b784ae0a725`
- Reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation range for re-review: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`

## Scope goal

- Remove the `fetch_excerpt` PageIndex fallback so the canonical retrieval surface fails closed on non-FTS excerpt IDs and keeps excerpt resolution on the authoritative FTS-only path.

## Scope completed

- This reviewed slice removes the PageIndex fallback from `fetch_excerpt` in `src/qual/retrieval/service.py`, so canonical excerpt lookup resolves through the FTS-only path.
- Non-FTS excerpt IDs now fail closed with `KeyError` instead of silently resolving through PageIndex, which keeps excerpt provenance deterministic and auditable on the canonical retrieval surface.
- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proves that FTS-backed excerpt IDs still resolve and PageIndex-only excerpt IDs are rejected.

## Canonical demo-path step advanced

- `retrieve relevant material`
- This slice makes that step more real by keeping engine-facing excerpt resolution deterministic and auditable as soon as retrieval returns FTS hits, which is the contract downstream basket promotion depends on.

## Tasks completed

1. Removed the PageIndex fallback from `fetch_excerpt` so the public excerpt lookup surface now resolves through the canonical FTS-only path.
2. Added approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proving PageIndex-only excerpt IDs fail closed with `KeyError`.

## Files changed

### Reviewed implementation files

- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

### Packet / handoff files

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`

## Commands run with results

- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Risks / blockers

- Risk: `HIGH`
- Blockers: none

## Required handoff fields

### Roadmap item(s) affected

- `Milestone 3: Real workflow loop` because this slice hardens the FTS-first retrieval contract the engine loop uses when it retrieves relevant material.
- `feat-retrieval-fts - retrieval/search` because this slice removes the non-canonical PageIndex fallback from excerpt lookup.

### Vision capability affected

- `Retrieval-first context handling` because this slice keeps excerpt lookup on the authoritative FTS path used to gather context.
- `Auditable state and workflow` because this slice makes excerpt provenance fail closed instead of resolving through a non-canonical fallback.

### Routing/provider impact note

- None

## Scope-check / ownership note

- Shared-by-approval edits: `YES`
- Approved shared regression surface: `tests/unit/test_unified_retrieval.py`
- Integrator-locked edits: `NO`

## Traceability note

- This packet is intentionally narrowed to the reviewed implementation slice `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
- Later metadata-only packet refresh commits do not change that reviewed implementation range unless the packet is explicitly regenerated to do so.
- Use the final HEAD SHA reported with this fixer handoff for the current packet-refresh branch tip.
