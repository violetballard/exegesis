from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass

import src.qual.commands.catalog as command_catalog
from src.qual.config import validate_project_name


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


def _normalize_argv(argv: list[str] | None) -> list[str]:
    raw = list(sys.argv[1:] if argv is None else argv)
    if not raw:
        return ["bootstrap"]

    known = set(command_catalog.command_cli_tokens())
    first = raw[0]
    # Backward compatibility: allow `--project ...` without explicit subcommand.
    if first.startswith("-"):
        return ["bootstrap", *raw]
    if first in known:
        return raw
    return raw


def _add_bootstrap_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--project",
        type=validate_project_name,
        help="Project name to bootstrap under local app data directory.",
    )


def _add_diff_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--original", help="Original text")
    parser.add_argument("--proposed", help="Proposed text")


def _add_context_basket_arguments(parser: argparse.ArgumentParser) -> None:
    basket_sub = parser.add_subparsers(dest="basket_action", required=True)

    basket_add = basket_sub.add_parser("add", help="Add an item id to basket")
    basket_add.add_argument("item_id", help="Context item id")

    basket_remove = basket_sub.add_parser("remove", help="Remove an item id from basket")
    basket_remove.add_argument("item_id", help="Context item id")

    basket_sub.add_parser("list", help="List basket item ids")
    basket_sub.add_parser("clear", help="Clear all basket item ids")


def _add_terminal_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--message", help="User terminal input")
    parser.add_argument(
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
    parser.add_argument("--section-type", help="Optional section type context")
    parser.add_argument("--user-intent", help="Optional user intent label")
    parser.add_argument("--input-tokens", type=int, default=120)
    parser.add_argument("--constraints-count", type=int, default=0)
    parser.add_argument("--requires-multi-step-tools", action="store_true")
    parser.add_argument("--sku-gb", type=int, default=128)
    parser.add_argument("--qwen-available", action="store_true")
    parser.add_argument("--runtime-supports-qwen", action="store_true")


def _add_command_arguments(parser: argparse.ArgumentParser, canonical_name: str) -> None:
    if canonical_name == "bootstrap":
        _add_bootstrap_arguments(parser)
    elif canonical_name == "diff-preview":
        _add_diff_arguments(parser)
    elif canonical_name == "context-basket":
        _add_context_basket_arguments(parser)
    elif canonical_name == "terminal":
        _add_terminal_arguments(parser)
    else:
        raise ValueError(f"Unknown CLI command target: {canonical_name}")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="qual-bootstrap")
    sub = parser.add_subparsers(dest="command")

    for token, canonical_name in command_catalog.command_cli_lookup_table():
        command_parser = sub.add_parser(token, help=_command_help(canonical_name))
        _add_command_arguments(command_parser, canonical_name)

    parser.set_defaults(
        command="bootstrap",
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


def _command_help(canonical_name: str) -> str:
    if canonical_name == "bootstrap":
        return "Run bootstrap shell"
    if canonical_name == "diff-preview":
        return "Preview unified diff output"
    if canonical_name == "context-basket":
        return "Manage context basket items"
    if canonical_name == "terminal":
        return "Run terminal routing scaffold"
    raise ValueError(f"Unknown CLI command target: {canonical_name}")


def command_parser_lookup_table() -> tuple[tuple[str, str], ...]:
    parser = _build_parser()
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            return tuple((token, command_catalog.canonical_command(token)) for token in action.choices)
    raise ValueError("Command CLI parser has no subcommands")


def parse_args(argv: list[str] | None = None) -> CLIArgs:
    parser = _build_parser()
    ns = parser.parse_args(_normalize_argv(argv))
    command = command_catalog.canonical_command(str(ns.command))
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
