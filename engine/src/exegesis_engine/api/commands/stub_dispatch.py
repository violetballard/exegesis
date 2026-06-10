from __future__ import annotations

import re
from dataclasses import dataclass
from hashlib import sha256
from typing import Union

from exegesis_engine.api.commands.catalog import command_lookup_table
from exegesis_engine.api.commands.diff_preview import (
    DiffPreviewInput,
    PatchApplyInput,
    PatchRejectInput,
    run_diff_preview,
    run_patch_apply,
    run_patch_reject,
)
from exegesis_engine.api.commands.engine_stubs import (
    BasketActionInput,
    BasketActionResult,
    ExportHandoffInput,
    ExportHandoffResult,
    OpenProjectInput,
    OpenProjectResult,
    RetrieveInput,
    RetrieveResult,
    ReviseInput,
    ReviseResult,
    SessionResumeInput,
    SessionResumeResult,
    SessionSaveInput,
    SessionSaveResult,
    run_basket_action,
    run_export_handoff,
    run_open_project,
    run_retrieve,
    run_revise,
    run_session_resume,
    run_session_save,
    NotebookActionInput,
    NotebookActionResult,
    run_notebook,
)

# Argv layouts for each partial command (tokens after the program name):
#   bootstrap <project_id> [<document_id>]
#   context-basket list
#   context-basket add <item_id>
#   terminal <document_id>
#   revise <document_id> [<basket_item_id> ...]
#   session-save <document_id> <session_id>
#   session-resume <session_id>
#   diff-preview [preview|apply|reject] <original> <proposed>
#   patch-apply <original> <proposed>
#   patch-reject <original> <proposed>
#
# These are the stable calling conventions that feat-engine-runs replaces the
# stub bodies against.  Parsing lives here; business logic lives in engine_stubs
# and diff_preview respectively.

BOOTSTRAP_COMMAND = "bootstrap"
RETRIEVE_COMMAND = "retrieve"
CONTEXT_BASKET_COMMAND = "context-basket"
TERMINAL_COMMAND = "terminal"
REVISE_COMMAND = "revise"
SESSION_SAVE_COMMAND = "session-save"
SESSION_RESUME_COMMAND = "session-resume"
DIFF_PREVIEW_COMMAND = "diff-preview"
PATCH_REVIEW_COMMAND = "patch-review"
PATCH_APPLY_COMMAND = "patch-apply"
PATCH_REJECT_COMMAND = "patch-reject"
NOTEBOOK_COMMAND = "notebook"
PATCH_REVIEW_ACTIONS = ("preview", "apply", "reject")


def _normalize_dispatch_token(value: str) -> str:
    return re.sub(r"[-_\s]+", "-", value.strip().casefold()).strip("-")


# All known command tokens in canonical demo-path execution order.
# Used by UnknownCommandError to report the valid surface, and by callers that
# need to enumerate every command without hard-coding individual token strings.
# revise, session-save, and session-resume are still stubs pending feat-engine-runs;
# engine_stubs.py carries the per-command blocker_reason for those three.
COMMAND_TOKENS: tuple[str, ...] = (
    BOOTSTRAP_COMMAND,
    RETRIEVE_COMMAND,
    CONTEXT_BASKET_COMMAND,
    REVISE_COMMAND,
    DIFF_PREVIEW_COMMAND,
    PATCH_APPLY_COMMAND,
    PATCH_REJECT_COMMAND,
    SESSION_SAVE_COMMAND,
    SESSION_RESUME_COMMAND,
    TERMINAL_COMMAND,
    NOTEBOOK_COMMAND,
)

# The three commands still backed by stubs (engine integration pending).
# feat-engine-runs replaces the bodies when it wires the loop.
PARTIAL_COMMAND_TOKENS: tuple[str, ...] = (
    REVISE_COMMAND,
    SESSION_SAVE_COMMAND,
    SESSION_RESUME_COMMAND,
)

# Commands that produce status="ok" in the current Milestone 3 loop — the
# diff/patch trio is fully functional today; all other commands are stubs
# blocked by upstream lanes.  feat-engine-runs and feat-context-storage
# consult this to know which commands can be trusted end-to-end right now.
READY_COMMAND_TOKENS: tuple[str, ...] = (
    DIFF_PREVIEW_COMMAND,
    PATCH_APPLY_COMMAND,
    PATCH_REJECT_COMMAND,
)

# Structured map from each stub command token to the lane that must close it.
# Importing lanes use this to know which commands they are responsible for
# wiring, and integration checks can assert coverage without parsing strings.
# A command missing from READY_COMMAND_TOKENS must appear here.
STUB_COMMAND_BLOCKERS: dict[str, str] = {
    BOOTSTRAP_COMMAND: "feat-context-storage",
    RETRIEVE_COMMAND: "feat-retrieval-fts",
    CONTEXT_BASKET_COMMAND: "feat-context-storage",
    REVISE_COMMAND: "feat-engine-runs",
    SESSION_SAVE_COMMAND: "feat-engine-runs",
    SESSION_RESUME_COMMAND: "feat-engine-runs",
    TERMINAL_COMMAND: "feat-engine-runs",
    NOTEBOOK_COMMAND: "feat-engine-runs",
}

# Deterministic map from command token to the demo-path step it advances.  This
# lets smoke tests and handoff tooling report canonical progress without
# inferring it from command names or blocker strings.
COMMAND_DEMO_PATH_STEPS: dict[str, str] = {
    BOOTSTRAP_COMMAND: "open-project-document",
    RETRIEVE_COMMAND: "retrieve-relevant-material",
    CONTEXT_BASKET_COMMAND: "promote-or-gather-context-into-basket",
    REVISE_COMMAND: "produce-plan-or-revision",
    DIFF_PREVIEW_COMMAND: "preview-and-apply-or-reject-patch",
    PATCH_APPLY_COMMAND: "preview-and-apply-or-reject-patch",
    PATCH_REJECT_COMMAND: "preview-and-apply-or-reject-patch",
    SESSION_SAVE_COMMAND: "persist-updated-document-session-state",
    SESSION_RESUME_COMMAND: "continue-without-losing-context",
    TERMINAL_COMMAND: "export-handoff",
    NOTEBOOK_COMMAND: "notebook-compaction",
}

# Canonical demo-path step order for readiness and handoff reporting.  Some
# steps have multiple command tokens, so consumers should not infer this by
# walking COMMAND_TOKENS directly.
COMMAND_DEMO_PATH_STEP_ORDER: tuple[str, ...] = (
    "open-project-document",
    "retrieve-relevant-material",
    "promote-or-gather-context-into-basket",
    "produce-plan-or-revision",
    "preview-and-apply-or-reject-patch",
    "persist-updated-document-session-state",
    "continue-without-losing-context",
    "export-handoff",
    "notebook-compaction",
)

STUB_BLOCKER_LANES_BY_STEP: dict[str, str] = {
    COMMAND_DEMO_PATH_STEPS[token]: lane
    for token, lane in STUB_COMMAND_BLOCKERS.items()
}


def _validate_command_dispatch_tables() -> None:
    expected_tokens = set(COMMAND_TOKENS)
    minimal_tokens = set(DEMO_PATH_MINIMAL_ARGV)
    if minimal_tokens != expected_tokens:
        missing = ", ".join(sorted(expected_tokens - minimal_tokens))
        extra = ", ".join(sorted(minimal_tokens - expected_tokens))
        raise ValueError(
            "DEMO_PATH_MINIMAL_ARGV must cover COMMAND_TOKENS exactly"
            f" (missing: {missing or '-'}; extra: {extra or '-'})"
        )

    for token, minimal_argv in DEMO_PATH_MINIMAL_ARGV.items():
        if not minimal_argv or minimal_argv[0] != token:
            raise ValueError(f"minimal argv for '{token}' must start with the command token")

    ready_tokens = set(READY_COMMAND_TOKENS)
    if not ready_tokens <= expected_tokens:
        extra_ready = ", ".join(sorted(ready_tokens - expected_tokens))
        raise ValueError(f"READY_COMMAND_TOKENS contains unknown commands: {extra_ready}")

    expected_stub_tokens = expected_tokens - ready_tokens
    blocker_tokens = set(STUB_COMMAND_BLOCKERS)
    if blocker_tokens != expected_stub_tokens:
        missing = ", ".join(sorted(expected_stub_tokens - blocker_tokens))
        extra = ", ".join(sorted(blocker_tokens - expected_stub_tokens))
        raise ValueError(
            "STUB_COMMAND_BLOCKERS must cover every non-ready command exactly"
            f" (missing: {missing or '-'}; extra: {extra or '-'})"
        )
    expected_blocker_lanes_by_step = {
        COMMAND_DEMO_PATH_STEPS[token]: lane
        for token, lane in STUB_COMMAND_BLOCKERS.items()
    }
    if STUB_BLOCKER_LANES_BY_STEP != expected_blocker_lanes_by_step:
        raise ValueError("STUB_BLOCKER_LANES_BY_STEP must match command blocker steps")

    step_tokens = set(COMMAND_DEMO_PATH_STEPS)
    if step_tokens != expected_tokens:
        missing = ", ".join(sorted(expected_tokens - step_tokens))
        extra = ", ".join(sorted(step_tokens - expected_tokens))
        raise ValueError(
            "COMMAND_DEMO_PATH_STEPS must cover COMMAND_TOKENS exactly"
            f" (missing: {missing or '-'}; extra: {extra or '-'})"
        )
    step_order = tuple(dict.fromkeys(COMMAND_DEMO_PATH_STEPS.values()))
    if step_order != COMMAND_DEMO_PATH_STEP_ORDER:
        raise ValueError("COMMAND_DEMO_PATH_STEP_ORDER must match command demo-path order")


def command_demo_path_step_order() -> tuple[str, ...]:
    """Return canonical demo-path steps in readiness/reporting order."""

    _validate_command_dispatch_tables()
    return COMMAND_DEMO_PATH_STEP_ORDER


def _command_aliases_from_catalog() -> dict[str, str]:
    aliases: dict[str, str] = {}
    for token, canonical in command_lookup_table():
        if token == canonical:
            continue
        if canonical in COMMAND_TOKENS:
            aliases[token] = canonical
    return aliases


# Compat aliases map catalog lookup tokens to their canonical COMMAND_TOKENS
# counterpart. dispatch_command resolves these before routing so alias tokens
# behave identically to the canonical form while COMMAND_TOKENS stays canonical.
COMMAND_ALIASES: dict[str, str] = _command_aliases_from_catalog()


def known_command_tokens() -> tuple[str, ...]:
    """Return every accepted dispatch token in deterministic lookup order."""

    tokens: list[str] = []
    for token in (*COMMAND_TOKENS, PATCH_REVIEW_COMMAND, *COMMAND_ALIASES):
        if token not in tokens:
            tokens.append(token)
    return tuple(tokens)


# Minimal valid argv for each COMMAND_TOKENS entry, in canonical demo-path order.
# Each tuple exercises the command with the smallest argument set that avoids a
# parse error — just enough to route and return a result (ok or stub).
# Use this to smoke-test the full demo-path surface without re-discovering argv
# layouts per command.  READY_COMMAND_TOKENS entries return exit 0; all others
# return exit 2 with their STUB_COMMAND_BLOCKERS lane name in the output.
DEMO_PATH_MINIMAL_ARGV: dict[str, tuple[str, ...]] = {
    BOOTSTRAP_COMMAND: (BOOTSTRAP_COMMAND, "proj-smoke"),
    RETRIEVE_COMMAND: (RETRIEVE_COMMAND, "smoke query"),
    CONTEXT_BASKET_COMMAND: (CONTEXT_BASKET_COMMAND, "list"),
    REVISE_COMMAND: (REVISE_COMMAND, "doc-smoke"),
    DIFF_PREVIEW_COMMAND: (DIFF_PREVIEW_COMMAND, "original\n", "proposed\n"),
    PATCH_APPLY_COMMAND: (PATCH_APPLY_COMMAND, "original\n", "proposed\n"),
    PATCH_REJECT_COMMAND: (PATCH_REJECT_COMMAND, "original\n", "proposed\n"),
    SESSION_SAVE_COMMAND: (SESSION_SAVE_COMMAND, "doc-smoke", "sess-smoke"),
    SESSION_RESUME_COMMAND: (SESSION_RESUME_COMMAND, "sess-smoke"),
    TERMINAL_COMMAND: (TERMINAL_COMMAND, "doc-smoke"),
    NOTEBOOK_COMMAND: (NOTEBOOK_COMMAND, "budget", "chat-smoke"),
}


@dataclass(frozen=True)
class ArgvParseError:
    command: str
    reason: str
    usage: str

    def __post_init__(self) -> None:
        if not isinstance(self.command, str):
            raise TypeError("command must be a string")
        if not isinstance(self.reason, str):
            raise TypeError("reason must be a string")
        if not isinstance(self.usage, str):
            raise TypeError("usage must be a string")
        if not self.command.strip():
            raise ValueError("command cannot be empty or whitespace only")


def _unexpected_argument_error(command: str, argument: str, usage: str) -> ArgvParseError:
    return ArgvParseError(
        command=command,
        reason=f"unexpected argument: {argument}",
        usage=usage,
    )


def _missing_text_argument_error(command: str, argument_name: str, usage: str) -> ArgvParseError:
    return ArgvParseError(
        command=command,
        reason=f"missing required argument: {argument_name}",
        usage=usage,
    )


def _null_byte_argument_error(command: str, usage: str) -> ArgvParseError:
    return ArgvParseError(
        command=command,
        reason="arguments cannot contain null bytes",
        usage=usage,
    )


def _argv_contains_null_byte(argv: tuple[str, ...]) -> bool:
    return any("\x00" in arg for arg in argv)


def _sanitize_command_text(value: str) -> str:
    return value.replace("\x00", "\\0")


def _null_byte_dispatch_error(argv: tuple[str, ...]) -> ArgvParseError:
    if "\x00" in argv[0]:
        return _null_byte_argument_error("command", "<command> [args]")

    token = _normalize_dispatch_token(argv[0])
    canonical = COMMAND_ALIASES.get(token, token)
    if canonical in {DIFF_PREVIEW_COMMAND, PATCH_APPLY_COMMAND, PATCH_REJECT_COMMAND}:
        return _null_byte_argument_error(canonical, f"{canonical} <original> <proposed>")
    return _null_byte_argument_error(canonical, f"{canonical} [args]")


def parse_bootstrap_argv(argv: tuple[str, ...]) -> OpenProjectInput | ArgvParseError:
    """Parse argv tokens for 'bootstrap' into an OpenProjectInput.

    Expected layout: (command_token, project_id, [document_id])
    """
    usage = "bootstrap <project_id> [<document_id>]"
    if _argv_contains_null_byte(argv):
        return _null_byte_argument_error(BOOTSTRAP_COMMAND, usage)
    if len(argv) < 2 or not argv[1].strip():
        return _missing_text_argument_error(BOOTSTRAP_COMMAND, "project_id", usage)
    if len(argv) > 3:
        return _unexpected_argument_error(BOOTSTRAP_COMMAND, argv[3], usage)
    if len(argv) >= 3 and not argv[2].strip():
        return _missing_text_argument_error(BOOTSTRAP_COMMAND, "document_id", usage)
    return OpenProjectInput(
        project_id=argv[1],
        document_id=argv[2] if len(argv) >= 3 else "",
    )


BASKET_ACTIONS = ("list", "add", "remove", "clear")
BASKET_ITEM_ACTIONS = ("add", "remove")


def parse_context_basket_argv(argv: tuple[str, ...]) -> BasketActionInput | ArgvParseError:
    """Parse argv tokens for 'context-basket' into a BasketActionInput.

    Expected layouts:
      context-basket list
      context-basket add <item_id>
      context-basket remove <item_id>
      context-basket clear
    """
    usage = "context-basket list | context-basket add <item_id> | context-basket remove <item_id> | context-basket clear"
    if _argv_contains_null_byte(argv):
        return _null_byte_argument_error(CONTEXT_BASKET_COMMAND, usage)
    if len(argv) < 2:
        return ArgvParseError(
            command=CONTEXT_BASKET_COMMAND,
            reason="missing required argument: action (list, add, remove, or clear)",
            usage=usage,
        )
    action = argv[1].strip().lower()
    if action not in BASKET_ACTIONS:
        return ArgvParseError(
            command=CONTEXT_BASKET_COMMAND,
            reason=f"unknown action '{action}': expected list, add, remove, or clear",
            usage=usage,
        )
    if action in BASKET_ITEM_ACTIONS and (len(argv) < 3 or not argv[2].strip()):
        return ArgvParseError(
            command=CONTEXT_BASKET_COMMAND,
            reason="missing required argument: item_id",
            usage=f"context-basket {action} <item_id>",
        )
    if action in BASKET_ITEM_ACTIONS and len(argv) > 3:
        return _unexpected_argument_error(CONTEXT_BASKET_COMMAND, argv[3], f"context-basket {action} <item_id>")
    if action not in BASKET_ITEM_ACTIONS and len(argv) > 2:
        return ArgvParseError(
            command=CONTEXT_BASKET_COMMAND,
            reason=f"unexpected argument for {action}: {argv[2]}",
            usage=f"context-basket {action}",
        )
    return BasketActionInput(
        action=action,
        item_id=argv[2] if action in BASKET_ITEM_ACTIONS else "",
    )


def parse_terminal_argv(argv: tuple[str, ...]) -> ExportHandoffInput | ArgvParseError:
    """Parse argv tokens for 'terminal' into an ExportHandoffInput.

    Expected layout: (command_token, document_id)
    """
    usage = "terminal <document_id>"
    if _argv_contains_null_byte(argv):
        return _null_byte_argument_error(TERMINAL_COMMAND, usage)
    if len(argv) < 2 or not argv[1].strip():
        return _missing_text_argument_error(TERMINAL_COMMAND, "document_id", usage)
    if len(argv) > 2:
        return _unexpected_argument_error(TERMINAL_COMMAND, argv[2], usage)
    return ExportHandoffInput(document_id=argv[1])


def _validate_argv(argv: tuple[str, ...]) -> None:
    if not isinstance(argv, (tuple, list)):
        raise TypeError(f"argv must be a list or tuple, got {type(argv).__name__}")
    for i, x in enumerate(argv):
        if not isinstance(x, str):
            raise TypeError(f"argv element at index {i} must be a string, got {type(x).__name__}")
        if len(x) > 50000000:
            raise ValueError(f"argv element at index {i} length cannot exceed 50000000 characters")


def dispatch_bootstrap(argv: tuple[str, ...]) -> OpenProjectResult | ArgvParseError:
    """Dispatch argv for 'bootstrap' to the open-project stub."""
    _validate_argv(argv)
    parsed = parse_bootstrap_argv(argv)
    if isinstance(parsed, ArgvParseError):
        return parsed
    return run_open_project(parsed)


def dispatch_context_basket(argv: tuple[str, ...]) -> BasketActionResult | ArgvParseError:
    """Dispatch argv for 'context-basket' to the basket-action stub."""
    _validate_argv(argv)
    parsed = parse_context_basket_argv(argv)
    if isinstance(parsed, ArgvParseError):
        return parsed
    return run_basket_action(parsed)


def dispatch_terminal(argv: tuple[str, ...]) -> ExportHandoffResult | ArgvParseError:
    """Dispatch argv for 'terminal' to the export-handoff stub."""
    _validate_argv(argv)
    parsed = parse_terminal_argv(argv)
    if isinstance(parsed, ArgvParseError):
        return parsed
    return run_export_handoff(parsed)


def dispatch_notebook(argv: tuple[str, ...]) -> NotebookActionResult | ArgvParseError:
    """Dispatch argv for 'notebook' to the run_notebook stub."""
    _validate_argv(argv)
    parsed = parse_notebook_argv(argv)
    if isinstance(parsed, ArgvParseError):
        return parsed
    return run_notebook(parsed)


def parse_retrieve_argv(argv: tuple[str, ...]) -> RetrieveInput | ArgvParseError:
    """Parse argv tokens for 'retrieve' into a RetrieveInput.

    Expected layout: (command_token, query_token [query_token ...])
    All tokens after the command are joined with a space so callers can pass
    multi-word queries without quoting: `retrieve exegesis scoring rubric`.
    """
    usage = "retrieve <query>"
    if _argv_contains_null_byte(argv):
        return _null_byte_argument_error(RETRIEVE_COMMAND, usage)
    query = " ".join(arg.strip() for arg in argv[1:] if arg.strip()).strip()
    if not query:
        return _missing_text_argument_error(RETRIEVE_COMMAND, "query", usage)
    return RetrieveInput(query=query)


def parse_notebook_argv(argv: tuple[str, ...]) -> NotebookActionInput | ArgvParseError:
    """Parse argv tokens for 'notebook' into a NotebookActionInput.

    Expected layouts:
      notebook budget <chat_id>
      notebook compact <chat_id> [--target-tokens N]
      notebook compactions <chat_id>
      notebook expand-compaction <compaction_id>
      notebook restore-raw <chat_id> <compaction_id>
      notebook pin <entry_id>
      notebook unpin <entry_id>
    """
    usage = (
        "notebook budget <chat_id>\n"
        "  | notebook compact <chat_id> [--target-tokens N]\n"
        "  | notebook compactions <chat_id>\n"
        "  | notebook expand-compaction <compaction_id>\n"
        "  | notebook restore-raw <chat_id> <compaction_id>\n"
        "  | notebook pin <entry_id>\n"
        "  | notebook unpin <entry_id>"
    )
    if _argv_contains_null_byte(argv):
        return _null_byte_argument_error("notebook", usage)
    if len(argv) < 2:
        return _missing_text_argument_error("notebook", "action", usage)

    action = argv[1].strip().lower()
    if action not in {"budget", "compact", "compactions", "expand-compaction", "restore-raw", "pin", "unpin"}:
        return ArgvParseError("notebook", f"unknown notebook action: {argv[1]}", usage)

    if action in {"budget", "compactions"}:
        if len(argv) < 3 or not argv[2].strip():
            return _missing_text_argument_error("notebook", "chat_id", usage)
        if len(argv) > 3:
            return _unexpected_argument_error("notebook", argv[3], usage)
        return NotebookActionInput(action=action, target=argv[2])

    elif action == "compact":
        if len(argv) < 3 or not argv[2].strip():
            return _missing_text_argument_error("notebook", "chat_id", usage)
        chat_id = argv[2]
        target_tokens = None
        if len(argv) > 3:
            if argv[3] == "--target-tokens":
                if len(argv) < 5 or not argv[4].strip():
                    return _missing_text_argument_error("notebook", "target_tokens value", usage)
                try:
                    target_tokens = int(argv[4])
                except ValueError:
                    return ArgvParseError("notebook", f"target-tokens must be an integer: {argv[4]}", usage)
                if target_tokens <= 0:
                    return ArgvParseError("notebook", f"target-tokens must be a positive integer: {argv[4]}", usage)
                if len(argv) > 5:
                    return _unexpected_argument_error("notebook", argv[5], usage)
            else:
                return _unexpected_argument_error("notebook", argv[3], usage)
        return NotebookActionInput(action=action, target=chat_id, target_tokens=target_tokens)

    elif action == "expand-compaction":
        if len(argv) < 3 or not argv[2].strip():
            return _missing_text_argument_error("notebook", "compaction_id", usage)
        if len(argv) > 3:
            return _unexpected_argument_error("notebook", argv[3], usage)
        return NotebookActionInput(action=action, target=argv[2])

    elif action == "restore-raw":
        if len(argv) < 3 or not argv[2].strip():
            return _missing_text_argument_error("notebook", "chat_id", usage)
        if len(argv) < 4 or not argv[3].strip():
            return _missing_text_argument_error("notebook", "compaction_id", usage)
        if len(argv) > 4:
            return _unexpected_argument_error("notebook", argv[4], usage)
        return NotebookActionInput(action=action, target=argv[2], target_extra=argv[3])

    elif action in {"pin", "unpin"}:
        if len(argv) < 3 or not argv[2].strip():
            return _missing_text_argument_error("notebook", "entry_id", usage)
        if len(argv) > 3:
            return _unexpected_argument_error("notebook", argv[3], usage)
        return NotebookActionInput(action=action, target=argv[2])

    return ArgvParseError("notebook", "invalid notebook command configuration", usage)


def dispatch_retrieve(argv: tuple[str, ...]) -> RetrieveResult | ArgvParseError:
    """Dispatch argv for 'retrieve' to the FTS retrieval stub."""
    _validate_argv(argv)
    parsed = parse_retrieve_argv(argv)
    if isinstance(parsed, ArgvParseError):
        return parsed
    return run_retrieve(parsed)


def parse_revise_argv(argv: tuple[str, ...]) -> ReviseInput | ArgvParseError:
    """Parse argv tokens for 'revise' into a ReviseInput.

    Expected layout: (command_token, document_id, *basket_item_ids)
    """
    usage = "revise <document_id> [<basket_item_id> ...]"
    if _argv_contains_null_byte(argv):
        return _null_byte_argument_error(REVISE_COMMAND, usage)
    if len(argv) < 2 or not argv[1].strip():
        return _missing_text_argument_error(REVISE_COMMAND, "document_id", usage)
    for item_id in argv[2:]:
        if not item_id.strip():
            return _missing_text_argument_error(REVISE_COMMAND, "basket_item_id", usage)
    return ReviseInput(
        document_id=argv[1],
        basket_item_ids=tuple(argv[2:]),
    )


def parse_session_save_argv(argv: tuple[str, ...]) -> SessionSaveInput | ArgvParseError:
    """Parse argv tokens for 'session-save' into a SessionSaveInput.

    Expected layout: (command_token, document_id, session_id)
    """
    usage = "session-save <document_id> <session_id>"
    if _argv_contains_null_byte(argv):
        return _null_byte_argument_error(SESSION_SAVE_COMMAND, usage)
    if len(argv) < 3 or not argv[1].strip() or not argv[2].strip():
        return ArgvParseError(
            command=SESSION_SAVE_COMMAND,
            reason="missing required arguments: document_id and/or session_id",
            usage=usage,
        )
    if len(argv) > 3:
        return _unexpected_argument_error(SESSION_SAVE_COMMAND, argv[3], usage)
    return SessionSaveInput(
        document_id=argv[1],
        session_id=argv[2],
    )


def parse_session_resume_argv(argv: tuple[str, ...]) -> SessionResumeInput | ArgvParseError:
    """Parse argv tokens for 'session-resume' into a SessionResumeInput.

    Expected layout: (command_token, session_id)
    """
    usage = "session-resume <session_id>"
    if _argv_contains_null_byte(argv):
        return _null_byte_argument_error(SESSION_RESUME_COMMAND, usage)
    if len(argv) < 2 or not argv[1].strip():
        return _missing_text_argument_error(SESSION_RESUME_COMMAND, "session_id", usage)
    if len(argv) > 2:
        return _unexpected_argument_error(SESSION_RESUME_COMMAND, argv[2], usage)
    return SessionResumeInput(session_id=argv[1])


def dispatch_revise(argv: tuple[str, ...]) -> ReviseResult | ArgvParseError:
    """Dispatch argv for the 'revise' command to the engine stub."""
    _validate_argv(argv)
    parsed = parse_revise_argv(argv)
    if isinstance(parsed, ArgvParseError):
        return parsed
    return run_revise(parsed)


def dispatch_session_save(argv: tuple[str, ...]) -> SessionSaveResult | ArgvParseError:
    """Dispatch argv for the 'session-save' command to the engine stub."""
    _validate_argv(argv)
    parsed = parse_session_save_argv(argv)
    if isinstance(parsed, ArgvParseError):
        return parsed
    return run_session_save(parsed)


def dispatch_session_resume(argv: tuple[str, ...]) -> SessionResumeResult | ArgvParseError:
    """Dispatch argv for the 'session-resume' command to the engine stub."""
    _validate_argv(argv)
    parsed = parse_session_resume_argv(argv)
    if isinstance(parsed, ArgvParseError):
        return parsed
    return run_session_resume(parsed)


def _parse_text_pair_argv(
    argv: tuple[str, ...],
    command: str,
) -> tuple[str, str] | ArgvParseError:
    usage = f"{command} <original> <proposed>"
    if _argv_contains_null_byte(argv):
        return _null_byte_argument_error(command, usage)
    if len(argv) < 3:
        return ArgvParseError(
            command=command,
            reason="missing required arguments: original and/or proposed",
            usage=usage,
        )
    if len(argv) > 3:
        return _unexpected_argument_error(command, argv[3], usage)
    return argv[1], argv[2]


def parse_diff_preview_argv(argv: tuple[str, ...]) -> DiffPreviewInput | ArgvParseError:
    result = _parse_text_pair_argv(argv, DIFF_PREVIEW_COMMAND)
    if isinstance(result, ArgvParseError):
        return result
    return DiffPreviewInput(original=result[0], proposed=result[1])


def parse_patch_apply_argv(argv: tuple[str, ...]) -> PatchApplyInput | ArgvParseError:
    result = _parse_text_pair_argv(argv, PATCH_APPLY_COMMAND)
    if isinstance(result, ArgvParseError):
        return result
    return PatchApplyInput(original=result[0], proposed=result[1])


def parse_patch_reject_argv(argv: tuple[str, ...]) -> PatchRejectInput | ArgvParseError:
    result = _parse_text_pair_argv(argv, PATCH_REJECT_COMMAND)
    if isinstance(result, ArgvParseError):
        return result
    return PatchRejectInput(original=result[0], proposed=result[1])


def dispatch_diff_preview(argv: tuple[str, ...]) -> str | ArgvParseError:
    """Dispatch argv for 'diff-preview' to the diff_preview handler."""
    _validate_argv(argv)
    if len(argv) >= 2 and argv[1] in PATCH_REVIEW_ACTIONS:
        action = argv[1]
        result = _parse_text_pair_argv((argv[0], *argv[2:]), DIFF_PREVIEW_COMMAND)
        if isinstance(result, ArgvParseError):
            return result
        if action == "apply":
            return run_patch_apply(PatchApplyInput(original=result[0], proposed=result[1]))
        if action == "reject":
            return run_patch_reject(PatchRejectInput(original=result[0], proposed=result[1]))
        return run_diff_preview(DiffPreviewInput(original=result[0], proposed=result[1]))
    parsed = parse_diff_preview_argv(argv)
    if isinstance(parsed, ArgvParseError):
        return parsed
    return run_diff_preview(parsed)


def dispatch_patch_apply(argv: tuple[str, ...]) -> str | ArgvParseError:
    """Dispatch argv for 'patch-apply' to the diff_preview handler."""
    _validate_argv(argv)
    parsed = parse_patch_apply_argv(argv)
    if isinstance(parsed, ArgvParseError):
        return parsed
    return run_patch_apply(parsed)


def dispatch_patch_reject(argv: tuple[str, ...]) -> str | ArgvParseError:
    """Dispatch argv for 'patch-reject' to the diff_preview handler."""
    _validate_argv(argv)
    parsed = parse_patch_reject_argv(argv)
    if isinstance(parsed, ArgvParseError):
        return parsed
    return run_patch_reject(parsed)


@dataclass(frozen=True)
class UnknownCommandError:
    """Returned when argv[0] does not match any known partial-command token."""

    token: str
    known_tokens: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.token, str):
            raise TypeError("token must be a string")
        if not isinstance(self.known_tokens, tuple):
            raise TypeError("known_tokens must be a tuple")
        for t in self.known_tokens:
            if not isinstance(t, str):
                raise TypeError("each known token must be a string")


PartialCommandResult = Union[
    OpenProjectResult,
    RetrieveResult,
    BasketActionResult,
    ExportHandoffResult,
    ReviseResult,
    SessionSaveResult,
    SessionResumeResult,
    str,
]

CommandDispatchResult = Union[PartialCommandResult, ArgvParseError, UnknownCommandError]


@dataclass(frozen=True)
class CommandOutput:
    """Normalized output from any dispatch_command call.

    status values: "ok" | "stub" | "parse_error" | "unknown_command"
    Lets callers check ready/status and, for unknown commands, accepted tokens
    without isinstance-switching the full result union.
    """

    status: str
    ready: bool
    message: str
    blocker_lane: str = ""
    blocker_step: str = ""
    blocker_reason: str = ""
    known_tokens: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.status, str):
            raise TypeError("status must be a string")
        if not isinstance(self.ready, bool):
            raise TypeError("ready must be a boolean")
        if not isinstance(self.message, str):
            raise TypeError("message must be a string")
        if not isinstance(self.blocker_lane, str):
            raise TypeError("blocker_lane must be a string")
        if not isinstance(self.blocker_step, str):
            raise TypeError("blocker_step must be a string")
        if not isinstance(self.blocker_reason, str):
            raise TypeError("blocker_reason must be a string")
        if not isinstance(self.known_tokens, tuple):
            raise TypeError("known_tokens must be a tuple")
        for t in self.known_tokens:
            if not isinstance(t, str):
                raise TypeError("each known token must be a string")

        allowed_statuses = {"ok", "stub", "parse_error", "unknown_command"}
        if self.status not in allowed_statuses:
            raise ValueError(f"status must be one of {allowed_statuses}")


@dataclass(frozen=True)
class CommandDispatchContractEntry:
    token: str
    demo_path_step: str
    minimal_argv: tuple[str, ...]
    status: str
    ready: bool
    blocker_lane: str = ""
    blocker_step: str = ""
    blocker_reason: str = ""
    output_status: str = ""
    exit_code: int = -1


@dataclass(frozen=True)
class CommandCompatDispatchContractEntry:
    token: str
    canonical_token: str
    demo_path_step: str
    minimal_argv: tuple[str, ...]
    canonical_minimal_argv: tuple[str, ...]
    status: str
    ready: bool
    output_status: str
    exit_code: int
    canonical_output_status: str
    canonical_exit_code: int
    blocker_lane: str = ""
    blocker_step: str = ""
    blocker_reason: str = ""


@dataclass(frozen=True)
class CommandDispatchSmokeEntry:
    token: str
    demo_path_step: str
    command: tuple[str, ...]
    exit_code: int
    output_status: str
    ready: bool
    message: str
    blocker_lane: str = ""
    blocker_step: str = ""
    blocker_reason: str = ""


@dataclass(frozen=True)
class CommandCompatDispatchSmokeEntry:
    token: str
    canonical_token: str
    demo_path_step: str
    command: tuple[str, ...]
    canonical_command: tuple[str, ...]
    exit_code: int
    canonical_exit_code: int
    output_status: str
    canonical_output_status: str
    ready: bool
    message: str
    canonical_message: str
    blocker_lane: str = ""
    blocker_step: str = ""
    blocker_reason: str = ""


@dataclass(frozen=True)
class CommandAcceptedTokenEntry:
    token: str
    token_kind: str
    canonical_token: str
    demo_path_step: str
    ready: bool
    output_status: str
    exit_code: int
    command: tuple[str, ...]
    blocker_lane: str = ""
    blocker_step: str = ""
    blocker_reason: str = ""


@dataclass(frozen=True)
class CommandDispatchReadinessSummary:
    program: str
    ready: bool
    command_count: int
    ready_command_count: int
    stub_command_count: int
    ready_tokens: tuple[str, ...]
    stub_tokens: tuple[str, ...]
    blockers: tuple[tuple[str, str, str, str], ...]
    next_blocker: tuple[str, str, str, str] | None
    commands: tuple[tuple[str, str, int, str], ...]
    fingerprint: str


@dataclass(frozen=True)
class CommandDispatchOutcomeEntry:
    token: str
    demo_path_step: str
    ready: bool
    output_status: str
    exit_code: int
    command: tuple[str, ...]
    blocker_lane: str = ""
    blocker_step: str = ""
    blocker_reason: str = ""


@dataclass(frozen=True)
class CommandDispatchDemoPathStepEntry:
    step: str
    status: str
    tokens: tuple[str, ...]
    blocker_lanes: tuple[str, ...] = ()


def command_dispatch_contract() -> tuple[CommandDispatchContractEntry, ...]:
    """Return the smoke-testable command surface in canonical dispatch order."""
    _validate_command_dispatch_tables()
    entries: list[CommandDispatchContractEntry] = []
    for token in COMMAND_TOKENS:
        minimal_argv = DEMO_PATH_MINIMAL_ARGV[token]
        status = "ready" if token in READY_COMMAND_TOKENS else "stub"
        blocker_lane = "" if status == "ready" else STUB_COMMAND_BLOCKERS[token]
        output = format_dispatch_result(dispatch_command(minimal_argv))
        exit_code, _ = cli_main(minimal_argv)
        if output.status == "parse_error":
            raise ValueError(f"minimal argv for '{token}' produced a parse error")
        if output.status == "unknown_command":
            raise ValueError(f"minimal argv for '{token}' produced an unknown command")
        if output.ready != (status == "ready"):
            raise ValueError(f"minimal argv for '{token}' disagrees with ready status")
        if status == "stub" and (not output.blocker_step or not output.blocker_reason):
            raise ValueError(f"minimal argv for '{token}' is missing structured blocker evidence")
        if status == "ready" and (output.blocker_step or output.blocker_reason):
            raise ValueError(f"minimal argv for '{token}' unexpectedly reports blocker evidence")
        entries.append(
            CommandDispatchContractEntry(
                token=token,
                demo_path_step=COMMAND_DEMO_PATH_STEPS[token],
                minimal_argv=minimal_argv,
                status=status,
                ready=status == "ready",
                blocker_lane=blocker_lane,
                blocker_step=output.blocker_step,
                blocker_reason=output.blocker_reason,
                output_status=output.status,
                exit_code=exit_code,
            )
        )
    return tuple(entries)


def command_dispatch_outcome_table(
    program: str = "qual-bootstrap",
) -> tuple[CommandDispatchOutcomeEntry, ...]:
    """Return smoke-testable CLI outcomes for the canonical demo-path commands."""

    entries = tuple(
        CommandDispatchOutcomeEntry(
            token=entry.token,
            demo_path_step=entry.demo_path_step,
            ready=entry.ready,
            output_status=entry.output_status,
            exit_code=entry.exit_code,
            command=entry.command,
            blocker_lane=entry.blocker_lane,
            blocker_step=entry.blocker_step,
            blocker_reason=entry.blocker_reason,
        )
        for entry in command_dispatch_smoke_contract(program=program)
    )
    _validate_command_dispatch_outcome_table(entries, program)
    return entries


def _validate_command_dispatch_outcome_table(
    entries: tuple[CommandDispatchOutcomeEntry, ...],
    program: str,
) -> None:
    if tuple(entry.token for entry in entries) != COMMAND_TOKENS:
        raise ValueError("Command dispatch outcome table token order is inconsistent")
    if tuple(entry.demo_path_step for entry in entries) != tuple(
        COMMAND_DEMO_PATH_STEPS[token] for token in COMMAND_TOKENS
    ):
        raise ValueError("Command dispatch outcome table demo-path steps are inconsistent")
    for entry in entries:
        if entry.command[0] != program:
            raise ValueError("Command dispatch outcome table program is inconsistent")
        if entry.ready != (entry.output_status == "ok" and entry.exit_code == CLI_EXIT_OK):
            raise ValueError("Command dispatch outcome readiness is inconsistent")
        if entry.ready and (entry.blocker_lane or entry.blocker_step or entry.blocker_reason):
            raise ValueError("Ready command dispatch outcome unexpectedly has blocker evidence")
        if not entry.ready and not (entry.blocker_lane and entry.blocker_step and entry.blocker_reason):
            raise ValueError("Blocked command dispatch outcome is missing blocker evidence")


def command_dispatch_readiness(
    program: str = "qual-bootstrap",
) -> CommandDispatchReadinessSummary:
    """Return structured readiness for the current demo-path dispatch surface."""

    smoke_entries = command_dispatch_smoke_contract(program=program)
    ready_entries = tuple(entry for entry in smoke_entries if entry.ready)
    stub_entries = tuple(entry for entry in smoke_entries if not entry.ready)
    blockers = tuple(
        (entry.token, entry.blocker_lane, entry.blocker_step, entry.blocker_reason)
        for entry in stub_entries
    )
    next_blocker = command_dispatch_next_blocker(smoke_entries)
    commands = tuple(
        (entry.token, entry.output_status, entry.exit_code, _format_command_line(entry.command))
        for entry in smoke_entries
    )
    summary = CommandDispatchReadinessSummary(
        program=program,
        ready=len(ready_entries) == len(smoke_entries),
        command_count=len(smoke_entries),
        ready_command_count=len(ready_entries),
        stub_command_count=len(stub_entries),
        ready_tokens=tuple(entry.token for entry in ready_entries),
        stub_tokens=tuple(entry.token for entry in stub_entries),
        blockers=blockers,
        next_blocker=next_blocker,
        commands=commands,
        fingerprint=_command_dispatch_readiness_fingerprint(
            program=program,
            commands=commands,
            blockers=blockers,
            next_blocker=next_blocker,
        ),
    )
    _validate_command_dispatch_readiness(summary, smoke_entries, program)
    return summary


def _validate_command_dispatch_readiness(
    summary: CommandDispatchReadinessSummary,
    smoke_entries: tuple[CommandDispatchSmokeEntry, ...],
    program: str,
) -> None:
    if summary.program != program:
        raise ValueError("Command dispatch readiness program is inconsistent")
    if summary.command_count != len(smoke_entries):
        raise ValueError("Command dispatch readiness command count is inconsistent")
    ready_entries = tuple(entry for entry in smoke_entries if entry.ready)
    stub_entries = tuple(entry for entry in smoke_entries if not entry.ready)
    if summary.ready != (len(ready_entries) == len(smoke_entries)):
        raise ValueError("Command dispatch readiness flag is inconsistent")
    if summary.ready_command_count != len(ready_entries):
        raise ValueError("Command dispatch readiness ready count is inconsistent")
    if summary.stub_command_count != len(stub_entries):
        raise ValueError("Command dispatch readiness stub count is inconsistent")
    if summary.ready_tokens != tuple(entry.token for entry in ready_entries):
        raise ValueError("Command dispatch readiness ready token order is inconsistent")
    if summary.stub_tokens != tuple(entry.token for entry in stub_entries):
        raise ValueError("Command dispatch readiness stub token order is inconsistent")
    if summary.blockers != tuple(
        (entry.token, entry.blocker_lane, entry.blocker_step, entry.blocker_reason)
        for entry in stub_entries
    ):
        raise ValueError("Command dispatch readiness blockers are inconsistent")
    if summary.next_blocker != command_dispatch_next_blocker(smoke_entries):
        raise ValueError("Command dispatch readiness next blocker is inconsistent")
    if summary.commands != tuple(
        (entry.token, entry.output_status, entry.exit_code, _format_command_line(entry.command))
        for entry in smoke_entries
    ):
        raise ValueError("Command dispatch readiness commands are inconsistent")
    expected_fingerprint = _command_dispatch_readiness_fingerprint(
        program=summary.program,
        commands=summary.commands,
        blockers=summary.blockers,
        next_blocker=summary.next_blocker,
    )
    if summary.fingerprint != expected_fingerprint:
        raise ValueError("Command dispatch readiness fingerprint is inconsistent")


def _command_dispatch_readiness_fingerprint(
    *,
    program: str,
    commands: tuple[tuple[str, str, int, str], ...],
    blockers: tuple[tuple[str, str, str, str], ...],
    next_blocker: tuple[str, str, str, str] | None,
) -> str:
    """Return a stable fingerprint for command order, status, and blocker evidence."""

    rows = [
        f"program={program}",
        *(
            f"command={token}|status={status}|exit={exit_code}|argv={command}"
            for token, status, exit_code, command in commands
        ),
        *(
            f"blocker={token}|lane={lane}|step={step}|reason={reason}"
            for token, lane, step, reason in blockers
        ),
        (
            "next-blocker=none"
            if next_blocker is None
            else "next-blocker=" + "|".join(next_blocker)
        ),
    ]
    return sha256("\n".join(rows).encode("utf-8")).hexdigest()


def command_dispatch_smoke_contract(
    program: str = "qual-bootstrap",
) -> tuple[CommandDispatchSmokeEntry, ...]:
    """Return executable smoke evidence for every canonical demo-path command."""
    entries: list[CommandDispatchSmokeEntry] = []
    for contract in command_dispatch_contract():
        output = format_dispatch_result(dispatch_command(contract.minimal_argv))
        exit_code, message = cli_main(contract.minimal_argv)
        if exit_code != contract.exit_code:
            raise ValueError(f"smoke exit for '{contract.token}' disagrees with dispatch contract")
        if output.status != contract.output_status:
            raise ValueError(f"smoke status for '{contract.token}' disagrees with dispatch contract")
        if output.ready != contract.ready:
            raise ValueError(f"smoke readiness for '{contract.token}' disagrees with dispatch contract")
        if output.blocker_step != contract.blocker_step:
            raise ValueError(f"smoke blocker step for '{contract.token}' disagrees with dispatch contract")
        if output.blocker_reason != contract.blocker_reason:
            raise ValueError(f"smoke blocker reason for '{contract.token}' disagrees with dispatch contract")
        entries.append(
            CommandDispatchSmokeEntry(
                token=contract.token,
                demo_path_step=contract.demo_path_step,
                command=(program, *contract.minimal_argv),
                exit_code=exit_code,
                output_status=output.status,
                ready=output.ready,
                message=message,
                blocker_lane=contract.blocker_lane,
                blocker_step=output.blocker_step,
                blocker_reason=output.blocker_reason,
            )
        )
    return tuple(entries)


def command_dispatch_smoke_commands(
    program: str = "qual-bootstrap",
) -> tuple[tuple[str, ...], ...]:
    """Return executable CLI smoke commands in canonical demo-path order."""

    entries = command_dispatch_smoke_contract(program=program)
    commands = tuple(entry.command for entry in entries)
    if commands != tuple((program, *entry.minimal_argv) for entry in command_dispatch_contract()):
        raise ValueError("Command dispatch smoke commands are inconsistent with the dispatch contract")
    return commands


def command_compat_dispatch_contract() -> tuple[CommandCompatDispatchContractEntry, ...]:
    """Return smoke argv for accepted compatibility tokens in deterministic order."""
    _validate_command_dispatch_tables()
    entries: list[CommandCompatDispatchContractEntry] = []
    compat_tokens = (PATCH_REVIEW_COMMAND, *COMMAND_ALIASES)
    for token in compat_tokens:
        canonical = DIFF_PREVIEW_COMMAND if token == PATCH_REVIEW_COMMAND else COMMAND_ALIASES[token]
        canonical_argv = DEMO_PATH_MINIMAL_ARGV[canonical]
        minimal_argv = (token, *canonical_argv[1:])
        output = format_dispatch_result(dispatch_command(minimal_argv))
        exit_code, _ = cli_main(minimal_argv)
        canonical_output = format_dispatch_result(dispatch_command(canonical_argv))
        canonical_exit_code, _ = cli_main(canonical_argv)
        if output.status in {"parse_error", "unknown_command"}:
            raise ValueError(f"compat argv for '{token}' did not route to '{canonical}'")
        if output.ready != canonical_output.ready:
            raise ValueError(f"compat argv for '{token}' disagrees with '{canonical}' ready status")
        if output.status != canonical_output.status:
            raise ValueError(f"compat argv for '{token}' disagrees with '{canonical}' output status")
        if exit_code != canonical_exit_code:
            raise ValueError(f"compat argv for '{token}' disagrees with '{canonical}' exit code")
        if not output.ready and (not output.blocker_step or not output.blocker_reason):
            raise ValueError(f"compat argv for '{token}' is missing structured blocker evidence")
        if output.ready and (output.blocker_step or output.blocker_reason):
            raise ValueError(f"compat argv for '{token}' unexpectedly reports blocker evidence")
        blocker_lane = "" if output.ready else STUB_COMMAND_BLOCKERS[canonical]
        entries.append(
            CommandCompatDispatchContractEntry(
                token=token,
                canonical_token=canonical,
                demo_path_step=COMMAND_DEMO_PATH_STEPS[canonical],
                minimal_argv=minimal_argv,
                canonical_minimal_argv=canonical_argv,
                status="ready" if output.ready else "stub",
                ready=output.ready,
                blocker_lane=blocker_lane,
                blocker_step=output.blocker_step,
                blocker_reason=output.blocker_reason,
                output_status=output.status,
                exit_code=exit_code,
                canonical_output_status=canonical_output.status,
                canonical_exit_code=canonical_exit_code,
            )
        )
    return tuple(entries)


def command_compat_dispatch_smoke_contract(
    program: str = "qual-bootstrap",
) -> tuple[CommandCompatDispatchSmokeEntry, ...]:
    """Return executable smoke evidence for every accepted compatibility token."""
    entries: list[CommandCompatDispatchSmokeEntry] = []
    for contract in command_compat_dispatch_contract():
        output = format_dispatch_result(dispatch_command(contract.minimal_argv))
        canonical_output = format_dispatch_result(dispatch_command(contract.canonical_minimal_argv))
        exit_code, message = cli_main(contract.minimal_argv)
        canonical_exit_code, canonical_message = cli_main(contract.canonical_minimal_argv)
        if exit_code != contract.exit_code:
            raise ValueError(f"compat smoke exit for '{contract.token}' disagrees with contract")
        if canonical_exit_code != contract.canonical_exit_code:
            raise ValueError(f"compat canonical smoke exit for '{contract.token}' disagrees with contract")
        if output.status != contract.output_status:
            raise ValueError(f"compat smoke status for '{contract.token}' disagrees with contract")
        if canonical_output.status != contract.canonical_output_status:
            raise ValueError(f"compat canonical smoke status for '{contract.token}' disagrees with contract")
        if output.ready != contract.ready or canonical_output.ready != contract.ready:
            raise ValueError(f"compat smoke readiness for '{contract.token}' disagrees with contract")
        if output.blocker_step != contract.blocker_step:
            raise ValueError(f"compat smoke blocker step for '{contract.token}' disagrees with contract")
        if output.blocker_reason != contract.blocker_reason:
            raise ValueError(f"compat smoke blocker reason for '{contract.token}' disagrees with contract")
        entries.append(
            CommandCompatDispatchSmokeEntry(
                token=contract.token,
                canonical_token=contract.canonical_token,
                demo_path_step=contract.demo_path_step,
                command=(program, *contract.minimal_argv),
                canonical_command=(program, *contract.canonical_minimal_argv),
                exit_code=exit_code,
                canonical_exit_code=canonical_exit_code,
                output_status=output.status,
                canonical_output_status=canonical_output.status,
                ready=output.ready,
                message=message,
                canonical_message=canonical_message,
                blocker_lane=contract.blocker_lane,
                blocker_step=output.blocker_step,
                blocker_reason=output.blocker_reason,
            )
        )
    return tuple(entries)


def command_compat_dispatch_smoke_commands(
    program: str = "qual-bootstrap",
) -> tuple[tuple[str, ...], ...]:
    """Return executable CLI smoke commands for compatibility aliases."""

    entries = command_compat_dispatch_smoke_contract(program=program)
    commands = tuple(entry.command for entry in entries)
    if commands != tuple((program, *entry.minimal_argv) for entry in command_compat_dispatch_contract()):
        raise ValueError("Compat dispatch smoke commands are inconsistent with the compat contract")
    return commands


def command_accepted_token_contract(
    program: str = "qual-bootstrap",
) -> tuple[CommandAcceptedTokenEntry, ...]:
    """Return every accepted dispatch token mapped to its canonical command.

    The rows are intentionally executable smoke entries, not catalog metadata, so
    downstream lanes can verify migration-safe aliases against real CLI results.
    """

    canonical_entries = command_dispatch_smoke_contract(program=program)
    compat_entries = command_compat_dispatch_smoke_contract(program=program)
    entries: tuple[CommandAcceptedTokenEntry, ...] = (
        *(
            CommandAcceptedTokenEntry(
                token=entry.token,
                token_kind="canonical",
                canonical_token=entry.token,
                demo_path_step=entry.demo_path_step,
                ready=entry.ready,
                output_status=entry.output_status,
                exit_code=entry.exit_code,
                command=entry.command,
                blocker_lane=entry.blocker_lane,
                blocker_step=entry.blocker_step,
                blocker_reason=entry.blocker_reason,
            )
            for entry in canonical_entries
        ),
        *(
            CommandAcceptedTokenEntry(
                token=entry.token,
                token_kind="compat",
                canonical_token=entry.canonical_token,
                demo_path_step=entry.demo_path_step,
                ready=entry.ready,
                output_status=entry.output_status,
                exit_code=entry.exit_code,
                command=entry.command,
                blocker_lane=entry.blocker_lane,
                blocker_step=entry.blocker_step,
                blocker_reason=entry.blocker_reason,
            )
            for entry in compat_entries
        ),
    )
    _validate_command_accepted_token_contract(entries, program)
    return entries


def _validate_command_accepted_token_contract(
    entries: tuple[CommandAcceptedTokenEntry, ...],
    program: str,
) -> None:
    if tuple(entry.token for entry in entries) != known_command_tokens():
        raise ValueError("Command accepted token contract order is inconsistent")
    for entry in entries:
        if entry.token_kind not in {"canonical", "compat"}:
            raise ValueError("Command accepted token kind is inconsistent")
        if entry.command[0] != program:
            raise ValueError("Command accepted token program is inconsistent")
        if entry.token_kind == "canonical" and entry.token != entry.canonical_token:
            raise ValueError("Canonical command token must map to itself")
        if entry.token_kind == "compat" and entry.token == entry.canonical_token:
            raise ValueError("Compat command token must map to a canonical token")
        if entry.canonical_token not in COMMAND_TOKENS:
            raise ValueError("Command accepted token canonical target is unknown")
        if entry.demo_path_step != COMMAND_DEMO_PATH_STEPS[entry.canonical_token]:
            raise ValueError("Command accepted token demo-path step is inconsistent")
        if entry.ready != (entry.output_status == "ok" and entry.exit_code == CLI_EXIT_OK):
            raise ValueError("Command accepted token readiness is inconsistent")
        if entry.ready and (entry.blocker_lane or entry.blocker_step or entry.blocker_reason):
            raise ValueError("Ready accepted token unexpectedly has blocker evidence")
        if not entry.ready and not (entry.blocker_lane and entry.blocker_step and entry.blocker_reason):
            raise ValueError("Blocked accepted token is missing blocker evidence")


def _format_command_line(command: tuple[str, ...]) -> str:
    return " ".join(part.replace("\n", "\\n") for part in command)


def command_dispatch_next_blocker(
    smoke_entries: tuple[CommandDispatchSmokeEntry, ...] | None = None,
) -> tuple[str, str, str, str] | None:
    """Return the first blocked demo-path command in canonical dispatch order."""

    entries = smoke_entries if smoke_entries is not None else command_dispatch_smoke_contract()
    for entry in entries:
        if not entry.ready:
            return (entry.token, entry.blocker_lane, entry.blocker_step, entry.blocker_reason)
    return None


def command_dispatch_blocker_lane_summary(
    smoke_entries: tuple[CommandDispatchSmokeEntry, ...] | None = None,
) -> tuple[tuple[str, int, tuple[str, ...]], ...]:
    """Return blocked command counts grouped by owning lane in dispatch order."""

    entries = smoke_entries if smoke_entries is not None else command_dispatch_smoke_contract()
    lane_tokens: dict[str, list[str]] = {}
    for entry in entries:
        if entry.ready:
            continue
        lane_tokens.setdefault(entry.blocker_lane, []).append(entry.token)
    return tuple((lane, len(tokens), tuple(tokens)) for lane, tokens in lane_tokens.items())


def _format_blocker_lane_summary(summary: tuple[tuple[str, int, tuple[str, ...]], ...]) -> str:
    if not summary:
        return "none"
    return "; ".join(f"{lane}={count}[{','.join(tokens)}]" for lane, count, tokens in summary)


def command_dispatch_demo_path_step_readiness(
    smoke_entries: tuple[CommandDispatchSmokeEntry, ...] | None = None,
) -> tuple[tuple[str, str, tuple[str, ...]], ...]:
    """Return readiness grouped by canonical demo-path step in command order."""

    entries = smoke_entries if smoke_entries is not None else command_dispatch_smoke_contract()
    grouped: dict[str, list[CommandDispatchSmokeEntry]] = {}
    for entry in entries:
        grouped.setdefault(entry.demo_path_step, []).append(entry)

    expected_steps = command_demo_path_step_order()
    actual_steps = tuple(grouped)
    if actual_steps != expected_steps:
        raise ValueError("Command dispatch demo-path step order is inconsistent")

    readiness: list[tuple[str, str, tuple[str, ...]]] = []
    for step in expected_steps:
        step_entries = grouped[step]
        status = "ready" if all(entry.ready for entry in step_entries) else "stub"
        readiness.append((step, status, tuple(entry.token for entry in step_entries)))
    return tuple(readiness)


def command_dispatch_demo_path_step_contract(
    smoke_entries: tuple[CommandDispatchSmokeEntry, ...] | None = None,
) -> tuple[CommandDispatchDemoPathStepEntry, ...]:
    """Return demo-path readiness with blocked lanes grouped per step."""

    entries = smoke_entries if smoke_entries is not None else command_dispatch_smoke_contract()
    by_step: dict[str, list[CommandDispatchSmokeEntry]] = {}
    for entry in entries:
        by_step.setdefault(entry.demo_path_step, []).append(entry)

    contract: list[CommandDispatchDemoPathStepEntry] = []
    for step, status, tokens in command_dispatch_demo_path_step_readiness(entries):
        blocker_lanes: list[str] = []
        for entry in by_step[step]:
            if entry.ready or entry.blocker_lane in blocker_lanes:
                continue
            blocker_lanes.append(entry.blocker_lane)
        contract.append(
            CommandDispatchDemoPathStepEntry(
                step=step,
                status=status,
                tokens=tokens,
                blocker_lanes=tuple(blocker_lanes),
            )
        )
    result = tuple(contract)
    _validate_command_dispatch_demo_path_step_contract(result, entries)
    return result


def _validate_command_dispatch_demo_path_step_contract(
    contract: tuple[CommandDispatchDemoPathStepEntry, ...],
    smoke_entries: tuple[CommandDispatchSmokeEntry, ...],
) -> None:
    step_readiness = command_dispatch_demo_path_step_readiness(smoke_entries)
    if tuple(entry.step for entry in contract) != tuple(step for step, _, _ in step_readiness):
        raise ValueError("Command dispatch demo-path step contract order is inconsistent")
    for entry, (step, status, tokens) in zip(contract, step_readiness):
        if (entry.step, entry.status, entry.tokens) != (step, status, tokens):
            raise ValueError("Command dispatch demo-path step contract readiness is inconsistent")
        step_entries = tuple(item for item in smoke_entries if item.demo_path_step == entry.step)
        expected_lanes = tuple(
            dict.fromkeys(item.blocker_lane for item in step_entries if not item.ready)
        )
        if entry.blocker_lanes != expected_lanes:
            raise ValueError("Command dispatch demo-path step contract blockers are inconsistent")
        if entry.status == "ready" and entry.blocker_lanes:
            raise ValueError("Ready demo-path step unexpectedly has blocker lanes")
        if entry.status == "stub" and not entry.blocker_lanes:
            raise ValueError("Stubbed demo-path step is missing blocker lanes")


def _format_demo_path_step_blockers(
    step_contract: tuple[CommandDispatchDemoPathStepEntry, ...],
) -> str:
    blocked = tuple(entry for entry in step_contract if entry.blocker_lanes)
    if not blocked:
        return "none"
    return "; ".join(f"{entry.step}={','.join(entry.blocker_lanes)}" for entry in blocked)


def _format_demo_path_step_readiness(
    step_readiness: tuple[tuple[str, str, tuple[str, ...]], ...],
) -> str:
    if not step_readiness:
        return "none"
    return "; ".join(
        f"{step}={status}[{','.join(tokens)}]" for step, status, tokens in step_readiness
    )


def command_blocker_lane_for_step(blocker_step: str) -> str:
    """Return the owning lane for a structured stub blocker step."""

    _validate_command_dispatch_tables()
    return STUB_BLOCKER_LANES_BY_STEP.get(blocker_step, "")


def command_dispatch_handoff_evidence(
    program: str = "qual-bootstrap",
) -> tuple[tuple[str, str], ...]:
    """Return deterministic smoke evidence for the current command surface.

    The evidence is derived from executable dispatch smoke contracts, so handoff
    tooling can report command readiness without re-implementing argv layouts or
    parsing stub output text.
    """

    smoke_entries = command_dispatch_smoke_contract(program=program)
    compat_entries = command_compat_dispatch_smoke_contract(program=program)
    ready_entries = tuple(entry for entry in smoke_entries if entry.ready)
    stub_entries = tuple(entry for entry in smoke_entries if not entry.ready)
    next_blocker = command_dispatch_next_blocker(smoke_entries)
    readiness = command_dispatch_readiness(program=program)
    blocker_lane_summary = command_dispatch_blocker_lane_summary(smoke_entries)
    step_readiness = command_dispatch_demo_path_step_readiness(smoke_entries)
    step_contract = command_dispatch_demo_path_step_contract(smoke_entries)
    ready_steps = tuple(step for step, status, _ in step_readiness if status == "ready")
    stub_steps = tuple(step for step, status, _ in step_readiness if status == "stub")
    evidence: tuple[tuple[str, str], ...] = (
        ("program", program),
        ("ready", "true" if len(ready_entries) == len(smoke_entries) else "false"),
        ("command-count", str(len(smoke_entries))),
        ("accepted-token-count", str(len(known_command_tokens()))),
        ("compat-command-count", str(len(compat_entries))),
        ("ready-command-count", str(len(ready_entries))),
        ("stub-command-count", str(len(stub_entries))),
        ("readiness-fingerprint", readiness.fingerprint),
        ("demo-path-step-count", str(len(step_readiness))),
        ("ready-demo-path-steps", ",".join(ready_steps) or "none"),
        ("stub-demo-path-steps", ",".join(stub_steps) or "none"),
        ("demo-path-step-readiness", _format_demo_path_step_readiness(step_readiness)),
        ("demo-path-step-blockers", _format_demo_path_step_blockers(step_contract)),
        ("blocker-lane-counts", _format_blocker_lane_summary(blocker_lane_summary)),
        (
            "next-blocker",
            (
                "none"
                if next_blocker is None
                else f"{next_blocker[0]}: {next_blocker[1]}: {next_blocker[2]}: {next_blocker[3]}"
            ),
        ),
        *(
            (
                f"command:{entry.token}",
                (
                    _format_command_line(entry.command)
                    + f" | step={entry.demo_path_step}"
                    + f" | status={entry.output_status}"
                    + f" | exit={entry.exit_code}"
                ),
            )
            for entry in smoke_entries
        ),
        *(
            (
                f"blocker:{entry.token}",
                f"{entry.blocker_lane}: {entry.blocker_step}: {entry.blocker_reason}",
            )
            for entry in stub_entries
        ),
        *(
            (
                f"compat:{entry.token}",
                (
                    _format_command_line(entry.command)
                    + f" -> {entry.canonical_token}"
                    + f" | step={entry.demo_path_step}"
                    + f" | status={entry.output_status}"
                    + f" | exit={entry.exit_code}"
                ),
            )
            for entry in compat_entries
        ),
    )
    _validate_command_dispatch_handoff_evidence(evidence, smoke_entries, compat_entries, program)
    return evidence


def _validate_command_dispatch_handoff_evidence(
    evidence: tuple[tuple[str, str], ...],
    smoke_entries: tuple[CommandDispatchSmokeEntry, ...],
    compat_entries: tuple[CommandCompatDispatchSmokeEntry, ...],
    program: str,
) -> None:
    if not evidence or evidence[0] != ("program", program):
        raise ValueError("Command dispatch handoff evidence program is inconsistent")
    keys = tuple(key for key, _ in evidence)
    if len(keys) != len(set(keys)):
        raise ValueError("Command dispatch handoff evidence keys must be unique")
    command_keys = tuple(key for key in keys if key.startswith("command:"))
    if command_keys != tuple(f"command:{entry.token}" for entry in smoke_entries):
        raise ValueError("Command dispatch handoff evidence command order is inconsistent")
    blocker_entries = tuple(entry for entry in smoke_entries if not entry.ready)
    blocker_keys = tuple(key for key in keys if key.startswith("blocker:"))
    if blocker_keys != tuple(f"blocker:{entry.token}" for entry in blocker_entries):
        raise ValueError("Command dispatch handoff evidence blocker order is inconsistent")
    compat_keys = tuple(key for key in keys if key.startswith("compat:"))
    if compat_keys != tuple(f"compat:{entry.token}" for entry in compat_entries):
        raise ValueError("Command dispatch handoff evidence compat order is inconsistent")
    evidence_by_key = dict(evidence)
    step_readiness = command_dispatch_demo_path_step_readiness(smoke_entries)
    step_contract = command_dispatch_demo_path_step_contract(smoke_entries)
    if evidence_by_key.get("demo-path-step-count") != str(len(step_readiness)):
        raise ValueError("Command dispatch handoff evidence demo-path step count is inconsistent")
    expected_ready_steps = ",".join(
        step for step, status, _ in step_readiness if status == "ready"
    ) or "none"
    if evidence_by_key.get("ready-demo-path-steps") != expected_ready_steps:
        raise ValueError("Command dispatch handoff evidence ready demo-path steps are inconsistent")
    expected_stub_steps = ",".join(
        step for step, status, _ in step_readiness if status == "stub"
    ) or "none"
    if evidence_by_key.get("stub-demo-path-steps") != expected_stub_steps:
        raise ValueError("Command dispatch handoff evidence stub demo-path steps are inconsistent")
    expected_step_readiness = _format_demo_path_step_readiness(step_readiness)
    if evidence_by_key.get("demo-path-step-readiness") != expected_step_readiness:
        raise ValueError("Command dispatch handoff evidence demo-path readiness is inconsistent")
    expected_step_blockers = _format_demo_path_step_blockers(step_contract)
    if evidence_by_key.get("demo-path-step-blockers") != expected_step_blockers:
        raise ValueError("Command dispatch handoff evidence demo-path blockers are inconsistent")
    for entry in compat_entries:
        compat_value = evidence_by_key[f"compat:{entry.token}"]
        if f" | step={entry.demo_path_step}" not in compat_value:
            raise ValueError("Command dispatch handoff evidence compat step is missing")
    required_keys = {
        "ready",
        "command-count",
        "accepted-token-count",
        "compat-command-count",
        "ready-command-count",
        "stub-command-count",
        "demo-path-step-count",
        "ready-demo-path-steps",
        "stub-demo-path-steps",
        "demo-path-step-readiness",
        "demo-path-step-blockers",
        "blocker-lane-counts",
        "next-blocker",
    }
    if not required_keys <= set(keys):
        raise ValueError("Command dispatch handoff evidence summary keys are incomplete")
    if evidence_by_key["accepted-token-count"] != str(len(known_command_tokens())):
        raise ValueError("Command dispatch handoff evidence accepted token count is inconsistent")
    if evidence_by_key["compat-command-count"] != str(len(compat_entries)):
        raise ValueError("Command dispatch handoff evidence compat count is inconsistent")
    readiness = command_dispatch_readiness(program=program)
    if evidence_by_key.get("readiness-fingerprint") != readiness.fingerprint:
        raise ValueError("Command dispatch handoff evidence fingerprint is inconsistent")
    expected_lane_summary = _format_blocker_lane_summary(command_dispatch_blocker_lane_summary(smoke_entries))
    if evidence_by_key["blocker-lane-counts"] != expected_lane_summary:
        raise ValueError("Command dispatch handoff evidence blocker lane summary is inconsistent")
    expected_next_blocker = command_dispatch_next_blocker(smoke_entries)
    next_blocker_value = evidence_by_key["next-blocker"]
    if expected_next_blocker is None:
        if next_blocker_value != "none":
            raise ValueError("Command dispatch handoff evidence next blocker is inconsistent")
    else:
        expected = (
            f"{expected_next_blocker[0]}: {expected_next_blocker[1]}: "
            f"{expected_next_blocker[2]}: {expected_next_blocker[3]}"
        )
        if next_blocker_value != expected:
            raise ValueError("Command dispatch handoff evidence next blocker is inconsistent")


def format_dispatch_result(result: CommandDispatchResult) -> CommandOutput:
    """Normalize any dispatch_command result into a CommandOutput.

    Callers that only need ready/status never have to isinstance-check the full
    result union themselves.  The three status codes "stub", "parse_error", and
    "unknown_command" each map to ready=False; "ok" maps to ready=True.
    """
    if isinstance(result, UnknownCommandError):
        tokens = ", ".join(_sanitize_command_text(token) for token in result.known_tokens)
        token = _sanitize_command_text(result.token)
        return CommandOutput(
            status="unknown_command",
            ready=False,
            message=f"unknown command '{token}': known tokens are {tokens}",
            known_tokens=result.known_tokens,
        )
    if isinstance(result, ArgvParseError):
        return CommandOutput(
            status="parse_error",
            ready=False,
            message=(
                f"{_sanitize_command_text(result.reason)} "
                f"(usage: {_sanitize_command_text(result.usage)})"
            ),
        )
    if isinstance(result, str):
        return CommandOutput(status="ok", ready=True, message=result)
    if not result.ready:
        blocker_lane = command_blocker_lane_for_step(result.blocker_step)
        return CommandOutput(
            status="stub",
            ready=False,
            message=result.blocker_reason,
            blocker_lane=blocker_lane,
            blocker_step=result.blocker_step,
            blocker_reason=result.blocker_reason,
        )
    return CommandOutput(status="ok", ready=True, message="ok")


def dispatch_command(
    argv: tuple[str, ...],
) -> Union[PartialCommandResult, ArgvParseError, UnknownCommandError]:
    """Route argv to the matching command dispatcher based on argv[0].

    argv layout: (command_token, *args) — same as each individual dispatcher.
    Returns UnknownCommandError when argv[0] is not a known command token
    so the caller does not need to enumerate COMMAND_TOKENS itself.
    """
    _validate_argv(argv)
    if not argv:
        return UnknownCommandError(token="", known_tokens=known_command_tokens())
    if _argv_contains_null_byte(argv):
        return _null_byte_dispatch_error(argv)
    token = _normalize_dispatch_token(argv[0])
    if token == PATCH_REVIEW_COMMAND:
        return dispatch_diff_preview((DIFF_PREVIEW_COMMAND,) + argv[1:])
    if token in COMMAND_ALIASES:
        canonical = COMMAND_ALIASES[token]
        return dispatch_command((canonical,) + argv[1:])
    if token == BOOTSTRAP_COMMAND:
        return dispatch_bootstrap(argv)
    if token == RETRIEVE_COMMAND:
        return dispatch_retrieve(argv)
    if token == CONTEXT_BASKET_COMMAND:
        return dispatch_context_basket(argv)
    if token == TERMINAL_COMMAND:
        return dispatch_terminal(argv)
    if token == NOTEBOOK_COMMAND:
        return dispatch_notebook(argv)
    if token == REVISE_COMMAND:
        return dispatch_revise(argv)
    if token == SESSION_SAVE_COMMAND:
        return dispatch_session_save(argv)
    if token == SESSION_RESUME_COMMAND:
        return dispatch_session_resume(argv)
    if token == DIFF_PREVIEW_COMMAND:
        return dispatch_diff_preview(argv)
    if token == PATCH_APPLY_COMMAND:
        return dispatch_patch_apply(argv)
    if token == PATCH_REJECT_COMMAND:
        return dispatch_patch_reject(argv)
    return UnknownCommandError(token=token, known_tokens=known_command_tokens())


CLI_EXIT_OK = 0
CLI_EXIT_USER_ERROR = 1
CLI_EXIT_STUB = 2


def get_help_message(target: str = "") -> str:
    """Return help or usage information for the CLI and its commands."""
    from exegesis_engine.api.commands.canonical import canonical_command
    from exegesis_engine.api.commands.catalog import command_aliases

    if target and target.strip():
        try:
            token = canonical_command(target)
        except Exception:
            token = target.strip().lower()
    else:
        token = ""

    usages = {
        "bootstrap": "bootstrap <project_id> [<document_id>]",
        "retrieve": "retrieve <query>",
        "context-basket": "context-basket list\n  | context-basket add <item_id>\n  | context-basket remove <item_id>\n  | context-basket clear",
        "terminal": "terminal <document_id>",
        "notebook": "notebook budget <chat_id>\n  | notebook compact <chat_id> [--target-tokens N]\n  | notebook compactions <chat_id>\n  | notebook expand-compaction <compaction_id>\n  | notebook restore-raw <chat_id> <compaction_id>\n  | notebook pin <entry_id>\n  | notebook unpin <entry_id>",
        "revise": "revise <document_id> [<basket_item_id> ...]",
        "session-save": "session-save <document_id> <session_id>",
        "session-resume": "session-resume <session_id>",
        "diff-preview": "diff-preview <original> <proposed>",
        "patch-apply": "patch-apply <original> <proposed>",
        "patch-reject": "patch-reject <original> <proposed>",
    }

    descriptions = {
        "bootstrap": "Run the project bootstrap flow.",
        "retrieve": "Retrieve relevant material.",
        "context-basket": "Manage retrieval context basket items.",
        "terminal": "Run terminal export handoff routing.",
        "notebook": "Manage notebook context compaction and budget.",
        "revise": "Produce a plan or revision.",
        "session-save": "Persist the updated document and session state.",
        "session-resume": "Resume the workflow without losing context.",
        "diff-preview": "Preview unified diff output.",
        "patch-apply": "Apply a proposed patch.",
        "patch-reject": "Reject a proposed patch.",
    }

    aliases_map: dict[str, str] = {}
    for cmd in usages:
        aliases = command_aliases(cmd)
        if aliases:
            aliases_map[cmd] = ", ".join(aliases)

    if token in usages:
        msg = [f"Usage: {usages[token]}", f"Description: {descriptions[token]}"]
        if token in aliases_map:
            msg.append(f"Aliases: {aliases_map[token]}")
        return "\n".join(msg)

    lines = [
        "Exegesis CLI - Command Surface",
        "",
        "Available commands:",
    ]
    for cmd in sorted(usages):
        desc = descriptions[cmd]
        alias_str = f" (aliases: {aliases_map[cmd]})" if cmd in aliases_map else ""
        lines.append(f"  {cmd:<16} - {desc}{alias_str}")
    lines.extend([
        "",
        "For help with a specific command, run:",
        "  help <command>",
        "  <command> --help",
        "  <command> -h",
    ])
    return "\n".join(lines)


def cli_main(argv: tuple[str, ...]) -> tuple[int, str]:
    """Run a command from argv and return (exit_code, output_text).

    Exit codes:
      0  — command succeeded (status "ok")
      1  — user/argv error (unknown command or parse error)
      2  — stub not yet wired (upstream lane still required)

    Callers can pass sys.argv[1:] directly; this function never raises.
    """
    if not isinstance(argv, (tuple, list)):
        return CLI_EXIT_USER_ERROR, f"Error: argv must be a list or tuple, got {type(argv).__name__}"
    if len(argv) > 1000:
        return CLI_EXIT_USER_ERROR, "Error: argv length cannot exceed 1000 elements"
    for i, x in enumerate(argv):
        if not isinstance(x, str):
            return CLI_EXIT_USER_ERROR, f"Error: argv element at index {i} must be a string, got {type(x).__name__}"
        if len(x) > 50000000:
            return CLI_EXIT_USER_ERROR, f"Error: argv element at index {i} length cannot exceed 50000000 characters"
    result = dispatch_command(argv)
    out = format_dispatch_result(result)
    if out.status == "ok":
        return CLI_EXIT_OK, out.message
    if out.status == "stub":
        blocker_prefix = (
            f"{out.blocker_lane}: {out.blocker_step}"
            if out.blocker_lane
            else out.blocker_step
        )
        lines = [f"[stub] {blocker_prefix}: {out.blocker_reason}"]
        return CLI_EXIT_STUB, "\n".join(lines)
    return CLI_EXIT_USER_ERROR, out.message


def dispatch_partial_command(
    argv: tuple[str, ...],
) -> Union[ReviseResult, SessionSaveResult, SessionResumeResult, ArgvParseError, UnknownCommandError]:
    """Route argv for the three engine-unwired stub commands.

    Only handles revise, session-save, and session-resume.  All other tokens
    return UnknownCommandError with known_tokens=PARTIAL_COMMAND_TOKENS so
    callers can distinguish a partial-command miss from a full-surface miss.
    Use dispatch_command for the full ten-command surface.
    """
    _validate_argv(argv)
    if not argv:
        return UnknownCommandError(token="", known_tokens=PARTIAL_COMMAND_TOKENS)
    if _argv_contains_null_byte(argv):
        return _null_byte_dispatch_error(argv)
    token = _normalize_dispatch_token(argv[0])
    if token == REVISE_COMMAND:
        return dispatch_revise(argv)
    if token == SESSION_SAVE_COMMAND:
        return dispatch_session_save(argv)
    if token == SESSION_RESUME_COMMAND:
        return dispatch_session_resume(argv)
    return UnknownCommandError(token=token, known_tokens=PARTIAL_COMMAND_TOKENS)
