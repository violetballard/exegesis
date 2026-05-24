from __future__ import annotations

from dataclasses import dataclass
from typing import Union

from src.qual.commands.engine_stubs import (
    ReviseInput,
    ReviseResult,
    SessionResumeInput,
    SessionResumeResult,
    SessionSaveInput,
    SessionSaveResult,
    run_revise,
    run_session_resume,
    run_session_save,
)

# Argv layouts for each partial command (tokens after the program name):
#   revise <document_id> [<basket_item_id> ...]
#   session-save <document_id> <session_id>
#   session-resume <session_id>
#
# These are the stable calling conventions that feat-engine-runs replaces the
# stub bodies against.  Parsing lives here; business logic lives in engine_stubs.

REVISE_COMMAND = "revise"
SESSION_SAVE_COMMAND = "session-save"
SESSION_RESUME_COMMAND = "session-resume"

# Complete set of partial-command tokens in canonical demo-path order.
# feat-engine-runs uses this tuple to enumerate which commands still need
# the engine loop wired rather than hard-coding individual token strings.
PARTIAL_COMMAND_TOKENS: tuple[str, ...] = (
    REVISE_COMMAND,
    SESSION_SAVE_COMMAND,
    SESSION_RESUME_COMMAND,
)


@dataclass(frozen=True)
class ArgvParseError:
    command: str
    reason: str
    usage: str


def parse_revise_argv(argv: tuple[str, ...]) -> ReviseInput | ArgvParseError:
    """Parse argv tokens for 'revise' into a ReviseInput.

    Expected layout: (command_token, document_id, *basket_item_ids)
    """
    if len(argv) < 2:
        return ArgvParseError(
            command=REVISE_COMMAND,
            reason="missing required argument: document_id",
            usage="revise <document_id> [<basket_item_id> ...]",
        )
    return ReviseInput(
        document_id=argv[1],
        basket_item_ids=tuple(argv[2:]),
    )


def parse_session_save_argv(argv: tuple[str, ...]) -> SessionSaveInput | ArgvParseError:
    """Parse argv tokens for 'session-save' into a SessionSaveInput.

    Expected layout: (command_token, document_id, session_id)
    """
    if len(argv) < 3:
        return ArgvParseError(
            command=SESSION_SAVE_COMMAND,
            reason="missing required arguments: document_id and/or session_id",
            usage="session-save <document_id> <session_id>",
        )
    return SessionSaveInput(
        document_id=argv[1],
        session_id=argv[2],
    )


def parse_session_resume_argv(argv: tuple[str, ...]) -> SessionResumeInput | ArgvParseError:
    """Parse argv tokens for 'session-resume' into a SessionResumeInput.

    Expected layout: (command_token, session_id)
    """
    if len(argv) < 2:
        return ArgvParseError(
            command=SESSION_RESUME_COMMAND,
            reason="missing required argument: session_id",
            usage="session-resume <session_id>",
        )
    return SessionResumeInput(session_id=argv[1])


def dispatch_revise(argv: tuple[str, ...]) -> ReviseResult | ArgvParseError:
    """Dispatch argv for the 'revise' command to the engine stub."""
    parsed = parse_revise_argv(argv)
    if isinstance(parsed, ArgvParseError):
        return parsed
    return run_revise(parsed)


def dispatch_session_save(argv: tuple[str, ...]) -> SessionSaveResult | ArgvParseError:
    """Dispatch argv for the 'session-save' command to the engine stub."""
    parsed = parse_session_save_argv(argv)
    if isinstance(parsed, ArgvParseError):
        return parsed
    return run_session_save(parsed)


def dispatch_session_resume(argv: tuple[str, ...]) -> SessionResumeResult | ArgvParseError:
    """Dispatch argv for the 'session-resume' command to the engine stub."""
    parsed = parse_session_resume_argv(argv)
    if isinstance(parsed, ArgvParseError):
        return parsed
    return run_session_resume(parsed)


@dataclass(frozen=True)
class UnknownCommandError:
    """Returned when argv[0] does not match any known partial-command token."""

    token: str
    known_tokens: tuple[str, ...]


PartialCommandResult = Union[ReviseResult, SessionSaveResult, SessionResumeResult]


def dispatch_partial_command(
    argv: tuple[str, ...],
) -> Union[PartialCommandResult, ArgvParseError, UnknownCommandError]:
    """Route argv to the matching partial-command dispatcher based on argv[0].

    argv layout: (command_token, *args) — same as each individual dispatcher.
    Returns UnknownCommandError when argv[0] is not a known partial-command token
    so the caller does not need to enumerate PARTIAL_COMMAND_TOKENS itself.
    """
    if not argv:
        return UnknownCommandError(token="", known_tokens=PARTIAL_COMMAND_TOKENS)
    token = argv[0]
    if token == REVISE_COMMAND:
        return dispatch_revise(argv)
    if token == SESSION_SAVE_COMMAND:
        return dispatch_session_save(argv)
    if token == SESSION_RESUME_COMMAND:
        return dispatch_session_resume(argv)
    return UnknownCommandError(token=token, known_tokens=PARTIAL_COMMAND_TOKENS)
