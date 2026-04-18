# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `reviewer-required handoff regeneration for the current branch tip`
- Reviewed implementation head: `1d0b5377bff5a5b45845c0f00e7f106eeae6f2ed`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..1d0b5377bff5a5b45845c0f00e7f106eeae6f2ed`
- Packet refresh note: this fixer commit is metadata-only, but it explicitly treats `1d0b5377bff5a5b45845c0f00e7f106eeae6f2ed` as reviewed retrieval/runtime code in scope rather than a metadata-only refresh.

## Scope goal

- Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt and provenance output.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: Keep the FTS-first retrieval lane scoped to deterministic excerpt and provenance output on the canonical engine retrieval surface.
- Risk reason: the reviewed implementation includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Checkpoint Status

- `plan complete`: the packet is reissued against the actual branch-tip implementation range and explicitly names the canonical demo-path step advanced.
- `first green tests`: all required gates were rerun on this fixer pass.
- `before risky/shared file edit`: the only shared implementation file in scope remains the approved regression surface `tests/unit/test_unified_retrieval.py`.
- `ready for handoff`: the handoff stays anchored to the reviewed implementation range above and keeps this final packet-refresh commit separate from that reviewed implementation slice.

## Scope completed

- SQLite FTS remains the authoritative MVP retrieval path in this reviewed slice.
- Public excerpt lookup resolves only through the canonical FTS-backed path in `src/qual/retrieval/service.py`, so PageIndex-only excerpt IDs fail closed instead of silently backfilling from compatibility storage.
- Retrieval payload, provenance, citation, evidence, and basket-promotion snapshots are normalized and copy-safe across `src/qual/retrieval/service.py` and `src/qual/engine/retrieval/payload.py`, including the later branch-tip fixes for excerpt query defaults, query text carriage, stale excerpt-context pruning, and policy-alias preservation in context bundles.
- Retrieval facade exports and engine bundle helpers remain aligned to the FTS-first contract across `src/qual/retrieval/__init__.py` and `src/qual/engine/retrieval/**`, while PageIndex and embeddings stay compatibility-only paths.
- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` exercises the cumulative reviewed slice, including the FTS-only excerpt contract and deterministic downstream payload behavior.

## Canonical Demo-Path Step Advanced

- Canonical demo-path step advanced: `retrieve relevant material`

This handoff explicitly advances the canonical demo-path step `retrieve relevant material`. It does so by keeping public excerpt lookup on the FTS-only retrieval contract and by preserving deterministic, auditable excerpt behavior for downstream basket promotion and workflow use.

## Tasks completed

1. Kept excerpt lookup on the FTS-only contract and tightened sparse excerpt query/provenance normalization so stale or partial excerpt context fails closed instead of rehydrating incorrect runtime state.
2. Canonicalized retrieval payload, provenance, citation, and evidence snapshots in `src/qual/retrieval/service.py` and `src/qual/engine/retrieval/payload.py`, including mirrored hit fields, ranked IDs, policy aliases, and copy-safe normalization.
3. Preserved canonical query text, query context, basket-promotion metadata, and policy aliases through retrieval source/context bundle rehydration and engine-facing exports.
4. Added and expanded approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for deterministic FTS-first retrieval behavior and the fail-closed excerpt lookup contract.

## Reviewed branch-tip commits

- `cf866ba3`: harden excerpt query context defaults
- `95eee546`: carry query text in basket promotion
- `5adbeb7b`: prune stale retrieval excerpt contexts
- `1d0b5377`: preserve policy alias in context bundles

## Files changed

- Runtime files in the reviewed implementation range:
  - `src/qual/engine/retrieval/__init__.py`
  - `src/qual/engine/retrieval/embeddings_strategy.py`
  - `src/qual/engine/retrieval/fts_strategy.py`
  - `src/qual/engine/retrieval/interface.py`
  - `src/qual/engine/retrieval/pageindex_strategy.py`
  - `src/qual/engine/retrieval/payload.py`
  - `src/qual/retrieval/__init__.py`
  - `src/qual/retrieval/service.py`
  - `tests/unit/test_unified_retrieval.py`
- Packet files in the reviewed implementation range:
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

## Reviewer fix closure

1. Expanded the reviewed implementation range and packet contents from the stale `...adfa8cdadd43747ffbcb612e4151e262b13e52ca` slice to the actual reviewed branch-tip slice `378cf9a74a3658058079a32f186fcd254c4a4034..1d0b5377bff5a5b45845c0f00e7f106eeae6f2ed`.
2. Corrected the traceability note so `1d0b5377bff5a5b45845c0f00e7f106eeae6f2ed` is treated as reviewed runtime code, not as a metadata-only packet refresh.
3. Updated `Scope completed`, `Files changed`, and the validation notes to match the real reviewed range.
4. Restated the canonical demo-path step explicitly as `retrieve relevant material`.

## Risks / blockers

- Risk: `HIGH`
- Blockers: none

## Required handoff fields

### Canonical demo-path step advanced

- `retrieve relevant material`

This change makes `retrieve relevant material` more real by keeping public excerpt lookup on the canonical FTS-only path and preserving deterministic, auditable excerpt provenance for downstream basket promotion and workflow use.

### Roadmap item(s) affected

- `Milestone 3: Real workflow loop`
- `feat-retrieval-fts`

### Vision capability affected

- `Retrieval-first context handling`
- `Auditable state and workflow`

### Routing/provider impact note

- None

### Proposed `README.md` patch text

- None

## Scope-check / ownership note

- Shared/integrator-locked edits: `YES`
- Approved shared exception: `tests/unit/test_unified_retrieval.py` is the sole shared-by-approval file in the reviewed implementation range.
