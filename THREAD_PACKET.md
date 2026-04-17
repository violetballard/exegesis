# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet refresh role: `feature-fixer reviewer handoff regeneration`
- Pre-fixer implementation trace anchor: `d264cf25c9101798ea784b3b38bf516a89c5890a`
- Reviewed implementation range for re-review: `adfa8cdadd43747ffbcb612e4151e262b13e52ca..(final fixer HEAD SHA reported with this handoff)`

## Scope goal

- Keep FTS-first retrieval authoritative while carrying deterministic provenance, retrieval policy, and basket-promotion evidence through the canonical downstream payload surfaces used by the engine loop.

## Scope completed

- The branch tip now preserves deterministic retrieval evidence across the FTS-first retrieval surfaces in `src/qual/retrieval/**` and `src/qual/engine/retrieval/**`, including doc-scope provenance tightening, excerpt lookup fingerprinting, basket-promotion backfill, retrieval-policy propagation, and normalized retrieval-evidence date ranges.
- `fetch_excerpt` remains FTS-only; PageIndex and embeddings stay deferred compatibility identifiers rather than required runtime paths.
- This fixer pass removes the out-of-lane `src/qual/engine/tools/excerpt_tools.py` retrieval change and the shared regression that depended on it, so the branch no longer asks the reviewer to accept that ownership violation.

## Canonical Demo-Path Step Advanced

- `promote or gather context into the basket`
- The true branch-tip work is no longer just an excerpt lookup slice. It advances basket gathering/promotion by preserving retrieval policy, provenance, and normalized evidence fields when FTS results are promoted into downstream payloads, which keeps the Milestone 3 engine loop auditable after retrieval results move into basket-facing workflow state.

## AGENTS.md handoff packet

- Risk reason: shared/high-risk work because the cumulative branch-tip slice still edits the approved shared regression surface `tests/unit/test_unified_retrieval.py`.
- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`
- Budget status:
  - Task cap met at `4` grouped tasks.
  - Size cap exceeded on the true implementation slice: `9` implementation files changed with `4558` insertions and `437` deletions.
  - Including packet metadata, the full branch-tip delta for this re-review is `12` files changed with `4794` insertions and `515` deletions.
- Tasks completed:
  1. Hardened FTS-first retrieval metadata in the canonical owned surfaces, including doc-scope provenance, excerpt lookup fingerprints, confidentiality-aware excerpt lookup metadata, and deterministic hit/provenance snapshots.
  2. Stabilized downstream retrieval payload backfill so basket-promotion, citation, source-bundle, and evidence payloads keep canonical FTS policy/provenance fields instead of degrading on sparse inputs.
  3. Normalized query, scope, constraint, strategy-id, and date-range handling for cache keys and payload snapshots so equivalent retrieval inputs produce deterministic downstream evidence.
  4. Kept shared regression coverage in `tests/unit/test_unified_retrieval.py` aligned with the canonical retrieval contract, and removed the extra out-of-lane `excerpt_tools` regression/assertion in this fixer pass.

## Files changed

### Implementation files

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

### Out-of-lane cleanup in this fixer pass

- `src/qual/engine/tools/excerpt_tools.py` was restored to its pre-lane behavior and is no longer part of the reviewed retrieval implementation surface.

## Commands run with results

- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Risks / blockers

- Risk: `HIGH`
- Merge risk detail: the branch is still a shared/high-risk retrieval slice and remains over the AGENTS size cap even after removing the out-of-lane helper edit, because the canonical retrieval payload and regression surfaces changed substantially before this fixer pass.
- Blockers: none

## Required handoff fields

### Roadmap item(s) affected

- `Milestone 3: Real workflow loop`
- `feat-retrieval-fts - retrieval/search`

### Vision capability affected

- `Retrieval-first context handling`
- `Auditable state and workflow`

### Routing/provider impact note

- None

## Scope-check / ownership note

- Shared-by-approval edits: `YES`
- Approved shared regression surface: `tests/unit/test_unified_retrieval.py`
- Out-of-lane edit removed in fixer pass: `src/qual/engine/tools/excerpt_tools.py`
- Integrator-locked edits: `NO`

## Traceability note

- This packet replaces the stale narrowed handoff that incorrectly described the branch tip as metadata-only after `adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
- Because this packet is itself part of the fixer commit, it records the pre-fixer trace anchor `d264cf25c9101798ea784b3b38bf516a89c5890a`; use the final HEAD SHA reported with this fixer handoff as the actual branch tip for re-review.
