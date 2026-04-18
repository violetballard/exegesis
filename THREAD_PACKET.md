# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `reviewer-fix packet regeneration`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Exact reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`

## Scope goal

- Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt and provenance output.

## Scope completed

- `fetch_excerpt` now resolves only through the canonical FTS lookup path in `src/qual/retrieval/service.py`.
- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` verifies that PageIndex-only excerpt IDs raise `KeyError`.
- This narrowed slice keeps PageIndex and embeddings as non-required compatibility paths and does not expand runtime retrieval scope beyond the FTS contract.

## Canonical Demo-Path Step Advanced

- `retrieve relevant material`

This change makes `retrieve relevant material` more real by fail-closing excerpt lookup on the canonical FTS path. If basket promotion is mentioned, it is only as a downstream consumer of deterministic FTS excerpts rather than new scope delivered here.

## Tasks completed

1. Removed the PageIndex fallback from `fetch_excerpt` so the public excerpt lookup surface now resolves through the canonical FTS-only path.
2. Added approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proving PageIndex-only excerpt IDs fail closed with `KeyError`.

## Files changed

- Reviewed implementation files:
  - `src/qual/retrieval/service.py`
  - `tests/unit/test_unified_retrieval.py`
- Metadata-only handoff files:
  - `.codex/kickoff_packets/feat-retrieval-fts.md`
  - `.codex/lane_meta/feat-retrieval-fts.json`
  - `THREAD_PACKET.md`
  - `codex_packet_handoff/tools/planner.py`
  - `tests/unit/test_packet_planner.py`

## Commands run with results

- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Reviewer fix closure

1. Added the explicit canonical demo-path mapping required by `AGENTS.md`: `retrieve relevant material`.
2. Tightened the scope-completed wording so it matches the reviewed diff exactly: `fetch_excerpt` is now FTS-only, and approved shared regression coverage verifies PageIndex-only excerpt IDs raise `KeyError`.

## Risks / blockers

- Risk: `HIGH`
- Blockers: `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` are tracked but not writable in this worktree sandbox, so this fixer pass updates the writable handoff packet surface only.

## Required handoff fields

### Roadmap item(s) affected

- `Milestone 3: Real workflow loop`
- `feat-retrieval-fts`

### Vision capability affected

- `Retrieval-first context handling`
- `Auditable state and workflow`

### Routing/provider impact note

- None

### Proposed `README.md` patch text

- None

## Scope-check / ownership note

- Shared/integrator-locked edits: `YES`
- Approved shared exception: `tests/unit/test_unified_retrieval.py` is the sole shared-by-approval file in the reviewed implementation.
