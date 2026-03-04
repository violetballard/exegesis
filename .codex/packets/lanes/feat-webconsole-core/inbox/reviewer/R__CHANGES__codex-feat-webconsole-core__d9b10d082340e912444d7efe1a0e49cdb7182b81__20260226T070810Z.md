## Verdict
CHANGES_REQUESTED

## Findings
- Branch diff still deletes the entire OSS console rendering stack (e.g., `src/qual/webconsole/render/a2ui.py:1`, `src/qual/webconsole/render/pages.py:1`, `src/qual/webconsole/templates/base.html:1`, `src/qual/webconsole/static/webconsole.js:1`). That wipes out the reference client Milestone 5 explicitly requires (`ROADMAP.md:106-129`) and the operator-first/A2UI capabilities in the product vision (`PRODUCT_VISION.md:35-44`). Restoring those assets is mandatory before we can review narrower HTTP-server changes.
- Canonical roadmap and product vision text was pruned without any stated approval: key launch policies and telemetry/packaging requirements were removed from `ROADMAP.md:58-129` and capabilities 8–10 were stripped from `PRODUCT_VISION.md:52-80`. Those files define the non-negotiable plan, so any edit must be tightly scoped and explicitly justified; right now the packet provides neither alignment nor rationale.
- `_WebConsoleHandler._handle` now constructs `ApiRequest` outside the `try/except`, so `_read_body` errors (missing `Content-Length`, oversized POST, etc.) no longer translate into JSON error responses but bubble out as uncaught exceptions (`src/qual/webconsole/server/http_server.py:80-91`). That regresses the very hardening this thread claims to deliver.
- High-risk budget guardrails aren’t met. The diff still touches far more than the allowed ≤8 files (examples beyond the packet list: `ROADMAP.md`, `PRODUCT_VISION.md`, `THREAD_OWNERSHIP.md`, `UNIFIED_RETRIEVAL_SPEC.md`, `.agents/skills/*.md`, etc.), violating the limits mandated in `AGENTS.md:7-55` and the lane-specific gate in `INTEGRATION.md:112-130`. The kickoff text saying “2 files touched” is incompatible with the actual branch state.

## Missing handoff fields
- Scope goal (required top-level field is blank).
- Roadmap item(s) affected (left as “pending confirmation” instead of naming the Milestone entry).
- Vision capability affected (also marked as pending instead of picking from `PRODUCT_VISION.md`).

## Required fixes before re-review
1. Rebase or otherwise restore the entire webconsole render/templates/static tree so Milestone‑5/A2UI functionality stays intact, then keep this thread scoped to the HTTP-server hardening (`src/qual/webconsole/render/**`, `src/qual/webconsole/templates/**`, `src/qual/webconsole/static/**` must no longer be deleted).
2. Revert unintended roadmap/vision edits (e.g., restore the profile-mode, telemetry, packaging, and UIPattern sections in `ROADMAP.md` and `PRODUCT_VISION.md`) unless there is an approved plan change with the proper packet to document it.
3. Put `_WebConsoleHandler._handle` back under the `try/except` so `_read_body` and header parsing errors continue to yield structured `ApiError` responses instead of uncaught exceptions (`src/qual/webconsole/server/http_server.py:80-91`).
4. Bring the handoff into compliance: stay within the high-risk budget (≤4 tasks, ≤8 files, ≤300 net LOC) or document an approved exception, and fill in the missing required fields (scope goal, roadmap mapping, vision capability).

No merge guidance while these issues remain.