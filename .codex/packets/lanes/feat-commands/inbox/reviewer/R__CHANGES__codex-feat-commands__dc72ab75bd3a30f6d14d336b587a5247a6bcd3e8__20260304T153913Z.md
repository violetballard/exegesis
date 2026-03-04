## Verdict
CHANGES_REQUESTED

## Findings
- `README.md:1` is replaced with a single `# init` line even though `INTEGRATION.md:9-11` marks README as integrator-owned; at the same time the governance docs `AGENTS.md`, `ROADMAP.md`, and `PRODUCT_VISION.md` are deleted outright. Removing the documents that define budgets, milestones, and required capabilities makes the branch non-compliant with the very plan (ROADMAP/Product Vision) reviewers must enforce.
- Major subsystems are dropped from the tree: `src/qual/docindex/service.py`, `src/qual/retrieval/service.py`, `src/qual/exporting/service.py`, `src/qual/webconsole/static/webconsole.js`, and the corresponding tests such as `tests/unit/test_diff_preview.py` are deleted. This eliminates retrieval, export, and web-console functionality that ROADMAP Milestones 1 & 5 and Product Vision capabilities 2/4/5 require, so the described “diff-preview metadata” tweak is neither testable nor shippable.
- `scripts/scope-check.sh:32-36` now whitelists `THREAD_PACKET.md`, `HANDOFF_COMMANDS*.md`, and the scope script itself unconditionally, bypassing the `SCOPE_ALLOW_SHARED` guard that AGENTS/INTEGRATION rely on to keep shared files protected. This change effectively disables the shared-file enforcement reviewers must trust.
- The handoff packet is inaccurate: `THREAD_PACKET.md:45-48` lists only three files, yet the branch actually edits/deletes >100 files including integrator-locked `README.md` and the governance specs above. The Feature→Review packet leaves “Scope goal,” “Roadmap item(s) affected,” and “Vision capability affected” blank or “pending,” violating `INTEGRATION.md:27-36`, and it incorrectly asserts “Shared/integrator-locked edits: NO.”

## Missing handoff fields
- Scope goal (left blank in the Feature→Review packet)
- Roadmap item(s) affected (marked “pending” instead of citing `ROADMAP.md`)
- Vision capability affected (marked “pending” instead of citing `PRODUCT_VISION.md`)
- Accurate files-changed list matching the real diff

## Required fixes before re-review
1. Restore the integrator-owned and governance documents (`README.md`, `AGENTS.md`, `ROADMAP.md`, `PRODUCT_VISION.md`, the full `INTEGRATION.md` content, etc.) and keep future edits out of these files unless an approved cross-lane plan explicitly calls for them.
2. Restore the removed engine subsystems and tests (`src/qual/docindex/service.py`, `src/qual/retrieval/service.py`, `src/qual/exporting/service.py`, `src/qual/webconsole/**`, `tests/unit/test_diff_preview.py`, and other deleted specs). Limit the branch scope to the declared lane-owned areas (`src/qual/commands/**`) or obtain explicit approval for any shared/integrator-locked edits.
3. Revert the unconditional allowlist in `scripts/scope-check.sh` so shared documents remain protected unless `SCOPE_ALLOW_SHARED=1` is set with explicit approval.
4. Rebuild the handoff packet with the actual scope goal, the concrete ROADMAP milestone and PRODUCT_VISION capability touched, the true list of files changed, and an honest ownership note acknowledging any shared or integrator-owned edits.

## If approved
Not applicable (changes are not approved).