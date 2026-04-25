# Thread Handoff Packet

- Lane: `feat-retrieval-fts`
- Branch: `codex/feat-retrieval-fts`
- Commit: `b9aa3451d28bf86c8d07ff06a9a86a647a200664`
- Packet refresh commit: `reported in final fixer handoff`
- Packet refresh role: `metadata-only packet regeneration for corrected review traceability`
- Pre-fix packet trace anchor: `b9aa3451d28bf86c8d07ff06a9a86a647a200664`
- Reviewed implementation range: `e6ec49365e1d0e1a3631b8a71b3af32bbe08aafd..b9aa3451d28bf86c8d07ff06a9a86a647a200664`

## Packet traceability note

- `e6ec49365e1d0e1a3631b8a71b3af32bbe08aafd` is the direct parent of `b9aa3451d28bf86c8d07ff06a9a86a647a200664`, so this reviewed implementation range is intentionally a single-commit slice.
- The reviewed implementation commit is the current branch tip before this fixer pass. The follow-up fixer commit is metadata-only and must not be treated as part of the reviewed implementation range.

## Current program focus

- Close the engine-side Milestone 3 workflow loop before activating any Textual UI lanes.

## Current engine execution order

1. `feat-context-storage` - Persistence floor for document, basket, vault, and session state.
2. `feat-commands` - Stable command surface for the CLI-first MVP loop.
3. `feat-retrieval-fts` - Authoritative FTS-first retrieval for engine runs.
4. `feat-engine-runs` - Close the plan, revise, patch, and apply loop in the engine.
5. `feat-a2ui-contract` - Support the engine loop with stable shared contracts, not UI ambition.

## Scope goal

- Canonicalize sparse lookup constraint mirrors so FTS excerpt promotion emits the same deterministic, auditable query-constraint payload shape as the canonical retrieval path.

## Priority outcomes

1. Keep SQLite FTS as the primary retrieval path.
2. Ensure sparse excerpt lookup mirrors canonicalize query constraints before provenance is emitted.
3. Keep downstream retrieval evidence deterministic when constraint defaults are rehydrated from saved excerpt context.

## Definition of done for this lane

- Retrieval remains FTS-first by default.
- Sparse excerpt lookup mirrors expose canonicalized `query_constraints` fields and defaulted mirror fields.
- Shared regression coverage proves the canonicalized mirror contract end to end.

## Do not spend time on

- Broadening scope beyond the sparse lookup constraint-mirroring fix.
- UI rendering concerns.
- Search features outside the core writing loop.

## Lane/owned paths

- `src/qual/retrieval/**`
- `src/qual/engine/retrieval/**`
- `engine/src/exegesis_engine/retrieval/**`

## Scope completed

- The reviewed slice is the single implementation commit `b9aa3451d28bf86c8d07ff06a9a86a647a200664`.
- In `src/qual/retrieval/service.py`, sparse excerpt lookup mirror fields now canonicalize `query_constraints` before the top-level and provenance mirror fields are derived, so absent values fail closed to the same normalized defaults used by the retrieval service.
- In `tests/unit/test_unified_retrieval.py`, approved shared regression coverage now verifies that sparse lookup mirrors expose canonicalized `query_constraints`, defaulted query mirror fields, and matching basket-promotion fields after excerpt rehydration.

## Canonical demo-path step advanced

- `retrieve relevant material`
- This work advances `retrieve relevant material` by making sparse excerpt lookups preserve canonical, auditable retrieval constraint mirrors when saved FTS context is rehydrated into provenance and basket-promotion payloads.

## Kickoff budget/limits compliance

- This reviewed implementation slice is high-risk because it includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- The slice changes 2 files and stays within the 4-task high-risk cap as a 2-task handoff.

## Approved exception note

- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` is part of this reviewed slice because it exercises the canonical retrieval contract for sparse excerpt lookup mirrors.

## Tasks completed

1. Canonicalized sparse excerpt lookup `query_constraints` mirrors before derived query mirror fields are emitted so lookup promotion uses the same normalized constraint contract as the main retrieval path.
2. Added shared regression coverage that proves sparse excerpt rehydration emits canonicalized query mirror fields and matching basket-promotion metadata.

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

- `ROADMAP.md`: Milestone 3: Real workflow loop
- `feat-retrieval-fts` - authoritative FTS-first retrieval feeding the engine loop.

### Vision capability affected

- `2. Retrieval-first context handling`
- `6. Auditable state and workflow`

### Canonical demo-path step advanced

- `retrieve relevant material`
- This work advances `retrieve relevant material` by making sparse excerpt lookups preserve canonical, auditable retrieval constraint mirrors when saved FTS context is rehydrated into provenance and basket-promotion payloads.

### Routing/provider impact note

- None

## Scope-check / ownership note

- Shared/integrator-locked edits: `YES`
- Approved exception: `tests/unit/test_unified_retrieval.py`
