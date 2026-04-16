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
- `retrieve relevant material`: this narrowed retrieval slice makes the canonical engine retrieval step more real by ensuring excerpt lookup stays on the authoritative FTS-first path and fails closed for PageIndex-only excerpt ids, while keeping payloads and provenance deterministic for downstream basket promotion and workflow use.

## AGENTS.md handoff packet
- Risk reason: the reviewed range includes shared-by-approval regression coverage in `tests/unit/test_unified_retrieval.py`, so this handoff remains shared/high-risk work under the 4-task cap.
- Approved exception note: `tests/unit/test_unified_retrieval.py` remains the sole shared-by-approval regression surface exercised by the retrieval implementation in this range. Approval source is the earlier lane handoff packet commit `50181dd5900ccee8cef2494f15e25ff04a624252` (`docs(retrieval): refresh handoff packet for current head`, dated `2026-04-01 17:02:24 -0700`), which recorded this approved shared regression surface before the shared-file edit shipped in reviewed implementation commit `adfa8cdadd43747ffbcb612e4151e262b13e52ca` on `2026-04-02 12:10:54 -0700`.
- Traceability note: earlier packet text that treated post-`adfa8cda` commits as metadata-only was incorrect and is superseded by this packet. Re-review should use the full reviewed range above and treat `d528d36a257a948d6636a9609db244ed8bf8383b` as the reviewed implementation head.
- Task budget: `4`
- Required checkpoint status notes:
  - `plan complete`: the thread scope was locked to the canonical demo-path retrieval step and the shared/high-risk 4-task budget before the reviewed implementation work proceeded.
  - `first green local tests`: the lane reached a green local test state before the final high-risk handoff, as reflected by the passing gate set recorded in this packet.
  - `before risky/shared file edit`: the shared-file exception for `tests/unit/test_unified_retrieval.py` was already recorded in the earlier lane handoff packet commit `50181dd5900ccee8cef2494f15e25ff04a624252` before the reviewed shared-file edit landed in `adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
  - `ready for handoff`: this packet refresh records the final re-review state with the canonical demo-path step, shared-file approval traceability, and passing gate evidence aligned.
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
- Reviewer fix addressed: refreshed the handoff packet to satisfy the `AGENTS.md` requirement for an explicit canonical demo-path mapping and tied that statement to the narrowed FTS-only excerpt lookup scope the reviewer requested.
- Gate refresh date: `2026-04-16`
- Packet note: this fixer pass is metadata-only. It records the reviewer-required scope-to-demo-path mapping without changing the reviewed implementation range.
- Re-review focus: verify the handoff now states explicitly that this slice advances the canonical `retrieve relevant material` demo-path step.

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
