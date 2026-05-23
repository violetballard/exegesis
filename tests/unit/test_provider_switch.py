from __future__ import annotations

import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

from packet_garden.tools import provider_switch


class ProviderSwitchTests(unittest.TestCase):
    def test_mark_provider_unavailable_sets_retry_cooldown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            state_file = Path(tmp) / "state.json"
            state_file.write_text('{"cloud_provider": "claude", "cloud_providers": {}}\n')

            with mock.patch.object(provider_switch, "STATE_FILE", state_file), mock.patch.object(
                provider_switch.time, "time", return_value=1000.0
            ):
                state = provider_switch.mark_provider_unavailable(
                    "codex",
                    retry_seconds=300,
                    reason="codex quota exhausted",
                )

        self.assertEqual(state["cloud_providers"]["codex"]["available"], False)
        self.assertEqual(state["cloud_providers"]["codex"]["retry_at"], 1300.0)
        self.assertEqual(state["cloud_providers"]["codex"]["reason"], "codex quota exhausted")
        self.assertEqual(state["cloud_provider"], "claude")

    def test_reset_cloud_state_can_mark_codex_unavailable_while_switching_to_claude(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            state_file = Path(tmp) / "state.json"
            state_file.write_text(
                '{"cloud_provider": "codex", "cloud_providers": {"codex": {"available": true, "retry_at": 0}}}\n'
            )

            with mock.patch.object(provider_switch, "STATE_FILE", state_file), mock.patch.object(
                provider_switch.time, "time", return_value=2000.0
            ):
                provider_switch.reset_cloud_state(
                    "claude",
                    ["claude", "codex"],
                    unavailable={"codex": (2300.0, "codex quota exhausted")},
                )

            state = provider_switch.load_json(state_file, {})

        self.assertEqual(state["runtime_mode"], "hybrid")
        self.assertEqual(state["cloud_provider"], "claude")
        self.assertEqual(state["cloud_provider_order"], ["claude", "codex"])
        self.assertEqual(state["cloud_providers"]["claude"]["available"], True)
        self.assertEqual(state["cloud_providers"]["codex"]["available"], False)
        self.assertEqual(state["cloud_providers"]["codex"]["retry_at"], 2300.0)
        self.assertEqual(state["cloud_providers"]["codex"]["reason"], "codex quota exhausted")

    def test_expired_unavailable_provider_becomes_available_in_router_state(self) -> None:
        from packet_garden.tools.router import _provider_available

        state = {"cloud_providers": {"codex": {"available": False, "retry_at": time.time() - 1}}}

        self.assertTrue(_provider_available(state, "codex"))
        self.assertEqual(state["cloud_providers"]["codex"]["retry_at"], 0)
        self.assertEqual(state["cloud_providers"]["codex"]["available"], True)


if __name__ == "__main__":
    unittest.main()
