# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `metadata-only reviewer-fix finalization`
- Packet refresh trace anchor before this fixer commit: `11441ef0f54f33a2adb128feb13ecf00555e2141`
- Reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation range: `d7fd5d200358287fa42a18d39e2b277463b9b69f..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Canonical demo-path step advanced: `retrieve relevant material`
- Plan-alignment statement: this reviewed range advances `retrieve relevant material` by keeping SQLite FTS authoritative, exporting the canonical retrieval contract through both facades, and making retrieval payloads, provenance snapshots, and excerpt lookup behavior deterministic enough for the engine-first workflow loop.
- Traceability note: review this lane against the reviewed implementation range above. The current packet refresh commit is metadata-only and does not broaden retrieval scope beyond `d7fd5d20..adfa8cda`.

## Scope Goal

- Regenerate the retrieval handoff packet so it accurately describes the full reviewed implementation range anchored at `adfa8cdadd43747ffbcb612e4151e262b13e52ca`, including the retrieval contract and provenance surfaces that landed before the final fail-closed excerpt change.

## Scope Completed

- Branch-level cumulative handoff from `d7fd5d200358287fa42a18d39e2b277463b9b69f..adfa8cdadd43747ffbcb612e4151e262b13e52ca`: SQLite FTS remains authoritative.
- The canonical retrieval query constructor and `retrieve_auto` helper are exported through both retrieval facades, so the public engine/package retrieval surfaces stay aligned.
- Retrieval dataclass-shaped constraints are normalized deterministically, and payload/provenance/hit snapshot helpers keep stable downstream shapes for engine flows.
- Source-bundle and provenance-bundle helpers return deterministic snapshots for downstream engine flows.
- Sparse source and context bundles rehydrate deterministically, including the provenance and query-context expectations covered in `tests/unit/test_unified_retrieval.py`.
- The excerpt lookup surface now uses the canonical FTS-only path, so PageIndex-only excerpt IDs fail closed under shared regression coverage.
- PageIndex and embeddings remain compatibility-only fallback shims that fail closed rather than required MVP retrieval paths.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: correct the reviewer-facing packet against the reviewed retrieval implementation head `adfa8cdadd43747ffbcb612e4151e262b13e52ca` without broadening the reviewed scope beyond that cumulative range.
- Risk reason: this handoff includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, so it is shared/high-risk work under the 4-task cap.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Keep the handoff anchored to reviewed implementation head `adfa8cda` and reviewed range `d7fd5d20..adfa8cda`.
2. Rewrite the scope and tasks so they explicitly include the retrieval contract, provenance snapshot, and helper-surface changes already present in that reviewed range.
3. State the canonical demo-path step explicitly as `retrieve relevant material` using the repo's engine-first wording.
4. Re-run the required gates and record results against the narrowed reviewed implementation head/range.

## Tasks Completed

1. Re-anchored the packet to reviewed implementation head `adfa8cdadd43747ffbcb612e4151e262b13e52ca` and reviewed range `d7fd5d200358287fa42a18d39e2b277463b9b69f..adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
2. Regenerated `Scope Completed` so it explicitly covers the retrieval contract changes in the reviewed range: facade exports, deterministic dataclass-shaped constraints, deterministic payload/provenance/hit snapshots, source/provenance bundle helpers, sparse bundle rehydration, and FTS-only excerpt lookup behavior.
3. Added the explicit canonical demo-path statement for `retrieve relevant material` and tied it to deterministic engine-first retrieval behavior.
4. Re-ran the required local gates after refreshing the reviewer-facing metadata.

## Files Changed

### Reviewed implementation files

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `codex_packet_handoff/tools/planner.py`
- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/embeddings_strategy.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/pageindex_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/__init__.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_packet_planner.py`
- `tests/unit/test_unified_retrieval.py` (approved shared regression coverage)

### Current metadata-only packet refresh files

- `THREAD_PACKET.md`
- `docs/gate_passed.txt`
- `.codex/kickoff_packets/feat-retrieval-fts.md` (unchanged in this session because the `apply_patch` tool rejects hidden `.codex/**` paths here)
- `.codex/lane_meta/feat-retrieval-fts.json` (unchanged in this session because the `apply_patch` tool rejects hidden `.codex/**` paths here)

## Commands Run With Results

- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Reviewer Fix Closure

1. `Scope completed` and `Tasks completed` now describe the full reviewed implementation range anchored at `adfa8cda`, not just the final `fetch_excerpt` fail-closed behavior.
2. The handoff explicitly includes the added retrieval contract, provenance snapshot, and helper-surface changes in scope and plan mapping rather than implying a narrower implementation than the reviewed range.
3. The handoff explicitly states that this work advances the canonical demo-path step `retrieve relevant material` using engine-first wording.
4. This fixer pass refreshes the writable reviewer-facing packet surfaces and removes the stale write-permission claim from the visible handoff.

## Risks / Blockers

- Risk: `HIGH`
- Blockers: the `apply_patch` tool in this session rejects hidden `.codex/**` paths as outside the project, so the tracked mirror files `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` could not be updated through the required edit path.

## Required Handoff Fields

### Roadmap item(s) affected

- `ROADMAP.md: Milestone 3: Product Readiness`
- `ROADMAP.md: define generation provenance contract (retrieval evidence attached to outputs)`

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
