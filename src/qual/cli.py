from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass

from src.qual.commands.canonical import canonical_command
from src.qual.config import validate_project_name


@dataclass(frozen=True)
class CLIArgs:
    command: str
    project: str | None
    original: str | None
    proposed: str | None
    basket_action: str | None
    basket_item_id: str | None


def _normalize_argv(argv: list[str] | None) -> list[str]:
    raw = list(sys.argv[1:] if argv is None else argv)
    if not raw:
        return ["bootstrap"]

    known = {"bootstrap", "diff-preview", "diff", "context-basket"}
    first = raw[0]
    # Backward compatibility: allow `--project ...` without explicit subcommand.
    if first.startswith("-"):
        return ["bootstrap", *raw]
    if first in known:
        return raw
    return raw


def parse_args(argv: list[str] | None = None) -> CLIArgs:
    parser = argparse.ArgumentParser(prog="qual-bootstrap")
    sub = parser.add_subparsers(dest="command")

    p_bootstrap = sub.add_parser("bootstrap", help="Run bootstrap shell")
    p_bootstrap.add_argument(
        "--project",
        type=validate_project_name,
        help="Project name to bootstrap under local app data directory.",
    )

    p_diff = sub.add_parser("diff-preview", help="Preview unified diff output")
    p_diff.add_argument("--original", help="Original text")
    p_diff.add_argument("--proposed", help="Proposed text")

    p_diff_alias = sub.add_parser("diff", help="Alias for diff-preview")
    p_diff_alias.add_argument("--original", help="Original text")
    p_diff_alias.add_argument("--proposed", help="Proposed text")

    p_basket = sub.add_parser("context-basket", help="Manage context basket items")
    p_basket_sub = p_basket.add_subparsers(dest="basket_action", required=True)

    p_basket_add = p_basket_sub.add_parser("add", help="Add an item id to basket")
    p_basket_add.add_argument("item_id", help="Context item id")

    p_basket_remove = p_basket_sub.add_parser("remove", help="Remove an item id from basket")
    p_basket_remove.add_argument("item_id", help="Context item id")

    p_basket_sub.add_parser("list", help="List basket item ids")
    p_basket_sub.add_parser("clear", help="Clear all basket item ids")

    parser.set_defaults(
        command="bootstrap",
        project=None,
        original=None,
        proposed=None,
        basket_action=None,
        item_id=None,
    )
    ns = parser.parse_args(_normalize_argv(argv))
    command = canonical_command(str(ns.command))
    return CLIArgs(
        command=command,
        project=ns.project,
        original=ns.original,
        proposed=ns.proposed,
        basket_action=ns.basket_action,
        basket_item_id=getattr(ns, "item_id", None),
    )
