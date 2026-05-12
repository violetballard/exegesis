from __future__ import annotations

from typing import Literal, TypeAlias

SelectionObjectType: TypeAlias = Literal[
    "project_item",
    "document_selection",
    "workflow_card",
    "basket_item",
    "patch_proposal",
    "search_result",
    "status",
]

OBJECT_TYPES: tuple[SelectionObjectType, ...] = (
    "project_item",
    "document_selection",
    "workflow_card",
    "basket_item",
    "patch_proposal",
    "search_result",
    "status",
)
