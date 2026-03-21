## Thread Handoff Packet

- Branch name: `codex/feat-a2ui-contract`
- Scope goal: Harden the read-only fallback path by validating the canonical `copy_to_clipboard` action payload and duplicate action-label handling in `src/qual/ui/a2ui.py`.
- Scope completed: Added canonical validation for read-only fallback actions in `src/qual/ui/a2ui.py`, including the expected `copy_to_clipboard` action id, `Copy JSON` label, string `text` payload, no confirmation, no policy-sensitive flag, and duplicate-action rejection.
- Tasks completed:
  1. Added `_validate_canonical_read_only_fallback_actions()` in `src/qual/ui/a2ui.py` to enforce the canonical fallback clipboard action shape.
  2. Wired the validator into `build_unknown_card()` so the read-only fallback path rejects invalid or duplicate fallback actions before materializing the card.
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
  - No known blockers. The change is intentionally narrow and stays inside the unknown-card read-only fallback path.
  - The fallback action contract is now stricter, so any future fallback payload changes must keep the canonical copy action shape and duplicate rejection behavior intact.
- Roadmap item(s) affected:
  - Milestone 5: A2UI Presentation Layer - keep read-only fallback actions canonical and safe when the client cannot render a specialized card, including duplicate action-label handling.
  - Milestone 5: A2UI Presentation Layer - validate the fallback clipboard action shape before exposing it in the materialized card.
  - Milestone 5: A2UI Presentation Layer - reject duplicate fallback actions so the terminal and contract stay aligned on a single canonical copy action.
- Vision capability affected:
  - Capability 5: Agent-to-UI protocol (A2UI) - read-only fallback cards now expose a single canonical clipboard action with validated payload shape.
  - Capability 4: Operator-first control surface - fallback handling stays safe and predictable by rejecting duplicate or malformed actions.
- Routing/provider impact note: None. No model routing or provider configuration was touched.
- Proposed `README.md` patch text: None.
