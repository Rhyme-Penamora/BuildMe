# =============================================================================
# File: sandbox_game/ui/main_menu.py
# =============================================================================
"""
Main menu for world selection and management.
"""

import pygame
import pygame_gui
from typing import Optional, Callable, List, Dict
from ui.popup import Popup
import settings


class MainMenu:
    """
    Main menu screen showing available worlds with create/load/delete options.
    """

    def __init__(self, screen: pygame.Surface, ui_manager: pygame_gui.UIManager):
        """
        Initialize main menu.

        Args:
            screen: Main pygame display surface
            ui_manager: pygame_gui UIManager instance
        """
        self.screen = screen
        self.ui_manager = ui_manager
        self.active = True
        self.selected_world: Optional[str] = None
        self.on_world_selected: Optional[Callable] = None
        self.on_new_world: Optional[Callable] = None
        self.on_delete_world: Optional[Callable] = None
        self.current_popup: Optional[Popup] = None
        self._new_world_window: Optional[pygame_gui.elements.UIWindow] = None
        self._new_world_entry: Optional[pygame_gui.elements.UITextEntryLine] = None
        self._new_world_confirm: Optional[pygame_gui.elements.UIButton] = None

        sw = settings.SCREEN_WIDTH
        sh = settings.SCREEN_HEIGHT

        # Title label
        self.title_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, int(sh * 0.05), sw, int(sh * 0.1)),
            text=settings.GAME_TITLE,
            manager=ui_manager
        )

        # World list (centered, 40% width, 50% height)
        list_w = int(sw * 0.4)
        list_h = int(sh * 0.5)
        list_x = (sw - list_w) // 2
        list_y = int(sh * 0.2)

        self.world_list = pygame_gui.elements.UISelectionList(
            relative_rect=pygame.Rect(list_x, list_y, list_w, list_h),
            item_list=[],
            manager=ui_manager
        )

        # Buttons row below the list
        btn_w = int(list_w * 0.3)
        btn_h = 50
        gap = 15
        total_btn_w = btn_w * 3 + gap * 2
        btn_start_x = (sw - total_btn_w) // 2
        btn_y = list_y + list_h + 20

        self.new_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(btn_start_x, btn_y, btn_w, btn_h),
            text="New World",
            manager=ui_manager
        )
        self.load_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(btn_start_x + btn_w + gap, btn_y, btn_w, btn_h),
            text="Load World",
            manager=ui_manager
        )
        self.delete_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(btn_start_x + (btn_w + gap) * 2, btn_y, btn_w, btn_h),
            text="Delete World",
            manager=ui_manager
        )

    def populate_world_list(self, worlds: List[Dict]) -> None:
        """
        Populate the world selection list.

        Args:
            worlds: List of world metadata dicts (must contain 'name')
        """
        self.world_list.set_item_list([w['name'] for w in worlds])

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle all UI events for the main menu.

        Args:
            event: pygame event

        Returns:
            True if event was consumed
        """
        # Popup gets priority
        if self.current_popup and self.current_popup.active:
            if self.current_popup.handle_event(event):
                return True
            if not self.current_popup.active:
                self.current_popup = None

        # New world window confirm button
        if (self._new_world_window is not None and
                event.type == pygame_gui.UI_BUTTON_PRESSED and
                event.ui_element == self._new_world_confirm):
            self._submit_new_world()
            return True

        # New world window closed via X
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
                selected = self.world_list.get_single_selection()
                if selected:
                    self.selected_world = selected
                    if self.on_world_selected:
                        self.on_world_selected(selected)
                    self.active = False
                return True

            if event.ui_element == self.delete_button:
                selected = self.world_list.get_single_selection()
                if selected:
                    self._show_delete_confirmation(selected)
                return True

        if event.type == pygame_gui.UI_SELECTION_LIST_DOUBLE_CLICKED_SELECTION:
            if event.ui_element == self.world_list:
                self.selected_world = event.text
                if self.on_world_selected:
                    self.on_world_selected(event.text)
                self.active = False
                return True

        return False

    def _show_new_world_dialog(self) -> None:
        """Open a small window with a text entry for the new world name."""
        if self._new_world_window is not None:
            return  # Already open

        sw = settings.SCREEN_WIDTH
        sh = settings.SCREEN_HEIGHT
        win_w = int(sw * 0.3)
        win_h = 160
        win_x = (sw - win_w) // 2
        win_y = (sh - win_h) // 2

        self._new_world_window = pygame_gui.elements.UIWindow(
            rect=pygame.Rect(win_x, win_y, win_w, win_h),
            manager=self.ui_manager,
            window_display_title="New World"
        )

        # Text entry inside the window
        self._new_world_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(10, 10, win_w - 30, 40),
            manager=self.ui_manager,
            container=self._new_world_window
        )
        self._new_world_entry.set_text("New World")

        # Confirm button
        self._new_world_confirm = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, 60, win_w - 30, 40),
            text="Create",
            manager=self.ui_manager,
            container=self._new_world_window
        )

    def _submit_new_world(self) -> None:
        """Read the name entry and call on_new_world callback."""
        if self._new_world_entry is None:
            return

        name = self._new_world_entry.get_text().strip()
        if name and self.on_new_world:
            self.on_new_world(name)

        # Close window
        if self._new_world_window:
            self._new_world_window.kill()
        self._new_world_window = None
        self._new_world_entry = None
        self._new_world_confirm = None

    def _show_delete_confirmation(self, world_name: str) -> None:
        """
        Show confirmation popup before deleting a world.

        Args:
            world_name: Name of world to delete
        """
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
        """Destroy all UI elements belonging to this menu."""
        self.title_label.kill()
        self.world_list.kill()
        self.new_button.kill()
        self.load_button.kill()
        self.delete_button.kill()
        if self._new_world_window:
            self._new_world_window.kill()
        if self.current_popup and self.current_popup.active:
            self.current_popup.dialog.kill()
