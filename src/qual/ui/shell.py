from __future__ import annotations

from src.qual.engine.service import EngineRuntime


class ShellUI:
    """Minimal CLI shell used to verify bootstrap wiring."""

    def render_startup(self, runtime: EngineRuntime) -> str:
        if runtime.basket.item_ids:
            preview_items = [self._format_item_id(value) for value in runtime.basket.item_ids[:3]]
            preview = ", ".join(preview_items)
            if len(runtime.basket.item_ids) > 3:
                remaining = len(runtime.basket.item_ids) - 3
                label = "item" if remaining == 1 else "items"
                preview = f"{preview}, +{remaining} more {label}"
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
        baseline = " ".join(value.split())
        if not baseline:
            return "<blank>"
        escaped = ShellUI._escape_control_chars(value)
        normalized = " ".join(escaped.split())
        rendered = ShellUI._truncate_for_preview(normalized, max_len=24)
        if "," in rendered or '"' in rendered or "\\" in rendered:
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

    @staticmethod
    def _truncate_for_preview(value: str, *, max_len: int) -> str:
        if len(value) <= max_len:
            return value

        prefix = value[: max_len - 3]
        while prefix:
            if prefix.endswith("\\"):
                prefix = prefix[:-1]
                continue
            escape_start = prefix.rfind("\\x")
            if escape_start != -1 and len(prefix) - escape_start < 4:
                prefix = prefix[:escape_start]
                continue
            break
        return f"{prefix}..."
