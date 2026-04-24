# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `feature lane handoff`
- Current branch tip before this handoff refresh commit: `dd73909afaeada2b8d48e7eade98f9a968636936`
- Reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation range: `d7fd5d200358287fa42a18d39e2b277463b9b69f..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Scope goal: keep the retrieval lane FTS-first for the MVP by making the canonical retrieval/query/export surfaces deterministic for downstream engine flows and by keeping public excerpt lookup on the authoritative SQLite FTS path.
- Canonical demo-path step advanced: `retrieve relevant material`
- Reviewer-required plan-alignment statement: This work makes `retrieve relevant material` more real by keeping SQLite FTS authoritative across the retrieval facade, exported helper surfaces, and excerpt rehydration path, so downstream basket-promotion inputs stay deterministic and PageIndex-only excerpt IDs fail closed.

## Scope Completed

- Kept the reviewed implementation range FTS-first for the MVP: SQLite FTS remains the authoritative retrieval backend, while PageIndex and embeddings stay compatibility-only fallback shims rather than required runtime paths.
- Deliberately expanded the retrieval contract surface where the canonical demo path needed it: exported the canonical retrieval query constructor and `retrieve_auto` helper through both retrieval facades, normalized payload/provenance snapshots, and backfilled sparse source/context bundles so engine-side consumers read one deterministic retrieval shape.
- Added provenance and export helpers needed by that same canonical retrieval step, including citation/source bundle normalization and FTS provenance bundle support, so the retrieved material passed downstream is auditable instead of lane-local or second-order-only.
- Hardened the public `fetch_excerpt` path to resolve through the canonical FTS lookup only, so PageIndex-only excerpt IDs now fail closed with `KeyError` instead of silently rehydrating through a non-canonical fallback.
- Verified the reviewed implementation range and re-ran the required local gate suite on the current packet-refresh branch head.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: correct the reviewer-facing handoff so it accurately describes the cumulative reviewed retrieval implementation range without widening beyond the approved FTS-first MVP lane.
- Risk reason: this reviewed slice includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, so it is shared/high-risk work under the 4-task cap.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks

1. Confirm the actual reviewed implementation head and cumulative reviewed range for the retrieval lane.
2. Regenerate the handoff so `Scope completed`, `Tasks completed`, and `Files changed` match that real range.
3. State directly which canonical demo-path step this work advances and justify the additional contract/provenance surface against that step.
4. Re-run the required gates and record results on the packet-refresh branch head.

## Tasks Completed

1. Confirmed the reviewed implementation range is `d7fd5d200358287fa42a18d39e2b277463b9b69f..adfa8cdadd43747ffbcb612e4151e262b13e52ca`, not the narrower `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca` slice previously described by the packet.
2. Reconciled the packet to the real reviewed scope, including the retrieval provenance/export helper work, the canonical retrieval facade exports, the planner coverage change, and the approved shared regression coverage.
3. Documented that the additional API and test expansion is deliberate contract-surface work for the canonical demo-path step `retrieve relevant material`, not detached second-order work: downstream engine flows need deterministic retrieval bundles, query helpers, and excerpt rehydration to consume the retrieved material reliably.
4. Re-ran `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`, all passing on the current packet-refresh branch head.

## Files Changed

- Metadata-only fixer pass for this handoff refresh:
- `THREAD_PACKET.md`
- Reviewed implementation files in `d7fd5d200358287fa42a18d39e2b277463b9b69f..adfa8cdadd43747ffbcb612e4151e262b13e52ca`:
- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`
- `codex_packet_handoff/tools/planner.py`
- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/embeddings_strategy.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/pageindex_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/__init__.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_packet_planner.py`
- `tests/unit/test_unified_retrieval.py`

## Commands Run With Results

- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Risks / Blockers

- Risk: `HIGH`
- Blockers: `None`

## Required Handoff Fields

### Roadmap item(s) affected

- `Milestone 3: Real workflow loop`
- `feat-retrieval-fts`
- The canonical `retrieve relevant material` step now uses deterministic FTS-first retrieval/query/export surfaces in the reviewed implementation range.

### Vision capability affected

- `2. Retrieval-first context handling`
- `6. Auditable state and workflow`

### Canonical demo-path step advanced

- `retrieve relevant material`
- The reviewed range makes that step more real by exporting one deterministic retrieval/query/provenance contract into engine-facing consumers and by keeping excerpt rehydration on the canonical FTS path.

### Routing/provider impact note

- None

### Proposed README.md patch text

- None

## Reviewer Fix Closure

1. `Scope completed`, `Tasks completed`, and `Files changed` now describe the full reviewed implementation range `d7fd5d200358287fa42a18d39e2b277463b9b69f..adfa8cdadd43747ffbcb612e4151e262b13e52ca`, including the provenance bundle APIs, retrieval facade exports, planner coverage, and shared regression coverage that remain in scope.
2. The packet explicitly justifies the additional API/test expansion against the canonical demo-path step `retrieve relevant material`: deterministic retrieval/query/export contracts are required for downstream engine flows to consume retrieved material reliably during Milestone 3.
3. The handoff directly names the canonical demo-path step advanced in the required form.
4. The extra provenance/export work is called out as deliberate contract-surface expansion that supports the canonical retrieval path rather than detached second-order work.

## Validation Refresh

- Full required gate suite rerun on `2026-04-24`
- Reviewed implementation range for this handoff: `d7fd5d200358287fa42a18d39e2b277463b9b69f..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Current packet-refresh branch head at validation time: `dd73909afaeada2b8d48e7eade98f9a968636936`
- This fixer pass is metadata-only and does not change the reviewed implementation head or reviewed implementation range above.
