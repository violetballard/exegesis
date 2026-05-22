from __future__ import annotations

import unittest

from src.qual.engine.policy_gate import PolicyGate


class PolicyGateTests(unittest.TestCase):
    def test_confidential_profile_accepts_loopback_endpoints(self) -> None:
        for endpoint in (
            "http://localhost:1234/v1",
            "http://127.8.9.10:1234/v1",
            "http://[::1]:1234/v1",
        ):
            with self.subTest(endpoint=endpoint):
                PolicyGate(
                    confidentiality_profile="confidential",
                    llm_base_url=endpoint,
                ).enforce_localhost_llm()

    def test_confidential_profile_rejects_non_loopback_endpoint(self) -> None:
        with self.assertRaises(PermissionError):
            PolicyGate(
                confidentiality_profile="confidential",
                llm_base_url="https://api.openai.com/v1",
            ).enforce_localhost_llm()
