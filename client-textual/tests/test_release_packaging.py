from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import plistlib
import tempfile
import unittest
from unittest.mock import patch

from exegesis_textual.app import main as app_main
from exegesis_textual.desktop.launcher import TERMINAL_CHILD_ENV, build_wezterm_command, release_child_environment
from exegesis_textual.services.projects import (
    LOCAL_DEVELOPER_ENV,
    RELEASE_MODE_ENV,
    TEXTUAL_SETTINGS_PATH_ENV,
    is_local_developer_mode,
    textual_projects_dir,
    textual_settings_path,
)
from exegesis_textual.services.prompt_integrity import load_prompt_manifest, load_verified_prompt, prompt_sha256
from exegesis_textual.workflow.mistral_chat import (
    DEFAULT_SYSTEM_PROMPT_MANIFEST_PATH,
    DEFAULT_SYSTEM_PROMPT_PATH,
    MistralChatBackend,
)

ROOT = Path(__file__).resolve().parents[2]
WEZTERM_CONFIG = ROOT / "client-textual" / "src" / "exegesis_textual" / "desktop" / "resources" / "wezterm.lua"
TEXTUAL_REQUIREMENTS = ROOT / "client-textual" / "requirements.txt"
TEXTUAL_LAUNCHER = ROOT / "scripts" / "run-textual-shell.sh"


def _load_release_script(name: str):
    path = ROOT / "scripts" / "release" / name
    spec = importlib.util.spec_from_file_location(name.replace(".py", ""), path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


class ReleasePackagingTests(unittest.TestCase):
    def test_release_mode_disables_local_developer_settings_path(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            env = {
                LOCAL_DEVELOPER_ENV: "1",
                RELEASE_MODE_ENV: "1",
                "HOME": tempdir,
            }
            with patch.dict(os.environ, env, clear=True):
                self.assertFalse(is_local_developer_mode())
                self.assertNotIn(".codex", str(textual_settings_path(ROOT)))
                self.assertEqual(
                    textual_settings_path(ROOT),
                    Path(tempdir) / "Library" / "Application Support" / "Exegesis" / "settings.json",
                )

    def test_test_override_settings_path_still_supports_ci(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            settings = Path(tempdir) / "settings.json"
            with patch.dict(os.environ, {TEXTUAL_SETTINGS_PATH_ENV: str(settings)}, clear=True):
                self.assertEqual(textual_settings_path(ROOT), settings)

    def test_release_mode_defaults_projects_to_documents_exegesis(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            with patch.dict(os.environ, {RELEASE_MODE_ENV: "1", "HOME": tempdir}, clear=True):
                self.assertEqual(textual_projects_dir(ROOT), Path(tempdir) / "Documents" / "Exegesis")

    def test_non_release_default_projects_stays_home_exegesis(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            with patch.dict(os.environ, {"HOME": tempdir}, clear=True):
                self.assertEqual(textual_projects_dir(ROOT), Path(tempdir) / "exegesis")

    def test_release_child_environment_strips_dev_prompt_override(self) -> None:
        env = release_child_environment(
            {
                LOCAL_DEVELOPER_ENV: "1",
                "EXEGESIS_SYSTEM_PROMPT_PATH": "/tmp/bad-prompt.md",
                "NO_COLOR": "1",
            }
        )
        self.assertEqual(env[RELEASE_MODE_ENV], "1")
        self.assertEqual(env[TERMINAL_CHILD_ENV], "1")
        self.assertNotIn(LOCAL_DEVELOPER_ENV, env)
        self.assertNotIn("EXEGESIS_SYSTEM_PROMPT_PATH", env)
        self.assertNotIn("NO_COLOR", env)

    def test_wezterm_command_uses_config_and_python_module_when_using_python(self) -> None:
        command = build_wezterm_command(Path("/tmp/wezterm"), Path("/tmp/wezterm.lua"), Path("/tmp/python"))
        self.assertEqual(command[:3], ["/tmp/wezterm", "--config-file", "/tmp/wezterm.lua"])
        self.assertIn("--always-new-process", command)
        self.assertEqual(command[-3:], ["/tmp/python", "-m", "exegesis_textual.app.main"])

    def test_wezterm_command_does_not_pass_python_flags_to_briefcase_stub(self) -> None:
        command = build_wezterm_command(Path("/tmp/wezterm"), Path("/tmp/wezterm.lua"), Path("/tmp/Exegesis"))
        self.assertEqual(command[-1], "/tmp/Exegesis")
        self.assertNotIn("-m", command)

    def test_packaged_wezterm_config_keeps_title_bar_and_starts_maximized(self) -> None:
        config = WEZTERM_CONFIG.read_text(encoding="utf-8")
        self.assertIn("window_decorations = 'TITLE | RESIZE'", config)
        self.assertIn("gui-startup", config)
        self.assertIn(":maximize()", config)

    def test_packaged_wezterm_config_forwards_clipboard_shortcuts_to_textual(self) -> None:
        config = WEZTERM_CONFIG.read_text(encoding="utf-8")
        self.assertNotIn("PasteFrom('Clipboard')", config)
        self.assertIn("{ key = 'c', mods = 'CMD', action = wezterm.action.SendKey({ key = 'c', mods = 'CTRL' }) }", config)
        self.assertIn("{ key = 'c', mods = 'SUPER', action = wezterm.action.SendKey({ key = 'c', mods = 'CTRL' }) }", config)
        self.assertIn("{ key = 'x', mods = 'CMD', action = wezterm.action.SendKey({ key = 'x', mods = 'CTRL' }) }", config)
        self.assertIn("{ key = 'x', mods = 'SUPER', action = wezterm.action.SendKey({ key = 'x', mods = 'CTRL' }) }", config)
        self.assertIn("{ key = 'v', mods = 'CMD', action = wezterm.action.SendKey({ key = 'v', mods = 'CTRL' }) }", config)
        self.assertIn("{ key = 'v', mods = 'SUPER', action = wezterm.action.SendKey({ key = 'v', mods = 'CTRL' }) }", config)
        self.assertIn("{ key = 'Insert', mods = 'SHIFT', action = wezterm.action.SendKey({ key = 'v', mods = 'CTRL' }) }", config)

    def test_dev_launcher_checks_all_provider_sdk_dependencies(self) -> None:
        requirements = TEXTUAL_REQUIREMENTS.read_text(encoding="utf-8")
        launcher = TEXTUAL_LAUNCHER.read_text(encoding="utf-8")
        for package, import_line in (
            ("mistralai", "import mistralai"),
            ("openai", "import openai"),
            ("anthropic", "import anthropic"),
            ("google-genai", "from google import genai"),
        ):
            self.assertIn(package, requirements)
            self.assertIn(import_line, launcher)

    def test_prompt_manifest_matches_packaged_writer_prompt(self) -> None:
        identity = load_prompt_manifest(DEFAULT_SYSTEM_PROMPT_MANIFEST_PATH)
        self.assertEqual(identity.prompt_id, "exegesis.writer")
        self.assertEqual(identity.sha256, prompt_sha256(DEFAULT_SYSTEM_PROMPT_PATH))
        prompt, verified_identity = load_verified_prompt(
            DEFAULT_SYSTEM_PROMPT_PATH,
            DEFAULT_SYSTEM_PROMPT_MANIFEST_PATH,
            require_manifest=True,
        )
        self.assertIn("Exegesis", prompt)
        self.assertEqual(verified_identity, identity)

    def test_release_mode_ignores_prompt_override(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            bad_prompt = Path(tempdir) / "bad.md"
            bad_prompt.write_text("bad override", encoding="utf-8")
            with patch.dict(
                os.environ,
                {
                    LOCAL_DEVELOPER_ENV: "1",
                    RELEASE_MODE_ENV: "1",
                    "EXEGESIS_SYSTEM_PROMPT_PATH": str(bad_prompt),
                },
                clear=True,
            ):
                backend = MistralChatBackend()
                self.assertEqual(backend._system_prompt_path(), DEFAULT_SYSTEM_PROMPT_PATH)
                self.assertNotEqual(backend._load_system_prompt(), "bad override")

    def test_release_mode_blocks_demo_reset_entrypoint(self) -> None:
        with patch.dict(os.environ, {RELEASE_MODE_ENV: "1"}, clear=True):
            with self.assertRaises(SystemExit):
                app_main.main(["--reset-demo-project"])

    def test_public_manifest_rejects_internal_paths(self) -> None:
        export_public_source = _load_release_script("export_public_source.py")
        manifest = export_public_source.load_manifest()
        export_public_source.included_paths(manifest)
        self.assertTrue(export_public_source._is_denied(Path(".codex/shell/settings.json"), manifest))
        self.assertTrue(export_public_source._is_denied(Path("packet_garden/daemon.py"), manifest))
        self.assertFalse(export_public_source._is_denied(Path("client-textual/src/exegesis_textual/app/main.py"), manifest))

    def test_iconset_has_required_sources(self) -> None:
        build_app_icon = _load_release_script("build_app_icon.py")
        build_app_icon.validate_iconset()

    def test_identity_patcher_rewrites_visible_wezterm_names(self) -> None:
        patcher = _load_release_script("patch_macos_app_identity.py")
        with tempfile.TemporaryDirectory() as tempdir:
            app = Path(tempdir) / "Exegesis.app"
            contents = app / "Contents"
            resources = contents / "Resources" / "WezTerm.app" / "Contents"
            resources.mkdir(parents=True)
            top = contents / "Info.plist"
            nested = resources / "Info.plist"
            for plist_path in (top, nested):
                with plist_path.open("wb") as handle:
                    plistlib.dump(
                        {
                            "CFBundleName": "WezTerm",
                            "CFBundleDisplayName": "WezTerm",
                            "CFBundleIdentifier": "com.github.wez.wezterm",
                            "CFBundleIconFile": "terminal",
                        },
                        handle,
                    )
            patcher.patch_app_bundle(app)
            patcher.assert_no_visible_wezterm_identity(app)
            with top.open("rb") as handle:
                payload = plistlib.load(handle)
            self.assertEqual(payload["CFBundleName"], "Exegesis")
            self.assertEqual(payload["CFBundleDisplayName"], "Exegesis")
            self.assertEqual(payload["CFBundleIdentifier"], "studio.exegesis.developer")

    def test_release_readiness_audit_passes_for_tracked_release_inputs(self) -> None:
        audit = _load_release_script("audit_release_readiness.py")
        audit.audit_release_readiness()


if __name__ == "__main__":
    unittest.main()
