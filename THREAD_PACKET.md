# Thread Handoff Packet

- Lane: `feat-retrieval-fts`
- Branch: `codex/feat-retrieval-fts`
- Commit: `e5d20f4012eed3c1e12e9acea2737e1e03dad50b`
- Packet refresh commit: `reported in final fixer handoff`
- Packet refresh role: `metadata-only reviewer-fix finalization`
- Reviewed implementation range: `combined retrieval implementation ending at e5d20f4012eed3c1e12e9acea2737e1e03dad50b; later packet-refresh commits remain metadata-only`

## Packet traceability note

- The prior packet incorrectly described an excerpt-only slice.
- This packet treats the lane as one combined high-risk retrieval handoff.
- Review the retrieval implementation against the commits listed in `Reviewed implementation commits`; later packet-refresh commits are metadata-only unless this handoff is regenerated.

## Reviewed implementation commits

1. `c7ca5bcdb3a1b829712c4b3d2f3a39e2bd26c14f` - enforce FTS-only hit strategies
2. `f8a32d372301be4a7c67b97a66ddc8e04f36011f` - add FTS provenance retrieval bundles
3. `4387c7277d8d983012d970312a6bcc14f6fb571d` - canonicalize hit provenance strategy metadata
4. `2389add23c703d2084922c3b446352ec50ac5ab8` - canonicalize retrieval query constructor text
5. `3b85692c04297f9373e48c94a82635a7df83d923` - canonicalize builder query text
6. `adfa8cdadd43747ffbcb612e4151e262b13e52ca` - make retrieval excerpts FTS-only
7. `e5d20f4012eed3c1e12e9acea2737e1e03dad50b` - reject binary engine query metadata

## Current program focus

- Close the engine-side Milestone 3 workflow loop before activating any Textual UI lanes.

## Current engine execution order

1. `feat-context-storage` - Persistence floor for document, basket, vault, and session state.
2. `feat-commands` - Stable command surface for the CLI-first MVP loop.
3. `feat-retrieval-fts` - Authoritative FTS-first retrieval for engine runs.
4. `feat-engine-runs` - Close the plan, revise, patch, and apply loop in the engine.
5. `feat-a2ui-contract` - Support the engine loop with stable shared contracts, not UI ambition.

## Scope goal

- Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt and provenance output.

## Priority outcomes

1. Keep SQLite FTS as the primary retrieval path.
2. Return stable, structured hits suitable for basket promotion and downstream workflow use.
3. Keep provenance, query metadata, and excerpt payloads deterministic and auditable.

## Definition of done for this lane

- Retrieval is FTS-first by default.
- Results are structured and deterministic enough for basket promotion and workflow cards.
- Excerpt provenance is stable and auditable.
- The canonical engine-facing retrieval helpers stay aligned with the FTS-first contract.

## Do not spend time on

- Over-investing in embeddings or alternate retrieval modes.
- UI rendering concerns.
- Search features outside the core writing loop.

## Lane/owned paths

- `src/qual/retrieval/**`
- `src/qual/engine/retrieval/**`
- `engine/src/exegesis_engine/retrieval/**`

## Scope completed

- Hardened the canonical retrieval surface so `RetrievalHit`, `RetrievalDocHit`, hit provenance payloads, and excerpt lookup resolution all fail closed to the FTS-first contract instead of accepting PageIndex-style strategy drift.
- Added and stabilized the canonical provenance-bundle surface for both direct service calls and package-level helpers, including `retrieve_fts_provenance_bundle`, `retrieve_auto_provenance_bundle`, and the mirrored engine/package exports that downstream engine flows call.
- Canonicalized downstream payload, context bundle, source bundle, citation bundle, and query-builder metadata so query text, query constraints, policy snapshots, shortlist order, and source provenance round-trip deterministically through the engine surface.
- Tightened excerpt lookup to the canonical FTS-only path by removing the `fetch_excerpt` PageIndex fallback and rejecting binary query metadata on the engine-facing retrieval helpers.
- Added broad shared regression coverage proving the FTS-only source-strategy contract, provenance-bundle helpers, helper/export behavior, snapshot safety, and PageIndex-only excerpt failures.

## Canonical demo-path step advanced

- `retrieve relevant material`
- This work makes `retrieve relevant material` more real by ensuring the engine retrieves, serializes, and rehydrates auditable FTS-backed hits and provenance through the same canonical helper surface that downstream workflow steps use.
- The provenance-bundle additions strengthen the same step rather than broadening scope: they make the retrieval result usable for basket promotion and later workflow cards without introducing a new retrieval mode.

## Kickoff budget/limits compliance

- This handoff is shared/high-risk work because it includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- The handoff is accounted as `4` meaningful high-risk tasks, not an excerpt-only 2-task slice.
- Later packet-refresh commits do not change the reviewed retrieval implementation.

## Approved exception note

- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for the `feat-retrieval-fts` lane; it is the sole shared-by-approval regression surface for the lane and exercises the canonical retrieval contract.

## Tasks completed

1. Enforced the FTS-first source-strategy contract across retrieval hits, doc hits, provenance normalization, and excerpt lookup resolution.
2. Added the canonical provenance-bundle service and package helper surface used by the engine-facing retrieval contract.
3. Canonicalized query-builder, downstream payload, source/context bundle, and audit metadata so retrieval outputs stay deterministic and auditable for the writing loop.
4. Added approved shared regression coverage for helper exports, snapshot-safe bundle rebuilding, provenance helpers, binary query metadata rejection, and FTS-only excerpt failures.

## Files changed

### Reviewed implementation files

- `src/qual/retrieval/__init__.py`
- `src/qual/retrieval/service.py`
- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/interface.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/pageindex_strategy.py`
- `src/qual/engine/retrieval/embeddings_strategy.py`
- `tests/unit/test_unified_retrieval.py`

### Metadata-only handoff files

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`
- `codex_packet_handoff/tools/init_lane_meta.py`
- `codex_packet_handoff/tools/planner.py`
- `tests/unit/test_packet_planner.py`
- `docs/gate_passed.txt`
- `docs/retrieval_post_adfa_commit_accounting.md`

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

- Milestone 3: Real workflow loop - retrieval stays the authoritative context path for the engine loop.
- `feat-retrieval-fts` - authoritative FTS-first retrieval feeding the engine loop.

### Vision capability affected

- Retrieval-first context handling
- Auditable state and workflow

### Canonical demo-path step advanced

- `retrieve relevant material`
- This work makes the `retrieve relevant material` step more real by strengthening the canonical engine-facing retrieval surface and its auditable provenance outputs.

### Routing/provider impact note

- None

## Scope-check / ownership note

- Shared/integrator-locked edits: `YES`
