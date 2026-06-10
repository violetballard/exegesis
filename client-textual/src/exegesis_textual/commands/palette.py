from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Callable

from textual.command import DiscoveryHit, Hit, Hits, Provider


@dataclass(frozen=True)
class PaletteCommand:
    key: str
    label: str
    description: str
    action: str


def _command_display(command: PaletteCommand) -> str:
    return f"{command.label} [{command.key}]"


def default_palette_commands() -> tuple[PaletteCommand, ...]:
    commands = [
        PaletteCommand("ctrl+p", "Open command palette", "Show the planned shell command surface.", "show_palette"),
        PaletteCommand("palette", "New Project", "Create a new project folder in the Exegesis projects directory.", "new_project"),
        PaletteCommand("palette", "Project Browser", "Open, switch, or delete projects in the Exegesis projects directory.", "open_project_browser"),
        PaletteCommand("palette", "Change projects directory", "Choose the folder where Exegesis project folders are stored.", "change_projects_directory"),
        PaletteCommand("palette", "Model Settings", "Configure the Mistral API key, model, and reasoning behavior.", "model_settings"),
        PaletteCommand("ctrl+shift+e", "Add excerpt", "Add the active document selection to the basket.", "add_excerpt_to_basket"),
        PaletteCommand("ctrl+shift+b", "Add document", "Add the active document to the basket.", "add_file_to_basket"),
        PaletteCommand("delete", "Delete basket item", "Remove the selected item from the basket.", "delete_selected_basket_item"),
        PaletteCommand("ctrl+shift+d", "New draft", "Create a new draft document.", "create_draft"),
        PaletteCommand("ctrl+shift+m", "New memo", "Create a new memo document.", "create_memo"),
        PaletteCommand("ctrl+shift+s", "New summary", "Create a new summary document.", "create_summary"),
        PaletteCommand("ctrl+shift+t", "New transcript", "Create a new transcript document.", "create_transcript"),
        PaletteCommand("ctrl+shift+l", "New literature", "Create a new literature document.", "create_literature"),
        PaletteCommand("ctrl+shift+f", "New folder", "Create a folder in the selected project category.", "create_folder"),
        PaletteCommand("ctrl+shift+u", "Update item", "Rename or move the selected project item.", "update_selected_project_item"),
        PaletteCommand("ctrl+shift+i", "Import", "Import a markdown document.", "import_document"),
        PaletteCommand("delete", "Move document to trash", "Move the selected project document to the project trash.", "move_selected_project_document_to_trash"),
        PaletteCommand("ctrl+shift+r", "Restore trash item", "Restore the selected project trash item.", "restore_selected_trash_item"),
        PaletteCommand(
            "ctrl+shift+delete",
            "Permanently delete trash item",
            "Permanently delete the selected project trash item.",
            "permanently_delete_selected_trash_item",
        ),
        PaletteCommand("ctrl+shift+1", "Save Short Summary", "Generate and save a roughly 100 word summary.", "save_short_summary"),
        PaletteCommand("ctrl+shift+2", "Save Medium Summary", "Generate and save a roughly 500 word summary.", "save_medium_summary"),
        PaletteCommand("ctrl+shift+3", "Save Long Summary", "Generate and save a roughly 1000 word summary.", "save_long_summary"),
        PaletteCommand("ctrl+enter", "Search", "Search project documents from the notebook composer.", "terminal_search"),
        PaletteCommand("ctrl+shift+g", "Draft", "Draft into the active document from the notebook composer.", "terminal_draft"),
        PaletteCommand("ctrl+shift+w", "Rewrite", "Rewrite the active document selection from the notebook composer.", "terminal_rewrite"),
        PaletteCommand("ctrl+shift+n", "New Chat", "Create a new notebook chat.", "terminal_new_chat"),
        PaletteCommand("ctrl+shift+x", "Save transcript", "Save the active notebook transcript.", "terminal_save"),
        PaletteCommand("ctrl+shift+v", "Compact chat", "Compact the active notebook chat and save the full transcript.", "terminal_compact"),
        PaletteCommand("ctrl+w", "Close tab", "Close the active document tab.", "close_document_tab"),
        PaletteCommand("ctrl+s", "Save document", "Save the active document without waiting for navigation.", "save_current_document"),
        PaletteCommand("f1", "Focus project", "Move focus to the project and document rail.", "focus_project"),
        PaletteCommand("f2", "Focus document", "Move focus to the main writing viewport.", "focus_document"),
        PaletteCommand("f3", "Focus basket", "Move focus to the promoted context basket.", "focus_basket"),
        PaletteCommand("f4", "Focus notebook", "Move focus to the notebook.", "focus_workflow"),
        PaletteCommand("f5", "Focus inspector", "Move focus to the inspector.", "focus_inspector"),
    ]
    if os.environ.get("EXEGESIS_TEXTUAL_LOCAL_DEVELOPER") == "1":
        commands.insert(
            -5,
            PaletteCommand("ctrl+r", "Restart Exegesis", "Save open documents and restart the Textual shell.", "restart_exegesis"),
        )
    return tuple(commands)


class ExegesisCommandProvider(Provider):
    """Expose Exegesis shell actions in Textual's native command palette."""

    def _callback_for(self, action_name: str) -> Callable[[], None]:
        def callback() -> None:
            self.app.run_worker(self.app.run_action(action_name), thread=False, exclusive=False)

        return callback

    async def search(self, query: str) -> Hits:
        matcher = self.matcher(query)
        for command in default_palette_commands():
            candidate = f"{command.label} {command.key} {command.description}"
            score = matcher.match(candidate)
            if score > 0:
                yield Hit(
                    score,
                    matcher.highlight(_command_display(command)),
                    self._callback_for(command.action),
                    text=command.label,
                    help=command.description,
                )

    async def discover(self) -> Hits:
        for command in default_palette_commands():
            yield DiscoveryHit(
                _command_display(command),
                self._callback_for(command.action),
                text=command.label,
                help=command.description,
            )


__all__ = ["ExegesisCommandProvider", "PaletteCommand", "default_palette_commands"]
