# Thread Handoff Packet

- Lane: `feat-retrieval-fts`
- Branch: `codex/feat-retrieval-fts`
- Commit: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Packet refresh commit: `reported in final fixer handoff`
- Packet refresh role: `metadata-only reviewer-fix finalization`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`

## Packet traceability note

- Review this handoff against the narrowed retrieval implementation range `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
- Later packet-refresh commits remain metadata-only for this handoff unless the packet is explicitly regenerated to widen the reviewed implementation range.

## Current program focus

- Close the engine-side Milestone 3 workflow loop before activating any Textual UI lanes.

## Scope goal

- Keep retrieval FTS-first for the MVP, make excerpt lookup deterministic and fail closed, and keep excerpt provenance auditable enough for engine workflows and basket promotion.

## Scope completed

- `fetch_excerpt` now resolves only through the canonical FTS-backed path, so PageIndex-only excerpt IDs fail closed instead of silently falling back.
- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proves PageIndex-only excerpt IDs now raise `KeyError`.

## Canonical demo-path step advanced

- `retrieve relevant material`
- Canonical demo-path statement: This work makes `retrieve relevant material` more real by enforcing FTS-only excerpt lookup and deterministic excerpt provenance on the canonical retrieval path.
- Basket-promotion statement: The deterministic and auditable excerpt contract gives downstream flows a stable payload they can safely promote or gather into the basket without PageIndex ambiguity.

## Reviewer fix reconciliation

- The handoff now explicitly names the canonical demo-path step `retrieve relevant material`.
- The packet now includes a concrete basket-promotion sentence tied to the deterministic and auditable excerpt contract.
- The reviewed implementation range remains narrowed to `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca` and does not widen scope back to unrelated retrieval work.

## Kickoff budget/limits compliance

- This handoff includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, so the packet is shared/high-risk work and should be read against the 4-task cap.
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

### Packet artifacts refreshed by this fixer pass

- `THREAD_PACKET.md`
- `docs/gate_passed.txt`

### Packet mirror artifacts blocked in this environment

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`

## Commands run and outcomes

- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

## Risks / blockers

- Residual risk: later retrieval changes that intentionally broaden excerpt lookup semantics will need coordinated updates to the shared regression surface in `tests/unit/test_unified_retrieval.py`.
- Blockers: `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` could not be refreshed with `apply_patch` in this environment.

## Required handoff fields

### Roadmap item(s) affected

- `ROADMAP.md`: Milestone 3: Real workflow loop
- `feat-retrieval-fts`: authoritative FTS-first retrieval feeding the engine loop

### Vision capability affected

- Retrieval-first context handling
- Auditable state and workflow

### Routing/provider impact note

- None

## Scope-check / ownership note

- Shared/integrator-locked edits: `YES`
