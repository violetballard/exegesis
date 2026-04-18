# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `reviewer-fix packet regeneration`
- Current branch tip before this fixer pass: `3f010faf88f624075d206de7742a4aa060aaed74`
- Reviewed implementation commit: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation range: `adfa8cdadd43747ffbcb612e4151e262b13e52ca^..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Packet-only descendants above the reviewed implementation head: metadata-only packet refresh commits; final HEAD SHA is reported with the fixer handoff
- Packet traceability note: this handoff is narrowed to the single reviewed implementation commit `adfa8cdadd43747ffbcb612e4151e262b13e52ca`; later metadata-only packet refresh commits do not broaden the reviewed retrieval implementation scope.

## Scope goal

- Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt and provenance output.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: keep excerpt lookup on the canonical SQLite FTS path and preserve deterministic provenance output for downstream engine flows.
- Risk reason: the reviewed implementation commit includes the approved shared regression surface `tests/unit/test_unified_retrieval.py`.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Keep excerpt lookup fail-closed on the canonical FTS path.
2. Preserve deterministic excerpt and provenance payload output.
3. Maintain approved shared regression coverage for the FTS-only excerpt contract.
4. Regenerate the handoff packet so every artifact points at one exact reviewed implementation commit and states the canonical demo-path step advanced.

### Checkpoint Status

- `plan complete`: all handoff artifacts are being narrowed to the single reviewed implementation commit `adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
- `first green tests`: recorded after rerunning the required gates for this fixer pass.
- `before risky/shared file edit`: the only shared implementation file in scope remains the approved regression surface `tests/unit/test_unified_retrieval.py`.
- `ready for handoff`: this packet now uses a single reviewed implementation scope and explicit demo-path mapping for re-review.

## Scope completed

- SQLite FTS remains the authoritative MVP retrieval path in this narrowed slice.
- The single reviewed implementation commit removes the PageIndex fallback from `fetch_excerpt()` so excerpt lookup now fail-closes on the canonical FTS-only path.
- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proves PageIndex-only excerpt IDs now raise `KeyError`.
- PageIndex and embeddings remain non-required compatibility paths in this slice; excerpt lookup no longer promotes PageIndex as a runtime fallback path for the MVP contract.

## Canonical Demo-Path Step Advanced

- `retrieve relevant material`

This handoff advances `retrieve relevant material` by forcing `fetch_excerpt()` to return only canonical FTS-backed excerpt payloads, which keeps downstream basket promotion and audit provenance tied to deterministic, auditable SQLite FTS hits.

## Tasks completed

1. `src/qual/retrieval/service.py` now makes `fetch_excerpt()` resolve through the canonical FTS-only path instead of falling back to PageIndex.
2. `tests/unit/test_unified_retrieval.py` adds approved shared regression coverage proving PageIndex-only excerpt IDs fail closed with `KeyError`.

## Files changed

- Reviewed implementation files:
  - `src/qual/retrieval/service.py`
  - `tests/unit/test_unified_retrieval.py`
- Metadata-only handoff files:
  - `THREAD_PACKET.md`

## Commands run with results

- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Reviewer fix closure

1. This packet now points at one unambiguous reviewed implementation scope: the single commit `adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
2. `Scope completed`, `Files changed`, and the budget framing are restated against that exact reviewed implementation commit.
3. The packet states explicitly which canonical demo-path step this change advances and how the FTS-only excerpt behavior strengthens that step.

## Risks / blockers

- Residual risk: non-canonical callers that still pass PageIndex-generated excerpt IDs into `qual.retrieval.fetch_excerpt()`, `qual.engine.retrieval.fetch_excerpt()`, or `RetrievalService.fetch_excerpt()` now receive `KeyError` instead of PageIndex-backed excerpt payloads.
- In-tree canonical retrieval flows do not rely on that fallback path. `rg` in this worktree found no remaining `RetrievalService.fetch_excerpt()` call sites that depend on PageIndex-only IDs, so the remaining exposure is compatibility-only callers outside the MVP demo path or downstream consumers still holding PageIndex excerpt IDs.
- Blockers: none

## Required handoff fields

### Roadmap item(s) affected

- `Milestone 3: Real workflow loop`
- `feat-retrieval-fts`

### Canonical demo-path step advanced

- `retrieve relevant material`

### Vision capability affected

- `Retrieval-first context handling`
- `Auditable state and workflow`

### Routing/provider impact note

- None

### Proposed `README.md` patch text

- None

## Scope-check / ownership note

- Shared/integrator-locked edits in the reviewed implementation commit: `YES`
- Approved shared exception: `tests/unit/test_unified_retrieval.py` is the sole shared-by-approval implementation file in the reviewed scope.
