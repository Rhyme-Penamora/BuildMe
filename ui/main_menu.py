# =============================================================================
# File: sandbox_game/ui/main_menu.py
# =============================================================================
"""
Main menu — modern dark UI with world list and management.
"""

import pygame
import pygame_gui
from typing import Optional, Callable, List, Dict
from ui.popup import Popup
import settings


class MainMenu:
    """Modern main menu with world selection."""

    def __init__(self, screen: pygame.Surface, ui_manager: pygame_gui.UIManager):
        self.screen = screen
        self.ui_manager = ui_manager
        self.active = True
        self.selected_world: Optional[str] = None
        self.on_world_selected: Optional[Callable] = None
        self.on_new_world: Optional[Callable] = None
        self.on_delete_world: Optional[Callable] = None
        self.current_popup: Optional[Popup] = None
        self._new_world_window: Optional[pygame_gui.elements.UIWindow] = None
        self._new_world_entry = None
        self._new_world_confirm = None

        sw = settings.SCREEN_WIDTH
        sh = settings.SCREEN_HEIGHT

        # Title
        self.title_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, int(sh * 0.06), sw, int(sh * 0.09)),
            text="BUILD ME",
            manager=ui_manager
        )

        self.subtitle_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, int(sh * 0.15), sw, int(sh * 0.05)),
            text="Programmable Sandbox Engine",
            manager=ui_manager
        )

        # World list panel
        panel_w = int(sw * 0.42)
        panel_h = int(sh * 0.55)
        panel_x = (sw - panel_w) // 2
        panel_y = int(sh * 0.23)

        self.world_list = pygame_gui.elements.UISelectionList(
            relative_rect=pygame.Rect(panel_x, panel_y, panel_w, panel_h),
            item_list=[],
            manager=ui_manager
        )

        # Buttons
        btn_w = int(panel_w * 0.3)
        btn_h = 48
        gap = 12
        total = btn_w * 3 + gap * 2
        bx = (sw - total) // 2
        by = panel_y + panel_h + 18

        self.new_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(bx, by, btn_w, btn_h),
            text="New World",
            manager=ui_manager
        )
        self.load_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(bx + btn_w + gap, by, btn_w, btn_h),
            text="Play",
            manager=ui_manager
        )
        self.delete_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(bx + (btn_w + gap) * 2, by, btn_w, btn_h),
            text="Delete",
            manager=ui_manager
        )

        # Version label
        self.version_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, sh - 32, sw, 28),
            text="v1.0  |  Python 3.9  |  pygame-ce",
            manager=ui_manager
        )

    def populate_world_list(self, worlds: List[Dict]) -> None:
        import time as _t
        items = []
        for w in worlds:
            lp = _t.strftime("%Y-%m-%d", _t.localtime(w.get('last_played', 0)))
            items.append(f"{w['name']}   (last played: {lp})")
        self._world_names = [w['name'] for w in worlds]
        self.world_list.set_item_list(items)

    def _get_selected_name(self) -> Optional[str]:
        sel = self.world_list.get_single_selection()
        if sel is None:
            return None
        idx = self.world_list.item_list.index({'text': sel, 'selected': True}) if False else None
        # Match by index in display list
        try:
            display_items = [
                item['text'] if isinstance(item, dict) else item
                for item in self.world_list.item_list
            ]
            i = display_items.index(sel)
            return self._world_names[i] if i < len(self._world_names) else sel
        except (ValueError, AttributeError):
            # Fallback: strip the last-played suffix
            return sel.split("   (")[0].strip()

    def handle_event(self, event: pygame.event.Event) -> bool:
        if self.current_popup and self.current_popup.active:
            if self.current_popup.handle_event(event):
                return True
            if not self.current_popup.active:
                self.current_popup = None

        if (self._new_world_window is not None and
                event.type == pygame_gui.UI_BUTTON_PRESSED and
                event.ui_element == self._new_world_confirm):
            self._submit_new_world()
            return True

        if (self._new_world_window is not None and
                event.type == pygame_gui.UI_WINDOW_CLOSE and
                event.ui_element == self._new_world_window):
            self._new_world_window = None
            self._new_world_entry = None
            self._new_world_confirm = None
            return True

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.new_button:
                self._show_new_world_dialog()
                return True

            if event.ui_element == self.load_button:
                name = self._get_selected_name()
                if name:
                    self.selected_world = name
                    if self.on_world_selected:
                        self.on_world_selected(name)
                    self.active = False
                return True

            if event.ui_element == self.delete_button:
                name = self._get_selected_name()
                if name:
                    self._show_delete_confirmation(name)
                return True

        if event.type == pygame_gui.UI_SELECTION_LIST_DOUBLE_CLICKED_SELECTION:
            if event.ui_element == self.world_list:
                name = event.text.split("   (")[0].strip()
                self.selected_world = name
                if self.on_world_selected:
                    self.on_world_selected(name)
                self.active = False
                return True

        return False

    def _show_new_world_dialog(self) -> None:
        if self._new_world_window is not None:
            return
        sw = settings.SCREEN_WIDTH
        sh = settings.SCREEN_HEIGHT
        ww, wh = int(sw * 0.32), 160
        self._new_world_window = pygame_gui.elements.UIWindow(
            rect=pygame.Rect((sw - ww) // 2, (sh - wh) // 2, ww, wh),
            manager=self.ui_manager,
            window_display_title="New World"
        )
        self._new_world_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(10, 10, ww - 30, 40),
            manager=self.ui_manager,
            container=self._new_world_window
        )
        self._new_world_entry.set_text("My World")
        self._new_world_confirm = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, 58, ww - 30, 40),
            text="Create",
            manager=self.ui_manager,
            container=self._new_world_window
        )

    def _submit_new_world(self) -> None:
        if self._new_world_entry is None:
            return
        name = self._new_world_entry.get_text().strip()
        if name and self.on_new_world:
            self.on_new_world(name)
        if self._new_world_window:
            self._new_world_window.kill()
        self._new_world_window = None
        self._new_world_entry = None
        self._new_world_confirm = None

    def _show_delete_confirmation(self, world_name: str) -> None:
        def confirm():
            if self.on_delete_world:
                self.on_delete_world(world_name)
        self.current_popup = Popup(
            self.ui_manager,
            "Delete World",
            f"Delete '{world_name}'? This cannot be undone.",
            on_confirm=confirm,
            confirm_text="Delete"
        )

    def cleanup(self) -> None:
        self.title_label.kill()
        self.subtitle_label.kill()
        self.world_list.kill()
        self.new_button.kill()
        self.load_button.kill()
        self.delete_button.kill()
        self.version_label.kill()
        if self._new_world_window:
            self._new_world_window.kill()
        if self.current_popup and self.current_popup.active:
            self.current_popup.dialog.kill()
