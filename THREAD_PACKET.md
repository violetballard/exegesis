# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet refresh role: `reviewer-fix current-tip traceability refresh`
- Current branch head before this fixer commit: `85d61f4510633e1d4bc74998fcf93308382b6e9c`
- Reviewed runtime implementation head in that branch state: `e7958b4656b045844262c3547cae0011446faef1`
- Re-review branch-tip range before this fixer commit: `378cf9a74a3658058079a32f186fcd254c4a4034..85d61f4510633e1d4bc74998fcf93308382b6e9c`

## Scope goal

- Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt and provenance output.

## Scope completed

- The reviewed branch state keeps SQLite FTS authoritative for this MVP lane.
- The excerpt lookup surface stays on the canonical FTS-only path, so PageIndex is not part of the MVP excerpt lookup contract for this lane and PageIndex-only excerpt IDs fail closed instead of promoting a non-canonical runtime fallback.
- Excerpt lookup payloads now carry the canonical retrieval policy snapshot at both the top level and inside provenance so downstream engine flows read one stable FTS-first contract.
- Ranked retrieval doc/excerpt ids are preserved in deterministic retrieval metadata so downstream engine consumers can rely on authoritative FTS ordering.
- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` exercises the canonical retrieval contract.

## Canonical demo-path step advanced

- `retrieve relevant material`
- This branch state makes that step more real by ensuring excerpt lookup resolves only through the authoritative FTS-backed path and by keeping the retrieval contract deterministic and auditable for downstream engine flows.
- This packet does not claim to advance `promote or gather context into the basket`; it stays scoped to the retrieval contract itself.

## Tasks completed

1. Kept excerpt lookup on the canonical FTS-only path so PageIndex-only excerpt ids fail closed through the public retrieval surface.
2. Normalized retrieval payload, provenance, and source-bundle snapshots so downstream engine consumers receive deterministic FTS-first metadata, including canonicalized helper `max_results` values and lookup policy snapshots.
3. Preserved authoritative FTS shortlist and ranking data in deterministic retrieval metadata, including ranked retrieval doc ids and excerpt ids for downstream engine consumers.
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

- `Milestone 3: Real workflow loop` because this branch state keeps the engine retrieval path FTS-first, deterministic, and auditable.
- `feat-retrieval-fts - retrieval/search` because this branch state preserves the lane's authoritative retrieval contract.

### Vision capability affected

- `Retrieval-first context handling`
- `Auditable state and workflow`

### Canonical demo-path step advanced

- `retrieve relevant material`
- This branch state makes that step more real by ensuring excerpt lookup only succeeds for authoritative FTS-derived excerpt IDs on the canonical retrieval surface and by preserving a deterministic, auditable FTS-first retrieval contract.
- This packet remains scoped to the retrieval step itself and does not claim basket-promotion changes.

### Routing/provider impact note

- None

## Scope-check / ownership note

- Shared-by-approval edits: `YES`
- Approved shared regression surface: `tests/unit/test_unified_retrieval.py`
- Integrator-locked edits: `NO`
- Packet mirror note: `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` remain read-only in this sandboxed worktree, so this fixer commit updates the writable handoff packet and re-runs gates against the actual branch tip but cannot rewrite those mirror files here.

## Traceability note

- The prior packet refresh already narrowed the canonical demo-path wording to `retrieve relevant material`; this fixer pass refreshes the handoff so it points at the actual current branch tip.
- Re-review should anchor to the branch-tip range `378cf9a74a3658058079a32f186fcd254c4a4034..85d61f4510633e1d4bc74998fcf93308382b6e9c`.
- Treat `c073ad1ffeba08fdc6930b34495d5f8abadf9f16` and `e7958b4656b045844262c3547cae0011446faef1` as reviewed runtime implementation; `85d61f4510633e1d4bc74998fcf93308382b6e9c` is the prior metadata-only packet refresh immediately before this fixer commit.
- Use the final HEAD SHA reported with this fixer handoff for the post-fix branch tip.
