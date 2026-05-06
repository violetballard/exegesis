## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Handoff type: high-risk retrieval fixer handoff for the FTS-first retrieval lane.
- Reviewed implementation base: `36c5d7554b5ebcfaf5ddc59856618a3b3acd05c9`.
- Reviewed implementation head: `HEAD` after this fixer commit; final SHA is reported in the fixer response.
- Reviewed implementation range for re-review: `36c5d7554b5ebcfaf5ddc59856618a3b3acd05c9..HEAD`.
- Scope classification: high-risk because this lane includes the approved shared regression surface `tests/unit/test_unified_retrieval.py`.
- Lane-owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`.
- Approved shared regression path: `tests/unit/test_unified_retrieval.py`.
- Integrator-locked files changed: none.

## Scope Completed

This fixer keeps SQLite FTS as the authoritative MVP retrieval path and adds auditable cache-use reporting for repeated FTS retrieval runs. Retrieval diagnostics already exposed `caches_used`; this pass records the same execution metadata in the `retrieval_executed` audit event so downstream engine runs can distinguish a fresh FTS execution from a cache-backed FTS execution without changing deterministic citation/source bundle equality.

Payload reconstruction now preserves optional `caches_used` maps when external or older source-bundle-shaped snapshots already contain them, while keeping cache use out of canonical result fingerprints and deterministic citation/source bundles. That keeps basket promotion and later revise/apply steps anchored to stable retrieved evidence while still making FTS execution provenance auditable.

## Tasks Completed

1. Canonical demo-path step advanced: `retrieve relevant material`. FTS retrieval audit events now include per-strategy cache-use metadata alongside strategies used and elapsed timings.
2. Canonical demo-path step supported: `promote or gather context into the basket`. Payload helpers normalize optional cache-use maps from source-bundle-shaped snapshots without making cache hits part of deterministic citation/source equality.
3. Approved shared regression coverage verifies repeated doc-scoped FTS retrieval reports `{"fts": true}` in diagnostics and audit metadata while preserving the stable result fingerprint.

## Files Changed

Reviewed implementation range for re-review: `36c5d7554b5ebcfaf5ddc59856618a3b3acd05c9..HEAD`.

- `THREAD_PACKET.md` - authoritative handoff packet for this fixer pass.
- `src/qual/retrieval/service.py` - records `caches_used` in retrieval audit metadata.
- `src/qual/engine/retrieval/payload.py` - normalizes optional cache-use maps from reconstructed retrieval snapshots.
- `tests/unit/test_unified_retrieval.py` - approved shared regression coverage for FTS cache-use diagnostics and audit metadata.

## Budget/Risk

- Task budget: `3/4` high-risk task groups.
- File count for reviewed implementation handoff: `4 files changed`.
- Size accounting before packet rewrite: `52 insertions(+), 1 deletion(-)` across code and test files.
- AGENTS file/size status: fits high-risk size limits of `<=8 files` and `<=300 net LOC`.
- Shared/integrator exception status: `tests/unit/test_unified_retrieval.py` is approved shared regression coverage for the retrieval lane; no integrator-locked files changed.
- Routing/provider impact: none.
- PageIndex/embeddings impact: no PageIndex, embeddings, hybrid, or alternate retrieval path was added as a required MVP path.
- Remaining risks/blockers: none.

## Roadmap/Vision

- Roadmap items affected: `ROADMAP.md` Milestone 4 FTS-first retrieval orchestration/source-attribution/auditable deterministic retrieval.
- Vision capability affected: retrieval-backed context, retrieval-first context handling, auditable outputs, and reliable local-first state.
- Architecture alignment: FTS remains the required local retrieval path. PageIndex and embeddings stay compatibility-only/deferred.
- Canonical demo-path mapping: advances `retrieve relevant material` and supports `promote or gather context into the basket`.
- Routing/provider impact note: none.
- Proposed `README.md` patch text: none.

## Commands Run

Commands run for this corrected branch-tip packet on the exact worktree state committed by this fixer pass:

- `python -m pytest tests/unit/test_unified_retrieval.py` - blocked because this Python environment has no `pytest` module installed.
- `python -m unittest tests.unit.test_unified_retrieval` - passed 56 retrieval tests.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - passed smoke tests and 125 unit tests.
- `./typecheck-test.sh` - passed Python source compilation under `src/`.
- `make ci` - passed setup, scope-check, format, lint, compile/typecheck, smoke tests, and 125 unit tests.

## Metadata Note

The root `THREAD_PACKET.md` is the authoritative regenerated handoff packet for this fixer pass. The reviewed implementation range intentionally covers `36c5d7554b5ebcfaf5ddc59856618a3b3acd05c9..HEAD` so all production and test changes present at the branch tip are traceable.
