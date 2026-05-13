"""Stable command compatibility surface for the CLI-first MVP loop."""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import asdict

from src.qual.commands.catalog import *  # noqa: F401,F403
from src.qual.commands.catalog import (
    command_demo_readiness_validate_ordered_script,
    command_demo_readiness_validate_script,
)
from src.qual.commands.canonical import *  # noqa: F401,F403
from src.qual.commands.canonical import (
    canonical_command_command_surface_payload,
    canonical_command_demo_loop_payload,
    canonical_command_demo_loop_smoke_payload,
    canonical_command_exact_action_route_payload,
    canonical_command_execution_plan_payload,
    canonical_command_handler_trust_gate_payload,
    canonical_command_handler_trusted_demo_path_payload,
    canonical_command_persist_continue_payload,
    canonical_command_readiness_handoff_packet_payload,
    canonical_command_readiness_command_audit_payload,
    canonical_command_readiness_cli_smoke_lines,
    canonical_command_readiness_command_progress_payload,
    canonical_command_readiness_cli_entrypoint_seal_payload,
    canonical_command_readiness_fingerprint,
    canonical_command_readiness_handoff_command_progress_payload,
    canonical_command_readiness_handoff_next_action_payload,
    canonical_command_readiness_next_status_payload,
    canonical_command_readiness_remaining_action_payload,
    canonical_command_readiness_required_gate_commands,
    canonical_command_readiness_seal,
    canonical_command_readiness_snapshot_payload,
    canonical_command_readiness_step_seal_payload,
    canonical_command_readiness_status_for_flow_step,
    canonical_command_retrieval_context_payload,
)
from src.qual.commands.diff_preview import (
    DiffPreviewInput,
    DiffPreviewResult,
    PatchReviewActionRoute,
    PatchReviewActionRouteValidation,
    PatchReviewActionResolution,
    PatchReviewActionResolutionSmokeContract,
    PatchReviewCommandStatus,
    PatchReviewCommandStatusPayload,
    PatchReviewCommandContract,
    PatchReviewCommandSmokeContract,
    PatchReviewDecision,
    PatchReviewReadinessContract,
    build_patch_review_command_contract,
    build_patch_review_command_smoke_contract,
    build_patch_review_action_resolution_smoke_contract,
    build_patch_review_action_route_lookup,
    build_patch_review_action_routes,
    build_patch_review_action_compatibility_aliases,
    build_diff_preview_result,
    build_patch_review_readiness_contract,
    build_patch_review_command_status_payload,
    build_patch_review_command_status,
    build_patch_review_decision,
    run_patch_review_action_route_lookup_json,
    run_patch_review_action_routes,
    run_patch_review_action_routes_json,
    run_patch_review_action_resolution,
    run_patch_review_action_resolution_json,
    run_patch_review_action_resolution_smoke_json,
    run_patch_review_command_status,
    run_patch_review_command_status_json,
    run_patch_review_command_contract,
    run_patch_review_command_contract_json,
    run_patch_review_command_smoke_contract,
    run_patch_review_command_smoke_contract_json,
    run_patch_review_decision,
    run_patch_review_readiness_contract,
    run_patch_review_readiness_contract_json,
    run_patch_review_action_route_validation,
    run_patch_review_action_route_validation_json,
    run_diff_preview,
    resolve_patch_review_action,
    validate_patch_review_action_routes,
    validate_patch_review_command_contract,
)

def build_mvp_demo_command_surface_payload(
    smoke_argvs: Sequence[Sequence[str] | str] = (),
) -> dict[str, object]:
    """Return the deterministic package-level contract for the MVP demo loop."""
    demo_loop = canonical_command_demo_loop_payload()
    command_surface = canonical_command_command_surface_payload()
    smoke_contract = canonical_command_demo_loop_smoke_payload()
    patch_review_contract = build_patch_review_command_contract()
    handoff_packet = canonical_command_readiness_handoff_packet_payload()
    command_readiness_audit = canonical_command_readiness_command_audit_payload()
    patch_review_route_validation = build_patch_review_route_validation_payload()
    patch_review_readiness_smoke = build_patch_review_readiness_smoke_payload()
    patch_review_action_resolution_smoke = build_patch_review_action_resolution_smoke_payload()
    readiness_seal = canonical_command_readiness_seal()
    readiness_fingerprint = canonical_command_readiness_fingerprint()
    smoke_gate = build_mvp_demo_smoke_gate_payload(demo_loop)
    trusted_command_contract = build_mvp_demo_trusted_command_contract_payload(demo_loop)
    handler_trusted_demo_path = canonical_command_handler_trusted_demo_path_payload()
    readiness_gate = build_mvp_demo_command_surface_readiness_gate_payload(
        demo_loop_ready=bool(demo_loop["is_ready"]),
        smoke_gate=smoke_gate,
        trusted_command_contract=trusted_command_contract,
        handler_trusted_demo_path=handler_trusted_demo_path,
        command_readiness_audit_complete=bool(command_readiness_audit["is_complete"]),
        patch_review_contract_ready=patch_review_contract.ready,
        patch_review_route_validation_ready=bool(patch_review_route_validation["is_valid"]),
        patch_review_readiness_smoke_ready=bool(patch_review_readiness_smoke["ready"]),
        patch_review_action_resolution_smoke_ready=bool(
            patch_review_action_resolution_smoke["ready"]
        ),
    )
    return {
        "is_ready": readiness_gate["is_ready"],
        "issues": readiness_gate["issues"],
        "readiness_gate": readiness_gate,
        "readiness_seal": asdict(readiness_seal),
        "readiness_fingerprint": asdict(readiness_fingerprint),
        "readiness_step_seals": canonical_command_readiness_step_seal_payload(),
        "readiness_cli_entrypoint_seals": (
            canonical_command_readiness_cli_entrypoint_seal_payload()
        ),
        "handoff_packet": handoff_packet,
        "command_readiness_audit": command_readiness_audit,
        "demo_loop": demo_loop,
        "entrypoint_shims": command_surface["entrypoint_shims"],
        "compatibility_invocations": command_cli_compatibility_invocation_payloads(),
        "execution_plan": canonical_command_execution_plan_payload(),
        "retrieval_context": canonical_command_retrieval_context_payload(),
        "patch_review": asdict(patch_review_contract),
        "patch_review_route_validation": patch_review_route_validation,
        "patch_review_readiness_smoke": patch_review_readiness_smoke,
        "patch_review_action_resolution_smoke": patch_review_action_resolution_smoke,
        "persist_continue": canonical_command_persist_continue_payload(),
        "demo_path_commands": build_mvp_demo_path_command_payload(demo_loop),
        "demo_path_command_sequence": build_mvp_demo_command_sequence_payload(
            demo_loop,
            smoke_contract,
        ),
        "demo_path_command_smoke_matrix": build_mvp_demo_command_smoke_matrix_payload(
            demo_loop,
            smoke_contract,
        ),
        "demo_path_step_surface": command_mvp_demo_step_surface_payload(),
        "trusted_command_contract": trusted_command_contract,
        "handler_trusted_demo_path": handler_trusted_demo_path,
        "smoke_gate": smoke_gate,
        "readiness_snapshot": canonical_command_readiness_snapshot_payload(smoke_argvs),
        "readiness_checkpoint": build_mvp_demo_readiness_checkpoint_payload(
            smoke_argvs
        ),
        "next_step": build_mvp_demo_next_step_payload(smoke_argvs),
        "resume_packet": build_mvp_demo_resume_packet_payload(smoke_argvs),
        "resume_script": build_mvp_demo_resume_script_payload(smoke_argvs),
        "handoff_progress": build_mvp_demo_cli_handoff_progress_payload(smoke_argvs),
        "next_command": canonical_command_readiness_next_status_payload(smoke_argvs),
        "smoke_contract": smoke_contract,
        "smoke_command_lines": canonical_command_readiness_cli_smoke_lines(),
        "smoke_transcript": build_mvp_demo_cli_smoke_transcript_payload(smoke_argvs),
    }


def run_mvp_demo_command_surface_json() -> str:
    """Return the package-level MVP demo command contract as stable JSON."""
    return json.dumps(
        build_mvp_demo_command_surface_payload(),
        sort_keys=True,
        separators=(",", ":"),
    )


def build_mvp_demo_command_surface_readiness_gate_payload(
    *,
    demo_loop_ready: bool,
    smoke_gate: dict[str, object],
    trusted_command_contract: dict[str, object],
    handler_trusted_demo_path: dict[str, object],
    command_readiness_audit_complete: bool,
    patch_review_contract_ready: bool,
    patch_review_route_validation_ready: bool,
    patch_review_readiness_smoke_ready: bool,
    patch_review_action_resolution_smoke_ready: bool,
) -> dict[str, object]:
    """Return the aggregate gate for trusting the package-level command contract."""
    component_status = {
        "demo_loop": demo_loop_ready,
        "smoke_gate": bool(smoke_gate["is_complete"]),
        "trusted_command_contract": bool(trusted_command_contract["is_trusted"]),
        "handler_trusted_demo_path": bool(handler_trusted_demo_path["is_complete"]),
        "command_readiness_audit": command_readiness_audit_complete,
        "patch_review_contract": patch_review_contract_ready,
        "patch_review_route_validation": patch_review_route_validation_ready,
        "patch_review_readiness_smoke": patch_review_readiness_smoke_ready,
        "patch_review_action_resolution_smoke": patch_review_action_resolution_smoke_ready,
    }
    issues = tuple(
        f"{component} not ready"
        for component, ready in component_status.items()
        if not ready
    )
    return {
        "is_ready": not issues,
        "issues": issues,
        "component_status": tuple(component_status.items()),
        "command_lines_match": smoke_gate["command_lines_match"],
        "smoke_gate_ordered": smoke_gate["is_ordered"],
        "untrusted_commands": trusted_command_contract["untrusted_commands"],
        "missing_handler_engine_actions": handler_trusted_demo_path["missing_engine_actions"],
    }


def build_mvp_demo_path_command_payload(
    demo_loop: dict[str, object] | None = None,
) -> tuple[dict[str, object], ...]:
    """Return demo-path steps mapped to the commands reviewers can smoke-test."""
    loop = demo_loop or canonical_command_demo_loop_payload()
    steps = tuple(loop["demo_path_steps"])
    command_lines = tuple(loop["command_lines"])
    smoke_argvs = tuple(loop["smoke_argvs"])
    action_lookup = dict(loop["action_lookup_table"])
    exact_action_argv_lookup = dict(
        zip(
            tuple(loop["engine_actions"]),
            tuple(loop["exact_action_argvs"]),
            strict=True,
        )
    )
    trusted_commands = {
        str(entry["command"]): entry
        for entry in canonical_command_handler_trusted_demo_path_payload()["commands"]
    }
    entries: list[dict[str, object]] = []
    for step, command_line, smoke_argv in zip(
        steps,
        command_lines,
        smoke_argvs,
        strict=True,
    ):
        command = smoke_argv[0]
        trusted_command = trusted_commands[command]
        entries.append(
            {
                "demo_path_step": step,
                "command": command,
                "command_line": command_line,
                "smoke_argv": smoke_argv,
                "engine_actions": action_lookup[step],
                "exact_action_argvs": tuple(
                    exact_action_argv_lookup[action] for action in action_lookup[step]
                ),
                "handler": trusted_command["handler"],
                "delegated_to": trusted_command["delegated_to"],
                "engine_delegated_to": trusted_command["engine_delegated_to"],
                "is_trusted": trusted_command["is_trusted"],
            }
        )
    return tuple(entries)


def build_mvp_demo_command_sequence_payload(
    demo_loop: dict[str, object] | None = None,
    smoke_contract: dict[str, object] | None = None,
) -> tuple[dict[str, object], ...]:
    """Return the ordered command sequence smoke runners should execute."""
    loop = demo_loop or canonical_command_demo_loop_payload()
    smoke = smoke_contract or canonical_command_demo_loop_smoke_payload()
    command_lookup = {
        str(entry["demo_path_step"]): entry
        for entry in build_mvp_demo_path_command_payload(loop)
    }
    entries: list[dict[str, object]] = []
    for smoke_entry in smoke["entries"]:
        demo_path_step = str(smoke_entry["demo_path_step"])
        command_entry = command_lookup[demo_path_step]
        entries.append(
            {
                "ordinal": smoke_entry["ordinal"],
                "flow_step": smoke_entry["flow_step"],
                "demo_path_step": demo_path_step,
                "command": command_entry["command"],
                "command_line": command_entry["command_line"],
                "smoke_argv": command_entry["smoke_argv"],
                "engine_actions": command_entry["engine_actions"],
                "exact_action_argvs": command_entry["exact_action_argvs"],
                "exact_action_lines": smoke_entry["exact_action_lines"],
                "handler": command_entry["handler"],
                "delegated_to": command_entry["delegated_to"],
                "engine_delegated_to": command_entry["engine_delegated_to"],
                "is_trusted": command_entry["is_trusted"],
                "smoke_ready": smoke_entry["ready"],
            }
        )
    return tuple(entries)


def build_mvp_demo_command_smoke_matrix_payload(
    demo_loop: dict[str, object] | None = None,
    smoke_contract: dict[str, object] | None = None,
) -> tuple[dict[str, object], ...]:
    """Return command-by-command smoke checks for the canonical demo path."""
    return tuple(
        {
            "ordinal": entry["ordinal"],
            "flow_step": entry["flow_step"],
            "demo_path_step": entry["demo_path_step"],
            "command": entry["command"],
            "command_line": entry["command_line"],
            "smoke_argv": entry["smoke_argv"],
            "engine_actions": entry["engine_actions"],
            "exact_action_lines": entry["exact_action_lines"],
            "handler": entry["handler"],
            "delegated_to": entry["delegated_to"],
            "engine_delegated_to": entry["engine_delegated_to"],
            "is_smoke_ready": bool(entry["smoke_ready"]),
            "is_handler_trusted": bool(entry["is_trusted"]),
            "is_trusted_demo_step": bool(entry["smoke_ready"])
            and bool(entry["is_trusted"]),
        }
        for entry in build_mvp_demo_command_sequence_payload(demo_loop, smoke_contract)
    )


def run_mvp_demo_command_smoke_matrix_json() -> str:
    """Return stable JSON for command-by-command MVP demo smoke checks."""
    return json.dumps(
        build_mvp_demo_command_smoke_matrix_payload(),
        sort_keys=True,
        separators=(",", ":"),
    )


def run_mvp_demo_path_command_json() -> str:
    """Return demo-path command audit data as stable JSON."""
    return json.dumps(
        build_mvp_demo_path_command_payload(),
        sort_keys=True,
        separators=(",", ":"),
    )


def build_mvp_demo_readiness_checkpoint_payload(
    smoke_argvs: Sequence[Sequence[str] | str] = (),
) -> dict[str, object]:
    """Return deterministic progress data for resuming the MVP demo command loop."""

    progress = canonical_command_readiness_handoff_command_progress_payload(smoke_argvs)
    next_action = canonical_command_readiness_handoff_next_action_payload(smoke_argvs)
    remaining_actions = canonical_command_readiness_remaining_action_payload(smoke_argvs)
    return {
        "is_complete": bool(progress["is_complete"])
        and bool(next_action["is_complete"])
        and bool(remaining_actions["is_complete"]),
        "progress": progress,
        "next_action": next_action,
        "remaining_actions": remaining_actions,
    }


def run_mvp_demo_readiness_checkpoint_json() -> str:
    """Return stable JSON for the resumable MVP demo readiness checkpoint."""
    return json.dumps(
        build_mvp_demo_readiness_checkpoint_payload(),
        sort_keys=True,
        separators=(",", ":"),
    )


def build_mvp_demo_next_step_payload(
    smoke_argvs: Sequence[Sequence[str] | str] = (),
) -> dict[str, object]:
    """Return the next exact command/action for resuming the MVP demo loop."""

    checkpoint = build_mvp_demo_readiness_checkpoint_payload(smoke_argvs)
    next_status = canonical_command_readiness_next_status_payload(smoke_argvs)
    return {
        "is_complete": checkpoint["is_complete"],
        "next_command": next_status,
        "next_action": checkpoint["next_action"],
        "remaining_actions": checkpoint["remaining_actions"],
    }


def build_mvp_demo_resume_packet_payload(
    smoke_argvs: Sequence[Sequence[str] | str] = (),
) -> dict[str, object]:
    """Return the trusted command packet for resuming a partial MVP demo loop."""

    command_checkpoint = canonical_command_readiness_command_progress_payload(smoke_argvs)
    exact_action_checkpoint = build_mvp_demo_readiness_checkpoint_payload(smoke_argvs)
    if command_checkpoint["is_complete"]:
        next_command = {
            "command": None,
            "flow_step": None,
            "demo_path_step": None,
            "argv": (),
            "command_line": "",
            "engine_actions": (),
            "ready": True,
        }
    else:
        next_status = canonical_command_readiness_status_for_flow_step(
            str(command_checkpoint["next_flow_step"])
        )
        next_command = {
            "command": next_status.command,
            "flow_step": next_status.flow_step,
            "demo_path_step": next_status.demo_path_step,
            "argv": next_status.argv,
            "command_line": next_status.command_line,
            "engine_actions": next_status.engine_actions,
            "ready": next_status.ready,
        }
    next_step = {
        **build_mvp_demo_next_step_payload(smoke_argvs),
        "is_complete": command_checkpoint["is_complete"],
        "next_command": next_command,
    }
    trusted_contract = build_mvp_demo_trusted_command_contract_payload()
    command_readiness = {
        str(entry["command"]): entry
        for entry in trusted_contract["command_readiness"]
    }
    command = next_command["command"]
    trusted_command = command_readiness.get(str(command)) if command is not None else None
    compatibility_invocations = tuple(
        entry
        for entry in command_cli_compatibility_invocation_payloads()
        if entry["canonical_name"] == command
    )
    invalid_argv = tuple(command_checkpoint["invalid_argv"])
    exact_action_invalid_argv = tuple(
        exact_action_checkpoint["remaining_actions"]["invalid_argv"]
    )
    return {
        "is_complete": command_checkpoint["is_complete"],
        "is_ready": bool(next_command["ready"])
        and (trusted_command is None or bool(trusted_command["is_trusted"]))
        and not invalid_argv
        and not exact_action_invalid_argv,
        "checkpoint": command_checkpoint,
        "exact_action_checkpoint": exact_action_checkpoint,
        "next_step": next_step,
        "trusted_command": trusted_command,
        "compatibility_invocations": compatibility_invocations,
        "invalid_argv": invalid_argv,
        "exact_action_invalid_argv": exact_action_invalid_argv,
    }


def run_mvp_demo_resume_packet_json() -> str:
    """Return stable JSON for resuming the MVP demo command loop."""
    return json.dumps(
        build_mvp_demo_resume_packet_payload(),
        sort_keys=True,
        separators=(",", ":"),
    )


def build_mvp_demo_resume_script_payload(
    smoke_argvs: Sequence[Sequence[str] | str] = (),
) -> dict[str, object]:
    """Return completed and remaining command lines for a resumable smoke run."""

    command_progress = canonical_command_readiness_command_progress_payload(smoke_argvs)
    exact_action_checkpoint = build_mvp_demo_readiness_checkpoint_payload(smoke_argvs)
    next_step = build_mvp_demo_next_step_payload(smoke_argvs)
    entries = tuple(command_progress["entries"])
    return {
        "is_complete": command_progress["is_complete"],
        "exact_actions_complete": exact_action_checkpoint["is_complete"],
        "input_argvs": tuple(
            tuple(argv) if not isinstance(argv, str) else (argv,)
            for argv in smoke_argvs
        ),
        "completed_command_lines": tuple(
            entry["command_line"] for entry in entries if entry["is_covered"]
        ),
        "covered_flow_steps": tuple(
            entry["flow_step"] for entry in entries if entry["is_covered"]
        ),
        "covered_engine_actions": tuple(
            action
            for entry in entries
            if entry["is_covered"]
            for action in tuple(
                engine_action for engine_action, _ in entry["action_lines"]
            )
        ),
        "next_step": next_step,
        "remaining_command_lines": tuple(
            entry["command_line"] for entry in entries if not entry["is_covered"]
        ),
        "remaining_exact_action_lines": tuple(
            exact_action_checkpoint["next_action"]["remaining_exact_action_lines"]
        ),
        "invalid_argv": tuple(command_progress["invalid_argv"]),
        "exact_action_invalid_argv": tuple(
            exact_action_checkpoint["remaining_actions"]["invalid_argv"]
        ),
    }


def run_mvp_demo_resume_script_json() -> str:
    """Return stable JSON for resuming the MVP demo command smoke script."""
    return json.dumps(
        build_mvp_demo_resume_script_payload(),
        sort_keys=True,
        separators=(",", ":"),
    )


def run_mvp_demo_next_step_json() -> str:
    """Return stable JSON for the next resumable MVP demo command/action."""
    return json.dumps(
        build_mvp_demo_next_step_payload(),
        sort_keys=True,
        separators=(",", ":"),
    )


def build_mvp_demo_smoke_gate_payload(
    demo_loop: dict[str, object] | None = None,
) -> dict[str, object]:
    """Return the smoke-test gate for the exact MVP demo command sequence."""
    loop = demo_loop or canonical_command_demo_loop_payload()
    expected_command_lines = tuple(loop["command_lines"])
    smoke_argvs = tuple(loop["smoke_argvs"])
    validation = command_demo_readiness_validate_script(smoke_argvs)
    ordered_validation = command_demo_readiness_validate_ordered_script(smoke_argvs)
    handler_gate = canonical_command_handler_trust_gate_payload()
    handler_demo_path_steps = tuple(handler_gate["demo_path_steps"])
    command_lines_match = validation.command_lines == expected_command_lines
    demo_path_steps_match = handler_demo_path_steps == tuple(loop["demo_path_steps"])
    return {
        "is_complete": (
            validation.is_complete
            and ordered_validation.is_ordered
            and command_lines_match
            and demo_path_steps_match
            and bool(handler_gate["is_complete"])
        ),
        "is_ordered": ordered_validation.is_ordered,
        "command_lines_match": command_lines_match,
        "demo_path_steps_match": demo_path_steps_match,
        "command_lines": validation.command_lines,
        "expected_command_lines": expected_command_lines,
        "handler_demo_path_steps": handler_demo_path_steps,
        "expected_flow_steps": ordered_validation.expected_flow_steps,
        "observed_flow_steps": ordered_validation.observed_flow_steps,
        "order_violations": ordered_validation.order_violations,
        "handler_trust_gate_complete": handler_gate["is_complete"],
        "handler_engine_delegations": handler_gate["engine_delegations"],
        "thin_handler_violations": handler_gate["thin_handler_violations"],
        "covered_flow_steps": validation.covered_flow_steps,
        "missing_flow_steps": validation.missing_flow_steps,
        "covered_engine_actions": validation.covered_engine_actions,
        "missing_engine_actions": validation.missing_engine_actions,
        "invalid_argv": validation.invalid_argv,
    }


def run_mvp_demo_smoke_gate_json() -> str:
    """Return stable JSON for the exact MVP demo command smoke gate."""
    return json.dumps(
        build_mvp_demo_smoke_gate_payload(),
        sort_keys=True,
        separators=(",", ":"),
    )


def build_mvp_demo_cli_handoff_payload(
    smoke_argvs: Sequence[Sequence[str] | str] = (),
) -> dict[str, object]:
    """Return the reviewer-facing CLI smoke handoff for the MVP demo path."""
    demo_loop = canonical_command_demo_loop_payload()
    handoff_packet = canonical_command_readiness_handoff_packet_payload()
    required_gate_commands = tuple(
        asdict(command) for command in canonical_command_readiness_required_gate_commands()
    )
    readiness_seal = canonical_command_readiness_seal()
    readiness_fingerprint = canonical_command_readiness_fingerprint()
    smoke_gate = build_mvp_demo_smoke_gate_payload(demo_loop)
    smoke_matrix = build_mvp_demo_command_smoke_matrix_payload(demo_loop)
    checkpoint = build_mvp_demo_readiness_checkpoint_payload(smoke_argvs)
    trusted_steps = tuple(
        entry
        for entry in smoke_matrix
        if bool(entry["is_smoke_ready"])
        and bool(entry["is_handler_trusted"])
        and bool(entry["is_trusted_demo_step"])
    )
    return {
        "is_ready": bool(smoke_gate["is_complete"])
        and len(trusted_steps) == len(smoke_matrix),
        "handoff_packet": handoff_packet,
        "roadmap_items": tuple(handoff_packet["roadmap_items"]),
        "vision_capabilities": tuple(handoff_packet["vision_capabilities"]),
        "routing_provider_impact": handoff_packet["routing_provider_impact"],
        "risks_blockers": tuple(handoff_packet["risks_blockers"]),
        "readiness_seal": asdict(readiness_seal),
        "readiness_fingerprint": asdict(readiness_fingerprint),
        "readiness_step_seals": canonical_command_readiness_step_seal_payload(),
        "readiness_cli_entrypoint_seals": (
            canonical_command_readiness_cli_entrypoint_seal_payload()
        ),
        "required_gate_commands": required_gate_commands,
        "required_gate_command_lines": tuple(
            command["command"] for command in required_gate_commands
        ),
        "canonical_demo_path_step_advanced": (
            "open project/document -> retrieve relevant material -> "
            "preview and apply or reject a patch -> persist and continue"
        ),
        "flow_steps": tuple(entry["flow_step"] for entry in smoke_matrix),
        "commands": tuple(entry["command"] for entry in smoke_matrix),
        "command_lines": tuple(entry["command_line"] for entry in smoke_matrix),
        "compatibility_invocations": command_cli_compatibility_invocation_payloads(),
        "smoke_argvs": tuple(entry["smoke_argv"] for entry in smoke_matrix),
        "engine_actions_by_step": tuple(
            (entry["demo_path_step"], entry["engine_actions"])
            for entry in smoke_matrix
        ),
        "exact_action_lines_by_step": tuple(
            (entry["demo_path_step"], entry["exact_action_lines"])
            for entry in smoke_matrix
        ),
        "smoke_gate": smoke_gate,
        "smoke_transcript": build_mvp_demo_cli_smoke_transcript_payload(
            smoke_argvs,
            demo_loop,
            smoke_matrix,
            smoke_gate,
        ),
        "checkpoint": checkpoint,
        "next_step": build_mvp_demo_next_step_payload(smoke_argvs),
        "resume_packet": build_mvp_demo_resume_packet_payload(smoke_argvs),
        "resume_script": build_mvp_demo_resume_script_payload(smoke_argvs),
        "handoff_progress": build_mvp_demo_cli_handoff_progress_payload(smoke_argvs),
    }


def run_mvp_demo_cli_handoff_json() -> str:
    """Return stable JSON for the reviewer-facing MVP demo CLI handoff."""
    return json.dumps(
        build_mvp_demo_cli_handoff_payload(),
        sort_keys=True,
        separators=(",", ":"),
    )


def build_mvp_demo_cli_handoff_progress_payload(
    smoke_argvs: Sequence[Sequence[str] | str] = (),
) -> dict[str, object]:
    """Return compact progress data for deterministic handoff smoke checks."""

    resume_script = build_mvp_demo_resume_script_payload(smoke_argvs)
    next_step = resume_script["next_step"]
    next_command = next_step["next_command"]
    trusted_contract = build_mvp_demo_trusted_command_contract_payload()
    remaining_command_lines = tuple(resume_script["remaining_command_lines"])
    remaining_exact_action_lines = tuple(resume_script["remaining_exact_action_lines"])
    return {
        "is_ready": bool(trusted_contract["is_trusted"])
        and not tuple(resume_script["invalid_argv"])
        and not tuple(resume_script["exact_action_invalid_argv"]),
        "is_complete": bool(resume_script["is_complete"]),
        "exact_actions_complete": bool(resume_script["exact_actions_complete"]),
        "completed_command_count": len(tuple(resume_script["completed_command_lines"])),
        "remaining_command_count": len(remaining_command_lines),
        "covered_flow_steps": tuple(resume_script["covered_flow_steps"]),
        "covered_engine_actions": tuple(resume_script["covered_engine_actions"]),
        "remaining_command_lines": remaining_command_lines,
        "remaining_exact_action_lines": remaining_exact_action_lines,
        "next_command": next_command,
        "next_command_line": next_command["command_line"],
        "next_engine_actions": tuple(next_command["engine_actions"]),
        "trusted_commands": tuple(trusted_contract["commands"]),
        "untrusted_commands": tuple(trusted_contract["untrusted_commands"]),
        "invalid_argv": tuple(resume_script["invalid_argv"]),
        "exact_action_invalid_argv": tuple(resume_script["exact_action_invalid_argv"]),
    }


def run_mvp_demo_cli_handoff_progress_json() -> str:
    """Return stable JSON for deterministic handoff smoke progress."""
    return json.dumps(
        build_mvp_demo_cli_handoff_progress_payload(),
        sort_keys=True,
        separators=(",", ":"),
    )


def build_mvp_demo_cli_smoke_transcript_payload(
    smoke_argvs: Sequence[Sequence[str] | str] = (),
    demo_loop: dict[str, object] | None = None,
    smoke_matrix: tuple[dict[str, object], ...] | None = None,
    smoke_gate: dict[str, object] | None = None,
) -> dict[str, object]:
    """Return the exact CLI transcript reviewers can replay for the MVP loop."""

    loop = demo_loop or canonical_command_demo_loop_payload()
    matrix = smoke_matrix or build_mvp_demo_command_smoke_matrix_payload(loop)
    gate = smoke_gate or build_mvp_demo_smoke_gate_payload(loop)
    checkpoint = build_mvp_demo_readiness_checkpoint_payload(smoke_argvs)
    transcript = tuple(
        {
            "ordinal": entry["ordinal"],
            "flow_step": entry["flow_step"],
            "demo_path_step": entry["demo_path_step"],
            "command": entry["command"],
            "command_line": entry["command_line"],
            "engine_actions": entry["engine_actions"],
            "exact_action_lines": entry["exact_action_lines"],
            "is_smoke_ready": bool(entry["is_smoke_ready"]),
            "is_handler_trusted": bool(entry["is_handler_trusted"]),
        }
        for entry in matrix
    )
    return {
        "is_replayable": bool(gate["is_complete"]),
        "is_complete": bool(checkpoint["is_complete"]),
        "canonical_demo_path_step_advanced": (
            "open project/document -> retrieve relevant material -> "
            "preview and apply or reject a patch -> persist and continue"
        ),
        "command_lines": tuple(entry["command_line"] for entry in transcript),
        "flow_steps": tuple(entry["flow_step"] for entry in transcript),
        "demo_path_steps": tuple(entry["demo_path_step"] for entry in transcript),
        "engine_actions": tuple(
            action
            for entry in transcript
            for action in tuple(entry["engine_actions"])
        ),
        "transcript": transcript,
        "checkpoint": checkpoint,
    }


def run_mvp_demo_cli_smoke_transcript_json() -> str:
    """Return stable JSON for replaying the MVP demo CLI smoke transcript."""
    return json.dumps(
        build_mvp_demo_cli_smoke_transcript_payload(),
        sort_keys=True,
        separators=(",", ":"),
    )


def build_mvp_demo_trusted_command_contract_payload(
    demo_loop: dict[str, object] | None = None,
) -> dict[str, object]:
    """Return a deterministic trust contract for the command sequence."""
    loop = demo_loop or canonical_command_demo_loop_payload()
    sequence = build_mvp_demo_command_sequence_payload(loop)
    smoke_gate = build_mvp_demo_smoke_gate_payload(loop)
    handler_gate = canonical_command_handler_trust_gate_payload()
    command_readiness = tuple(
        {
            "ordinal": entry["ordinal"],
            "flow_step": entry["flow_step"],
            "demo_path_step": entry["demo_path_step"],
            "command": entry["command"],
            "command_line": entry["command_line"],
            "engine_actions": entry["engine_actions"],
            "handler": entry["handler"],
            "delegated_to": entry["delegated_to"],
            "engine_delegated_to": entry["engine_delegated_to"],
            "is_trusted": entry["is_trusted"],
            "smoke_ready": entry["smoke_ready"],
        }
        for entry in sequence
    )
    untrusted_commands = tuple(
        str(entry["command"])
        for entry in command_readiness
        if not bool(entry["is_trusted"]) or not bool(entry["smoke_ready"])
    )
    return {
        "is_trusted": (
            bool(smoke_gate["is_complete"])
            and bool(handler_gate["is_complete"])
            and not untrusted_commands
        ),
        "demo_path_steps": loop["demo_path_steps"],
        "command_lines": loop["command_lines"],
        "commands": tuple(entry["command"] for entry in command_readiness),
        "untrusted_commands": untrusted_commands,
        "command_readiness": command_readiness,
        "smoke_gate_complete": smoke_gate["is_complete"],
        "smoke_gate_ordered": smoke_gate["is_ordered"],
        "handler_trust_gate_complete": handler_gate["is_complete"],
        "thin_handler_violations": handler_gate["thin_handler_violations"],
    }


def run_mvp_demo_trusted_command_contract_json() -> str:
    """Return stable JSON for the trusted MVP demo command contract."""
    return json.dumps(
        build_mvp_demo_trusted_command_contract_payload(),
        sort_keys=True,
        separators=(",", ":"),
    )


def build_patch_review_readiness_smoke_payload() -> dict[str, object]:
    """Return changed/no-change patch-review readiness payloads for smoke checks."""
    changed_payload = DiffPreviewInput(
        "draft text before review\n",
        "revised draft text\n",
    )
    no_change_payload = DiffPreviewInput(
        "unchanged draft text\n",
        "unchanged draft text\n",
    )
    changed = build_patch_review_readiness_contract(changed_payload)
    no_change = build_patch_review_readiness_contract(no_change_payload)
    return {
        "ready": changed.ready and no_change.ready,
        "changed": asdict(changed),
        "no_change": asdict(no_change),
    }


def run_patch_review_readiness_smoke_json() -> str:
    """Return deterministic patch-review readiness smoke data as stable JSON."""
    return json.dumps(
        build_patch_review_readiness_smoke_payload(),
        sort_keys=True,
        separators=(",", ":"),
    )


def build_patch_review_action_resolution_smoke_payload() -> dict[str, object]:
    """Return deterministic patch-review action resolution data for smoke checks."""
    return asdict(build_patch_review_action_resolution_smoke_contract())


def build_patch_review_route_validation_payload() -> dict[str, object]:
    """Return deterministic patch-review route validation data for smoke checks."""
    return asdict(validate_patch_review_command_contract())


def run_patch_review_route_validation_payload_json() -> str:
    """Return package-level patch-review route validation data as JSON."""
    return json.dumps(
        build_patch_review_route_validation_payload(),
        sort_keys=True,
        separators=(",", ":"),
    )


def run_patch_review_action_resolution_smoke_payload_json() -> str:
    """Return package-level patch-review action resolution smoke data as JSON."""
    return json.dumps(
        build_patch_review_action_resolution_smoke_payload(),
        sort_keys=True,
        separators=(",", ":"),
    )


def build_mvp_demo_command_surface_audit_payload() -> dict[str, object]:
    """Return a deterministic audit bundle for command-surface handoff checks."""
    command_surface = canonical_command_command_surface_payload()
    readiness_seal = canonical_command_readiness_seal()
    readiness_fingerprint = canonical_command_readiness_fingerprint()
    return {
        "surface": build_mvp_demo_command_surface_payload(),
        "command_surface": command_surface,
        "readiness_seal": asdict(readiness_seal),
        "readiness_fingerprint": asdict(readiness_fingerprint),
        "readiness_step_seals": canonical_command_readiness_step_seal_payload(),
        "readiness_cli_entrypoint_seals": (
            canonical_command_readiness_cli_entrypoint_seal_payload()
        ),
        "entrypoint_shims": command_surface["entrypoint_shims"],
        "compatibility_invocations": command_cli_compatibility_invocation_payloads(),
        "handler_trust_gate": canonical_command_handler_trust_gate_payload(),
        "handler_trusted_demo_path": canonical_command_handler_trusted_demo_path_payload(),
        "handoff_packet": canonical_command_readiness_handoff_packet_payload(),
        "required_gate_commands": tuple(
            asdict(command) for command in canonical_command_readiness_required_gate_commands()
        ),
        "command_readiness_audit": canonical_command_readiness_command_audit_payload(),
        "exact_action_routes": canonical_command_exact_action_route_payload(),
        "demo_path_commands": build_mvp_demo_path_command_payload(),
        "demo_path_command_sequence": build_mvp_demo_command_sequence_payload(),
        "demo_path_command_smoke_matrix": build_mvp_demo_command_smoke_matrix_payload(),
        "demo_path_step_surface": command_mvp_demo_step_surface_payload(),
        "trusted_command_contract": build_mvp_demo_trusted_command_contract_payload(),
        "cli_handoff": build_mvp_demo_cli_handoff_payload(),
        "smoke_gate": build_mvp_demo_smoke_gate_payload(),
        "readiness_checkpoint": build_mvp_demo_readiness_checkpoint_payload(),
        "next_step": build_mvp_demo_next_step_payload(),
        "resume_packet": build_mvp_demo_resume_packet_payload(),
        "patch_review_route_validation": build_patch_review_route_validation_payload(),
        "patch_review_readiness_smoke": build_patch_review_readiness_smoke_payload(),
        "patch_review_action_resolution_smoke": build_patch_review_action_resolution_smoke_payload(),
    }


def run_mvp_demo_command_surface_audit_json() -> str:
    """Return the MVP demo command-surface audit bundle as stable JSON."""
    return json.dumps(
        build_mvp_demo_command_surface_audit_payload(),
        sort_keys=True,
        separators=(",", ":"),
    )


_PUBLIC_EXPORT_EXCLUSIONS = {
    "DraftingService",
    "Hashable",
    "PurePath",
    "Sequence",
    "T",
    "TypeVar",
    "annotations",
    "asdict",
    "catalog",
    "canonical",
    "dataclass",
    "hashlib",
    "json",
    "lru_cache",
    "os",
    "re",
    "shlex",
}

__all__ = tuple(
    name
    for name in globals()
    if not name.startswith("_") and name not in _PUBLIC_EXPORT_EXCLUSIONS
)
