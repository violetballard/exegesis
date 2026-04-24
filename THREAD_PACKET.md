# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `metadata-only reviewer-fix finalization`
- Packet refresh trace anchor before this fixer attempt: `864d87926c820122269090f48052d7af7e4e8729`
- Reviewer packet refresh commit preserved for traceability: `8a545525c6fbaa908a82d249d07c3cbb85cb7add`
- Reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation files: `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- Canonical demo-path step advanced: `retrieve relevant material`
- Plan-alignment statement: this reviewed slice strengthens `retrieve relevant material` by making excerpt lookup resolve only through the authoritative FTS path, which keeps downstream basket and workflow provenance deterministic.
- Reviewer-required canonical demo-path sentence: This work makes the "retrieve relevant material" step of the canonical demo path more real by forcing excerpt lookup to resolve only through the authoritative FTS-backed retrieval path.
- Explicit Milestone 3 mapping: this slice advances `Milestone 3: Real workflow loop` by keeping retrieval/search FTS-first and structured enough for basket promotion.
- Traceability note: re-review this lane against the reviewed implementation range above. Commits after `adfa8cdadd43747ffbcb612e4151e262b13e52ca` are metadata-only packet refreshes unless a later handoff explicitly broadens the reviewed implementation range.

## Scope Goal

- Resubmit the retrieval handoff as a completed AGENTS high-risk packet for the reviewed FTS-only excerpt slice without broadening runtime retrieval scope.

## Scope Completed

- SQLite FTS remains the authoritative MVP retrieval path in the reviewed slice.
- `fetch_excerpt` now resolves through the canonical FTS-only lookup path in `src/qual/retrieval/service.py`.
- Direct `retrieval_doc_bundle()` and `retrieval_excerpt_bundle()` snapshots now surface the authoritative ranked `retrieved_doc_ids` and `retrieved_excerpt_ids` lists without requiring callers to unpack the larger retrieval summary payload first.
- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proves that PageIndex-only excerpt IDs fail closed with `KeyError`.
- PageIndex and embeddings remain compatibility-only paths and are not required MVP runtime paths in this slice.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: resubmit the retrieval handoff as a completed AGENTS high-risk packet for the reviewed FTS-only excerpt slice without broadening runtime retrieval scope.
- Risk reason: approved shared regression coverage in `tests/unit/test_unified_retrieval.py` makes this a shared/high-risk handoff even though the narrowed implementation slice stays within two reviewed files.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Regenerate the canonical kickoff/handoff packet for `feat-retrieval-fts` using the High-Risk template instead of the low-risk shape.
2. State the concrete high-risk reason tied to the approved shared regression file `tests/unit/test_unified_retrieval.py`.
3. Keep the reviewed implementation scope anchored to `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca` and the two reviewed files only.
4. Ensure the canonical packet artifacts agree on the same high-risk budget classification and shared-file ownership note before re-review if the `.codex` packet mirrors are writable.

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

1. Confirmed the lane stayed within retrieval-owned code and identified that the direct doc/excerpt bundle helpers were not surfacing the authoritative ranked `retrieved_*_ids` lists even though the canonical payload contract treats those as first-class promotion metadata.
2. Updated `src/qual/retrieval/service.py` so `retrieval_doc_bundle()` and `retrieval_excerpt_bundle()` now expose `retrieved_doc_ids` and `retrieved_excerpt_ids` directly from the canonical FTS-ranked result.
3. Verified the runtime contract with a direct shell probe of the retrieval service and re-ran `python -m unittest tests.unit.test_unified_retrieval`.
4. Re-ran the required local gates and refreshed the writable handoff artifacts with the real outcomes.

## Files Changed

- `src/qual/retrieval/service.py`
- `THREAD_PACKET.md`
- `docs/gate_passed.txt`

## Commands Run With Results

- `python -m unittest tests.unit.test_unified_retrieval`: `PASS`
- direct retrieval bundle shell probe (`python - <<'PY' ...`): `PASS`
- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Reviewer Fix Closure

1. The handoff is explicitly resubmitted as a completed `Thread Kickoff (High-Risk)` packet.
2. The packet still includes the concrete `Risk reason` tied to the approved shared regression surface in `tests/unit/test_unified_retrieval.py`.
3. The direct doc/excerpt bundle helpers now carry the same ranked retrieval-id ordering metadata that downstream promotion flows already expect from the canonical payload contract.
4. The required local gates have been rerun on the current branch head and are recorded here as passing outcomes.

## Risks / Blockers

- Risk: `HIGH`
- Compatibility risk: direct consumers of `retrieval_doc_bundle()` and `retrieval_excerpt_bundle()` now receive explicit ranked `retrieved_*_ids` fields; this is additive and aligns those bundle snapshots with the canonical downstream payload contract used for basket/context promotion.
- Blockers: none

## Ready For Handoff

- Status: ready for handoff

## Required Handoff Fields

### Roadmap item(s) affected

- `Milestone 3: Real workflow loop`
- `feat-retrieval-fts`: retrieval/search
- `retrieval returns structured results suitable for basket promotion`

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
