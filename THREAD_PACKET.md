## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Reviewed implementation commit: `36893f06df85409c4595d64adb8af60455c086a6`
- Reviewed commit type: Canonical auto payload plumbing for the FTS-first MVP.

## Scope Goal

Expose the canonical auto retrieval payload inside retrieval-owned paths while preserving the FTS-first MVP contract for downstream engine generation flows.

## Scope Completed

The reviewed implementation routes `retrieve_auto()` through the retrieval service's canonical FTS-first payload path, exposes `retrieve_auto_payload()` for downstream consumers, re-exports `primary_strategy_id` from the engine retrieval package, and adds focused unit coverage for payload parity and package-export behavior. PageIndex and embeddings remain deferred and are not required MVP paths.

### Related implementation files

- Reviewed code files:
  - `src/qual/engine/retrieval/__init__.py`
  - `src/qual/engine/tools/retrieval_tools.py`
  - `src/qual/retrieval/service.py`
  - `tests/unit/test_unified_retrieval.py`
- Handoff-only artifacts updated in this fix commit:
  - `.codex/kickoff_packets/feat-retrieval-fts.md`
  - `.codex/lane_meta/feat-retrieval-fts.json`
  - `THREAD_PACKET.md`
- Tasks completed:
  1. Routed `retrieve_auto()` through the canonical retrieval-service FTS-first payload path.
  2. Exposed `retrieve_auto_payload()` and `primary_strategy_id()` through the engine retrieval surface.
  3. Added focused unit coverage for canonical payload parity and package-export behavior.
  4. Rewrote the handoff packet metadata so the reviewed code files and handoff-only artifacts are separated explicitly.
- Files changed:
  - Reviewed implementation code:
    - `src/qual/engine/retrieval/__init__.py`
    - `src/qual/engine/tools/retrieval_tools.py`
    - `src/qual/retrieval/service.py`
    - `tests/unit/test_unified_retrieval.py`
  - Handoff-only artifacts:
    - `.codex/kickoff_packets/feat-retrieval-fts.md`
    - `.codex/lane_meta/feat-retrieval-fts.json`
    - `THREAD_PACKET.md`
- Commands run with results:
  - `make scope-check` -> passed
  - `./quality-format.sh --check` -> passed
  - `./quality-lint.sh` -> passed
  - `./quality-test.sh` -> passed
  - `./typecheck-test.sh` -> passed
  - `make ci` -> passed
  - These gate results were rerun against the handoff packet fix state.
- Reviewer fix closure:
  - `#1` split the reviewed code files from the handoff-only artifacts and kept the reviewed patch surface exact.
  - `#2` added a concrete scope-completed summary tied to the reviewed commit.
  - `#3` narrowed the task summary to the canonical auto payload plumbing actually delivered by `36893f06df85409c4595d64adb8af60455c086a6`.
  - `#4` reran the required gates after the handoff packet fix and captured the passing results.
- Checkpoint status:
  - plan complete
  - first green tests: `./quality-test.sh` passed
  - ready for handoff: all required local gates passed
- Risks/blockers:
  - No blockers. The packet wording is now explicit about the retrieval implementation boundary and the reviewed patch surface.
- Roadmap item(s) affected:
  - Milestone 4: Retrieval Layer -> FTS-first ingestion/index path for context/vault documents
  - Milestone 4: Retrieval Layer -> Retrieval orchestration data needed before drafting/diff generation
  - Milestone 4: Retrieval Layer -> Source-attribution model for retrieved chunks
  - Milestone 2: Test Hardening -> Add focused unit coverage for core behaviors
- Vision capability affected:
  - 2. Retrieval-first context handling
  - 3. Auditable generation
  - 4. Operator-first control surface
- Routing/provider impact note: None.
- Proposed `README.md` patch text: None.
