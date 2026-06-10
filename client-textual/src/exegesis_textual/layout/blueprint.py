from __future__ import annotations

from dataclasses import dataclass

from exegesis_textual.panes.basket_pane import BASKET_PANE_COPY
from exegesis_textual.panes.document_pane import DOCUMENT_PANE_COPY
from exegesis_textual.panes.project_pane import PROJECT_PANE_COPY
from exegesis_textual.workflow.workflow_pane import WORKFLOW_PANE_COPY

@dataclass(frozen=True)
class ShellBlueprint:
    protocol_target: str
    adapter_state: str
    engine_integration: str
    panes: tuple["PaneBlueprint", ...]


@dataclass(frozen=True)
class PaneBlueprint:
    slug: str
    title: str
    purpose: str


def shortcut_label(chord: str, description: str) -> Text:
    label = Text()
    label.append(chord, style="#ffa62b bold")
    if description:
        label.append(f" {description}", style="bold")
    return label


SHELL_BLUEPRINT = ShellBlueprint(
    protocol_target="A2UI v0.9 (planned target)",
    adapter_state="Provisional shell adapter only; not yet protocol-conformant.",
    engine_integration="Scaffold-only shell with placeholder workflow surfaces.",
    panes=(
        PaneBlueprint("project", PROJECT_PANE_COPY.title, PROJECT_PANE_COPY.summary),
        PaneBlueprint("document", DOCUMENT_PANE_COPY.title, DOCUMENT_PANE_COPY.summary),
        PaneBlueprint("basket", BASKET_PANE_COPY.title, BASKET_PANE_COPY.summary),
        PaneBlueprint("workflow", WORKFLOW_PANE_COPY.title, WORKFLOW_PANE_COPY.summary),
        PaneBlueprint("inspector", "Inspector", "Diagnostics and detail rail."),
    ),
)


__all__ = ["PaneBlueprint", "SHELL_BLUEPRINT", "ShellBlueprint"]
