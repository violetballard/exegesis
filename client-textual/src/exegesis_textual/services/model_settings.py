from __future__ import annotations

from dataclasses import dataclass, field
from ipaddress import ip_address
from pathlib import Path
from urllib.parse import urlparse, urlunparse

from exegesis_textual.services.projects import load_textual_settings, save_textual_settings

MISTRAL_PROVIDER = "mistral"
CLAUDE_PROVIDER = "claude"
GOOGLE_PROVIDER = "google"
OPENAI_PROVIDER = "openai"
LOCAL_OPENAI_PROVIDER = "local_openai"
PROVIDER_OPTIONS = (MISTRAL_PROVIDER, CLAUDE_PROVIDER, GOOGLE_PROVIDER, OPENAI_PROVIDER, LOCAL_OPENAI_PROVIDER)
PROVIDER_LABELS = {
    MISTRAL_PROVIDER: "Mistral",
    CLAUDE_PROVIDER: "Claude",
    GOOGLE_PROVIDER: "Google",
    OPENAI_PROVIDER: "OpenAI",
    LOCAL_OPENAI_PROVIDER: "Local OpenAI Compatible Endpoint [Confidential]",
}

DEFAULT_CONTEXT_WINDOW_TOKENS = 256_000
UNKNOWN_CONTEXT_WINDOW_TOKENS = 0
CONTEXT_200K_TOKENS = 200_000
CONTEXT_256K_TOKENS = 256_000
CONTEXT_270K_TOKENS = 270_000
CONTEXT_1M_TOKENS = 1_000_000
LOCAL_CONTEXT_SNAPS = (0, 2_048, 4_096, 8_192, 16_384, 32_768, 65_536, 128_000, 256_000, 512_000, 1_000_000)

DEFAULT_MISTRAL_MODEL = "mistral-small-latest"
MISTRAL_SMALL_MODEL = "mistral-small-latest"
MISTRAL_MEDIUM_MODEL = "mistral-medium-3-5"
MISTRAL_LARGE_MODEL = "mistral-large-latest"
MISTRAL_MODEL_OPTIONS = (MISTRAL_SMALL_MODEL, MISTRAL_MEDIUM_MODEL, MISTRAL_LARGE_MODEL)
MISTRAL_REASONING_MODELS = frozenset((MISTRAL_SMALL_MODEL, MISTRAL_MEDIUM_MODEL))
MISTRAL_REASONING_EFFORTS = ("high", "none")

CLAUDE_FABLE_MODEL = "claude-fable-5"
CLAUDE_OPUS_MODEL = "claude-opus-4-8"
CLAUDE_SONNET_MODEL = "claude-sonnet-4-6"
CLAUDE_HAIKU_MODEL = "claude-haiku-4-5"
CLAUDE_MODEL_OPTIONS = (CLAUDE_FABLE_MODEL, CLAUDE_OPUS_MODEL, CLAUDE_SONNET_MODEL, CLAUDE_HAIKU_MODEL)
CLAUDE_DEEP_REASONING_EFFORTS = ("low", "medium", "high", "xhigh", "max")
CLAUDE_SONNET_REASONING_EFFORTS = ("low", "medium", "high", "max")

GOOGLE_GEMINI_FLASH_MODEL = "gemini-3.5-flash"
GOOGLE_MODEL_OPTIONS = (GOOGLE_GEMINI_FLASH_MODEL,)
GOOGLE_REASONING_EFFORTS = ("low", "medium", "high")

OPENAI_GPT_55_MODEL = "gpt-5.5"
OPENAI_MODEL_OPTIONS = (OPENAI_GPT_55_MODEL,)
OPENAI_REASONING_EFFORTS = ("low", "medium", "high", "xhigh")

DEFAULT_LOCAL_OPENAI_ENDPOINT = "http://127.0.0.1:1234"
DEFAULT_LOCAL_OPENAI_MODEL = ""
DEFAULT_LOCAL_OPENAI_API_KEY = "local"
DEFAULT_REASONING_START_TAG = "<think>"
DEFAULT_REASONING_END_TAG = "</think>"

DEFAULT_REASONING_EFFORT = "high"
MODEL_SETTINGS_KEY = "model"
_MODEL_SETTINGS_SCHEMA_VERSION = 2


@dataclass(frozen=True)
class ModelOption:
    provider: str
    model: str
    label: str
    reasoning_efforts: tuple[str, ...] = ()
    default_reasoning_effort: str = "none"
    context_windows: tuple[int, ...] = (DEFAULT_CONTEXT_WINDOW_TOKENS,)
    default_context_window: int = DEFAULT_CONTEXT_WINDOW_TOKENS

    def supports_reasoning(self) -> bool:
        return bool(self.reasoning_efforts) and self.reasoning_efforts != ("none",)

    def supports_context_selector(self) -> bool:
        return len(self.context_windows) > 1


MODEL_CATALOG: dict[str, ModelOption] = {
    MISTRAL_SMALL_MODEL: ModelOption(MISTRAL_PROVIDER, MISTRAL_SMALL_MODEL, "Mistral Small Latest", MISTRAL_REASONING_EFFORTS, "high", (CONTEXT_256K_TOKENS,), CONTEXT_256K_TOKENS),
    MISTRAL_MEDIUM_MODEL: ModelOption(MISTRAL_PROVIDER, MISTRAL_MEDIUM_MODEL, "Mistral Medium 3.5", MISTRAL_REASONING_EFFORTS, "high", (CONTEXT_256K_TOKENS,), CONTEXT_256K_TOKENS),
    MISTRAL_LARGE_MODEL: ModelOption(MISTRAL_PROVIDER, MISTRAL_LARGE_MODEL, "Mistral Large Latest", (), "none", (CONTEXT_256K_TOKENS,), CONTEXT_256K_TOKENS),
    CLAUDE_FABLE_MODEL: ModelOption(CLAUDE_PROVIDER, CLAUDE_FABLE_MODEL, "Claude Fable 5", CLAUDE_DEEP_REASONING_EFFORTS, "high", (CONTEXT_256K_TOKENS, CONTEXT_1M_TOKENS), CONTEXT_256K_TOKENS),
    CLAUDE_OPUS_MODEL: ModelOption(CLAUDE_PROVIDER, CLAUDE_OPUS_MODEL, "Claude Opus 4.8", CLAUDE_DEEP_REASONING_EFFORTS, "high", (CONTEXT_256K_TOKENS, CONTEXT_1M_TOKENS), CONTEXT_256K_TOKENS),
    CLAUDE_SONNET_MODEL: ModelOption(CLAUDE_PROVIDER, CLAUDE_SONNET_MODEL, "Claude Sonnet 4.6", CLAUDE_SONNET_REASONING_EFFORTS, "high", (CONTEXT_256K_TOKENS, CONTEXT_1M_TOKENS), CONTEXT_256K_TOKENS),
    CLAUDE_HAIKU_MODEL: ModelOption(CLAUDE_PROVIDER, CLAUDE_HAIKU_MODEL, "Claude Haiku 4.5", (), "none", (CONTEXT_200K_TOKENS,), CONTEXT_200K_TOKENS),
    GOOGLE_GEMINI_FLASH_MODEL: ModelOption(GOOGLE_PROVIDER, GOOGLE_GEMINI_FLASH_MODEL, "Gemini 3.5 Flash", GOOGLE_REASONING_EFFORTS, "medium", (CONTEXT_200K_TOKENS, CONTEXT_1M_TOKENS), CONTEXT_200K_TOKENS),
    OPENAI_GPT_55_MODEL: ModelOption(OPENAI_PROVIDER, OPENAI_GPT_55_MODEL, "GPT-5.5", OPENAI_REASONING_EFFORTS, "medium", (CONTEXT_270K_TOKENS, CONTEXT_1M_TOKENS), CONTEXT_270K_TOKENS),
}

DEFAULT_MODEL_BY_PROVIDER = {
    MISTRAL_PROVIDER: MISTRAL_SMALL_MODEL,
    CLAUDE_PROVIDER: CLAUDE_SONNET_MODEL,
    GOOGLE_PROVIDER: GOOGLE_GEMINI_FLASH_MODEL,
    OPENAI_PROVIDER: OPENAI_GPT_55_MODEL,
    LOCAL_OPENAI_PROVIDER: DEFAULT_LOCAL_OPENAI_MODEL,
}
MODEL_OPTIONS_BY_PROVIDER = {
    MISTRAL_PROVIDER: MISTRAL_MODEL_OPTIONS,
    CLAUDE_PROVIDER: CLAUDE_MODEL_OPTIONS,
    GOOGLE_PROVIDER: GOOGLE_MODEL_OPTIONS,
    OPENAI_PROVIDER: OPENAI_MODEL_OPTIONS,
    LOCAL_OPENAI_PROVIDER: (),
}

REASONING_LABELS = {
    "none": "None",
    "low": "Low",
    "medium": "Medium",
    "high": "High",
    "extra": "Extra",
    "max": "Max",
    "ultracode": "Ultracode",
    "xhigh": "Extra High",
}
CONTEXT_LABELS = {
    UNKNOWN_CONTEXT_WINDOW_TOKENS: "Unknown",
    CONTEXT_200K_TOKENS: "200k",
    CONTEXT_256K_TOKENS: "256k",
    CONTEXT_270K_TOKENS: "270k",
    CONTEXT_1M_TOKENS: "1M",
}


@dataclass(frozen=True)
class ProviderModelProfile:
    provider: str
    model: str
    reasoning_effort: str = "none"
    context_window_tokens: int = DEFAULT_CONTEXT_WINDOW_TOKENS
    endpoint_url: str = ""
    reasoning_start_tag: str = DEFAULT_REASONING_START_TAG
    reasoning_end_tag: str = DEFAULT_REASONING_END_TAG

    def payload_reasoning_effort(self) -> str | None:
        if self.provider == LOCAL_OPENAI_PROVIDER:
            return self.reasoning_effort.strip() or None
        option = model_option(self.model)
        if not option.supports_reasoning() or self.reasoning_effort == "none":
            return None
        if self.reasoning_effort not in option.reasoning_efforts:
            return option.default_reasoning_effort
        return self.reasoning_effort


@dataclass(frozen=True)
class ModelSettings:
    provider: str = MISTRAL_PROVIDER
    model: str = DEFAULT_MISTRAL_MODEL
    reasoning_effort: str = DEFAULT_REASONING_EFFORT
    context_window_tokens: int = DEFAULT_CONTEXT_WINDOW_TOKENS
    settings_prompt_dismissed: bool = False
    endpoint_url: str = ""
    reasoning_start_tag: str = DEFAULT_REASONING_START_TAG
    reasoning_end_tag: str = DEFAULT_REASONING_END_TAG
    profiles: dict[str, ProviderModelProfile] = field(default_factory=dict, compare=False)

    def __post_init__(self) -> None:
        if self.provider != LOCAL_OPENAI_PROVIDER:
            return
        if self.model == DEFAULT_MISTRAL_MODEL:
            object.__setattr__(self, "model", DEFAULT_LOCAL_OPENAI_MODEL)
        if self.reasoning_effort == DEFAULT_REASONING_EFFORT:
            object.__setattr__(self, "reasoning_effort", "")
        if not self.endpoint_url:
            object.__setattr__(self, "endpoint_url", DEFAULT_LOCAL_OPENAI_ENDPOINT)

    def model_option(self) -> ModelOption:
        return model_option(self.model)

    def active_profile(self) -> ProviderModelProfile:
        return provider_profile_from_settings(self, self.provider)

    def profile_for_provider(self, provider: str) -> ProviderModelProfile:
        return provider_profile_from_settings(self, provider)

    def provider_label(self) -> str:
        return PROVIDER_LABELS.get(self.provider, self.provider.title())

    def model_label(self) -> str:
        if self.provider == LOCAL_OPENAI_PROVIDER:
            return self.model or "Local model"
        return self.model_option().label

    def context_window_label(self) -> str:
        return context_window_label(self.context_window_tokens)

    def provider_payload_reasoning_effort(self) -> str | None:
        return self.active_profile().payload_reasoning_effort()

    def local_endpoint_configured(self) -> bool:
        profile = self.profile_for_provider(LOCAL_OPENAI_PROVIDER)
        return bool(profile.model.strip()) and is_loopback_endpoint(profile.endpoint_url)


# Compatibility name retained while the first-release code migrates to neutral naming.
MistralModelSettings = ModelSettings


def provider_label(provider: str) -> str:
    return PROVIDER_LABELS.get(provider, provider.title())


def model_option(model: str) -> ModelOption:
    return MODEL_CATALOG.get(model) or MODEL_CATALOG[DEFAULT_MISTRAL_MODEL]


def model_options_for_provider(provider: str) -> tuple[ModelOption, ...]:
    model_ids = MODEL_OPTIONS_BY_PROVIDER.get(provider, MISTRAL_MODEL_OPTIONS)
    return tuple(MODEL_CATALOG[model_id] for model_id in model_ids)


def default_profile_for_provider(provider: str) -> ProviderModelProfile:
    clean_provider = provider if provider in PROVIDER_OPTIONS else MISTRAL_PROVIDER
    if clean_provider == LOCAL_OPENAI_PROVIDER:
        return ProviderModelProfile(
            provider=LOCAL_OPENAI_PROVIDER,
            model=DEFAULT_LOCAL_OPENAI_MODEL,
            reasoning_effort="",
            context_window_tokens=CONTEXT_256K_TOKENS,
            endpoint_url=DEFAULT_LOCAL_OPENAI_ENDPOINT,
            reasoning_start_tag=DEFAULT_REASONING_START_TAG,
            reasoning_end_tag=DEFAULT_REASONING_END_TAG,
        )
    option = MODEL_CATALOG[DEFAULT_MODEL_BY_PROVIDER[clean_provider]]
    return ProviderModelProfile(
        provider=clean_provider,
        model=option.model,
        reasoning_effort=option.default_reasoning_effort if option.supports_reasoning() else "none",
        context_window_tokens=option.default_context_window,
    )


def default_model_settings_for_provider(provider: str, *, dismissed: bool = False) -> ModelSettings:
    profile = default_profile_for_provider(provider)
    return _settings_from_profile(profile, dismissed=dismissed, profiles=_default_profiles())


def _default_profiles() -> dict[str, ProviderModelProfile]:
    return {provider: default_profile_for_provider(provider) for provider in PROVIDER_OPTIONS}


def provider_profile_from_settings(settings: ModelSettings, provider: str) -> ProviderModelProfile:
    clean_provider = provider if provider in PROVIDER_OPTIONS else MISTRAL_PROVIDER
    profile = settings.profiles.get(clean_provider)
    if profile is not None:
        return profile
    if clean_provider == settings.provider:
        return ProviderModelProfile(
            provider=settings.provider,
            model=settings.model,
            reasoning_effort=settings.reasoning_effort,
            context_window_tokens=settings.context_window_tokens,
            endpoint_url=settings.endpoint_url,
            reasoning_start_tag=settings.reasoning_start_tag,
            reasoning_end_tag=settings.reasoning_end_tag,
        )
    return default_profile_for_provider(clean_provider)


def _settings_from_profile(
    profile: ProviderModelProfile,
    *,
    dismissed: bool,
    profiles: dict[str, ProviderModelProfile] | None = None,
) -> ModelSettings:
    clean_profiles = dict(profiles or _default_profiles())
    clean_profiles[profile.provider] = profile
    return ModelSettings(
        provider=profile.provider,
        model=profile.model,
        reasoning_effort=profile.reasoning_effort,
        context_window_tokens=profile.context_window_tokens,
        settings_prompt_dismissed=dismissed,
        endpoint_url=profile.endpoint_url,
        reasoning_start_tag=profile.reasoning_start_tag,
        reasoning_end_tag=profile.reasoning_end_tag,
        profiles=clean_profiles,
    )


def model_supports_reasoning(model: str) -> bool:
    return model_option(model).supports_reasoning()


def reasoning_options_for_model(model: str) -> tuple[str, ...]:
    option = model_option(model)
    return option.reasoning_efforts or ("none",)


def context_options_for_model(model: str) -> tuple[int, ...]:
    return model_option(model).context_windows


def context_window_label(tokens: int) -> str:
    return CONTEXT_LABELS.get(tokens, f"{tokens:,}")


def normalize_local_context_window(raw: object) -> int:
    try:
        tokens = int(raw)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return CONTEXT_256K_TOKENS
    return max(0, min(CONTEXT_1M_TOKENS, tokens))


def normalize_local_openai_base_url(endpoint_url: str) -> str:
    raw = (endpoint_url or DEFAULT_LOCAL_OPENAI_ENDPOINT).strip() or DEFAULT_LOCAL_OPENAI_ENDPOINT
    parsed = urlparse(raw if "://" in raw else f"http://{raw}")
    path = parsed.path.rstrip("/")
    if not path:
        path = "/v1"
    return urlunparse((parsed.scheme, parsed.netloc, path, "", "", ""))


def is_loopback_endpoint(endpoint_url: str) -> bool:
    raw = (endpoint_url or "").strip()
    if not raw:
        return False
    parsed = urlparse(raw if "://" in raw else f"http://{raw}")
    host = (parsed.hostname or "").strip().lower()
    if host == "localhost":
        return True
    try:
        address = ip_address(host)
    except ValueError:
        return False
    return address.is_loopback


def normalize_provider_profile(provider: str, raw: object) -> ProviderModelProfile:
    payload = raw if isinstance(raw, dict) else {}
    clean_provider = provider if provider in PROVIDER_OPTIONS else MISTRAL_PROVIDER
    if clean_provider == LOCAL_OPENAI_PROVIDER:
        endpoint = payload.get("endpoint_url")
        model = payload.get("model")
        reasoning = payload.get("reasoning_effort")
        start_tag = payload.get("reasoning_start_tag")
        end_tag = payload.get("reasoning_end_tag")
        return ProviderModelProfile(
            provider=LOCAL_OPENAI_PROVIDER,
            model=model.strip() if isinstance(model, str) else DEFAULT_LOCAL_OPENAI_MODEL,
            reasoning_effort=reasoning.strip() if isinstance(reasoning, str) else "",
            context_window_tokens=normalize_local_context_window(payload.get("context_window_tokens")),
            endpoint_url=endpoint.strip() if isinstance(endpoint, str) and endpoint.strip() else DEFAULT_LOCAL_OPENAI_ENDPOINT,
            reasoning_start_tag=start_tag if isinstance(start_tag, str) and start_tag else DEFAULT_REASONING_START_TAG,
            reasoning_end_tag=end_tag if isinstance(end_tag, str) and end_tag else DEFAULT_REASONING_END_TAG,
        )

    raw_model = payload.get("model")
    model = raw_model if isinstance(raw_model, str) and raw_model in MODEL_CATALOG and MODEL_CATALOG[raw_model].provider == clean_provider else ""
    if not model:
        model = DEFAULT_MODEL_BY_PROVIDER[clean_provider]
    option = MODEL_CATALOG[model]

    raw_reasoning = payload.get("reasoning_effort")
    reasoning_effort = raw_reasoning if isinstance(raw_reasoning, str) and raw_reasoning in reasoning_options_for_model(model) else ""
    if not reasoning_effort:
        reasoning_effort = option.default_reasoning_effort
    if not option.supports_reasoning():
        reasoning_effort = "none"

    raw_context = payload.get("context_window_tokens")
    try:
        context_window = int(raw_context)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        context_window = option.default_context_window
    if context_window not in option.context_windows:
        context_window = option.default_context_window

    return ProviderModelProfile(clean_provider, model, reasoning_effort, context_window)


def _profile_payload(profile: ProviderModelProfile) -> dict[str, object]:
    payload: dict[str, object] = {
        "model": profile.model,
        "reasoning_effort": profile.reasoning_effort,
        "context_window_tokens": profile.context_window_tokens,
    }
    if profile.provider == LOCAL_OPENAI_PROVIDER:
        payload.update(
            {
                "endpoint_url": profile.endpoint_url,
                "reasoning_start_tag": profile.reasoning_start_tag,
                "reasoning_end_tag": profile.reasoning_end_tag,
            }
        )
    return payload


def normalize_model_settings(raw: object) -> ModelSettings:
    payload = raw if isinstance(raw, dict) else {}
    schema_version = payload.get("schema_version")
    if schema_version == _MODEL_SETTINGS_SCHEMA_VERSION and isinstance(payload.get("profiles"), dict):
        raw_provider = payload.get("active_provider")
        provider = raw_provider if isinstance(raw_provider, str) and raw_provider in PROVIDER_OPTIONS else MISTRAL_PROVIDER
        raw_profiles = payload.get("profiles") if isinstance(payload.get("profiles"), dict) else {}
        profiles = {
            profile_provider: normalize_provider_profile(profile_provider, raw_profiles.get(profile_provider))
            for profile_provider in PROVIDER_OPTIONS
        }
        dismissed = bool(payload.get("settings_prompt_dismissed"))
        return _settings_from_profile(profiles[provider], dismissed=dismissed, profiles=profiles)

    raw_provider = payload.get("provider")
    raw_model = payload.get("model")
    provider = raw_provider if isinstance(raw_provider, str) and raw_provider in PROVIDER_OPTIONS else ""
    if not provider and isinstance(raw_model, str) and raw_model in MODEL_CATALOG:
        provider = MODEL_CATALOG[raw_model].provider
    if not provider:
        provider = MISTRAL_PROVIDER
    profile = normalize_provider_profile(provider, payload)
    profiles = _default_profiles()
    profiles[provider] = profile
    dismissed = bool(payload.get("settings_prompt_dismissed"))
    return _settings_from_profile(profile, dismissed=dismissed, profiles=profiles)


def normalize_mistral_model_settings(raw: object) -> ModelSettings:
    return normalize_model_settings(raw)


def load_model_settings(repo_root: Path | None = None) -> ModelSettings:
    settings = load_textual_settings(repo_root)
    return normalize_model_settings(settings.get(MODEL_SETTINGS_KEY))


def load_mistral_model_settings(repo_root: Path | None = None) -> ModelSettings:
    return load_model_settings(repo_root)


def save_model_settings(model_settings: ModelSettings, repo_root: Path | None = None) -> None:
    settings = load_textual_settings(repo_root)
    current = normalize_model_settings(settings.get(MODEL_SETTINGS_KEY))
    profiles = dict(current.profiles or _default_profiles())
    active_profile = ProviderModelProfile(
        provider=model_settings.provider if model_settings.provider in PROVIDER_OPTIONS else MISTRAL_PROVIDER,
        model=model_settings.model,
        reasoning_effort=model_settings.reasoning_effort,
        context_window_tokens=model_settings.context_window_tokens,
        endpoint_url=model_settings.endpoint_url,
        reasoning_start_tag=model_settings.reasoning_start_tag,
        reasoning_end_tag=model_settings.reasoning_end_tag,
    )
    normalized_profile = normalize_provider_profile(active_profile.provider, _profile_payload(active_profile))
    profiles[normalized_profile.provider] = normalized_profile
    settings[MODEL_SETTINGS_KEY] = {
        "schema_version": _MODEL_SETTINGS_SCHEMA_VERSION,
        "active_provider": normalized_profile.provider,
        "settings_prompt_dismissed": bool(model_settings.settings_prompt_dismissed),
        # Keep legacy flat fields during the schema transition so existing tests,
        # diagnostics, and older dev settings readers keep seeing the active profile.
        "provider": normalized_profile.provider,
        "model": normalized_profile.model,
        "reasoning_effort": normalized_profile.reasoning_effort,
        "context_window_tokens": normalized_profile.context_window_tokens,
        "profiles": {provider: _profile_payload(profiles[provider]) for provider in PROVIDER_OPTIONS},
    }
    save_textual_settings(settings, repo_root)


def save_mistral_model_settings(model_settings: ModelSettings, repo_root: Path | None = None) -> None:
    save_model_settings(model_settings, repo_root)


def mark_model_settings_prompt_dismissed(repo_root: Path | None = None) -> ModelSettings:
    current = load_model_settings(repo_root)
    updated = ModelSettings(
        provider=current.provider,
        model=current.model,
        reasoning_effort=current.reasoning_effort,
        context_window_tokens=current.context_window_tokens,
        settings_prompt_dismissed=True,
        endpoint_url=current.endpoint_url,
        reasoning_start_tag=current.reasoning_start_tag,
        reasoning_end_tag=current.reasoning_end_tag,
        profiles=current.profiles,
    )
    save_model_settings(updated, repo_root)
    return updated


__all__ = [
    "CLAUDE_FABLE_MODEL",
    "CLAUDE_HAIKU_MODEL",
    "CLAUDE_MODEL_OPTIONS",
    "CLAUDE_OPUS_MODEL",
    "CLAUDE_PROVIDER",
    "CLAUDE_SONNET_MODEL",
    "CONTEXT_1M_TOKENS",
    "CONTEXT_200K_TOKENS",
    "CONTEXT_256K_TOKENS",
    "CONTEXT_270K_TOKENS",
    "DEFAULT_CONTEXT_WINDOW_TOKENS",
    "DEFAULT_LOCAL_OPENAI_API_KEY",
    "DEFAULT_LOCAL_OPENAI_ENDPOINT",
    "DEFAULT_LOCAL_OPENAI_MODEL",
    "DEFAULT_MISTRAL_MODEL",
    "DEFAULT_MODEL_BY_PROVIDER",
    "DEFAULT_REASONING_EFFORT",
    "DEFAULT_REASONING_END_TAG",
    "DEFAULT_REASONING_START_TAG",
    "GOOGLE_GEMINI_FLASH_MODEL",
    "GOOGLE_MODEL_OPTIONS",
    "GOOGLE_PROVIDER",
    "LOCAL_CONTEXT_SNAPS",
    "LOCAL_OPENAI_PROVIDER",
    "MISTRAL_LARGE_MODEL",
    "MISTRAL_MEDIUM_MODEL",
    "MISTRAL_MODEL_OPTIONS",
    "MISTRAL_PROVIDER",
    "MISTRAL_REASONING_EFFORTS",
    "MISTRAL_SMALL_MODEL",
    "MODEL_CATALOG",
    "MODEL_OPTIONS_BY_PROVIDER",
    "OPENAI_GPT_55_MODEL",
    "OPENAI_MODEL_OPTIONS",
    "OPENAI_PROVIDER",
    "PROVIDER_LABELS",
    "PROVIDER_OPTIONS",
    "ProviderModelProfile",
    "ModelOption",
    "ModelSettings",
    "MistralModelSettings",
    "context_options_for_model",
    "context_window_label",
    "default_model_settings_for_provider",
    "is_loopback_endpoint",
    "load_mistral_model_settings",
    "load_model_settings",
    "mark_model_settings_prompt_dismissed",
    "model_option",
    "model_options_for_provider",
    "model_supports_reasoning",
    "normalize_local_openai_base_url",
    "normalize_mistral_model_settings",
    "normalize_model_settings",
    "normalize_local_context_window",
    "provider_label",
    "provider_profile_from_settings",
    "reasoning_options_for_model",
    "save_mistral_model_settings",
    "save_model_settings",
]
