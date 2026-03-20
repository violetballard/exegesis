# Lane Kickoff: feat-a2ui-contract

- Branch: `codex/feat-a2ui-contract`
- Lane/owned paths: `src/qual/ui/**`
- Scope goal: Stabilize the A2UI contract and CLI fallback rendering so engine flows can emit structured artifacts now and future `Exegesis Console` work can consume the same payloads later.

### Priority outcomes
1. Keep card/action schemas deterministic and versionable.
2. Make CLI fallback rendering reliable for the demo loop.
3. Enforce safe unknown-card and allowlisted-action behavior.

### Guardrails
- No dedicated web client work.
- Keep renderer logic separate from engine decisions.
- Favor a small, stable contract over broad UI ambition.
