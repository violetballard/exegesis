from __future__ import annotations

from src.qual.bootstrap import build_runtime
from src.qual.commands.diff_preview import DiffPreviewInput, run_diff_preview
from src.qual.config import default_config
from src.qual.context.store import ContextBasketStore
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
    store = ContextBasketStore(config.app_data_dir)
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
