from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from exegesis_textual.services.projects import load_textual_settings, save_textual_settings

MISTRAL_PROVIDER = "mistral"
DEFAULT_MISTRAL_MODEL = "mistral-small-latest"
MISTRAL_SMALL_MODEL = "mistral-small-latest"
MISTRAL_MEDIUM_MODEL = "mistral-medium-3-5"
MISTRAL_LARGE_MODEL = "mistral-large-latest"
MISTRAL_MODEL_OPTIONS = (MISTRAL_SMALL_MODEL, MISTRAL_MEDIUM_MODEL, MISTRAL_LARGE_MODEL)
MISTRAL_REASONING_MODELS = frozenset((MISTRAL_SMALL_MODEL, MISTRAL_MEDIUM_MODEL))
MISTRAL_REASONING_EFFORTS = ("high", "none")
DEFAULT_REASONING_EFFORT = "high"
MODEL_SETTINGS_KEY = "model"


@dataclass(frozen=True)
class MistralModelSettings:
    provider: str = MISTRAL_PROVIDER
    model: str = DEFAULT_MISTRAL_MODEL
    reasoning_effort: str = DEFAULT_REASONING_EFFORT
    settings_prompt_dismissed: bool = False

    def provider_payload_reasoning_effort(self) -> str | None:
        if not model_supports_reasoning(self.model):
            return None
        if self.reasoning_effort == "none":
            return None
        return self.reasoning_effort or DEFAULT_REASONING_EFFORT


def model_supports_reasoning(model: str) -> bool:
    return model in MISTRAL_REASONING_MODELS


def normalize_mistral_model_settings(raw: object) -> MistralModelSettings:
    payload = raw if isinstance(raw, dict) else {}
    provider = payload.get("provider")
    if provider != MISTRAL_PROVIDER:
        provider = MISTRAL_PROVIDER
    model = payload.get("model")
    if model not in MISTRAL_MODEL_OPTIONS:
        model = DEFAULT_MISTRAL_MODEL
    reasoning_effort = payload.get("reasoning_effort")
    if reasoning_effort not in MISTRAL_REASONING_EFFORTS:
        reasoning_effort = DEFAULT_REASONING_EFFORT
    if not model_supports_reasoning(str(model)):
        reasoning_effort = "none"
    dismissed = bool(payload.get("settings_prompt_dismissed"))
    return MistralModelSettings(
        provider=str(provider),
        model=str(model),
        reasoning_effort=str(reasoning_effort),
        settings_prompt_dismissed=dismissed,
    )


def load_mistral_model_settings(repo_root: Path | None = None) -> MistralModelSettings:
    settings = load_textual_settings(repo_root)
    return normalize_mistral_model_settings(settings.get(MODEL_SETTINGS_KEY))


def save_mistral_model_settings(model_settings: MistralModelSettings, repo_root: Path | None = None) -> None:
    settings = load_textual_settings(repo_root)
    settings[MODEL_SETTINGS_KEY] = {
        "provider": MISTRAL_PROVIDER,
        "model": model_settings.model,
        "reasoning_effort": model_settings.reasoning_effort,
        "settings_prompt_dismissed": model_settings.settings_prompt_dismissed,
    }
    save_textual_settings(settings, repo_root)


def mark_model_settings_prompt_dismissed(repo_root: Path | None = None) -> MistralModelSettings:
    current = load_mistral_model_settings(repo_root)
    updated = MistralModelSettings(
        provider=current.provider,
        model=current.model,
        reasoning_effort=current.reasoning_effort,
        settings_prompt_dismissed=True,
    )
    save_mistral_model_settings(updated, repo_root)
    return updated


__all__ = [
    "DEFAULT_MISTRAL_MODEL",
    "DEFAULT_REASONING_EFFORT",
    "MISTRAL_LARGE_MODEL",
    "MISTRAL_MEDIUM_MODEL",
    "MISTRAL_MODEL_OPTIONS",
    "MISTRAL_PROVIDER",
    "MISTRAL_REASONING_EFFORTS",
    "MISTRAL_SMALL_MODEL",
    "MistralModelSettings",
    "load_mistral_model_settings",
    "mark_model_settings_prompt_dismissed",
    "model_supports_reasoning",
    "normalize_mistral_model_settings",
    "save_mistral_model_settings",
]
