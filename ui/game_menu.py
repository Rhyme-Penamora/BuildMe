# =============================================================================
# File: sandbox_game/ui/game_menu.py
# =============================================================================
"""
In-game ESC menu — extended for Phase 5 with all required options.
"""

import pygame
import pygame_gui
from typing import Optional, Callable
import settings


class GameMenu:
    """
    In-game pause/game menu with all Phase 5 options wired up.
    """

    def __init__(self, ui_manager: pygame_gui.UIManager):
        """
        Initialize game menu.

        Args:
            ui_manager: pygame_gui UIManager instance
        """
        self.ui_manager = ui_manager
        self.active = False

        # Callbacks (set by Game after init)
        self.on_save:             Optional[Callable] = None
        self.on_load:             Optional[Callable] = None
        self.on_settings:         Optional[Callable] = None
        self.on_help:             Optional[Callable] = None
        self.on_file_editor:      Optional[Callable] = None
        self.on_tutorial:         Optional[Callable] = None
        self.on_customize_player: Optional[Callable] = None
        self.on_exit_to_menu:     Optional[Callable] = None

        sw = settings.SCREEN_WIDTH
        sh = settings.SCREEN_HEIGHT

        panel_w = int(sw * 0.28)
        panel_h = int(sh * 0.74)
        panel_x = (sw - panel_w) // 2
        panel_y = (sh - panel_h) // 2

        self.panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(panel_x, panel_y, panel_w, panel_h),
            manager=ui_manager,
            starting_layer_height=10
        )
        self.panel.hide()

        # Title
        self.title_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 12, panel_w, 32),
            text="Game Menu",
            manager=ui_manager,
            container=self.panel
        )

        # Button layout
        btn_w = int(panel_w * 0.82)
        btn_h = 44
        gap = 10
        bx = (panel_w - btn_w) // 2
        by = 54

        button_defs = [
            ("Resume",            "resume"),
            ("Save World",        "save"),
            ("Settings",          "settings"),
            ("Help",              "help"),
            ("File Editor",       "file_editor"),
            ("Tutorial",          "tutorial"),
            ("Customize Player",  "customize_player"),
            ("Exit to Main Menu", "exit"),
        ]

        self._buttons = {}
        for label, key in button_defs:
            btn = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(bx, by, btn_w, btn_h),
                text=label,
                manager=ui_manager,
                container=self.panel
            )
            self._buttons[key] = btn
            by += btn_h + gap

    # ------------------------------------------------------------------
    # Show / hide / toggle
    # ------------------------------------------------------------------

    def show(self) -> None:
        """Show game menu."""
        self.active = True
        self.panel.show()

    def hide(self) -> None:
        """Hide game menu."""
        self.active = False
        self.panel.hide()

    def toggle(self) -> None:
        """Toggle game menu visibility."""
        if self.active:
            self.hide()
        else:
            self.show()

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle button events for the game menu.

        Args:
            event: pygame event

        Returns:
            True if event was consumed
        """
        if not self.active:
            return False

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            btn = event.ui_element

            if btn == self._buttons.get('resume'):
                self.hide()
                return True

            if btn == self._buttons.get('save'):
                if self.on_save:
                    self.on_save()
                self.hide()
                return True

            if btn == self._buttons.get('settings'):
                if self.on_settings:
                    self.on_settings()
                return True

            if btn == self._buttons.get('help'):
                if self.on_help:
                    self.on_help()
                return True

            if btn == self._buttons.get('file_editor'):
                if self.on_file_editor:
                    self.on_file_editor()
                self.hide()
                return True

            if btn == self._buttons.get('tutorial'):
                if self.on_tutorial:
                    self.on_tutorial()
                self.hide()
                return True

            if btn == self._buttons.get('customize_player'):
                if self.on_customize_player:
                    self.on_customize_player()
                return True

            if btn == self._buttons.get('exit'):
                if self.on_exit_to_menu:
                    self.on_exit_to_menu()
                self.hide()
                return True

        return False
