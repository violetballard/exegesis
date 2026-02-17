from __future__ import annotations

from src.qual.engine.service import EngineRuntime


class ShellUI:
    """Minimal CLI shell used to verify bootstrap wiring."""

    def render_startup(self, runtime: EngineRuntime) -> str:
        if runtime.basket.item_ids:
            preview_items = [self._format_item_id(value) for value in runtime.basket.item_ids[:3]]
            preview = ", ".join(preview_items)
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

    @staticmethod
    def _format_item_id(value: str) -> str:
        normalized = " ".join(value.split())
        if len(normalized) <= 24:
            return normalized
        return f"{normalized[:21]}..."
