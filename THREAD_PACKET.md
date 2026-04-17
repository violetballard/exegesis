# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet refresh role: `reviewer-fix handoff regeneration`
- Current branch head before this fixer commit: `0bf7ccda2294e87cbca054b7eea3b89d0db62ab8`
- Reviewed implementation head: `0bf7ccda2294e87cbca054b7eea3b89d0db62ab8`
- Reviewed implementation range for re-review: `378cf9a74a3658058079a32f186fcd254c4a4034..0bf7ccda2294e87cbca054b7eea3b89d0db62ab8`

## Scope goal

- Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt and provenance output.

## Scope completed

- The reviewed implementation range keeps SQLite FTS authoritative for this MVP lane and preserves PageIndex plus embeddings as deferred compatibility paths rather than required runtime paths.
- The excerpt lookup surface now stays on the canonical FTS-only path, so PageIndex-only excerpt IDs fail closed instead of promoting a non-canonical runtime fallback.
- Retrieval context bundles rebuilt from source-bundle-only inputs now reconstruct the canonical downstream payload instead of echoing the source bundle shape, keeping downstream workflow payloads deterministic on the canonical engine surface.
- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proves both the FTS-only excerpt contract and the source-bundle context reconstruction behavior.

## Canonical demo-path step advanced

- `retrieve relevant material`
- This reviewed slice makes that step more real by keeping excerpt lookup fail-closed to the authoritative FTS path and by preserving deterministic retrieval context payloads before downstream basket promotion.
- The immediate downstream step it supports is `promote or gather context into the basket`, but this packet remains scoped to the retrieval step itself.

## Tasks completed

1. Removed the PageIndex fallback from `fetch_excerpt` so the public excerpt lookup surface now resolves through the canonical FTS-only path.
2. Added approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proving PageIndex-only excerpt IDs fail closed with `KeyError`.
3. Fixed source-bundle context reconstruction so retrieval context bundles rebuild the canonical downstream payload rather than returning the source bundle as the downstream payload snapshot.
4. Extended shared regression coverage in `tests/unit/test_unified_retrieval.py` to verify source-bundle-only context reconstruction keeps the canonical downstream payload shape intact.

## Files changed

### Reviewed implementation files

- `src/qual/retrieval/service.py`
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
- `feat-retrieval-fts - retrieval/search` because this reviewed slice preserves the lane's authoritative excerpt lookup and retrieval context payload contracts.

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

- Re-review should anchor to the reviewed implementation range `378cf9a74a3658058079a32f186fcd254c4a4034..0bf7ccda2294e87cbca054b7eea3b89d0db62ab8`.
- This packet intentionally includes `0bf7ccda2294e87cbca054b7eea3b89d0db62ab8` because it changes retrieval code in `src/qual/engine/retrieval/payload.py` and shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Use the final HEAD SHA reported with this fixer handoff for the post-fix branch tip.
