# Lane Kickoff: feat-a2ui-contract

- Branch: `codex/feat-a2ui-contract`
- Lane/owned paths: `src/qual/ui/**`
- Scope goal: Harden the `Milestone 5: A2UI Presentation Layer` contract in `src/qual/ui/a2ui.py` by enforcing canonical, duplicate-free capability allowlists for cards and actions while keeping the existing A2UI fallback behavior stable for future `Exegesis Console` consumption.

### Priority outcomes
1. Keep card and action allowlists canonical and duplicate-free at the handshake boundary.
2. Keep the A2UI fallback path stable while capability validation tightens.
3. Keep contract tests aligned with the validation rules in `src/qual/ui/a2ui.py`.

### Guardrails
- No dedicated web client work.
- Keep renderer logic separate from engine decisions.
- Favor a small, stable contract over broad UI ambition.
