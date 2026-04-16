## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Handoff type: `retrieval feature handoff for the FTS-first retrieval lane`
- Packet HEAD role: `metadata-only gate-refresh handoff`
- Reviewed implementation head: `d528d36a257a948d6636a9609db244ed8bf8383b`
- Reviewed implementation range: `d7fd5d200358287fa42a18d39e2b277463b9b69f..d528d36a257a948d6636a9609db244ed8bf8383b`

## Scope completed
- Kept SQLite FTS as the authoritative retrieval path for the MVP and preserved the canonical `retrieve_auto`/`retrieve_fts` engine surface.
- Hardened retrieval query, cache, payload, provenance, evidence, and fingerprint normalization so downstream bundles stay deterministic and auditable, including sparse provenance metadata normalization.
- Removed the `fetch_excerpt` PageIndex fallback so excerpt lookup now fails closed on the canonical FTS-only path, and hardened sparse source bundle normalization.
- Added and updated regression coverage for the canonical retrieval contract, including PageIndex-only excerpt ids raising `KeyError` and packet-planner traceability coverage.

## Canonical demo-path step advanced
- `retrieve relevant material`: this reviewed range hardens the engine-side retrieval step by keeping excerpt lookup, payloads, and provenance deterministic on the FTS-first path used for downstream basket promotion and workflow use.

## AGENTS.md handoff packet
- Risk reason: the reviewed range includes shared-by-approval regression coverage in `tests/unit/test_unified_retrieval.py`, so this handoff remains shared/high-risk work under the 4-task cap.
- Approved exception note: `tests/unit/test_unified_retrieval.py` remains the sole shared-by-approval regression surface exercised by the retrieval implementation in this range.
- Traceability note: earlier packet text that treated post-`adfa8cda` commits as metadata-only was incorrect and is superseded by this packet. Re-review should use the full reviewed range above and treat `d528d36a257a948d6636a9609db244ed8bf8383b` as the reviewed implementation head.
- Task budget: `4`
- Tasks completed:
  1. Kept the retrieval lane FTS-first, including stable retrieval entrypoints, normalized candidate-doc handling, and unresolved collection-scope guards.
  2. Hardened deterministic retrieval payloads, evidence, provenance, query snapshots, and fingerprint generation across the retrieval facade and engine payload helpers.
  3. Narrowed excerpt lookup to the canonical FTS-only path and hardened sparse retrieval source bundle normalization.
  4. Expanded regression coverage for retrieval determinism and fail-closed excerpt lookup, then normalized sparse provenance metadata in the canonical retrieval service without widening scope beyond the FTS-first lane.
- Files changed:
  - `.codex/kickoff_packets/feat-retrieval-fts.md`
  - `.codex/lane_meta/feat-retrieval-fts.json`
  - `THREAD_PACKET.md`
  - `src/qual/retrieval/service.py`
  - `tests/unit/test_unified_retrieval.py`

## Commands run with results
- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

## Reviewer-required fix evidence
- Reviewer fix addressed: reran the full required gate set on reviewed implementation head `d528d36a257a948d6636a9609db244ed8bf8383b` and refreshed this packet with the passing results above.
- Gate refresh date: `2026-04-16`
- Packet note: this fixer pass is metadata-only. It records the green gate evidence the reviewer requested without changing the reviewed implementation range.

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
