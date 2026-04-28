from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass

from src.qual.commands.canonical import canonical_command
from src.qual.config import validate_project_name

_BOOTSTRAP_COMMAND = "bootstrap"
_DIFF_PREVIEW_COMMAND = "diff-preview"
_DIFF_PREVIEW_ALIASES = ("diff",)
_CONTEXT_BASKET_COMMAND = "context-basket"
_TERMINAL_COMMAND = "terminal"

_CLI_PARSER_ENTRYPOINTS: tuple[tuple[str, tuple[str, ...]], ...] = (
    (_BOOTSTRAP_COMMAND, (_BOOTSTRAP_COMMAND,)),
    (_DIFF_PREVIEW_COMMAND, (_DIFF_PREVIEW_COMMAND, *_DIFF_PREVIEW_ALIASES)),
    (_CONTEXT_BASKET_COMMAND, (_CONTEXT_BASKET_COMMAND,)),
    (_TERMINAL_COMMAND, (_TERMINAL_COMMAND,)),
)


@dataclass(frozen=True)
class CLIArgs:
    command: str
    project: str | None
    original: str | None
    proposed: str | None
    basket_action: str | None
    basket_item_id: str | None
    terminal_message: str | None
    terminal_operation_kind: str | None
    terminal_section_type: str | None
    terminal_user_intent: str | None
    terminal_input_tokens: int
    terminal_constraints_count: int
    terminal_requires_multi_step_tools: bool
    terminal_sku_gb: int
    terminal_qwen_available: bool
    terminal_runtime_supports_qwen: bool


def _add_diff_preview_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--original", help="Original text")
    parser.add_argument("--proposed", help="Proposed text")


def _subparser_action(parser: argparse.ArgumentParser) -> argparse._SubParsersAction:
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            return action
    raise ValueError("CLI parser is missing a command subparser surface")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="qual-bootstrap")
    sub = parser.add_subparsers(dest="command")

    for command_name, entrypoints in _CLI_PARSER_ENTRYPOINTS:
        for index, entrypoint in enumerate(entrypoints):
            alias_label = "" if index == 0 else " alias"
            if command_name == _BOOTSTRAP_COMMAND:
                p_bootstrap = sub.add_parser(entrypoint, help=f"Run bootstrap shell{alias_label}")
                p_bootstrap.add_argument(
                    "--project",
                    type=validate_project_name,
                    help="Project name to bootstrap under local app data directory.",
                )
                continue

            if command_name == _DIFF_PREVIEW_COMMAND:
                p_diff = sub.add_parser(entrypoint, help=f"Preview unified diff output{alias_label}")
                _add_diff_preview_args(p_diff)
                continue

            if command_name == _CONTEXT_BASKET_COMMAND:
                p_basket = sub.add_parser(entrypoint, help=f"Manage context basket items{alias_label}")
                p_basket_sub = p_basket.add_subparsers(dest="basket_action", required=True)

                p_basket_add = p_basket_sub.add_parser("add", help="Add an item id to basket")
                p_basket_add.add_argument("item_id", help="Context item id")

                p_basket_remove = p_basket_sub.add_parser("remove", help="Remove an item id from basket")
                p_basket_remove.add_argument("item_id", help="Context item id")

                p_basket_sub.add_parser("list", help="List basket item ids")
                p_basket_sub.add_parser("clear", help="Clear all basket item ids")
                continue

            if command_name == _TERMINAL_COMMAND:
                p_terminal = sub.add_parser(entrypoint, help=f"Run terminal routing scaffold{alias_label}")
                p_terminal.add_argument("--message", help="User terminal input")
                p_terminal.add_argument(
                    "--operation-kind",
                    choices=[
                        "terminal_chat",
                        "terminal_query",
                        "terminal_tool_orchestration",
                        "terminal_outline_request",
                        "terminal_synthesis_request",
                    ],
                    default="terminal_chat",
                )
                p_terminal.add_argument("--section-type", help="Optional section type context")
                p_terminal.add_argument("--user-intent", help="Optional user intent label")
                p_terminal.add_argument("--input-tokens", type=int, default=120)
                p_terminal.add_argument("--constraints-count", type=int, default=0)
                p_terminal.add_argument("--requires-multi-step-tools", action="store_true")
                p_terminal.add_argument("--sku-gb", type=int, default=128)
                p_terminal.add_argument("--qwen-available", action="store_true")
                p_terminal.add_argument("--runtime-supports-qwen", action="store_true")
                continue

            raise ValueError(f"Unknown CLI parser command entrypoint group: {command_name}")

    parser.set_defaults(
        command=_BOOTSTRAP_COMMAND,
        project=None,
        original=None,
        proposed=None,
        basket_action=None,
        item_id=None,
        message=None,
        operation_kind=None,
        section_type=None,
        user_intent=None,
        input_tokens=120,
        constraints_count=0,
        requires_multi_step_tools=False,
        sku_gb=128,
        qwen_available=False,
        runtime_supports_qwen=False,
    )
    return parser


def parser_cli_entrypoints() -> tuple[tuple[str, tuple[str, ...]], ...]:
    grouped: dict[str, list[str]] = {}
    for entrypoint in _subparser_action(_build_parser()).choices:
        command_name = canonical_command(entrypoint)
        grouped.setdefault(command_name, []).append(entrypoint)
    return tuple((command_name, tuple(entrypoints)) for command_name, entrypoints in grouped.items())


def _parser_cli_tokens() -> set[str]:
    return {
        token
        for _, entrypoints in parser_cli_entrypoints()
        for token in entrypoints
    }


def _normalize_argv(argv: list[str] | None) -> list[str]:
    raw = list(sys.argv[1:] if argv is None else argv)
    if not raw:
        return [_BOOTSTRAP_COMMAND]

    known = _parser_cli_tokens()
    first = raw[0]
    # Backward compatibility: allow `--project ...` without explicit subcommand.
    if first.startswith("-"):
        return [_BOOTSTRAP_COMMAND, *raw]
    if first in known:
        return raw
    return raw


def parse_args(argv: list[str] | None = None) -> CLIArgs:
    from src.qual.commands.catalog import command_cli_contract

    command_cli_contract()
    parser = _build_parser()
    ns = parser.parse_args(_normalize_argv(argv))
    command = canonical_command(str(ns.command))
    return CLIArgs(
        command=command,
        project=ns.project,
        original=ns.original,
        proposed=ns.proposed,
        basket_action=ns.basket_action,
        basket_item_id=getattr(ns, "item_id", None),
        terminal_message=getattr(ns, "message", None),
        terminal_operation_kind=getattr(ns, "operation_kind", None),
        terminal_section_type=getattr(ns, "section_type", None),
        terminal_user_intent=getattr(ns, "user_intent", None),
        terminal_input_tokens=int(getattr(ns, "input_tokens", 120)),
        terminal_constraints_count=int(getattr(ns, "constraints_count", 0)),
        terminal_requires_multi_step_tools=bool(getattr(ns, "requires_multi_step_tools", False)),
        terminal_sku_gb=int(getattr(ns, "sku_gb", 128)),
        terminal_qwen_available=bool(getattr(ns, "qwen_available", False)),
        terminal_runtime_supports_qwen=bool(getattr(ns, "runtime_supports_qwen", False)),
    )
