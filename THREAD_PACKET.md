# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet refresh role: `metadata-only reviewer re-review regeneration`
- Packet refresh trace anchor before this commit: `8339c6552ed833b7878ac600e946df54ef29bc0c`
- Reviewed implementation head: `8339c6552ed833b7878ac600e946df54ef29bc0c`
- Reviewed implementation range for re-review: `d7fd5d200358287fa42a18d39e2b277463b9b69f..8339c6552ed833b7878ac600e946df54ef29bc0c`

## Scope goal

- Remove the `fetch_excerpt` PageIndex fallback so the canonical retrieval surface fails closed on non-FTS excerpt IDs and keeps excerpt resolution on the authoritative FTS-only path.

## Scope completed

- This reviewed slice keeps SQLite FTS authoritative by removing the `fetch_excerpt` PageIndex fallback from the canonical retrieval service in `src/qual/retrieval/service.py`.
- The change makes non-FTS excerpt IDs fail closed with `KeyError` instead of silently resolving through PageIndex, keeping excerpt lookup deterministic and auditable on the canonical retrieval path.
- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` validates that `fetch_excerpt` now accepts only FTS-backed excerpt IDs and rejects PageIndex-only IDs.

## Canonical Demo-Path Step Advanced

- `retrieve relevant material`
- This slice makes the retrieval step more real by keeping canonical excerpt resolution deterministic and auditable as soon as FTS results are produced, which is the contract downstream basket promotion depends on.

## Reviewer Fixes Addressed

- Added the explicit canonical demo-path step the reviewer requested.
- Kept that statement tightly scoped to this reviewed slice: deterministic, FTS-only excerpt lookup on the canonical engine path.
- Regenerated the writable canonical handoff packet in `THREAD_PACKET.md`; the `.codex` packet mirrors remain read-only in this lane worktree and are documented under risks.

## AGENTS.md handoff packet

- Risk reason: shared/high-risk work because the reviewed implementation range still edits the approved shared regression surface `tests/unit/test_unified_retrieval.py`.
- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`
- Budget status:
  - Task cap met at `4` grouped tasks.
  - Size cap exceeded on the true implementation slice: `9` implementation files changed with `6119` insertions and `478` deletions.
  - Including this packet-refresh commit, the full handoff state touches `12` files: `9` implementation files plus `3` packet files.
- Tasks completed:
  1. Hardened canonical FTS retrieval metadata, query normalization, and excerpt lookup payloads so deterministic provenance and policy fields survive the reviewed retrieval path.
  2. Stabilized downstream retrieval payload backfill so sparse source, citation, provenance, excerpt, and basket-promotion snapshots rehydrate to the same canonical FTS-first contract.
  3. Preserved FTS-first behavior while tightening cache/input normalization, context propagation, basket-promotion metadata, and source-bundle fingerprints without promoting PageIndex or embeddings to required runtime paths.
  4. Kept the approved shared regression surface `tests/unit/test_unified_retrieval.py` aligned with the corrected cumulative retrieval contract.

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

### Packet / handoff files

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`

## Commands run with results

- Validation rerun date: `2026-04-16`
- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Risks / blockers

- Risk: `HIGH`
- Merge risk detail: the reviewed implementation slice remains shared/high-risk and well over the AGENTS size cap because the canonical retrieval payload and regression surfaces changed substantially after the original `adfa8cda` review point.
- Blockers: none
- Packet mirror note: `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` are read-only in this sandboxed lane worktree, so this fixer pass updates the canonical `THREAD_PACKET.md` handoff record only.

## Required handoff fields

### Canonical demo-path step advanced

- `retrieve relevant material`
- This handoff makes the retrieval step more real by keeping the engine-facing excerpt lookup and retrieval payloads on the canonical FTS-only path with deterministic, auditable metadata for downstream basket and workflow use.


### Roadmap item(s) affected

- `Milestone 3: Real workflow loop` because this slice hardens the FTS-first retrieval contract used by the engine loop.
- `feat-retrieval-fts - retrieval/search` because this slice removes the non-canonical PageIndex fallback from excerpt lookup.

### Vision capability affected

- `Retrieval-first context handling` because this slice keeps excerpt lookup on the authoritative FTS path used to gather context.
- `Auditable state and workflow` because this slice makes excerpt provenance fail closed instead of resolving through a non-canonical fallback.

### Routing/provider impact note

- None

## Scope-check / ownership note

- Shared-by-approval edits: `YES`
- Approved shared regression surface: `tests/unit/test_unified_retrieval.py`
- Integrator-locked edits: `NO`

## Traceability note

- This packet supersedes the stale narrowed handoff that stopped at `adfa8cdadd43747ffbcb612e4151e262b13e52ca` even though later branch commits changed retrieval runtime code.
- Re-review should evaluate the true cumulative implementation slice `d7fd5d200358287fa42a18d39e2b277463b9b69f..8339c6552ed833b7878ac600e946df54ef29bc0c`, then treat this packet-refresh commit as metadata-only on top of that implementation head.
- Because this packet commit is itself metadata-only, it does not self-record its own final SHA inside the packet. Use the final HEAD SHA reported with this handoff as the packet-refresh branch tip.
