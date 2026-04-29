# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review target: actual branch tip after this fixer commit
- Review basis: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3..HEAD`
- Scope: high-risk command CLI contract hardening plus MVP smoke-contract public exports for the current Engine-first MVP focus without starting `feat-console`
- Current fixer pass: regenerate the handoff for the actual branch tip and actual reviewer-observed range, disclose `src/qual/cli.py` as shared-by-approval and integrator-locked, stop classifying code/test commits as metadata-only, prove live argparse choices drift is rejected, map each completed task to canonical demo-path steps, and rerun all required gates.

## Fixer Prompt `20260429T100047Z` Fix Satisfaction

1. The packet now reviews `f8d860ed9f6299f0169c4f21321ac5f37c949fd3..HEAD`, the actual branch-tip range named by the reviewer.
2. Code/test commits after `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` are explicitly included in the branch-tip review range, not classified as metadata-only.
3. `src/qual/cli.py` is explicitly disclosed as shared-by-approval and integrator-locked, with approval basis and high-risk risk accounting.
4. Size accounting is recomputed from the actual range and discloses that the net LOC budget is exceeded instead of preserving the previous narrow-slice story.
5. Each completed task maps to exact canonical demo-path steps: `open project/document`, `retrieve material`, `preview/apply/reject patch`, and `continue working`.
6. Required branch-tip gates are rerun and recorded in `THREAD_PACKET.md`, including the bare `make scope-check` and `make ci` shared-file failures and the `SCOPE_ALLOW_SHARED=1` scope/CI passes.
