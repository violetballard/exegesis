from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass

from exegesis_engine.config import validate_project_name
from src.qual.commands.catalog import CommandCliContract, command_cli_contract


_SUPPORTED_PARSER_CANONICAL_COMMANDS: tuple[str, ...] = (
    "bootstrap",
    "diff-preview",
    "context-basket",
    "terminal",
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


def _parser_cli_contract() -> CommandCliContract:
    contract = command_cli_contract()
    canonical_names = tuple(dict.fromkeys(canonical for _, canonical in contract.lookup_table))
    if canonical_names != contract.canonical_names:
        raise RuntimeError("CLI parser contract lookup is inconsistent")
    if contract.canonical_names != _SUPPORTED_PARSER_CANONICAL_COMMANDS:
        raise RuntimeError("CLI parser handlers are inconsistent with command catalog")
    return contract


def _parser_tokens_by_canonical_name() -> dict[str, tuple[str, ...]]:
    tokens_by_name: dict[str, list[str]] = {
        canonical_name: [] for canonical_name in _parser_cli_contract().canonical_names
    }
    for token, canonical_name in _parser_cli_contract().lookup_table:
        tokens_by_name[canonical_name].append(token)
    return {name: tuple(tokens) for name, tokens in tokens_by_name.items()}


def _normalize_argv(argv: list[str] | None) -> list[str]:
    raw = list(sys.argv[1:] if argv is None else argv)
    if not raw:
        return ["bootstrap"]

    known = set(_parser_cli_contract().tokens)
    first = raw[0]
    if first.startswith("-"):
        return ["bootstrap", *raw]
    if first in known:
        return raw
    return raw


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="qual-bootstrap")
    sub = parser.add_subparsers(dest="command")
    parser_tokens = _parser_tokens_by_canonical_name()

    for bootstrap_token in parser_tokens["bootstrap"]:
        p_bootstrap = sub.add_parser(bootstrap_token, help="Run bootstrap shell")
        p_bootstrap.add_argument(
            "--project",
            type=validate_project_name,
            help="Project name to bootstrap under local app data directory.",
        )

    for diff_token in parser_tokens["diff-preview"]:
        p_diff = sub.add_parser(diff_token, help="Preview unified diff output")
        p_diff.add_argument("--original", help="Original text")
        p_diff.add_argument("--proposed", help="Proposed text")

    for basket_token in parser_tokens["context-basket"]:
        p_basket = sub.add_parser(basket_token, help="Manage context basket items")
        p_basket_sub = p_basket.add_subparsers(dest="basket_action", required=True)

        p_basket_add = p_basket_sub.add_parser("add", help="Add an item id to basket")
        p_basket_add.add_argument("item_id", help="Context item id")

        p_basket_remove = p_basket_sub.add_parser("remove", help="Remove an item id from basket")
        p_basket_remove.add_argument("item_id", help="Context item id")

        p_basket_sub.add_parser("list", help="List basket item ids")
        p_basket_sub.add_parser("clear", help="Clear all basket item ids")

    for terminal_token in parser_tokens["terminal"]:
        p_terminal = sub.add_parser(terminal_token, help="Run terminal routing scaffold")
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


def parse_args(argv: list[str] | None = None) -> CLIArgs:
    parser = _build_parser()
    ns = parser.parse_args(_normalize_argv(argv))
    command = dict(_parser_cli_contract().lookup_table)[str(ns.command)]
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
