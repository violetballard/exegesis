from __future__ import annotations

from src.qual.engine.service import EngineRuntime


class ShellUI:
    """Minimal CLI shell used to verify bootstrap wiring."""

    def render_startup(self, runtime: EngineRuntime) -> str:
        if runtime.basket.item_ids:
            preview = ", ".join(runtime.basket.item_ids[:3])
            if len(runtime.basket.item_ids) > 3:
                preview = f"{preview}, +{len(runtime.basket.item_ids) - 3} more"
        else:
            preview = "<empty>"
        return (
            "Qual Workstation bootstrap is running\n"
            f"- project: {runtime.vault.project_name}\n"
            f"- vault: {runtime.vault.root_dir}\n"
            f"- locked: {runtime.vault.is_locked}\n"
            f"- context_items: {len(runtime.basket.item_ids)}\n"
            f"- context_preview: {preview}"
        )
