# Lane Kickoff: feat-a2ui-contract

- Branch: `codex/feat-a2ui-contract`
- Lane/owned paths: `src/qual/ui/**`
- Scope goal: Stabilize the A2UI contract and CLI fallback rendering so engine flows can emit structured artifacts now and future `Exegesis Console` work can consume the same payloads later.

### Priority outcomes
1. Keep card/action schemas deterministic and versionable.
2. Make CLI fallback rendering reliable for the demo loop.
3. Keep contract work in service of the engine loop instead of leading product scope.

### Definition of done
- Shared action, card, and selection structures are stable enough for engine outputs.
- CLI can consume the same structures that future UI work will consume.
- Contract shape does not force UI-specific assumptions into the engine.

### Do not spend time on
- The full final A2UI protocol.
- Presentation richness before the engine loop is standing.
- Letting contract polish outrun actual workflow behavior.

### Guardrails
- No dedicated web client work.
- Keep renderer logic separate from engine decisions.
- Favor a small, stable contract over broad UI ambition.
