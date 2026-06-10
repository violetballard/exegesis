from __future__ import annotations

import importlib
import unittest
from unittest.mock import patch

app_main = importlib.import_module("exegesis_textual.app.main")


class TextualAppMainTests(unittest.TestCase):
    def test_restart_result_returns_launcher_restart_code(self) -> None:
        with patch.object(app_main, "QualShellApp") as app_cls:
            app_cls.return_value.run.return_value = "restart"

            self.assertEqual(app_main.main([]), 75)

    def test_normal_exit_returns_success(self) -> None:
        with patch.object(app_main, "QualShellApp") as app_cls:
            app_cls.return_value.run.return_value = None

            self.assertEqual(app_main.main([]), 0)


if __name__ == "__main__":
    unittest.main()
