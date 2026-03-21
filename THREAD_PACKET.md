## Thread Handoff Packet

- Branch name: `codex/feat-a2ui-contract`
- Scope goal: Version fallback card debug metadata in `src/qual/ui/a2ui.py` and keep the fallback assertions aligned with that versioned debug payload.
- Scope completed: Added `contract_version: 2` to fallback debug metadata in `src/qual/ui/a2ui.py` and updated the matching assertions to require the versioned fallback debug payload.
- Tasks completed:
  1. Added `contract_version: 2` to `_build_fallback_debug()` in `src/qual/ui/a2ui.py` so generic and unknown fallback cards carry a stable contract marker in their debug payload.
  2. Updated the fallback-card assertions in `tests/unit/test_a2ui_contract.py` so the generic and unknown fallback paths verify the versioned debug metadata and its matching contract behavior.
- Files changed:
  - `src/qual/ui/a2ui.py`
  - `tests/unit/test_a2ui_contract.py`
- Commands run with results:
  - `make scope-check` -> passed
  - `./quality-format.sh --check` -> passed
  - `./quality-lint.sh` -> passed
  - `./quality-test.sh` -> passed
  - `./typecheck-test.sh` -> passed
  - `make ci` -> passed
- Risks/blockers:
  - No known blockers. The change is intentionally narrow and stays inside fallback debug metadata versioning.
  - Future fallback rendering changes must preserve the `contract_version` marker so debug payloads stay contract-verifiable.
- Roadmap item(s) affected:
  - Milestone 5: A2UI Presentation Layer - version fallback debug metadata so generic and unknown cards advertise a stable contract marker.
  - Milestone 5: A2UI Presentation Layer - keep fallback assertions aligned with the versioned debug payload exposed by the contract.
- Vision capability affected:
  - Capability 5: Agent-to-UI protocol (A2UI) - fallback cards now carry versioned debug metadata that clients can validate against the contract.
  - Capability 4: Operator-first control surface - fallback presentation stays predictable because the debug payload is now explicitly versioned.
- Routing/provider impact note: None. No model routing or provider configuration was touched.
- Proposed `README.md` patch text: None.
