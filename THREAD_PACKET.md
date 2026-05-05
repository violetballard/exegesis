## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Base branch HEAD before this pass: `36422e25565cb2a3ddfd6e4d551a980b0c9140cb`
- Final commit: created after this packet refresh; final SHA is reported in the fixer deliverable.
- Scope classification: high-risk/shared because this pass updates approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Handoff type: retrieval feature fixer handoff for the FTS-first retrieval lane.

## Scope Completed

This pass adds a deterministic `excerpt_lookup_fingerprint` to canonical FTS-only excerpt lookup payloads. The fingerprint is derived from the excerpt id, doc id, source hash, canonical span, text hash, source strategy, backend, mode, and lookup resolution, and is mirrored into the lookup provenance snapshot.

The change keeps SQLite FTS as the authoritative retrieval path. PageIndex and embeddings remain deferred/compatibility-only paths and are not introduced as active retrieval strategies.

## Tasks Completed

1. Added a stable FTS excerpt lookup fingerprint to standalone excerpt lookup payloads for downstream audit and basket/context promotion checks.
2. Mirrored the lookup fingerprint into excerpt lookup provenance so copied payloads remain self-auditing.
3. Added approved shared regression coverage proving lookup aliases preserve the same fingerprint and remain FTS-only.

## Files Changed

- `src/qual/retrieval/service.py` - adds deterministic excerpt lookup fingerprint construction and includes it in canonical FTS lookup payloads/provenance.
- `tests/unit/test_unified_retrieval.py` - approved shared regression coverage for stable FTS lookup fingerprints.
- `THREAD_PACKET.md` - updated handoff packet for this fixer pass.

Lane-owned source files:

- `src/qual/retrieval/service.py`

Shared-by-approval files:

- `tests/unit/test_unified_retrieval.py` - approved shared regression surface for the retrieval lane.

Integrator-locked files: none.

## Budget/Risk

- Task budget: `3/4` high-risk tasks.
- File budget: `3/8` high-risk files.
- Source/test file count: `2` files.
- Current pass net LOC before packet update: `+66`.
- Shared-file approval note: `tests/unit/test_unified_retrieval.py` is the approved shared-by-approval regression surface for this lane.
- Routing/provider impact: none.
- PageIndex/embeddings impact: none; both remain deferred/compatibility-only.
- Remaining risk: low implementation risk; the change is additive to FTS excerpt lookup payloads and covered by focused and full local gates.

## Roadmap/Vision

- Roadmap items affected: `ROADMAP.md` active MVP focus for `feat-retrieval-fts`; Milestone 3/4 retrieval layer support for retrieving relevant material.
- Vision capabilities affected: `PRODUCT_VISION.md` retrieval-first context handling and auditable generation/state.
- Canonical demo-path mapping: this work advances `retrieve relevant material` and supports basket/context promotion by making standalone FTS excerpt lookups carry stable audit fingerprints.
- Routing/provider impact note: none.
- Proposed `README.md` patch text: none.

## Commands Run

- `python -m pytest tests/unit/test_unified_retrieval.py -q` FAIL: active Python 3.14 environment has no `pytest` module; no environment changes were made.
- `python -m unittest tests.unit.test_unified_retrieval -q` PASS, 64 tests.
- `./quality-format.sh --check` PASS.
- `./quality-lint.sh` PASS.
- `./quality-test.sh` PASS, 133 tests.
- `./typecheck-test.sh` PASS.
- `make ci` PASS, including scope-check for `codex/feat-retrieval-fts` and 133 tests.

## Risks/Blockers

No blocker remains. The bare `pytest` command could not run because the active Python environment does not include `pytest`, but the repo's unittest-based focused coverage and all required handoff gates passed.
