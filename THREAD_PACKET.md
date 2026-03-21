## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Scope goal: Capture the commit-accurate FTS provenance hardening and `primary_strategy_id` plumbing in retrieval policy and service.
- Scope completed: The reviewed commit `5588e19ac01c380b6369781afe145f4f3850a5ba` hardens FTS provenance in `src/qual/retrieval/service.py` and threads `primary_strategy_id` through `src/qual/engine/retrieval/__init__.py` and `src/qual/engine/retrieval/policy.py`.
- Tasks completed:
    1. Rewrote the scope goal to describe FTS provenance hardening plus `primary_strategy_id` plumbing in retrieval policy and service.
    2. Added an explicit `Scope completed` field that names the actual source files changed by `5588e19ac01c380b6369781afe145f4f3850a5ba`.
    3. Tightened the roadmap and vision mapping to FTS provenance stability and FTS-first policy plumbing only.
- Files changed:
  - `src/qual/engine/retrieval/__init__.py`
  - `src/qual/engine/retrieval/policy.py`
  - `src/qual/retrieval/service.py`
- Commands run with results:
  - `make scope-check` -> passed
  - `./quality-format.sh --check` -> passed
  - `./quality-lint.sh` -> passed
  - `./quality-test.sh` -> passed
  - `./typecheck-test.sh` -> passed
  - `make ci` -> passed
- Reviewer fix closure:
  - `#1` rewrote the scope goal and tasks to describe the actual FTS provenance hardening plus `primary_strategy_id` plumbing.
  - `#2` removed unrelated packet references and matched the file list to the reviewed commit exactly.
  - `#3` added an explicit `Scope completed` field for the actual source changes.
  - `#4` tightened roadmap and vision mapping to FTS provenance stability and FTS-first policy plumbing only.
- Checkpoint status:
  - plan complete
  - first green tests: `./quality-test.sh` passed
  - ready for handoff: all required local gates passed in this cleanup pass
- Risks/blockers:
  - No blockers. The reviewed diff is limited to `src/qual/engine/retrieval/__init__.py`, `src/qual/engine/retrieval/policy.py`, and `src/qual/retrieval/service.py`.
- Roadmap item(s) affected:
  - FTS provenance stability: keep retrieval provenance handling explicit and stable in `src/qual/retrieval/service.py`.
  - FTS-first policy plumbing: keep `primary_strategy_id` exposure narrow and consistent in retrieval exports.
- Vision capability affected:
  - FTS provenance stability
  - FTS-first policy plumbing
- Routing/provider impact note: None. No model routing or provider configuration was touched.
- Proposed `README.md` patch text: None.
