## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Handoff type: `retrieval feature handoff for the FTS-first retrieval lane`
- Packet HEAD role: `metadata-only reviewer-fix finalization`
- Reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`

## Scope completed
- Removed the PageIndex fallback from `fetch_excerpt` so the public excerpt lookup surface resolves through the canonical FTS-only path.
- Added approved shared regression coverage proving PageIndex-only excerpt ids fail closed with `KeyError`.
- Kept SQLite FTS as the authoritative MVP retrieval path and did not reintroduce PageIndex or embeddings as required runtime paths.

## Canonical demo-path step advanced
- `retrieve relevant material`: this slice hardens deterministic, auditable FTS-only excerpt retrieval on the canonical retrieval step, which keeps provenance stable for downstream basket promotion and workflow use.

## AGENTS.md handoff packet
- Risk reason: shared-by-approval regression coverage in `tests/unit/test_unified_retrieval.py` is part of the reviewed implementation range, so this handoff uses the high-risk/shared-work framing required by `AGENTS.md`.
- Approved exception note: `tests/unit/test_unified_retrieval.py` is the sole shared-by-approval file exercised in this reviewed slice.
- Task budget: `4`
- Tasks completed:
  1. Removed the PageIndex fallback from `fetch_excerpt` so the public excerpt lookup surface now resolves through the canonical FTS-only path.
  2. Added approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proving PageIndex-only excerpt ids fail closed with `KeyError`.
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

## Risks/blockers
- Risks: high; the slice changes the public excerpt lookup contract, but keeps runtime behavior narrowed to deterministic FTS-only retrieval.
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
