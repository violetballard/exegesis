## Thread Handoff Packet

- Branch name: `codex/feat-a2ui-contract`
- Scope goal: Make unknown-card rendering copy-only in `src/qual/ui/a2ui.py` and keep terminal fallback rendering aligned with the same copy-only fallback rule.
- Scope completed: Hardened unknown-card rendering so it emits only the canonical copy-to-clipboard action, and updated terminal fallback rendering to respect that copy-only fallback rule.
- Tasks completed:
  1. Updated unknown-card rendering in `src/qual/ui/a2ui.py` so fallback cards keep only the canonical `copy_to_clipboard` action and preserve the read-only clipboard payload.
  2. Adjusted terminal fallback rendering in `src/qual/ui/a2ui.py` so unknown-card output follows the copy-only fallback rule instead of exposing broader actions.
- Files changed:
  - `src/qual/ui/a2ui.py`
- Commands run with results:
  - `make scope-check` -> passed
  - `./quality-format.sh --check` -> passed
  - `./quality-lint.sh` -> passed
  - `./quality-test.sh` -> passed
  - `./typecheck-test.sh` -> passed
  - `make ci` -> passed
- Risks/blockers:
  - No known blockers. The change is intentionally narrow and stays inside unknown-card materialization and terminal fallback display.
  - Future fallback rendering changes must preserve the copy-only constraint so terminal fallback stays read-only.
- Roadmap item(s) affected:
  - Milestone 5: A2UI Presentation Layer - make unknown-card fallback rendering copy-only in the A2UI materialization path.
  - Milestone 5: A2UI Presentation Layer - keep terminal fallback rendering aligned with the read-only unknown-card behavior.
- Vision capability affected:
  - Capability 5: Agent-to-UI protocol (A2UI) - unknown-card fallback now exposes a canonical copy-only action payload.
  - Capability 4: Operator-first control surface - terminal fallback stays predictable because it presents read-only unknown-card output.
- Routing/provider impact note: None. No model routing or provider configuration was touched.
- Proposed `README.md` patch text: None.
