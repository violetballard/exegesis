## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Handoff type: `retrieval feature handoff for the FTS-first retrieval lane`

## Scope completed
- Kept SQLite FTS as the authoritative MVP retrieval path.
- Removed the public `fetch_excerpt` PageIndex fallback so excerpt lookup now fails closed on the canonical FTS-only path.
- Kept the approved shared regression surface in `tests/unit/test_unified_retrieval.py` aligned with that contract by asserting PageIndex-only excerpt ids raise `KeyError`.

## Canonical demo-path step advanced
- `retrieve relevant material`: this handoff makes the canonical retrieval step more real by requiring FTS-backed excerpt ids on the public excerpt lookup surface. `fetch_excerpt` now fails closed unless the excerpt resolves through the canonical SQLite FTS path, which preserves deterministic and auditable provenance for downstream engine flows.

## AGENTS.md handoff packet
- Risk reason: shared-by-approval regression coverage in `tests/unit/test_unified_retrieval.py` is part of the reviewed implementation range, so this handoff uses the high-risk/shared-work framing required by `AGENTS.md`.
- Approved exception note: `tests/unit/test_unified_retrieval.py` is the sole shared-by-approval file exercised in this lane for the canonical retrieval contract.
- Task budget: `4`
- Tasks completed:
  1. Removed the PageIndex fallback from `src/qual/retrieval/service.py` so `fetch_excerpt` resolves only through the canonical FTS excerpt lookup path.
  2. Added approved shared regression coverage proving PageIndex-only excerpt ids fail closed with `KeyError`.
- Files changed:
  - `src/qual/retrieval/service.py`
  - `tests/unit/test_unified_retrieval.py`

## Commands run with results
- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

## Final reviewer-fix verification
- `2026-04-13`: Updated the handoff packet to state the canonical demo-path step explicitly as `retrieve relevant material` and tied it to the FTS-only `fetch_excerpt` contract change the reviewer requested.
- `2026-04-13`: Re-ran all required gates after confirming the handoff packet reflects both the high-risk/shared-work framing and the required demo-path alignment from review.

## Risks/blockers
- Risks: high; shared approved regression coverage is part of the reviewed slice, but runtime behavior remains narrowed to the FTS-only retrieval contract.
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
