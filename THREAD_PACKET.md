# Thread Handoff Packet

- Lane: `feat-retrieval-fts`
- Branch: `codex/feat-retrieval-fts`
- Reviewed implementation head: `22a56fce70167ddd4c7708fd4a1ee18fad7b8ffe`
- Packet refresh role: `reviewer-fix handoff regeneration`
- Reviewed implementation range: `d7fd5d200358287fa42a18d39e2b277463b9b69f..22a56fce70167ddd4c7708fd4a1ee18fad7b8ffe`

## Packet traceability note

- This packet is regenerated to include the full retrieval implementation now present on the branch, including the post-`adfa8cdadd43747ffbcb612e4151e262b13e52ca` engine-surface export fixes in `47e06828cb813c1daa4b3a321889c90ed743a7c0` and `22a56fce70167ddd4c7708fd4a1ee18fad7b8ffe`.
- The reviewed implementation range above is the authoritative scope for retrieval code review on this branch.
- This fixer pass adds only packet artifacts and verification output; the final branch-tip SHA for that metadata-only refresh is reported in the fixer handoff.

## Current program focus

- Close the engine-side Milestone 3 workflow loop before activating any Textual UI lanes.

## Scope goal

- Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt and provenance output on the canonical engine surface.

## Scope completed

- `fetch_excerpt` now resolves only through the canonical FTS-backed path, so PageIndex-only excerpt IDs fail closed instead of silently falling back.
- The engine retrieval shim now explicitly exposes `RetrievalConstraints` and `RetrievalQuery`, so engine callers construct FTS-first retrieval requests from the same public contract used by the retrieval package.
- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proves both behaviors: PageIndex-only excerpt IDs raise `KeyError`, and the engine retrieval surface exposes identity-stable canonical query dataclasses.

## Canonical demo-path step advanced

- `retrieve relevant material`
- Canonical demo-path statement: This work makes `retrieve relevant material` more real by enforcing FTS-only excerpt lookup and exposing one deterministic retrieval-query contract on the canonical engine surface.
- Basket-promotion statement: Downstream basket-promotion and later revise/apply flows now consume one auditable retrieval payload shape instead of mixing FTS-first behavior with implicit shim-only query construction.

## Reviewer fix reconciliation

- The packet now includes the runtime engine-surface work that previously sat outside the reviewed range.
- `Files changed` and scope language now explicitly include `src/qual/engine/retrieval/__init__.py`.
- The canonical demo-path step is named directly in the packet.
- The engine-surface export remains within retrieval-lane scope because `src/qual/engine/retrieval/**` is an owned lane path and the exported types are the canonical retrieval query contract used to reach the FTS-first service.

## Kickoff budget/limits compliance

- This handoff includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, so the packet is shared/high-risk work and should be read against the 4-task cap.
- The reviewed implementation files remain within the high-risk lane-owned/shared-by-approval scope: `src/qual/retrieval/service.py`, `src/qual/engine/retrieval/__init__.py`, and `tests/unit/test_unified_retrieval.py`.

## Approved exception note

- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for the `feat-retrieval-fts` lane; it is the sole shared-by-approval regression surface for the lane and exercises the canonical retrieval contract.

## Tasks completed (numbered)

1. Removed the PageIndex fallback from `fetch_excerpt` so the public excerpt lookup surface now resolves through the canonical FTS-only path.
2. Added approved shared regression coverage proving PageIndex-only excerpt IDs fail closed with `KeyError`.
3. Exposed `RetrievalConstraints` and `RetrievalQuery` on the engine retrieval surface so engine callers import the canonical query contract from the owned retrieval shim.
4. Extended approved shared regression coverage to assert those exported types are present and identity-stable on the engine retrieval surface.

## Files changed

### Reviewed implementation files

- `src/qual/retrieval/service.py`
- `src/qual/engine/retrieval/__init__.py`
- `tests/unit/test_unified_retrieval.py`

### Packet artifacts refreshed by this fixer pass

- `THREAD_PACKET.md`
- `docs/gate_passed.txt`

## Commands run and outcomes

- `python -m unittest tests.unit.test_unified_retrieval -q`: PASS
- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

## Risks / blockers

- Residual risk: future retrieval shim changes must keep the explicit engine export list and shared regression assertions aligned with the retrieval-owned dataclasses.
- Blockers: none

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
