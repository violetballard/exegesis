# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review target: actual branch tip after this fixer commit
- Review basis: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3..HEAD`
- Scope: high-risk command CLI contract hardening plus MVP smoke-contract public exports for the current Engine-first MVP focus without starting `feat-console`
- Current fixer pass: satisfy fixer prompt `20260429T104143Z` by making `command_cli_contract()` name and validate the live argparse parser surface directly, preserving regression coverage for real parser token drift, naming the canonical demo-path steps advanced, and clarifying ownership for the current fixer slice versus the broader branch-tip range.

## Fixer Prompt `20260429T104143Z` Fix Satisfaction

1. `command_cli_contract()` now captures `src.qual.cli.command_parser_lookup_table()` and `src.qual.cli.command_parser_tokens()` as explicit live parser inputs before validation.
2. Regression coverage includes real argparse parser choice mutation and top-level `add_parser()` token rewrite cases, so parser token drift in `src/qual/cli.py` is rejected independently of `command_names()` drift.
3. The canonical demo-path steps advanced are `open project/document`, `retrieve material`, `preview/apply/reject patch`, and `continue working` through the CLI fallback commands.
4. Current fixer-slice ownership is lane-owned command contract plus handoff metadata; the broader branch-tip packet separately discloses the prior `src/qual/cli.py` shared/integrator-locked parser binding and its approval basis.
