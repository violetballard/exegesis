#!/usr/bin/env python3
from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List

Json = Dict[str, Any]

ENGINE_MILESTONE_FOCUS = (
    "Close the engine-side Milestone 3 workflow loop before activating any Textual UI lanes."
)

ENGINE_PRIORITY_ORDER = [
    "feat-context-storage",
    "feat-commands",
    "feat-retrieval-fts",
    "feat-engine-runs",
    "feat-a2ui-contract",
]

LANE_PROFILES: Dict[str, Json] = {
    "feat-context-storage": {
        "scope_goal": (
            "Make document, basket, vault, and session state deterministic and recoverable "
            "so the engine-side workflow loop has a trustworthy persistence floor."
        ),
        "priority_summary": "Persistence floor for document, basket, vault, and session state.",
        "priority_outcomes": [
            "Keep document, basket, vault, and session persistence deterministic and recoverable.",
            "Prefer recovery, canonicalization, and auditability over new storage surface area.",
            "Support the engine-side workflow loop without introducing UI-specific state semantics.",
        ],
        "definition_of_done": [
            "Document state persists cleanly.",
            "Basket and context state persist cleanly.",
            "Malformed or partial local state is recovered or quarantined safely.",
            "Engine flows can rely on storage without defensive one-off repair logic.",
        ],
        "do_not_spend_time_on": [
            "UI-facing basket semantics or interaction patterns.",
            "Speculative sync or collaboration features.",
            "Storage abstractions that do not improve determinism or recovery.",
        ],
        "risk": "MEDIUM",
        "roadmap_items": [
            "ROADMAP.md: Milestone 3: Real workflow loop",
            "ROADMAP.md: Milestone 4: Dogfooding readiness",
        ],
        "vision_capabilities": [
            "1. Local-first state and identity",
            "6. Auditable state and workflow",
        ],
        "routing_provider_impact": "None",
    },
    "feat-commands": {
        "scope_goal": (
            "Keep the CLI as a reliable MVP client while the package migration and canonical "
            "engine contract settle."
        ),
        "priority_summary": "Stable command surface for the CLI-first MVP loop.",
        "priority_outcomes": [
            "Keep command behavior deterministic and easy to smoke-test.",
            "Prefer thin command entrypoints over embedded business logic.",
            "Preserve compatibility with the canonical engine contract while UI lanes stay disabled.",
        ],
        "definition_of_done": [
            "Core engine actions are reachable through stable commands.",
            "Command behavior is deterministic and smoke-testable.",
            "Compatibility shims keep old command surfaces working where required.",
            "Command handlers stay thin and delegate real behavior to engine code.",
        ],
        "do_not_spend_time_on": [
            "Fancy CLI UX that does not support the MVP loop.",
            "New command flags that do not help open, retrieve, basket, revise, patch, or save.",
            "Embedding engine behavior directly in command handlers.",
        ],
        "risk": "LOW",
        "roadmap_items": [
            "ROADMAP.md: Milestone 3: Real workflow loop",
            "ROADMAP.md: Milestone 4: Dogfooding readiness",
        ],
        "vision_capabilities": [
            "4. Operator-first control surface",
            "6. Auditable state and workflow",
        ],
        "routing_provider_impact": "None",
    },
    "feat-retrieval-fts": {
        "scope_goal": (
            "Make FTS-first retrieval the trustworthy input path for the engine-side workflow "
            "loop, with deterministic excerpt and provenance payloads."
        ),
        "priority_summary": "Authoritative FTS-first retrieval for engine runs.",
        "priority_outcomes": [
            "Keep SQLite FTS as the primary retrieval path.",
            "Return stable, structured hits suitable for basket promotion and downstream workflow use.",
            "Keep provenance and excerpt payloads deterministic and auditable.",
        ],
        "definition_of_done": [
            "Retrieval is FTS-first by default.",
            "Results are structured and deterministic enough for basket promotion and workflow cards.",
            "Excerpt provenance is stable and auditable.",
            "Retrieval is reachable through the canonical engine surface.",
        ],
        "do_not_spend_time_on": [
            "Over-investing in embeddings or alternate retrieval modes.",
            "UI rendering concerns.",
            "Search features outside the core writing loop.",
        ],
        "risk": "LOW",
        "roadmap_items": [
            "ROADMAP.md: Milestone 3: Real workflow loop",
        ],
        "vision_capabilities": [
            "2. Retrieval-first context handling",
            "6. Auditable state and workflow",
        ],
        "routing_provider_impact": "None",
    },
    "feat-engine-runs": {
        "scope_goal": (
            "Stand up the real engine loop for planning, drafting or revising, patch proposal, "
            "and apply or reject flow through one deterministic app-service surface."
        ),
        "priority_summary": "Close the plan, revise, patch, and apply loop in the engine.",
        "priority_outcomes": [
            "Make the engine run lifecycle deterministic and testable.",
            "Keep patch proposal, apply, reject, and audit behavior coherent.",
            "Provide one explicit engine-side acceptance path for the Milestone 3 loop.",
        ],
        "definition_of_done": [
            "Plan-from-context works through the engine contract.",
            "Revise-selection or draft-from-context works through the engine contract.",
            "Patch proposal shape is stable.",
            "Apply and reject update document state consistently.",
            "One explicit engine-side acceptance flow proves the loop end to end.",
        ],
        "do_not_spend_time_on": [
            "UI-driven workflow behavior.",
            "Speculative orchestration layers before one path is clearly solid.",
            "Multiple alternate run modes before the core loop stands.",
        ],
        "risk": "MEDIUM",
        "roadmap_items": [
            "ROADMAP.md: Milestone 3: Real workflow loop",
            "ROADMAP.md: Milestone 4: Dogfooding readiness",
        ],
        "vision_capabilities": [
            "2. Retrieval-first context handling",
            "3. Patch-first revision workflow",
            "6. Auditable state and workflow",
        ],
        "routing_provider_impact": "Low. Keep provider and routing decisions centralized; no broad routing refactor is in scope.",
    },
    "feat-a2ui-contract": {
        "scope_goal": (
            "Provide just enough shared card, action, and selection contract stability for the "
            "CLI now and the future Textual client later, without letting contract work outrun the engine loop."
        ),
        "priority_summary": "Support the engine loop with stable shared contracts, not UI ambition.",
        "priority_outcomes": [
            "Keep card, action, and selection structures deterministic and versionable.",
            "Support reliable CLI fallback rendering for engine outputs.",
            "Keep rendering choices out of shared engine-facing contracts.",
        ],
        "definition_of_done": [
            "Shared action, card, and selection structures are stable enough for engine outputs.",
            "CLI can consume the same structures that future UI work will consume.",
            "Contract shape does not force UI-specific assumptions into the engine.",
        ],
        "do_not_spend_time_on": [
            "The full final A2UI protocol.",
            "Presentation richness before the engine loop is standing.",
            "Letting contract polish outrun actual workflow behavior.",
        ],
        "risk": "LOW",
        "roadmap_items": [
            "ROADMAP.md: Milestone 3: Real workflow loop",
            "ROADMAP.md: Milestone 4: Dogfooding readiness",
        ],
        "vision_capabilities": [
            "5. Agent-to-UI protocol (A2UI)",
            "4. Operator-first control surface",
        ],
        "routing_provider_impact": "None",
    },
    "feat-console-shell": {
        "scope_goal": "Disabled until the engine-side Milestone 3 loop stands and Textual is intentionally activated.",
        "priority_summary": "Disabled UI lane.",
        "priority_outcomes": [],
        "definition_of_done": [],
        "do_not_spend_time_on": [],
        "risk": "LOW",
        "roadmap_items": ["ROADMAP.md: Milestone 1: Standing shell"],
        "vision_capabilities": ["4. Operator-first control surface"],
        "routing_provider_impact": "None",
    },
    "feat-console-workflow": {
        "scope_goal": "Disabled until the engine-side Milestone 3 loop stands and Textual is intentionally activated.",
        "priority_summary": "Disabled UI lane.",
        "priority_outcomes": [],
        "definition_of_done": [],
        "do_not_spend_time_on": [],
        "risk": "LOW",
        "roadmap_items": ["ROADMAP.md: Milestone 2: Core pane interactions"],
        "vision_capabilities": ["5. Agent-to-UI protocol (A2UI)"],
        "routing_provider_impact": "None",
    },
}


def lane_profile(lane: str) -> Json:
    return deepcopy(LANE_PROFILES.get(lane, {}))


def default_lane_meta(lane: str) -> Json:
    profile = lane_profile(lane)
    return {
        "scope_goal": str(profile.get("scope_goal") or ""),
        "tasks_completed": [],
        "risk": str(profile.get("risk") or "LOW"),
        "roadmap_items": list(profile.get("roadmap_items") or []),
        "vision_capabilities": list(profile.get("vision_capabilities") or []),
        "routing_provider_impact": str(profile.get("routing_provider_impact") or "None"),
        "proposed_readme_patch": "",
        "shared_file_exception": False,
        "kickoff_budget_note": "",
        "approved_exception_note": "",
        "priority_outcomes": list(profile.get("priority_outcomes") or []),
        "definition_of_done": list(profile.get("definition_of_done") or []),
        "do_not_spend_time_on": list(profile.get("do_not_spend_time_on") or []),
    }


def engine_priority_lines() -> List[str]:
    lines: List[str] = []
    for index, lane in enumerate(ENGINE_PRIORITY_ORDER, start=1):
        profile = lane_profile(lane)
        summary = str(profile.get("priority_summary") or "").strip()
        if summary:
            lines.append(f"{index}. `{lane}` - {summary}")
        else:
            lines.append(f"{index}. `{lane}`")
    return lines

