## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Handoff type: `retrieval feature handoff for the FTS-first retrieval lane`
- Packet HEAD role: `docs-only reviewer-fix handoff correction`
- Reviewed implementation head: `96bed1e1feb3a4708e74b768b9e3659cb0a000de`
- Reviewed implementation range: `410b8fa0dc040ae4805ecf7627fc2468ccc58ace..96bed1e1feb3a4708e74b768b9e3659cb0a000de`

## Scope completed
- Normalized retrieval document identity inputs so document ids, document types, and title hints are canonicalized before metadata, blob, and FTS writes, and legacy blob rows are cleaned up when an input doc id changes only by surrounding whitespace.
- Normalized retrieval evidence strategy ids when rebuilding downstream payloads from source bundles so active and deferred strategy lists stay deterministic and deduplicated in the auditable FTS-first payload surface.
- Kept SQLite FTS as the authoritative MVP retrieval path and limited the reviewed implementation slice to lane-owned retrieval code plus the approved shared regression file.

## Canonical demo-path step advanced
- `retrieve relevant material`: this slice hardens deterministic, auditable FTS-only excerpt retrieval on the canonical engine retrieval step, keeping downstream basket promotion and workflow use anchored to stable provenance.

## AGENTS.md handoff packet
- Risk reason: shared-by-approval regression coverage in `tests/unit/test_unified_retrieval.py` is part of the reviewed implementation range, so this handoff uses the high-risk/shared-work framing required by `AGENTS.md`.
- Approved exception note: `tests/unit/test_unified_retrieval.py` is the sole shared-by-approval file exercised in this reviewed slice.
- Task budget: `4`
- Tasks completed:
  1. Canonicalized retrieval document ids, document types, and title hints before storage and FTS updates.
  2. Removed legacy blob/meta duplication when a document is rewritten with a normalized doc id.
  3. Normalized evidence strategy id lists rebuilt from source bundles so downstream payloads keep stable FTS-first provenance.
  4. Added regression coverage for document identity normalization and evidence strategy id normalization.
- Files changed:
  - `src/qual/retrieval/service.py`
  - `src/qual/engine/retrieval/payload.py`
  - `tests/unit/test_unified_retrieval.py`

## Commands run with results
- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

## Risks/blockers
- Risks: high; the slice includes approved shared regression coverage, but runtime scope remains limited to deterministic FTS-first retrieval payload handling.
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
