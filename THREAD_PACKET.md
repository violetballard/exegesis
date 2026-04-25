# Thread Handoff Packet

- Lane: `feat-retrieval-fts`
- Branch: `codex/feat-retrieval-fts`
- Commit: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Packet refresh commit: `reported in final fixer handoff`
- Packet refresh role: `metadata-only reviewer-fix finalization`
- Pre-fix packet refresh trace anchor: `778eb5db8d5623d58a12051794ef720cb23ebd3a`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`

## Packet traceability note

- `378cf9a74a3658058079a32f186fcd254c4a4034` is the direct parent of `adfa8cdadd43747ffbcb612e4151e262b13e52ca`, so this reviewed implementation range is intentionally a single-commit slice.
- Review the implementation against that exact one-commit range; later packet-refresh commits remain metadata-only unless this handoff is regenerated.

## Current program focus

- Close the engine-side Milestone 3 workflow loop before activating any Textual UI lanes.

## Current engine execution order

1. `feat-context-storage` - Persistence floor for document, basket, vault, and session state.
2. `feat-commands` - Stable command surface for the CLI-first MVP loop.
3. `feat-retrieval-fts` - Authoritative FTS-first retrieval for engine runs.
4. `feat-engine-runs` - Close the plan, revise, patch, and apply loop in the engine.
5. `feat-a2ui-contract` - Support the engine loop with stable shared contracts, not UI ambition.

## Scope goal

- Tighten the canonical excerpt lookup surface so the engine's FTS-first retrieval path fails closed instead of silently rehydrating PageIndex-only excerpts.

## Priority outcomes

1. Keep SQLite FTS as the primary retrieval path.
2. Ensure excerpt lookup uses the same canonical FTS evidence path as retrieval results.
3. Prove that PageIndex-only excerpt IDs are rejected instead of being normalized into mixed-source payloads.

## Definition of done for this lane

- Retrieval is FTS-first by default.
- Excerpt lookup fails closed on the canonical FTS path.
- Shared regression coverage proves PageIndex-only excerpt IDs are rejected.

## Do not spend time on

- Broadening the reviewed slice into earlier retrieval facade or provenance-bundle work.
- UI rendering concerns.
- Search features outside the core writing loop.

## Lane/owned paths

- `src/qual/retrieval/**`
- `src/qual/engine/retrieval/**`
- `engine/src/exegesis_engine/retrieval/**`

## Scope completed

- The reviewed slice is the single implementation commit `adfa8cdadd43747ffbcb612e4151e262b13e52ca` only.
- In `src/qual/retrieval/service.py`, `fetch_excerpt` now delegates directly to the canonical `_lookup_fts_excerpt(...)` path and no longer falls back to PageIndex normalization.
- In `tests/unit/test_unified_retrieval.py`, shared regression coverage now asserts both a synthetic PageIndex-only document and an existing PageIndex query path raise `KeyError` when `fetch_excerpt` is asked to resolve non-FTS excerpt IDs.
- This handoff deliberately excludes earlier retrieval-surface and provenance-bundle work from scope; those behaviors are not claimed as part of this re-review packet.

## Canonical demo-path step advanced

- `retrieve relevant material`
- This work makes the `retrieve relevant material` step more real by ensuring excerpt follow-up reads use the same FTS-backed source of truth as the retrieval hit that surfaced the material.
- The fail-closed behavior strengthens the demo path by preventing PageIndex-only excerpts from masquerading as canonical retrieval evidence.

## Kickoff budget/limits compliance

- This handoff is high-risk only because it includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, so the 4-task cap applies.
- The reviewed implementation slice changes 2 files with 59 lines touched in `adfa8cdadd43747ffbcb612e4151e262b13e52ca`, which fits the shared/high-risk size budget.
- The packet accounts for the full reviewed slice in 2 meaningful tasks and does not claim broader cumulative retrieval work.

## Approved exception note

- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for the `feat-retrieval-fts` lane; it is the sole shared-by-approval regression surface for this reviewed slice and exercises the canonical retrieval contract.

## Tasks completed

1. Removed the PageIndex fallback from `fetch_excerpt` so the canonical excerpt lookup surface now resolves only through the FTS-backed lookup path.
2. Added approved shared regression coverage proving PageIndex-only excerpt IDs now fail closed with `KeyError` instead of being normalized as retrieval payloads.

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
- Blockers: `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` are read-only in this worktree, so the packet mirrors there could not be updated in this fixer pass.

## Required handoff fields

### Roadmap item(s) affected

- `ROADMAP.md`: Milestone 3: Real workflow loop
- `feat-retrieval-fts` - authoritative FTS-first retrieval feeding the engine loop.

### Vision capability affected

- `2. Retrieval-first context handling`
- `3. Auditable generation`

### Canonical demo-path step advanced

- `retrieve relevant material`
- This work makes the `retrieve relevant material` step more real by forcing excerpt follow-up reads through the same canonical FTS-backed evidence path as the retrieval hit itself.

### Routing/provider impact note

- None

## Scope-check / ownership note

- Shared/integrator-locked edits: `YES`
