## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Scope goal: Centralize the FTS-first retrieval policy in `src/qual/engine/retrieval/policy.py` and propagate policy metadata through retrieval service diagnostics, provenance, and audit records.
- Scope completed: The reviewed commit `d050e4016bb446424a031b3c0b9c21b26220c5a9` updates `src/qual/engine/retrieval/__init__.py`, `src/qual/engine/retrieval/policy.py`, and `src/qual/retrieval/service.py`; it makes the FTS-first policy the single source of truth for active and deferred strategies and threads the policy metadata through retrieval diagnostics, provenance, and audit output.
- Tasks completed:
  1. Regenerated the packet so `Files changed` matches commit `d050e4016bb446424a031b3c0b9c21b26220c5a9` exactly and includes `src/qual/engine/retrieval/policy.py`.
  2. Removed unrelated `.codex`, PageIndex, retrieval-package, and test entries from the handoff scope because they are not part of the reviewed commit.
  3. Tightened the scope goal, task list, roadmap, and vision mapping to FTS-first policy centralization plus auditable retrieval metadata.
- Files changed:
  - `src/qual/engine/retrieval/__init__.py`
  - `src/qual/engine/retrieval/policy.py`
  - `src/qual/retrieval/service.py`
- Commands run with results:
  - `make scope-check` -> passed for branch `codex/feat-retrieval-fts`
  - `./quality-format.sh --check` -> passed
  - `./quality-lint.sh` -> passed
  - `./quality-test.sh` -> passed (`Ran 81 tests`, `OK`)
  - `./typecheck-test.sh` -> passed
  - `make ci` -> passed
- Reviewer fix closure:
  - `#1` rewrote the scope so it describes the actual `d050e4016bb446424a031b3c0b9c21b26220c5a9` change: FTS-first policy centralization in the retrieval engine and service.
  - `#2` removed unrelated `PageIndex`, retrieval-package, and test files from the files-changed claim because they are not part of the reviewed commit.
  - `#3` added an explicit `Scope completed` field describing the policy centralization and metadata propagation work.
  - `#4` tightened roadmap and vision mapping to retrieval orchestration policy and auditable FTS-first behavior.
  - `#5` reset the `Files changed` list so it matches the reviewed commit exactly.
- Checkpoint status:
  - plan complete
  - first green tests: `./quality-test.sh` passed (`Ran 81 tests`, `OK`)
  - ready for handoff: all required local gates passed in this cleanup pass
- Risks/blockers:
  - No shared, integrator-locked, or cross-lane source files are included in the reviewed commit.
  - This reviewed change is FTS-first policy centralization in `engine/retrieval`, not the broader retrieval MVP, ingestion, or PageIndex work.
- Roadmap item(s) affected:
  - Retrieval orchestration policy: centralize FTS-first strategy selection and fallback metadata.
  - Auditable FTS-first retrieval behavior: keep diagnostics, provenance, and audit output aligned with policy.
- Vision capability affected:
  - FTS-first retrieval orchestration
  - Auditable retrieval provenance
- Routing/provider impact note: None. No model routing or provider configuration was touched.
- Proposed `README.md` patch text: None.
