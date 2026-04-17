from __future__ import annotations

import copy
import hashlib
import json
import unicodedata
from collections.abc import Mapping, Set
from dataclasses import dataclass, fields, is_dataclass
from typing import Any, Callable, Protocol

A2UI_VERSION = 1
A2UI_CONTRACT_VERSION = 2
A2UI_ACTION_SCHEMA_VERSION = 1
A2UI_CAPABILITIES_SCHEMA_VERSION = 1
SELECTION_SCHEMA_VERSION = 1
CARD_CONTRACT_VERSION = 1
TERMINAL_FALLBACK_SCHEMA_VERSION = 1
TERMINAL_ARTIFACT_SCHEMA_VERSION = 1
TERMINAL_ARTIFACT_RENDER_TARGET_SCHEMA_VERSION = 1
TERMINAL_ARTIFACT_RENDERING_SCHEMA_VERSION = 1
TERMINAL_ARTIFACT_CLI_FALLBACK_SCHEMA_VERSION = 1
TERMINAL_ARTIFACT_CLI_FALLBACK_TARGET_SCHEMA_VERSION = 1
TERMINAL_ARTIFACT_RAW_LEAF_CARD_DEFAULT_SCHEMA_VERSION = 1
_TERMINAL_ARTIFACT_ENVELOPE_TYPE = "TerminalArtifact"
GENERIC_CARD_TYPE = "GenericCard"
UNKNOWN_CARD_TYPE = "UnknownCard"
DEFAULT_UNKNOWN_CARD_PREVIEW_BYTES = 8_192
FALLBACK_COPY_ACTION_ID = "copy_to_clipboard"
GENERIC_FALLBACK_SUBTITLE = "Rendered as GenericCard because client does not support this specialized card."
UNKNOWN_FALLBACK_SUBTITLE = "Read-only fallback view with safe primitive blocks and raw JSON preview."
GENERIC_FALLBACK_TITLE_PREFIX = "Fallback view for "
UNKNOWN_FALLBACK_TITLE_PREFIX = "Unsupported card type: "
TERMINAL_ARTIFACT_SUPPORTED_KINDS: tuple[str, str, str] = ("card", "action", "selection")
TERMINAL_ARTIFACT_DEFAULT_KIND = "card"
_RESERVED_CARD_TYPES: tuple[str, ...] = (GENERIC_CARD_TYPE, UNKNOWN_CARD_TYPE)
_SPECIALIZED_CARD_TYPES: tuple[str, ...] = (
    "ProposedEditCard",
    "EvidenceCard",
    "QuestionsCard",
    "RunLogCard",
)

ALLOWED_ACTION_IDS: tuple[str, ...] = (
    "apply_patch",
    "reject_patch",
    "open_section",
    "open_corpus_item",
    "pin_to_context_set",
    "create_context_set",
    "run_agent",
    "refresh_license",
    "export_document",
    "copy_to_clipboard",
)

REQUIRED_PRIMITIVE_BLOCKS: tuple[str, ...] = (
    "MarkdownBlock",
    "KeyValueBlock",
    "ListBlock",
    "TableBlock",
    "AlertBlock",
    "ProgressBlock",
    "CodeBlock",
)

_PRIMITIVE_BLOCK_SET = set(REQUIRED_PRIMITIVE_BLOCKS)
_ALLOWED_ACTION_SET = set(ALLOWED_ACTION_IDS)
_TERMINAL_ARTIFACT_SUPPORTED_KIND_SET = set(TERMINAL_ARTIFACT_SUPPORTED_KINDS)
_TERMINAL_ARTIFACT_NON_CARD_KIND_SET = set(TERMINAL_ARTIFACT_SUPPORTED_KINDS) - {TERMINAL_ARTIFACT_DEFAULT_KIND}

_PRIMITIVE_BLOCK_SCHEMAS: dict[str, tuple[str, ...]] = {
    "MarkdownBlock": ("markdown",),
    "KeyValueBlock": ("items",),
    "ListBlock": ("items",),
    "TableBlock": ("rows",),
    "AlertBlock": ("severity", "title", "message"),
    "ProgressBlock": ("status_text", "title"),
    "CodeBlock": ("code", "language", "collapsed"),
}

_PRIMITIVE_BLOCK_REQUIRED_FIELDS: dict[str, tuple[str, ...]] = {
    "MarkdownBlock": ("markdown",),
    "KeyValueBlock": ("items",),
    "ListBlock": ("items",),
    "TableBlock": ("rows",),
    "AlertBlock": ("message",),
    "ProgressBlock": ("status_text",),
    "CodeBlock": ("code",),
}

_ACTION_SCHEMAS: dict[str, dict[str, type]] = {
    "apply_patch": {"patch_id": str},
    "reject_patch": {"patch_id": str},
    "open_section": {"section_id": str},
    "open_corpus_item": {"item_id": str},
    "pin_to_context_set": {"item_id": str},
    "create_context_set": {"name": str},
    "run_agent": {"operation": str},
    "refresh_license": {},
    "export_document": {"format": str},
    "copy_to_clipboard": {"text": str},
}

_CAPABILITIES_REQUIRED_FIELDS: tuple[str, ...] = (
    "a2ui_version",
    "client_name",
    "cards_supported",
    "primitive_blocks_supported",
    "actions_supported",
    "max_payload_bytes",
    "supports_streaming",
)


@dataclass(frozen=True)
class A2UICapabilities:
    a2ui_version: int
    client_name: str
    cards_supported: tuple[str, ...]
    primitive_blocks_supported: tuple[str, ...]
    actions_supported: tuple[str, ...]
    max_payload_bytes: int
    supports_streaming: bool


@dataclass(frozen=True)
class ActionRef:
    id: str
    label: str
    payload: dict[str, Any]
    confirm: dict[str, str] | None = None
    policy_sensitive: bool = False


@dataclass(frozen=True)
class SelectionRef:
    id: str
    label: str
    payload: dict[str, Any]
    selected: bool = False
    disabled: bool = False


class PolicyGate(Protocol):
    def allow_action(self, action_id: str, payload: dict[str, Any], *, policy_sensitive: bool) -> bool:
        ...


class A2UISessionStore:
    def __init__(self) -> None:
        self._by_session: dict[str, A2UICapabilities] = {}

    def register(self, session_id: str, capabilities: A2UICapabilities) -> None:
        self._by_session[session_id] = normalize_capabilities(capabilities)

    def get(self, session_id: str) -> A2UICapabilities:
        if session_id not in self._by_session:
            raise KeyError(f"Unknown session: {session_id}")
        return self._by_session[session_id]


def _snapshot_contract_section(section: Mapping[str, Any]) -> dict[str, Any]:
    return copy.deepcopy(section)


def describe_a2ui_contract() -> dict[str, Any]:
    """Return the stable, versioned A2UI contract manifest.

    The manifest is intentionally JSON-serializable so clients can fingerprint
    the contract they negotiated without having to mirror internal module state.
    """

    manifest = _build_a2ui_contract_manifest()
    manifest["contract_fingerprint"] = a2ui_contract_fingerprint()
    capabilities = _snapshot_contract_section(manifest["schemas"]["capabilities"])
    manifest["capabilities"] = capabilities
    manifest["capabilities_fingerprint"] = capabilities["contract_fingerprint"]
    manifest["capabilities_contract"] = _snapshot_contract_section(capabilities)
    manifest["capabilities_contract_fingerprint"] = manifest["capabilities_fingerprint"]
    card_contract = _snapshot_contract_section(manifest["schemas"]["card_contract"])
    manifest["card_contract"] = card_contract
    manifest["card_contract_fingerprint"] = card_contract["contract_fingerprint"]
    action_contract = _snapshot_contract_section(manifest["schemas"]["action"])
    manifest["action"] = action_contract
    manifest["action_fingerprint"] = action_contract["contract_fingerprint"]
    manifest["action_contract"] = _snapshot_contract_section(action_contract)
    manifest["action_contract_fingerprint"] = manifest["action_fingerprint"]
    selection_contract = _snapshot_contract_section(manifest["schemas"]["selection"])
    manifest["selection"] = selection_contract
    manifest["selection_fingerprint"] = selection_contract["contract_fingerprint"]
    manifest["selection_contract"] = _snapshot_contract_section(selection_contract)
    manifest["selection_contract_fingerprint"] = manifest["selection_fingerprint"]
    manifest["card_fingerprint"] = card_contract_fingerprint()
    terminal_artifact_rendering = _snapshot_contract_section(
        manifest["schemas"]["terminal_artifact_rendering"]
    )
    manifest["terminal_artifact_rendering"] = terminal_artifact_rendering
    manifest["terminal_artifact_rendering_fingerprint"] = terminal_artifact_rendering["contract_fingerprint"]
    terminal_artifact_render_target = _snapshot_contract_section(
        manifest["schemas"]["terminal_artifact_render_target"]
    )
    manifest["terminal_artifact_render_target"] = terminal_artifact_render_target
    manifest["terminal_artifact_render_target_fingerprint"] = terminal_artifact_render_target[
        "contract_fingerprint"
    ]
    terminal_artifact_cli_fallback = _snapshot_contract_section(
        manifest["schemas"]["terminal_artifact_cli_fallback"]
    )
    manifest["terminal_artifact_cli_fallback"] = terminal_artifact_cli_fallback
    manifest["terminal_artifact_cli_fallback_fingerprint"] = terminal_artifact_cli_fallback[
        "contract_fingerprint"
    ]
    terminal_artifact_cli_fallback_target = _snapshot_contract_section(
        manifest["schemas"]["terminal_artifact_cli_fallback_target"]
    )
    manifest["terminal_artifact_cli_fallback_target"] = terminal_artifact_cli_fallback_target
    manifest["terminal_artifact_cli_fallback_target_fingerprint"] = terminal_artifact_cli_fallback_target[
        "contract_fingerprint"
    ]
    manifest["terminal_artifact_cli_fallback_target_contract"] = _snapshot_contract_section(
        terminal_artifact_cli_fallback_target
    )
    manifest["terminal_artifact_cli_fallback_target_contract_fingerprint"] = manifest[
        "terminal_artifact_cli_fallback_target_fingerprint"
    ]
    terminal_artifact_contract = _snapshot_contract_section(manifest["schemas"]["terminal_artifact"])
    manifest["terminal_artifact"] = terminal_artifact_contract
    manifest["terminal_artifact_contract"] = _snapshot_contract_section(terminal_artifact_contract)
    manifest["terminal_artifact_contract_fingerprint"] = manifest["terminal_artifact_fingerprint"]
    manifest["terminal_artifact_render_target_contract"] = _snapshot_contract_section(
        terminal_artifact_render_target
    )
    manifest["terminal_artifact_render_target_contract_fingerprint"] = manifest["terminal_artifact_render_target_fingerprint"]
    manifest["terminal_fallback"] = _snapshot_contract_section(manifest["terminal_fallback"])
    manifest["terminal_fallback_contract"] = _snapshot_contract_section(manifest["terminal_fallback"])
    manifest["terminal_fallback_contract_fingerprint"] = manifest["terminal_fallback_fingerprint"]
    terminal_artifact_raw_leaf_card_default = _snapshot_contract_section(
        terminal_artifact_contract["raw_leaf_card_default_contract"]
    )
    manifest["terminal_artifact_raw_leaf_card_default"] = terminal_artifact_raw_leaf_card_default
    manifest["terminal_artifact_raw_leaf_card_default_fingerprint"] = terminal_artifact_raw_leaf_card_default[
        "contract_fingerprint"
    ]
    manifest["terminal_artifact_raw_leaf_card_default_contract_fingerprints"] = _snapshot_contract_section(
        terminal_artifact_contract["raw_leaf_card_default_contract_fingerprints"]
    )
    manifest["terminal_artifact_raw_leaf_card_default_contract"] = _snapshot_contract_section(
        terminal_artifact_raw_leaf_card_default
    )
    manifest["terminal_artifact_raw_leaf_card_default_contract_fingerprint"] = manifest[
        "terminal_artifact_raw_leaf_card_default_fingerprint"
    ]
    terminal_artifact_raw_leaf_card_default_policy = _snapshot_contract_section(
        terminal_artifact_contract["terminal_artifact_raw_leaf_card_default_policy"]
    )
    manifest["terminal_artifact_raw_leaf_card_default_policy"] = terminal_artifact_raw_leaf_card_default_policy
    manifest["terminal_artifact_raw_leaf_card_default_policy_fingerprint"] = (
        terminal_artifact_raw_leaf_card_default_policy["contract_fingerprint"]
    )
    manifest["terminal_artifact_raw_leaf_card_default_policy_contract"] = _snapshot_contract_section(
        terminal_artifact_raw_leaf_card_default_policy
    )
    manifest["terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint"] = (
        manifest["terminal_artifact_raw_leaf_card_default_policy_fingerprint"]
    )
    terminal_artifact_envelope = _snapshot_contract_section(terminal_artifact_contract["terminal_artifact_envelope_contract"])
    manifest["terminal_artifact_envelope"] = terminal_artifact_envelope
    manifest["terminal_artifact_envelope_contract"] = _snapshot_contract_section(terminal_artifact_envelope)
    manifest["terminal_artifact_envelope_fingerprint"] = terminal_artifact_envelope["contract_fingerprint"]
    manifest["terminal_artifact_envelope_contract_fingerprint"] = manifest["terminal_artifact_envelope_fingerprint"]
    terminal_artifact_kind_contracts = _snapshot_contract_section(
        terminal_artifact_contract["terminal_artifact_kind_contracts"]
    )
    manifest["terminal_artifact_kind_contracts"] = _snapshot_contract_section(terminal_artifact_kind_contracts)
    manifest["terminal_artifact_kind_contracts_fingerprint"] = terminal_artifact_contract[
        "terminal_artifact_kind_contracts_fingerprint"
    ]
    manifest["terminal_artifact_rendering_contract"] = _snapshot_contract_section(terminal_artifact_rendering)
    manifest["terminal_artifact_rendering_contract_fingerprint"] = manifest["terminal_artifact_rendering_fingerprint"]
    manifest["terminal_artifact_cli_fallback_contract"] = _snapshot_contract_section(
        terminal_artifact_cli_fallback
    )
    manifest["terminal_artifact_cli_fallback_contract_fingerprint"] = manifest[
        "terminal_artifact_cli_fallback_fingerprint"
    ]
    manifest["terminal_artifact_cli_fallback_target_contract_fingerprints"] = _snapshot_contract_section(
        terminal_artifact_contract["terminal_artifact_cli_fallback_target_contract_fingerprints"]
    )
    manifest["contract_fingerprints"] = _build_a2ui_contract_fingerprint_summary()
    return manifest


def _canonicalize_capabilities(capabilities: A2UICapabilities) -> A2UICapabilities:
    """Snapshot a validated handshake into immutable, canonical fields.

    ``validate_capabilities`` accepts either lists or tuples so callers can
    build the payload naturally, but the session store should retain a stable
    immutable copy once the handshake is negotiated. Supported sequences are
    reordered into the contract's canonical sequence so equivalent handshakes
    collapse to the same stored snapshot.
    """

    return A2UICapabilities(
        a2ui_version=capabilities.a2ui_version,
        client_name=capabilities.client_name.strip(),
        cards_supported=_canonicalize_supported_sequence(
            capabilities.cards_supported,
            canonical_order=_SPECIALIZED_CARD_TYPES,
        ),
        primitive_blocks_supported=_canonicalize_supported_sequence(
            capabilities.primitive_blocks_supported,
            canonical_order=REQUIRED_PRIMITIVE_BLOCKS,
        ),
        actions_supported=_canonicalize_supported_sequence(
            capabilities.actions_supported,
            canonical_order=ALLOWED_ACTION_IDS,
        ),
        max_payload_bytes=capabilities.max_payload_bytes,
        supports_streaming=capabilities.supports_streaming,
    )


def normalize_capabilities(capabilities: A2UICapabilities) -> A2UICapabilities:
    """Return the canonical, immutable snapshot for an A2UI capability handshake."""

    validate_capabilities(capabilities)
    return _canonicalize_capabilities(capabilities)


def describe_a2ui_contract_fingerprints(
    include_terminal_artifact: bool = False,
    include_action: bool = False,
    include_terminal_artifact_render_target: bool = False,
    include_terminal_artifact_rendering: bool = False,
    include_terminal_artifact_cli_fallback: bool = False,
    include_terminal_artifact_cli_fallback_target: bool = False,
    include_terminal_artifact_raw_leaf_card_default: bool = False,
    include_terminal_artifact_raw_leaf_card_default_policy: bool = False,
    include_contract_aliases: bool = False,
) -> dict[str, str]:
    """Return stable fingerprints for the contract sections and embedded contracts.

    The default key set stays lean for existing callers. Opt-in flags expose the
    embedded dispatch fingerprints, including the raw-leaf card-default
    recovery contract and its policy contract, plus contract aliases that the
    full manifest already surfaces so lightweight callers can negotiate the
    same contract slice without pulling the entire manifest.
    """

    manifest = _build_a2ui_contract_manifest()
    fingerprints = {
        "contract": _fingerprint_manifest_section(manifest),
        "capabilities": a2ui_capabilities_contract_fingerprint(),
        "cards": _fingerprint_manifest_section(manifest["cards"]),
        "fallbacks": _fingerprint_manifest_section(manifest["fallbacks"]),
        "selection": selection_contract_fingerprint(),
        "primitive_blocks": _fingerprint_manifest_section(manifest["primitive_blocks"]),
        "actions": _fingerprint_manifest_section(manifest["actions"]),
        "schemas": _fingerprint_manifest_section(manifest["schemas"]),
        "card_contract": card_contract_fingerprint(),
        "terminal_fallback": terminal_fallback_contract_fingerprint(),
    }
    if include_action:
        fingerprints["action"] = action_contract_fingerprint()
    if include_terminal_artifact:
        fingerprints["terminal_artifact"] = manifest["terminal_artifact_fingerprint"]
    if include_terminal_artifact_render_target:
        fingerprints["terminal_artifact_render_target"] = terminal_artifact_render_target_contract_fingerprint()
    if include_terminal_artifact_rendering:
        fingerprints["terminal_artifact_rendering"] = terminal_artifact_rendering_contract_fingerprint()
    if include_terminal_artifact_cli_fallback:
        fingerprints["terminal_artifact_cli_fallback"] = terminal_artifact_cli_fallback_contract_fingerprint()
    if include_terminal_artifact_cli_fallback_target:
        fingerprints["terminal_artifact_cli_fallback_target"] = (
            terminal_artifact_cli_fallback_target_contract_fingerprint()
        )
    if include_terminal_artifact_raw_leaf_card_default:
        fingerprints["terminal_artifact_raw_leaf_card_default"] = (
            terminal_artifact_raw_leaf_card_default_contract_fingerprint()
        )
    if include_terminal_artifact_raw_leaf_card_default_policy:
        fingerprints["terminal_artifact_raw_leaf_card_default_policy"] = (
            terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint()
        )
    if include_contract_aliases:
        fingerprints["capabilities_contract"] = a2ui_capabilities_contract_fingerprint()
        fingerprints["action_contract"] = action_contract_fingerprint()
        fingerprints["selection_contract"] = selection_contract_fingerprint()
        fingerprints["terminal_fallback_contract"] = terminal_fallback_contract_fingerprint()
        fingerprints["terminal_artifact_kind_contracts"] = terminal_artifact_kind_contracts_fingerprint()
        fingerprints["terminal_artifact_contract"] = terminal_artifact_contract_fingerprint()
        fingerprints["terminal_artifact_envelope"] = terminal_artifact_envelope_contract_fingerprint()
        fingerprints["terminal_artifact_envelope_contract"] = terminal_artifact_envelope_contract_fingerprint()
        fingerprints["terminal_artifact_render_target"] = terminal_artifact_render_target_contract_fingerprint()
        fingerprints["terminal_artifact_rendering"] = terminal_artifact_rendering_contract_fingerprint()
        fingerprints["terminal_artifact_cli_fallback"] = terminal_artifact_cli_fallback_contract_fingerprint()
        fingerprints["terminal_artifact_cli_fallback_target"] = (
            terminal_artifact_cli_fallback_target_contract_fingerprint()
        )
        fingerprints["terminal_artifact_cli_fallback_target_fingerprint"] = (
            terminal_artifact_cli_fallback_target_contract_fingerprint()
        )
        fingerprints["terminal_artifact_raw_leaf_card_default"] = (
            terminal_artifact_raw_leaf_card_default_contract_fingerprint()
        )
        fingerprints["terminal_artifact_render_target_contract"] = (
            terminal_artifact_render_target_contract_fingerprint()
        )
        fingerprints["terminal_artifact_rendering_contract"] = terminal_artifact_rendering_contract_fingerprint()
        fingerprints["terminal_artifact_cli_fallback_contract"] = (
            terminal_artifact_cli_fallback_contract_fingerprint()
        )
        fingerprints["terminal_artifact_cli_fallback_target_contract"] = (
            terminal_artifact_cli_fallback_target_contract_fingerprint()
        )
        fingerprints["terminal_artifact_raw_leaf_card_default_contract"] = (
            terminal_artifact_raw_leaf_card_default_contract_fingerprint()
        )
        fingerprints["terminal_artifact_raw_leaf_card_default_policy"] = (
            terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint()
        )
        fingerprints["terminal_artifact_raw_leaf_card_default_policy_contract"] = (
            terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint()
        )
    return fingerprints


def _build_a2ui_contract_fingerprint_summary() -> dict[str, str]:
    return describe_a2ui_contract_fingerprints(
        include_terminal_artifact=True,
        include_action=True,
        include_terminal_artifact_render_target=True,
        include_terminal_artifact_rendering=True,
        include_terminal_artifact_cli_fallback=True,
        include_terminal_artifact_cli_fallback_target=True,
    )


def describe_selection_contract() -> dict[str, Any]:
    """Return the stable, versioned SelectionRef contract manifest."""

    manifest = _build_selection_contract_manifest()
    fingerprint = selection_contract_fingerprint()
    manifest["selection_fingerprint"] = fingerprint
    manifest["selection_contract_fingerprint"] = fingerprint
    manifest["contract_fingerprint"] = fingerprint
    return manifest


def describe_action_contract() -> dict[str, Any]:
    """Return the stable, versioned ActionRef contract manifest."""

    manifest = _build_action_contract_manifest()
    fingerprint = action_contract_fingerprint()
    manifest["action_fingerprint"] = fingerprint
    manifest["action_contract_fingerprint"] = fingerprint
    manifest["contract_fingerprint"] = fingerprint
    return manifest


def describe_card_contract() -> dict[str, Any]:
    """Return the stable, versioned card contract manifest."""

    manifest = _build_card_contract_manifest()
    fingerprint = card_contract_fingerprint()
    manifest["card_fingerprint"] = fingerprint
    manifest["card_contract_fingerprint"] = fingerprint
    manifest["contract_fingerprint"] = fingerprint
    return manifest


def describe_a2ui_capabilities_contract() -> dict[str, Any]:
    """Return the stable, versioned A2UI capabilities handshake manifest."""

    manifest = _build_a2ui_capabilities_contract_manifest()
    fingerprint = a2ui_capabilities_contract_fingerprint()
    manifest["capabilities_fingerprint"] = fingerprint
    manifest["contract_fingerprint"] = fingerprint
    return manifest


def describe_terminal_fallback_contract() -> dict[str, Any]:
    """Return the stable terminal fallback contract manifest."""

    manifest = _build_terminal_fallback_contract_manifest()
    fingerprint = terminal_fallback_contract_fingerprint()
    manifest["terminal_fallback_fingerprint"] = fingerprint
    manifest["terminal_fallback_contract_fingerprint"] = fingerprint
    manifest["contract_fingerprint"] = fingerprint
    return manifest


def describe_terminal_artifact_raw_leaf_card_default_contract() -> dict[str, Any]:
    """Return the stable raw-leaf card default contract manifest."""

    manifest = _build_terminal_artifact_raw_leaf_card_default_contract_manifest()
    fingerprint = terminal_artifact_raw_leaf_card_default_contract_fingerprint()
    manifest["raw_leaf_card_default_fingerprint"] = fingerprint
    manifest["raw_leaf_card_default_contract_fingerprint"] = fingerprint
    manifest["contract_fingerprint"] = fingerprint
    manifest["raw_leaf_card_default_contract_fingerprints"] = describe_terminal_artifact_raw_leaf_card_default_contract_fingerprints()
    return manifest


def describe_terminal_artifact_raw_leaf_card_default_policy_contract_fingerprints(
    include_terminal_artifact_raw_leaf_card_default_policy: bool = False,
) -> dict[str, str]:
    """Return stable fingerprints for the raw-leaf card-default policy contract section."""

    return _build_terminal_artifact_raw_leaf_card_default_policy_contract_fingerprints(
        include_terminal_artifact_raw_leaf_card_default_policy=include_terminal_artifact_raw_leaf_card_default_policy,
    )


def describe_terminal_artifact_raw_leaf_card_default_policy_contract() -> dict[str, Any]:
    """Return the stable raw-leaf card default policy contract manifest."""

    manifest = _build_terminal_artifact_raw_leaf_card_default_policy_contract_manifest()
    fingerprint = terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint()
    manifest["raw_leaf_card_default_policy_fingerprint"] = fingerprint
    manifest["raw_leaf_card_default_policy_contract_fingerprint"] = fingerprint
    manifest["contract_fingerprint"] = fingerprint
    manifest["raw_leaf_card_default_policy_contract_fingerprints"] = (
        describe_terminal_artifact_raw_leaf_card_default_policy_contract_fingerprints()
    )
    return manifest


def describe_terminal_artifact_envelope_contract() -> dict[str, Any]:
    """Return the stable TerminalArtifact envelope contract manifest."""

    manifest = _build_terminal_artifact_envelope_manifest()
    fingerprint = terminal_artifact_envelope_contract_fingerprint()
    manifest["terminal_artifact_envelope_fingerprint"] = fingerprint
    manifest["terminal_artifact_envelope_contract_fingerprint"] = fingerprint
    manifest["contract_fingerprint"] = fingerprint
    return manifest


def describe_terminal_artifact_raw_leaf_card_default_contract_fingerprints(
    include_terminal_artifact_raw_leaf_card_default: bool = False,
) -> dict[str, str]:
    """Return stable fingerprints for the raw-leaf card-default contract section."""

    return _build_terminal_artifact_raw_leaf_card_default_contract_fingerprints(
        include_terminal_artifact_raw_leaf_card_default=include_terminal_artifact_raw_leaf_card_default,
    )


def describe_terminal_artifact_contract() -> dict[str, Any]:
    """Return the stable terminal artifact dispatch contract manifest."""

    manifest = _build_terminal_artifact_contract_manifest()
    fingerprint = terminal_artifact_contract_fingerprint()
    manifest["terminal_artifact_fingerprint"] = fingerprint
    manifest["terminal_artifact_contract_fingerprint"] = fingerprint
    manifest["contract_fingerprint"] = fingerprint
    manifest["terminal_artifact_render_target"] = _snapshot_contract_section(
        manifest["render_target_contract"]
    )
    manifest["terminal_artifact_render_target_fingerprint"] = terminal_artifact_render_target_contract_fingerprint()
    manifest["raw_leaf_card_default_contract_fingerprint"] = manifest["raw_leaf_card_default_contract"][
        "contract_fingerprint"
    ]
    terminal_artifact_raw_leaf_card_default_policy = _snapshot_contract_section(
        manifest["terminal_artifact_raw_leaf_card_default_policy_contract"]
    )
    manifest["terminal_artifact_raw_leaf_card_default_policy"] = terminal_artifact_raw_leaf_card_default_policy
    manifest["terminal_artifact_raw_leaf_card_default_policy_fingerprint"] = (
        terminal_artifact_raw_leaf_card_default_policy["contract_fingerprint"]
    )
    terminal_artifact_envelope = _snapshot_contract_section(manifest["envelope"])
    manifest["terminal_artifact_envelope"] = terminal_artifact_envelope
    manifest["terminal_artifact_envelope_contract"] = _snapshot_contract_section(terminal_artifact_envelope)
    manifest["terminal_artifact_envelope_fingerprint"] = terminal_artifact_envelope["contract_fingerprint"]
    manifest["terminal_artifact_envelope_contract_fingerprint"] = manifest["terminal_artifact_envelope_fingerprint"]
    manifest["terminal_artifact_kind_contracts"] = _snapshot_contract_section(manifest["kind_contracts"])
    manifest["terminal_artifact_kind_contracts_fingerprint"] = terminal_artifact_kind_contracts_fingerprint()
    return manifest


def describe_terminal_artifact_render_target_contract() -> dict[str, Any]:
    """Return the stable terminal artifact render-target contract manifest."""

    manifest = _build_terminal_artifact_render_target_contract_manifest()
    fingerprint = terminal_artifact_render_target_contract_fingerprint()
    manifest["terminal_artifact_render_target_fingerprint"] = fingerprint
    manifest["terminal_artifact_render_target_contract_fingerprint"] = fingerprint
    manifest["contract_fingerprint"] = fingerprint
    manifest["raw_leaf_card_default_contract_fingerprint"] = manifest["raw_leaf_card_default_contract"][
        "contract_fingerprint"
    ]
    manifest["raw_leaf_card_default_policy_contract_fingerprint"] = manifest["raw_leaf_card_default_policy_contract"][
        "contract_fingerprint"
    ]
    manifest["terminal_artifact_raw_leaf_card_default_policy_fingerprint"] = manifest[
        "raw_leaf_card_default_policy_contract_fingerprint"
    ]
    manifest["terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint"] = manifest[
        "raw_leaf_card_default_policy_contract_fingerprint"
    ]
    return manifest


def describe_terminal_artifact_render_target_contract_fingerprints(
    include_terminal_artifact_render_target: bool = False,
    include_contract_aliases: bool = False,
) -> dict[str, str]:
    """Return stable fingerprints for the render-target contract sections.

    Pass ``include_terminal_artifact_render_target=True`` to include the
    wrapper contract fingerprint itself alongside the nested section
    fingerprints. Pass ``include_contract_aliases=True`` to include alias keys
    that mirror the manifest field names.
    """

    fingerprints = _build_terminal_artifact_render_target_contract_fingerprints(
        include_terminal_artifact_render_target=include_terminal_artifact_render_target,
    )
    if include_contract_aliases:
        fingerprints["terminal_artifact_kind_contracts"] = terminal_artifact_kind_contracts_fingerprint()
        fingerprints["terminal_artifact_render_target"] = terminal_artifact_render_target_contract_fingerprint()
        fingerprints["terminal_artifact_render_target_contract"] = (
            terminal_artifact_render_target_contract_fingerprint()
        )
        fingerprints["terminal_artifact_raw_leaf_card_default"] = (
            terminal_artifact_raw_leaf_card_default_contract_fingerprint()
        )
        fingerprints["terminal_artifact_raw_leaf_card_default_contract"] = (
            terminal_artifact_raw_leaf_card_default_contract_fingerprint()
        )
        fingerprints["terminal_artifact_raw_leaf_card_default_policy"] = (
            terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint()
        )
        fingerprints["terminal_artifact_raw_leaf_card_default_policy_contract"] = (
            terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint()
        )
    return fingerprints


def describe_terminal_artifact_kind_resolution_contract() -> dict[str, Any]:
    """Return the stable terminal-artifact kind-resolution contract section."""

    manifest = _build_terminal_artifact_kind_resolution_manifest()
    fingerprint = terminal_artifact_kind_resolution_fingerprint()
    manifest["kind_resolution_fingerprint"] = fingerprint
    manifest["kind_resolution_contract_fingerprint"] = fingerprint
    manifest["contract_fingerprint"] = fingerprint
    return manifest


def describe_terminal_artifact_fallback_recovery_contract() -> dict[str, Any]:
    """Return the stable terminal-artifact fallback-recovery contract section."""

    manifest = _build_terminal_artifact_fallback_recovery_manifest()
    fingerprint = terminal_artifact_fallback_recovery_fingerprint()
    manifest["fallback_recovery_fingerprint"] = fingerprint
    manifest["fallback_recovery_contract_fingerprint"] = fingerprint
    manifest["contract_fingerprint"] = fingerprint
    return manifest


def describe_terminal_artifact_rendering_contract() -> dict[str, Any]:
    """Return the stable terminal artifact rendering contract manifest."""

    manifest = _build_terminal_artifact_rendering_contract_manifest()
    fingerprint = terminal_artifact_rendering_contract_fingerprint()
    manifest["terminal_artifact_rendering_fingerprint"] = fingerprint
    manifest["terminal_artifact_rendering_contract_fingerprint"] = fingerprint
    manifest["contract_fingerprint"] = fingerprint
    manifest["terminal_artifact_render_target"] = manifest["render_target_contract"]
    manifest["terminal_artifact_render_target_fingerprint"] = terminal_artifact_render_target_contract_fingerprint()
    manifest["raw_leaf_card_default_contract_fingerprint"] = manifest["raw_leaf_card_default_contract"][
        "contract_fingerprint"
    ]
    manifest["raw_leaf_card_default_policy_contract_fingerprint"] = manifest["raw_leaf_card_default_policy_contract"][
        "contract_fingerprint"
    ]
    manifest["terminal_artifact_raw_leaf_card_default_policy_fingerprint"] = manifest[
        "raw_leaf_card_default_policy_contract_fingerprint"
    ]
    manifest["terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint"] = manifest[
        "raw_leaf_card_default_policy_contract_fingerprint"
    ]
    return manifest


def describe_terminal_artifact_rendering_contract_fingerprints(
    include_terminal_artifact_rendering: bool = False,
    include_contract_aliases: bool = False,
) -> dict[str, str]:
    """Return stable fingerprints for the rendering-contract sections.

    Pass ``include_terminal_artifact_rendering=True`` to include the wrapper
    contract fingerprint itself alongside the nested section fingerprints.
    Pass ``include_contract_aliases=True`` to include alias keys that mirror
    the manifest field names.
    """

    fingerprints = _build_terminal_artifact_rendering_contract_fingerprints(
        include_terminal_artifact_rendering=include_terminal_artifact_rendering,
    )
    if include_contract_aliases:
        fingerprints["terminal_artifact_kind_contracts"] = terminal_artifact_kind_contracts_fingerprint()
        fingerprints["terminal_artifact_rendering"] = terminal_artifact_rendering_contract_fingerprint()
        fingerprints["terminal_artifact_render_target_contract"] = (
            terminal_artifact_render_target_contract_fingerprint()
        )
        fingerprints["terminal_artifact_render_target"] = terminal_artifact_render_target_contract_fingerprint()
        fingerprints["terminal_artifact_rendering_contract"] = terminal_artifact_rendering_contract_fingerprint()
        fingerprints["terminal_artifact_raw_leaf_card_default"] = (
            terminal_artifact_raw_leaf_card_default_contract_fingerprint()
        )
        fingerprints["terminal_artifact_raw_leaf_card_default_contract"] = (
            terminal_artifact_raw_leaf_card_default_contract_fingerprint()
        )
        fingerprints["terminal_artifact_raw_leaf_card_default_policy"] = (
            terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint()
        )
        fingerprints["terminal_artifact_raw_leaf_card_default_policy_contract"] = (
            terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint()
        )
    return fingerprints


def describe_terminal_artifact_cli_fallback_contract() -> dict[str, Any]:
    """Return the stable CLI fallback wrapper contract manifest."""

    manifest = _build_terminal_artifact_cli_fallback_contract_manifest()
    fingerprint = terminal_artifact_cli_fallback_contract_fingerprint()
    manifest["terminal_artifact_cli_fallback_fingerprint"] = fingerprint
    manifest["terminal_artifact_cli_fallback_contract_fingerprint"] = fingerprint
    manifest["contract_fingerprint"] = fingerprint
    manifest["terminal_artifact_render_target"] = manifest["render_target_contract"]
    manifest["terminal_artifact_render_target_fingerprint"] = terminal_artifact_render_target_contract_fingerprint()
    manifest["raw_leaf_card_default_contract_fingerprint"] = manifest["raw_leaf_card_default_contract"][
        "contract_fingerprint"
    ]
    return manifest


def describe_terminal_artifact_cli_fallback_target_contract() -> dict[str, Any]:
    """Return the stable CLI fallback target-selection contract manifest."""

    manifest = _build_terminal_artifact_cli_fallback_target_contract_manifest()
    fingerprint = terminal_artifact_cli_fallback_target_contract_fingerprint()
    manifest["terminal_artifact_cli_fallback_target_fingerprint"] = fingerprint
    manifest["terminal_artifact_cli_fallback_target_contract_fingerprint"] = fingerprint
    manifest["contract_fingerprint"] = fingerprint
    manifest["contract_fingerprints"] = describe_terminal_artifact_cli_fallback_target_contract_fingerprints()
    return manifest


def describe_terminal_artifact_cli_fallback_target_contract_fingerprints(
    include_terminal_artifact_cli_fallback_target: bool = False,
    include_contract_aliases: bool = False,
) -> dict[str, str]:
    """Return stable fingerprints for the CLI fallback target-selection contract.

    The default key set stays focused on the shared render-target and raw-leaf
    recovery contracts. Opt in to include the wrapper contract fingerprint or
    alias keys when a caller needs the full negotiated contract slice.
    """

    fingerprints = _build_terminal_artifact_cli_fallback_target_contract_fingerprints(
        include_terminal_artifact_cli_fallback_target=include_terminal_artifact_cli_fallback_target,
    )
    if include_contract_aliases:
        fingerprints["terminal_artifact_render_target"] = terminal_artifact_render_target_contract_fingerprint()
        fingerprints["terminal_artifact_render_target_contract"] = (
            terminal_artifact_render_target_contract_fingerprint()
        )
        fingerprints["terminal_artifact_cli_fallback_target"] = (
            terminal_artifact_cli_fallback_target_contract_fingerprint()
        )
        fingerprints["terminal_artifact_cli_fallback_target_contract"] = (
            terminal_artifact_cli_fallback_target_contract_fingerprint()
        )
        fingerprints["terminal_artifact_cli_fallback_target_fingerprint"] = (
            terminal_artifact_cli_fallback_target_contract_fingerprint()
        )
        fingerprints["terminal_artifact_raw_leaf_card_default"] = (
            terminal_artifact_raw_leaf_card_default_contract_fingerprint()
        )
        fingerprints["terminal_artifact_raw_leaf_card_default_contract"] = (
            terminal_artifact_raw_leaf_card_default_contract_fingerprint()
        )
        fingerprints["terminal_artifact_raw_leaf_card_default_policy"] = (
            terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint()
        )
        fingerprints["terminal_artifact_raw_leaf_card_default_policy_contract"] = (
            terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint()
        )
    return fingerprints


def describe_terminal_artifact_kind_contracts() -> dict[str, dict[str, str]]:
    """Return the stable kind contract map shared by terminal artifact manifests."""

    return _build_terminal_artifact_kind_contracts()


def describe_terminal_artifact_contract_fingerprints(
    include_terminal_artifact: bool = False,
    include_kind_contracts: bool = False,
    include_contract_aliases: bool = False,
) -> dict[str, str]:
    """Return stable fingerprints for the terminal artifact contract and subcontracts.

    Pass ``include_contract_aliases=True`` to include alias keys that mirror
    the manifest field names.
    """

    fingerprints = {
        "card_contract": card_contract_fingerprint(),
        "action_contract": action_contract_fingerprint(),
        "selection_contract": selection_contract_fingerprint(),
        "render_target_contract": terminal_artifact_render_target_contract_fingerprint(),
        "terminal_fallback_contract": terminal_fallback_contract_fingerprint(),
        "rendering_contract": terminal_artifact_rendering_contract_fingerprint(),
        "cli_fallback_contract": terminal_artifact_cli_fallback_contract_fingerprint(),
        "raw_leaf_card_default_contract": terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
    }
    if include_terminal_artifact:
        fingerprints["terminal_artifact"] = terminal_artifact_contract_fingerprint()
    if include_kind_contracts:
        fingerprints["kind_contracts"] = terminal_artifact_kind_contracts_fingerprint()
    if include_contract_aliases:
        fingerprints["terminal_artifact_kind_contracts"] = terminal_artifact_kind_contracts_fingerprint()
        fingerprints["terminal_artifact_contract"] = terminal_artifact_contract_fingerprint()
        fingerprints["terminal_artifact_envelope"] = terminal_artifact_envelope_contract_fingerprint()
        fingerprints["terminal_artifact_envelope_contract"] = terminal_artifact_envelope_contract_fingerprint()
        fingerprints["terminal_artifact_render_target"] = terminal_artifact_render_target_contract_fingerprint()
        fingerprints["terminal_artifact_render_target_contract"] = (
            terminal_artifact_render_target_contract_fingerprint()
        )
        fingerprints["terminal_artifact_rendering"] = terminal_artifact_rendering_contract_fingerprint()
        fingerprints["terminal_artifact_rendering_contract"] = terminal_artifact_rendering_contract_fingerprint()
        fingerprints["terminal_artifact_cli_fallback"] = terminal_artifact_cli_fallback_contract_fingerprint()
        fingerprints["terminal_artifact_cli_fallback_contract"] = (
            terminal_artifact_cli_fallback_contract_fingerprint()
        )
        fingerprints["terminal_artifact_cli_fallback_target"] = (
            terminal_artifact_cli_fallback_target_contract_fingerprint()
        )
        fingerprints["terminal_artifact_cli_fallback_target_contract"] = (
            terminal_artifact_cli_fallback_target_contract_fingerprint()
        )
        fingerprints["terminal_artifact_cli_fallback_target_fingerprint"] = (
            terminal_artifact_cli_fallback_target_contract_fingerprint()
        )
        fingerprints["terminal_artifact_raw_leaf_card_default"] = (
            terminal_artifact_raw_leaf_card_default_contract_fingerprint()
        )
        fingerprints["terminal_artifact_raw_leaf_card_default_contract"] = (
            terminal_artifact_raw_leaf_card_default_contract_fingerprint()
        )
        fingerprints["terminal_artifact_raw_leaf_card_default_policy"] = (
            terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint()
        )
        fingerprints["terminal_artifact_raw_leaf_card_default_policy_contract"] = (
            terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint()
        )
    return fingerprints


def describe_terminal_artifact_cli_fallback_contract_fingerprints(
    include_terminal_artifact_cli_fallback: bool = False,
    include_contract_aliases: bool = False,
) -> dict[str, str]:
    """Return stable fingerprints for the CLI fallback wrapper contract sections.

    Pass ``include_terminal_artifact_cli_fallback=True`` to include the wrapper
    contract fingerprint itself alongside the nested section fingerprints.
    Pass ``include_contract_aliases=True`` to include alias keys that mirror
    the manifest field names.
    """

    fingerprints = _build_terminal_artifact_cli_fallback_contract_fingerprints(
        include_terminal_artifact_cli_fallback=include_terminal_artifact_cli_fallback,
    )
    if include_contract_aliases:
        fingerprints["terminal_artifact_kind_contracts"] = terminal_artifact_kind_contracts_fingerprint()
        fingerprints["terminal_artifact_cli_fallback"] = terminal_artifact_cli_fallback_contract_fingerprint()
        fingerprints["terminal_artifact_rendering"] = terminal_artifact_rendering_contract_fingerprint()
        fingerprints["terminal_artifact_render_target_contract"] = (
            terminal_artifact_render_target_contract_fingerprint()
        )
        fingerprints["terminal_artifact_render_target"] = terminal_artifact_render_target_contract_fingerprint()
        fingerprints["terminal_artifact_rendering_contract"] = terminal_artifact_rendering_contract_fingerprint()
        fingerprints["terminal_artifact_cli_fallback_contract"] = (
            terminal_artifact_cli_fallback_contract_fingerprint()
        )
        fingerprints["terminal_artifact_cli_fallback_target"] = (
            terminal_artifact_cli_fallback_target_contract_fingerprint()
        )
        fingerprints["terminal_artifact_cli_fallback_target_contract"] = (
            terminal_artifact_cli_fallback_target_contract_fingerprint()
        )
        fingerprints["terminal_artifact_cli_fallback_target_fingerprint"] = (
            terminal_artifact_cli_fallback_target_contract_fingerprint()
        )
        fingerprints["terminal_artifact_raw_leaf_card_default"] = (
            terminal_artifact_raw_leaf_card_default_contract_fingerprint()
        )
        fingerprints["terminal_artifact_raw_leaf_card_default_contract"] = (
            terminal_artifact_raw_leaf_card_default_contract_fingerprint()
        )
        fingerprints["terminal_artifact_raw_leaf_card_default_policy"] = (
            terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint()
        )
        fingerprints["terminal_artifact_raw_leaf_card_default_policy_contract"] = (
            terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint()
        )
    return fingerprints


def _build_terminal_artifact_rendering_contract_fingerprints(
    *,
    include_terminal_artifact_rendering: bool = False,
) -> dict[str, str]:
    fingerprints = {
        "kind_contracts": terminal_artifact_kind_contracts_fingerprint(),
        "render_target_contract": terminal_artifact_render_target_contract_fingerprint(),
        "terminal_fallback_contract": terminal_fallback_contract_fingerprint(),
        "raw_leaf_card_default_contract": terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        "raw_leaf_card_default_policy_contract": terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
    }
    if include_terminal_artifact_rendering:
        fingerprints["terminal_artifact_rendering"] = terminal_artifact_rendering_contract_fingerprint()
    return fingerprints


def _build_terminal_artifact_cli_fallback_contract_fingerprints(
    *,
    include_terminal_artifact_cli_fallback: bool = False,
) -> dict[str, str]:
    fingerprints = {
        "kind_contracts": terminal_artifact_kind_contracts_fingerprint(),
        "render_target_contract": terminal_artifact_render_target_contract_fingerprint(),
        "rendering_contract": terminal_artifact_rendering_contract_fingerprint(),
        "terminal_fallback_contract": terminal_fallback_contract_fingerprint(),
        "raw_leaf_card_default_contract": terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        "raw_leaf_card_default_policy_contract": terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
    }
    if include_terminal_artifact_cli_fallback:
        fingerprints["terminal_artifact_cli_fallback"] = terminal_artifact_cli_fallback_contract_fingerprint()
    return fingerprints


def _build_terminal_artifact_cli_fallback_target_contract_fingerprints(
    *,
    include_terminal_artifact_cli_fallback_target: bool = False,
) -> dict[str, str]:
    fingerprints = {
        "render_target_contract": terminal_artifact_render_target_contract_fingerprint(),
        "terminal_fallback_contract": terminal_fallback_contract_fingerprint(),
        "raw_leaf_card_default_contract": terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        "raw_leaf_card_default_policy_contract": terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
        "kind_resolution": terminal_artifact_kind_resolution_fingerprint(),
        "fallback_recovery": terminal_artifact_fallback_recovery_fingerprint(),
    }
    if include_terminal_artifact_cli_fallback_target:
        fingerprints["terminal_artifact_cli_fallback_target"] = (
            terminal_artifact_cli_fallback_target_contract_fingerprint()
        )
    return fingerprints


def _build_terminal_artifact_raw_leaf_card_default_policy_contract_fingerprints(
    *,
    include_terminal_artifact_raw_leaf_card_default_policy: bool = False,
) -> dict[str, str]:
    fingerprint = terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint()
    fingerprints = {
        "raw_leaf_card_default_policy_contract": fingerprint,
    }
    if include_terminal_artifact_raw_leaf_card_default_policy:
        fingerprints["terminal_artifact_raw_leaf_card_default_policy_contract"] = fingerprint
    return fingerprints


def _build_terminal_artifact_raw_leaf_card_default_contract_fingerprints(
    *,
    include_terminal_artifact_raw_leaf_card_default: bool = False,
) -> dict[str, str]:
    fingerprint = terminal_artifact_raw_leaf_card_default_contract_fingerprint()
    fingerprints = {
        "raw_leaf_card_default_contract": fingerprint,
    }
    if include_terminal_artifact_raw_leaf_card_default:
        fingerprints["terminal_artifact_raw_leaf_card_default_contract"] = fingerprint
    return fingerprints


def build_terminal_artifact_envelope(artifact: Any, *, kind: str) -> dict[str, Any]:
    """Build a canonical ``TerminalArtifact`` envelope for structured CLI payloads.

    The envelope keeps the kind explicit so engine callers can emit stable
    artifacts now and future UI clients can consume the same payload shape
    later without guessing. The helper rejects mismatched kind/payload pairs
    so the engine cannot accidentally label an action as a card or vice versa.
    TerminalArtifact payloads are normalized to plain dictionary snapshots so
    the contract stays predictable even when callers pass dataclass instances.
    """

    normalized_kind = _normalize_terminal_artifact_kind(artifact, kind=kind)
    artifact_snapshot = normalize_terminal_artifact_payload(artifact, kind=normalized_kind)
    envelope = {
        "type": _TERMINAL_ARTIFACT_ENVELOPE_TYPE,
        "kind": normalized_kind,
        "artifact": artifact_snapshot,
        "contract_version": A2UI_CONTRACT_VERSION,
        "a2ui_version": A2UI_VERSION,
    }
    validate_terminal_artifact_envelope(envelope)
    return envelope


def normalize_terminal_artifact_payload(artifact: Any, *, kind: str | None = None) -> dict[str, Any]:
    """Return the canonical payload snapshot for a structured terminal artifact.

    Action and selection payloads are normalized through the public ref
    validators before being converted to plain dictionaries. Canonical
    ``ActionRef`` and ``SelectionRef`` mappings may include a ``type`` hint
    when they arrive from the renderer path, and that hint is stripped before
    validation so the stored envelope stays on the canonical leaf shape. Card
    payloads are copied as mappings or dataclass snapshots so the envelope does
    not retain references to mutable source objects. Unordered set-like values
    are converted to sorted lists so the snapshot stays deterministic and
    JSON-safe.
    """

    normalized_kind = _normalize_terminal_artifact_kind(artifact, kind=kind)
    if normalized_kind == "action":
        if isinstance(artifact, Mapping):
            artifact = _strip_terminal_type_hint(artifact, expected_type="ActionRef")
        return _action_ref_to_dict(normalize_action_ref(artifact))
    if normalized_kind == "selection":
        if isinstance(artifact, Mapping):
            artifact = _strip_terminal_type_hint(artifact, expected_type="SelectionRef")
        return _selection_ref_to_dict(normalize_selection_ref(artifact))
    _validate_terminal_artifact_card_payload(artifact)
    card_snapshot = _coerce_terminal_card(artifact)
    if card_snapshot is None:
        raise ValueError("TerminalArtifact card artifact must be a mapping or card-like object")
    if _should_preserve_raw_leaf_card_default(card_snapshot):
        return _copy_terminal_artifact_payload(card_snapshot)
    card_snapshot = _canonicalize_card_top_level_fields(card_snapshot)
    return _copy_terminal_artifact_payload(card_snapshot)


def validate_terminal_artifact_envelope(envelope: Any) -> None:
    if not isinstance(envelope, Mapping):
        raise ValueError("TerminalArtifact must be an object")
    extra_keys = set(envelope) - {
        "type",
        "kind",
        "artifact",
        "contract_version",
        "a2ui_version",
    }
    if extra_keys:
        extras = ", ".join(sorted(extra_keys))
        raise ValueError(f"Unexpected TerminalArtifact field(s): {extras}")
    artifact_type = envelope.get("type")
    if not isinstance(artifact_type, str) or artifact_type.strip() != _TERMINAL_ARTIFACT_ENVELOPE_TYPE:
        raise ValueError("TerminalArtifact type must be TerminalArtifact")
    if "kind" not in envelope:
        raise ValueError("TerminalArtifact kind is required")
    kind = envelope.get("kind")
    if not isinstance(kind, str):
        raise ValueError("TerminalArtifact kind must be a string")
    normalized_kind = kind.strip().lower()
    if normalized_kind not in _TERMINAL_ARTIFACT_SUPPORTED_KIND_SET:
        raise ValueError("TerminalArtifact kind must be one of: card, action, selection")
    if "artifact" not in envelope:
        raise ValueError("TerminalArtifact artifact is required")
    if envelope.get("artifact") is None:
        raise ValueError("TerminalArtifact artifact is required")
    contract_version = envelope.get("contract_version")
    if contract_version is not None and (
        type(contract_version) is not int or contract_version != A2UI_CONTRACT_VERSION
    ):
        raise ValueError("TerminalArtifact contract_version is invalid")
    a2ui_version = envelope.get("a2ui_version")
    if a2ui_version is not None and type(a2ui_version) is not int:
        raise ValueError("TerminalArtifact a2ui_version is invalid")
    if a2ui_version is not None and a2ui_version != A2UI_VERSION:
        raise ValueError("TerminalArtifact a2ui_version is invalid")
    _validate_terminal_artifact_payload_kind(envelope["artifact"], normalized_kind)


def _build_a2ui_contract_manifest() -> dict[str, Any]:
    return {
        "contract_version": A2UI_CONTRACT_VERSION,
        "a2ui_version": A2UI_VERSION,
        "capabilities": describe_a2ui_capabilities_contract(),
        "card_contract": describe_card_contract(),
        "terminal_fallback": describe_terminal_fallback_contract(),
        "terminal_artifact": describe_terminal_artifact_contract(),
        "terminal_fallback_fingerprint": terminal_fallback_contract_fingerprint(),
        "terminal_artifact_fingerprint": terminal_artifact_contract_fingerprint(),
        "cards": {
            "generic": GENERIC_CARD_TYPE,
            "unknown": UNKNOWN_CARD_TYPE,
            "reserved": list(_RESERVED_CARD_TYPES),
            "specialized": list(_SPECIALIZED_CARD_TYPES),
        },
        "selection": describe_selection_contract(),
        "action": describe_action_contract(),
        "terminal_artifact_envelope": describe_terminal_artifact_envelope_contract(),
        "fallbacks": _build_card_fallback_manifest(),
        "schemas": _build_a2ui_schema_manifest(),
        "primitive_blocks": [
            {
                "type": block_type,
                "fields": list(_PRIMITIVE_BLOCK_SCHEMAS[block_type]),
            }
            for block_type in REQUIRED_PRIMITIVE_BLOCKS
        ],
        "actions": [
            {
                "id": action_id,
                "version": A2UI_ACTION_SCHEMA_VERSION,
                "payload_fields": sorted(schema),
            }
            for action_id, schema in sorted(_ACTION_SCHEMAS.items())
        ],
    }


def _build_a2ui_capabilities_contract_manifest() -> dict[str, Any]:
    return {
        "contract_version": A2UI_CONTRACT_VERSION,
        "a2ui_version": A2UI_VERSION,
        "capabilities_schema_version": A2UI_CAPABILITIES_SCHEMA_VERSION,
        "capabilities_version": A2UI_CAPABILITIES_SCHEMA_VERSION,
        "type": "A2UICapabilities",
        "message_type": "A2UI_CAPABILITIES",
        "session_scope": "per-session",
        "required_fields": list(_CAPABILITIES_REQUIRED_FIELDS),
        "optional_fields": [],
        "field_contracts": _build_a2ui_capabilities_field_contracts(),
    }


def _validate_terminal_artifact_payload_kind(artifact: Any, kind: str) -> None:
    if kind == "card":
        card_artifact = _coerce_terminal_card(artifact)
        if card_artifact is None:
            raise ValueError("TerminalArtifact card artifact must be a mapping or card-like object")
        card_type = _normalize_card_type(card_artifact)
        if card_type in {_TERMINAL_ARTIFACT_ENVELOPE_TYPE, "ActionRef", "SelectionRef"}:
            raise ValueError("TerminalArtifact card artifact must be a typed card")
        if card_type == "<missing>" and not _should_preserve_raw_leaf_card_default(card_artifact):
            raise ValueError("TerminalArtifact card artifact must be a typed card")
        if _infer_terminal_artifact_kind_from_mapping(card_artifact) in {"action", "selection"}:
            raise ValueError("TerminalArtifact card artifact must not use action or selection payload shape")
        return
    if kind == "action":
        try:
            if isinstance(artifact, Mapping):
                artifact = _strip_terminal_type_hint(artifact, expected_type="ActionRef")
            normalize_action_ref(artifact)
        except ValueError as exc:
            raise ValueError("TerminalArtifact action artifact is invalid") from exc
        return
    if kind == "selection":
        try:
            if isinstance(artifact, Mapping):
                artifact = _strip_terminal_type_hint(artifact, expected_type="SelectionRef")
            normalize_selection_ref(artifact)
        except ValueError as exc:
            raise ValueError("TerminalArtifact selection artifact is invalid") from exc
        return
    raise ValueError("TerminalArtifact kind must be one of: card, action, selection")


def _validate_terminal_artifact_card_payload(artifact: Any) -> None:
    inferred_kind = _normalize_terminal_artifact_kind(artifact, kind=None)
    if inferred_kind in {"action", "selection"}:
        raise ValueError("TerminalArtifact card artifact must not use action or selection payload shape")


def _build_selection_contract_manifest() -> dict[str, Any]:
    return {
        "contract_version": A2UI_CONTRACT_VERSION,
        "a2ui_version": A2UI_VERSION,
        "selection_schema_version": SELECTION_SCHEMA_VERSION,
        "selection_version": SELECTION_SCHEMA_VERSION,
        "type": "SelectionRef",
        "required_fields": ["id", "label", "payload"],
        "optional_fields": ["selected", "disabled"],
        "normalization": {
            "id": "trimmed non-empty string",
            "label": "trimmed non-empty string",
            "payload": "object copy",
            "selected": "bool default false",
            "disabled": "bool default false",
        },
    }


def _build_action_contract_manifest() -> dict[str, Any]:
    return {
        "contract_version": A2UI_CONTRACT_VERSION,
        "a2ui_version": A2UI_VERSION,
        "action_schema_version": A2UI_ACTION_SCHEMA_VERSION,
        "action_version": A2UI_ACTION_SCHEMA_VERSION,
        "type": "ActionRef",
        "required_fields": ["id", "label", "payload"],
        "optional_fields": ["confirm", "policy_sensitive"],
        "allowed_actions": sorted(ALLOWED_ACTION_IDS),
        "payload_schemas": _build_action_payload_schema_manifest(),
    }


def _build_card_contract_manifest() -> dict[str, Any]:
    return {
        "contract_version": A2UI_CONTRACT_VERSION,
        "a2ui_version": A2UI_VERSION,
        "card_contract_version": CARD_CONTRACT_VERSION,
        "card_version": CARD_CONTRACT_VERSION,
        "type": "CardContract",
        "card_schemas": _build_card_schema_manifest(),
        "fallbacks": _build_card_fallback_manifest(),
    }


def _build_terminal_fallback_contract_manifest() -> dict[str, Any]:
    return {
        "contract_version": A2UI_CONTRACT_VERSION,
        "a2ui_version": A2UI_VERSION,
        "terminal_fallback_schema_version": TERMINAL_FALLBACK_SCHEMA_VERSION,
        "terminal_fallback_version": TERMINAL_FALLBACK_SCHEMA_VERSION,
        "type": "TerminalFallbackContract",
        "supported_kinds": list(TERMINAL_ARTIFACT_SUPPORTED_KINDS),
        "default_kind": TERMINAL_ARTIFACT_DEFAULT_KIND,
        "read_only_action": _build_read_only_fallback_action_manifest()[0],
        "card_fallbacks": _build_card_fallback_manifest(),
    }


def _build_terminal_artifact_contract_manifest(*, include_contract_fingerprints: bool = True) -> dict[str, Any]:
    render_target_contract = describe_terminal_artifact_render_target_contract()
    rendering_contract = describe_terminal_artifact_rendering_contract()
    cli_fallback_contract = describe_terminal_artifact_cli_fallback_contract()
    cli_fallback_target_contract = describe_terminal_artifact_cli_fallback_target_contract()
    raw_leaf_card_default_contract = describe_terminal_artifact_raw_leaf_card_default_contract()
    manifest = {
        "contract_version": A2UI_CONTRACT_VERSION,
        "a2ui_version": A2UI_VERSION,
        "terminal_artifact_schema_version": TERMINAL_ARTIFACT_SCHEMA_VERSION,
        "terminal_artifact_version": TERMINAL_ARTIFACT_SCHEMA_VERSION,
        "type": "TerminalArtifactContract",
        "envelope": describe_terminal_artifact_envelope_contract(),
        "supported_kinds": list(TERMINAL_ARTIFACT_SUPPORTED_KINDS),
        "default_kind": TERMINAL_ARTIFACT_DEFAULT_KIND,
        "render_target_contract": render_target_contract,
        "rendering": rendering_contract,
        "terminal_artifact_rendering": _snapshot_contract_section(rendering_contract),
        "terminal_artifact_render_target_contract": _snapshot_contract_section(render_target_contract),
        "terminal_artifact_rendering_contract": _snapshot_contract_section(rendering_contract),
        "kind_contracts": _build_terminal_artifact_kind_contracts(),
        "raw_leaf_card_default": _build_terminal_artifact_raw_leaf_card_default_manifest(),
        "raw_leaf_card_default_contract": raw_leaf_card_default_contract,
        "terminal_artifact_raw_leaf_card_default_contract": _snapshot_contract_section(
            raw_leaf_card_default_contract
        ),
        "raw_leaf_card_default_contract_fingerprints": describe_terminal_artifact_raw_leaf_card_default_contract_fingerprints(),
        "raw_leaf_card_default_policy": copy.deepcopy(
            cli_fallback_target_contract["raw_leaf_card_default_policy"]
        ),
        "resolver_failure_policy": copy.deepcopy(
            cli_fallback_contract["resolver_failure_policy"]
        ),
        "terminal_artifact_raw_leaf_card_default_policy_contract": _snapshot_contract_section(
            describe_terminal_artifact_raw_leaf_card_default_policy_contract()
        ),
        "terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint": terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
        "terminal_fallback_contract": {
            "kind": "card",
            "contract_fingerprint": terminal_fallback_contract_fingerprint(),
        },
        "terminal_fallback_fingerprint": terminal_fallback_contract_fingerprint(),
        "cli_fallback": cli_fallback_contract,
        "terminal_artifact_cli_fallback": _snapshot_contract_section(cli_fallback_contract),
        "cli_fallback_contract": _snapshot_contract_section(cli_fallback_contract),
        "terminal_artifact_cli_fallback_contract": _snapshot_contract_section(cli_fallback_contract),
        "terminal_artifact_cli_fallback_target": cli_fallback_target_contract,
        "terminal_artifact_cli_fallback_target_contract": _snapshot_contract_section(cli_fallback_target_contract),
        "terminal_artifact_cli_fallback_target_fingerprint": cli_fallback_target_contract["contract_fingerprint"],
        "terminal_artifact_cli_fallback_target_contract_fingerprint": cli_fallback_target_contract[
            "contract_fingerprint"
        ],
        "terminal_artifact_cli_fallback_target_contract_fingerprints": _snapshot_contract_section(
            cli_fallback_target_contract["contract_fingerprints"]
        ),
        "terminal_artifact_render_target_fingerprint": terminal_artifact_render_target_contract_fingerprint(),
        "terminal_artifact_rendering_fingerprint": terminal_artifact_rendering_contract_fingerprint(),
        "raw_leaf_card_default_contract_fingerprint": raw_leaf_card_default_contract["contract_fingerprint"],
        "rendering_contract": {
            "kind": "card",
            "contract_fingerprint": terminal_artifact_rendering_contract_fingerprint(),
        },
        "terminal_artifact_cli_fallback_fingerprint": terminal_artifact_cli_fallback_contract_fingerprint(),
        "terminal_artifact_render_target_contract_fingerprint": terminal_artifact_render_target_contract_fingerprint(),
        "terminal_artifact_rendering_contract_fingerprint": terminal_artifact_rendering_contract_fingerprint(),
        "terminal_fallback_contract_fingerprint": terminal_fallback_contract_fingerprint(),
        "kind_resolution": copy.deepcopy(render_target_contract["kind_resolution"]),
        "kind_resolution_fingerprint": render_target_contract["kind_resolution_fingerprint"],
        "fallback_recovery": copy.deepcopy(render_target_contract["fallback_recovery"]),
        "fallback_recovery_fingerprint": render_target_contract["fallback_recovery_fingerprint"],
    }
    if include_contract_fingerprints:
        manifest["contract_fingerprints"] = describe_terminal_artifact_contract_fingerprints(
            include_terminal_artifact=True
        )
    return manifest


def _build_terminal_artifact_rendering_contract_manifest() -> dict[str, Any]:
    render_target_contract = describe_terminal_artifact_render_target_contract()
    raw_leaf_card_default_contract = describe_terminal_artifact_raw_leaf_card_default_contract()
    kind_contracts = _build_terminal_artifact_kind_contracts()
    terminal_artifact_kind_contracts = _snapshot_contract_section(kind_contracts)
    return {
        "contract_version": A2UI_CONTRACT_VERSION,
        "a2ui_version": A2UI_VERSION,
        "terminal_artifact_schema_version": TERMINAL_ARTIFACT_SCHEMA_VERSION,
        "terminal_artifact_rendering_schema_version": TERMINAL_ARTIFACT_RENDERING_SCHEMA_VERSION,
        "terminal_artifact_rendering_version": TERMINAL_ARTIFACT_RENDERING_SCHEMA_VERSION,
        "type": "TerminalArtifactRenderingContract",
        "supported_kinds": list(TERMINAL_ARTIFACT_SUPPORTED_KINDS),
        "default_kind": TERMINAL_ARTIFACT_DEFAULT_KIND,
        "envelope": describe_terminal_artifact_envelope_contract(),
        "kind_contracts": kind_contracts,
        "terminal_artifact_kind_contracts": terminal_artifact_kind_contracts,
        "render_target_contract": render_target_contract,
        "terminal_artifact_render_target_contract": _snapshot_contract_section(render_target_contract),
        "terminal_artifact_kind_contracts_fingerprint": terminal_artifact_kind_contracts_fingerprint(),
        "renderer_entrypoints": {
            "terminal_artifact": "render_terminal_artifact",
            "card": "render_terminal_card",
            "action": "render_terminal_action",
            "selection": "render_terminal_selection",
            "cli_fallback": "render_terminal_cli_fallback",
        },
        "render_target_resolver": "resolve_terminal_artifact_render_target",
        "fallback_renderer": "ShellUI.render_artifact",
        "raw_leaf_card_default": _build_terminal_artifact_raw_leaf_card_default_manifest(),
        "raw_leaf_card_default_contract": raw_leaf_card_default_contract,
        "terminal_artifact_raw_leaf_card_default_contract": _snapshot_contract_section(
            raw_leaf_card_default_contract
        ),
        "raw_leaf_card_default_contract_fingerprints": describe_terminal_artifact_raw_leaf_card_default_contract_fingerprints(),
        "raw_leaf_card_default_policy": copy.deepcopy(_build_terminal_artifact_raw_leaf_card_default_policy_manifest()),
        "raw_leaf_card_default_policy_contract": describe_terminal_artifact_raw_leaf_card_default_policy_contract(),
        "terminal_artifact_raw_leaf_card_default_policy_contract": _snapshot_contract_section(
            describe_terminal_artifact_raw_leaf_card_default_policy_contract()
        ),
        "raw_leaf_card_default_policy_contract_fingerprints": describe_terminal_artifact_raw_leaf_card_default_policy_contract_fingerprints(),
        "terminal_artifact_raw_leaf_card_default_policy_contract_fingerprints": _snapshot_contract_section(
            describe_terminal_artifact_raw_leaf_card_default_policy_contract_fingerprints(
                include_terminal_artifact_raw_leaf_card_default_policy=True,
            )
        ),
        "terminal_fallback_contract": describe_terminal_fallback_contract(),
        "terminal_fallback_fingerprint": terminal_fallback_contract_fingerprint(),
        "kind_resolution": copy.deepcopy(render_target_contract["kind_resolution"]),
        "kind_resolution_fingerprint": render_target_contract["kind_resolution_fingerprint"],
        "fallback_recovery": copy.deepcopy(render_target_contract["fallback_recovery"]),
        "fallback_recovery_fingerprint": render_target_contract["fallback_recovery_fingerprint"],
        "contract_fingerprints": describe_terminal_artifact_rendering_contract_fingerprints(),
    }


def _build_terminal_artifact_cli_fallback_contract_manifest() -> dict[str, Any]:
    render_target_contract = describe_terminal_artifact_render_target_contract()
    rendering_contract = describe_terminal_artifact_rendering_contract()
    terminal_fallback_contract = describe_terminal_fallback_contract()
    terminal_artifact_cli_fallback_target_contract = describe_terminal_artifact_cli_fallback_target_contract()
    raw_leaf_card_default_contract = describe_terminal_artifact_raw_leaf_card_default_contract()
    raw_leaf_card_default_policy_contract = describe_terminal_artifact_raw_leaf_card_default_policy_contract()
    kind_contracts = _build_terminal_artifact_kind_contracts()
    terminal_artifact_kind_contracts = _snapshot_contract_section(kind_contracts)
    renderer_entrypoints = copy.deepcopy(rendering_contract["renderer_entrypoints"])
    renderer_entrypoints["cli_fallback"] = "render_terminal_cli_fallback"
    return {
        "contract_version": A2UI_CONTRACT_VERSION,
        "a2ui_version": A2UI_VERSION,
        "terminal_artifact_schema_version": TERMINAL_ARTIFACT_SCHEMA_VERSION,
        "terminal_artifact_cli_fallback_schema_version": TERMINAL_ARTIFACT_CLI_FALLBACK_SCHEMA_VERSION,
        "terminal_artifact_cli_fallback_version": TERMINAL_ARTIFACT_CLI_FALLBACK_SCHEMA_VERSION,
        "type": "TerminalArtifactCliFallbackContract",
        "fallback_target_resolver": "resolve_terminal_artifact_cli_fallback_target",
        "render_target_resolver": "resolve_terminal_artifact_render_target",
        "fallback_renderer": "ShellUI.render_artifact",
        "supported_kinds": list(TERMINAL_ARTIFACT_SUPPORTED_KINDS),
        "default_kind": TERMINAL_ARTIFACT_DEFAULT_KIND,
        "envelope": describe_terminal_artifact_envelope_contract(),
        "kind_contracts": kind_contracts,
        "terminal_artifact_kind_contracts": terminal_artifact_kind_contracts,
        "terminal_artifact_kind_contracts_fingerprint": terminal_artifact_kind_contracts_fingerprint(),
        "render_target_contract": render_target_contract,
        "terminal_artifact_render_target_contract": _snapshot_contract_section(render_target_contract),
        "renderer_entrypoints": renderer_entrypoints,
        "rendering": rendering_contract,
        "terminal_artifact_rendering": _snapshot_contract_section(rendering_contract),
        "terminal_artifact_rendering_contract": _snapshot_contract_section(rendering_contract),
        "rendering_fingerprint": terminal_artifact_rendering_contract_fingerprint(),
        "terminal_artifact_cli_fallback_target": terminal_artifact_cli_fallback_target_contract,
        "terminal_artifact_cli_fallback_target_contract": _snapshot_contract_section(
            terminal_artifact_cli_fallback_target_contract
        ),
        "terminal_artifact_cli_fallback_target_fingerprint": terminal_artifact_cli_fallback_target_contract[
            "contract_fingerprint"
        ],
        "terminal_artifact_cli_fallback_target_contract_fingerprint": terminal_artifact_cli_fallback_target_contract[
            "contract_fingerprint"
        ],
        "terminal_artifact_cli_fallback_target_contract_fingerprints": _snapshot_contract_section(
            terminal_artifact_cli_fallback_target_contract["contract_fingerprints"]
        ),
        "raw_leaf_card_default": _build_terminal_artifact_raw_leaf_card_default_manifest(),
        "raw_leaf_card_default_contract": raw_leaf_card_default_contract,
        "terminal_artifact_raw_leaf_card_default_contract": _snapshot_contract_section(
            raw_leaf_card_default_contract
        ),
        "raw_leaf_card_default_contract_fingerprints": describe_terminal_artifact_raw_leaf_card_default_contract_fingerprints(),
        "raw_leaf_card_default_policy": copy.deepcopy(
            terminal_artifact_cli_fallback_target_contract["raw_leaf_card_default_policy"]
        ),
        "raw_leaf_card_default_policy_contract": raw_leaf_card_default_policy_contract,
        "terminal_artifact_raw_leaf_card_default_policy_contract": _snapshot_contract_section(
            raw_leaf_card_default_policy_contract
        ),
        "raw_leaf_card_default_policy_contract_fingerprint": raw_leaf_card_default_policy_contract[
            "contract_fingerprint"
        ],
        "raw_leaf_card_default_policy_contract_fingerprints": describe_terminal_artifact_raw_leaf_card_default_policy_contract_fingerprints(),
        "terminal_artifact_raw_leaf_card_default_policy_fingerprint": raw_leaf_card_default_policy_contract[
            "contract_fingerprint"
        ],
        "terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint": raw_leaf_card_default_policy_contract[
            "contract_fingerprint"
        ],
        "terminal_artifact_raw_leaf_card_default_policy_contract_fingerprints": _snapshot_contract_section(
            describe_terminal_artifact_raw_leaf_card_default_policy_contract_fingerprints(
                include_terminal_artifact_raw_leaf_card_default_policy=True,
            )
        ),
        "kind_resolution": copy.deepcopy(render_target_contract["kind_resolution"]),
        "kind_resolution_fingerprint": render_target_contract["kind_resolution_fingerprint"],
        "fallback_recovery": copy.deepcopy(render_target_contract["fallback_recovery"]),
        "fallback_recovery_fingerprint": render_target_contract["fallback_recovery_fingerprint"],
        "kind_policy": {
            "card": "defer to terminal artifact dispatch and keep card as the default recovery path",
            "action": "recover action payloads with render_terminal_action",
            "selection": "recover selection payloads with render_terminal_selection",
        },
        "resolver_failure_policy": {
            "retry_resolver": "resolve_terminal_artifact_render_target",
            "raw_leaf_card_default_kind": TERMINAL_ARTIFACT_DEFAULT_KIND,
            "leaf_renderers": {
                "card": "render_terminal_card",
                "action": "render_terminal_action",
                "selection": "render_terminal_selection",
            },
        },
        "terminal_fallback_contract": terminal_fallback_contract,
        "terminal_artifact_render_target_contract_fingerprint": terminal_artifact_render_target_contract_fingerprint(),
        "terminal_artifact_rendering_contract_fingerprint": terminal_artifact_rendering_contract_fingerprint(),
        "terminal_fallback_contract_fingerprint": terminal_fallback_contract_fingerprint(),
        "contract_fingerprints": describe_terminal_artifact_cli_fallback_contract_fingerprints(),
    }


def _build_terminal_artifact_cli_fallback_target_contract_manifest() -> dict[str, Any]:
    render_target_contract = describe_terminal_artifact_render_target_contract()
    raw_leaf_card_default_contract = describe_terminal_artifact_raw_leaf_card_default_contract()
    raw_leaf_card_default_policy_contract = describe_terminal_artifact_raw_leaf_card_default_policy_contract()
    return {
        "contract_version": A2UI_CONTRACT_VERSION,
        "a2ui_version": A2UI_VERSION,
        "terminal_artifact_schema_version": TERMINAL_ARTIFACT_SCHEMA_VERSION,
        "terminal_artifact_cli_fallback_target_schema_version": TERMINAL_ARTIFACT_CLI_FALLBACK_TARGET_SCHEMA_VERSION,
        "terminal_artifact_cli_fallback_target_version": TERMINAL_ARTIFACT_CLI_FALLBACK_TARGET_SCHEMA_VERSION,
        "type": "TerminalArtifactCliFallbackTargetContract",
        "fallback_target_resolver": "resolve_terminal_artifact_cli_fallback_target",
        "fallback_renderer": "ShellUI.render_artifact",
        "supported_kinds": list(TERMINAL_ARTIFACT_SUPPORTED_KINDS),
        "default_kind": TERMINAL_ARTIFACT_DEFAULT_KIND,
        "renderer_entrypoints": {
            "terminal_artifact": "render_terminal_artifact",
            "cli_fallback": "render_terminal_cli_fallback",
            "card": "render_terminal_card",
            "action": "render_terminal_action",
            "selection": "render_terminal_selection",
        },
        "preserve_raw_leaf_card_default": True,
        "raw_leaf_required_fields": ["id", "label", "payload"],
        "raw_leaf_hint_fields": {
            "action": ["confirm", "policy_sensitive"],
            "selection": ["selected", "disabled"],
        },
        "raw_leaf_card_default_policy": _build_terminal_artifact_raw_leaf_card_default_policy_manifest(),
        "kind_resolution": copy.deepcopy(render_target_contract["kind_resolution"]),
        "kind_resolution_fingerprint": render_target_contract["kind_resolution_fingerprint"],
        "fallback_recovery": copy.deepcopy(render_target_contract["fallback_recovery"]),
        "fallback_recovery_fingerprint": render_target_contract["fallback_recovery_fingerprint"],
        "raw_leaf_card_default_contract": raw_leaf_card_default_contract,
        "raw_leaf_card_default_contract_fingerprint": raw_leaf_card_default_contract["contract_fingerprint"],
        "raw_leaf_card_default_policy_contract": raw_leaf_card_default_policy_contract,
        "raw_leaf_card_default_policy_contract_fingerprint": raw_leaf_card_default_policy_contract[
            "contract_fingerprint"
        ],
        "raw_leaf_card_default_policy_contract_fingerprints": describe_terminal_artifact_raw_leaf_card_default_policy_contract_fingerprints(),
        "terminal_artifact_raw_leaf_card_default_policy_contract": _snapshot_contract_section(
            raw_leaf_card_default_policy_contract
        ),
        "terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint": raw_leaf_card_default_policy_contract[
            "contract_fingerprint"
        ],
        "terminal_artifact_raw_leaf_card_default_policy_contract_fingerprints": _snapshot_contract_section(
            describe_terminal_artifact_raw_leaf_card_default_policy_contract_fingerprints(
                include_terminal_artifact_raw_leaf_card_default_policy=True,
            )
        ),
        "terminal_artifact_cli_fallback_target_contract_fingerprints": describe_terminal_artifact_cli_fallback_target_contract_fingerprints(),
        "contract_fingerprints": describe_terminal_artifact_cli_fallback_target_contract_fingerprints(),
    }


def _build_terminal_artifact_envelope_manifest() -> dict[str, Any]:
    return {
        "type": _TERMINAL_ARTIFACT_ENVELOPE_TYPE,
        "contract_version": A2UI_CONTRACT_VERSION,
        "a2ui_version": A2UI_VERSION,
        "terminal_artifact_schema_version": TERMINAL_ARTIFACT_SCHEMA_VERSION,
        "required_fields": ["kind", "artifact"],
        "optional_fields": ["contract_version", "a2ui_version"],
        "kind_field": "kind",
        "artifact_field": "artifact",
        "supported_kinds": list(TERMINAL_ARTIFACT_SUPPORTED_KINDS),
    }


def _build_terminal_artifact_kind_resolution_manifest() -> dict[str, Any]:
    return {
        "precedence": [
            "validated envelope kind",
            "typed payload kind",
            "explicit caller kind hint",
            "partial leaf hint recovery",
            "schema-valid leaf payload recovery",
            "card default",
        ],
        "card_payloads_override_conflicting_action_or_selection_hints": True,
        "partial_leaf_recovery": {
            "required_fields": ["id", "payload"],
            "action_hints": ["confirm", "policy_sensitive"],
            "selection_hints": ["selected", "disabled"],
        },
        "leaf_recovery": _build_terminal_artifact_leaf_recovery_manifest(),
    }


def _build_terminal_artifact_fallback_recovery_manifest() -> dict[str, Any]:
    return {
        "malformed_card_envelopes": {
            "action": "normalize_action_ref",
            "selection": "normalize_selection_ref",
        }
    }


def _build_terminal_artifact_leaf_recovery_manifest() -> dict[str, Any]:
    return {
        "malformed_card_envelopes": {
            "action": "normalize_action_ref",
            "selection": "normalize_selection_ref",
        }
    }


def _build_terminal_artifact_raw_leaf_card_default_manifest() -> dict[str, Any]:
    return {
        "preserve_when_kind_is_unset": True,
        "required_fields": ["id", "label", "payload"],
        "excluded_fields": ["type", "blocks", "actions", "confirm", "policy_sensitive", "selected", "disabled"],
    }


def _build_terminal_artifact_raw_leaf_card_default_policy_manifest() -> dict[str, Any]:
    return {
        "default_kind": TERMINAL_ARTIFACT_DEFAULT_KIND,
        "preserve_when_kind_is_unset": True,
        "invalid_kind_treated_as_absent": True,
    }


def _build_terminal_artifact_raw_leaf_card_default_policy_contract_manifest() -> dict[str, Any]:
    raw_leaf_card_default_policy = _build_terminal_artifact_raw_leaf_card_default_policy_manifest()
    return {
        "contract_version": A2UI_CONTRACT_VERSION,
        "a2ui_version": A2UI_VERSION,
        "terminal_artifact_schema_version": TERMINAL_ARTIFACT_SCHEMA_VERSION,
        "terminal_artifact_raw_leaf_card_default_schema_version": TERMINAL_ARTIFACT_RAW_LEAF_CARD_DEFAULT_SCHEMA_VERSION,
        "terminal_artifact_raw_leaf_card_default_policy_version": TERMINAL_ARTIFACT_RAW_LEAF_CARD_DEFAULT_SCHEMA_VERSION,
        "type": "TerminalArtifactRawLeafCardDefaultPolicyContract",
        "default_kind": raw_leaf_card_default_policy["default_kind"],
        "preserve_when_kind_is_unset": raw_leaf_card_default_policy["preserve_when_kind_is_unset"],
        "invalid_kind_treated_as_absent": raw_leaf_card_default_policy["invalid_kind_treated_as_absent"],
    }


def _build_terminal_artifact_raw_leaf_card_default_contract_manifest() -> dict[str, Any]:
    raw_leaf_card_default = _build_terminal_artifact_raw_leaf_card_default_manifest()
    return {
        "contract_version": A2UI_CONTRACT_VERSION,
        "a2ui_version": A2UI_VERSION,
        "terminal_artifact_schema_version": TERMINAL_ARTIFACT_SCHEMA_VERSION,
        "terminal_artifact_raw_leaf_card_default_schema_version": TERMINAL_ARTIFACT_RAW_LEAF_CARD_DEFAULT_SCHEMA_VERSION,
        "terminal_artifact_raw_leaf_card_default_version": TERMINAL_ARTIFACT_RAW_LEAF_CARD_DEFAULT_SCHEMA_VERSION,
        "type": "TerminalArtifactRawLeafCardDefaultContract",
        "default_kind": TERMINAL_ARTIFACT_DEFAULT_KIND,
        "preserve_when_kind_is_unset": raw_leaf_card_default["preserve_when_kind_is_unset"],
        "required_fields": list(raw_leaf_card_default["required_fields"]),
        "excluded_fields": list(raw_leaf_card_default["excluded_fields"]),
    }


def _build_terminal_artifact_kind_contracts() -> dict[str, dict[str, str]]:
    return {
        "card": {
            "kind": "card",
            "contract_fingerprint": card_contract_fingerprint(),
        },
        "action": {
            "kind": "action",
            "contract_fingerprint": action_contract_fingerprint(),
        },
        "selection": {
            "kind": "selection",
            "contract_fingerprint": selection_contract_fingerprint(),
        },
    }


def _build_terminal_artifact_render_target_contract_manifest() -> dict[str, Any]:
    raw_leaf_card_default_contract = describe_terminal_artifact_raw_leaf_card_default_contract()
    kind_contracts = _build_terminal_artifact_kind_contracts()
    terminal_artifact_kind_contracts = _snapshot_contract_section(kind_contracts)
    return {
        "contract_version": A2UI_CONTRACT_VERSION,
        "a2ui_version": A2UI_VERSION,
        "terminal_artifact_schema_version": TERMINAL_ARTIFACT_SCHEMA_VERSION,
        "terminal_artifact_render_target_schema_version": TERMINAL_ARTIFACT_RENDER_TARGET_SCHEMA_VERSION,
        "terminal_artifact_render_target_version": TERMINAL_ARTIFACT_RENDER_TARGET_SCHEMA_VERSION,
        "type": "TerminalArtifactRenderTargetContract",
        "render_target_resolver": "resolve_terminal_artifact_render_target",
        "supported_kinds": list(TERMINAL_ARTIFACT_SUPPORTED_KINDS),
        "default_kind": TERMINAL_ARTIFACT_DEFAULT_KIND,
        "envelope": describe_terminal_artifact_envelope_contract(),
        "kind_contracts": kind_contracts,
        "terminal_artifact_kind_contracts": terminal_artifact_kind_contracts,
        "terminal_artifact_kind_contracts_fingerprint": terminal_artifact_kind_contracts_fingerprint(),
        "raw_leaf_card_default": _build_terminal_artifact_raw_leaf_card_default_manifest(),
        "raw_leaf_card_default_contract": raw_leaf_card_default_contract,
        "terminal_artifact_raw_leaf_card_default_contract": _snapshot_contract_section(
            raw_leaf_card_default_contract
        ),
        "raw_leaf_card_default_contract_fingerprints": describe_terminal_artifact_raw_leaf_card_default_contract_fingerprints(),
        "raw_leaf_card_default_policy": copy.deepcopy(_build_terminal_artifact_raw_leaf_card_default_policy_manifest()),
        "raw_leaf_card_default_policy_contract": describe_terminal_artifact_raw_leaf_card_default_policy_contract(),
        "terminal_artifact_raw_leaf_card_default_policy_contract": _snapshot_contract_section(
            describe_terminal_artifact_raw_leaf_card_default_policy_contract()
        ),
        "raw_leaf_card_default_policy_contract_fingerprints": describe_terminal_artifact_raw_leaf_card_default_policy_contract_fingerprints(),
        "terminal_artifact_raw_leaf_card_default_policy_contract_fingerprints": _snapshot_contract_section(
            describe_terminal_artifact_raw_leaf_card_default_policy_contract_fingerprints(
                include_terminal_artifact_raw_leaf_card_default_policy=True,
            )
        ),
        "kind_resolution": _build_terminal_artifact_kind_resolution_manifest(),
        "kind_resolution_fingerprint": terminal_artifact_kind_resolution_fingerprint(),
        "fallback_recovery": _build_terminal_artifact_fallback_recovery_manifest(),
        "fallback_recovery_fingerprint": terminal_artifact_fallback_recovery_fingerprint(),
        "contract_fingerprints": describe_terminal_artifact_render_target_contract_fingerprints(),
    }


def _build_terminal_artifact_render_target_contract_fingerprints(
    *,
    include_terminal_artifact_render_target: bool = False,
) -> dict[str, str]:
    fingerprints = {
        "kind_contracts": terminal_artifact_kind_contracts_fingerprint(),
        "raw_leaf_card_default_contract": terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        "raw_leaf_card_default_policy_contract": terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
        "kind_resolution": terminal_artifact_kind_resolution_fingerprint(),
        "fallback_recovery": terminal_artifact_fallback_recovery_fingerprint(),
    }
    if include_terminal_artifact_render_target:
        fingerprints["terminal_artifact_render_target"] = terminal_artifact_render_target_contract_fingerprint()
    return fingerprints


def terminal_artifact_kind_contracts_fingerprint() -> str:
    """Return a stable fingerprint for the shared terminal artifact kind contracts."""

    manifest = describe_terminal_artifact_kind_contracts()
    return _fingerprint_manifest_section(manifest)


def _build_read_only_fallback_action_manifest() -> list[dict[str, Any]]:
    return [
        {
            "id": FALLBACK_COPY_ACTION_ID,
            "label": "Copy JSON",
            "version": A2UI_ACTION_SCHEMA_VERSION,
            "payload_fields": ["text"],
        }
    ]


def _build_read_only_json_preview_block(payload: dict[str, Any], *, max_payload_bytes: int) -> dict[str, Any]:
    return {
        "type": "CodeBlock",
        "language": "json",
        "code": _render_payload_preview(payload, max_payload_bytes=max_payload_bytes, pretty=True),
        "collapsed": True,
    }


def _build_action_payload_schema_manifest() -> list[dict[str, Any]]:
    return [
        {
            "id": action_id,
            "version": A2UI_ACTION_SCHEMA_VERSION,
            "fields": sorted(schema),
        }
        for action_id, schema in sorted(_ACTION_SCHEMAS.items())
    ]


def _build_card_schema_manifest() -> list[dict[str, Any]]:
    return [
        {
            "type": GENERIC_CARD_TYPE,
            "version": A2UI_VERSION,
            "required_fields": ["type", "title", "a2ui_version", "blocks", "actions"],
            "optional_fields": ["subtitle", "debug"],
            "allowed_actions": sorted(ALLOWED_ACTION_IDS),
            "action_policy": "client_allowlist",
        },
        {
            "type": UNKNOWN_CARD_TYPE,
            "version": A2UI_VERSION,
            "required_fields": ["type", "title", "subtitle", "a2ui_version", "debug", "blocks", "actions"],
            "optional_fields": [],
            "allowed_actions": [FALLBACK_COPY_ACTION_ID],
            "action_policy": "copy_to_clipboard_only",
        },
    ]


def _build_card_fallback_manifest() -> dict[str, Any]:
    return {
        "generic_card": {
            "type": GENERIC_CARD_TYPE,
            "action_policy": "client_allowlist",
            "allowed_actions": [FALLBACK_COPY_ACTION_ID],
            "actions": _build_read_only_fallback_action_manifest(),
        },
        "unknown_card": {
            "type": UNKNOWN_CARD_TYPE,
            "action_policy": "copy_to_clipboard_only",
            "allowed_actions": [FALLBACK_COPY_ACTION_ID],
            "default_preview_bytes": DEFAULT_UNKNOWN_CARD_PREVIEW_BYTES,
            "actions": _build_read_only_fallback_action_manifest(),
        },
    }


def _build_a2ui_schema_manifest() -> dict[str, Any]:
    return {
        "capabilities": describe_a2ui_capabilities_contract(),
        "card_contract": describe_card_contract(),
        "cards": _build_card_schema_manifest(),
        "selection": describe_selection_contract(),
        "action": describe_action_contract(),
        "terminal_artifact_envelope": describe_terminal_artifact_envelope_contract(),
        "terminal_artifact_render_target": describe_terminal_artifact_render_target_contract(),
        "actions": [
            {
                "type": "ActionRef",
                "version": A2UI_ACTION_SCHEMA_VERSION,
                "required_fields": ["id", "label", "payload"],
                "optional_fields": ["confirm", "policy_sensitive"],
                "payload_schemas": _build_action_payload_schema_manifest(),
            }
        ],
        "terminal_fallback": describe_terminal_fallback_contract(),
        "terminal_artifact": describe_terminal_artifact_contract(),
        "terminal_artifact_rendering": describe_terminal_artifact_rendering_contract(),
        "terminal_artifact_cli_fallback": describe_terminal_artifact_cli_fallback_contract(),
        "terminal_artifact_cli_fallback_target": describe_terminal_artifact_cli_fallback_target_contract(),
    }


def _build_a2ui_capabilities_field_contracts() -> list[dict[str, Any]]:
    return [
        {
            "field": "a2ui_version",
            "type": "int",
            "description": f"must equal {A2UI_VERSION}",
        },
        {
            "field": "client_name",
            "type": "str",
            "description": "trimmed non-empty string",
        },
        {
            "field": "cards_supported",
            "type": "tuple[str, ...]",
            "description": "canonical unique card types excluding reserved card names",
            "reserved_values": list(_RESERVED_CARD_TYPES),
        },
        {
            "field": "primitive_blocks_supported",
            "type": "tuple[str, ...]",
            "description": "canonical unique primitive block types",
            "required_values": list(REQUIRED_PRIMITIVE_BLOCKS),
        },
        {
            "field": "actions_supported",
            "type": "tuple[str, ...]",
            "description": "canonical unique allowlisted action ids",
            "allowed_values": sorted(ALLOWED_ACTION_IDS),
        },
        {
            "field": "max_payload_bytes",
            "type": "int",
            "description": "positive payload byte ceiling",
        },
        {
            "field": "supports_streaming",
            "type": "bool",
            "description": "streaming support flag",
        },
    ]


def _canonicalize_supported_sequence(
    values: tuple[str, ...],
    *,
    canonical_order: tuple[str, ...],
) -> tuple[str, ...]:
    order_index = {value: index for index, value in enumerate(canonical_order)}
    return tuple(
        sorted(
            values,
            key=lambda value: (
                order_index.get(value, len(order_index)),
                value,
            ),
        )
    )


def a2ui_contract_fingerprint() -> str:
    """Return a stable fingerprint for the current contract manifest."""

    manifest = _build_a2ui_contract_manifest()
    return _fingerprint_manifest_section(manifest)


def selection_contract_fingerprint() -> str:
    """Return a stable fingerprint for the SelectionRef contract manifest."""

    manifest = _build_selection_contract_manifest()
    return _fingerprint_manifest_section(manifest)


def action_contract_fingerprint() -> str:
    """Return a stable fingerprint for the ActionRef contract manifest."""

    manifest = _build_action_contract_manifest()
    return _fingerprint_manifest_section(manifest)


def card_contract_fingerprint() -> str:
    """Return a stable fingerprint for the card contract manifest."""

    manifest = _build_card_contract_manifest()
    return _fingerprint_manifest_section(manifest)


def terminal_fallback_contract_fingerprint() -> str:
    """Return a stable fingerprint for the terminal fallback contract manifest."""

    manifest = _build_terminal_fallback_contract_manifest()
    return _fingerprint_manifest_section(manifest)


def terminal_artifact_contract_fingerprint() -> str:
    """Return a stable fingerprint for the terminal artifact dispatch manifest."""

    manifest = _build_terminal_artifact_contract_manifest(include_contract_fingerprints=False)
    return _fingerprint_manifest_section(manifest)


def terminal_artifact_envelope_contract_fingerprint() -> str:
    """Return a stable fingerprint for the TerminalArtifact envelope manifest."""

    manifest = _build_terminal_artifact_envelope_manifest()
    return _fingerprint_manifest_section(manifest)


def terminal_artifact_rendering_contract_fingerprint() -> str:
    """Return a stable fingerprint for the terminal artifact rendering manifest."""

    manifest = _build_terminal_artifact_rendering_contract_manifest()
    return _fingerprint_manifest_section(manifest)


def terminal_artifact_cli_fallback_contract_fingerprint() -> str:
    """Return a stable fingerprint for the terminal artifact CLI fallback manifest."""

    manifest = _build_terminal_artifact_cli_fallback_contract_manifest()
    return _fingerprint_manifest_section(manifest)


def terminal_artifact_cli_fallback_target_contract_fingerprint() -> str:
    """Return a stable fingerprint for the CLI fallback target-selection manifest."""

    manifest = _build_terminal_artifact_cli_fallback_target_contract_manifest()
    return _fingerprint_manifest_section(manifest)


def terminal_artifact_raw_leaf_card_default_contract_fingerprint() -> str:
    """Return a stable fingerprint for the raw-leaf card default contract manifest."""

    manifest = _build_terminal_artifact_raw_leaf_card_default_contract_manifest()
    return _fingerprint_manifest_section(manifest)


def terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint() -> str:
    """Return a stable fingerprint for the raw-leaf card default policy manifest."""

    manifest = _build_terminal_artifact_raw_leaf_card_default_policy_contract_manifest()
    return _fingerprint_manifest_section(manifest)


def terminal_artifact_render_target_contract_fingerprint() -> str:
    """Return a stable fingerprint for the terminal artifact render-target manifest."""

    manifest = _build_terminal_artifact_render_target_contract_manifest()
    return _fingerprint_manifest_section(manifest)


def terminal_artifact_kind_resolution_fingerprint() -> str:
    """Return a stable fingerprint for the terminal artifact kind-resolution manifest."""

    manifest = _build_terminal_artifact_kind_resolution_manifest()
    return _fingerprint_manifest_section(manifest)


def terminal_artifact_fallback_recovery_fingerprint() -> str:
    """Return a stable fingerprint for the terminal artifact fallback-recovery manifest."""

    manifest = _build_terminal_artifact_fallback_recovery_manifest()
    return _fingerprint_manifest_section(manifest)


def a2ui_capabilities_contract_fingerprint() -> str:
    """Return a stable fingerprint for the A2UI capabilities handshake manifest."""

    manifest = _build_a2ui_capabilities_contract_manifest()
    return _fingerprint_manifest_section(manifest)


def _fingerprint_manifest_section(section: Any) -> str:
    return hashlib.sha256(_canonical_json(section).encode("utf-8")).hexdigest()


def validate_capabilities(capabilities: A2UICapabilities) -> None:
    if type(capabilities.a2ui_version) is not int or capabilities.a2ui_version != A2UI_VERSION:
        raise ValueError("Unsupported a2ui version")
    if not isinstance(capabilities.client_name, str) or not capabilities.client_name.strip():
        raise ValueError("client_name is required")
    if type(capabilities.max_payload_bytes) is not int or capabilities.max_payload_bytes <= 0:
        raise ValueError("max_payload_bytes must be positive")
    if not isinstance(capabilities.supports_streaming, bool):
        raise ValueError("supports_streaming must be a bool")
    cards_supported = _validate_supported_string_sequence(
        capabilities.cards_supported,
        field_name="cards_supported",
    )
    seen_cards: set[str] = set()
    for card_type in cards_supported:
        if not card_type.strip():
            raise ValueError("Supported card types must be non-empty strings")
        if card_type != card_type.strip():
            raise ValueError(f"Supported card types must be canonical, got: {card_type!r}")
        canonical_card_type = card_type
        if canonical_card_type in _RESERVED_CARD_TYPES:
            raise ValueError(f"Reserved card type cannot be advertised as supported: {canonical_card_type}")
        if canonical_card_type in seen_cards:
            raise ValueError(f"Duplicate supported card type: {canonical_card_type}")
        seen_cards.add(canonical_card_type)
    primitive_blocks_supported = _validate_supported_string_sequence(
        capabilities.primitive_blocks_supported,
        field_name="primitive_blocks_supported",
    )
    seen_blocks: set[str] = set()
    for block_type in primitive_blocks_supported:
        if not block_type.strip():
            raise ValueError("Supported primitive block types must be non-empty strings")
        if block_type != block_type.strip():
            raise ValueError(f"Supported primitive block types must be canonical, got: {block_type!r}")
        canonical_block_type = block_type
        if canonical_block_type in seen_blocks:
            raise ValueError(f"Duplicate supported primitive block type: {canonical_block_type}")
        seen_blocks.add(canonical_block_type)
    if not _PRIMITIVE_BLOCK_SET.issubset(seen_blocks):
        raise ValueError("Missing required primitive block support")
    actions_supported = _validate_supported_string_sequence(
        capabilities.actions_supported,
        field_name="actions_supported",
    )
    seen_actions: set[str] = set()
    for action_id in actions_supported:
        if not action_id.strip():
            raise ValueError("Supported action ids must be non-empty strings")
        if action_id != action_id.strip():
            raise ValueError(f"Supported action ids must be canonical, got: {action_id!r}")
        canonical_action_id = action_id
        if canonical_action_id not in _ALLOWED_ACTION_SET:
            raise ValueError(f"Unknown action in capabilities: {canonical_action_id}")
        if canonical_action_id in seen_actions:
            raise ValueError(f"Duplicate supported action id: {canonical_action_id}")
        seen_actions.add(canonical_action_id)


def engine_prepare_card(card: Any, capabilities: A2UICapabilities) -> dict[str, Any]:
    validate_capabilities(capabilities)
    coerced_card = _coerce_card_payload(card)
    if coerced_card is not None:
        card = coerced_card
    card_type = _normalize_card_type(card)
    if card_type == GENERIC_CARD_TYPE:
        return _materialize_generic_card(card, capabilities)
    if card_type == UNKNOWN_CARD_TYPE:
        return _materialize_unknown_card(card, capabilities)

    if card_type in set(capabilities.cards_supported):
        _validate_card_version(card)
        return _materialize_versioned_card(card, capabilities)

    # Safe fallback for unsupported specialized cards.
    read_only_actions = _build_read_only_fallback_actions(
        card,
        supported_actions=set(capabilities.actions_supported),
        max_payload_bytes=capabilities.max_payload_bytes,
    )
    fallback_card = {
        "type": GENERIC_CARD_TYPE,
        "title": _build_fallback_title(GENERIC_CARD_TYPE, source_card_type=card_type),
        "subtitle": GENERIC_FALLBACK_SUBTITLE,
        "a2ui_version": A2UI_VERSION,
        "debug": _build_fallback_debug(card_type, fallback_kind="generic"),
        "blocks": [
            {
                "type": "AlertBlock",
                "severity": "info",
                "title": "Card fallback",
                "message": "Rendered as GenericCard because client does not support this specialized card.",
            },
            *_extract_safe_primitive_blocks(card, allow_code_block=False),
            _build_read_only_json_preview_block(card, max_payload_bytes=capabilities.max_payload_bytes),
        ],
        "actions": read_only_actions,
    }
    _validate_fallback_card(
        fallback_card,
        expected_type=GENERIC_CARD_TYPE,
        expected_fallback_kind="generic",
    )
    return fallback_card


def validate_unknown_card(card: Any) -> None:
    coerced_card = _coerce_card_payload(card)
    if coerced_card is not None:
        card = coerced_card
    _validate_fallback_card(
        card,
        expected_type=UNKNOWN_CARD_TYPE,
        expected_fallback_kind="unknown",
    )


def studio_materialize_card(card: Any, capabilities: A2UICapabilities) -> dict[str, Any]:
    validate_capabilities(capabilities)
    coerced_card = _coerce_card_payload(card)
    if coerced_card is not None:
        card = coerced_card
    card_type = _normalize_card_type(card)
    if card_type == GENERIC_CARD_TYPE:
        return _materialize_generic_card(card, capabilities)
    if card_type == UNKNOWN_CARD_TYPE:
        return _materialize_unknown_card(card, capabilities)
    if card_type in set(capabilities.cards_supported):
        _validate_card_version(card)
        return _materialize_versioned_card(card, capabilities)
    fallback_card = build_unknown_card(
        card,
        max_payload_bytes=capabilities.max_payload_bytes,
        supported_actions=capabilities.actions_supported,
    )
    return fallback_card


def build_unknown_card(
    raw_card: Any,
    *,
    max_payload_bytes: int | None = DEFAULT_UNKNOWN_CARD_PREVIEW_BYTES,
    supported_actions: tuple[str, ...] | None = None,
) -> dict[str, Any]:
    coerced_card = _coerce_card_payload(raw_card)
    if coerced_card is not None:
        raw_card = coerced_card
    type_name = _normalize_card_type(raw_card)
    effective_max_payload_bytes = _normalize_preview_budget(max_payload_bytes)
    blocks = _extract_safe_primitive_blocks(raw_card, allow_code_block=False)
    blocks.append(_build_read_only_json_preview_block(raw_card, max_payload_bytes=effective_max_payload_bytes))
    actions = _build_unknown_card_actions(
        raw_card,
        supported_actions=supported_actions,
        max_payload_bytes=effective_max_payload_bytes,
    )
    _validate_canonical_read_only_fallback_actions(actions)
    card = {
        "type": UNKNOWN_CARD_TYPE,
        "title": _build_fallback_title(UNKNOWN_CARD_TYPE, source_card_type=type_name),
        "subtitle": UNKNOWN_FALLBACK_SUBTITLE,
        "a2ui_version": A2UI_VERSION,
        "debug": _build_fallback_debug(type_name, fallback_kind="unknown"),
        "blocks": blocks,
        "actions": actions,
    }
    _validate_fallback_card(card, expected_type=UNKNOWN_CARD_TYPE, expected_fallback_kind="unknown")
    return card


def validate_generic_card(card: Any, *, strict_actions: bool = True) -> None:
    coerced_card = _coerce_card_payload(card)
    if coerced_card is not None:
        card = coerced_card
    if card.get("type") != GENERIC_CARD_TYPE:
        raise ValueError("Card type must be GenericCard")
    version = card.get("a2ui_version")
    if version is not None:
        if type(version) is not int:
            raise ValueError("GenericCard a2ui_version must be an int")
        if version != A2UI_VERSION:
            raise ValueError("Unsupported GenericCard a2ui_version")
    title = card.get("title")
    if not isinstance(title, str) or not title.strip():
        raise ValueError("GenericCard title is required")
    subtitle = card.get("subtitle")
    if subtitle is not None and not isinstance(subtitle, str):
        raise ValueError("GenericCard subtitle must be a string when provided")
    if "blocks" not in card:
        raise ValueError("GenericCard blocks are required")
    blocks = card.get("blocks")
    if not isinstance(blocks, (list, tuple)):
        raise ValueError("GenericCard blocks must be a list or tuple")
    for block in blocks:
        validate_primitive_block(block)
    if "actions" not in card:
        raise ValueError("GenericCard actions are required")
    actions = card.get("actions")
    if not isinstance(actions, (list, tuple)):
        raise ValueError("GenericCard actions must be a list or tuple")
    if strict_actions:
        seen_actions: set[str] = set()
        for action in actions:
            normalized_action = _normalize_action(_action_ref_to_dict(action), supported_actions=_ALLOWED_ACTION_SET)
            action_key = _canonical_json(normalized_action)
            if action_key in seen_actions:
                raise ValueError("GenericCard actions must not contain duplicates")
            seen_actions.add(action_key)


def _validate_fallback_card(
    card: dict[str, Any],
    *,
    expected_type: str,
    expected_fallback_kind: str,
) -> None:
    extra_keys = set(card) - {"type", "title", "subtitle", "a2ui_version", "debug", "blocks", "actions"}
    if extra_keys:
        extras = ", ".join(sorted(extra_keys))
        raise ValueError(f"Fallback card contains unexpected field(s): {extras}")
    if card.get("type") != expected_type:
        raise ValueError(f"Fallback card type must be {expected_type}")
    version = card.get("a2ui_version")
    if type(version) is not int:
        raise ValueError("Fallback card a2ui_version must be an int")
    if version != A2UI_VERSION:
        raise ValueError("Unsupported fallback card a2ui_version")
    title = card.get("title")
    if not isinstance(title, str) or not title.strip():
        raise ValueError("Fallback card title is required")
    subtitle = card.get("subtitle")
    if not isinstance(subtitle, str) or not subtitle.strip():
        raise ValueError("Fallback card subtitle is required")
    blocks = card.get("blocks")
    if not isinstance(blocks, (list, tuple)):
        raise ValueError("Fallback card blocks must be a list or tuple")
    for block in blocks:
        validate_primitive_block(block)
    actions = card.get("actions")
    if not isinstance(actions, (list, tuple)):
        raise ValueError("Fallback card actions must be a list or tuple")
    _validate_canonical_read_only_fallback_actions(actions)
    debug = card.get("debug")
    if not isinstance(debug, Mapping):
        raise ValueError("Fallback card debug is required")
    extra_debug_keys = set(debug) - {"contract_version", "fallback_kind", "source_card_type"}
    if extra_debug_keys:
        extras = ", ".join(sorted(extra_debug_keys))
        raise ValueError(f"Fallback card debug contains unexpected field(s): {extras}")
    contract_version = debug.get("contract_version")
    if type(contract_version) is not int or contract_version != A2UI_CONTRACT_VERSION:
        raise ValueError("Fallback card debug contract_version is invalid")
    fallback_kind = debug.get("fallback_kind")
    source_card_type = debug.get("source_card_type")
    if not isinstance(fallback_kind, str) or fallback_kind.strip() != expected_fallback_kind:
        raise ValueError("Fallback card debug fallback_kind is invalid")
    if not isinstance(source_card_type, str) or source_card_type.strip() != source_card_type or not source_card_type.strip():
        raise ValueError("Fallback card debug source_card_type is required")
    expected_title = _build_fallback_title(expected_type, source_card_type=source_card_type)
    if title.strip() != expected_title:
        raise ValueError("Fallback card title is invalid")
    expected_subtitle = _fallback_subtitle(expected_fallback_kind)
    if subtitle.strip() != expected_subtitle:
        raise ValueError("Fallback card subtitle is invalid")


def _validate_card_version(card: dict[str, Any]) -> None:
    version = card.get("a2ui_version")
    if version is None:
        return
    if type(version) is not int:
        raise ValueError("Card a2ui_version must be an int")
    if version != A2UI_VERSION:
        raise ValueError("Unsupported card a2ui_version")


def validate_primitive_block(block: Any) -> None:
    if not isinstance(block, Mapping):
        raise ValueError("Primitive block must be an object")
    block_type = str(block.get("type", ""))
    if block_type not in _PRIMITIVE_BLOCK_SET:
        raise ValueError(f"Unsupported primitive block: {block_type}")
    _validate_primitive_block_fields(block_type, block)


def validate_action_ref(action: Any) -> None:
    action = _action_ref_to_dict(action)
    _normalize_action(action, supported_actions=_ALLOWED_ACTION_SET)


def validate_selection_ref(selection: Any) -> None:
    selection = _selection_ref_to_dict(selection)
    _normalize_selection(selection)


def normalize_action_ref(action: ActionRef | Mapping[str, Any]) -> ActionRef:
    normalized = _normalize_action(_action_ref_to_dict(action), supported_actions=_ALLOWED_ACTION_SET)
    return ActionRef(
        id=str(normalized["id"]),
        label=str(normalized["label"]),
        payload=_copy_action_payload(normalized["payload"]),
        confirm=dict(normalized["confirm"]) if "confirm" in normalized else None,
        policy_sensitive=bool(normalized.get("policy_sensitive", False)),
    )


def normalize_selection_ref(selection: SelectionRef | Mapping[str, Any]) -> SelectionRef:
    normalized = _normalize_selection(_selection_ref_to_dict(selection))
    return SelectionRef(
        id=str(normalized["id"]),
        label=str(normalized["label"]),
        payload=_copy_selection_payload(normalized["payload"]),
        selected=bool(normalized.get("selected", False)),
        disabled=bool(normalized.get("disabled", False)),
    )


def execute_action_with_policy_gate(
    *,
    action: ActionRef | Mapping[str, Any],
    capabilities: A2UICapabilities,
    policy_gate: PolicyGate,
    executor: Callable[[ActionRef], Any],
) -> Any:
    validate_capabilities(capabilities)
    normalized_action = normalize_action_ref(action)
    if normalized_action.id not in set(capabilities.actions_supported):
        raise ValueError("Action not supported by client")
    if not policy_gate.allow_action(
        normalized_action.id,
        normalized_action.payload,
        policy_sensitive=normalized_action.policy_sensitive,
    ):
        raise PermissionError("PolicyGate blocked action")
    return executor(normalized_action)


def render_terminal_card(card: Any) -> str:
    """Render a card payload, or unwrap a valid TerminalArtifact envelope.

    The shared CLI still calls this helper directly, so recoverable envelopes
    are accepted here as a compatibility bridge to the generic artifact
    renderer.
    """

    normalized_card = _coerce_terminal_card(card)
    if normalized_card is None:
        return _render_invalid_terminal_card(card)

    try:
        card_type = _normalize_card_type(normalized_card)
        if card_type == _TERMINAL_ARTIFACT_ENVELOPE_TYPE:
            try:
                return render_terminal_artifact(normalized_card)
            except Exception:
                try:
                    recovered_artifact, recovered_kind = _resolve_terminal_artifact_render_target(
                        normalized_card,
                        allow_invalid_envelope_recovery=True,
                    )
                except Exception:
                    recovered_artifact = None
                    recovered_kind = None
                else:
                    if recovered_kind == "action":
                        try:
                            return render_terminal_action(recovered_artifact)
                        except Exception:
                            return _render_invalid_terminal_action(recovered_artifact)
                    if recovered_kind == "selection":
                        try:
                            return render_terminal_selection(recovered_artifact)
                        except Exception:
                            return _render_invalid_terminal_selection(recovered_artifact)
                    if recovered_kind == "card":
                        try:
                            return render_terminal_card(recovered_artifact)
                        except Exception:
                            pass
                recovered_card = _resolve_terminal_artifact_card_fallback(normalized_card)
                if recovered_card is not None:
                    try:
                        return render_terminal_card(recovered_card)
                    except Exception:
                        pass
                return _render_invalid_terminal_artifact(normalized_card)
        # Keep the card leaf renderer card-only so explicit action/selection
        # payloads do not masquerade as cards when a caller bypasses dispatch.
        if _infer_terminal_artifact_kind_from_mapping(normalized_card) in {"action", "selection"}:
            return _render_invalid_terminal_card(normalized_card)
        raw_title = _normalize_card_title(normalized_card)
        title = _render_terminal_inline_text(raw_title)
        rendered_card_type = _render_terminal_inline_text(card_type)
        actions = normalized_card.get("actions")
        subtitle = normalized_card.get("subtitle")
        generic_fallback_source = _resolve_generic_fallback_source(
            raw_title,
            actions,
            normalized_card.get("debug"),
        )
        generic_fallback_hint = _is_canonical_generic_fallback_signal(subtitle, actions)
        lines = [f"[{rendered_card_type}] {title}"]
        if card_type == UNKNOWN_CARD_TYPE:
            lines.append(UNKNOWN_FALLBACK_SUBTITLE)
        elif card_type == GENERIC_CARD_TYPE and (
            generic_fallback_source is not None or generic_fallback_hint
        ):
            lines.append(GENERIC_FALLBACK_SUBTITLE)
        elif isinstance(subtitle, str) and subtitle.strip():
            lines.append(_render_terminal_inline_text(subtitle.strip()))
        version = normalized_card.get("a2ui_version")
        if type(version) is int:
            lines.append(f"A2UI v{version}")
        rendered_fallback = _render_terminal_fallback_notice(
            card_type,
            title,
            debug=normalized_card.get("debug"),
            generic_fallback_source=generic_fallback_source,
            generic_fallback_hint=generic_fallback_hint,
        )
        if rendered_fallback:
            lines.extend(rendered_fallback)
        rendered_policy = _render_terminal_action_policy(
            card_type,
            title,
            debug=normalized_card.get("debug"),
            generic_fallback_source=generic_fallback_source,
            generic_fallback_hint=generic_fallback_hint,
        )
        if rendered_policy:
            lines.extend(rendered_policy)
        debug = normalized_card.get("debug")
        rendered_debug = _render_terminal_fallback_debug(
            card_type,
            title,
            debug,
            generic_fallback_source=generic_fallback_source,
        )
        if not rendered_debug:
            rendered_debug = _render_terminal_debug(debug)
        if rendered_debug:
            lines.append("Debug:")
            lines.extend(rendered_debug)
        for block in _iter_card_entries(normalized_card.get("blocks")):
            lines.extend(_render_terminal_block(block))
        rendered_actions = _render_terminal_actions(
            actions,
            supported_actions={FALLBACK_COPY_ACTION_ID} if card_type == UNKNOWN_CARD_TYPE else _ALLOWED_ACTION_SET,
        )
        actions_present = actions is not None
        actions_are_list = isinstance(actions, (list, tuple))
        filtered_actions = actions_are_list and len(rendered_actions) < len(actions)
        if rendered_actions:
            lines.append("Actions:")
            lines.extend(rendered_actions)
            if filtered_actions:
                lines.append("Some actions filtered out by allowlist or validation")
        elif actions_present:
            lines.append("Actions: none available")
            if actions_are_list and actions:
                lines.append("Actions filtered out by allowlist or validation")
            elif not actions_are_list:
                lines.append("Actions filtered out by allowlist or validation")
        return "\n".join(lines)
    except Exception:
        return _render_invalid_terminal_card(normalized_card)


def render_terminal_selection(selection: Any) -> str:
    if isinstance(selection, SelectionRef):
        selection = _selection_ref_to_dict(selection)
    elif isinstance(selection, Mapping):
        selection = _strip_terminal_type_hint(selection, expected_type="SelectionRef")
        selection = _unwrap_terminal_artifact_leaf_payload(selection, expected_kind="selection")

    try:
        normalized = _normalize_selection(selection)
    except ValueError:
        return _render_invalid_terminal_selection(selection)

    lines = [
        f"[SelectionRef] {_render_terminal_inline_text(normalized['label'])}",
        f"Selection schema v{SELECTION_SCHEMA_VERSION}",
        f"- id: {_render_terminal_inline_text(normalized['id'])}",
        f"- selected: {'true' if bool(normalized.get('selected', False)) else 'false'}",
        f"- disabled: {'true' if bool(normalized.get('disabled', False)) else 'false'}",
    ]
    payload = normalized.get("payload")
    if isinstance(payload, Mapping):
        lines.append(f"- payload: {_render_payload_preview(payload, max_payload_bytes=256)}")
    return "\n".join(lines)


def render_terminal_action(action: Any) -> str:
    if isinstance(action, ActionRef):
        action = _action_ref_to_dict(action)
    elif isinstance(action, Mapping):
        action = _strip_terminal_type_hint(action, expected_type="ActionRef")
        action = _unwrap_terminal_artifact_leaf_payload(action, expected_kind="action")

    try:
        normalized = normalize_action_ref(action)
    except ValueError:
        return _render_invalid_terminal_action(action)

    lines = [
        f"[ActionRef] {_render_terminal_inline_text(normalized.label)}",
        f"Action schema v{A2UI_ACTION_SCHEMA_VERSION}",
        f"- id: {_render_terminal_inline_text(normalized.id)}",
        f"- payload: {_render_payload_preview(normalized.payload, max_payload_bytes=256)}",
    ]
    if normalized.confirm is not None:
        lines.append(f"- confirm: {_render_payload_preview(normalized.confirm, max_payload_bytes=256)}")
    if normalized.policy_sensitive:
        lines.append("- policy_sensitive: true")
    return "\n".join(lines)


def _resolve_terminal_artifact_render_target(
    artifact: Any,
    *,
    requested_kind: str | None = None,
    allow_invalid_envelope_recovery: bool = False,
) -> tuple[Any, str]:
    """Resolve the concrete payload and render kind for a terminal artifact.

    The renderer and CLI fallback path both use this helper so they stay in
    lockstep when terminal envelopes are malformed but still recoverable.
    """

    envelope_kind_hint = None
    envelope_validated = False
    saw_terminal_artifact_envelope = False
    if isinstance(artifact, Mapping):
        artifact_type = artifact.get("type")
        if isinstance(artifact_type, str) and artifact_type.strip() == _TERMINAL_ARTIFACT_ENVELOPE_TYPE:
            saw_terminal_artifact_envelope = True
            envelope_kind_hint = _normalize_terminal_artifact_envelope_kind(artifact.get("kind"))
            envelope_validated = True

    try:
        artifact, envelope_kind = _unwrap_terminal_artifact_payload(artifact)
    except ValueError:
        envelope_validated = False
        if not allow_invalid_envelope_recovery and envelope_kind_hint is not None:
            raise
        recovered = _recover_terminal_artifact_payload_from_invalid_envelope(
            artifact,
            requested_kind=requested_kind,
            envelope_kind_hint=envelope_kind_hint,
            allow_invalid_metadata=allow_invalid_envelope_recovery,
        )
        if recovered is None:
            raise
        artifact, envelope_kind = recovered

    typed_kind = _infer_terminal_artifact_explicit_kind(artifact)
    kind = requested_kind
    if envelope_kind is not None:
        if (
            requested_kind is not None
            and requested_kind != envelope_kind
            and not allow_invalid_envelope_recovery
        ):
            raise ValueError("kind does not match TerminalArtifact envelope")
        kind = envelope_kind
    elif typed_kind in {"action", "selection"}:
        if requested_kind == "card":
            _validate_terminal_artifact_card_payload(artifact)
        kind = typed_kind
    elif typed_kind == "card":
        # Preserve typed card payloads as cards even if a caller passes a
        # conflicting action/selection hint.
        kind = "card"
    elif requested_kind is not None:
        kind = requested_kind
    if allow_invalid_envelope_recovery and typed_kind is None and kind == "card" and requested_kind != "card":
        if not _should_preserve_raw_leaf_card_default(artifact):
            # Only promote structured leaf payloads during malformed-envelope
            # recovery. Ambiguous raw-leaf cards should remain cards so the
            # generic renderer stays aligned with the explicit CLI fallback.
            recovered_kind = _recover_terminal_artifact_leaf_kind(artifact)
            if recovered_kind is not None:
                kind = recovered_kind

    resolved_kind = _normalize_terminal_artifact_kind(artifact, kind=kind)
    if requested_kind is None and resolved_kind == "card" and not envelope_validated:
        # Preserve explicit action/selection hints even when the payload is not
        # wrapped in a malformed envelope, so partial leaf artifacts do not get
        # flattened into the card default.
        recovered_partial_kind = _infer_terminal_artifact_partial_leaf_kind(artifact)
        if recovered_partial_kind is not None:
            resolved_kind = recovered_partial_kind
    if allow_invalid_envelope_recovery and requested_kind is None and resolved_kind == "card":
        if saw_terminal_artifact_envelope:
            if envelope_kind_hint is None:
                # Malformed envelopes with an unusable kind stay on the card
                # path so explicit kind errors do not get reinterpreted as a
                # structured leaf recovery.
                return artifact, "card"
            # Card envelopes with invalid metadata may still wrap a concrete
            # action or selection leaf, so recover the leaf kind before
            # falling back to the generic card render.
            recovered_leaf_kind = _recover_terminal_artifact_leaf_kind(artifact)
            if recovered_leaf_kind is not None:
                resolved_kind = recovered_leaf_kind
        else:
            # Raw leaf payloads can still be recovered in fallback mode when
            # the resolver is called directly, but the shell keeps the
            # explicit raw-leaf card-default shortcut before this entrypoint.
            recovered_leaf_kind = _recover_terminal_artifact_leaf_kind(artifact)
            if recovered_leaf_kind is not None:
                resolved_kind = recovered_leaf_kind
    return artifact, resolved_kind


def render_terminal_artifact(artifact: Any, *, kind: str | None = None) -> str:
    """Render a structured A2UI artifact through the terminal fallback path.

    Raw card dictionaries remain the default because they are the common CLI
    payload shape. Callers that already know the artifact kind can pass
    ``kind="action"`` or ``kind="selection"`` to render those payloads
    without ambiguity. A typed ``TerminalArtifact`` envelope with ``kind`` and
    ``artifact`` fields is also accepted so engine payloads can stay explicit
    without forcing heuristic kind detection.
    """

    requested_kind = None
    if kind is not None:
        requested_kind = _normalize_terminal_artifact_kind(artifact, kind=kind)
    if requested_kind is None and _should_preserve_raw_leaf_card_default(artifact):
        try:
            return render_terminal_card(artifact)
        except Exception:
            return _render_invalid_terminal_card(artifact)
    malformed_envelope = _is_malformed_terminal_artifact_envelope(artifact)
    allow_invalid_envelope_recovery = malformed_envelope
    if requested_kind == "card" and malformed_envelope:
        payload = artifact.get("artifact") if isinstance(artifact, Mapping) else None
        payload_kind = _infer_terminal_artifact_explicit_kind(payload)
        if payload_kind not in _TERMINAL_ARTIFACT_NON_CARD_KIND_SET:
            payload_kind = _recover_terminal_artifact_leaf_kind(payload)
        if payload_kind in _TERMINAL_ARTIFACT_NON_CARD_KIND_SET:
            return _render_invalid_terminal_card(artifact)
    artifact, resolved_kind = _resolve_terminal_artifact_render_target(
        artifact,
        requested_kind=requested_kind,
        allow_invalid_envelope_recovery=allow_invalid_envelope_recovery,
    )
    if resolved_kind == "action":
        return render_terminal_action(artifact)
    if resolved_kind == "selection":
        return render_terminal_selection(artifact)
    if requested_kind != "card":
        _validate_terminal_artifact_card_payload(artifact)
    return render_terminal_card(artifact)


def render_terminal_cli_fallback(artifact: Any, *, kind: str | None = None) -> str:
    """Render a structured A2UI artifact through the explicit CLI fallback entrypoint.

    The CLI fallback path stays independent from the generic artifact renderer
    so terminal recovery can still work if the main dispatch path is broken.
    Invalid kind hints are treated as absent so the fallback entrypoint stays
    resilient when upstream callers drift.
    """

    requested_kind = None
    if kind is not None:
        try:
            requested_kind = _normalize_terminal_artifact_kind(artifact, kind=kind)
        except ValueError:
            requested_kind = None
    fallback_target: tuple[Any, str] | None = None
    try:
        fallback_target = resolve_terminal_artifact_cli_fallback_target(
            artifact,
            kind=kind,
        )
    except Exception:
        # Keep the explicit CLI fallback path usable even if the shared
        # resolver breaks by retrying the local target resolver before giving
        # up. This preserves action/selection recovery for demo flows.
        fallback_target = None
    else:
        if requested_kind == "card" and fallback_target[1] in _TERMINAL_ARTIFACT_NON_CARD_KIND_SET:
            return _render_invalid_terminal_card(artifact)

    malformed_envelope = _is_malformed_terminal_artifact_envelope(artifact)
    if requested_kind == "card" and malformed_envelope:
        payload = artifact.get("artifact") if isinstance(artifact, Mapping) else None
        payload_kind = _infer_terminal_artifact_explicit_kind(payload)
        if payload_kind not in _TERMINAL_ARTIFACT_NON_CARD_KIND_SET:
            payload_kind = _recover_terminal_artifact_leaf_kind(payload)
        if payload_kind in _TERMINAL_ARTIFACT_NON_CARD_KIND_SET:
            return _render_invalid_terminal_card(artifact)
    if fallback_target is None:
        # Keep the explicit CLI fallback path usable even if the shared
        # resolver breaks by retrying the local target resolver before giving
        # up. This preserves action/selection recovery for demo flows.
        if _should_preserve_raw_leaf_card_default(artifact):
            fallback_artifact, fallback_kind = artifact, "card"
        else:
            try:
                fallback_artifact, fallback_kind = _resolve_terminal_artifact_render_target(
                    artifact,
                    requested_kind=requested_kind,
                    allow_invalid_envelope_recovery=True,
                )
            except Exception:
                return _render_terminal_artifact_cli_fallback_failure(artifact, requested_kind=requested_kind)
    else:
        fallback_artifact, fallback_kind = fallback_target
    try:
        return _render_terminal_artifact_resolved(
            fallback_artifact,
            fallback_kind,
            requested_kind=requested_kind,
        )
    except Exception:
        return _render_terminal_artifact_cli_fallback_failure(artifact, requested_kind=requested_kind)


render_terminal_a2ui = render_terminal_artifact


def resolve_terminal_artifact_render_target(
    artifact: Any,
    *,
    requested_kind: str | None = None,
    allow_invalid_envelope_recovery: bool = False,
) -> tuple[Any, str]:
    """Resolve the concrete payload and render kind for a terminal artifact."""

    return _resolve_terminal_artifact_render_target(
        artifact,
        requested_kind=requested_kind,
        allow_invalid_envelope_recovery=allow_invalid_envelope_recovery,
    )


def resolve_terminal_artifact_cli_fallback_target(
    artifact: Any,
    *,
    kind: str | None = None,
) -> tuple[Any, str]:
    """Resolve the payload and render kind for the explicit CLI fallback path.

    Raw leaf card defaults stay on the card path when no valid kind hint is
    present, so the shell and CLI fallback can share the same target-selection
    contract without duplicating heuristics. If the shared render-target
    resolver fails on a malformed envelope, recover a nested leaf payload
    before falling back to the card default.
    """

    requested_kind = None
    if kind is not None:
        try:
            requested_kind = _normalize_terminal_artifact_kind(artifact, kind=kind)
        except ValueError:
            requested_kind = None
    if requested_kind is None and _should_preserve_raw_leaf_card_default(artifact):
        return artifact, "card"
    if requested_kind is None and isinstance(artifact, Mapping):
        artifact_type = artifact.get("type")
        if isinstance(artifact_type, str) and artifact_type.strip() == _TERMINAL_ARTIFACT_ENVELOPE_TYPE:
            if _normalize_terminal_artifact_envelope_kind(artifact.get("kind")) is None:
                payload = artifact.get("artifact")
                if _should_preserve_raw_leaf_card_default(payload):
                    # The explicit CLI fallback path should keep ambiguous raw
                    # leaves on the card default when the envelope kind is unusable.
                    return payload, "card"

    try:
        return _resolve_terminal_artifact_render_target(
            artifact,
            requested_kind=requested_kind,
            allow_invalid_envelope_recovery=True,
        )
    except Exception:
        if requested_kind is None and isinstance(artifact, Mapping):
            artifact_type = artifact.get("type")
            if isinstance(artifact_type, str) and artifact_type.strip() == _TERMINAL_ARTIFACT_ENVELOPE_TYPE:
                recovered = _recover_terminal_artifact_payload_from_invalid_envelope(
                    artifact,
                    requested_kind=requested_kind,
                    envelope_kind_hint=_normalize_terminal_artifact_envelope_kind(artifact.get("kind")),
                    allow_invalid_metadata=True,
                )
                if recovered is not None:
                    recovered_artifact, recovered_kind = recovered
                    while recovered_kind == "card" and isinstance(recovered_artifact, Mapping):
                        nested_recovered = _recover_terminal_artifact_payload_from_invalid_envelope(
                            recovered_artifact,
                            requested_kind=None,
                            envelope_kind_hint=_normalize_terminal_artifact_envelope_kind(
                                recovered_artifact.get("kind")
                            ),
                            allow_invalid_metadata=True,
                        )
                        if nested_recovered is None:
                            break
                        if nested_recovered == (recovered_artifact, recovered_kind):
                            break
                        recovered_artifact, recovered_kind = nested_recovered
                    return recovered_artifact, recovered_kind
        fallback_kind = requested_kind
        if fallback_kind is None:
            fallback_kind = _infer_terminal_artifact_explicit_kind(artifact)
        if fallback_kind is None and isinstance(artifact, Mapping):
            fallback_kind = _infer_terminal_artifact_partial_leaf_kind(artifact)
        if fallback_kind is None:
            fallback_kind = "card"
        return artifact, fallback_kind


def _render_terminal_artifact_resolved(
    artifact: Any,
    resolved_kind: str,
    *,
    requested_kind: str | None = None,
) -> str:
    if resolved_kind == "action":
        try:
            return render_terminal_action(artifact)
        except Exception:
            return _render_invalid_terminal_action(artifact)
    if resolved_kind == "selection":
        try:
            return render_terminal_selection(artifact)
        except Exception:
            return _render_invalid_terminal_selection(artifact)
    if requested_kind != "card":
        _validate_terminal_artifact_card_payload(artifact)
    try:
        return render_terminal_card(artifact)
    except Exception:
        return _render_invalid_terminal_card(artifact)


def _render_terminal_artifact_cli_fallback_failure(
    artifact: Any,
    *,
    requested_kind: str | None,
) -> str:
    if _should_preserve_raw_leaf_card_default(artifact):
        try:
            return render_terminal_card(artifact)
        except Exception:
            return _render_invalid_terminal_card(artifact)
    fallback_kind = requested_kind
    if fallback_kind is None:
        fallback_kind = _infer_terminal_artifact_explicit_kind(artifact)
    if fallback_kind is None and isinstance(artifact, Mapping):
        fallback_kind = _infer_terminal_artifact_partial_leaf_kind(artifact)
    if fallback_kind == "action":
        try:
            return render_terminal_action(artifact)
        except Exception:
            return _render_invalid_terminal_action(artifact)
    if fallback_kind == "selection":
        try:
            return render_terminal_selection(artifact)
        except Exception:
            return _render_invalid_terminal_selection(artifact)
    try:
        if fallback_kind != "card":
            _validate_terminal_artifact_card_payload(artifact)
        return render_terminal_card(artifact)
    except Exception:
        return _render_invalid_terminal_card(artifact)


def _resolve_terminal_artifact_card_fallback(
    artifact: Any,
    *,
    _seen_envelope_ids: set[int] | None = None,
) -> dict[str, Any] | None:
    if not isinstance(artifact, Mapping):
        return None
    artifact_type = artifact.get("type")
    if not isinstance(artifact_type, str) or artifact_type.strip() != _TERMINAL_ARTIFACT_ENVELOPE_TYPE:
        return None

    if _seen_envelope_ids is None:
        _seen_envelope_ids = set()
    artifact_id = id(artifact)
    if artifact_id in _seen_envelope_ids:
        return None
    _seen_envelope_ids.add(artifact_id)

    payload = artifact.get("artifact")
    if isinstance(payload, Mapping):
        payload_type = payload.get("type")
        if isinstance(payload_type, str) and payload_type.strip() == _TERMINAL_ARTIFACT_ENVELOPE_TYPE:
            recovered_card = _resolve_terminal_artifact_card_fallback(
                payload,
                _seen_envelope_ids=_seen_envelope_ids,
            )
            if recovered_card is not None:
                return recovered_card
        card_payload = _coerce_terminal_card(payload)
        if card_payload is None:
            return None
        if _infer_terminal_artifact_kind_from_mapping(card_payload) in {"action", "selection"}:
            return None
        return card_payload
    return None


def _render_invalid_terminal_selection(selection: Any) -> str:
    selection = _prepare_terminal_artifact_invalid_preview(selection, expected_kind="selection")
    lines = [
        "[SelectionRef] <invalid selection>",
        f"Selection schema v{SELECTION_SCHEMA_VERSION}",
        f"- raw: {_render_payload_preview(selection, max_payload_bytes=256)}",
    ]
    return "\n".join(lines)


def _render_invalid_terminal_action(action: Any) -> str:
    action = _prepare_terminal_artifact_invalid_preview(action, expected_kind="action")
    lines = [
        "[ActionRef] <invalid action>",
        f"Action schema v{A2UI_ACTION_SCHEMA_VERSION}",
        f"- raw: {_render_payload_preview(action, max_payload_bytes=256)}",
    ]
    return "\n".join(lines)


def _prepare_terminal_artifact_invalid_preview(artifact: Any, *, expected_kind: str) -> Any:
    """Return a preview-safe snapshot for invalid leaf renders.

    Invalid action and selection renders should avoid echoing recoverable
    terminal-envelope wrappers so the raw preview stays focused on the leaf
    payload that actually failed validation.
    """

    if isinstance(artifact, ActionRef):
        artifact = _action_ref_to_dict(artifact)
    elif isinstance(artifact, SelectionRef):
        artifact = _selection_ref_to_dict(artifact)
    if not isinstance(artifact, Mapping):
        return artifact

    expected_type = "ActionRef" if expected_kind == "action" else "SelectionRef"
    artifact = _strip_terminal_type_hint(artifact, expected_type=expected_type)
    recovered = _recover_terminal_artifact_payload_from_invalid_envelope(
        artifact,
        requested_kind=expected_kind,
        allow_invalid_metadata=True,
    )
    if recovered is not None:
        artifact, _ = recovered
        return artifact
    return artifact


def _normalize_terminal_artifact_kind(artifact: Any, *, kind: str | None) -> str:
    if kind is None:
        if isinstance(artifact, ActionRef):
            return "action"
        if isinstance(artifact, SelectionRef):
            return "selection"
        if isinstance(artifact, Mapping):
            inferred_kind = _infer_terminal_artifact_kind_from_mapping(artifact)
            if inferred_kind is not None:
                return inferred_kind
        return "card"

    if not isinstance(kind, str):
        raise ValueError("kind must be a string")
    normalized_kind = kind.strip().lower()
    if normalized_kind not in _TERMINAL_ARTIFACT_SUPPORTED_KIND_SET:
        raise ValueError("kind must be one of: card, action, selection")
    return normalized_kind


def _extract_terminal_artifact_envelope(artifact: Any) -> tuple[Any, str] | None:
    if not isinstance(artifact, Mapping):
        return None
    artifact_type = artifact.get("type")
    if not isinstance(artifact_type, str) or artifact_type.strip() != _TERMINAL_ARTIFACT_ENVELOPE_TYPE:
        return None
    validate_terminal_artifact_envelope(artifact)
    kind = artifact["kind"]
    normalized_kind = kind.strip().lower()
    payload = artifact["artifact"]
    return payload, normalized_kind


def _unwrap_terminal_artifact_payload(
    artifact: Any,
    *,
    _seen_envelope_ids: set[int] | None = None,
) -> tuple[Any, str | None]:
    """Peel nested TerminalArtifact envelopes down to the concrete payload."""

    if not isinstance(artifact, Mapping):
        return artifact, None
    artifact_type = artifact.get("type")
    if not isinstance(artifact_type, str) or artifact_type.strip() != _TERMINAL_ARTIFACT_ENVELOPE_TYPE:
        return artifact, None

    if _seen_envelope_ids is None:
        _seen_envelope_ids = set()
    artifact_id = id(artifact)
    if artifact_id in _seen_envelope_ids:
        raise ValueError("TerminalArtifact envelope cycle detected")
    _seen_envelope_ids.add(artifact_id)

    payload = artifact.get("artifact")
    if isinstance(payload, Mapping):
        payload_type = payload.get("type")
        if isinstance(payload_type, str) and payload_type.strip() == _TERMINAL_ARTIFACT_ENVELOPE_TYPE:
            return _unwrap_terminal_artifact_payload(payload, _seen_envelope_ids=_seen_envelope_ids)

    validate_terminal_artifact_envelope(artifact)
    kind = artifact["kind"]
    normalized_kind = kind.strip().lower()
    return payload, normalized_kind


def _recover_terminal_artifact_payload_from_invalid_envelope(
    artifact: Any,
    *,
    requested_kind: str | None,
    envelope_kind_hint: str | None = None,
    allow_invalid_metadata: bool = False,
    _seen_envelope_ids: set[int] | None = None,
) -> tuple[Any, str] | None:
    """Recover a render target from an otherwise-shaped TerminalArtifact envelope."""

    if not isinstance(artifact, Mapping):
        return None
    artifact_type = artifact.get("type")
    if not isinstance(artifact_type, str) or artifact_type.strip() != _TERMINAL_ARTIFACT_ENVELOPE_TYPE:
        return None
    if not allow_invalid_metadata:
        extra_keys = set(artifact) - {"type", "kind", "artifact", "contract_version", "a2ui_version"}
        if extra_keys:
            return None
        contract_version = artifact.get("contract_version")
        if contract_version is not None and (
            type(contract_version) is not int or contract_version != A2UI_CONTRACT_VERSION
        ):
            return None
        a2ui_version = artifact.get("a2ui_version")
        if a2ui_version is not None and (type(a2ui_version) is not int or a2ui_version != A2UI_VERSION):
            return None
    if "artifact" not in artifact or artifact.get("artifact") is None:
        return None

    if _seen_envelope_ids is None:
        _seen_envelope_ids = set()
    artifact_id = id(artifact)
    if artifact_id in _seen_envelope_ids:
        return None
    _seen_envelope_ids.add(artifact_id)

    payload = artifact.get("artifact")
    if isinstance(payload, Mapping):
        payload_type = payload.get("type")
        if isinstance(payload_type, str) and payload_type.strip() == _TERMINAL_ARTIFACT_ENVELOPE_TYPE:
            recovered = _recover_terminal_artifact_payload_from_invalid_envelope(
                payload,
                requested_kind=requested_kind,
                _seen_envelope_ids=_seen_envelope_ids,
            )
            if recovered is not None:
                return recovered

    payload_kind = _infer_terminal_artifact_explicit_kind(payload)
    if payload_kind is not None:
        return payload, payload_kind
    if requested_kind == "card":
        return payload, "card"
    if envelope_kind_hint in {"action", "selection"}:
        return payload, envelope_kind_hint
    if requested_kind in {"action", "selection"}:
        return payload, requested_kind
    if isinstance(payload, Mapping) or _coerce_terminal_card(payload) is not None:
        return payload, "card"
    return None


def _normalize_terminal_artifact_envelope_kind(kind: Any) -> str | None:
    if not isinstance(kind, str):
        return None
    normalized_kind = kind.strip().lower()
    if normalized_kind in _TERMINAL_ARTIFACT_SUPPORTED_KIND_SET:
        return normalized_kind
    return None


def _is_malformed_terminal_artifact_envelope(artifact: Any) -> bool:
    if not isinstance(artifact, Mapping):
        return False
    artifact_type = artifact.get("type")
    if not isinstance(artifact_type, str) or artifact_type.strip() != _TERMINAL_ARTIFACT_ENVELOPE_TYPE:
        return False
    try:
        validate_terminal_artifact_envelope(artifact)
    except ValueError:
        return True
    return False


def _unwrap_terminal_artifact_leaf_payload(artifact: Any, *, expected_kind: str) -> Any:
    if not isinstance(artifact, Mapping):
        return artifact
    artifact_type = artifact.get("type")
    if not isinstance(artifact_type, str) or artifact_type.strip() != _TERMINAL_ARTIFACT_ENVELOPE_TYPE:
        return artifact
    try:
        payload, envelope_kind = _unwrap_terminal_artifact_payload(artifact)
    except ValueError:
        return artifact
    if envelope_kind == expected_kind:
        return payload
    return artifact


def _infer_terminal_artifact_kind_from_mapping(artifact: Mapping[str, Any]) -> str | None:
    artifact_type = artifact.get("type")
    if isinstance(artifact_type, str):
        normalized_type = artifact_type.strip()
        if normalized_type == "ActionRef":
            return "action"
        if normalized_type == "SelectionRef":
            return "selection"
        if normalized_type and normalized_type != _TERMINAL_ARTIFACT_ENVELOPE_TYPE:
            return "card"

    if (not isinstance(artifact_type, str) or not artifact_type.strip()) and any(
        field in artifact for field in ("blocks", "actions")
    ):
        # Untyped card-shaped payloads should stay on the card path even if
        # they carry stray action/selection-style fields.
        return "card"

    has_required_fields = all(field in artifact for field in ("id", "label", "payload"))
    if not has_required_fields:
        return None

    has_action_hints = any(field in artifact for field in ("confirm", "policy_sensitive"))
    has_selection_hints = any(field in artifact for field in ("selected", "disabled"))
    if has_action_hints and not has_selection_hints:
        return "action"
    if has_selection_hints and not has_action_hints:
        return "selection"
    return None


def _infer_terminal_artifact_explicit_kind(artifact: Any) -> str | None:
    if isinstance(artifact, ActionRef):
        return "action"
    if isinstance(artifact, SelectionRef):
        return "selection"
    if isinstance(artifact, Mapping):
        artifact_type = artifact.get("type")
        if isinstance(artifact_type, str):
            normalized_type = artifact_type.strip()
            if normalized_type == "ActionRef":
                return "action"
            if normalized_type == "SelectionRef":
                return "selection"
            if normalized_type and normalized_type != _TERMINAL_ARTIFACT_ENVELOPE_TYPE:
                return "card"
        return _infer_terminal_artifact_kind_from_mapping(artifact)
    return None


def _recover_terminal_artifact_leaf_kind(artifact: Any) -> str | None:
    """Recover the most specific leaf kind from a schema-valid payload."""

    try:
        normalize_action_ref(artifact)
    except Exception:
        try:
            normalize_selection_ref(artifact)
        except Exception:
            return None
        return "selection"
    return "action"


def _infer_terminal_artifact_partial_leaf_kind(artifact: Any) -> str | None:
    """Infer a leaf kind from a partial payload that still carries action hints."""

    if not isinstance(artifact, Mapping):
        return None

    artifact_type = artifact.get("type")
    if isinstance(artifact_type, str):
        normalized_type = artifact_type.strip()
        if normalized_type == "ActionRef":
            return "action"
        if normalized_type == "SelectionRef":
            return "selection"
        if normalized_type and normalized_type != _TERMINAL_ARTIFACT_ENVELOPE_TYPE:
            return None

    if any(field in artifact for field in ("blocks", "actions")):
        return None
    if not all(field in artifact for field in ("id", "payload")):
        return None

    has_action_hints = any(field in artifact for field in ("confirm", "policy_sensitive"))
    has_selection_hints = any(field in artifact for field in ("selected", "disabled"))
    if has_action_hints and not has_selection_hints:
        return "action"
    if has_selection_hints and not has_action_hints:
        return "selection"
    return None


def _should_preserve_raw_leaf_card_default(artifact: Any) -> bool:
    """Return True when an untyped raw leaf should stay on the card path."""

    if isinstance(artifact, (ActionRef, SelectionRef)):
        return False
    if not isinstance(artifact, Mapping):
        return False

    artifact_type = artifact.get("type")
    if isinstance(artifact_type, str) and artifact_type.strip():
        return False
    if any(field in artifact for field in ("confirm", "policy_sensitive", "selected", "disabled")):
        return False
    if any(field in artifact for field in ("blocks", "actions")):
        return False
    return all(field in artifact for field in ("id", "label", "payload"))


def _strip_terminal_type_hint(artifact: Mapping[str, Any], *, expected_type: str) -> dict[str, Any]:
    artifact_type = artifact.get("type")
    if not isinstance(artifact_type, str) or artifact_type.strip() != expected_type:
        return dict(artifact)

    stripped = dict(artifact)
    stripped.pop("type", None)
    return stripped


def _filter_card_actions(card: dict[str, Any], capabilities: A2UICapabilities) -> dict[str, Any]:
    filtered = _filter_supported_actions(card.get("actions"), supported_actions=set(capabilities.actions_supported))
    out = dict(card)
    out["actions"] = filtered
    return out


def _filter_read_only_fallback_actions(
    raw_card: dict[str, Any],
    *,
    supported_actions: set[str],
    max_payload_bytes: int,
) -> list[dict[str, Any]]:
    """Return the canonical copy action for a read-only fallback card."""

    if FALLBACK_COPY_ACTION_ID not in supported_actions:
        return []
    return [
        _build_copy_to_clipboard_action(
            _render_payload_preview(raw_card, max_payload_bytes=max_payload_bytes, pretty=True),
        )
    ]


def _build_unknown_card_actions(
    raw_card: dict[str, Any],
    *,
    supported_actions: tuple[str, ...] | set[str] | None,
    max_payload_bytes: int,
) -> list[dict[str, Any]]:
    if isinstance(supported_actions, set):
        canonical_supported_actions = supported_actions
    else:
        canonical_supported_actions = _canonicalize_supported_actions(supported_actions)
    return _filter_read_only_fallback_actions(
        raw_card,
        supported_actions=canonical_supported_actions,
        max_payload_bytes=max_payload_bytes,
    )


def _build_read_only_fallback_actions(
    raw_card: dict[str, Any],
    *,
    supported_actions: set[str],
    max_payload_bytes: int,
) -> list[dict[str, Any]]:
    return _filter_read_only_fallback_actions(
        raw_card,
        supported_actions=supported_actions,
        max_payload_bytes=max_payload_bytes,
    )


def _filter_supported_actions(actions: Any, *, supported_actions: set[str]) -> list[dict[str, Any]]:
    if not isinstance(actions, (list, tuple)):
        return []
    filtered: list[dict[str, Any]] = []
    seen: set[str] = set()
    for action in actions:
        try:
            normalized = _normalize_action(action, supported_actions=supported_actions)
        except ValueError:
            continue
        action_key = _canonical_json(normalized)
        if action_key in seen:
            continue
        seen.add(action_key)
        filtered.append(normalized)
    # Keep tuple-shaped or reordered action containers deterministic once
    # they are materialized back into the canonical list form.
    return sorted(filtered, key=_canonical_json)


def _validate_canonical_read_only_fallback_actions(
    actions: list[Any] | tuple[Any, ...],
) -> None:
    seen_actions: set[str] = set()
    for action in actions:
        validate_action_ref(action)
        action_dict = _action_ref_to_dict(action)
        if action_dict.get("id") != FALLBACK_COPY_ACTION_ID:
            raise ValueError("Fallback card actions must be copy_to_clipboard only")
        if action_dict.get("label") != "Copy JSON":
            raise ValueError("Fallback card actions must use the canonical Copy JSON label")
        if "confirm" in action_dict:
            raise ValueError("Fallback card actions must not require confirmation")
        if action_dict.get("policy_sensitive") is True:
            raise ValueError("Fallback card actions must not be policy-sensitive")
        payload = action_dict.get("payload")
        if not isinstance(payload, Mapping) or set(payload) != {"text"}:
            raise ValueError("Fallback card actions must use the canonical clipboard payload")
        if not isinstance(payload.get("text"), str):
            raise ValueError("Fallback card actions must use a string clipboard payload")
        action_key = _canonical_json(action_dict)
        if action_key in seen_actions:
            raise ValueError("Fallback card actions must not contain duplicates")
        seen_actions.add(action_key)


def _is_canonical_read_only_fallback_actions(actions: Any) -> bool:
    if actions is None:
        return True
    if not isinstance(actions, (list, tuple)):
        return False
    if not actions:
        return True
    try:
        _validate_canonical_read_only_fallback_actions(actions)
    except ValueError:
        return False
    return True


def _materialize_versioned_card(card: dict[str, Any], capabilities: A2UICapabilities) -> dict[str, Any]:
    out = _canonicalize_card_top_level_fields(card)
    out["blocks"] = _extract_safe_primitive_blocks(out)
    out = _filter_card_actions(out, capabilities)
    out["title"] = _normalize_card_text(out.get("title"), fallback="<untitled>")
    subtitle = _normalize_card_text(out.get("subtitle"))
    if subtitle is None:
        out.pop("subtitle", None)
    else:
        out["subtitle"] = subtitle
    out["a2ui_version"] = A2UI_VERSION
    return out


def _materialize_generic_card(card: dict[str, Any], capabilities: A2UICapabilities) -> dict[str, Any]:
    _validate_card_version(card)
    out = _canonicalize_card_top_level_fields(card)
    out["blocks"] = _extract_safe_primitive_blocks(out)
    actions = out.get("actions")
    if actions is None:
        out["actions"] = []
    else:
        # Generic cards should keep the safe subset of content instead of
        # aborting on malformed nested payloads.
        out["actions"] = _filter_supported_actions(actions, supported_actions=set(capabilities.actions_supported))
    out["title"] = _normalize_card_text(out.get("title"), fallback="<untitled>")
    subtitle = _normalize_card_text(out.get("subtitle"))
    if subtitle is None:
        out.pop("subtitle", None)
    else:
        out["subtitle"] = subtitle
    out["a2ui_version"] = A2UI_VERSION
    validate_generic_card(out)
    return out


def _materialize_unknown_card(card: dict[str, Any], capabilities: A2UICapabilities) -> dict[str, Any]:
    safe_card = _canonicalize_card_top_level_fields(card)
    source_card_type = _extract_unknown_card_source_type(safe_card)
    preview_card = {
        "type": source_card_type,
        "title": _build_fallback_title(UNKNOWN_CARD_TYPE, source_card_type=source_card_type),
        "subtitle": UNKNOWN_FALLBACK_SUBTITLE,
        "a2ui_version": A2UI_VERSION,
        "debug": _build_fallback_debug(source_card_type, fallback_kind="unknown"),
        "blocks": _extract_safe_primitive_blocks(safe_card, allow_code_block=False),
        "actions": [],
    }
    return build_unknown_card(
        preview_card,
        max_payload_bytes=capabilities.max_payload_bytes,
        supported_actions=set(capabilities.actions_supported),
    )


def _normalize_action(action: ActionRef | Mapping[str, Any], *, supported_actions: set[str]) -> dict[str, Any]:
    action = _action_ref_to_dict(action)
    if not isinstance(action, Mapping):
        raise ValueError("ActionRef must be an object")
    extra_keys = set(action) - {"id", "label", "payload", "confirm", "policy_sensitive"}
    if extra_keys:
        extras = ", ".join(sorted(extra_keys))
        raise ValueError(f"Unexpected action field(s): {extras}")
    action_id = action.get("id")
    if not isinstance(action_id, str):
        raise ValueError("Action id is required")
    action_id = action_id.strip()
    if not action_id:
        raise ValueError("Action id is required")
    if action_id not in supported_actions:
        raise ValueError(f"Unsupported action id: {action_id}")
    label = action.get("label")
    if not isinstance(label, str) or not label.strip():
        raise ValueError("Action label is required")
    payload = action.get("payload")
    if not isinstance(payload, Mapping):
        raise ValueError("Action payload must be an object")
    _validate_action_payload(action_id, payload)

    normalized: dict[str, Any] = {
        "id": action_id,
        "label": label.strip(),
        "payload": _copy_action_payload(payload),
    }
    confirm = action.get("confirm")
    if confirm is not None:
        normalized["confirm"] = _normalize_confirm(confirm)
    policy_sensitive = action.get("policy_sensitive", False)
    if not isinstance(policy_sensitive, bool):
        raise ValueError("Action policy_sensitive must be a bool")
    if policy_sensitive:
        normalized["policy_sensitive"] = True
    return normalized


def _normalize_selection(selection: Any) -> dict[str, Any]:
    if not isinstance(selection, Mapping):
        raise ValueError("SelectionRef must be an object")
    extra_keys = set(selection) - {"id", "label", "payload", "selected", "disabled"}
    if extra_keys:
        extras = ", ".join(sorted(extra_keys))
        raise ValueError(f"Unexpected selection field(s): {extras}")
    selection_id = selection.get("id")
    if not isinstance(selection_id, str):
        raise ValueError("Selection id is required")
    selection_id = selection_id.strip()
    if not selection_id:
        raise ValueError("Selection id is required")
    label = selection.get("label")
    if not isinstance(label, str) or not label.strip():
        raise ValueError("Selection label is required")
    payload = selection.get("payload")
    if not isinstance(payload, Mapping):
        raise ValueError("Selection payload must be an object")

    normalized: dict[str, Any] = {
        "id": selection_id,
        "label": label.strip(),
        "payload": _copy_selection_payload(payload),
    }
    selected = selection.get("selected", False)
    if not isinstance(selected, bool):
        raise ValueError("Selection selected must be a bool")
    if selected:
        normalized["selected"] = True
    disabled = selection.get("disabled", False)
    if not isinstance(disabled, bool):
        raise ValueError("Selection disabled must be a bool")
    if disabled:
        normalized["disabled"] = True
    return normalized


def _selection_ref_to_dict(selection: SelectionRef | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(selection, SelectionRef):
        selection_dict: dict[str, Any] = {
            "id": selection.id,
            "label": selection.label,
            "payload": _copy_selection_payload(selection.payload),
        }
        if selection.selected:
            selection_dict["selected"] = selection.selected
        if selection.disabled:
            selection_dict["disabled"] = selection.disabled
        return selection_dict
    if isinstance(selection, Mapping):
        return dict(selection)
    raise ValueError("SelectionRef must be an object")


def _action_ref_to_dict(action: ActionRef | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(action, ActionRef):
        action_dict: dict[str, Any] = {
            "id": action.id,
            "label": action.label,
            "payload": _copy_action_payload(action.payload),
        }
        if action.confirm is not None:
            action_dict["confirm"] = action.confirm
        if action.policy_sensitive:
            action_dict["policy_sensitive"] = action.policy_sensitive
        return action_dict
    if isinstance(action, Mapping):
        return dict(action)
    raise ValueError("ActionRef must be an object")


def _normalize_confirm(confirm: Any) -> dict[str, str]:
    if not isinstance(confirm, Mapping):
        raise ValueError("Action confirm must be an object")
    title = confirm.get("title")
    message = confirm.get("message")
    if not isinstance(title, str) or not title.strip():
        raise ValueError("Action confirm title is required")
    if not isinstance(message, str) or not message.strip():
        raise ValueError("Action confirm message is required")
    extra_keys = set(confirm) - {"title", "message"}
    if extra_keys:
        extras = ", ".join(sorted(extra_keys))
        raise ValueError(f"Unexpected confirm field(s): {extras}")
    return {"title": title.strip(), "message": message.strip()}


def _copy_selection_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    return _copy_terminal_artifact_payload(payload)


def _copy_action_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    return _copy_terminal_artifact_payload(payload)


def _copy_terminal_artifact_payload(artifact: Any) -> Any:
    """Return an isolated snapshot for a terminal artifact payload.

    The terminal artifact envelope is a public contract boundary. Snapshotting
    the payload keeps engine-produced envelopes deterministic even if the
    original object is mutated after the wrapper is built. Nested A2UI
    dataclasses are converted to plain dictionaries so the snapshot stays
    client-friendly for CLI fallback rendering.
    """

    return _snapshot_terminal_artifact_value(artifact)


def _snapshot_terminal_artifact_value(value: Any, *, _seen_ids: set[int] | None = None) -> Any:
    if _seen_ids is None:
        _seen_ids = set()

    if isinstance(value, ActionRef):
        value_id = id(value)
        if value_id in _seen_ids:
            return f"<cycle:{type(value).__name__}>"
        _seen_ids.add(value_id)
        try:
            return _snapshot_terminal_artifact_value(_action_ref_to_dict(value), _seen_ids=_seen_ids)
        finally:
            _seen_ids.remove(value_id)

    if isinstance(value, SelectionRef):
        value_id = id(value)
        if value_id in _seen_ids:
            return f"<cycle:{type(value).__name__}>"
        _seen_ids.add(value_id)
        try:
            return _snapshot_terminal_artifact_value(_selection_ref_to_dict(value), _seen_ids=_seen_ids)
        finally:
            _seen_ids.remove(value_id)

    if is_dataclass(value) and not isinstance(value, type):
        value_id = id(value)
        if value_id in _seen_ids:
            return f"<cycle:{type(value).__name__}>"
        _seen_ids.add(value_id)
        try:
            try:
                snapshot = {field.name: getattr(value, field.name) for field in fields(value)}
            except Exception:
                try:
                    return copy.deepcopy(value)
                except Exception:
                    return f"<non-json:{type(value).__name__}>"
            return {
                key: _snapshot_terminal_artifact_value(item, _seen_ids=_seen_ids)
                for key, item in snapshot.items()
            }
        finally:
            _seen_ids.remove(value_id)

    if isinstance(value, Mapping):
        value_id = id(value)
        if value_id in _seen_ids:
            return f"<cycle:{type(value).__name__}>"
        _seen_ids.add(value_id)
        try:
            # Canonicalize mappings so engine-produced payload snapshots do not
            # depend on insertion order from the source object.
            return {
                key: _snapshot_terminal_artifact_value(value[key], _seen_ids=_seen_ids)
                for key in sorted(value, key=lambda item: str(item))
            }
        finally:
            _seen_ids.remove(value_id)

    if isinstance(value, list):
        value_id = id(value)
        if value_id in _seen_ids:
            return f"<cycle:{type(value).__name__}>"
        _seen_ids.add(value_id)
        try:
            return [_snapshot_terminal_artifact_value(item, _seen_ids=_seen_ids) for item in value]
        finally:
            _seen_ids.remove(value_id)

    if isinstance(value, tuple):
        value_id = id(value)
        if value_id in _seen_ids:
            return f"<cycle:{type(value).__name__}>"
        _seen_ids.add(value_id)
        try:
            # Normalize tuple-shaped snapshots to JSON-native lists so
            # terminal artifact envelopes stay language-agnostic.
            return [_snapshot_terminal_artifact_value(item, _seen_ids=_seen_ids) for item in value]
        finally:
            _seen_ids.remove(value_id)

    if isinstance(value, Set):
        value_id = id(value)
        if value_id in _seen_ids:
            return f"<cycle:{type(value).__name__}>"
        _seen_ids.add(value_id)
        try:
            # Unordered set-like containers need a deterministic JSON-safe representation.
            normalized_items = [
                _snapshot_terminal_artifact_value(item, _seen_ids=_seen_ids) for item in value
            ]
            return sorted(normalized_items, key=_canonical_json_sort_key)
        finally:
            _seen_ids.remove(value_id)

    try:
        return copy.deepcopy(value)
    except Exception:
        return value


def _validate_action_payload(action_id: str, payload: Mapping[str, Any]) -> None:
    schema = _ACTION_SCHEMAS.get(action_id)
    if schema is None:
        raise ValueError(f"No schema for action id: {action_id}")
    extra_keys = set(payload) - set(schema)
    if extra_keys:
        extras = ", ".join(sorted(extra_keys))
        raise ValueError(f"Unexpected payload field for {action_id}: {extras}")
    for key, value_type in schema.items():
        if key not in payload:
            raise ValueError(f"Missing payload field for {action_id}: {key}")
        if not isinstance(payload[key], value_type):
            raise ValueError(f"Invalid payload type for {action_id}:{key}")


def _validate_primitive_block_fields(block_type: str, block: Mapping[str, Any]) -> None:
    schema_fields = set(_PRIMITIVE_BLOCK_SCHEMAS[block_type])
    required_fields = set(_PRIMITIVE_BLOCK_REQUIRED_FIELDS[block_type])
    extra_keys = set(block) - ({"type"} | schema_fields)
    if extra_keys:
        extras = ", ".join(sorted(extra_keys))
        raise ValueError(f"Unexpected primitive block field(s) for {block_type}: {extras}")
    for field_name in required_fields:
        if field_name not in block:
            raise ValueError(f"Missing primitive block field for {block_type}: {field_name}")
    if block_type == "MarkdownBlock":
        if not isinstance(block["markdown"], str):
            raise ValueError("Invalid primitive block field for MarkdownBlock: markdown")
        return
    if block_type == "KeyValueBlock":
        if not isinstance(block["items"], list):
            raise ValueError("Invalid primitive block field for KeyValueBlock: items")
        return
    if block_type == "ListBlock":
        if not isinstance(block["items"], list):
            raise ValueError("Invalid primitive block field for ListBlock: items")
        return
    if block_type == "TableBlock":
        if not isinstance(block["rows"], list):
            raise ValueError("Invalid primitive block field for TableBlock: rows")
        return
    if block_type == "AlertBlock":
        if not isinstance(block["message"], str):
            raise ValueError("Invalid primitive block field for AlertBlock: message")
        severity = block.get("severity")
        if severity is not None and not isinstance(severity, str):
            raise ValueError("Invalid primitive block field for AlertBlock: severity")
        title = block.get("title")
        if title is not None and not isinstance(title, str):
            raise ValueError("Invalid primitive block field for AlertBlock: title")
        return
    if block_type == "ProgressBlock":
        if not isinstance(block["status_text"], str):
            raise ValueError("Invalid primitive block field for ProgressBlock: status_text")
        title = block.get("title")
        if title is not None and not isinstance(title, str):
            raise ValueError("Invalid primitive block field for ProgressBlock: title")
        return
    if block_type == "CodeBlock":
        if not isinstance(block["code"], str):
            raise ValueError("Invalid primitive block field for CodeBlock: code")
        language = block.get("language")
        if language is not None and not isinstance(language, str):
            raise ValueError("Invalid primitive block field for CodeBlock: language")
        collapsed = block.get("collapsed")
        if collapsed is not None and not isinstance(collapsed, bool):
            raise ValueError("Invalid primitive block field for CodeBlock: collapsed")
        return


def _canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _canonicalize_card_top_level_fields(card: dict[str, Any]) -> dict[str, Any]:
    allowed_keys = ("type", "title", "subtitle", "a2ui_version", "debug", "blocks", "actions")
    return {key: card[key] for key in allowed_keys if key in card}


def _render_payload_preview(
    payload: dict[str, Any],
    *,
    max_payload_bytes: int | None,
    pretty: bool = False,
) -> str:
    sanitized_payload = _sanitize_json_preview_value(payload)
    rendered = json.dumps(
        sanitized_payload,
        indent=2 if pretty else None,
        sort_keys=True,
        separators=None if pretty else (",", ":"),
        ensure_ascii=True,
    )
    if max_payload_bytes is None or len(rendered.encode("utf-8")) <= max_payload_bytes:
        return rendered
    if max_payload_bytes <= 0:
        return ""

    budget = max_payload_bytes
    suffix = f"\n...[truncated to {max_payload_bytes} bytes]" if pretty else f"...[truncated to {max_payload_bytes} bytes]"
    suffix_bytes = len(suffix.encode("utf-8"))
    if suffix_bytes >= budget:
        return suffix[:budget]

    prefix = rendered.encode("utf-8")[: budget - suffix_bytes].decode("utf-8", errors="ignore")
    return f"{prefix}{suffix}"


def _build_copy_to_clipboard_action(text: str) -> dict[str, Any]:
    return _normalize_action(
        {
            "id": FALLBACK_COPY_ACTION_ID,
            "label": "Copy JSON",
            "payload": {"text": text},
        },
        supported_actions={FALLBACK_COPY_ACTION_ID},
    )


def _sanitize_json_preview_value(value: Any, *, _seen_ids: set[int] | None = None) -> Any:
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if _seen_ids is None:
        _seen_ids = set()

    value_id = id(value)
    if value_id in _seen_ids:
        return f"<cycle:{type(value).__name__}>"

    if isinstance(value, Mapping):
        _seen_ids.add(value_id)
        try:
            sanitized_items = [
                (str(key), _sanitize_json_preview_value(value[key], _seen_ids=_seen_ids))
                for key in sorted(value, key=lambda item: str(item))
            ]
            return {key: sanitized_value for key, sanitized_value in sanitized_items}
        finally:
            _seen_ids.remove(value_id)

    if isinstance(value, list):
        _seen_ids.add(value_id)
        try:
            return [_sanitize_json_preview_value(item, _seen_ids=_seen_ids) for item in value]
        finally:
            _seen_ids.remove(value_id)

    if isinstance(value, tuple):
        _seen_ids.add(value_id)
        try:
            return [_sanitize_json_preview_value(item, _seen_ids=_seen_ids) for item in value]
        finally:
            _seen_ids.remove(value_id)

    if isinstance(value, Set):
        _seen_ids.add(value_id)
        try:
            sanitized_items = [_sanitize_json_preview_value(item, _seen_ids=_seen_ids) for item in value]
            return sorted(sanitized_items, key=_canonical_json_sort_key)
        finally:
            _seen_ids.remove(value_id)

    return f"<non-json:{type(value).__name__}>"


def _is_safe_scalar_value(value: Any) -> bool:
    return value is None or isinstance(value, (bool, int, float, str))


def _canonical_json_sort_key(value: Any) -> str:
    if isinstance(value, Mapping):
        return _canonical_json({str(key): value[key] for key in sorted(value, key=lambda item: str(item))})
    if isinstance(value, list):
        return _canonical_json({"items": value})
    return str(value)


def _render_terminal_actions(actions: Any, *, supported_actions: set[str]) -> list[str]:
    normalized_actions = _canonicalize_supported_action_list(actions, supported_actions=supported_actions)
    normalized_actions = sorted(normalized_actions, key=_canonical_json)

    identity_counts: dict[str, int] = {}
    for action in normalized_actions:
        identity_key = _canonical_json(
            {
                "id": _render_terminal_inline_text(action["id"]),
                "label": _render_terminal_inline_text(action["label"]),
            }
        )
        identity_counts[identity_key] = identity_counts.get(identity_key, 0) + 1

    lines: list[str] = []
    for action in normalized_actions:
        label = _render_terminal_inline_text(action["label"])
        action_id = _render_terminal_inline_text(action["id"])
        identity_key = _canonical_json({"id": action_id, "label": label})
        if identity_counts.get(identity_key, 0) > 1:
            payload_preview = _render_payload_preview(action["payload"], max_payload_bytes=96)
            lines.append(
                f"- {label} ({action_id}{_render_action_variant_suffix(action)}; payload: {payload_preview})"
            )
            continue
        lines.append(f"- {label} ({action_id}{_render_action_variant_suffix(action)})")
    return lines


def _render_action_variant_suffix(action: dict[str, Any]) -> str:
    suffix_parts: list[str] = []
    confirm = action.get("confirm")
    if isinstance(confirm, Mapping):
        confirm_title = confirm.get("title")
        if isinstance(confirm_title, str) and confirm_title.strip():
            suffix_parts.append(f"confirm: {_render_terminal_inline_text(confirm_title.strip())}")
        else:
            suffix_parts.append("confirm")
    if action.get("policy_sensitive") is True:
        suffix_parts.append("policy-sensitive")
    if not suffix_parts:
        return ""
    return "; " + "; ".join(suffix_parts)


def _render_terminal_debug(debug: Any) -> list[str]:
    if not isinstance(debug, Mapping):
        return []
    lines: list[str] = []
    for key in sorted(debug):
        value = debug[key]
        if isinstance(value, bool):
            rendered_value = "true" if value else "false"
        elif isinstance(value, (str, int)):
            rendered_value = _render_terminal_inline_text(value)
        else:
            continue
        lines.append(f"- {key}: {rendered_value}")
    return lines


def _render_terminal_fallback_debug(
    card_type: str,
    title: str,
    debug: Any,
    *,
    generic_fallback_source: str | None = None,
) -> list[str]:
    fallback_debug = _extract_terminal_fallback_debug(debug)
    if fallback_debug is None:
        if card_type == UNKNOWN_CARD_TYPE:
            source_card_type = _infer_unknown_fallback_source(title)
            fallback_kind = "unknown"
        elif card_type == GENERIC_CARD_TYPE:
            source_card_type = generic_fallback_source
            fallback_kind = "generic"
        else:
            return []
        if source_card_type is None:
            return []
    else:
        fallback_kind, source_card_type = fallback_debug

    lines: list[str] = []
    contract_version = None
    if isinstance(debug, Mapping):
        contract_version = debug.get("contract_version")
    if type(contract_version) is not int:
        contract_version = A2UI_CONTRACT_VERSION
    lines.append(f"- contract_version: {contract_version}")
    lines.append(f"- fallback_kind: {_render_terminal_inline_text(fallback_kind)}")
    lines.append(f"- source_card_type: {_render_terminal_inline_text(source_card_type)}")
    return lines


def _render_terminal_fallback_notice(
    card_type: str,
    title: str,
    *,
    debug: Any,
    generic_fallback_source: str | None = None,
    generic_fallback_hint: bool = False,
) -> list[str]:
    fallback_debug = _extract_terminal_fallback_debug(debug)
    if fallback_debug is not None:
        fallback_kind, source_card_type = fallback_debug
        return [
            f"Fallback: {_render_terminal_inline_text(fallback_kind)} from {_render_terminal_inline_text(source_card_type)}"
        ]
    if card_type == UNKNOWN_CARD_TYPE:
        source_card_type = _infer_unknown_fallback_source(title)
        if source_card_type is not None:
            return [f"Fallback: unknown from {_render_terminal_inline_text(source_card_type)}"]
        return ["Fallback: unknown card"]
    if card_type == GENERIC_CARD_TYPE:
        if generic_fallback_source is not None:
            return [f"Fallback: generic from {_render_terminal_inline_text(generic_fallback_source)}"]
        if generic_fallback_hint:
            return ["Fallback: generic card"]
    return []


def _extract_terminal_fallback_debug(debug: Any) -> tuple[str, str] | None:
    if not isinstance(debug, Mapping):
        return None
    fallback_kind = debug.get("fallback_kind")
    source_card_type = debug.get("source_card_type")
    if not isinstance(fallback_kind, str) or not isinstance(source_card_type, str):
        return None
    normalized_fallback_kind = fallback_kind.strip()
    normalized_source_card_type = source_card_type.strip()
    if normalized_fallback_kind not in {"generic", "unknown"}:
        return None
    if not normalized_source_card_type:
        return None
    return normalized_fallback_kind, normalized_source_card_type


def _render_terminal_action_policy(
    card_type: str,
    title: str,
    debug: Any,
    *,
    generic_fallback_source: str | None = None,
    generic_fallback_hint: bool = False,
) -> list[str]:
    if card_type == UNKNOWN_CARD_TYPE:
        return ["Action policy: copy_to_clipboard_only"]
    if card_type == GENERIC_CARD_TYPE and (
        _is_fallback_card_debug(debug)
        or generic_fallback_source is not None
        or generic_fallback_hint
    ):
        return ["Action policy: client_allowlist"]
    return []


def _is_fallback_card_debug(debug: Any) -> bool:
    return _extract_terminal_fallback_debug(debug) is not None


def _resolve_generic_fallback_source(title: str, actions: Any, debug: Any) -> str | None:
    fallback_debug = _extract_terminal_fallback_debug(debug)
    if fallback_debug is not None:
        fallback_kind, source_card_type = fallback_debug
        if fallback_kind == "generic":
            return source_card_type
        return None

    source_card_type = _infer_generic_fallback_source(title)
    if source_card_type is None:
        return None
    if actions is None:
        return source_card_type
    if not _is_canonical_read_only_fallback_actions(actions):
        return None
    return source_card_type


def _is_canonical_generic_fallback_signal(subtitle: Any, actions: Any) -> bool:
    if not isinstance(subtitle, str) or subtitle.strip() != GENERIC_FALLBACK_SUBTITLE:
        return False
    return actions is None or _is_canonical_read_only_fallback_actions(actions)


def _infer_generic_fallback_source(title: str) -> str | None:
    if not title.startswith(GENERIC_FALLBACK_TITLE_PREFIX):
        return None
    source_card_type = title[len(GENERIC_FALLBACK_TITLE_PREFIX) :].strip()
    return source_card_type or None


def _infer_unknown_fallback_source(title: str) -> str | None:
    if not title.startswith(UNKNOWN_FALLBACK_TITLE_PREFIX):
        return None
    source_card_type = title[len(UNKNOWN_FALLBACK_TITLE_PREFIX) :].strip()
    return source_card_type or None


def _iter_card_entries(entries: Any) -> list[Any]:
    if not isinstance(entries, (list, tuple)):
        return []
    return list(entries)


def _normalize_card_type(card: dict[str, Any]) -> str:
    raw_type = card.get("type")
    if not isinstance(raw_type, str):
        return "<missing>"
    card_type = raw_type.strip()
    return card_type if card_type else "<missing>"


def _normalize_card_title(card: dict[str, Any]) -> str:
    raw_title = card.get("title")
    if not isinstance(raw_title, str):
        return "<untitled>"
    title = raw_title.strip()
    return title if title else "<untitled>"


def _normalize_card_text(value: Any, *, fallback: str | None = None) -> str | None:
    if value is None:
        return fallback
    if not isinstance(value, str):
        return fallback
    normalized = value.strip()
    if normalized:
        return normalized
    return fallback


def _build_fallback_debug(source_card_type: str, *, fallback_kind: str) -> dict[str, Any]:
    return {
        "contract_version": A2UI_CONTRACT_VERSION,
        "fallback_kind": fallback_kind,
        "source_card_type": source_card_type,
    }


def _extract_unknown_card_source_type(card: dict[str, Any]) -> str:
    debug = card.get("debug")
    if isinstance(debug, Mapping):
        source_card_type = debug.get("source_card_type")
        if isinstance(source_card_type, str):
            normalized_source_card_type = source_card_type.strip()
            if normalized_source_card_type:
                return normalized_source_card_type
    normalized_type = _normalize_card_type(card)
    return normalized_type if normalized_type != "<missing>" else UNKNOWN_CARD_TYPE


def _normalize_preview_budget(max_payload_bytes: int | None) -> int:
    if max_payload_bytes is None:
        return DEFAULT_UNKNOWN_CARD_PREVIEW_BYTES
    if type(max_payload_bytes) is not int:
        raise ValueError("max_payload_bytes must be an int or None")
    if max_payload_bytes < 0:
        raise ValueError("max_payload_bytes must be non-negative")
    return max_payload_bytes


def _build_fallback_title(expected_type: str, *, source_card_type: str) -> str:
    if expected_type == GENERIC_CARD_TYPE:
        return f"Fallback view for {source_card_type}"
    if expected_type == UNKNOWN_CARD_TYPE:
        return f"{UNKNOWN_FALLBACK_TITLE_PREFIX}{source_card_type}"
    raise ValueError(f"Unsupported fallback card type: {expected_type}")


def _fallback_subtitle(fallback_kind: str) -> str:
    if fallback_kind == "generic":
        return GENERIC_FALLBACK_SUBTITLE
    if fallback_kind == "unknown":
        return UNKNOWN_FALLBACK_SUBTITLE
    raise ValueError(f"Unsupported fallback kind: {fallback_kind}")


def _extract_safe_primitive_blocks(card: dict[str, Any], *, allow_code_block: bool = True) -> list[dict[str, Any]]:
    nested_blocks = card.get("blocks")
    if not isinstance(nested_blocks, (list, tuple)):
        return []

    safe_blocks: list[dict[str, Any]] = []
    for block in nested_blocks:
        sanitized_block = _sanitize_safe_primitive_block(block, allow_code_block=allow_code_block)
        if sanitized_block is not None:
            safe_blocks.append(sanitized_block)
    return safe_blocks


def _sanitize_safe_primitive_block(block: Any, *, allow_code_block: bool = True) -> dict[str, Any] | None:
    if not isinstance(block, Mapping):
        return None
    block_type = str(block.get("type", "")).strip()
    if block_type not in _PRIMITIVE_BLOCK_SET:
        return None
    if block_type == "MarkdownBlock":
        markdown = block.get("markdown")
        if not isinstance(markdown, str):
            return None
        return {"type": block_type, "markdown": markdown}
    if block_type == "AlertBlock":
        message = block.get("message")
        if not isinstance(message, str):
            return None
        sanitized: dict[str, Any] = {
            "type": block_type,
            "severity": _normalize_card_text(block.get("severity"), fallback="info") or "info",
            "message": message,
        }
        title = _normalize_card_text(block.get("title"))
        if title is not None:
            sanitized["title"] = title
        return sanitized
    if block_type == "CodeBlock":
        if not allow_code_block:
            return None
        code = block.get("code")
        if not isinstance(code, str):
            return None
        sanitized = {"type": block_type, "code": code}
        language = block.get("language")
        if language is not None:
            if not isinstance(language, str):
                return None
            sanitized["language"] = language
        collapsed = block.get("collapsed")
        if collapsed is not None:
            if not isinstance(collapsed, bool):
                return None
            sanitized["collapsed"] = collapsed
        return sanitized
    if block_type == "ProgressBlock":
        status_text = block.get("status_text")
        if not isinstance(status_text, str):
            return None
        sanitized = {
            "type": block_type,
            "status_text": status_text,
        }
        title = block.get("title")
        if title is not None:
            if not isinstance(title, str):
                return None
            sanitized["title"] = title
        return sanitized
    if block_type == "KeyValueBlock":
        items = block.get("items")
        if not isinstance(items, list):
            return None
        sanitized_items: list[dict[str, Any]] = []
        for item in items:
            if not isinstance(item, Mapping):
                continue
            key = item.get("key")
            if not isinstance(key, str) or not key.strip():
                continue
            value = item.get("value")
            if not _is_safe_scalar_value(value):
                continue
            sanitized_items.append({"key": key.strip(), "value": value})
        if not sanitized_items:
            return None
        return {"type": block_type, "items": sanitized_items}
    if block_type == "ListBlock":
        items = block.get("items")
        if not isinstance(items, list):
            return None
        sanitized_items: list[Any] = []
        for item in items:
            if isinstance(item, str):
                rendered_item = item.strip()
                if rendered_item:
                    sanitized_items.append(rendered_item)
            elif isinstance(item, Mapping):
                label = item.get("label")
                if isinstance(label, str) and label.strip():
                    sanitized_items.append({"label": label.strip()})
        if not sanitized_items:
            return None
        return {"type": block_type, "items": sanitized_items}
    if block_type == "TableBlock":
        rows = block.get("rows")
        if not isinstance(rows, list):
            return None
        sanitized_rows: list[list[Any]] = []
        for row in rows:
            if not isinstance(row, list):
                continue
            sanitized_row: list[Any] = []
            for cell in row:
                if isinstance(cell, (str, int, float, bool)) or cell is None:
                    sanitized_row.append(cell)
            if sanitized_row:
                sanitized_rows.append(sanitized_row)
        if not sanitized_rows:
            return None
        return {"type": block_type, "rows": sanitized_rows}
    return None


def _canonicalize_supported_actions(supported_actions: tuple[str, ...] | None) -> set[str]:
    if supported_actions is None:
        return set(_ALLOWED_ACTION_SET)

    canonical_actions: set[str] = set()
    for action_id in supported_actions:
        if not isinstance(action_id, str):
            continue
        normalized_action_id = action_id.strip()
        if normalized_action_id in _ALLOWED_ACTION_SET:
            canonical_actions.add(normalized_action_id)
    return canonical_actions


def _canonicalize_supported_action_list(
    actions: Any,
    *,
    supported_actions: set[str],
) -> list[dict[str, Any]]:
    if not isinstance(actions, (list, tuple)):
        return []

    filtered: list[dict[str, Any]] = []
    seen: set[str] = set()
    for action in actions:
        try:
            normalized = _normalize_action(action, supported_actions=supported_actions)
        except ValueError:
            continue
        action_key = _canonical_json(normalized)
        if action_key in seen:
            continue
        seen.add(action_key)
        filtered.append(normalized)
    return filtered


def _validate_supported_string_sequence(values: Any, *, field_name: str) -> tuple[str, ...]:
    if not isinstance(values, (list, tuple)):
        raise ValueError(f"{field_name} must be a list or tuple of strings")
    validated: list[str] = []
    for value in values:
        if not isinstance(value, str):
            raise ValueError(f"{field_name} must contain only strings")
        validated.append(value)
    return tuple(validated)


def _render_terminal_block(block: Any) -> list[str]:
    if not isinstance(block, Mapping):
        return ["[unsupported block: malformed]"]
    block_type = str(block.get("type", "")).strip()
    if not block_type:
        return ["[unsupported block: missing type]"]
    if block_type == "MarkdownBlock":
        markdown = block.get("markdown")
        if not isinstance(markdown, str):
            return _render_terminal_invalid_primitive_block(block_type, "markdown")
        return [_render_terminal_text(markdown)]
    if block_type == "AlertBlock":
        message = block.get("message")
        if not isinstance(message, str):
            return _render_terminal_invalid_primitive_block(block_type, "message")
        severity_value = block.get("severity", "info")
        if isinstance(severity_value, str):
            severity = _render_terminal_inline_text(severity_value.strip()).upper() or "INFO"
        else:
            severity = "INFO"
        message = _render_terminal_inline_text(message)
        return [f"{severity}: {message}"]
    if block_type == "CodeBlock":
        code = block.get("code")
        if not isinstance(code, str):
            return _render_terminal_invalid_primitive_block(block_type, "code")
        return [_render_terminal_text(code)]
    if block_type == "ProgressBlock":
        status_text = block.get("status_text")
        if not isinstance(status_text, str):
            return _render_terminal_invalid_primitive_block(block_type, "status_text")
        title_value = block.get("title", "progress")
        if isinstance(title_value, str):
            title = _render_terminal_inline_text(title_value) or "progress"
        else:
            title = "progress"
        status_text = _render_terminal_inline_text(status_text)
        return [f"{title}: {status_text}"]
    if block_type == "KeyValueBlock":
        items = block.get("items", [])
        if not isinstance(items, list):
            return ["[KeyValueBlock: invalid items]"]
        lines: list[str] = []
        for item in items:
            if not isinstance(item, Mapping):
                continue
            key = _render_terminal_inline_text(item.get("key", ""))
            if not key:
                continue
            value = item.get("value", None)
            if not _is_safe_scalar_value(value):
                continue
            if isinstance(value, bool):
                value = "true" if value else "false"
            value = _render_terminal_inline_text(value) or "<blank>"
            lines.append(f"- {key}: {value}")
        return lines or ["[KeyValueBlock: empty]"]
    if block_type == "ListBlock":
        items = block.get("items", [])
        if not isinstance(items, list):
            return ["[ListBlock: invalid items]"]
        lines: list[str] = []
        for item in items:
            if isinstance(item, str):
                rendered_item = _render_terminal_inline_text(item)
                if rendered_item:
                    lines.append(f"- {rendered_item}")
            elif isinstance(item, Mapping):
                label = item.get("label", "")
                if isinstance(label, str):
                    rendered_label = _render_terminal_inline_text(label)
                    if rendered_label:
                        lines.append(f"- {rendered_label}")
        return lines or ["[ListBlock: empty]"]
    if block_type == "TableBlock":
        rows = block.get("rows", [])
        if not isinstance(rows, list):
            return ["[table: invalid rows]"]
        lines = ["[table]"]
        for row in rows:
            if not isinstance(row, list):
                continue
            rendered_cells: list[str] = []
            for cell in row:
                if cell is None:
                    rendered_cells.append("<blank>")
                elif isinstance(cell, bool):
                    rendered_cells.append("true" if cell else "false")
                elif isinstance(cell, (str, int, float)):
                    rendered_cells.append(_render_terminal_inline_text(cell))
                else:
                    rendered_cells.append(f"<non-json:{type(cell).__name__}>")
            if rendered_cells:
                lines.append(f"- {' | '.join(rendered_cells)}")
        return lines if len(lines) > 1 else ["[table: empty]"]
    return [f"[unsupported block: {_render_terminal_inline_text(block_type)}]"]


def _render_terminal_invalid_primitive_block(block_type: str, field_name: str) -> list[str]:
    return [f"[{block_type}: invalid {field_name}]"]


def _coerce_card_payload(card: Any) -> dict[str, Any] | None:
    if isinstance(card, dict):
        return card
    if isinstance(card, Mapping):
        try:
            return dict(card)
        except Exception:
            return None
    if is_dataclass(card) and not isinstance(card, type):
        try:
            snapshot = _snapshot_terminal_artifact_value(card)
        except Exception:
            return None
        if isinstance(snapshot, Mapping):
            return dict(snapshot)
        return None
    if not any(hasattr(card, attr) for attr in ("type", "title", "subtitle", "blocks", "actions", "debug", "a2ui_version")):
        return None
    try:
        snapshot = dict(vars(card))
    except Exception:
        return None
    if isinstance(snapshot, Mapping):
        return dict(snapshot)
    return None


def _coerce_terminal_card(card: Any) -> dict[str, Any] | None:
    if isinstance(card, dict):
        return card
    if isinstance(card, Mapping):
        try:
            return dict(card)
        except Exception:
            return None
    required_attrs = ("type", "title", "blocks", "actions")
    if not all(hasattr(card, attr) for attr in required_attrs):
        return None
    card_type = getattr(card, "type")
    if not isinstance(card_type, str):
        return None
    normalized_card_type = card_type.strip()
    if not normalized_card_type or normalized_card_type in {"ActionRef", "SelectionRef", _TERMINAL_ARTIFACT_ENVELOPE_TYPE}:
        return None
    if is_dataclass(card):
        try:
            snapshot = _snapshot_terminal_artifact_value(card)
        except Exception:
            return None
        if isinstance(snapshot, Mapping):
            return dict(snapshot)
        return None
    try:
        snapshot = dict(vars(card))
    except Exception:
        return None
    if isinstance(snapshot, Mapping):
        return dict(snapshot)
    return None


def _render_invalid_terminal_card(card: Any | None = None) -> str:
    lines = [
        "[UnknownCard] <invalid card>",
        "Fallback: unknown card",
        "Action policy: copy_to_clipboard_only",
    ]
    if card is not None:
        lines.append(f"- raw: {_render_payload_preview(card, max_payload_bytes=256)}")
    return "\n".join(lines)


def _render_invalid_terminal_artifact(artifact: Any) -> str:
    return "\n".join(
        [
            "[TerminalArtifact] <invalid artifact>",
            f"TerminalArtifact schema v{TERMINAL_ARTIFACT_SCHEMA_VERSION}",
            f"- raw: {_render_payload_preview(artifact, max_payload_bytes=256)}",
        ]
    )


def _render_terminal_text(value: Any) -> str:
    if value is None:
        return ""
    return _escape_terminal_text(str(value))


def _render_terminal_inline_text(value: Any) -> str:
    rendered = _render_terminal_text(value)
    if not rendered:
        return ""
    return " ".join(rendered.replace("\n", " ").split())


def _escape_terminal_text(value: str) -> str:
    parts: list[str] = []
    for char in value:
        code = ord(char)
        if char == "\n":
            parts.append(char)
        elif code < 32 or code == 127:
            parts.append(f"\\x{code:02x}")
        elif unicodedata.category(char).startswith("C"):
            if code <= 0xFFFF:
                parts.append(f"\\u{code:04x}")
            else:
                parts.append(f"\\U{code:08x}")
        else:
            parts.append(char)
    return "".join(parts)
