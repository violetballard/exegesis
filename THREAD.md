# Thread Packet Pointer

This file exists for compatibility with older lane and fixer prompts.

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Packet refresh commit status: metadata-only resubmission packet update.
- Reviewed implementation base previously approved for comparison: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
- Reviewed implementation range in this resubmission: the full branch delta through `5ea27f3d960f2f2876347f2b8ce616223227a713`.
- The resubmission commit is metadata-only, but the true reviewed basis includes non-doc command and diff-preview implementation across:
  - `scripts/scope-check.sh`
  - `src/qual/commands/__init__.py`
  - `src/qual/commands/canonical.py`
  - `src/qual/commands/catalog.py`
  - `src/qual/commands/diff_preview.py`
  - `tests/unit/test_commands_catalog.py`
  - `tests/unit/test_diff_preview.py`
  - `THREAD.md`
  - `THREAD_PACKET.md`
- True implementation scope included in the reviewed range:
  - parser-surface and command-catalog hardening, including drift rejection, lookup helpers, parser-ready entry argv helpers, smoke argv helpers, trusted-surface helpers, and CLI shim contracts
  - demo token and shim resolution work, including stable workflow, compatibility, and next-action metadata for `project-open`, `retrieval`, `patch-review`, `apply-patch`, `reject-patch`, `persist`, and `export-handoff`
  - legacy alias normalization and retrieval/document-open compatibility handling
  - diff-preview truncation, fingerprint, and no-diff payload stabilization
  - expanded regression coverage for command parser surfaces, trusted/demo workflow tables, compatibility aliases, next-action metadata, and diff-preview behavior
- Recomputed budget against the true reviewed basis:
  - `9` files changed
  - `+9652/-485` lines in the full `f8d860ed..5ea27f3d` range
  - this is not a valid `AGENTS.md` high-risk `4`-task handoff as previously framed because it exceeds the `<=8 files` and `<=300 net LOC` size limits
  - the packet is now truthful about that budget miss; the implementation should be split into smaller reviewable packets before integration promotion
- Canonical demo-path steps advanced by the true range:
  - `open project/document`
  - `retrieval`
  - `patch-review`
  - `apply-patch`
  - `reject-patch`
  - `persist`
  - `export-handoff`
- Roadmap / vision alignment for the true scope:
  - `ROADMAP.md` Milestone 1 (`Bootstrap Flow Stabilization`) scope item `Command and diff-preview behavior hardening`
  - `ROADMAP.md` Milestone 2 (`Test Hardening`) scope items `Add focused unit coverage for core behaviors` and `Keep command-level probes for integration confidence`
  - `PRODUCT_VISION.md` capability 4 (`Operator-first control surface`): the branch hardens the CLI-first MVP route across the full reviewed command surface while Textual remains disabled
- Required gates rerun for the true reviewed basis:
  - `make scope-check`
  - `./quality-format.sh --check`
  - `./quality-lint.sh`
  - `./quality-test.sh`
  - `./typecheck-test.sh`
  - `make ci`
