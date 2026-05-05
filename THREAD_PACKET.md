## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Base branch HEAD before this pass: `deb503b70614cac43fdf05b97f1d52c345b204ba`
- Final commit: created after this packet refresh; final SHA is reported in the fixer deliverable.
- Scope classification: high-risk/shared because this pass updates approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Handoff type: retrieval feature fixer handoff for the FTS-first retrieval lane.

## Scope Completed

This pass tightens the canonical FTS-only excerpt lookup surface for downstream engine callers. Standalone excerpt lookups now expose the same `excerpt_text` field shape as retrieval hits while preserving the existing `text` field, and the public retrieval facades now include `fetch_excerpt` as a generic alias that still fails closed through the FTS-only lookup path.

The change keeps SQLite FTS as the authoritative retrieval path. PageIndex and embeddings remain deferred/compatibility-only paths and are not introduced as active retrieval strategies.

## Tasks Completed

1. Normalized standalone FTS excerpt lookup payloads so fetched excerpts expose `excerpt_text` in parity with retrieval hit payloads for basket/context promotion.
2. Added `fetch_excerpt` to the public retrieval and engine retrieval facades while keeping the call routed to the canonical FTS-only service path.
3. Added approved shared regression coverage proving the new facade aliases return the canonical FTS payload and preserve `text`/`excerpt_text` parity.

## Files Changed

- `src/qual/retrieval/service.py` - normalizes FTS excerpt lookup payloads to carry both `text` and `excerpt_text`.
- `src/qual/retrieval/__init__.py` - exports the generic `fetch_excerpt` facade through the canonical FTS-only lookup path.
- `src/qual/engine/retrieval/__init__.py` - exports the engine-facing `fetch_excerpt` facade through the canonical retrieval package.
- `tests/unit/test_unified_retrieval.py` - approved shared regression coverage for `fetch_excerpt` facades and lookup text parity.
- `THREAD_PACKET.md` - updated handoff packet for this fixer pass.

Lane-owned source files:

- `src/qual/retrieval/service.py`
- `src/qual/retrieval/__init__.py`
- `src/qual/engine/retrieval/__init__.py`

Shared-by-approval files:

- `tests/unit/test_unified_retrieval.py` - approved shared regression surface for the retrieval lane.

Integrator-locked files: none.

## Budget/Risk

- Task budget: `3/4` high-risk tasks.
- File budget: `5/8` high-risk files.
- Source/test file count: `4` files.
- Current pass net LOC before packet update: `+41`.
- Shared-file approval note: `tests/unit/test_unified_retrieval.py` is the approved shared-by-approval regression surface for this lane.
- Routing/provider impact: none.
- PageIndex/embeddings impact: none; both remain deferred/compatibility-only.
- Remaining risk: low implementation risk; the change is additive to FTS excerpt lookup facades/payloads and covered by focused and full local gates.

## Roadmap/Vision

- Roadmap items affected: `ROADMAP.md` active MVP focus for `feat-retrieval-fts`; Milestone 3/4 retrieval layer support for retrieving relevant material.
- Vision capabilities affected: `PRODUCT_VISION.md` retrieval-first context handling and auditable generation/state.
- Canonical demo-path mapping: this work advances `retrieve relevant material` and supports basket/context promotion by making standalone FTS excerpt lookups match the canonical retrieval hit text shape through the public engine surface.
- Routing/provider impact note: none.
- Proposed `README.md` patch text: none.

## Commands Run

- `python -m unittest tests.unit.test_unified_retrieval -q` PASS, 64 tests.
- `./quality-format.sh --check` PASS.
- `./quality-lint.sh` PASS.
- `./quality-test.sh` PASS, 133 tests.
- `./typecheck-test.sh` PASS.
- `make ci` PASS, including scope-check for `codex/feat-retrieval-fts` and 133 tests.

## Risks/Blockers

No blocker remains. Focused retrieval coverage and all required handoff gates passed.
