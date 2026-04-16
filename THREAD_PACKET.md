# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Reviewed implementation head before final handoff refresh: `168ee849304999df4127eeba1c36d8f6f889a6c3`
- Packet refresh commit: `reported in final fixer handoff`
- Packet refresh role: `lane handoff metadata refresh`
- Reviewed implementation range: `75572c120239a84402a82b845c3df797806fcdf4..168ee849304999df4127eeba1c36d8f6f889a6c3`

## Scope goal
- Keep the retrieval lane scoped to the FTS-first MVP contract for engine flows: deterministic query/payload/provenance output, canonical facade exports, and FTS-only excerpt lookup behavior.

## Scope completed
- SQLite FTS remains the authoritative MVP retrieval path in the reviewed implementation range.
- Retrieval exports and bundle helpers now surface deterministic query, payload, provenance, citation, and source snapshots through both retrieval facades.
- `fetch_excerpt` and the canonical excerpt lookup surface fail closed on the FTS-only path instead of accepting PageIndex-only excerpt payloads.
- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` exercises the canonical FTS-first retrieval contract, including the fail-closed excerpt lookup behavior.
- PageIndex and embeddings remain compatibility-only paths and are not restored as required runtime retrieval backends.

## Canonical Demo-Path Step Advanced
- Canonical demo-path step advanced: `retrieve relevant material`
- This reviewed implementation range makes `retrieve relevant material` more real by keeping retrieval output deterministic and auditable while forcing excerpt lookup through the canonical FTS-only path.

## AGENTS.md Handoff Packet
- Risk reason: shared/high-risk work because the reviewed implementation includes the approved shared regression surface `tests/unit/test_unified_retrieval.py`.
- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`
- Tasks completed:
  1. Kept SQLite FTS authoritative and exported the canonical retrieval query plus retrieval helpers through both retrieval facades.
  2. Canonicalized retrieval payload, provenance, citation, and source bundle snapshots for deterministic downstream engine use.
  3. Hardened excerpt lookup so the public retrieval surface resolves through the canonical FTS-only path and PageIndex-only excerpt IDs fail closed.
  4. Added and maintained approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for the FTS-first retrieval contract.

## Files changed
### Reviewed implementation files
- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/embeddings_strategy.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/interface.py`
- `src/qual/engine/retrieval/pageindex_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/__init__.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

### Handoff metadata files
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
- `Milestone 3: Real workflow loop`
- `feat-retrieval-fts - authoritative FTS-first retrieval feeding the engine loop`

### Vision capability affected
- `Retrieval-first context handling`
- `Auditable state and workflow`

### Routing/provider impact note
- None

## Scope-check / ownership note
- Shared-by-approval edits: `YES` (Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for the `feat-retrieval-fts` lane; it is the sole shared-by-approval regression surface for the lane and exercises the canonical retrieval contract.)
- Integrator-locked edits: `NO`

## Regression coverage note
- `tests/unit/test_unified_retrieval.py::test_fetch_excerpt_requires_an_fts_lookup_hit`
- `tests/unit/test_unified_retrieval.py::test_retrieval_service_rejects_pageindex_excerpt_payloads`

## Traceability note
- The reviewed implementation range ends at `168ee849304999df4127eeba1c36d8f6f889a6c3`, which removes the off-scope packet-planner drift from the branch diff.
- The current branch tip reported in the final fixer handoff is a metadata-only packet refresh commit.
- No post-reviewed commit changes executable code outside the retrieval lane.
