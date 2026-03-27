from __future__ import annotations

from exegesis_engine.api.bootstrap import build_runtime
from exegesis_engine.config import default_config
from src.qual.commands.diff_preview import DiffPreviewInput, run_diff_preview
from exegesis_engine.context.store import ContextBasketStore
from src.qual.engine.terminal_chat import TerminalRoutingInput, route_terminal_model
from exegesis_engine.storage.vault import VaultService
from src.qual.ui.a2ui import render_terminal_card
from src.qual.ui.shell import ShellUI


def run_bootstrap(*, project_name: str | None = None) -> int:
    runtime = build_runtime(project_name=project_name)
    ui = ShellUI()
    print(ui.render_startup(runtime))
    return 0


def run_diff_preview_command(*, original: str | None, proposed: str | None) -> int:
    before = original if original is not None else "The first draft paragraph.\n"
    after = proposed if proposed is not None else "The revised draft paragraph with evidence.\n"
    print(run_diff_preview(DiffPreviewInput(original=before, proposed=after)))
    return 0


def run_context_basket_command(*, action: str | None, item_id: str | None) -> int:
    config = default_config()
    vault = VaultService().create_or_open(config.app_data_dir, config.default_project_name)
    store = ContextBasketStore(vault.root_dir)
    basket = store.load()

    if action == "add":
        if not item_id:
            raise ValueError("item_id is required for context-basket add")
        basket.add(item_id)
        store.save(basket)
        print(f"Added to context basket: {item_id}")
        return 0

    if action == "remove":
        if not item_id:
            raise ValueError("item_id is required for context-basket remove")
        basket.remove(item_id)
        store.save(basket)
        print(f"Removed from context basket: {item_id}")
        return 0

    if action == "list":
        if not basket.item_ids:
            print("Context basket is empty")
            return 0
        for value in basket.item_ids:
            print(value)
        return 0

    if action == "clear":
        store.clear()
        print("Context basket cleared")
        return 0

    raise ValueError("context-basket action must be one of: add, remove, list, clear")


def run_terminal_command(
    *,
    operation_kind: str | None,
    message: str | None,
    section_type: str | None,
    user_intent: str | None,
    input_tokens: int,
    constraints_count: int,
    requires_multi_step_tools: bool,
    sku_gb: int,
    qwen_available: bool,
    runtime_supports_qwen: bool,
) -> int:
    kind = operation_kind if operation_kind is not None else "terminal_chat"
    decision = route_terminal_model(
        TerminalRoutingInput(
            operation_kind=kind,  # type: ignore[arg-type]
            sku_gb=sku_gb,
            pack_contains_qwen=qwen_available,
            runtime_supports_qwen=runtime_supports_qwen,
            requires_multi_step_tools=requires_multi_step_tools,
            input_tokens=input_tokens,
            constraints_count=constraints_count,
            section_type=section_type,
            user_intent=user_intent,
        )
    )
    card = {
        "type": "GenericCard",
        "title": "Terminal routing decision",
        "blocks": [
            {
                "type": "KeyValueBlock",
                "items": [
                    {"key": "operation_kind", "value": kind},
                    {"key": "model_used", "value": decision.model_used},
                    {"key": "escalation_applied", "value": str(decision.escalation_applied)},
                    {"key": "escalation_reason", "value": decision.escalation_reason},
                    {"key": "mode_used", "value": decision.mode_used},
                    {"key": "max_output_tokens", "value": str(decision.max_output_tokens)},
                ],
            },
            {"type": "MarkdownBlock", "markdown": f"Input: {message or '<empty>'}"},
        ],
    }
    print(render_terminal_card(card))
    return 0
