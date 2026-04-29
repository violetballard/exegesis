# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review target: actual branch tip after the `20260429T094519Z` fixer pass
- Review basis: `a6cf0fd59763be784dae53d1cf707938ef20c385..HEAD` after this fixer commit
- Scope: command CLI contract hardening plus MVP smoke-contract public exports for the current Engine-first MVP focus without starting `feat-console`
- Current fixer pass: prove the command contract rejects live argparse token drift, explicitly map the slice to CLI fallback command execution across the canonical demo path, and rerun required gates.

## Fixer Prompt `20260429T094519Z` Fix Satisfaction

1. `src/qual/cli.py` builds the real argparse top-level parser from `command_cli_lookup_table()` and exposes live parser tokens through `command_parser_tokens()`.
2. `command_cli_contract()` compares catalog tokens and lookup rows against the live argparse parser surface.
3. `tests/unit/test_commands_catalog.py` proves same-canonical alias drift, missing/extra parser-token drift, parser-token reorder drift, and actual `add_parser()` rewrite drift are rejected.
4. `THREAD_PACKET.md` names the canonical demo-path step advanced as CLI fallback command execution across `project-open` -> `retrieval` -> `patch-review` -> `export-handoff`.
5. Required branch-tip gates are recorded in `THREAD_PACKET.md` after rerun.
