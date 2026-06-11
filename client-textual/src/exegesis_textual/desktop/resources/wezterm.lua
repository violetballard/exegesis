local wezterm = require 'wezterm'
local mux = wezterm.mux

wezterm.on('format-window-title', function()
  return 'Exegesis'
end)

wezterm.on('gui-startup', function(cmd)
  local _, _, window = mux.spawn_window(cmd or {})
  window:gui_window():maximize()
end)

return {
  automatically_reload_config = false,
  check_for_updates = false,
  disable_default_key_bindings = true,
  enable_csi_u_key_encoding = true,
  enable_kitty_keyboard = true,
  font_size = 15.0,
  hide_tab_bar_if_only_one_tab = true,
  set_environment_variables = {
    EXEGESIS_TEXTUAL_RELEASE_MODE = '1',
    COLORTERM = 'truecolor',
    TERM = 'xterm-256color',
  },
  window_close_confirmation = 'NeverPrompt',
  window_decorations = 'TITLE | RESIZE',
  window_padding = {
    left = 0,
    right = 0,
    top = 0,
    bottom = 0,
  },
  initial_cols = 180,
  initial_rows = 54,
  keys = {
    { key = 'c', mods = 'CMD', action = wezterm.action.SendKey({ key = 'c', mods = 'CTRL' }) },
    { key = 'c', mods = 'SUPER', action = wezterm.action.SendKey({ key = 'c', mods = 'CTRL' }) },
    { key = 'c', mods = 'CTRL', action = wezterm.action.SendKey({ key = 'c', mods = 'CTRL' }) },
    { key = 'Insert', mods = 'CTRL', action = wezterm.action.SendKey({ key = 'c', mods = 'CTRL' }) },
    { key = 'x', mods = 'CMD', action = wezterm.action.SendKey({ key = 'x', mods = 'CTRL' }) },
    { key = 'x', mods = 'SUPER', action = wezterm.action.SendKey({ key = 'x', mods = 'CTRL' }) },
    { key = 'x', mods = 'CTRL', action = wezterm.action.SendKey({ key = 'x', mods = 'CTRL' }) },
    { key = 'v', mods = 'CMD', action = wezterm.action.SendKey({ key = 'v', mods = 'CTRL' }) },
    { key = 'v', mods = 'SUPER', action = wezterm.action.SendKey({ key = 'v', mods = 'CTRL' }) },
    { key = 'v', mods = 'CTRL', action = wezterm.action.SendKey({ key = 'v', mods = 'CTRL' }) },
    { key = 'Insert', mods = 'SHIFT', action = wezterm.action.SendKey({ key = 'v', mods = 'CTRL' }) },
    { key = 'q', mods = 'CMD', action = wezterm.action.SendKey({ key = 'q', mods = 'CTRL' }) },
    { key = 'q', mods = 'SUPER', action = wezterm.action.SendKey({ key = 'q', mods = 'CTRL' }) },
  },
}
