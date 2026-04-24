# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `metadata-only reviewer-fix scope alignment`
- Current submitted tip before this packet refresh commit: `7baf6c00c87f89ef8b80e60b167e03d4eb3f2b88`
- Reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Packet traceability note: review this lane against the narrowed implementation range above. The current packet refresh commit is metadata-only and does not broaden retrieval scope beyond `378cf9a7..adfa8cda`.
- Canonical demo-path step advanced: `retrieve relevant material`
- Reviewer-required plan-alignment statement: This work advances `retrieve relevant material` by making the public excerpt lookup surface resolve through the authoritative SQLite FTS path, so PageIndex-only excerpt IDs fail closed under shared regression coverage. That is the reviewed slice's direct contribution to Milestone 3's FTS-first structured retrieval requirement.
- Evidence note: `tests/unit/test_unified_retrieval.py` covers both the narrowed service-level contract and the public retrieval facade for this slice. `test_retrieval_service_rejects_pageindex_excerpt_payloads` proves PageIndex-only excerpt IDs fail closed on `fetch_excerpt(...)`, and `test_retrieve_fts_excerpt_returns_canonical_fts_payload` proves the canonical/public FTS excerpt helpers return the same payload shape.
- Packet authority note: this top-level packet and `docs/gate_passed.txt` are the reviewer-facing source of truth for the explicit demo-path mapping, high-risk/shared classification, and narrowed scope wording on this branch.

## Scope Goal

- Regenerate the retrieval-specific handoff packet so it stays narrowed to reviewed range `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`, states explicitly that this work advances `retrieve relevant material`, and reports the metadata-only refresh files from this packet slice accurately.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: correct the reviewer packet against the reviewed range `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca` without widening the lane beyond the approved FTS-only excerpt fail-closed slice.
- Risk reason: this handoff includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, so it is shared/high-risk work under the 4-task cap.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Keep the handoff anchored to reviewed implementation head `adfa8cda` and reviewed range `378cf9a7..adfa8cda`.
2. State the canonical demo-path step explicitly as `retrieve relevant material`.
3. Reconcile the packet file lists and metadata-only traceability so they match this packet-refresh slice, including `docs/gate_passed.txt`.
4. Re-run the required gates and record results against the narrowed reviewed implementation head/range.

### Checkpoint Status

- `plan complete`: the packet is anchored to the reviewer-approved retrieval implementation range `378cf9a7..adfa8cda`.
- `first green tests`: recorded after rerunning `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.
- `before risky/shared file edit`: this handoff includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- `ready for handoff`: the kickoff packet, lane metadata, top-level packet, and gate summary agree on the same reviewed implementation head, reviewed range, risk class, reviewed files, and metadata-only refresh files.

## Scope Completed

- Removed the PageIndex fallback from `fetch_excerpt`, so the public excerpt lookup surface now resolves through the canonical FTS-only path.
- Added regression coverage proving PageIndex-only excerpt IDs now raise `KeyError` instead of silently backfilling through PageIndex.
- Kept the reviewed evidence intentionally narrow to the FTS-only excerpt lookup contract and its fail-closed regression coverage rather than broader retrieval or provenance claims.
- This handoff explicitly states that the reviewed slice advances the canonical demo-path step `retrieve relevant material`, which is the Milestone 3 FTS-first structured retrieval requirement this slice makes more real.

## Reviewed Scope Boundary

- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation files:
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`
- Current metadata-only handoff files in this packet refresh:
- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`
- `docs/gate_passed.txt`

## Tasks Completed

1. Kept `fetch_excerpt` on the canonical FTS-only lookup path so PageIndex-only excerpt IDs fail closed.
2. Added regression tests proving non-FTS excerpt IDs now raise `KeyError` and the public FTS excerpt helper still returns the canonical payload.
3. Kept the reviewed scope anchored to commit `adfa8cdadd43747ffbcb612e4151e262b13e52ca` and range `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
4. Re-emitted retrieval-specific handoff artifacts so the completed packet is no longer stale or lane-mismatched.

## Files Changed

- Reviewed implementation files in `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`:
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`
- Current metadata-only packet refresh files:
- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`
- `docs/gate_passed.txt`

## Commands Run With Results

- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Reviewer Fix Closure

1. The handoff now names the canonical demo-path step directly as `retrieve relevant material`.
2. The plan-alignment statement explains that this step becomes more real because excerpt lookup stays on the auditable SQLite FTS path and PageIndex-only excerpt IDs fail closed within the reviewed `378cf9a7..adfa8cda` slice.
3. The scope-completed text is narrowed to the reviewed slice: removal of the PageIndex fallback from `fetch_excerpt` and regression coverage proving non-FTS excerpt IDs now raise `KeyError`.
4. The handoff remains classified as shared/high-risk work because the reviewed slice includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
5. This fixer pass reran the required local gate suite on a metadata-only packet refresh without changing the reviewed implementation range.

## Risks / Blockers

- Risk: `HIGH`
- Blockers: none

## Required Handoff Fields

### Roadmap item(s) affected

- `Milestone 3: Product Readiness` via the `retrieve relevant material` step's deterministic FTS-first excerpt-query contract
- `feat-retrieval-fts` FTS-only excerpt fail-closed slice

### Canonical demo-path step advanced

- `retrieve relevant material`
- Deterministic FTS-only excerpt lookup keeps the demo path auditable, fail-closed, and aligned with Milestone 3's FTS-first structured retrieval requirement.

### Vision capability affected

- `2. Retrieval-first context handling`
- `3. Auditable generation`

### Routing/provider impact note

- None

### Proposed `README.md` patch text

- None

## Scope-Check / Ownership Note

- Shared or integrator-locked edits: `YES`
- Approved shared regression coverage remains limited to `tests/unit/test_unified_retrieval.py`.
