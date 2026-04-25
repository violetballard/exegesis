# Thread Handoff Packet

- Lane: `feat-retrieval-fts`
- Branch: `codex/feat-retrieval-fts`
- Commit: `5885b67031db4c51dffe7bce7647bae265d4f236`
- Packet refresh commit: `reported in final fixer handoff`
- Packet refresh role: `metadata-only reviewer-fix finalization`
- Pre-fix packet refresh trace anchor: `af6dbf89c145f6157378deca5c9e5dd42b0ea193`
- Reviewed implementation range: `8356d5f2d0ee39f2e079bb1059a79e397ba58a91..5885b67031db4c51dffe7bce7647bae265d4f236`

## Packet traceability note

- `8356d5f2d0ee39f2e079bb1059a79e397ba58a91` is the direct parent of `5885b67031db4c51dffe7bce7647bae265d4f236`, so this reviewed implementation range is intentionally a single-commit slice.
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

- Tighten canonical lookup-promotion defaults so the engine's FTS-first retrieval path preserves deterministic, auditable constraint snapshots when excerpt provenance is rehydrated.

## Priority outcomes

1. Keep SQLite FTS as the primary retrieval path.
2. Ensure excerpt provenance rehydration uses the same canonical constraint normalization path as retrieval results.
3. Keep query constraint snapshots stable across lookup promotion so downstream workflow evidence stays deterministic.

## Definition of done for this lane

- Retrieval is FTS-first by default.
- Excerpt provenance promotion uses canonicalized query-constraint payloads.
- Lookup-driven retrieval snapshots stay deterministic and auditable.

## Do not spend time on

- Broadening the reviewed slice into earlier excerpt fail-closed work or wider retrieval facade changes.
- UI rendering concerns.
- Search features outside the core writing loop.

## Lane/owned paths

- `src/qual/retrieval/**`
- `src/qual/engine/retrieval/**`
- `engine/src/exegesis_engine/retrieval/**`

## Scope completed

- The reviewed slice is the single implementation commit `5885b67031db4c51dffe7bce7647bae265d4f236` only.
- In `src/qual/retrieval/service.py`, lookup-promotion query constraints now pass through `_canonical_query_constraint_snapshot_payload(...)` before the excerpt provenance snapshot is constructed.
- This keeps lookup-triggered retrieval summaries aligned with the canonical retrieval constraint shape used elsewhere in the FTS-first retrieval service instead of preserving raw, potentially non-canonical constraint payloads.
- This handoff deliberately excludes earlier excerpt fail-closed work and broader retrieval-facade changes from scope; those behaviors are not newly claimed as part of this re-review packet.

## Canonical demo-path step advanced

- `retrieve relevant material`
- This work advances `retrieve relevant material` by canonicalizing lookup-promotion constraint snapshots before provenance is emitted, which keeps downstream basket and workflow use tied to deterministic, auditable retrieval evidence.

## Kickoff budget/limits compliance

- This reviewed implementation slice changes 1 lane-owned file with 7 lines touched in `5885b67031db4c51dffe7bce7647bae265d4f236`, which fits the high-risk size budget.
- The packet accounts for the full reviewed slice in 1 meaningful task and does not claim broader cumulative retrieval work.

## Approved exception note

- No additional shared-by-approval files are part of this reviewed slice.

## Tasks completed

1. Canonicalized lookup-promotion query constraints before excerpt provenance snapshots are emitted so retrieval diagnostics and summaries keep the same deterministic constraint shape as the rest of the FTS-first service.

## Files changed

### Reviewed implementation files

- `src/qual/retrieval/service.py`

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
- This work advances `retrieve relevant material` by canonicalizing lookup-promotion constraint snapshots before provenance is emitted, which keeps downstream basket and workflow use tied to deterministic, auditable retrieval evidence.

### Routing/provider impact note

- None

## Scope-check / ownership note

- Shared/integrator-locked edits: `NO`
