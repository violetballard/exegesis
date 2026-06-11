from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from textual.command import DiscoveryHit, Hit, Hits, Provider

from exegesis_textual.actions.registry import AppActionSpec, palette_action_specs
from exegesis_textual.services.projects import is_local_developer_mode


@dataclass(frozen=True)
class PaletteCommand:
    key: str
    label: str
    description: str
    action: str
    action_id: str = ""


def _command_display(command: PaletteCommand) -> str:
    return f"{command.label} [{command.key}]"


def _palette_command_from_spec(spec: AppActionSpec) -> PaletteCommand:
    return PaletteCommand(
        spec.shortcut or "palette",
        spec.label,
        spec.description,
        spec.action_name,
        spec.id,
    )


def default_palette_commands() -> tuple[PaletteCommand, ...]:
    return tuple(
        _palette_command_from_spec(spec)
        for spec in palette_action_specs(include_local_developer=is_local_developer_mode())
    )


class ExegesisCommandProvider(Provider):
    """Expose Exegesis shell actions in Textual's native command palette."""

    def _callback_for(self, command: PaletteCommand) -> Callable[[], None]:
        def callback() -> None:
            dispatcher = getattr(self.app, "dispatch_app_action", None)
            if command.action_id and callable(dispatcher):
                self.app.run_worker(dispatcher(command.action_id, source="palette"), thread=False, exclusive=False)
                return
            self.app.run_worker(self.app.run_action(command.action), thread=False, exclusive=False)

        return callback

    async def search(self, query: str) -> Hits:
        matcher = self.matcher(query)
        for command in default_palette_commands():
            candidate = f"{command.label} {command.key} {command.description} {command.action_id}"
            score = matcher.match(candidate)
            if score > 0:
                yield Hit(
                    score,
                    matcher.highlight(_command_display(command)),
                    self._callback_for(command),
                    text=command.label,
                    help=command.description,
                )

    async def discover(self) -> Hits:
        for command in default_palette_commands():
            yield DiscoveryHit(
                _command_display(command),
                self._callback_for(command),
                text=command.label,
                help=command.description,
            )


__all__ = ["ExegesisCommandProvider", "PaletteCommand", "default_palette_commands"]
