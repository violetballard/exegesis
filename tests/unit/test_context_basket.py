from __future__ import annotations

import json
import unittest

from src.qual.commands.context_basket import (
    CONTEXT_BASKET_ADD_ENGINE_ACTION,
    CONTEXT_BASKET_COMMAND_NAME,
    CONTEXT_BASKET_DEMO_PATH_STEP,
    CONTEXT_BASKET_FLOW_STEP,
    CONTEXT_BASKET_SEARCH_ENGINE_ACTION,
    BasketItem,
    BasketOperation,
    BasketOperationResult,
    ContextBasketActionRoute,
    ContextBasketCommandContract,
    ContextBasketCommandSmokeContract,
    ContextBasketReadinessContract,
    ContextBasketStatus,
    build_basket_item,
    build_basket_operation,
    build_basket_operation_result,
    build_context_basket_action_route,
    build_context_basket_action_route_lookup,
    build_context_basket_action_routes,
    build_context_basket_command_contract,
    build_context_basket_command_smoke_contract,
    build_context_basket_readiness_contract,
    build_context_basket_status,
    resolve_context_basket_action,
    run_context_basket_action_route_lookup_json,
    run_context_basket_action_routes,
    run_context_basket_action_routes_json,
    run_context_basket_command_contract,
    run_context_basket_command_contract_json,
    run_context_basket_command_smoke_contract,
    run_context_basket_command_smoke_contract_json,
    run_context_basket_readiness_contract,
    run_context_basket_readiness_contract_json,
    validate_context_basket_command_contract,
)


class BasketItemTests(unittest.TestCase):
    def test_basket_item_default_score(self) -> None:
        item = build_basket_item("source", "content")
        self.assertEqual(item.source, "source")
        self.assertEqual(item.content, "content")
        self.assertEqual(item.score, 0.0)

    def test_basket_item_custom_score(self) -> None:
        item = build_basket_item("source", "content", score=0.85)
        self.assertEqual(item.score, 0.85)

    def test_basket_item_is_frozen(self) -> None:
        item = build_basket_item("source", "content")
        with self.assertRaises(Exception):
            item.source = "other"  # type: ignore[attr-defined]


class BasketOperationTests(unittest.TestCase):
    def test_operation_with_item(self) -> None:
        item = build_basket_item("src", "ctx")
        op = build_basket_operation("add", item)
        self.assertEqual(op.action, "add")
        self.assertEqual(op.item, item)

    def test_operation_without_item(self) -> None:
        op = build_basket_operation("search")
        self.assertEqual(op.action, "search")
        self.assertIsNone(op.item)


class BasketOperationResultTests(unittest.TestCase):
    def test_result_default_message(self) -> None:
        result = build_basket_operation_result("add", "engine.add")
        self.assertEqual(result.action, "add")
        self.assertEqual(result.engine_action, "engine.add")
        self.assertTrue(result.success)

    def test_result_custom_message(self) -> None:
        result = build_basket_operation_result(
            "add", "engine.add", message="added item"
        )
        self.assertEqual(result.message, "added item")

    def test_result_failure(self) -> None:
        result = build_basket_operation_result(
            "add", "engine.add", success=False, message="not found"
        )
        self.assertFalse(result.success)
        self.assertEqual(result.message, "not found")


class ContextBasketStatusTests(unittest.TestCase):
    def test_status_defaults(self) -> None:
        status = build_context_basket_status()
        self.assertEqual(status.command, CONTEXT_BASKET_COMMAND_NAME)
        self.assertEqual(status.flow_step, CONTEXT_BASKET_FLOW_STEP)
        self.assertEqual(status.demo_path_step, CONTEXT_BASKET_DEMO_PATH_STEP)
        self.assertEqual(status.item_count, 0)
        self.assertTrue(status.ready)

    def test_status_item_count(self) -> None:
        status = build_context_basket_status(item_count=3)
        self.assertEqual(status.item_count, 3)

    def test_status_engine_actions(self) -> None:
        status = build_context_basket_status()
        self.assertIn(CONTEXT_BASKET_SEARCH_ENGINE_ACTION, status.engine_actions)
        self.assertIn(CONTEXT_BASKET_ADD_ENGINE_ACTION, status.engine_actions)


class ContextBasketActionRouteTests(unittest.TestCase):
    def test_action_routes_return_two_routes(self) -> None:
        routes = build_context_basket_action_routes()
        self.assertEqual(len(routes), 2)

    def test_search_route(self) -> None:
        routes = build_context_basket_action_routes()
        search_route = routes[0]
        self.assertEqual(search_route.action, "search")
        self.assertEqual(search_route.engine_action, CONTEXT_BASKET_SEARCH_ENGINE_ACTION)
        self.assertEqual(search_route.command, CONTEXT_BASKET_COMMAND_NAME)
        self.assertEqual(search_route.flow_step, CONTEXT_BASKET_FLOW_STEP)
        self.assertTrue(search_route.ready)

    def test_add_route(self) -> None:
        routes = build_context_basket_action_routes()
        add_route = routes[1]
        self.assertEqual(add_route.action, "add")
        self.assertEqual(add_route.engine_action, CONTEXT_BASKET_ADD_ENGINE_ACTION)
        self.assertTrue(add_route.ready)

    def test_route_lookup_includes_canonical_actions(self) -> None:
        lookup = build_context_basket_action_route_lookup()
        self.assertIn("search", lookup)
        self.assertIn("add", lookup)

    def test_route_lookup_includes_compatibility_aliases(self) -> None:
        lookup = build_context_basket_action_route_lookup()
        self.assertIn("retrieve", lookup)
        self.assertIn("basket-add", lookup)
        self.assertIn("gather-context", lookup)

    def test_route_lookup_aliases_resolve_to_canonical_engine_action(self) -> None:
        lookup = build_context_basket_action_route_lookup()
        search_route = lookup["search"]
        retrieve_route = lookup["retrieve"]
        self.assertEqual(search_route.engine_action, retrieve_route.engine_action)
        add_route = lookup["add"]
        basket_add_route = lookup["basket-add"]
        self.assertEqual(add_route.engine_action, basket_add_route.engine_action)


class ContextBasketCommandContractTests(unittest.TestCase):
    def test_contract_is_valid(self) -> None:
        contract = build_context_basket_command_contract()
        valid, errors = validate_context_basket_command_contract(contract)
        self.assertTrue(valid)
        self.assertEqual(len(errors), 0)

    def test_contract_covers_expected_actions(self) -> None:
        contract = build_context_basket_command_contract()
        action_names = [route[0] for route in contract.action_routes]
        self.assertIn("search", action_names)
        self.assertIn("add", action_names)

    def test_contract_includes_all_engine_actions(self) -> None:
        contract = build_context_basket_command_contract()
        self.assertIn(CONTEXT_BASKET_SEARCH_ENGINE_ACTION, contract.engine_actions)
        self.assertIn(CONTEXT_BASKET_ADD_ENGINE_ACTION, contract.engine_actions)

    def test_contract_includes_compatibility_aliases(self) -> None:
        contract = build_context_basket_command_contract()
        alias_tokens = [alias[0] for alias in contract.action_compatibility_aliases]
        self.assertIn("retrieve", alias_tokens)
        self.assertIn("gather-context", alias_tokens)

    def test_contract_validation_rejects_wrong_command(self) -> None:
        contract = build_context_basket_command_contract()
        wrong_contract = ContextBasketCommandContract(
            command="wrong-command",
            flow_step=contract.flow_step,
            demo_path_step=contract.demo_path_step,
            action_routes=contract.action_routes,
            action_compatibility_aliases=contract.action_compatibility_aliases,
            engine_actions=contract.engine_actions,
            ready=contract.ready,
        )
        valid, errors = validate_context_basket_command_contract(wrong_contract)
        self.assertFalse(valid)
        self.assertTrue(any("command mismatch" in e for e in errors))

    def test_contract_validation_rejects_wrong_flow_step(self) -> None:
        contract = build_context_basket_command_contract()
        wrong_contract = ContextBasketCommandContract(
            command=contract.command,
            flow_step="wrong-flow-step",
            demo_path_step=contract.demo_path_step,
            action_routes=contract.action_routes,
            action_compatibility_aliases=contract.action_compatibility_aliases,
            engine_actions=contract.engine_actions,
            ready=contract.ready,
        )
        valid, errors = validate_context_basket_command_contract(wrong_contract)
        self.assertFalse(valid)
        self.assertTrue(any("flow_step mismatch" in e for e in errors))


class ContextBasketSmokeContractTests(unittest.TestCase):
    def test_smoke_contract_has_search_route(self) -> None:
        contract = build_context_basket_command_smoke_contract()
        self.assertEqual(
            contract.search_action_route,
            ("search", CONTEXT_BASKET_SEARCH_ENGINE_ACTION),
        )

    def test_smoke_contract_has_add_route(self) -> None:
        contract = build_context_basket_command_smoke_contract()
        self.assertEqual(
            contract.add_action_route,
            ("add", CONTEXT_BASKET_ADD_ENGINE_ACTION),
        )

    def test_smoke_contract_is_ready(self) -> None:
        contract = build_context_basket_command_smoke_contract()
        self.assertTrue(contract.ready)


class ContextBasketReadinessContractTests(unittest.TestCase):
    def test_readiness_contract_has_no_missing_routes(self) -> None:
        contract = build_context_basket_readiness_contract()
        self.assertEqual(len(contract.missing_action_routes), 0)

    def test_readiness_contract_has_no_missing_engine_actions(self) -> None:
        contract = build_context_basket_readiness_contract()
        self.assertEqual(len(contract.missing_engine_actions), 0)

    def test_readiness_contract_valid_routes_match_expected(self) -> None:
        contract = build_context_basket_readiness_contract()
        self.assertEqual(
            contract.valid_action_routes, contract.expected_action_routes
        )

    def test_readiness_contract_is_ready(self) -> None:
        contract = build_context_basket_readiness_contract()
        self.assertTrue(contract.ready)


class ResolveContextBasketActionTests(unittest.TestCase):
    def test_resolve_search(self) -> None:
        canonical, engine_action = resolve_context_basket_action("search")
        self.assertEqual(canonical, "search")
        self.assertEqual(engine_action, CONTEXT_BASKET_SEARCH_ENGINE_ACTION)

    def test_resolve_add(self) -> None:
        canonical, engine_action = resolve_context_basket_action("add")
        self.assertEqual(canonical, "add")
        self.assertEqual(engine_action, CONTEXT_BASKET_ADD_ENGINE_ACTION)

    def test_resolve_list_defaults_to_search(self) -> None:
        canonical, engine_action = resolve_context_basket_action("list")
        self.assertEqual(canonical, "search")
        self.assertEqual(engine_action, CONTEXT_BASKET_SEARCH_ENGINE_ACTION)

    def test_resolve_retrieve_alias(self) -> None:
        canonical, engine_action = resolve_context_basket_action("retrieve")
        self.assertEqual(canonical, "search")
        self.assertEqual(engine_action, CONTEXT_BASKET_SEARCH_ENGINE_ACTION)

    def test_resolve_basket_add_alias(self) -> None:
        canonical, engine_action = resolve_context_basket_action("basket-add")
        self.assertEqual(canonical, "add")
        self.assertEqual(engine_action, CONTEXT_BASKET_ADD_ENGINE_ACTION)

    def test_resolve_unknown_defaults_to_search(self) -> None:
        canonical, engine_action = resolve_context_basket_action("unknown-action")
        self.assertEqual(canonical, "search")
        self.assertEqual(engine_action, CONTEXT_BASKET_SEARCH_ENGINE_ACTION)

    def test_resolve_case_insensitive(self) -> None:
        canonical, engine_action = resolve_context_basket_action("SEARCH")
        self.assertEqual(canonical, "search")
        self.assertEqual(engine_action, CONTEXT_BASKET_SEARCH_ENGINE_ACTION)


class ContextBasketJsonOutputTests(unittest.TestCase):
    def test_action_routes_json_is_valid(self) -> None:
        output = run_context_basket_action_routes_json()
        data = json.loads(output)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)

    def test_action_route_lookup_json_is_valid(self) -> None:
        output = run_context_basket_action_route_lookup_json()
        data = json.loads(output)
        self.assertIsInstance(data, dict)
        self.assertIn("search", data)
        self.assertIn("add", data)

    def test_command_contract_json_is_valid(self) -> None:
        output = run_context_basket_command_contract_json()
        data = json.loads(output)
        self.assertEqual(data["command"], CONTEXT_BASKET_COMMAND_NAME)
        self.assertEqual(data["flow_step"], CONTEXT_BASKET_FLOW_STEP)
        self.assertTrue(data["ready"])

    def test_smoke_contract_json_is_valid(self) -> None:
        output = run_context_basket_command_smoke_contract_json()
        data = json.loads(output)
        self.assertEqual(data["command"], CONTEXT_BASKET_COMMAND_NAME)
        self.assertTrue(data["ready"])

    def test_readiness_contract_json_is_valid(self) -> None:
        output = run_context_basket_readiness_contract_json()
        data = json.loads(output)
        self.assertEqual(data["command"], CONTEXT_BASKET_COMMAND_NAME)
        self.assertTrue(data["ready"])
        self.assertEqual(len(data["missing_engine_actions"]), 0)


class RunFunctionTests(unittest.TestCase):
    def test_run_command_contract_returns_contract(self) -> None:
        result = run_context_basket_command_contract()
        self.assertIsInstance(result, ContextBasketCommandContract)
        self.assertTrue(result.ready)

    def test_run_smoke_contract_returns_contract(self) -> None:
        result = run_context_basket_command_smoke_contract()
        self.assertIsInstance(result, ContextBasketCommandSmokeContract)
        self.assertTrue(result.ready)

    def test_run_readiness_contract_returns_contract(self) -> None:
        result = run_context_basket_readiness_contract()
        self.assertIsInstance(result, ContextBasketReadinessContract)
        self.assertTrue(result.ready)

    def test_run_action_routes_returns_routes(self) -> None:
        result = run_context_basket_action_routes()
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], ContextBasketActionRoute)
