## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Handoff type: `retrieval feature handoff for the FTS-first retrieval lane`
- Packet HEAD role: `reviewed implementation head`
- Reviewed implementation head: `ded01c00cdaa76ebe13ba0cedaef0b76736b6473`
- Reviewed implementation range: `d7fd5d200358287fa42a18d39e2b277463b9b69f..ded01c00cdaa76ebe13ba0cedaef0b76736b6473`

## Scope completed
- Kept SQLite FTS as the authoritative retrieval path for the MVP and preserved the canonical `retrieve_auto`/`retrieve_fts` engine surface.
- Hardened retrieval query, cache, payload, provenance, evidence, and fingerprint normalization so downstream bundles stay deterministic and auditable.
- Removed the `fetch_excerpt` PageIndex fallback so excerpt lookup now fails closed on the canonical FTS-only path, and hardened sparse source bundle normalization.
- Added and updated regression coverage for the canonical retrieval contract, including PageIndex-only excerpt ids raising `KeyError` and packet-planner traceability coverage.

## Canonical demo-path step advanced
- `retrieve relevant material`: this reviewed range hardens the engine-side retrieval step by keeping excerpt lookup, payloads, and provenance deterministic on the FTS-first path used for downstream basket promotion and workflow use.

## AGENTS.md handoff packet
- Risk reason: the reviewed range includes shared-by-approval regression coverage in `tests/unit/test_unified_retrieval.py`, so this handoff remains shared/high-risk work under the 4-task cap.
- Approved exception note: `tests/unit/test_unified_retrieval.py` remains the sole shared-by-approval regression surface exercised by the retrieval implementation in this range.
- Traceability note: earlier packet text that treated post-`adfa8cda` commits as metadata-only was incorrect and is superseded by this packet. Re-review should use the full reviewed range above and treat `ded01c00cdaa76ebe13ba0cedaef0b76736b6473` as the reviewed implementation head.
- Task budget: `4`
- Tasks completed:
  1. Kept the retrieval lane FTS-first, including stable retrieval entrypoints, normalized candidate-doc handling, and unresolved collection-scope guards.
  2. Hardened deterministic retrieval payloads, evidence, provenance, query snapshots, and fingerprint generation across the retrieval facade and engine payload helpers.
  3. Narrowed excerpt lookup to the canonical FTS-only path and hardened sparse retrieval source bundle normalization.
  4. Expanded regression coverage for retrieval determinism, fail-closed excerpt lookup, and packet-planner traceability for the reviewed range.
- Files changed:
  - `.codex/kickoff_packets/feat-retrieval-fts.md`
  - `.codex/lane_meta/feat-retrieval-fts.json`
  - `THREAD_PACKET.md`
  - `codex_packet_handoff/tools/planner.py`
  - `src/qual/engine/retrieval/__init__.py`
  - `src/qual/engine/retrieval/embeddings_strategy.py`
  - `src/qual/engine/retrieval/fts_strategy.py`
  - `src/qual/engine/retrieval/interface.py`
  - `src/qual/engine/retrieval/pageindex_strategy.py`
  - `src/qual/engine/retrieval/payload.py`
  - `src/qual/retrieval/__init__.py`
  - `src/qual/retrieval/service.py`
  - `tests/unit/test_packet_planner.py`
  - `tests/unit/test_unified_retrieval.py`

## Commands run with results
- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

## Risks/blockers
- Risks: high; the reviewed range changes retrieval payload normalization and the public excerpt lookup contract, but it keeps runtime behavior narrowed to deterministic FTS-first retrieval.
- Blockers: none

## Roadmap item(s) affected
- `ROADMAP.md`: `Milestone 3: Real workflow loop`
- `ROADMAP.md`: `feat-retrieval-fts - retrieval/search`

## Vision capability affected
- `PRODUCT_VISION.md`: `2. Retrieval-first context handling`
- `PRODUCT_VISION.md`: `6. Auditable state and workflow`

## Routing/provider impact note
- None

## Proposed README.md patch text
- None
