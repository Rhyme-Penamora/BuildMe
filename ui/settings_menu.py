# =============================================================================
# File: sandbox_game/ui/settings_menu.py
# =============================================================================
"""
Full settings menu: display, controls, mobile, game rules, world, audio, UI.
"""

import os
import json
import pygame
import pygame_gui
from typing import Optional, Callable, Dict, Any
import settings

MIN_BTN = 48


class SettingsMenu:
    """
    Multi-tab settings menu covering all configurable game options.
    """

    _TABS = ["Display", "Controls", "Mobile", "Game Rules", "World", "Audio", "UI"]

    def __init__(self, ui_manager: pygame_gui.UIManager):
        """
        Initialize settings menu.

        Args:
            ui_manager: pygame_gui UIManager instance
        """
        self.ui_manager = ui_manager
        self.active = False
        self._current_tab = "Display"

        self._keybindings: Dict[str, int] = dict(settings.KEYBINDINGS)
        self._game_rules: Dict[str, bool] = dict(settings.GAME_RULES)
        self._global: Dict[str, Any] = dict(settings.GLOBAL_SETTINGS)

        self.on_apply: Optional[Callable[[Dict, Dict, Dict], None]] = None
        self.on_close: Optional[Callable] = None

        self._remapping_action: Optional[str] = None

        sw = settings.SCREEN_WIDTH
        sh = settings.SCREEN_HEIGHT

        pw = int(sw * 0.72)
        ph = int(sh * 0.82)
        px = (sw - pw) // 2
        py = (sh - ph) // 2

        self.panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(px, py, pw, ph),
            manager=ui_manager
        )
        self.panel.hide()

        self.title_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 8, pw - 20, 28),
            text="Settings",
            manager=ui_manager,
            container=self.panel
        )

        tab_w = max(80, (pw - 20) // len(self._TABS))
        for i, tab in enumerate(self._TABS):
            btn = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(
                    10 + i * tab_w, 44, tab_w - 4, 30
                ),
                text=tab,
                manager=ui_manager,
                container=self.panel
            )
            setattr(self, f"_tab_btn_{tab.lower().replace(' ', '_')}", btn)

        content_y = 84
        content_h = ph - content_y - 56
        self._content_rect = pygame.Rect(10, content_y, pw - 20, content_h)

        self.content_box = pygame_gui.elements.UITextBox(
            html_text="<font size=3>Select a tab.</font>",
            relative_rect=self._content_rect,
            manager=ui_manager,
            container=self.panel
        )

        self._dynamic_elements = []

        btn_y = ph - 48
        self.apply_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, btn_y, 110, 38),
            text="Apply",
            manager=ui_manager,
            container=self.panel
        )
        self.close_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(pw - 120, btn_y, 110, 38),
            text="Close",
            manager=ui_manager,
            container=self.panel
        )

        self.status_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(130, btn_y + 4, pw - 270, 30),
            text="",
            manager=ui_manager,
            container=self.panel
        )

    def show(self, tab: str = "Display") -> None:
        """
        Show settings menu on the given tab.

        Args:
            tab: Initial tab to display
        """
        self.active = True
        self._keybindings = dict(settings.KEYBINDINGS)
        self._game_rules = dict(settings.GAME_RULES)
        self._global = dict(settings.GLOBAL_SETTINGS)
        self._switch_tab(tab)
        self.panel.show()

    def hide(self) -> None:
        """Hide settings menu."""
        self.active = False
        self._remapping_action = None
        self.panel.hide()
        self._clear_dynamic()

    def toggle(self) -> None:
        """Toggle settings menu visibility."""
        if self.active:
            self.hide()
        else:
            self.show()

    def _switch_tab(self, tab: str) -> None:
        """
        Switch to a tab and rebuild dynamic content.

        Args:
            tab: Tab name string
        """
        self._current_tab = tab
        self._clear_dynamic()
        self._remapping_action = None

        builders = {
            "Display":    self._build_display_tab,
            "Controls":   self._build_controls_tab,
            "Mobile":     self._build_mobile_tab,
            "Game Rules": self._build_game_rules_tab,
            "World":      self._build_world_tab,
            "Audio":      self._build_audio_tab,
            "UI":         self._build_ui_tab,
        }
        builder = builders.get(tab)
        if builder:
            builder()

    def _clear_dynamic(self) -> None:
        """Destroy all dynamically created UI elements."""
        for el in self._dynamic_elements:
            try:
                el.kill()
            except Exception:
                pass
        self._dynamic_elements.clear()

    def _make_label(self, text: str, y: int, x: int = 10) -> pygame_gui.elements.UILabel:
        """
        Create a label inside the content area.

        Args:
            text: Label text
            y: Y offset inside content area
            x: X offset inside content area

        Returns:
            Created UILabel
        """
        pw = int(settings.SCREEN_WIDTH * 0.72)
        lbl = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(
                self._content_rect.x + x,
                self._content_rect.y + y,
                pw - 40,
                26
            ),
            text=text,
            manager=self.ui_manager,
            container=self.panel
        )
        self._dynamic_elements.append(lbl)
        return lbl

    def _make_button(
        self, text: str, y: int, x: int = 10, w: int = 180, h: int = 32
    ) -> pygame_gui.elements.UIButton:
        """
        Create a button inside the content area.

        Args:
            text: Button label
            y: Y offset in content area
            x: X offset in content area
            w: Width
            h: Height

        Returns:
            Created UIButton
        """
        btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(
                self._content_rect.x + x,
                self._content_rect.y + y,
                w, h
            ),
            text=text,
            manager=self.ui_manager,
            container=self.panel
        )
        self._dynamic_elements.append(btn)
        return btn

    def _make_entry(
        self, default: str, y: int, x: int = 200, w: int = 120
    ) -> pygame_gui.elements.UITextEntryLine:
        """
        Create a text entry inside the content area.

        Args:
            default: Default text value
            y: Y offset in content area
            x: X offset in content area
            w: Width

        Returns:
            Created UITextEntryLine
        """
        entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(
                self._content_rect.x + x,
                self._content_rect.y + y,
                w, 30
            ),
            manager=self.ui_manager,
            container=self.panel
        )
        entry.set_text(default)
        self._dynamic_elements.append(entry)
        return entry

    def _build_display_tab(self) -> None:
        """Build Display settings tab controls."""
        y = 4
        self._make_label("Display Settings", y)
        y += 32
        self._make_label(
            f"Fullscreen: {'ON' if self._global.get('fullscreen') else 'OFF'}", y
        )
        self._fs_toggle = self._make_button("Toggle Fullscreen", y, x=240, w=170)
        y += 38
        self._make_label(f"Target FPS: {self._global.get('target_fps', 60)}", y)
        self._fps_entry = self._make_entry(
            str(self._global.get('target_fps', 60)), y, x=200, w=80
        )
        y += 38
        self._make_label("Resolution: 1280x720 (fixed)", y)

    def _build_controls_tab(self) -> None:
        """Build Controls (keybinding remapping) tab."""
        y = 4
        self._make_label("Click an action then press a new key to remap.", y)
        y += 32

        self._kb_buttons: Dict[str, pygame_gui.elements.UIButton] = {}
        for action, key_const in self._keybindings.items():
            key_name = pygame.key.name(key_const).upper()
            lbl_text = f"{action:<20} →  {key_name}"
            if self._remapping_action == action:
                lbl_text = f"{action:<20} →  [ press any key ]"
            btn = self._make_button(lbl_text, y, x=10, w=340, h=28)
            self._kb_buttons[action] = btn
            y += 34
            if y > self._content_rect.height - 40:
                break

    def _build_mobile_tab(self) -> None:
        """Build Mobile controls settings tab."""
        y = 4
        self._make_label("Mobile / Virtual Controls", y)
        y += 32
        mob_state = "ON" if self._global.get('mobile_controls') else "OFF"
        self._make_label(f"Virtual controls: {mob_state}", y)
        self._mob_toggle = self._make_button("Toggle Mobile Controls", y, x=240, w=200)
        y += 38
        self._make_label(f"D-pad size: {self._global.get('dpad_size', 80)}px", y)
        self._dpad_entry = self._make_entry(
            str(self._global.get('dpad_size', 80)), y, x=200, w=80
        )
        y += 38
        self._make_label(
            f"Action button size: {self._global.get('action_btn_size', 64)}px", y
        )
        self._abtn_entry = self._make_entry(
            str(self._global.get('action_btn_size', 64)), y, x=240, w=80
        )
        y += 38
        self._make_label("Changes take effect after Apply.", y)

    def _build_game_rules_tab(self) -> None:
        """Build Game Rules toggles tab."""
        y = 4
        self._make_label("Game Rules (changes apply immediately)", y)
        y += 32

        self._rule_buttons: Dict[str, pygame_gui.elements.UIButton] = {}
        for rule, value in self._game_rules.items():
            state = "ON" if value else "OFF"
            btn = self._make_button(
                f"{rule.replace('_', ' ').title()}: {state}",
                y, x=10, w=280, h=32
            )
            self._rule_buttons[rule] = btn
            y += 40

    def _build_world_tab(self) -> None:
        """Build World settings tab."""
        y = 4
        self._make_label("World Settings", y)
        y += 32
        self._make_label("Auto-save interval (seconds):", y)
        self._autosave_entry = self._make_entry("60", y, x=260, w=80)
        y += 38
        self._make_label("World expansion limit (tiles):", y)
        self._expand_entry = self._make_entry("200", y, x=260, w=80)
        y += 38
        self._make_label("Entity spawn limit:", y)
        self._spawn_limit_entry = self._make_entry("100", y, x=200, w=80)
        y += 38
        self._make_label("Inventory slot count:", y)
        self._inv_slots_entry = self._make_entry("20", y, x=200, w=80)

    def _build_audio_tab(self) -> None:
        """Build Audio settings tab."""
        y = 4
        self._make_label("Audio Settings", y)
        y += 32
        vol_pct = int(self._global.get('volume', 1.0) * 100)
        self._make_label(f"Master Volume: {vol_pct}%", y)
        self._vol_entry = self._make_entry(str(vol_pct), y, x=200, w=80)
        y += 38
        self._make_label("(Audio system reserved for future update)", y)

    def _build_ui_tab(self) -> None:
        """Build UI / theme settings tab."""
        y = 4
        self._make_label("UI & Theme Settings", y)
        y += 32
        self._make_label(f"Font scale: {self._global.get('font_scale', 1.0)}", y)
        self._font_scale_entry = self._make_entry(
            str(self._global.get('font_scale', 1.0)), y, x=160, w=80
        )
        y += 38
        self._make_label("HUD Editor — toggle HUD elements:", y)
        y += 28
        self._hud_mode_btn   = self._make_button("HUD: show mode",     y, x=10, w=200)
        y += 36
        self._hud_pos_btn    = self._make_button("HUD: show position",  y, x=10, w=200)
        y += 36
        self._hud_tile_btn   = self._make_button("HUD: show tile",      y, x=10, w=200)
        y += 36
        self._hud_health_btn = self._make_button("HUD: show health",    y, x=10, w=200)

    def _apply_settings(self) -> None:
        """Read all dynamic UI elements and persist settings."""
        try:
            fps_e = getattr(self, '_fps_entry', None)
            if fps_e:
                self._global['target_fps'] = max(10, int(fps_e.get_text()))
        except (ValueError, AttributeError):
            pass

        try:
            dpad_e = getattr(self, '_dpad_entry', None)
            if dpad_e:
                self._global['dpad_size'] = max(MIN_BTN, int(dpad_e.get_text()))
        except (ValueError, AttributeError):
            pass

        try:
            abtn_e = getattr(self, '_abtn_entry', None)
            if abtn_e:
                self._global['action_btn_size'] = max(MIN_BTN, int(abtn_e.get_text()))
        except (ValueError, AttributeError):
            pass

        try:
            vol_e = getattr(self, '_vol_entry', None)
            if vol_e:
                self._global['volume'] = max(
                    0.0, min(1.0, int(vol_e.get_text()) / 100.0)
                )
        except (ValueError, AttributeError):
            pass

        try:
            fs_e = getattr(self, '_font_scale_entry', None)
            if fs_e:
                self._global['font_scale'] = max(
                    0.5, min(3.0, float(fs_e.get_text()))
                )
        except (ValueError, AttributeError):
            pass

        settings.KEYBINDINGS.update(self._keybindings)
        settings.GAME_RULES.update(self._game_rules)
        settings.GLOBAL_SETTINGS.update(self._global)

        self._save_global()
        self.status_label.set_text("Settings applied.")

        if self.on_apply:
            self.on_apply(self._keybindings, self._game_rules, self._global)

    def _save_global(self) -> None:
        """Write global settings to settings.json."""
        data = {
            'keybindings': {k: v for k, v in self._keybindings.items()},
            'game_rules':  self._game_rules,
            'global':      self._global,
        }
        try:
            with open("settings.json", 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Settings save error: {e}")

    def load_global(self) -> None:
        """Load settings from settings.json if it exists."""
        try:
            if os.path.exists("settings.json"):
                with open("settings.json", 'r') as f:
                    data = json.load(f)
                for action, key in data.get('keybindings', {}).items():
                    if action in settings.KEYBINDINGS:
                        settings.KEYBINDINGS[action] = int(key)
                for rule, val in data.get('game_rules', {}).items():
                    if rule in settings.GAME_RULES:
                        settings.GAME_RULES[rule] = bool(val)
                for key, val in data.get('global', {}).items():
                    if key in settings.GLOBAL_SETTINGS:
                        settings.GLOBAL_SETTINGS[key] = val
        except Exception as e:
            print(f"Settings load error: {e}")

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle all settings menu UI events.

        Args:
            event: pygame event

        Returns:
            True if event was consumed
        """
        if not self.active:
            return False

        if self._remapping_action and event.type == pygame.KEYDOWN:
            self._keybindings[self._remapping_action] = event.key
            settings.KEYBINDINGS[self._remapping_action] = event.key
            self._remapping_action = None
            self._switch_tab("Controls")
            self.status_label.set_text("Key remapped.")
            return True

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.close_button:
                self.hide()
                if self.on_close:
                    self.on_close()
                return True

            if event.ui_element == self.apply_button:
                self._apply_settings()
                return True

            for tab in self._TABS:
                attr = f"_tab_btn_{tab.lower().replace(' ', '_')}"
                btn = getattr(self, attr, None)
                if btn and event.ui_element == btn:
                    self._switch_tab(tab)
                    return True

            if hasattr(self, '_fs_toggle') and event.ui_element == self._fs_toggle:
                self._global['fullscreen'] = not self._global.get('fullscreen', False)
                self._switch_tab("Display")
                return True

            if hasattr(self, '_mob_toggle') and event.ui_element == self._mob_toggle:
                self._global['mobile_controls'] = not self._global.get(
                    'mobile_controls', False
                )
                self._switch_tab("Mobile")
                return True

            if hasattr(self, '_kb_buttons'):
                for action, btn in self._kb_buttons.items():
                    if event.ui_element == btn:
                        self._remapping_action = action
                        self._switch_tab("Controls")
                        return True

            if hasattr(self, '_rule_buttons'):
                for rule, btn in self._rule_buttons.items():
                    if event.ui_element == btn:
                        self._game_rules[rule] = not self._game_rules[rule]
                        settings.GAME_RULES[rule] = self._game_rules[rule]
                        self._switch_tab("Game Rules")
                        return True

            from core.event_bus import event_bus
            hud_map = {
                '_hud_mode_btn':   'hud_toggle_mode',
                '_hud_pos_btn':    'hud_toggle_position',
                '_hud_tile_btn':   'hud_toggle_tile',
                '_hud_health_btn': 'hud_toggle_health',
            }
            for attr, ev_name in hud_map.items():
                btn = getattr(self, attr, None)
                if btn and event.ui_element == btn:
                    event_bus.publish(ev_name)
                    return True

        return False
