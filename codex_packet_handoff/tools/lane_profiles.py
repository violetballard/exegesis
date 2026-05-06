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
    "feat-ocr-import": {
        "scope_goal": "Disabled future lane for Markdown-direct and OCR-backed typed import specs.",
        "priority_summary": "Disabled OCR import lane.",
        "priority_outcomes": [
            "Keep Markdown import direct without OCR.",
            "Specify non-Markdown OCR normalization into editable Markdown.",
            "Preserve OCR provenance for audit, metadata extraction, and RAG indexing.",
        ],
        "definition_of_done": [
            "Supported import formats are specified.",
            "Online and local OCR model targets are specified.",
            "OCR provenance fields are specified.",
            "No runtime OCR behavior is active until the lane is enabled.",
        ],
        "do_not_spend_time_on": [
            "Runtime OCR implementation before explicit activation.",
            "Shell import filtering behavior before explicit activation.",
            "RAG indexing before normalized import exists.",
        ],
        "risk": "MEDIUM",
        "roadmap_items": ["ROADMAP.md: Milestone 6: OCR import"],
        "vision_capabilities": ["2. Retrieval-first context handling", "6. Auditable state and workflow"],
        "routing_provider_impact": "None while disabled.",
    },
    "feat-literature-import": {
        "scope_goal": "Disabled future lane for literature import metadata extraction and editing specs.",
        "priority_summary": "Disabled literature import lane.",
        "priority_outcomes": [
            "Treat literature as an import type selected in the import modal.",
            "Specify metadata extraction for Markdown and OCR-derived literature.",
            "Keep detected metadata editable before save and later in the inspector.",
        ],
        "definition_of_done": [
            "Literature metadata fields are specified.",
            "Deterministic and model-assisted extraction order is specified.",
            "Metadata approval and inspector editing flows are specified.",
            "No runtime metadata extraction behavior is active until the lane is enabled.",
        ],
        "do_not_spend_time_on": [
            "Runtime metadata extraction before explicit activation.",
            "Separate literature import UI outside the typed import modal.",
            "Inventing metadata values without editable uncertainty.",
        ],
        "risk": "MEDIUM",
        "roadmap_items": ["ROADMAP.md: Milestone 7: Literature import"],
        "vision_capabilities": ["2. Retrieval-first context handling", "6. Auditable state and workflow"],
        "routing_provider_impact": "None while disabled.",
    },
    "feat-rag-index": {
        "scope_goal": "Disabled future lane for Markdown-aware chunking, embeddings, and additive vector retrieval specs.",
        "priority_summary": "Disabled RAG indexing lane.",
        "priority_outcomes": [
            "Specify chunk records over normalized Markdown.",
            "Keep FTS as the retrieval baseline while vector retrieval is additive.",
            "Specify online Mistral and local Qwen embedding targets.",
        ],
        "definition_of_done": [
            "Chunking defaults and metadata are specified.",
            "Embedding targets are specified.",
            "FTS-plus-vector retrieval behavior is specified.",
            "No runtime RAG behavior is active until the lane is enabled.",
        ],
        "do_not_spend_time_on": [
            "Runtime vector indexing before explicit activation.",
            "Replacing the current FTS-first retrieval path.",
            "RAG UI behavior before retrieval contracts are stable.",
        ],
        "risk": "MEDIUM",
        "roadmap_items": ["ROADMAP.md: Milestone 8: RAG indexing and retrieval"],
        "vision_capabilities": ["2. Retrieval-first context handling", "6. Auditable state and workflow"],
        "routing_provider_impact": "None while disabled.",
    },
    "feat-qual-coding": {
        "scope_goal": "Disabled future lane for basic qualitative coding, code folders, and code-focused inspection specs.",
        "priority_summary": "Disabled qualitative coding lane.",
        "priority_outcomes": [
            "Specify one-code selected-text highlighting.",
            "Specify project/browser folder semantics for document folders and parent codes.",
            "Specify code inspector and code-focused document views with frequencies and appearances.",
        ],
        "definition_of_done": [
            "Code project/database model is specified.",
            "Folder and parent-code drag-and-drop semantics are specified.",
            "Inspector and code view contracts are specified.",
            "No runtime coding behavior is active until the lane is enabled.",
        ],
        "do_not_spend_time_on": [
            "Runtime coding implementation before explicit activation.",
            "Multi-level code hierarchy beyond one parent level for MVP.",
            "Full qualitative analysis dashboards beyond the code view contract.",
        ],
        "risk": "MEDIUM",
        "roadmap_items": ["ROADMAP.md: Milestone 9: Basic qualitative coding"],
        "vision_capabilities": ["2. Retrieval-first context handling", "6. Auditable state and workflow"],
        "routing_provider_impact": "None while disabled.",
    },
    "feat-editor-basics": {
        "scope_goal": "Disabled future lane for copy, paste, undo, and redo editor primitive specs.",
        "priority_summary": "Disabled editor basics lane.",
        "priority_outcomes": [
            "Specify copy and paste behavior over the document editor.",
            "Specify undo and redo behavior over document edits.",
            "Specify shortcut and command-palette coverage for editor basics.",
        ],
        "definition_of_done": [
            "Copy/paste/undo/redo contracts are specified.",
            "Shortcut row behavior is specified.",
            "No runtime editor basics behavior is active until the lane is enabled.",
        ],
        "do_not_spend_time_on": [
            "Runtime editor implementation before explicit activation.",
            "Project taxonomy or coding behavior.",
            "WYSIWYG editing surfaces.",
        ],
        "risk": "LOW",
        "roadmap_items": ["ROADMAP.md: Milestone 10: Editor basics"],
        "vision_capabilities": ["1. Writer-first workspace"],
        "routing_provider_impact": "None while disabled.",
    },
    "feat-citations": {
        "scope_goal": "Disabled future lane for Pandoc-compatible citation insertion and literature-link rendering specs.",
        "priority_summary": "Disabled citation support lane.",
        "priority_outcomes": [
            "Specify manual literature citation insertion with optional locators.",
            "Specify LLM-used literature citation requirements.",
            "Specify Pandoc-compatible storage and document-pane link rendering.",
        ],
        "definition_of_done": [
            "Citation storage/rendering contract is specified.",
            "Manual and model-used citation behavior is specified.",
            "Document top-row placement is specified.",
            "No runtime citation behavior is active until the lane is enabled.",
        ],
        "do_not_spend_time_on": [
            "Runtime citation insertion before explicit activation.",
            "Export/reference-list generation, which belongs to feat-export.",
            "Non-literature citation systems before literature records exist.",
        ],
        "risk": "MEDIUM",
        "roadmap_items": ["ROADMAP.md: Milestone 11: Citation support"],
        "vision_capabilities": ["6. Auditable state and workflow"],
        "routing_provider_impact": "None while disabled.",
    },
    "feat-export": {
        "scope_goal": "Disabled future lane for raw Markdown, APA PDF, APA DOCX, and CSL/Pandoc export specs.",
        "priority_summary": "Disabled export support lane.",
        "priority_outcomes": [
            "Specify raw Markdown, PDF, and DOCX export behavior.",
            "Specify APA identity metadata capture and editing.",
            "Specify CSL/Pandoc scaffolding for future citation styles.",
        ],
        "definition_of_done": [
            "Export format contract is specified.",
            "APA metadata and reference-list requirements are specified.",
            "Export modal behavior is specified.",
            "No runtime export behavior is active until the lane is enabled.",
        ],
        "do_not_spend_time_on": [
            "Runtime Pandoc export before explicit activation.",
            "Citation insertion behavior, which belongs to feat-citations.",
            "Future styles beyond the CSL/Pandoc extension scaffold.",
        ],
        "risk": "MEDIUM",
        "roadmap_items": ["ROADMAP.md: Milestone 12: Export support"],
        "vision_capabilities": ["1. Writer-first workspace", "6. Auditable state and workflow"],
        "routing_provider_impact": "None while disabled.",
    },
    "feat-zotero-import": {
        "scope_goal": "Disabled future lane for Zotero literature import, auth, metadata, and attached-file pipeline specs.",
        "priority_summary": "Disabled Zotero import lane.",
        "priority_outcomes": [
            "Specify Zotero as a literature import source.",
            "Specify browser/login or API-key workflow and secure credential storage.",
            "Specify metadata and attached-file import through the literature/OCR pipeline.",
        ],
        "definition_of_done": [
            "Zotero import/auth contract is specified.",
            "Zotero metadata mapping is specified.",
            "Attached-file pipeline behavior is specified.",
            "No runtime Zotero behavior is active until the lane is enabled.",
        ],
        "do_not_spend_time_on": [
            "Runtime Zotero API integration before explicit activation.",
            "Bypassing the literature/OCR import pipeline.",
            "Reference-manager sync beyond import.",
        ],
        "risk": "MEDIUM",
        "roadmap_items": ["ROADMAP.md: Milestone 13: Zotero import"],
        "vision_capabilities": ["2. Retrieval-first context handling", "6. Auditable state and workflow"],
        "routing_provider_impact": "None while disabled.",
    },
    "feat-formatting-bar": {
        "scope_goal": "Disabled future lane for Markdown formatting bar and formatting shortcut specs.",
        "priority_summary": "Disabled formatting bar lane.",
        "priority_outcomes": [
            "Specify basic formatting controls for bold, italic, underline where supported, and headings.",
            "Specify direct Markdown syntax insertion/wrapping.",
            "Specify semantic heading preference for export and retrieval compatibility.",
        ],
        "definition_of_done": [
            "Formatting bar contract is specified.",
            "Formatting shortcuts and command-palette entries are specified.",
            "No runtime formatting behavior is active until the lane is enabled.",
        ],
        "do_not_spend_time_on": [
            "Runtime formatting bar implementation before explicit activation.",
            "WYSIWYG state models.",
            "Manual heading styling that bypasses Markdown headings.",
        ],
        "risk": "LOW",
        "roadmap_items": ["ROADMAP.md: Milestone 14: Formatting bar"],
        "vision_capabilities": ["1. Writer-first workspace"],
        "routing_provider_impact": "None while disabled.",
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
