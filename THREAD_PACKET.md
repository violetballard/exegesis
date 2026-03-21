## Thread Handoff Packet

- Branch name: `codex/feat-a2ui-contract`
- Scope goal: Harden unknown-card preview handling by normalizing the preview budget in `src/qual/ui/a2ui.py`.
- Scope completed: Added preview-budget normalization in `src/qual/ui/a2ui.py` so unknown-card rendering clamps and standardizes the preview byte limit before building the raw JSON preview.
- Tasks completed:
  1. Added preview-budget normalization in `src/qual/ui/a2ui.py` to make unknown-card preview sizing deterministic and safe.
  2. Wired the normalized budget into `build_unknown_card()` so the raw JSON preview is rendered with a canonical byte limit before the card is materialized.
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
  - No known blockers. The change is intentionally narrow and stays inside unknown-card preview budgeting.
  - Future unknown-card rendering changes must preserve the normalized preview budget so preview truncation stays deterministic.
- Roadmap item(s) affected:
  - Milestone 5: A2UI Presentation Layer - keep unknown-card fallback rendering safe and deterministic when the client cannot render a specialized card.
  - Milestone 5: A2UI Presentation Layer - standardize the preview budget used for fallback JSON rendering so output remains stable.
- Vision capability affected:
  - Capability 5: Agent-to-UI protocol (A2UI) - unknown-card artifacts now render with a normalized preview budget for CLI-first fallback consumption.
  - Capability 4: Operator-first control surface - fallback presentation stays predictable by clamping preview size before rendering raw JSON.
- Routing/provider impact note: None. No model routing or provider configuration was touched.
- Proposed `README.md` patch text: None.
