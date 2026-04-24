# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `metadata-only reviewer-fix re-emit`
- Current submitted tip before this packet refresh commit: `e96b9e841bca7609b37a168126eb982e8f352f49`
- Reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation range: `d7fd5d200358287fa42a18d39e2b277463b9b69f..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Packet traceability note: review this lane against the narrowed implementation range above. The current packet refresh commit is metadata-only and does not broaden retrieval scope beyond `d7fd5d20..adfa8cda`.
- Canonical demo-path step advanced: `retrieve relevant material`
- Reviewer-required plan-alignment statement: This change makes `retrieve relevant material` more real by ensuring retrieval evidence, provenance, and excerpt lookup all stay anchored to the authoritative SQLite FTS path.
- Evidence note: `tests/unit/test_unified_retrieval.py` covers both the narrowed service-level contract and the public retrieval facade for this slice. It proves PageIndex-only excerpt IDs fail closed on `fetch_excerpt(...)`, verifies the canonical/public FTS excerpt helpers return the same payload shape, and covers the provenance-bundle, payload snapshot, and public helper behavior that now sits on the same FTS-first runtime contract.
- Packet authority note: this top-level packet and `docs/gate_passed.txt` are the reviewer-facing source of truth for the explicit demo-path mapping and plan-alignment wording on this branch.

## Scope Goal

- Regenerate the retrieval-specific handoff packet so it stays narrowed to reviewed commit `adfa8cdadd43747ffbcb612e4151e262b13e52ca`, truthfully describes the full reviewed retrieval slice, states explicitly that this change makes `retrieve relevant material` more real, and reports the reviewer-facing refresh files from this packet slice accurately.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: correct the reviewer packet against the reviewed retrieval implementation head `adfa8cdadd43747ffbcb612e4151e262b13e52ca` while keeping the claim narrow to the reviewed FTS-first retrieval slice and not newly asserting broader engine-surface reachability outside that range.
- Scope note: this handoff covers the narrowed reviewed retrieval slice, including the FTS-only runtime guards, provenance-bundle surface, deterministic payload work, and excerpt lookup behavior behind the existing retrieval surface; it does not newly establish broader engine-surface reachability on its own.
- Risk reason: this handoff includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, so it is shared/high-risk work under the 4-task cap.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Keep the handoff anchored to reviewed implementation head `adfa8cda` and reviewed range `d7fd5d20..adfa8cda`.
2. Regenerate `Scope completed` and `Tasks completed` so they match the full reviewed retrieval slice instead of an excerpt-only summary.
3. State the canonical demo-path step explicitly as `retrieve relevant material` and tie it to the reviewed FTS-only retrieval/runtime contract.
4. Reconcile the packet file lists, shared-file approval note, and metadata-only traceability so they match this packet-refresh slice, then re-run the required gates.

### Checkpoint Status

- `plan complete`: the packet is anchored to the reviewer-approved retrieval implementation range `d7fd5d20..adfa8cda`.
- `first green tests`: recorded after rerunning `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.
- `before risky/shared file edit`: this handoff includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- `ready for handoff`: the top-level packet and gate summary agree on the same reviewed implementation head, reviewed range, risk class, reviewed files, and reviewer-facing refresh files; `.codex/` mirrors remain stale because that subtree is not writable in this worktree.

## Scope Completed

- SQLite FTS remains the authoritative retrieval path for the reviewed implementation range.
- Retrieval hit/doc-hit models enforce FTS-only runtime contracts, so the public retrieval surfaces stay fail-closed when non-FTS data tries to cross that boundary.
- The public excerpt lookup surface resolves through the canonical FTS path, so PageIndex-only excerpt IDs fail closed with no PageIndex runtime fallback on that surface.
- Provenance bundles, payload snapshots, and sparse source/context rehydration stay deterministic across the reviewed retrieval helpers and public facade.
- This reviewed retrieval slice makes the canonical demo-path step `retrieve relevant material` more real by ensuring the engine-first demo path consumes deterministic FTS-backed retrieval payloads and provenance instead of fallback-derived excerpt lookups.

## Reviewed Scope Boundary

- Reviewed implementation range: `d7fd5d200358287fa42a18d39e2b277463b9b69f..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation files:
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`
- Current reviewer-facing handoff files refreshed in this fixer pass:
- `THREAD_PACKET.md`
- `docs/gate_passed.txt`
- Stale `.codex/` mirror files not refreshed due to local filesystem write restrictions:
- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`

## Tasks Completed

1. Documented the reviewed FTS-first runtime changes accurately: FTS-only excerpt lookup, FTS-only retrieval hit/doc-hit guards, deterministic provenance bundles, deterministic payload snapshots, and shared coverage for those public helper surfaces.
2. Kept the reviewed scope anchored to commit `adfa8cdadd43747ffbcb612e4151e262b13e52ca` and range `d7fd5d200358287fa42a18d39e2b277463b9b69f..adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
3. Added the explicit AGENTS narrowing statement that this slice makes `retrieve relevant material` more real in the engine-first demo path.
4. Re-emitted the reviewer-facing handoff artifacts so the completed packet is no longer stale or lane-mismatched, and recorded that the `.codex/` mirror files could not be refreshed in this worktree because that subtree is not writable.

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
3. The handoff is classified consistently as shared/high-risk work because the reviewed slice includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, and that approval is reconfirmed to cover the provenance/payload/helper assertions in addition to the fail-closed excerpt regression.
4. The completed packet is retrieval-specific and branch-local instead of lane-stale.
5. The reviewed file list and reviewer-facing gate summary match the narrowed reviewed implementation range and current packet-refresh contents, and the packet explicitly calls out the stale `.codex/` mirrors.
6. The reviewer-facing truth sources are explicitly identified so re-review reads the demo-path mapping from this packet and `docs/gate_passed.txt`.

## Risks / Blockers

- Risk: `HIGH`
- Blockers: `.codex/` packet mirrors are not writable in this worktree, so only the reviewer-facing handoff packet and gate summary were refreshed.

## Required Handoff Fields

### Roadmap item(s) affected

- `Milestone 3: Real workflow loop` via the `retrieve relevant material` step's deterministic FTS-backed retrieval contract
- `feat-retrieval-fts` FTS-only retrieval/runtime guard and provenance-helper slice

### Canonical demo-path step advanced

- `retrieve relevant material`
- Deterministic FTS-only retrieval payloads, provenance bundles, and excerpt lookup strengthen auditable basket-promotion inputs.

### Vision capability affected

- `2. Retrieval-first context handling`
- `6. Auditable state and workflow`

### Routing/provider impact note

- None

### Proposed `README.md` patch text

- None

## Scope-Check / Ownership Note

- Shared or integrator-locked edits: `YES`
- Approved shared regression coverage remains limited to `tests/unit/test_unified_retrieval.py`, and that approval covers the fail-closed excerpt regression plus the payload, provenance-bundle, and public helper assertions in the narrowed reviewed range.
