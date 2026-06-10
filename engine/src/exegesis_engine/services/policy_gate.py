from __future__ import annotations

from dataclasses import dataclass
from ipaddress import ip_address
from typing import Any
from urllib.parse import urlparse


@dataclass(frozen=True)
class PolicyGate:
    confidentiality_profile: str
    llm_base_url: str

    def __post_init__(self) -> None:
        if self.confidentiality_profile not in {"confidential", "standard"}:
            raise ValueError("confidentiality_profile must be one of: confidential, standard")
        if not isinstance(self.llm_base_url, str):
            raise TypeError("llm_base_url must be a string")
        if not self.llm_base_url.strip():
            raise ValueError("llm_base_url must be a non-empty string")
        parsed = urlparse(self.llm_base_url)
        if parsed.scheme not in {"http", "https"}:
            raise ValueError("llm_base_url must start with http:// or https://")
        if not parsed.hostname:
            raise ValueError("llm_base_url must contain a valid hostname")
        try:
            _ = parsed.port
        except ValueError as e:
            raise ValueError(f"llm_base_url has invalid port: {e}") from e

    def enforce_localhost_llm(self) -> None:
        if self.confidentiality_profile != "confidential":
            return
        if not self._is_localhost(self.llm_base_url):
            raise PermissionError("Confidential profile requires localhost OpenAI-compatible endpoint")

    def enforce_local_only_ocr(self, *, mode: str, pdf_text_extraction: str) -> None:
        if self.confidentiality_profile != "confidential":
            return
        if mode != "offline_only":
            raise PermissionError("Confidential profile requires offline_only mode")
        if pdf_text_extraction != "local":
            raise PermissionError("Confidential profile requires local OCR/text extraction")

    def can_use_vision(self, *, runtime_image_input: bool, model_supports_vision: bool) -> bool:
        return bool(runtime_image_input and model_supports_vision)

    def allow_action(
        self,
        action_id: str,
        payload: dict[str, Any],
        *,
        policy_sensitive: bool,
    ) -> bool:
        if self.confidentiality_profile == "confidential":
            if policy_sensitive:
                try:
                    self.enforce_localhost_llm()
                except PermissionError:
                    return False
            if "pdf_text_extraction" in payload or "mode" in payload:
                mode = str(payload.get("mode", "online"))
                pdf_text_extraction = str(payload.get("pdf_text_extraction", "cloud"))
                try:
                    self.enforce_local_only_ocr(mode=mode, pdf_text_extraction=pdf_text_extraction)
                except PermissionError:
                    return False
        return True

    @staticmethod
    def _is_localhost(raw: str) -> bool:
        parsed = urlparse(raw)
        if parsed.scheme not in {"http", "https"}:
            return False
        host = parsed.hostname
        if host is None:
            return False
        if host.casefold() == "localhost":
            return True
        try:
            ip = ip_address(host)
            if ip.is_loopback:
                return True
            mapped = getattr(ip, "ipv4_mapped", None)
            if mapped is not None:
                return mapped.is_loopback
            return False
        except ValueError:
            return False
