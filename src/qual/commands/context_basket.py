from __future__ import annotations

import json
from dataclasses import dataclass

CONTEXT_BASKET_SEARCH_ENGINE_ACTION = "ExegesisAppService.search_project"
CONTEXT_BASKET_ADD_ENGINE_ACTION = "ExegesisAppService.add_basket_item"
CONTEXT_BASKET_COMMAND_NAME = "context-basket"
CONTEXT_BASKET_FLOW_STEP = "retrieval"
CONTEXT_BASKET_DEMO_PATH_STEP = "retrieve relevant material and gather context"
CONTEXT_BASKET_ACTION_COMPATIBILITY_ALIASES: tuple[tuple[str, str], ...] = (
    ("retrieve", "search"),
    ("retrieve-relevant-material", "search"),
    ("search-project", "search"),
    ("basket-add", "add"),
    ("add-basket-item", "add"),
    ("gather-context", "add"),
    ("promote-context", "add"),
    ("promote-retrieval-result", "add"),
)
CONTEXT_BASKET_ACTION_COMPATIBILITY_ALIAS_BY_TOKEN: dict[str, str] = dict(
    CONTEXT_BASKET_ACTION_COMPATIBILITY_ALIASES
)


@dataclass(frozen=True)
class BasketItem:
    source: str
    content: str
    score: float = 0.0


@dataclass(frozen=True)
class BasketOperation:
    action: str
    item: BasketItem | None = None


@dataclass(frozen=True)
class BasketOperationResult:
    action: str
    engine_action: str
    success: bool
    message: str


@dataclass(frozen=True)
class ContextBasketStatus:
    command: str
    flow_step: str
    demo_path_step: str
    item_count: int
    engine_actions: tuple[str, ...]
    ready: bool


@dataclass(frozen=True)
class ContextBasketActionRoute:
    action: str
    engine_action: str
    command: str
    flow_step: str
    demo_path_step: str
    ready: bool


@dataclass(frozen=True)
class ContextBasketCommandContract:
    command: str
    flow_step: str
    demo_path_step: str
    action_routes: tuple[tuple[str, str], ...]
    action_compatibility_aliases: tuple[tuple[str, str], ...]
    engine_actions: tuple[str, ...]
    ready: bool


@dataclass(frozen=True)
class ContextBasketCommandSmokeContract:
    command: str
    flow_step: str
    demo_path_step: str
    search_action_route: tuple[str, str]
    add_action_route: tuple[str, str]
    action_compatibility_aliases: tuple[tuple[str, str], ...]
    ready: bool


@dataclass(frozen=True)
class ContextBasketReadinessContract:
    command: str
    flow_step: str
    demo_path_step: str
    action_routes: tuple[tuple[str, str], ...]
    expected_action_routes: tuple[tuple[str, str], ...]
    valid_action_routes: tuple[tuple[str, str], ...]
    missing_action_routes: tuple[tuple[str, str], ...]
    action_compatibility_aliases: tuple[tuple[str, str], ...]
    engine_actions: tuple[str, ...]
    missing_engine_actions: tuple[str, ...]
    ready: bool


def build_basket_item(source: str, content: str, score: float = 0.0) -> BasketItem:
    return BasketItem(source=source, content=content, score=score)


def build_basket_operation(action: str, item: BasketItem | None = None) -> BasketOperation:
    return BasketOperation(action=action, item=item)


def build_basket_operation_result(
    action: str,
    engine_action: str,
    success: bool = True,
    message: str = "",
) -> BasketOperationResult:
    return BasketOperationResult(
        action=action,
        engine_action=engine_action,
        success=success,
        message=message or f"{engine_action} for {action}",
    )


def build_context_basket_status(
    item_count: int = 0,
    engine_actions: tuple[str, ...] | None = None,
) -> ContextBasketStatus:
    actions = engine_actions or (
        CONTEXT_BASKET_SEARCH_ENGINE_ACTION,
        CONTEXT_BASKET_ADD_ENGINE_ACTION,
    )
    return ContextBasketStatus(
        command=CONTEXT_BASKET_COMMAND_NAME,
        flow_step=CONTEXT_BASKET_FLOW_STEP,
        demo_path_step=CONTEXT_BASKET_DEMO_PATH_STEP,
        item_count=item_count,
        engine_actions=actions,
        ready=True,
    )


def build_context_basket_action_route(
    action: str,
    engine_action: str,
) -> ContextBasketActionRoute:
    return ContextBasketActionRoute(
        action=action,
        engine_action=engine_action,
        command=CONTEXT_BASKET_COMMAND_NAME,
        flow_step=CONTEXT_BASKET_FLOW_STEP,
        demo_path_step=CONTEXT_BASKET_DEMO_PATH_STEP,
        ready=True,
    )


def build_context_basket_action_routes() -> tuple[ContextBasketActionRoute, ...]:
    return (
        build_context_basket_action_route("search", CONTEXT_BASKET_SEARCH_ENGINE_ACTION),
        build_context_basket_action_route("add", CONTEXT_BASKET_ADD_ENGINE_ACTION),
    )


def build_context_basket_action_route_lookup() -> dict[str, ContextBasketActionRoute]:
    routes = build_context_basket_action_routes()
    result: dict[str, ContextBasketActionRoute] = {}
    for route in routes:
        result[route.action] = route
    for alias, canonical in CONTEXT_BASKET_ACTION_COMPATIBILITY_ALIASES:
        if canonical in result:
            result[alias] = result[canonical]
    return result


def build_context_basket_command_contract() -> ContextBasketCommandContract:
    return ContextBasketCommandContract(
        command=CONTEXT_BASKET_COMMAND_NAME,
        flow_step=CONTEXT_BASKET_FLOW_STEP,
        demo_path_step=CONTEXT_BASKET_DEMO_PATH_STEP,
        action_routes=(
            ("search", CONTEXT_BASKET_SEARCH_ENGINE_ACTION),
            ("add", CONTEXT_BASKET_ADD_ENGINE_ACTION),
        ),
        action_compatibility_aliases=CONTEXT_BASKET_ACTION_COMPATIBILITY_ALIASES,
        engine_actions=(
            CONTEXT_BASKET_SEARCH_ENGINE_ACTION,
            CONTEXT_BASKET_ADD_ENGINE_ACTION,
        ),
        ready=True,
    )


def build_context_basket_command_smoke_contract() -> ContextBasketCommandSmokeContract:
    return ContextBasketCommandSmokeContract(
        command=CONTEXT_BASKET_COMMAND_NAME,
        flow_step=CONTEXT_BASKET_FLOW_STEP,
        demo_path_step=CONTEXT_BASKET_DEMO_PATH_STEP,
        search_action_route=("search", CONTEXT_BASKET_SEARCH_ENGINE_ACTION),
        add_action_route=("add", CONTEXT_BASKET_ADD_ENGINE_ACTION),
        action_compatibility_aliases=CONTEXT_BASKET_ACTION_COMPATIBILITY_ALIASES,
        ready=True,
    )


def build_context_basket_readiness_contract() -> ContextBasketReadinessContract:
    expected_routes: tuple[tuple[str, str], ...] = (
        ("search", CONTEXT_BASKET_SEARCH_ENGINE_ACTION),
        ("add", CONTEXT_BASKET_ADD_ENGINE_ACTION),
    )
    return ContextBasketReadinessContract(
        command=CONTEXT_BASKET_COMMAND_NAME,
        flow_step=CONTEXT_BASKET_FLOW_STEP,
        demo_path_step=CONTEXT_BASKET_DEMO_PATH_STEP,
        action_routes=expected_routes,
        expected_action_routes=expected_routes,
        valid_action_routes=expected_routes,
        missing_action_routes=(),
        action_compatibility_aliases=CONTEXT_BASKET_ACTION_COMPATIBILITY_ALIASES,
        engine_actions=(
            CONTEXT_BASKET_SEARCH_ENGINE_ACTION,
            CONTEXT_BASKET_ADD_ENGINE_ACTION,
        ),
        missing_engine_actions=(),
        ready=True,
    )


def resolve_context_basket_action(action: str) -> tuple[str, str]:
    original = action.strip().lower()
    normalized_underscore = original.replace("-", "_").replace(" ", "_")
    if original in CONTEXT_BASKET_ACTION_COMPATIBILITY_ALIAS_BY_TOKEN:
        canonical = CONTEXT_BASKET_ACTION_COMPATIBILITY_ALIAS_BY_TOKEN[original]
    elif normalized_underscore in CONTEXT_BASKET_ACTION_COMPATIBILITY_ALIAS_BY_TOKEN:
        canonical = CONTEXT_BASKET_ACTION_COMPATIBILITY_ALIAS_BY_TOKEN[normalized_underscore]
    elif normalized_underscore == "search":
        canonical = "search"
    elif normalized_underscore == "add":
        canonical = "add"
    elif normalized_underscore == "list":
        canonical = "search"
    else:
        canonical = "search"
    engine_action = (
        CONTEXT_BASKET_SEARCH_ENGINE_ACTION
        if canonical == "search"
        else CONTEXT_BASKET_ADD_ENGINE_ACTION
    )
    return (canonical, engine_action)


def run_context_basket_action_route_lookup_json() -> str:
    lookup = build_context_basket_action_route_lookup()
    serializable = {
        action: {
            "engine_action": route.engine_action,
            "command": route.command,
            "flow_step": route.flow_step,
            "demo_path_step": route.demo_path_step,
            "ready": route.ready,
        }
        for action, route in lookup.items()
    }
    return json.dumps(serializable, indent=2)


def run_context_basket_action_routes() -> tuple[ContextBasketActionRoute, ...]:
    return build_context_basket_action_routes()


def run_context_basket_action_routes_json() -> str:
    routes = build_context_basket_action_routes()
    serializable = [
        {
            "action": route.action,
            "engine_action": route.engine_action,
            "command": route.command,
            "flow_step": route.flow_step,
            "demo_path_step": route.demo_path_step,
            "ready": route.ready,
        }
        for route in routes
    ]
    return json.dumps(serializable, indent=2)


def run_context_basket_command_contract() -> ContextBasketCommandContract:
    return build_context_basket_command_contract()


def run_context_basket_command_contract_json() -> str:
    contract = build_context_basket_command_contract()
    return json.dumps(
        {
            "command": contract.command,
            "flow_step": contract.flow_step,
            "demo_path_step": contract.demo_path_step,
            "action_routes": [list(route) for route in contract.action_routes],
            "action_compatibility_aliases": [
                list(alias) for alias in contract.action_compatibility_aliases
            ],
            "engine_actions": list(contract.engine_actions),
            "ready": contract.ready,
        },
        indent=2,
    )


def run_context_basket_command_smoke_contract() -> ContextBasketCommandSmokeContract:
    return build_context_basket_command_smoke_contract()


def run_context_basket_command_smoke_contract_json() -> str:
    contract = build_context_basket_command_smoke_contract()
    return json.dumps(
        {
            "command": contract.command,
            "flow_step": contract.flow_step,
            "demo_path_step": contract.demo_path_step,
            "search_action_route": list(contract.search_action_route),
            "add_action_route": list(contract.add_action_route),
            "action_compatibility_aliases": [
                list(alias) for alias in contract.action_compatibility_aliases
            ],
            "ready": contract.ready,
        },
        indent=2,
    )


def run_context_basket_readiness_contract() -> ContextBasketReadinessContract:
    return build_context_basket_readiness_contract()


def run_context_basket_readiness_contract_json() -> str:
    contract = build_context_basket_readiness_contract()
    return json.dumps(
        {
            "command": contract.command,
            "flow_step": contract.flow_step,
            "demo_path_step": contract.demo_path_step,
            "action_routes": [list(route) for route in contract.action_routes],
            "expected_action_routes": [
                list(route) for route in contract.expected_action_routes
            ],
            "valid_action_routes": [list(route) for route in contract.valid_action_routes],
            "missing_action_routes": [
                list(route) for route in contract.missing_action_routes
            ],
            "engine_actions": list(contract.engine_actions),
            "missing_engine_actions": list(contract.missing_engine_actions),
            "ready": contract.ready,
        },
        indent=2,
    )


def validate_context_basket_command_contract(
    contract: ContextBasketCommandContract,
) -> tuple[bool, tuple[str, ...]]:
    errors: list[str] = []
    if contract.command != CONTEXT_BASKET_COMMAND_NAME:
        errors.append(
            f"command mismatch: expected {CONTEXT_BASKET_COMMAND_NAME!r}, "
            f"got {contract.command!r}"
        )
    if contract.flow_step != CONTEXT_BASKET_FLOW_STEP:
        errors.append(
            f"flow_step mismatch: expected {CONTEXT_BASKET_FLOW_STEP!r}, "
            f"got {contract.flow_step!r}"
        )
    expected_routes: tuple[tuple[str, str], ...] = (
        ("search", CONTEXT_BASKET_SEARCH_ENGINE_ACTION),
        ("add", CONTEXT_BASKET_ADD_ENGINE_ACTION),
    )
    if contract.action_routes != expected_routes:
        errors.append(
            f"action_routes mismatch: expected {expected_routes!r}, "
            f"got {contract.action_routes!r}"
        )
    expected_engine_actions: tuple[str, ...] = (
        CONTEXT_BASKET_SEARCH_ENGINE_ACTION,
        CONTEXT_BASKET_ADD_ENGINE_ACTION,
    )
    if contract.engine_actions != expected_engine_actions:
        errors.append(
            f"engine_actions mismatch: expected {expected_engine_actions!r}, "
            f"got {contract.engine_actions!r}"
        )
    return (len(errors) == 0, tuple(errors))
