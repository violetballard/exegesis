# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet refresh role: `reviewer-fix traceability correction`
- Current branch head before this fixer commit: `c59f89132c1e24cacd4e8c5b0bfc6df0d5455cad`
- Latest runtime implementation head in that branch state: `c162148380388589a552b1d722889d0fca9f5bdf`
- Re-review branch-tip range before this fixer commit: `378cf9a74a3658058079a32f186fcd254c4a4034..c59f89132c1e24cacd4e8c5b0bfc6df0d5455cad`

## Scope goal

- Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt and provenance output.

## Scope completed

- The reviewed branch state keeps SQLite FTS authoritative for this MVP lane.
- The excerpt lookup surface stays on the canonical FTS-only path, so PageIndex-only excerpt IDs fail closed instead of promoting a non-canonical runtime fallback.
- Ranked retrieval doc/excerpt ids are carried into basket-promotion metadata so downstream consumers can preserve authoritative FTS ordering.
- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` exercises the canonical retrieval contract.

## Canonical demo-path step advanced

- `retrieve relevant material`
- This branch state makes that step more real by ensuring excerpt lookup resolves only through the authoritative FTS-backed path and by preserving the ranked retrieval ids that downstream basket-promotion consumers need.
- The immediate downstream step it supports is `promote or gather context into the basket`, but this packet remains scoped to the retrieval step itself.

## Tasks completed

1. Kept excerpt lookup on the canonical FTS-only path so PageIndex-only excerpt ids fail closed through the public retrieval surface.
2. Normalized retrieval payload, provenance, and source-bundle snapshots so downstream engine consumers receive deterministic FTS-first metadata.
3. Preserved authoritative FTS shortlist and ranking data in basket-promotion metadata, including ranked retrieval doc ids and excerpt ids for downstream promotion flows.
4. Kept approved shared regression coverage in `tests/unit/test_unified_retrieval.py` aligned with the canonical retrieval contract.

## Files changed

### Reviewed implementation files in the branch-tip range

- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/embeddings_strategy.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/interface.py`
- `src/qual/engine/retrieval/pageindex_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/__init__.py`
- `src/qual/retrieval/service.py`
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

- `Milestone 3: Real workflow loop` because this branch state keeps the engine retrieval path FTS-first, deterministic, and auditable.
- `feat-retrieval-fts - retrieval/search` because this branch state preserves the lane's authoritative retrieval contract.

### Vision capability affected

- `Retrieval-first context handling`
- `Auditable state and workflow`

### Canonical demo-path step advanced

- `retrieve relevant material`
- This branch state makes that step more real by ensuring excerpt lookup only succeeds through the authoritative FTS-backed path and by preserving ranked retrieval ids for later basket promotion.

### Routing/provider impact note

- None

## Scope-check / ownership note

- Shared-by-approval edits: `YES`
- Approved shared regression surface: `tests/unit/test_unified_retrieval.py`
- Integrator-locked edits: `NO`

## Traceability note

- The prior packet was stale because it claimed `c162148380388589a552b1d722889d0fca9f5bdf` was metadata-only and did not describe the real branch tip `c59f89132c1e24cacd4e8c5b0bfc6df0d5455cad`.
- Re-review should anchor to the branch-tip range `378cf9a74a3658058079a32f186fcd254c4a4034..c59f89132c1e24cacd4e8c5b0bfc6df0d5455cad`.
- Treat `c162148380388589a552b1d722889d0fca9f5bdf` as reviewed runtime implementation, not as a metadata-only packet refresh.
- Use the final HEAD SHA reported with this fixer handoff for the post-fix branch tip.
