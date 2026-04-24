# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `branch-tip handoff refresh`
- Packet refresh trace anchor before this fixer attempt: `2e052094c4cc2d4c3693c4dcb0f6e8f0c7764909`
- Reviewed implementation head: `bca26c21e58161f0e3da8fdaf8049ef84771d934`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..bca26c21e58161f0e3da8fdaf8049ef84771d934`
- Branch-tip handoff range before this fixer refresh: `378cf9a74a3658058079a32f186fcd254c4a4034..2e052094c4cc2d4c3693c4dcb0f6e8f0c7764909`
- Runtime implementation files in the reviewed range: `src/qual/engine/retrieval/__init__.py`, `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- Packet/supporting files in the branch-tip handoff range: `.codex/kickoff_packets/feat-retrieval-fts.md`, `.codex/lane_meta/feat-retrieval-fts.json`, `THREAD_PACKET.md`, `docs/gate_passed.txt`
- Canonical demo-path step advanced: `retrieve relevant material`
- Reviewer-required canonical demo-path sentence: This work makes the `retrieve relevant material` step of the canonical demo path more real by keeping retrieval/search FTS-first, forcing excerpt lookup through the authoritative FTS-backed path, and surfacing ranked retrieval ids for downstream promotion and context assembly.
- Explicit Milestone 3 mapping: this branch-tip slice advances `Milestone 3: Real workflow loop` by keeping retrieval/search FTS-first for the MVP while making the retrieval payloads more complete for downstream workflow consumers.
- FTS-first gate statement: the reviewed implementation range remains FTS-first for the MVP; PageIndex and embeddings stay deferred or compatibility-only shims and are not promoted to active runtime retrieval paths in this handoff.
- Traceability note: re-review runtime behavior against the reviewed implementation range above. The packet refresh commit `2e052094c4cc2d4c3693c4dcb0f6e8f0c7764909` is metadata-only; the later runtime retrieval change after `adfa8cdadd43747ffbcb612e4151e262b13e52ca` is `bca26c21e58161f0e3da8fdaf8049ef84771d934`.

## Scope Goal

- Resubmit the retrieval handoff against the actual branch-tip implementation instead of the stale pre-`bca26c21` slice.

## Scope Completed

- SQLite FTS remains the authoritative MVP retrieval path in the reviewed slice.
- `fetch_excerpt` resolves through the canonical FTS-only lookup path in `src/qual/retrieval/service.py`, and approved shared regression coverage proves PageIndex-only excerpt ids fail closed with `KeyError`.
- `src/qual/engine/retrieval/__init__.py` lazy-binds retrieval runtime types while continuing to delegate to the canonical retrieval facade, so engine callers keep the same FTS-first runtime contract without the eager import-cycle coupling.
- Direct retrieval bundle payloads now surface authoritative ranked `retrieved_doc_ids` and `retrieved_excerpt_ids`, which makes downstream basket/context promotion consume the same ranked ids produced by the FTS-first retrieval path.
- PageIndex and embeddings remain compatibility-only paths and are not required MVP runtime paths in this reviewed slice.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: resubmit the retrieval handoff against the actual branch-tip implementation instead of the stale pre-`bca26c21` slice.
- Risk reason: approved shared regression coverage in `tests/unit/test_unified_retrieval.py` makes the lane shared/high-risk, and the branch-tip handoff also includes packet artifacts that must stay traceable to the real runtime retrieval scope.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Regenerate the canonical kickoff and handoff packet fields so they describe the real branch-tip reviewed slice through `bca26c21e58161f0e3da8fdaf8049ef84771d934`.
2. Update `Scope completed`, `Tasks completed`, `Files changed`, and gate reporting so they match the current retrieval implementation and packet-supporting files.
3. Restate the AGENTS-required canonical demo-path sentence for the retrieval step and make the FTS-first MVP gate explicit against the refreshed reviewed range.
4. Re-run the required local gates on the refreshed packet branch head and record the outcomes for re-review.

### Early Review Triggers

- before first edit to any shared/integrator-locked file
- before changing public interfaces or command contracts
- before touching provider routing/config behavior

### Stop Triggers

- unresolved test/lint/typecheck after 2 attempts
- unresolved `make scope-check`
- budget/size/time limit hit

### Checkpoint Cadence (short updates)

- plan complete
- first green tests
- before risky/shared file edit
- ready for handoff

### Handoff Packet

- branch name
- tasks completed (numbered)
- files changed
- commands run + outcomes
- risks/blockers
- all required fields from `INTEGRATION.md`

## Tasks Completed

1. Preserved the FTS-first retrieval contract across the canonical retrieval service and the engine retrieval facade while lazy-binding engine runtime types in `src/qual/engine/retrieval/__init__.py`.
2. Kept excerpt lookup on the authoritative FTS-only path in `src/qual/retrieval/service.py` and covered the fail-closed PageIndex-only case in approved shared regression coverage.
3. Exposed ranked `retrieved_doc_ids` and `retrieved_excerpt_ids` in retrieval bundles so downstream workflow consumers can use the same ranked ids produced by the retrieval service.
4. Refreshed the handoff artifacts to match the actual branch-tip reviewed implementation range, the retrieval demo-path step, and the FTS-first MVP gate.

## Files Changed

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`
- `docs/gate_passed.txt`
- `src/qual/engine/retrieval/__init__.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

## Commands Run With Results

- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Reviewer Fix Closure

1. The packet now describes the real reviewed implementation through `bca26c21e58161f0e3da8fdaf8049ef84771d934`, which includes the later runtime `src/qual/retrieval/service.py` change the reviewer called out.
2. `Scope completed`, `Tasks completed`, `Files changed`, and the gate summary now map to the actual branch-tip handoff slice instead of the stale pre-`bca26c21` slice.
3. The AGENTS-required canonical demo-path step is stated explicitly as `retrieve relevant material`.
4. The packet now states directly that the refreshed reviewed range remains FTS-first for the MVP and that PageIndex and embeddings remain non-primary paths.

## Risks / Blockers

- Risk: `HIGH`
- Compatibility risk: downstream callers that still pass PageIndex-only excerpt ids to `RetrievalService.fetch_excerpt` now fail closed with `KeyError`, so consumers must preserve canonical FTS excerpt ids from the authoritative retrieval path.
- Blockers: none

## Ready For Handoff

- Status: ready for handoff

## Required Handoff Fields

### Roadmap item(s) affected

- `Milestone 3: Real workflow loop`
- `feat-retrieval-fts`: retrieval/search

### Vision capability affected

- `Retrieval-first context handling`
- `Auditable state and workflow`

### Routing/provider impact note

- None

### Proposed `README.md` patch text

- None

## Scope-Check / Ownership Note

- Shared-by-approval edits in reviewed range: `YES`
- Integrator-locked edits in reviewed range: `NO`
- Approved shared regression coverage remains limited to `tests/unit/test_unified_retrieval.py`.
