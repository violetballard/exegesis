# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `reviewer-fix packet regeneration`
- Current branch tip before this fixer pass: `e398c81caafee19dd55b6b62f9bc57615b0b05c8`
- Reviewed implementation head: `e398c81caafee19dd55b6b62f9bc57615b0b05c8`
- Reviewed implementation range: `d7fd5d200358287fa42a18d39e2b277463b9b69f..e398c81caafee19dd55b6b62f9bc57615b0b05c8`
- Packet-only descendant above the reviewed implementation head: this fixer commit updates handoff metadata only; final HEAD SHA is reported in the fixer handoff.
- Packet traceability note: the reviewed implementation range now includes every non-metadata descendant on this branch through `e398c81caafee19dd55b6b62f9bc57615b0b05c8`, so the post-fix branch tip is truthfully metadata-only above the reviewed retrieval implementation head.

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
4. Regenerate the handoff packet so the reviewed range, files changed, and canonical demo-path mapping match the real reviewed implementation head.

### Checkpoint Status

- `plan complete`: the reviewed implementation scope is restated against the true runtime branch tip before this fixer pass.
- `first green tests`: recorded after rerunning the required local gates for this fixer pass.
- `before risky/shared file edit`: the only shared implementation file in the reviewed scope remains `tests/unit/test_unified_retrieval.py`.
- `ready for handoff`: this packet now states the exact reviewed implementation range, the exact cumulative file set, and the explicit canonical demo-path step advanced.

## Scope completed

- The reviewed implementation range keeps SQLite FTS authoritative across the retrieval facade and excerpt lookup surface.
- Retrieval hits, provenance bundles, citation/source/context payloads, and sparse bundle rehydration remain deterministic and auditable for downstream engine flows.
- The later reviewed tip commit `e398c81caafee19dd55b6b62f9bc57615b0b05c8` updates `src/qual/retrieval/service.py` to carry canonical query constraints and lookup context into excerpt lookup audit records and payloads, which remains in scope because it strengthens auditable FTS-first retrieval behavior rather than adding a new retrieval mode.
- `fetch_excerpt()` now fails closed for non-FTS excerpt IDs, approved shared regression coverage proves PageIndex-only excerpt IDs raise `KeyError`, and PageIndex plus embeddings remain compatibility-only shims rather than required MVP paths.

## Canonical Demo-Path Step Advanced

- `retrieve relevant material`

This handoff advances `retrieve relevant material` by keeping the canonical engine retrieval surface FTS-first, deterministic, and auditable from query normalization through excerpt lookup payloads. Some reviewed changes also preserve retrieval context that downstream basket promotion can consume, but the primary demo-path step advanced by this lane remains `retrieve relevant material`.

## Tasks completed

1. Kept SQLite FTS authoritative across retrieval entrypoints, excerpt lookup, and hit strategy enforcement.
2. Stabilized retrieval payload, provenance, citation, source, and context bundles so downstream engine consumers get deterministic snapshots and sparse rehydration.
3. Expanded the canonical retrieval facade to normalize public query constraints and carry query context through excerpt lookup and basket-promotion-adjacent payloads without promoting PageIndex or embeddings to required runtime paths.
4. Kept approved shared regression coverage in `tests/unit/test_unified_retrieval.py` and aligned packet-planner tooling/tests so review packets can represent the reviewed implementation range accurately.

## Files changed

- Reviewed implementation files in `d7fd5d200358287fa42a18d39e2b277463b9b69f..e398c81caafee19dd55b6b62f9bc57615b0b05c8`:
  - `codex_packet_handoff/tools/planner.py`
  - `src/qual/engine/retrieval/__init__.py`
  - `src/qual/engine/retrieval/embeddings_strategy.py`
  - `src/qual/engine/retrieval/fts_strategy.py`
  - `src/qual/engine/retrieval/interface.py`
  - `src/qual/engine/retrieval/pageindex_strategy.py`
  - `src/qual/engine/retrieval/payload.py`
  - `src/qual/retrieval/__init__.py`
  - `src/qual/retrieval/service.py`
  - `tests/unit/test_packet_planner.py`
  - `tests/unit/test_unified_retrieval.py`
- Packet-only fixer commit files:
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

1. The reviewed implementation range now matches the actual branch-tip ancestry through `e398c81caafee19dd55b6b62f9bc57615b0b05c8` instead of stopping at stale commit `adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
2. The `Files changed` section now distinguishes the exact cumulative reviewed implementation file set from the metadata-only fixer commit file set.
3. The packet now includes an explicit `Canonical Demo-Path Step Advanced` field with the scope-tightened value `retrieve relevant material`.
4. The packet keeps scope tight to the FTS-first retrieval MVP while honestly disclosing later reviewed descendants that touched retrieval query constraints and packet-planner support.

## Risks / blockers

- Risk: `HIGH`
- Residual risk: the reviewed implementation range is cumulative and significantly exceeds the nominal high-risk size budget, so integration risk remains higher than the narrowed `adfa8c...` slice even though the lane scope stays retrieval-focused.
- Residual risk: compatibility-only callers that still hold PageIndex-generated excerpt IDs will now receive `KeyError` from canonical excerpt lookup surfaces instead of PageIndex-backed payloads.
- Blockers: none

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
