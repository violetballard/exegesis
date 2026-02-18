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
        normalized = ShellUI._escape_control_chars(normalized)
        if len(normalized) <= 24:
            rendered = normalized
        else:
            rendered = f"{normalized[:21]}..."
        if "," in rendered or '"' in rendered:
            escaped = rendered.replace("\\", "\\\\").replace('"', '\\"')
            return f'"{escaped}"'
        return rendered

    @staticmethod
    def _escape_control_chars(value: str) -> str:
        parts: list[str] = []
        for char in value:
            code = ord(char)
            if code < 32 or code == 127:
                parts.append(f"\\x{code:02x}")
            else:
                parts.append(char)
        return "".join(parts)
