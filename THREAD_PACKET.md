# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `metadata-only reviewer-fix finalization`
- Current branch tip before this fixer pass: `2dd617613923b6d1a61e9ab9ce7cbd996b84ae18`
- Reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation range: `d7fd5d200358287fa42a18d39e2b277463b9b69f..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Packet-only descendant above the reviewed implementation head: this fixer commit updates handoff metadata only; final HEAD SHA is reported in the fixer handoff.
- Packet traceability note: later metadata-only packet refresh commits may advance the branch tip, but they do not move the reviewed retrieval implementation head or reviewed implementation range unless this packet is explicitly regenerated to do so.

## Scope goal

- Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt and provenance output.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: keep retrieval/search FTS-first, deterministic, and auditable on the canonical engine surface.
- Risk reason: the reviewed cumulative range includes the approved shared regression surface `tests/unit/test_unified_retrieval.py`.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Keep SQLite FTS authoritative for retrieval and excerpt lookup.
2. Preserve deterministic payload, provenance, and bundle snapshots for downstream engine flows.
3. Carry canonical query constraints and lookup context through the retrieval facade without reopening PageIndex or embeddings as required paths.
4. Re-emit the handoff packet so the kickoff file, lane metadata, and review packet all describe the same high-risk/shared FTS-only reviewed implementation slice.

### Checkpoint Status

- `plan complete`: the reviewed implementation scope is restated against the packet-refresh branch tip before this fixer pass.
- `first green tests`: recorded after rerunning the required local gates for this fixer pass.
- `before risky/shared file edit`: the only shared implementation file in the reviewed scope remains `tests/unit/test_unified_retrieval.py`.
- `ready for handoff`: this packet now states the exact reviewed implementation range, the exact cumulative file set, and the explicit FTS-only excerpt contract.

## Scope completed

- The reviewed implementation range keeps SQLite FTS authoritative across the retrieval facade and excerpt lookup surface.
- Retrieval hits, provenance bundles, citation/source/context payloads, and sparse bundle rehydration remain deterministic and auditable for downstream engine flows.
- Public retrieval helpers accept normalized constraint inputs and preserve canonical query/constraint context through excerpt lookup and basket-promotion-adjacent payloads.
- `fetch_excerpt()` now fails closed for non-FTS excerpt IDs, approved shared regression coverage proves PageIndex-only excerpt IDs raise `KeyError`, and PageIndex plus embeddings remain compatibility-only shims rather than fallback excerpt paths.

## Canonical Demo-Path Step Advanced

- `retrieve relevant material`

This handoff advances `retrieve relevant material` by keeping the canonical engine retrieval surface FTS-first, deterministic, and auditable from query normalization through excerpt lookup payloads.

## Tasks completed

1. Kept SQLite FTS authoritative across retrieval entrypoints, excerpt lookup, and hit strategy enforcement.
2. Stabilized retrieval payload, provenance, citation, source, and context bundles so downstream engine consumers get deterministic snapshots and sparse rehydration.
3. Expanded the canonical retrieval facade to normalize public query constraints and carry query context through excerpt lookup and basket-promotion-adjacent payloads without promoting PageIndex or embeddings to required runtime paths.
4. Re-emitted the packet metadata so the kickoff file, lane meta, and thread handoff all consistently classify the shared test edit as high-risk work under the 4-task cap and describe the reviewed contract as FTS-only for `fetch_excerpt()`.

## Files changed

- Reviewed implementation files in `d7fd5d200358287fa42a18d39e2b277463b9b69f..adfa8cdadd43747ffbcb612e4151e262b13e52ca`:
  - `src/qual/engine/retrieval/__init__.py`
  - `src/qual/engine/retrieval/embeddings_strategy.py`
  - `src/qual/engine/retrieval/fts_strategy.py`
  - `src/qual/engine/retrieval/interface.py`
  - `src/qual/engine/retrieval/pageindex_strategy.py`
  - `src/qual/engine/retrieval/payload.py`
  - `src/qual/retrieval/__init__.py`
  - `src/qual/retrieval/service.py`
  - `tests/unit/test_unified_retrieval.py`
- Packet-only fixer commit files:
  - `THREAD_PACKET.md`

## Commands run with results

- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Reviewer fix closure

1. The handoff is explicitly classified as shared/high-risk work because `tests/unit/test_unified_retrieval.py` is the approved shared regression surface, so the 4-task cap applies consistently across the packet set.
2. The reviewed contract wording is tightened to match the implementation: `fetch_excerpt()` is FTS-only and does not retain a PageIndex fallback path.
3. The thread packet is re-emitted against the same reviewed implementation head and range already recorded in the kickoff packet and lane metadata, so re-review has one consistent source of truth.

## Risks / blockers

- Risk: `HIGH`
- Residual risk: compatibility-only callers that still hold PageIndex-generated excerpt IDs will now receive `KeyError` from canonical excerpt lookup surfaces instead of PageIndex-backed payloads.
- Blockers: `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` are readable but not writable in this sandbox, so their trace-anchor strings could not be refreshed during this pass.

## Required handoff fields

### Roadmap item(s) affected

- `Milestone 3: Real workflow loop`
- `feat-retrieval-fts`

### Canonical demo-path step advanced

- `retrieve relevant material`

### Vision capability affected

- `2. Retrieval-first context handling`
- `6. Auditable state and workflow`

### Routing/provider impact note

- None

### Proposed `README.md` patch text

- None

## Scope-check / ownership note

- Shared/integrator-locked edits in the reviewed implementation range: `YES`
- Approved shared exception: `tests/unit/test_unified_retrieval.py` is the sole shared-by-approval implementation file in the reviewed retrieval scope.
- Packet-only fixer files are handoff metadata files and do not change reviewed retrieval runtime behavior.
