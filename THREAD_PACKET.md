# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `metadata-only reviewer-fix re-emit`
- Current submitted tip before this packet refresh commit: `0beefa6afaf0634b279a394653b4b99e02144031`
- Reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation range: `d7fd5d200358287fa42a18d39e2b277463b9b69f..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Packet traceability note: review this lane against the narrowed implementation range above. The current packet refresh commit is metadata-only and does not broaden retrieval scope beyond `d7fd5d20..adfa8cda`.
- Canonical demo-path step advanced: `retrieve relevant material` via the FTS-first engine surface with fail-closed excerpt lookup and auditable provenance.
- Reviewer-required plan-alignment statement: This work advances `retrieve relevant material` by making the public excerpt lookup surface resolve through the authoritative SQLite FTS path, so PageIndex-only excerpt IDs fail closed under shared regression coverage and basket-promotion inputs stay deterministic.
- Evidence note: `tests/unit/test_unified_retrieval.py` covers both the narrowed service-level contract and the public retrieval facade for this slice. `test_retrieval_service_rejects_pageindex_excerpt_payloads` proves PageIndex-only excerpt IDs fail closed on `fetch_excerpt(...)`, and `test_retrieve_fts_excerpt_returns_canonical_fts_payload` proves the canonical/public FTS excerpt helpers return the same payload shape.
- Packet authority note: this top-level packet and `docs/gate_passed.txt` are the reviewer-facing source of truth for the explicit demo-path mapping and plan-alignment wording on this branch.

## Scope Goal

- Regenerate the retrieval-specific handoff packet so it stays narrowed to reviewed commit `adfa8cdadd43747ffbcb612e4151e262b13e52ca`, states explicitly that this work advances `retrieve relevant material`, and reports the metadata-only refresh files from this packet slice accurately.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: correct the reviewer packet against the reviewed retrieval implementation head `adfa8cdadd43747ffbcb612e4151e262b13e52ca` without widening the lane beyond the approved FTS-only excerpt fail-closed slice.
- Risk reason: this handoff includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, so it is shared/high-risk work under the 4-task cap.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Keep the handoff anchored to reviewed implementation head `adfa8cda` and reviewed range `d7fd5d20..adfa8cda`.
2. State the canonical demo-path step explicitly as `retrieve relevant material`.
3. Reconcile the packet file lists and metadata-only traceability so they match this packet-refresh slice, including `docs/gate_passed.txt`.
4. Re-run the required gates and record results against the narrowed reviewed implementation head/range.

### Checkpoint Status

- `plan complete`: the packet is anchored to the reviewer-approved retrieval implementation range `d7fd5d20..adfa8cda`.
- `first green tests`: recorded after rerunning `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.
- `before risky/shared file edit`: this handoff includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- `ready for handoff`: the kickoff packet, lane metadata, top-level packet, and gate summary agree on the same reviewed implementation head, reviewed range, risk class, reviewed files, and metadata-only refresh files.

## Scope Completed

- SQLite FTS remains the authoritative retrieval path for the reviewed implementation range.
- The public excerpt lookup surface resolves through the canonical FTS path, so PageIndex-only excerpt IDs fail closed with no PageIndex runtime fallback on that surface.
- The reviewed evidence is intentionally narrow: it hardens the excerpt lookup contract and its public FTS helper surface rather than re-proving every broader lane claim.
- This handoff explicitly states that the reviewed slice advances the canonical demo-path step `retrieve relevant material`.

## Reviewed Scope Boundary

- Reviewed implementation range: `d7fd5d200358287fa42a18d39e2b277463b9b69f..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
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
2. Kept the reviewed scope anchored to commit `adfa8cdadd43747ffbcb612e4151e262b13e52ca` and range `d7fd5d200358287fa42a18d39e2b277463b9b69f..adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
3. Re-emitted retrieval-specific handoff artifacts so the completed packet is no longer stale or lane-mismatched.
4. Regenerated the metadata-only file lists so this packet-refresh slice discloses `.codex/kickoff_packets/feat-retrieval-fts.md`, `.codex/lane_meta/feat-retrieval-fts.json`, `THREAD_PACKET.md`, and `docs/gate_passed.txt`.

## Files Changed

- Reviewed implementation files in `d7fd5d200358287fa42a18d39e2b277463b9b69f..adfa8cdadd43747ffbcb612e4151e262b13e52ca`:
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

1. The packet stays narrowed to reviewed implementation head `adfa8cdadd43747ffbcb612e4151e262b13e52ca` and reviewed range `d7fd5d200358287fa42a18d39e2b277463b9b69f..adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
2. The handoff explicitly states that this work advances the canonical demo-path step `retrieve relevant material`.
3. The handoff is classified consistently as shared/high-risk work because the reviewed slice includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
4. The completed packet is retrieval-specific and branch-local instead of lane-stale.
5. The reviewed file list, metadata-only file list, and gate summary all match the narrowed reviewed implementation range and current packet-refresh contents.
6. The reviewer-facing truth sources are explicitly identified so re-review reads the demo-path mapping from this packet and `docs/gate_passed.txt`.

## Risks / Blockers

- Remaining risks: none identified in the reviewed slice beyond normal merge risk on a metadata-only packet refresh. Re-review should continue to anchor retrieval scope to `adfa8cdadd43747ffbcb612e4151e262b13e52ca` so later packet-refresh commits are not mistaken for new retrieval implementation changes.
- Blockers: none

## Required Handoff Fields

### Roadmap item(s) affected

- `Milestone 3: Real workflow loop` via the `retrieve relevant material` step's deterministic excerpt-query contract
- `feat-retrieval-fts` FTS-only excerpt fail-closed slice

### Canonical demo-path step advanced

- `retrieve relevant material` via the FTS-first engine surface with fail-closed excerpt lookup and auditable provenance.
- Deterministic FTS-only excerpt lookup strengthens auditable basket-promotion inputs.

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
