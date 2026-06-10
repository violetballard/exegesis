from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass

from exegesis_engine.api.commands.canonical import canonical_command
from exegesis_engine.api.commands.catalog import normalize_command_argv
from exegesis_engine.config import validate_project_name


@dataclass(frozen=True)
class CLIArgs:
    command: str
    project: str | None
    original: str | None
    proposed: str | None
    diff_preview_action: str
    retrieve_query: str | None
    basket_action: str | None
    basket_item_id: str | None
    document_id: str | None
    basket_item_ids: tuple[str, ...]
    session_id: str | None
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
    notebook_action: str | None
    notebook_target: str | None
    notebook_target_extra: str | None
    notebook_target_tokens: int | None


def _normalize_argv(argv: list[str] | None) -> list[str]:
    raw = list(sys.argv[1:] if argv is None else argv)
    return list(normalize_command_argv(raw))


def parse_args(argv: list[str] | None = None) -> CLIArgs:
    parser = argparse.ArgumentParser(prog="qual-bootstrap")
    sub = parser.add_subparsers(dest="command")

    p_bootstrap = sub.add_parser(
        "bootstrap",
        aliases=("open", "project-open", "project"),
        help="Run bootstrap shell",
    )
    p_bootstrap.add_argument(
        "--project",
        type=validate_project_name,
        help="Project name to bootstrap under local app data directory.",
    )

    p_diff = sub.add_parser(
        "diff-preview",
        aliases=("diff", "diff_preview", "patch-review"),
        help="Preview unified diff output",
    )
    p_diff.add_argument(
        "diff_preview_action",
        nargs="?",
        choices=("preview", "apply", "reject"),
        default="preview",
        help="Patch review action to perform.",
    )
    p_diff.add_argument("--original", help="Original text")
    p_diff.add_argument("--proposed", help="Proposed text")

    p_patch_apply = sub.add_parser("patch-apply", help="Apply proposed patch text")
    p_patch_apply.add_argument("--original", help="Original text")
    p_patch_apply.add_argument("--proposed", help="Proposed text")
    p_patch_apply.set_defaults(diff_preview_action="apply")

    p_patch_reject = sub.add_parser("patch-reject", help="Reject proposed patch text")
    p_patch_reject.add_argument("--original", help="Original text")
    p_patch_reject.add_argument("--proposed", help="Proposed text")
    p_patch_reject.set_defaults(diff_preview_action="reject")

    p_retrieve = sub.add_parser("retrieve", help="Retrieve relevant material")
    p_retrieve.add_argument("query", nargs="+", help="Retrieval query")

    p_basket = sub.add_parser(
        "context-basket",
        aliases=("context", "basket"),
        help="Manage context basket items",
    )
    p_basket_sub = p_basket.add_subparsers(dest="basket_action", required=True)

    p_basket_add = p_basket_sub.add_parser("add", help="Add an item id to basket")
    p_basket_add.add_argument("item_id", help="Context item id")

    p_basket_remove = p_basket_sub.add_parser("remove", help="Remove an item id from basket")
    p_basket_remove.add_argument("item_id", help="Context item id")

    p_basket_sub.add_parser("list", help="List basket item ids")
    p_basket_sub.add_parser("clear", help="Clear all basket item ids")

    p_revise = sub.add_parser("revise", help="Produce a plan or revision scaffold")
    p_revise.add_argument("document_id", help="Document id to revise")
    p_revise.add_argument("basket_item_ids", nargs="*", help="Optional basket item ids")

    p_session_save = sub.add_parser("session-save", help="Persist session scaffold")
    p_session_save.add_argument("document_id", help="Document id to persist")
    p_session_save.add_argument("session_id", help="Session id to persist")

    p_session_resume = sub.add_parser("session-resume", help="Resume session scaffold")
    p_session_resume.add_argument("session_id", help="Session id to resume")

    p_terminal = sub.add_parser("terminal", help="Run terminal routing scaffold")
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

    p_notebook = sub.add_parser(
        "notebook",
        help="Manage notebook context compaction and budget",
    )
    p_notebook.add_argument("notebook_action", nargs="?", default=None, choices=("budget", "compact", "compactions", "expand-compaction", "restore-raw", "pin", "unpin"))
    p_notebook.add_argument("notebook_target", nargs="?", default=None)
    p_notebook.add_argument("notebook_target_extra", nargs="?", default=None)
    p_notebook.add_argument("--target-tokens", dest="notebook_target_tokens", type=int, default=None)

    parser.set_defaults(
        command="bootstrap",
        project=None,
        original=None,
        proposed=None,
        diff_preview_action="preview",
        query=None,
        basket_action=None,
        item_id=None,
        document_id=None,
        basket_item_ids=(),
        session_id=None,
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
        notebook_action=None,
        notebook_target=None,
        notebook_target_extra=None,
        notebook_target_tokens=None,
    )
    ns = parser.parse_args(_normalize_argv(argv))
    command = canonical_command(str(ns.command))
    action = str(getattr(ns, "diff_preview_action", "preview"))
    if command == "patch-apply":
        action = "apply"
    if command == "patch-reject":
        action = "reject"
    query = getattr(ns, "query", None)
    return CLIArgs(
        command=command,
        project=ns.project,
        original=ns.original,
        proposed=ns.proposed,
        diff_preview_action=action,
        retrieve_query=" ".join(query) if query else None,
        basket_action=ns.basket_action,
        basket_item_id=getattr(ns, "item_id", None),
        document_id=getattr(ns, "document_id", None),
        basket_item_ids=tuple(getattr(ns, "basket_item_ids", ())),
        session_id=getattr(ns, "session_id", None),
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
        notebook_action=getattr(ns, "notebook_action", None),
        notebook_target=getattr(ns, "notebook_target", None),
        notebook_target_extra=getattr(ns, "notebook_target_extra", None),
        notebook_target_tokens=getattr(ns, "notebook_target_tokens", None),
    )
