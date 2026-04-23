# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `reviewer-fix packet regeneration against actual branch tip`
- Current branch tip before this fixer pass: `0bf3263dbcc96d1b94cb890c27bfd4a2375ba61d`
- Reviewed implementation head: `0bf3263dbcc96d1b94cb890c27bfd4a2375ba61d`
- Reviewed implementation range: `adfa8cdadd43747ffbcb612e4151e262b13e52ca..0bf3263dbcc96d1b94cb890c27bfd4a2375ba61d`
- Packet traceability note: the previous handoff incorrectly described post-`adfa8cda` commits as metadata-only. This packet is regenerated against the actual submitted tip `0bf3263d` and now treats the full post-`adfa8cda` retrieval/runtime diff as in-scope reviewed implementation. Interleaved docs-only packet refresh commits remain metadata, but they no longer narrow or replace the actual reviewed implementation head. This `THREAD_PACKET.md` file is the authoritative re-review source in this worktree for the canonical demo-path mapping because the mirrored `.codex` packet files are locked read-only here.

## Scope goal

- Keep Milestone 3 retrieval FTS-first while making post-lookup payloads, provenance, and excerpt/audit surfaces deterministic and fail-closed on the canonical retrieval path.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`
- Scope goal: preserve SQLite FTS as the authoritative retrieval path while hardening deterministic retrieval payloads and excerpt lookup behavior for downstream engine flows.
- Risk reason: the reviewed implementation range includes the approved shared regression surface `tests/unit/test_unified_retrieval.py`.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Regenerate the handoff packet against the real branch tip and enumerate the full post-`adfa8cda` retrieval/runtime scope.
2. Confirm every post-`adfa8cda` non-metadata file remains in the retrieval lane or the approved shared regression surface.
3. Restate the scope, task summary, and canonical demo-path mapping so they explain how the newer runtime changes keep retrieval FTS-first.
4. Re-run the required gate suite on the corrected packet state.

### Early Review Triggers

- before first edit to the shared-by-approval regression file `tests/unit/test_unified_retrieval.py`
- before changing public retrieval command or contract wording in the handoff packet
- before touching provider routing/config behavior

### Checkpoint Status

- `plan complete`: this packet now targets the actual branch tip `0bf3263d` instead of the stale `adfa8cda` metadata-only story.
- `first green tests`: recorded after rerunning `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` for this fixer pass.
- `before risky/shared file edit`: the only shared implementation file in the reviewed range remains `tests/unit/test_unified_retrieval.py`.
- `ready for handoff`: this packet now aligns `Reviewed implementation range`, `Scope completed`, `Tasks completed`, and `Files changed` to the real branch tip and names the canonical demo-path step explicitly.

## Scope completed

- Canonical demo-path step advanced: `retrieve relevant material`.
- This reviewed slice advances `retrieve relevant material` by keeping SQLite FTS authoritative while hardening the payload, provenance, source-bundle, and excerpt lookup data that downstream engine flows consume after retrieval.
- The post-`adfa8cda` runtime work stays inside the `feat-retrieval-fts` lane-owned paths `src/qual/retrieval/**` and `src/qual/engine/retrieval/**`, plus the pre-approved shared regression file `tests/unit/test_unified_retrieval.py`. No routing, provider, CLI, app, or integrator-locked entrypoints are touched.
- The runtime changes keep retrieval FTS-first rather than widening scope: `src/qual/retrieval/service.py` continues to treat FTS as authoritative, the `fts_strategy` changes normalize cache/query behavior around that same path, and the `pageindex_strategy` / `embeddings_strategy` edits remain compatibility-shim adjustments instead of restoring them as required retrieval paths.
- The branch tip `0bf3263d` adds another fail-closed retrieval hardening step by rejecting orphaned excerpt query fingerprints instead of letting stale lookup metadata silently survive. The immediately preceding runtime commit `69456f6b` does the same for orphaned sparse query mirrors.
- Across the full post-`adfa8cda` range, retrieval payload snapshots, provenance fingerprints, source/context bundle backfills, helper exports, and excerpt lookup audit fields are normalized so downstream engine flows receive deterministic, auditable retrieval state without reopening non-FTS behavior.

## Reviewed Scope Boundary

- The reviewed implementation range is `adfa8cdadd43747ffbcb612e4151e262b13e52ca..0bf3263dbcc96d1b94cb890c27bfd4a2375ba61d`.
- That reviewed range contains runtime changes in the following non-metadata files:
  - `src/qual/engine/retrieval/__init__.py`
  - `src/qual/engine/retrieval/embeddings_strategy.py`
  - `src/qual/engine/retrieval/fts_strategy.py`
  - `src/qual/engine/retrieval/interface.py`
  - `src/qual/engine/retrieval/pageindex_strategy.py`
  - `src/qual/engine/retrieval/payload.py`
  - `src/qual/retrieval/__init__.py`
  - `src/qual/retrieval/service.py`
  - `tests/unit/test_unified_retrieval.py`
- Interleaved `.codex/**`, `THREAD_PACKET.md`, and `docs/gate_passed.txt` commits in the same branch window are metadata-only and are not listed above as reviewed implementation files.

## Canonical Demo-Path Step Advanced

- `retrieve relevant material`

This handoff advances `retrieve relevant material` by ensuring the retrieval result that leaves the FTS lane stays canonical and auditable: query inputs normalize deterministically, FTS cache/query state stays isolated, payload/source-bundle reconstruction preserves the right provenance, and excerpt lookup fails closed when stale or orphaned query metadata would otherwise blur the authoritative FTS path.

## Tasks completed

1. Kept `retrieve relevant material` FTS-first by hardening the canonical retrieval/query surface across `src/qual/retrieval/service.py`, `src/qual/retrieval/__init__.py`, `src/qual/engine/retrieval/__init__.py`, and `src/qual/engine/retrieval/interface.py`, including helper exports, query normalization, confidentiality handling, and fail-closed excerpt lookup behavior.
2. Made `retrieve relevant material` deterministic and auditable in `src/qual/engine/retrieval/payload.py` and `src/qual/retrieval/service.py` by normalizing payload snapshots, basket-promotion state, source/context bundles, citation/provenance backfills, fingerprints, ranked-id mirrors, and excerpt query metadata.
3. Preserved the roadmap requirement to stay FTS-first by limiting `src/qual/engine/retrieval/fts_strategy.py`, `src/qual/engine/retrieval/pageindex_strategy.py`, and `src/qual/engine/retrieval/embeddings_strategy.py` to cache/query normalization and compatibility-shim adjustments rather than widening PageIndex or embeddings into required paths.
4. Extended the approved shared regression surface in `tests/unit/test_unified_retrieval.py` over the post-`adfa8cda` runtime range and regenerated this packet so `Reviewed implementation range`, `Scope completed`, `Files changed`, and the explicit demo-path step all match the actual submitted tip `0bf3263d`.

## Files changed

- Non-metadata reviewed implementation files in `adfa8cdadd43747ffbcb612e4151e262b13e52ca..0bf3263dbcc96d1b94cb890c27bfd4a2375ba61d`:
  - `src/qual/engine/retrieval/__init__.py`
  - `src/qual/engine/retrieval/embeddings_strategy.py`
  - `src/qual/engine/retrieval/fts_strategy.py`
  - `src/qual/engine/retrieval/interface.py`
  - `src/qual/engine/retrieval/pageindex_strategy.py`
  - `src/qual/engine/retrieval/payload.py`
  - `src/qual/retrieval/__init__.py`
  - `src/qual/retrieval/service.py`
  - `tests/unit/test_unified_retrieval.py`
- Metadata-only files touched by packet refresh commits in the same branch window:
  - `.codex/kickoff_packets/feat-retrieval-fts.md`
  - `.codex/lane_meta/feat-retrieval-fts.json`
  - `THREAD_PACKET.md`
  - `docs/gate_passed.txt`

## Commands run with results

- Gate rerun date: `2026-04-23`
- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS` (`199` tests, `OK`)
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Reviewer fix closure

1. The packet is regenerated against the actual submitted tip `0bf3263d` instead of pretending the post-`adfa8cda` chain is metadata-only.
2. `Reviewed implementation range`, `Scope completed`, `Tasks completed`, and `Files changed` now account for every non-metadata file changed between `adfa8cda` and `0bf3263d`.
3. The packet now explains why the post-`adfa8cda` runtime changes remain within the `feat-retrieval-fts` lane and still satisfy the roadmap requirement to keep retrieval FTS-first without widening scope.
4. The canonical demo-path step advanced is stated directly as `retrieve relevant material` and tied to the submitted change set.
5. The required gate suite is rerun for this corrected handoff packet and passed: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.

## Risks / blockers

- Risk: `HIGH`
- Residual risk: downstream callers that carried stale or orphaned excerpt query metadata may now fail closed instead of receiving repaired lookup payloads, which is the intended FTS-first contract but can surface latent test gaps in callers outside this lane.
- Blockers: writes to `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` are blocked in this worktree with `Operation not permitted`, so those mirror files remain stale even though this authoritative packet is corrected.

## Required handoff fields

### Roadmap item(s) affected

- `ROADMAP.md: Milestone 3: Real workflow loop`
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
- All other non-metadata reviewed files stay in the lane-owned retrieval paths.
