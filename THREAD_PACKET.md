# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet refresh role: `reviewer-fix handoff regeneration`
- Current branch head before this fixer commit: `5f1f7c6275dd0e3f4d4c910e43d0426390476aa0`
- Reviewed implementation head: `5f1f7c6275dd0e3f4d4c910e43d0426390476aa0`
- Reviewed implementation range for re-review: `378cf9a74a3658058079a32f186fcd254c4a4034..5f1f7c6275dd0e3f4d4c910e43d0426390476aa0`

## Scope goal

- Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt and provenance output.

## Scope completed

- The reviewed implementation range keeps SQLite FTS authoritative for this MVP lane and preserves PageIndex plus embeddings as deferred compatibility paths rather than required runtime paths.
- The excerpt lookup surface stays on the canonical FTS-only path, so PageIndex-only excerpt IDs fail closed instead of promoting a non-canonical runtime fallback.
- Retrieval payloads, provenance snapshots, citation bundles, source-bundle reconstruction, and basket-promotion fields are normalized so downstream engine flows receive deterministic canonical payloads.
- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proves the FTS-only excerpt contract, source-bundle context reconstruction, citation normalization, and basket-promotion normalization behavior.

## Canonical demo-path step advanced

- `retrieve relevant material`
- This reviewed slice makes that step more real by keeping excerpt lookup fail-closed to the authoritative FTS path and by preserving deterministic retrieval payloads before downstream basket promotion.
- The immediate downstream step it supports is `promote or gather context into the basket`, but this packet remains scoped to the retrieval step itself.

## Tasks completed

1. Kept the public excerpt lookup surface and retrieval facades FTS-first, including the fail-closed `fetch_excerpt` path and canonical retrieval aliases.
2. Canonicalized retrieval payload, query, provenance, evidence, and citation snapshots so sparse source and context bundles rebuild deterministic downstream payloads.
3. Preserved basket-promotion context through retrieval payloads and normalized promotion identity fields for downstream workflow use.
4. Added approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for FTS-only excerpt lookup, payload reconstruction, citation normalization, and basket-promotion normalization.

## Files changed

### Reviewed implementation files

- `src/qual/retrieval/__init__.py`
- `src/qual/retrieval/service.py`
- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/embeddings_strategy.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/interface.py`
- `src/qual/engine/retrieval/pageindex_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `tests/unit/test_unified_retrieval.py`

### Packet / handoff files

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

- `Milestone 3: Real workflow loop` because this reviewed slice keeps the engine retrieval path FTS-first, deterministic, and auditable.
- `feat-retrieval-fts - retrieval/search` because this reviewed slice preserves the lane's authoritative excerpt lookup, payload, and basket-promotion contracts.

### Vision capability affected

- `Retrieval-first context handling`
- `Auditable state and workflow`

### Routing/provider impact note

- None

## Scope-check / ownership note

- Shared-by-approval edits: `YES`
- Approved shared regression surface: `tests/unit/test_unified_retrieval.py`
- Integrator-locked edits: `NO`

## Traceability note

- Re-review should anchor to the reviewed implementation range `378cf9a74a3658058079a32f186fcd254c4a4034..5f1f7c6275dd0e3f4d4c910e43d0426390476aa0`.
- This regenerated handoff intentionally includes the committed retrieval changes after `adfa8cdadd43747ffbcb612e4151e262b13e52ca`, including `0bf7ccda2294e87cbca054b7eea3b89d0db62ab8`, `9ae8e5e8af717b7dc08ca2cba78ee2b0ffdf1db5`, `49b540f75bdc3873579d8caa35f42d970611a2db`, and `5f1f7c6275dd0e3f4d4c910e43d0426390476aa0`.
- Use the final HEAD SHA reported with this fixer handoff for the post-fix branch tip.
