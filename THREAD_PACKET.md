## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Handoff type: `retrieval feature handoff for the FTS-first retrieval lane`
- Packet HEAD role: `metadata-only reviewer-fix gate evidence refresh for 2026-04-16 rerun`
- Reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Packet refresh base commit before this rerun: `e4d7956110458f2d9e375d82c50e443b039a0571`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`

## Scope goal
- Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt, provenance, and evidence output.

## Scope completed
- SQLite FTS remains the authoritative MVP retrieval path in the narrowed slice. The reviewed implementation commit removes the PageIndex fallback from `fetch_excerpt`, keeping excerpt lookup on the canonical FTS-only path, while approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proves PageIndex-only excerpt IDs now raise `KeyError`. This means the public excerpt lookup surface no longer promotes PageIndex as a required runtime path. PageIndex and embeddings remain non-required compatibility paths in this slice.

## Canonical demo-path step advanced

- Reviewer-required alignment note: this metadata-only fixer pass keeps the handoff explicit about the canonical demo-path step required by `AGENTS.md`.
- `retrieve relevant material`: this handoff explicitly advances that canonical demo-path step because `fetch_excerpt` now fails closed to the canonical FTS-backed lookup path instead of falling back to PageIndex. Retrieval hits, excerpt lookup payloads, and downstream evidence/provenance bundles now stay deterministic and auditable on the FTS-first path.
- Specific contract tightening: `fetch_excerpt` now fails closed to the FTS-backed canonical retrieval surface, so `PageIndex` is not promoted as a required runtime path for the MVP retrieval contract.
- Pre-basket rationale: this is MVP retrieval work rather than general cleanup because the stricter FTS-only excerpt contract preserves the structured and auditable retrieval surface needed before the engine can `promote or gather context into the basket`.

## Reviewer-required fix
- Reviewer packet fix addressed: `Resolve failing gate output and include passing results.`
- Reviewer packet fix addressed: `Add an explicit canonical demo-path step and tighten the roadmap/vision mapping to that step-level rationale.`
- Local reproduction note: no failing gate was reproducible on branch tip `e4d7956110458f2d9e375d82c50e443b039a0571` when rerun on `2026-04-16`.
- Fixer action: reran the full required gate sweep and refreshed this handoff packet so the passing evidence is explicit for re-review.

## AGENTS.md handoff packet
- Risk reason: shared/high-risk work because the reviewed implementation range includes the approved shared regression surface `tests/unit/test_unified_retrieval.py`.
- Task budget: `4`
- Required checkpoint status notes:
  - `plan complete`: the packet is now anchored to the narrowed reviewed implementation head and reviewed range in the reviewer packet.
  - `first green local tests`: the required gate sweep rerun completed cleanly on `2026-04-16`.
  - `before risky/shared file edit`: no new risky/shared implementation files were edited in this fixer pass; the reviewed implementation range still includes the approved shared regression file.
  - `ready for handoff`: the packet traceability is internally consistent and the required gates are rerun with passing results recorded below.
- Tasks completed:
  1. Removed the PageIndex fallback from `fetch_excerpt` so the public excerpt lookup surface now resolves through the canonical FTS-only path.
  2. Added approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proving PageIndex-only excerpt IDs fail closed with `KeyError`.
- Files changed:
  - `src/qual/retrieval/service.py`
  - `tests/unit/test_unified_retrieval.py`

## Commands run with results
- `make scope-check`: PASS on `2026-04-16` (`[devex] scope-check: passed for branch 'codex/feat-retrieval-fts'`)
- `./quality-format.sh --check`: PASS on `2026-04-16` (`[format] check passed`)
- `./quality-lint.sh`: PASS on `2026-04-16` (`[lint] passed`)
- `./quality-test.sh`: PASS on `2026-04-16` (`Ran 157 tests in 4.938s`, `OK`, `[test] passed`)
- `./typecheck-test.sh`: PASS on `2026-04-16` (`[typecheck] compiling Python sources in src/`)
- `make ci`: PASS on `2026-04-16` (`Ran 157 tests in 4.904s`, `OK`, `[devex] CI entrypoint completed`)
- Final fixer-pass note: the full required gate sweep was rerun on the lane branch and this metadata-only refresh commit records the passing evidence requested by review.

## Risks/blockers
- Risks: high, because the narrowed reviewed range includes approved shared regression coverage.
- Blockers: none

## Roadmap item(s) affected
- `ROADMAP.md`: `Milestone 3: Real workflow loop`
- Step-level alignment: `retrieve relevant material` is the canonical demo-path step this narrowed retrieval slice advances by keeping excerpt lookup on the authoritative FTS-backed path before basket promotion.

## Vision capability affected
- `PRODUCT_VISION.md`: `2. Retrieval-first context handling`
- `PRODUCT_VISION.md`: `6. Auditable state and workflow`
- Step-level alignment: deterministic excerpt lookup, provenance, and evidence output stay stable on the FTS-first path used before `promote or gather context into the basket`.

## Routing/provider impact note
- None

## Proposed README.md patch text
- None
