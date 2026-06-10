from __future__ import annotations

import uuid

from exegesis_engine.state.models import BasketItem, WorkflowCard


class PlanService:
    def plan_from_basket(
        self,
        basket_items: list[BasketItem],
        *,
        context_snippets: dict[str, list[str]] | None = None,
        prior_context_summary: str | None = None,
        metadata: dict[str, object] | None = None,
    ) -> WorkflowCard:
        if not isinstance(basket_items, list):
            raise TypeError("basket_items must be a list")
        for item in basket_items:
            if not isinstance(item, BasketItem):
                raise TypeError("basket_items must contain only BasketItem instances")

        if context_snippets is not None:
            if not isinstance(context_snippets, dict):
                raise TypeError("context_snippets must be a dictionary")
            for k, v in context_snippets.items():
                if not isinstance(k, str):
                    raise TypeError("context_snippets keys must be strings")
                if "\x00" in k:
                    raise ValueError("context_snippets keys cannot contain null bytes")
                if not isinstance(v, list):
                    raise TypeError("context_snippets values must be lists")
                for snippet in v:
                    if not isinstance(snippet, str):
                        raise TypeError("context_snippets list elements must be strings")
                    if "\x00" in snippet:
                        raise ValueError("context_snippets list elements cannot contain null bytes")
        if prior_context_summary is not None and not isinstance(prior_context_summary, str):
            raise TypeError("prior_context_summary must be a string")
        if metadata is not None:
            if not isinstance(metadata, dict):
                raise TypeError("metadata must be a dictionary")
            for key in metadata:
                if not isinstance(key, str):
                    raise TypeError("metadata keys must be string types")

        if not basket_items:
            body = "Basket is empty. Add context items before planning."
        else:
            lines = []
            if prior_context_summary:
                lines.append(f"Prior session context:\n{prior_context_summary}\n")
            for item in basket_items:
                snippets = (context_snippets or {}).get(item.id, [])
                if snippets:
                    for idx, snippet in enumerate(snippets):
                        excerpt = snippet[:200].strip()
                        if len(snippets) > 1:
                            lines.append(f"- {item.label} ({item.item_type}) [{idx+1}]: {excerpt}")
                        else:
                            lines.append(f"- {item.label} ({item.item_type}): {excerpt}")
                else:
                    lines.append(f"- Use {item.label} ({item.item_type})")
            body = "\n".join(lines)

        card_metadata = {
            "item_count": len(basket_items),
            "snippet_count": sum(len(v) for v in (context_snippets or {}).values()),
        }
        if metadata is not None:
            card_metadata.update(metadata)

        return WorkflowCard(
            id=f"plan-{uuid.uuid4()}",
            card_type="plan",
            title="Plan From Basket",
            body=body,
            metadata=card_metadata,
            actions=[{"id": "save_to_project", "label": "Save plan"}],
        )
