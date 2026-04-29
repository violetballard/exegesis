# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review target: full branch tip of `codex/feat-commands`.
- Review basis: `git diff main...codex/feat-commands`.
- Scope: deterministic MVP command contract for the current command catalog, parser surface, smoke command lines, and demo-path checkpoints.
- Demo-path mapping: task-by-task details in `THREAD_PACKET.md` explicitly use the canonical steps `open document`, `retrieve material`, `gather/promote context`, `preview/apply/reject patch`, `persist/save`, and `continue`; this slice does not claim direct `plan/revise` implementation.
- Final readiness: the command-catalog slice now makes `retrieve material` and `gather/promote context` more real for the CLI-first Milestone 3 loop, while locking adjacent patch-review, persistence, and continuation handoffs.
- Shared-file exception: `src/qual/cli.py` is included in the branch-tip review target because the actual argparse parser consumes catalog-owned CLI tokens.
- Fixer prompt satisfied: `20260429T130328Z`; canonical packet details live in `THREAD_PACKET.md`.
