# Thread Handoff Packet

- Lane: `feat-retrieval-fts`
- Branch: `codex/feat-retrieval-fts`

## Scope completed

- Kept the engine-side retrieval shim explicitly aligned with the canonical FTS-first retrieval surface by exporting `RetrievalConstraints` and `RetrievalQuery` through `src/qual/engine/retrieval/__init__.py`.
- Added regression coverage proving those lazy runtime types are part of the explicit engine retrieval public API, not just opportunistic attributes.

## Canonical demo-path step advanced

- `retrieve relevant material`
- The engine-facing retrieval surface now exposes the canonical query dataclasses directly, so engine callers and downstream tooling can construct deterministic FTS-first retrieval requests from the same public contract used by the retrieval package.
- This keeps basket-promotion and later revise/apply flows anchored to one auditable retrieval query shape instead of private or implicit module internals.

## Tasks completed (numbered)

1. Added `RetrievalConstraints` and `RetrievalQuery` to the explicit engine retrieval export list so the compatibility shim publishes the canonical query contract.
2. Extended approved shared regression coverage in `tests/unit/test_unified_retrieval.py` to assert those exported types are present and identity-stable on the engine retrieval surface.

## Files changed

- `src/qual/engine/retrieval/__init__.py`
- `tests/unit/test_unified_retrieval.py`
- `THREAD_PACKET.md`
- `docs/gate_passed.txt`

## Commands run and outcomes

- `python -m unittest tests.unit.test_unified_retrieval -q`: PASS
- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

## Risks / blockers

- Residual risk: the retrieval lane still relies on approved shared coverage in `tests/unit/test_unified_retrieval.py`, so future engine-surface export changes should keep that shared contract in sync.
- Blockers: none

## Required handoff fields

### Roadmap item(s) affected

- `ROADMAP.md`: Milestone 4: Retrieval Layer
- `ROADMAP.md`: Milestone 3: Product Readiness

### Vision capability affected

- `2. Retrieval-first context handling`
- `3. Auditable generation`

### Routing/provider impact note

- None

### Proposed `README.md` patch text

- None
