from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass

from src.qual.drafting.service import DraftingService

MAX_DIFF_OUTPUT_CHARS = 20_000
MAX_DIFF_OUTPUT_CHARS_ENV = "QUAL_DIFF_MAX_OUTPUT_CHARS"
IGNORE_TRAILING_WHITESPACE_ENV = "QUAL_DIFF_IGNORE_TRAILING_WHITESPACE"
SUPPRESS_FILE_HEADERS_ENV = "QUAL_DIFF_SUPPRESS_FILE_HEADERS"
INCLUDE_SUMMARY_ENV = "QUAL_DIFF_INCLUDE_SUMMARY"
SUMMARY_ONLY_ENV = "QUAL_DIFF_SUMMARY_ONLY"
INCLUDE_SUMMARY_DETAILS_ENV = "QUAL_DIFF_INCLUDE_SUMMARY_DETAILS"
INCLUDE_OPTIONS_BANNER_ENV = "QUAL_DIFF_INCLUDE_OPTIONS_BANNER"
TRUNCATION_STRATEGY_ENV = "QUAL_DIFF_TRUNCATION_STRATEGY"
STRIP_ANSI_ENV = "QUAL_DIFF_STRIP_ANSI"
CANONICALIZE_INLINE_WHITESPACE_ENV = "QUAL_DIFF_CANONICALIZE_INLINE_WHITESPACE"
IGNORE_CASE_ENV = "QUAL_DIFF_IGNORE_CASE"
IGNORE_EDGE_BLANK_LINES_ENV = "QUAL_DIFF_IGNORE_EDGE_BLANK_LINES"
IGNORE_ALL_BLANK_LINES_ENV = "QUAL_DIFF_IGNORE_ALL_BLANK_LINES"
TRUNCATION_MARKER_ENV = "QUAL_DIFF_TRUNCATION_MARKER"
ANSI_ESCAPE_RE = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")
PATCH_REVIEW_APPLY_ENGINE_ACTION = "ExegesisAppService.apply_patch"
PATCH_REVIEW_REJECT_ENGINE_ACTION = "ExegesisAppService.reject_patch"
PATCH_REVIEW_REVISE_ENGINE_ACTION = "ExegesisAppService.revise_selection"
PATCH_REVIEW_CONTINUE_ENGINE_ACTION = "ExegesisAppService.save_document"
PATCH_REVIEW_COMMAND_NAME = "diff-preview"
PATCH_REVIEW_FLOW_STEP = "patch-review"
PATCH_REVIEW_DEMO_PATH_STEP = "preview and apply or reject a patch"


@dataclass(frozen=True)
class DiffPreviewInput:
    original: str
    proposed: str


@dataclass(frozen=True)
class DiffPreviewResult:
    output: str
    summary: str
    has_changes: bool
    normalized_equal: bool
    truncated: bool


@dataclass(frozen=True)
class PatchReviewDecision:
    status: str
    next_actions: tuple[str, ...]
    summary: str
    has_changes: bool
    normalized_equal: bool
    truncated: bool
    engine_actions: tuple[str, ...] = ()


@dataclass(frozen=True)
class PatchReviewCommandStatus:
    command: str
    flow_step: str
    demo_path_step: str
    decision_status: str
    next_actions: tuple[str, ...]
    engine_actions: tuple[str, ...]
    ready: bool
    action_routes: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class PatchReviewCommandStatusPayload:
    command: str
    flow_step: str
    demo_path_step: str
    decision: str
    next_actions: tuple[str, ...]
    engine_actions: tuple[str, ...]
    ready: bool
    has_changes: bool
    normalized_equal: bool
    truncated: bool
    action_routes: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class PatchReviewActionRoute:
    action: str
    engine_action: str
    command: str
    flow_step: str
    demo_path_step: str
    ready: bool


@dataclass(frozen=True)
class PatchReviewActionResolution:
    action: str
    engine_action: str
    command: str
    flow_step: str
    demo_path_step: str
    decision_status: str
    allowed: bool
    ready: bool
    reason: str


@dataclass(frozen=True)
class PatchReviewCommandContract:
    command: str
    flow_step: str
    demo_path_step: str
    change_action_routes: tuple[tuple[str, str], ...]
    no_change_action_routes: tuple[tuple[str, str], ...]
    engine_actions: tuple[str, ...]
    ready: bool


@dataclass(frozen=True)
class PatchReviewCommandSmokeContract:
    command: str
    flow_step: str
    demo_path_step: str
    changed_decision: str
    changed_action_routes: tuple[tuple[str, str], ...]
    no_change_decision: str
    no_change_action_routes: tuple[tuple[str, str], ...]
    ready: bool


@dataclass(frozen=True)
class PatchReviewReadinessContract:
    command: str
    flow_step: str
    demo_path_step: str
    decision_status: str
    next_actions: tuple[str, ...]
    action_routes: tuple[tuple[str, str], ...]
    expected_action_routes: tuple[tuple[str, str], ...]
    valid_action_routes: tuple[tuple[str, str], ...]
    missing_action_routes: tuple[tuple[str, str], ...]
    engine_actions: tuple[str, ...]
    missing_engine_actions: tuple[str, ...]
    missing_expected_engine_actions: tuple[str, ...]
    extra_engine_actions: tuple[str, ...]
    ready: bool


def _normalize_text(value: str) -> str:
    # Normalize newlines so diff output is stable across platforms.
    return value.replace("\r\n", "\n").replace("\r", "\n")


def _env_enabled(name: str) -> bool:
    value = os.getenv(name)
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _normalize_trailing_whitespace(value: str) -> str:
    lines = value.splitlines(keepends=True)
    normalized: list[str] = []
    for line in lines:
        if line.endswith("\n"):
            normalized.append(f"{line[:-1].rstrip(' \t')}\n")
        else:
            normalized.append(line.rstrip(" \t"))
    return "".join(normalized)


def _strip_ansi(value: str) -> str:
    return ANSI_ESCAPE_RE.sub("", value)


def _canonicalize_inline_whitespace(value: str) -> str:
    lines = value.splitlines(keepends=True)
    normalized: list[str] = []
    for line in lines:
        newline = "\n" if line.endswith("\n") else ""
        body = line[:-1] if newline else line
        body = re.sub(r"[ \t]+", " ", body)
        normalized.append(body + newline)
    return "".join(normalized)


def _normalize_case(value: str) -> str:
    return value.casefold()


def _strip_edge_blank_lines(value: str) -> str:
    lines = value.splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    if not lines:
        return ""
    return "\n".join(lines) + "\n"


def _strip_all_blank_lines(value: str) -> str:
    lines = [line for line in value.splitlines() if line.strip()]
    if not lines:
        return ""
    return "\n".join(lines) + "\n"


def _suppress_file_headers(diff: str) -> str:
    lines = diff.splitlines(keepends=True)
    if len(lines) >= 2 and lines[0].startswith("--- ") and lines[1].startswith("+++ "):
        return "".join(lines[2:])
    return diff


def _max_diff_output_chars() -> int:
    raw = os.getenv(MAX_DIFF_OUTPUT_CHARS_ENV)
    if raw is None:
        return MAX_DIFF_OUTPUT_CHARS
    try:
        parsed = int(raw.strip())
    except ValueError:
        return MAX_DIFF_OUTPUT_CHARS
    if parsed <= 0:
        return MAX_DIFF_OUTPUT_CHARS
    return parsed


def _summarize_diff(diff: str) -> str:
    added = 0
    removed = 0
    hunks = 0
    for line in diff.splitlines():
        if line.startswith("@@ "):
            hunks += 1
            continue
        if line.startswith("+++ ") or line.startswith("--- "):
            continue
        if line.startswith("+"):
            added += 1
            continue
        if line.startswith("-"):
            removed += 1
    summary = f"Diff summary: +{added} -{removed} (hunks: {hunks})"
    if _env_enabled(INCLUDE_SUMMARY_DETAILS_ENV):
        changed = added + removed
        net = added - removed
        summary = f"{summary} [changed: {changed}, net: {net:+d}]"
    return summary


def _options_banner(*, ignore_trailing_whitespace: bool, suppress_file_headers: bool, max_chars: int) -> str:
    return (
        "Diff options: "
        f"ignore_trailing_whitespace={str(ignore_trailing_whitespace).lower()}, "
        f"suppress_file_headers={str(suppress_file_headers).lower()}, "
        f"strip_ansi={str(_env_enabled(STRIP_ANSI_ENV)).lower()}, "
        f"canonicalize_inline_whitespace={str(_env_enabled(CANONICALIZE_INLINE_WHITESPACE_ENV)).lower()}, "
        f"ignore_case={str(_env_enabled(IGNORE_CASE_ENV)).lower()}, "
        f"ignore_edge_blank_lines={str(_env_enabled(IGNORE_EDGE_BLANK_LINES_ENV)).lower()}, "
        f"ignore_all_blank_lines={str(_env_enabled(IGNORE_ALL_BLANK_LINES_ENV)).lower()}, "
        f"max_output_chars={max_chars}, "
        f"truncation_strategy={_truncation_strategy()}"
    )


def _truncation_strategy() -> str:
    raw = os.getenv(TRUNCATION_STRATEGY_ENV)
    if raw is None:
        return "middle"
    value = raw.strip().lower()
    if value in {"middle", "tail"}:
        return value
    return "middle"


def _truncation_marker(omitted: int) -> str:
    custom = os.getenv(TRUNCATION_MARKER_ENV)
    if custom is not None and custom.strip():
        return custom.strip()
    return f"... diff truncated ({omitted} characters omitted) ..."


def _truncate_diff(diff: str, max_chars: int) -> str:
    strategy = _truncation_strategy()
    if strategy == "tail":
        omitted = len(diff) - max_chars
        return f"{_truncation_marker(omitted)}\n{diff[-max_chars:]}"

    head_chars = max_chars // 2
    tail_chars = max_chars - head_chars
    omitted = len(diff) - (head_chars + tail_chars)
    return (
        f"{diff[:head_chars]}"
        f"{_truncation_marker(omitted)}"
        f"{diff[-tail_chars:]}"
    )


def build_diff_preview_result(payload: DiffPreviewInput) -> DiffPreviewResult:
    original = _normalize_text(payload.original)
    proposed = _normalize_text(payload.proposed)
    ignore_trailing_whitespace = _env_enabled(IGNORE_TRAILING_WHITESPACE_ENV)
    suppress_file_headers = _env_enabled(SUPPRESS_FILE_HEADERS_ENV)
    include_options_banner = _env_enabled(INCLUDE_OPTIONS_BANNER_ENV)

    if _env_enabled(STRIP_ANSI_ENV):
        original = _strip_ansi(original)
        proposed = _strip_ansi(proposed)
    if _env_enabled(CANONICALIZE_INLINE_WHITESPACE_ENV):
        original = _canonicalize_inline_whitespace(original)
        proposed = _canonicalize_inline_whitespace(proposed)
    if _env_enabled(IGNORE_CASE_ENV):
        original = _normalize_case(original)
        proposed = _normalize_case(proposed)
    if _env_enabled(IGNORE_EDGE_BLANK_LINES_ENV):
        original = _strip_edge_blank_lines(original)
        proposed = _strip_edge_blank_lines(proposed)
    if _env_enabled(IGNORE_ALL_BLANK_LINES_ENV):
        original = _strip_all_blank_lines(original)
        proposed = _strip_all_blank_lines(proposed)
    if ignore_trailing_whitespace:
        original = _normalize_trailing_whitespace(original)
        proposed = _normalize_trailing_whitespace(proposed)

    if not original and not proposed:
        output = "No diff: both inputs are empty."
        return DiffPreviewResult(
            output=output,
            summary=output,
            has_changes=False,
            normalized_equal=True,
            truncated=False,
        )

    if original == proposed:
        output = "No diff: inputs are identical after normalization."
        return DiffPreviewResult(
            output=output,
            summary=output,
            has_changes=False,
            normalized_equal=True,
            truncated=False,
        )

    drafting = DraftingService()
    diff = drafting.propose_diff(original, proposed)
    summary_source = diff
    summary = _summarize_diff(summary_source)
    if suppress_file_headers:
        diff = _suppress_file_headers(diff)
    if not diff:
        output = "No diff: inputs are identical."
        return DiffPreviewResult(
            output=output,
            summary=output,
            has_changes=False,
            normalized_equal=False,
            truncated=False,
        )
    max_chars = _max_diff_output_chars()
    banner = ""
    if include_options_banner:
        banner = (
            _options_banner(
                ignore_trailing_whitespace=ignore_trailing_whitespace,
                suppress_file_headers=suppress_file_headers,
                max_chars=max_chars,
            )
            + "\n\n"
        )
    if _env_enabled(SUMMARY_ONLY_ENV):
        return DiffPreviewResult(
            output=f"{banner}{summary}",
            summary=summary,
            has_changes=True,
            normalized_equal=False,
            truncated=False,
        )

    output = diff
    truncated = False
    if len(diff) > max_chars:
        output = _truncate_diff(diff, max_chars)
        truncated = True

    if _env_enabled(INCLUDE_SUMMARY_ENV):
        output = f"{banner}{output}\n\n{summary}"
    else:
        output = f"{banner}{output}"
    return DiffPreviewResult(
        output=output,
        summary=summary,
        has_changes=True,
        normalized_equal=False,
        truncated=truncated,
    )


def run_diff_preview(payload: DiffPreviewInput) -> str:
    return build_diff_preview_result(payload).output


def _patch_review_engine_actions_for_result(result: DiffPreviewResult) -> tuple[str, ...]:
    if result.has_changes:
        return (
            PATCH_REVIEW_REVISE_ENGINE_ACTION,
            PATCH_REVIEW_APPLY_ENGINE_ACTION,
            PATCH_REVIEW_REJECT_ENGINE_ACTION,
        )
    return (PATCH_REVIEW_CONTINUE_ENGINE_ACTION,)


def _patch_review_action_routes_for_decision(
    decision: PatchReviewDecision,
) -> tuple[tuple[str, str], ...]:
    if decision.status == "changes-detected":
        return (
            ("revise", PATCH_REVIEW_REVISE_ENGINE_ACTION),
            ("apply", PATCH_REVIEW_APPLY_ENGINE_ACTION),
            ("reject", PATCH_REVIEW_REJECT_ENGINE_ACTION),
        )
    return tuple(
        (action, engine_action)
        for action, engine_action in zip(
            decision.next_actions,
            decision.engine_actions,
            strict=True,
        )
    )


def _patch_review_command_ready(decision: PatchReviewDecision) -> bool:
    routes = _patch_review_action_routes_for_decision(decision)
    route_actions = {action for action, _engine_action in routes}
    route_engine_actions = {engine_action for _action, engine_action in routes}
    return (
        bool(routes)
        and all(action and engine_action for action, engine_action in routes)
        and set(decision.next_actions).issubset(route_actions)
        and set(decision.engine_actions).issubset(route_engine_actions)
    )


def _patch_review_action_route_lookup_for_decision(
    decision: PatchReviewDecision,
) -> tuple[tuple[str, str], ...]:
    return tuple(
        (action, engine_action)
        for action, engine_action in _patch_review_action_routes_for_decision(decision)
        if action and engine_action
    )


def _normalize_patch_review_action(action: str) -> str:
    return action.strip().lower().replace("_", "-")


def _patch_review_smoke_contract_ready(
    changed_routes: tuple[tuple[str, str], ...],
    no_change_routes: tuple[tuple[str, str], ...],
) -> bool:
    contract = build_patch_review_command_contract()
    return (
        contract.ready
        and changed_routes == contract.change_action_routes
        and no_change_routes == contract.no_change_action_routes
    )


def build_patch_review_decision(payload: DiffPreviewInput) -> PatchReviewDecision:
    result = build_diff_preview_result(payload)
    if result.has_changes:
        status = "changes-detected"
        next_actions = ("apply", "reject")
    elif result.normalized_equal:
        status = "no-op"
        next_actions = ("continue",)
    else:
        status = "no-diff"
        next_actions = ("continue",)
    engine_actions = _patch_review_engine_actions_for_result(result)
    return PatchReviewDecision(
        status=status,
        next_actions=next_actions,
        summary=result.summary,
        has_changes=result.has_changes,
        normalized_equal=result.normalized_equal,
        truncated=result.truncated,
        engine_actions=engine_actions,
    )


def build_patch_review_command_status(payload: DiffPreviewInput) -> PatchReviewCommandStatus:
    decision = build_patch_review_decision(payload)
    return PatchReviewCommandStatus(
        command=PATCH_REVIEW_COMMAND_NAME,
        flow_step=PATCH_REVIEW_FLOW_STEP,
        demo_path_step=PATCH_REVIEW_DEMO_PATH_STEP,
        decision_status=decision.status,
        next_actions=decision.next_actions,
        engine_actions=decision.engine_actions,
        ready=_patch_review_command_ready(decision),
        action_routes=_patch_review_action_route_lookup_for_decision(decision),
    )


def build_patch_review_command_status_payload(
    payload: DiffPreviewInput,
) -> PatchReviewCommandStatusPayload:
    """Return a deterministic status payload for CLI smoke checks."""

    decision = build_patch_review_decision(payload)
    return PatchReviewCommandStatusPayload(
        command=PATCH_REVIEW_COMMAND_NAME,
        flow_step=PATCH_REVIEW_FLOW_STEP,
        demo_path_step=PATCH_REVIEW_DEMO_PATH_STEP,
        decision=decision.status,
        next_actions=decision.next_actions,
        engine_actions=decision.engine_actions,
        ready=_patch_review_command_ready(decision),
        has_changes=decision.has_changes,
        normalized_equal=decision.normalized_equal,
        truncated=decision.truncated,
        action_routes=_patch_review_action_route_lookup_for_decision(decision),
    )


def build_patch_review_action_routes(payload: DiffPreviewInput) -> tuple[PatchReviewActionRoute, ...]:
    """Return the exact patch-review action routes exposed by the command surface."""

    decision = build_patch_review_decision(payload)
    return tuple(
        PatchReviewActionRoute(
            action=action,
            engine_action=engine_action,
            command=PATCH_REVIEW_COMMAND_NAME,
            flow_step=PATCH_REVIEW_FLOW_STEP,
            demo_path_step=PATCH_REVIEW_DEMO_PATH_STEP,
            ready=bool(action and engine_action),
        )
        for action, engine_action in _patch_review_action_routes_for_decision(decision)
    )


def build_patch_review_action_route_lookup(payload: DiffPreviewInput) -> tuple[tuple[str, str], ...]:
    """Return a deterministic action -> engine-action lookup for CLI smoke checks."""

    return _patch_review_action_route_lookup_for_decision(build_patch_review_decision(payload))


def resolve_patch_review_action(
    payload: DiffPreviewInput,
    action: str,
) -> PatchReviewActionResolution:
    """Resolve one requested patch-review action to the engine action it may call."""

    requested_action = _normalize_patch_review_action(action)
    decision = build_patch_review_decision(payload)
    current_routes = dict(_patch_review_action_routes_for_decision(decision))
    expected_routes = dict(_expected_patch_review_action_routes())
    engine_action = current_routes.get(requested_action, expected_routes.get(requested_action, ""))
    if not requested_action:
        allowed = False
        reason = "missing-action"
    elif requested_action not in expected_routes:
        allowed = False
        reason = "unknown-action"
    elif requested_action not in current_routes:
        allowed = False
        reason = "action-not-available"
    else:
        allowed = True
        reason = "allowed"
    return PatchReviewActionResolution(
        action=requested_action,
        engine_action=engine_action,
        command=PATCH_REVIEW_COMMAND_NAME,
        flow_step=PATCH_REVIEW_FLOW_STEP,
        demo_path_step=PATCH_REVIEW_DEMO_PATH_STEP,
        decision_status=decision.status,
        allowed=allowed,
        ready=allowed and _patch_review_command_ready(decision),
        reason=reason,
    )


def build_patch_review_command_contract() -> PatchReviewCommandContract:
    """Return the stable patch-review route surface without requiring document text."""

    change_action_routes = (
        ("revise", PATCH_REVIEW_REVISE_ENGINE_ACTION),
        ("apply", PATCH_REVIEW_APPLY_ENGINE_ACTION),
        ("reject", PATCH_REVIEW_REJECT_ENGINE_ACTION),
    )
    no_change_action_routes = (("continue", PATCH_REVIEW_CONTINUE_ENGINE_ACTION),)
    engine_actions = tuple(
        engine_action
        for _, engine_action in change_action_routes + no_change_action_routes
    )
    return PatchReviewCommandContract(
        command=PATCH_REVIEW_COMMAND_NAME,
        flow_step=PATCH_REVIEW_FLOW_STEP,
        demo_path_step=PATCH_REVIEW_DEMO_PATH_STEP,
        change_action_routes=change_action_routes,
        no_change_action_routes=no_change_action_routes,
        engine_actions=engine_actions,
        ready=all(
            action and engine_action
            for action, engine_action in change_action_routes + no_change_action_routes
        ),
    )


def build_patch_review_command_smoke_contract() -> PatchReviewCommandSmokeContract:
    """Return the deterministic changed/no-change routes for command smoke checks."""

    changed = build_patch_review_decision(
        DiffPreviewInput("draft text before review\n", "revised draft text\n")
    )
    no_change = build_patch_review_decision(
        DiffPreviewInput("unchanged draft text\n", "unchanged draft text\n")
    )
    changed_routes = _patch_review_action_route_lookup_for_decision(changed)
    no_change_routes = _patch_review_action_route_lookup_for_decision(no_change)
    return PatchReviewCommandSmokeContract(
        command=PATCH_REVIEW_COMMAND_NAME,
        flow_step=PATCH_REVIEW_FLOW_STEP,
        demo_path_step=PATCH_REVIEW_DEMO_PATH_STEP,
        changed_decision=changed.status,
        changed_action_routes=changed_routes,
        no_change_decision=no_change.status,
        no_change_action_routes=no_change_routes,
        ready=_patch_review_smoke_contract_ready(changed_routes, no_change_routes),
    )


def run_patch_review_decision(payload: DiffPreviewInput) -> str:
    decision = build_patch_review_decision(payload)
    return (
        f"patch-review: {decision.status}; "
        f"next-actions={','.join(decision.next_actions)}; "
        f"engine-actions={','.join(decision.engine_actions)}; "
        f"truncated={str(decision.truncated).lower()}; "
        f"{decision.summary}"
    )


def run_patch_review_command_status(payload: DiffPreviewInput) -> str:
    status = build_patch_review_command_status(payload)
    return (
        f"command={status.command}; "
        f"flow-step={status.flow_step}; "
        f"demo-path-step={status.demo_path_step}; "
        f"decision={status.decision_status}; "
        f"next-actions={','.join(status.next_actions)}; "
        f"engine-actions={','.join(status.engine_actions)}; "
        f"action-routes={json.dumps(status.action_routes)}; "
        f"ready={str(status.ready).lower()}"
    )


def run_patch_review_command_status_json(payload: DiffPreviewInput) -> str:
    status = build_patch_review_command_status_payload(payload)
    return json.dumps(
        {
            "command": status.command,
            "flow_step": status.flow_step,
            "demo_path_step": status.demo_path_step,
            "decision": status.decision,
            "next_actions": status.next_actions,
            "engine_actions": status.engine_actions,
            "ready": status.ready,
            "has_changes": status.has_changes,
            "normalized_equal": status.normalized_equal,
            "truncated": status.truncated,
            "action_routes": status.action_routes,
        },
        sort_keys=True,
        separators=(",", ":"),
    )


def run_patch_review_action_routes(payload: DiffPreviewInput) -> str:
    routes = build_patch_review_action_routes(payload)
    if not routes:
        return "patch-review-route: none"
    return "\n".join(
        (
            f"patch-review-route: action={route.action}; "
            f"engine-action={route.engine_action}; "
            f"command={route.command}; "
            f"flow-step={route.flow_step}; "
            f"demo-path-step={route.demo_path_step}; "
            f"ready={str(route.ready).lower()}"
        )
        for route in routes
    )


def run_patch_review_action_routes_json(payload: DiffPreviewInput) -> str:
    routes = build_patch_review_action_routes(payload)
    return json.dumps(
        [
            {
                "action": route.action,
                "engine_action": route.engine_action,
                "command": route.command,
                "flow_step": route.flow_step,
                "demo_path_step": route.demo_path_step,
                "ready": route.ready,
            }
            for route in routes
        ],
        sort_keys=True,
        separators=(",", ":"),
    )


def run_patch_review_action_route_lookup_json(payload: DiffPreviewInput) -> str:
    return json.dumps(
        build_patch_review_action_route_lookup(payload),
        sort_keys=True,
        separators=(",", ":"),
    )


def run_patch_review_action_resolution(payload: DiffPreviewInput, action: str) -> str:
    resolution = resolve_patch_review_action(payload, action)
    return (
        f"patch-review-action: action={resolution.action}; "
        f"engine-action={resolution.engine_action}; "
        f"command={resolution.command}; "
        f"flow-step={resolution.flow_step}; "
        f"demo-path-step={resolution.demo_path_step}; "
        f"decision={resolution.decision_status}; "
        f"allowed={str(resolution.allowed).lower()}; "
        f"ready={str(resolution.ready).lower()}; "
        f"reason={resolution.reason}"
    )


def run_patch_review_action_resolution_json(payload: DiffPreviewInput, action: str) -> str:
    resolution = resolve_patch_review_action(payload, action)
    return json.dumps(
        {
            "action": resolution.action,
            "engine_action": resolution.engine_action,
            "command": resolution.command,
            "flow_step": resolution.flow_step,
            "demo_path_step": resolution.demo_path_step,
            "decision_status": resolution.decision_status,
            "allowed": resolution.allowed,
            "ready": resolution.ready,
            "reason": resolution.reason,
        },
        sort_keys=True,
        separators=(",", ":"),
    )


def run_patch_review_command_contract() -> str:
    contract = build_patch_review_command_contract()
    return (
        f"command={contract.command}; "
        f"flow-step={contract.flow_step}; "
        f"demo-path-step={contract.demo_path_step}; "
        f"change-action-routes={json.dumps(contract.change_action_routes)}; "
        f"no-change-action-routes={json.dumps(contract.no_change_action_routes)}; "
        f"engine-actions={','.join(contract.engine_actions)}; "
        f"ready={str(contract.ready).lower()}"
    )


def run_patch_review_command_contract_json() -> str:
    contract = build_patch_review_command_contract()
    return json.dumps(
        {
            "command": contract.command,
            "flow_step": contract.flow_step,
            "demo_path_step": contract.demo_path_step,
            "change_action_routes": contract.change_action_routes,
            "no_change_action_routes": contract.no_change_action_routes,
            "engine_actions": contract.engine_actions,
            "ready": contract.ready,
        },
        sort_keys=True,
        separators=(",", ":"),
    )


def run_patch_review_command_smoke_contract() -> str:
    contract = build_patch_review_command_smoke_contract()
    return (
        f"command={contract.command}; "
        f"flow-step={contract.flow_step}; "
        f"demo-path-step={contract.demo_path_step}; "
        f"changed-decision={contract.changed_decision}; "
        f"changed-action-routes={json.dumps(contract.changed_action_routes)}; "
        f"no-change-decision={contract.no_change_decision}; "
        f"no-change-action-routes={json.dumps(contract.no_change_action_routes)}; "
        f"ready={str(contract.ready).lower()}"
    )


def run_patch_review_command_smoke_contract_json() -> str:
    contract = build_patch_review_command_smoke_contract()
    return json.dumps(
        {
            "command": contract.command,
            "flow_step": contract.flow_step,
            "demo_path_step": contract.demo_path_step,
            "changed_decision": contract.changed_decision,
            "changed_action_routes": contract.changed_action_routes,
            "no_change_decision": contract.no_change_decision,
            "no_change_action_routes": contract.no_change_action_routes,
            "ready": contract.ready,
        },
        sort_keys=True,
        separators=(",", ":"),
    )


@dataclass(frozen=True)
class PatchReviewActionRouteValidation:
    is_valid: bool
    engine_actions: tuple[str, ...]
    valid_engine_actions: tuple[str, ...]
    missing_engine_actions: tuple[str, ...]
    missing_expected_engine_actions: tuple[str, ...]
    extra_engine_actions: tuple[str, ...]
    expected_action_routes: tuple[tuple[str, str], ...]
    valid_action_routes: tuple[tuple[str, str], ...]
    invalid_action_routes: tuple[tuple[str, str], ...]
    missing_action_routes: tuple[tuple[str, str], ...]


def _expected_patch_review_action_routes() -> tuple[tuple[str, str], ...]:
    contract = build_patch_review_command_contract()
    return contract.change_action_routes + contract.no_change_action_routes


def validate_patch_review_action_routes(
    routes: tuple[tuple[str, str], ...],
) -> PatchReviewActionRouteValidation:
    """Validate exact patch-review action routes against demo-path engine actions.

    This catches both unknown engine actions and valid engine actions wired to
    the wrong command action token.
    """
    from src.qual.commands.catalog import command_demo_engine_actions

    demo_engine_actions = set(command_demo_engine_actions())
    expected_action_routes = _expected_patch_review_action_routes()
    expected_action_route_set = set(expected_action_routes)
    route_engine_actions = tuple(engine_action for _, engine_action in routes)
    route_set = set(route_engine_actions)

    valid = tuple(
        engine_action
        for engine_action in route_engine_actions
        if engine_action in demo_engine_actions
    )
    missing = tuple(
        engine_action
        for engine_action in route_engine_actions
        if engine_action not in demo_engine_actions
    )
    # Extra actions are demo-path actions not covered by this contract's routes.
    extra = tuple(
        engine_action
        for engine_action in command_demo_engine_actions()
        if engine_action not in route_set
    )
    valid_action_routes = tuple(
        route
        for route in routes
        if route in expected_action_route_set
    )
    invalid_action_routes = tuple(
        route
        for route in routes
        if route not in expected_action_route_set
    )
    route_pairs = set(routes)
    missing_action_routes = tuple(
        route
        for route in expected_action_routes
        if route not in route_pairs
    )
    missing_expected_engine_actions = tuple(
        engine_action
        for _, engine_action in expected_action_routes
        if engine_action not in route_set
    )

    return PatchReviewActionRouteValidation(
        is_valid=(
            len(missing) == 0
            and len(missing_expected_engine_actions) == 0
            and len(invalid_action_routes) == 0
            and len(missing_action_routes) == 0
        ),
        engine_actions=route_engine_actions,
        valid_engine_actions=valid,
        missing_engine_actions=missing,
        missing_expected_engine_actions=missing_expected_engine_actions,
        extra_engine_actions=extra,
        expected_action_routes=expected_action_routes,
        valid_action_routes=valid_action_routes,
        invalid_action_routes=invalid_action_routes,
        missing_action_routes=missing_action_routes,
    )


def _patch_review_action_route_validation_payload(
    validation: PatchReviewActionRouteValidation,
) -> dict[str, object]:
    return {
        "is_valid": validation.is_valid,
        "engine_actions": validation.engine_actions,
        "valid_engine_actions": validation.valid_engine_actions,
        "missing_engine_actions": validation.missing_engine_actions,
        "missing_expected_engine_actions": validation.missing_expected_engine_actions,
        "extra_engine_actions": validation.extra_engine_actions,
        "expected_action_routes": validation.expected_action_routes,
        "valid_action_routes": validation.valid_action_routes,
        "invalid_action_routes": validation.invalid_action_routes,
        "missing_action_routes": validation.missing_action_routes,
    }


def validate_patch_review_command_contract() -> PatchReviewActionRouteValidation:
    """Validate the patch review command contract against the demo path engine actions.

    Returns a validation result indicating whether all engine actions in the
    contract are covered by the canonical demo path.
    """
    contract = build_patch_review_command_contract()
    all_routes = contract.change_action_routes + contract.no_change_action_routes
    return validate_patch_review_action_routes(all_routes)


def run_patch_review_action_route_validation() -> str:
    """Return a human-readable validation report for CLI smoke checks."""
    validation = validate_patch_review_command_contract()
    parts = [
        f"patch-review-route-validation: is_valid={str(validation.is_valid).lower()}",
        f"engine_actions={','.join(validation.engine_actions)}",
        f"valid={','.join(validation.valid_engine_actions)}",
    ]
    if validation.missing_engine_actions:
        parts.append(
            f"missing={','.join(validation.missing_engine_actions)}"
        )
    if validation.missing_expected_engine_actions:
        parts.append(
            "missing-expected="
            + ",".join(validation.missing_expected_engine_actions)
        )
    if validation.invalid_action_routes:
        parts.append(
            "invalid-routes="
            + json.dumps(validation.invalid_action_routes, separators=(",", ":"))
        )
    if validation.missing_action_routes:
        parts.append(
            "missing-routes="
            + json.dumps(validation.missing_action_routes, separators=(",", ":"))
        )
    if validation.extra_engine_actions:
        parts.append(
            f"extra={','.join(validation.extra_engine_actions)}"
        )
    return "; ".join(parts)


def run_patch_review_action_route_validation_json() -> str:
    """Return the patch-review route validation as deterministic JSON."""
    return json.dumps(
        _patch_review_action_route_validation_payload(
            validate_patch_review_command_contract()
        ),
        sort_keys=True,
        separators=(",", ":"),
    )


def build_patch_review_readiness_contract(
    payload: DiffPreviewInput,
) -> PatchReviewReadinessContract:
    """Bundle patch-review decision state with the stable demo-path route contract."""

    status = build_patch_review_command_status(payload)
    validation = validate_patch_review_command_contract()
    return PatchReviewReadinessContract(
        command=status.command,
        flow_step=status.flow_step,
        demo_path_step=status.demo_path_step,
        decision_status=status.decision_status,
        next_actions=status.next_actions,
        action_routes=status.action_routes,
        expected_action_routes=validation.expected_action_routes,
        valid_action_routes=validation.valid_action_routes,
        missing_action_routes=validation.missing_action_routes,
        engine_actions=status.engine_actions,
        missing_engine_actions=validation.missing_engine_actions,
        missing_expected_engine_actions=validation.missing_expected_engine_actions,
        extra_engine_actions=validation.extra_engine_actions,
        ready=status.ready and validation.is_valid,
    )


def _patch_review_readiness_contract_payload(
    contract: PatchReviewReadinessContract,
) -> dict[str, object]:
    return {
        "command": contract.command,
        "flow_step": contract.flow_step,
        "demo_path_step": contract.demo_path_step,
        "decision_status": contract.decision_status,
        "next_actions": contract.next_actions,
        "action_routes": contract.action_routes,
        "expected_action_routes": contract.expected_action_routes,
        "valid_action_routes": contract.valid_action_routes,
        "missing_action_routes": contract.missing_action_routes,
        "engine_actions": contract.engine_actions,
        "missing_engine_actions": contract.missing_engine_actions,
        "missing_expected_engine_actions": contract.missing_expected_engine_actions,
        "extra_engine_actions": contract.extra_engine_actions,
        "ready": contract.ready,
    }


def run_patch_review_readiness_contract(payload: DiffPreviewInput) -> str:
    """Return a compact readiness line for patch-review command smoke checks."""

    contract = build_patch_review_readiness_contract(payload)
    return (
        f"patch-review-readiness: command={contract.command}; "
        f"flow-step={contract.flow_step}; "
        f"demo-path-step={contract.demo_path_step}; "
        f"decision={contract.decision_status}; "
        f"next-actions={','.join(contract.next_actions)}; "
        f"action-routes={json.dumps(contract.action_routes)}; "
        f"missing-routes={json.dumps(contract.missing_action_routes)}; "
        f"missing-engine-actions={','.join(contract.missing_engine_actions)}; "
        f"missing-expected-engine-actions={','.join(contract.missing_expected_engine_actions)}; "
        f"ready={str(contract.ready).lower()}"
    )


def run_patch_review_readiness_contract_json(payload: DiffPreviewInput) -> str:
    """Return deterministic JSON for patch-review command readiness checks."""

    return json.dumps(
        _patch_review_readiness_contract_payload(
            build_patch_review_readiness_contract(payload)
        ),
        sort_keys=True,
        separators=(",", ":"),
    )
