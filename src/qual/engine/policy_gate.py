from __future__ import annotations

from dataclasses import dataclass
from ipaddress import ip_address
from urllib.parse import urlparse


@dataclass(frozen=True)
class PolicyGate:
    confidentiality_profile: str
    llm_base_url: str

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
            return ip_address(host).is_loopback
        except ValueError:
            return False
