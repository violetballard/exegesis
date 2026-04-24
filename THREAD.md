# Thread Packet Pointer

This file exists for compatibility with older lane and fixer prompts.

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Packet refresh status: reviewer-fix packet refresh regenerated on 2026-04-24 for the exact reviewed implementation slice.
- Reviewed implementation commit: `088768cd1a66f67052618f271522d19225ebf0a1` (`Stabilize terminal demo command tokenization`).
- Reviewed implementation files:
  - `src/qual/commands/__init__.py`
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
- Metadata-only refresh files:
  - `THREAD.md`
  - `THREAD_PACKET.md`
- Reviewed implementation scope:
  - deterministic CLI compatibility for the patch-decision fallback surface: preserve requested terminal demo verbs and publish one trusted invocation table for `patch-review -> apply-patch/reject-patch -> persist -> export-handoff`
- Primary canonical demo-path step advanced now:
  - `preview and apply or reject a patch`
- Required handoff field now called out explicitly:
  - `Canonical demo-path step advanced: preview and apply or reject a patch`
- Explicit re-review statement:
  - this slice advances the canonical `preview and apply or reject a patch` step, and no other demo-path step
- Primary-step scope note:
  - this packet advances `preview and apply or reject a patch` only
- One-line plan alignment:
  - this change makes `preview and apply or reject a patch` more real by keeping the CLI fallback patch-decision contract deterministic and preserving the requested workflow verb before the operator chooses apply or reject
- Active MVP operator path strengthened:
  - the CLI fallback path for `patch-review -> apply-patch/reject-patch -> persist -> export-handoff` by keeping command tokenization deterministic and trusted invocation order stable
- Direct plan-alignment statement:
  - this change makes `preview and apply or reject a patch` more real by preserving the requested patch-decision verb and publishing one deterministic trusted invocation contract for that branch
- Traceability note:
  - `088768cd1a66f67052618f271522d19225ebf0a1` is the actual implementation tip for this reviewed slice; later commits on the branch are packet-only refreshes
- Concrete blocker removed for Milestone 3:
  - the active CLI surface no longer allows terminal-backed patch-decision commands to drift silently away from the requested `apply-patch` or `reject-patch` verb when terminal messages vary, and consumers now have one authoritative trusted invocation table for that branch before the operator can continue through `persist` and `export-handoff`
- Scope-tightening note:
  - this reviewed slice hardens only deterministic patch-branch command tokenization plus trusted invocation-table publication for the primary `preview and apply or reject a patch` fallback step; it does not claim progress on project open, retrieval quality, persistence semantics, or final export delivery beyond that branch contract
- Why this is milestone-worthy now:
  - the roadmap requires the CLI to execute the MVP `vault -> context -> run -> patch -> export` loop while Textual remains disabled, so preventing silent drift in the patch-decision branch is direct operator-surface hardening rather than second-order cleanup
- Roadmap / vision alignment for this reviewed slice:
  - `ROADMAP.md` Milestone 3 exit criterion: `CLI can execute the MVP flow (vault -> context -> run -> patch -> export) against the same engine PolicyGate`, applied here to the `patch` segment only
  - `PRODUCT_VISION.md` capability 4 `Operator-first control surface`: keep the CLI patch-decision branch deterministic
  - `PRODUCT_VISION.md` capability 5 `Agent-to-UI protocol (A2UI)`: keep the parser-ready patch-branch contract stable for CLI-first artifact consumption
- Ownership / scope note:
  - lane-owned implementation paths: `src/qual/commands/__init__.py`, `src/qual/commands/catalog.py`
  - approved shared-by-approval exception: `tests/unit/test_commands_catalog.py`
  - approval reference: the local `reviewer` lane recorded the shared-test approval in `.codex/packet_router/local_jobs/reviewer/20260416T185314Z__feat-commands__F__codex-feat-commands__f3e88eb90a1116054bac208067568d3c7fbed927__20260416T185054Z.md.spec.json`
  - integrator-locked edits are not part of this slice
- Required gates for the reviewed slice:
  - `make scope-check`
  - `./quality-format.sh --check`
  - `./quality-lint.sh`
  - `./quality-test.sh`
  - `./typecheck-test.sh`
  - `make ci`
