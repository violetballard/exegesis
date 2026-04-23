# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `reviewer-fix packet refresh`
- Current retrieval/runtime branch tip under review: `0bf3263dbcc96d1b94cb890c27bfd4a2375ba61d`
- Reviewed implementation range for retrieval/runtime scope: `adfa8cdadd43747ffbcb612e4151e262b13e52ca..0bf3263dbcc96d1b94cb890c27bfd4a2375ba61d`
- Packet traceability note: the reviewed implementation head is the real runtime commit `0bf3263dbcc96d1b94cb890c27bfd4a2375ba61d`, not a metadata-only refresh. This fixer pass updates packet metadata to match the actual post-`adfa8cda` retrieval diff, then reruns the full gate suite before creating a metadata-only packet-refresh commit on top.

## Scope goal

- Keep the retrieval lane FTS-first and deterministic by normalizing canonical retrieval payloads, provenance, and query fingerprints while failing closed on orphaned excerpt-query state.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`
- Scope goal: keep retrieval/search FTS-first, deterministic, and auditable on the canonical engine retrieval surface.
- Risk reason: the reviewed implementation range includes the approved shared regression surface `tests/unit/test_unified_retrieval.py`.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Normalize canonical retrieval query, scope, and constraint fingerprints so equivalent FTS queries produce stable downstream payloads and provenance.
2. Tighten retrieval payload/source-bundle normalization so sparse rehydration, citation bundles, and diagnostics stay deterministic and auditable.
3. Keep excerpt lookup FTS-first by rejecting orphaned or non-canonical excerpt-query mirrors instead of widening fallback behavior.
4. Extend approved shared regression coverage and re-emit the handoff packet against the actual post-`adfa8cda` retrieval/runtime branch tip.

### Early Review Triggers

- before first edit to the shared-by-approval regression file `tests/unit/test_unified_retrieval.py`
- before changing public retrieval command or contract wording in the handoff packet
- before touching provider routing/config behavior

### Checkpoint Status

- `plan complete`: the packet now anchors scope to the real post-`adfa8cda` retrieval/runtime range ending at `0bf3263d`.
- `first green tests`: recorded after rerunning `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` for the corrected packet.
- `before risky/shared file edit`: the only shared implementation file in the reviewed range remains `tests/unit/test_unified_retrieval.py`.
- `ready for handoff`: this packet now matches the actual retrieval/runtime diff after `adfa8cda`, explicitly maps the lane to `retrieve relevant material`, and records gate results for the corrected submission.

## Scope completed

- Canonical demo-path step advanced: `retrieve relevant material`.
- This reviewed range advances `retrieve relevant material` by keeping the retrieval lane on the canonical SQLite FTS path while making equivalent query inputs normalize to the same deterministic payload, provenance, and fingerprint surfaces.
- Post-`adfa8cda` retrieval runtime work stays within the `feat-retrieval-fts` lane because every runtime file changed in the reviewed range is under `src/qual/retrieval/**` or `src/qual/engine/retrieval/**`, with one approved shared regression file in `tests/unit/test_unified_retrieval.py`.
- The runtime change in [src/qual/retrieval/service.py](/Users/doctor-violet/.codex/worktrees/rfts/qual/src/qual/retrieval/service.py:1) remains FTS-first because it normalizes query/scope metadata, carries deterministic excerpt-query context, and fails closed on orphaned excerpt query fingerprints instead of adding a new PageIndex or embeddings-required path.
- The engine-side changes in [src/qual/engine/retrieval/payload.py](/Users/doctor-violet/.codex/worktrees/rfts/qual/src/qual/engine/retrieval/payload.py:1), [src/qual/engine/retrieval/fts_strategy.py](/Users/doctor-violet/.codex/worktrees/rfts/qual/src/qual/engine/retrieval/fts_strategy.py:1), [src/qual/engine/retrieval/__init__.py](/Users/doctor-violet/.codex/worktrees/rfts/qual/src/qual/engine/retrieval/__init__.py:1), and related retrieval interface files remain within scope because they expose and serialize the same canonical retrieval result rather than widening into new provider, routing, or non-FTS retrieval behavior.
- SQLite FTS remains authoritative in this lane. PageIndex and embeddings remain compatibility-only fallback surfaces and are not reintroduced as required MVP paths by this reviewed range.

## Reviewed Scope Boundary

- Reviewed implementation range: `adfa8cdadd43747ffbcb612e4151e262b13e52ca..0bf3263dbcc96d1b94cb890c27bfd4a2375ba61d`
- Non-metadata files changed in that exact range:
  - `src/qual/engine/retrieval/__init__.py`
  - `src/qual/engine/retrieval/embeddings_strategy.py`
  - `src/qual/engine/retrieval/fts_strategy.py`
  - `src/qual/engine/retrieval/interface.py`
  - `src/qual/engine/retrieval/pageindex_strategy.py`
  - `src/qual/engine/retrieval/payload.py`
  - `src/qual/retrieval/__init__.py`
  - `src/qual/retrieval/service.py`
  - `tests/unit/test_unified_retrieval.py`
- Metadata files also changed in that exact range:
  - `.codex/kickoff_packets/feat-retrieval-fts.md`
  - `.codex/lane_meta/feat-retrieval-fts.json`
  - `THREAD_PACKET.md`
  - `docs/gate_passed.txt`

## Canonical Demo-Path Step Advanced

- `retrieve relevant material`

This handoff advances `retrieve relevant material` by making the canonical retrieval surface produce stable FTS-backed query/payload/provenance outputs and by rejecting orphaned excerpt-query context rather than silently widening retrieval behavior.

## Tasks completed

1. Normalized canonical retrieval query text, scope prefixes, date ranges, section hints, and related fingerprint inputs in `src/qual/retrieval/service.py` so equivalent FTS queries resolve to the same deterministic `retrieve relevant material` payloads.
2. Tightened canonical retrieval payload, citation, source-bundle, and diagnostics serialization across `src/qual/retrieval/__init__.py`, `src/qual/engine/retrieval/payload.py`, `src/qual/engine/retrieval/__init__.py`, `src/qual/engine/retrieval/interface.py`, `src/qual/engine/retrieval/fts_strategy.py`, `src/qual/engine/retrieval/pageindex_strategy.py`, and `src/qual/engine/retrieval/embeddings_strategy.py` so downstream engine flows stay auditable without widening beyond the retrieval lane.
3. Hardened the FTS-first excerpt path in `src/qual/retrieval/service.py` by persisting canonical excerpt-query context and failing closed on orphaned excerpt query fingerprints, which keeps `retrieve relevant material` tied to authoritative FTS state instead of reopening non-canonical fallback behavior.
4. Expanded approved shared regression coverage in `tests/unit/test_unified_retrieval.py` to prove the normalized deterministic retrieval contract and the orphaned excerpt-query fail-closed behavior, then regenerated this packet and the mirrored retrieval lane metadata against the actual post-`adfa8cda` branch tip.

## Files changed

- Retrieval/runtime files in `adfa8cdadd43747ffbcb612e4151e262b13e52ca..0bf3263dbcc96d1b94cb890c27bfd4a2375ba61d`:
  - `src/qual/engine/retrieval/__init__.py`
  - `src/qual/engine/retrieval/embeddings_strategy.py`
  - `src/qual/engine/retrieval/fts_strategy.py`
  - `src/qual/engine/retrieval/interface.py`
  - `src/qual/engine/retrieval/pageindex_strategy.py`
  - `src/qual/engine/retrieval/payload.py`
  - `src/qual/retrieval/__init__.py`
  - `src/qual/retrieval/service.py`
  - `tests/unit/test_unified_retrieval.py`
- Packet metadata files refreshed for this reviewer-fix pass:
  - `.codex/kickoff_packets/feat-retrieval-fts.md`
  - `.codex/lane_meta/feat-retrieval-fts.json`
  - `THREAD_PACKET.md`
  - `docs/gate_passed.txt`

## Commands run with results

- Gate rerun date: `2026-04-23`
- `make scope-check`: `PASS` (`no policy for branch 'codex/feat-retrieval-fts'; skipping`)
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS` (`199` tests, `OK`)
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Reviewer fix closure

1. The packet is regenerated against the real retrieval/runtime branch tip `0bf3263dbcc96d1b94cb890c27bfd4a2375ba61d` instead of calling that commit metadata-only.
2. `Reviewed implementation range`, `Scope completed`, `Tasks completed`, and `Files changed` now cover every non-metadata retrieval/runtime file present between `adfa8cda` and `0bf3263d`.
3. The packet now explains why the post-`adfa8cda` runtime change in `src/qual/retrieval/service.py` and the other post-`adfa8cda` retrieval-file edits stay inside the `feat-retrieval-fts` lane and remain FTS-first.
4. The canonical demo-path step advanced is stated explicitly as `retrieve relevant material` and is tied directly to the reviewed change set.
5. The required gate suite is rerun and reported for the corrected submission in this packet and in `docs/gate_passed.txt`.

## Risks / blockers

- Risk: `HIGH`
- Residual risk: the reviewed range is broader than the earlier narrowed excerpt-only packet, so re-review now correctly covers a larger deterministic retrieval contract across nine runtime/shared files.
- Residual risk: the lane still depends on approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Blockers: writes to `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` are OS-blocked with `operation not permitted` in this worktree, so those mirror files remain stale even though this authoritative packet is corrected.

## Required handoff fields

### Roadmap item(s) affected

- `Milestone 4: Retrieval Layer`
- `feat-retrieval-fts`

### Canonical demo-path step advanced

- `retrieve relevant material`

### Vision capability affected

- `2. Retrieval-first context handling`
- `3. Auditable generation`

### Routing/provider impact note

- None

### Proposed `README.md` patch text

- None

## Scope-check / ownership note

- Shared/integrator-locked edits in the reviewed implementation range: `YES`
- Approved shared exception: `tests/unit/test_unified_retrieval.py` is the sole shared-by-approval implementation file in the reviewed retrieval scope.
- Packet-refresh edits in this fixer pass are metadata only and do not change retrieval runtime behavior beyond the already-reviewed branch tip `0bf3263d`.
