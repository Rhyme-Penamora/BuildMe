# =============================================================================
# File: sandbox_game/ui/player_customize.py
# =============================================================================
"""
Player customization panel — name, speed, health, sprite, size.
"""

import os
import pygame
import pygame_gui
from typing import Optional, Callable
import settings


class PlayerCustomizePanel:
    """
    In-game panel for fully customizing the player entity.
    """

    def __init__(self, ui_manager: pygame_gui.UIManager):
        """
        Initialize player customization panel.

        Args:
            ui_manager: pygame_gui UIManager instance
        """
        self.ui_manager = ui_manager
        self.active = False
        self.player = None

        # Callback when sprite should be opened
        self.on_open_sprite_editor: Optional[Callable] = None

        sw = settings.SCREEN_WIDTH
        sh = settings.SCREEN_HEIGHT

        pw = int(sw * 0.42)
        ph = int(sh * 0.68)
        px = (sw - pw) // 2
        py = (sh - ph) // 2

        self.panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(px, py, pw, ph),
            manager=ui_manager,
            starting_layer_height=14
        )
        self.panel.hide()

        # Title
        self.title = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 8, pw - 20, 28),
            text="Customize Player",
            manager=ui_manager,
            container=self.panel
        )

        row_h = 36
        gap = 10
        lbl_w = 160
        entry_w = 160
        y = 46

        def _row(label_text: str) -> pygame_gui.elements.UITextEntryLine:
            """Helper: create a label+entry row, advance y, return entry."""
            nonlocal y
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(10, y, lbl_w, row_h),
                text=label_text,
                manager=ui_manager,
                container=self.panel
            )
            entry = pygame_gui.elements.UITextEntryLine(
                relative_rect=pygame.Rect(lbl_w + 20, y, entry_w, row_h),
                manager=ui_manager,
                container=self.panel
            )
            y += row_h + gap
            return entry

        self._name_entry  = _row("Player Name:")
        self._speed_entry = _row("Move Speed (px/s):")
        self._hp_entry    = _row("Max Health:")
        self._w_entry     = _row("Width (px):")
        self._h_entry     = _row("Height (px):")

        # Sprite button
        self._sprite_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, y, 180, 36),
            text="Change Sprite…",
            manager=ui_manager,
            container=self.panel
        )
        y += 46

        # Apply / Close
        self._apply_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, ph - 50, 110, 36),
            text="Apply",
            manager=ui_manager,
            container=self.panel
        )
        self._close_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(pw - 120, ph - 50, 110, 36),
            text="Close",
            manager=ui_manager,
            container=self.panel
        )

        # Status
        self._status = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(130, ph - 46, pw - 260, 30),
            text="",
            manager=ui_manager,
            container=self.panel
        )

    # ------------------------------------------------------------------
    # Show / hide
    # ------------------------------------------------------------------

    def show(self, player) -> None:
        """
        Open panel and populate fields from player state.

        Args:
            player: Player entity instance
        """
        self.player = player
        self.active = True

        self._name_entry.set_text(getattr(player, 'name', 'Player'))
        self._speed_entry.set_text(str(getattr(player, 'speed', settings.PLAYER_SPEED)))
        self._hp_entry.set_text(str(getattr(player, 'max_health', 100)))
        w, h = getattr(player, 'size', (settings.PLAYER_SIZE, settings.PLAYER_SIZE))
        self._w_entry.set_text(str(int(w)))
        self._h_entry.set_text(str(int(h)))

        self.panel.show()

    def hide(self) -> None:
        """Hide the panel."""
        self.active = False
        self.panel.hide()

    # ------------------------------------------------------------------
    # Apply changes
    # ------------------------------------------------------------------

    def _apply(self) -> None:
        """Read form fields and update player attributes."""
        if not self.player:
            return

        try:
            name = self._name_entry.get_text().strip()
            if name:
                self.player.name = name

            speed = float(self._speed_entry.get_text())
            self.player.speed = max(10.0, speed)

            max_hp = int(self._hp_entry.get_text())
            self.player.max_health = max(1, max_hp)
            if hasattr(self.player, 'health'):
                self.player.health = min(self.player.health, self.player.max_health)

            w = max(8, int(self._w_entry.get_text()))
            h = max(8, int(self._h_entry.get_text()))
            self.player.size = [w, h]

            self._status.set_text("Applied.")
        except ValueError as e:
            self._status.set_text(f"Error: {e}")

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle panel UI events.

        Args:
            event: pygame event

        Returns:
            True if event was consumed
        """
        if not self.active:
            return False

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self._close_btn:
                self.hide()
                return True
            if event.ui_element == self._apply_btn:
                self._apply()
                return True
            if event.ui_element == self._sprite_btn:
                if self.on_open_sprite_editor:
                    self.on_open_sprite_editor(self.player)
                return True

        return False
