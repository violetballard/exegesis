# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `metadata-only reviewer-fix packet refresh`
- Packet refresh trace anchor before this fixer attempt: `bca26c21e58161f0e3da8fdaf8049ef84771d934`
- Reviewed implementation head: `bca26c21e58161f0e3da8fdaf8049ef84771d934`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..bca26c21e58161f0e3da8fdaf8049ef84771d934`
- Reviewed implementation files: `.codex/kickoff_packets/feat-retrieval-fts.md`, `.codex/lane_meta/feat-retrieval-fts.json`, `docs/gate_passed.txt`, `src/qual/engine/retrieval/__init__.py`, `src/qual/engine/retrieval/embeddings_strategy.py`, `src/qual/engine/retrieval/fts_strategy.py`, `src/qual/engine/retrieval/interface.py`, `src/qual/engine/retrieval/pageindex_strategy.py`, `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/__init__.py`, `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- Canonical demo-path step advanced: `retrieve relevant material`
- Plan-alignment statement: this reviewed slice strengthens `retrieve relevant material` by keeping the MVP explicitly FTS-first, making retrieval payloads and provenance deterministic for downstream engine flows, and preserving ranked retrieval ids on the narrowed bundles used for later basket/context promotion.
- Reviewer-required canonical demo-path sentence: This work makes the "retrieve relevant material" step of the canonical demo path more real by keeping retrieval/search FTS-first end to end and forcing excerpt resolution through the authoritative FTS-backed retrieval path.
- Explicit Milestone 3 mapping: this slice advances `Milestone 3: Real workflow loop` by shipping an FTS-first retrieval path with deterministic payload/provenance surfaces and fail-closed compatibility shims for non-FTS excerpt lookup inputs.
- FTS-first confirmation: the actual reviewed branch tip remains FTS-first for the MVP; SQLite FTS is authoritative, while PageIndex and embeddings remain compatibility-only fallback shims that fail closed when the canonical FTS path is not available.
- Traceability note: re-review this lane against the reviewed implementation range above. This fixer pass is metadata-only; the reviewed implementation head remains `bca26c21e58161f0e3da8fdaf8049ef84771d934` unless a later handoff explicitly broadens the reviewed implementation range.

## Scope Goal

- Resubmit the retrieval handoff against the actual branch tip so the reviewed slice, files changed, completed tasks, and gate evidence all match the real FTS-first retrieval implementation under review.

## Scope Completed

- SQLite FTS remains the authoritative MVP retrieval path in the reviewed slice.
- The canonical retrieval query constructor and `retrieve_auto` helper are exported through both retrieval facades.
- Retrieval payloads, provenance snapshots, sparse source/context bundles, and strategy hit snapshots are deterministic for downstream engine flows.
- `fetch_excerpt` resolves through the canonical FTS-only lookup path, and the shared regression coverage proves PageIndex-only excerpt ids fail closed with `KeyError`.
- Ranked document ids and excerpt ids are preserved directly on the narrower retrieval bundles so downstream consumers do not need to unpack larger summary payloads just to preserve authoritative FTS ordering.
- Engine retrieval runtime types are lazy-bound so the engine retrieval facade can expose the canonical retrieval helpers without widening import-time runtime coupling.
- PageIndex and embeddings remain compatibility-only paths and are not required MVP runtime paths in this reviewed slice.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: resubmit the retrieval handoff against the real branch-tip implementation and confirm the full reviewed slice still satisfies the FTS-first MVP contract.
- Risk reason: the lane includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, and the truthful reviewed slice spans retrieval facade, engine retrieval export, payload, and test surfaces rather than a two-file narrowed excerpt patch.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Regenerate the packet surfaces against the actual branch tip `bca26c21e58161f0e3da8fdaf8049ef84771d934` instead of the stale `..adfa8c` reviewed range.
2. Update `Scope completed`, `Tasks completed`, `Files changed`, and `Commands run with results` so they match the real reviewed slice and its runtime retrieval changes.
3. Restate the canonical demo-path step as `retrieve relevant material` and explicitly confirm the branch tip remains FTS-first for MVP review.
4. Re-run the required local gates on the refreshed metadata-only handoff commit.

### Early Review Triggers

- before first edit to any shared/integrator-locked file
- before changing public interfaces or command contracts
- before touching provider routing/config behavior

### Stop Triggers

- unresolved test/lint/typecheck after 2 attempts
- unresolved `make scope-check`
- budget/size/time limit hit

### Checkpoint Cadence (short updates)

- plan complete
- first green tests
- before risky/shared file edit
- ready for handoff

### Handoff Packet

- branch name
- tasks completed (numbered)
- files changed
- commands run + outcomes
- risks/blockers
- all required fields from `INTEGRATION.md`

## Tasks Completed

1. Kept retrieval/search FTS-first across the reviewed slice by exporting the canonical query builder and `retrieve_auto` helper through both retrieval facades while leaving PageIndex and embeddings as fail-closed compatibility shims.
2. Hardened deterministic retrieval payloads, provenance snapshots, sparse source/context bundles, and audit-aligned hit metadata for downstream engine flows.
3. Removed the noncanonical excerpt fallback path so excerpt lookup resolves only through the authoritative FTS path, then added approved shared regression coverage proving PageIndex-only excerpt ids fail closed.
4. Extended the reviewed tip with the remaining runtime follow-ups: lazy-bound engine retrieval runtime typing and direct `retrieved_doc_ids` / `retrieved_excerpt_ids` exposure on narrowed retrieval bundles.

## Files Changed

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `docs/gate_passed.txt`
- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/embeddings_strategy.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/interface.py`
- `src/qual/engine/retrieval/pageindex_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/__init__.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`
- `THREAD_PACKET.md`

## Commands Run With Results

- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Reviewer Fix Closure

1. The packet is regenerated against the actual reviewed implementation head `bca26c21e58161f0e3da8fdaf8049ef84771d934`, and the reviewed implementation range now includes every non-metadata commit after `378cf9a74a3658058079a32f186fcd254c4a4034`.
2. `Scope completed`, `Tasks completed`, `Files changed`, and the gate table now describe the real reviewed slice, including the later runtime edits in `src/qual/engine/retrieval/__init__.py` and `src/qual/retrieval/service.py`.
3. The handoff explicitly states that this work advances the canonical demo-path step `retrieve relevant material`.
4. The packet explicitly reconfirms that the actual branch tip remains FTS-first for the MVP under the `feat-retrieval-fts` lane gate.

## Risks / Blockers

- Risk: `HIGH`
- Compatibility risk: downstream callers that still pass PageIndex-only excerpt ids to `RetrievalService.fetch_excerpt` now fail closed with `KeyError`, so consumers must preserve canonical FTS excerpt ids from the authoritative retrieval path.
- Blockers: none

## Ready For Handoff

- Status: ready for handoff

## Required Handoff Fields

### Roadmap item(s) affected

- `Milestone 3: Real workflow loop`
- `feat-retrieval-fts`: retrieval/search

### Vision capability affected

- `Retrieval-first context handling`
- `Auditable state and workflow`

### Routing/provider impact note

- None

### Proposed `README.md` patch text

- None

## Scope-Check / Ownership Note

- Shared or integrator-locked edits: `YES`
- Approved shared regression coverage remains limited to `tests/unit/test_unified_retrieval.py`.
