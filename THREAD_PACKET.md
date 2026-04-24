# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `retrieval query canonicalization`

## Scope Goal

- Keep the FTS-first retrieval lane deterministic by making the canonical query builder normalize `query_text` the same way downstream payloads, provenance, and fingerprints already do.

## Scope Completed

- Canonicalized `build_retrieval_query()` so query objects emitted through the retrieval facade now casefold and collapse query text before engine use.
- Updated the builder contract note to state that query text is part of the deterministic normalization surface.
- Kept the change inside retrieval-owned code and preserved the FTS-first/PageIndex-deferred boundary.

## Thread Kickoff

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`
- Scope goal: tighten the canonical retrieval query constructor so engine callers receive the same normalized query text that downstream retrieval payloads and fingerprints already expect.

### Budget

- Task budget: `8`
- Time budget: `45m`
- Size limits: `<=12 files`, `<=500 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks

1. Inspect the retrieval-owned query-construction path and confirm the deterministic contract gap.
2. Patch the canonical retrieval facade without expanding into deferred retrieval strategies.
3. Run focused retrieval validation and the required lane gates.
4. Refresh the handoff packet with the actual change and verification results.

### Stop Triggers

- integrator-locked/shared-by-approval edits needed
- unresolved test/lint/typecheck after 2 attempts
- unresolved `make scope-check`
- budget/size/time limit hit

### Checkpoint Cadence

- plan complete
- first green tests
- before risky/shared file edit
- ready for handoff

## AGENTS Checkpoint Evidence

- `plan complete`: narrowed the work to the canonical retrieval query builder in `src/qual/retrieval/__init__.py`.
- `first green tests`: `python -m unittest tests.unit.test_unified_retrieval` passed after the builder change.
- `before risky/shared file edit`: no risky/shared file edits were needed; scope stayed fully inside lane-owned retrieval paths.
- `ready for handoff`: required gates passed and the packet now reflects the current retrieval-owned change instead of the earlier metadata-only packet refresh work.

## Tasks Completed

1. Identified that the canonical retrieval builder still preserved caller casing in `query_text` even though retrieval payloads and fingerprints already canonicalized it.
2. Normalized builder-emitted query text with casefolded whitespace-collapsed output so engine callers now get the deterministic query object directly.
3. Re-ran focused retrieval validation plus all required handoff gates.
4. Replaced the stale packet-refresh handoff with this commit-scoped integration packet.

## Files Changed

- `src/qual/retrieval/__init__.py`
- `THREAD_PACKET.md`

## Commands Run With Results

- `python -m unittest tests.unit.test_unified_retrieval`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Risks / Blockers

- Risk: `LOW`
- No shared-by-approval or integrator-locked files were edited in this pass.
- No routing/provider behavior changed.

## Required Handoff Fields

### Roadmap item(s) affected

- `ROADMAP.md: Milestone 3: Product Readiness`
- `ROADMAP.md: Milestone 4: Retrieval Layer`

### Vision capability affected

- `2. Retrieval-first context handling`
- `3. Auditable generation`

### Routing/provider impact note

- None

### Proposed `README.md` patch text

- None

## Scope-Check / Ownership Note

- Shared-by-approval edits in this pass: `NO`
- Integrator-locked edits in this pass: `NO`
- Retrieval remains FTS-first; PageIndex and embeddings stay deferred/fallback-only.
