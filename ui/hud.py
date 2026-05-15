# =============================================================================
# File: sandbox_game/ui/hud.py
# =============================================================================
"""
Heads-up display — supports element visibility toggles and health bar.
All positions are relative to screen size (no hardcoded pixel coords).
"""

import pygame
from typing import Tuple, Optional
import settings
from core.event_bus import event_bus


class HUD:
    """
    In-game HUD with toggleable elements and health bar.
    Subscribes to event bus for visibility toggle events from settings menu.
    """

    def __init__(self, screen: pygame.Surface):
        """
        Initialize HUD.

        Args:
            screen: Main pygame display surface
        """
        self.screen = screen
        self.sw = settings.SCREEN_WIDTH
        self.sh = settings.SCREEN_HEIGHT

        try:
            self.font = pygame.font.Font(None, 24)
            self.font_small = pygame.font.Font(None, 18)
        except Exception:
            self.font = None
            self.font_small = None

        # HUD state
        self.mode = "Play"
        self.sub_mode = ""
        self.selected_tile = "floor"
        self.world_name = ""
        self.player_pos: Tuple[int, int] = (0, 0)
        self.player_health: int = 100
        self.player_max_health: int = 100

        # Visibility toggles (all on by default)
        self.show_mode = True
        self.show_position = True
        self.show_tile = True
        self.show_health = True

        # Subscribe to toggle events from settings menu
        event_bus.subscribe('hud_toggle_mode',     lambda _: self._toggle('show_mode'))
        event_bus.subscribe('hud_toggle_position', lambda _: self._toggle('show_position'))
        event_bus.subscribe('hud_toggle_tile',     lambda _: self._toggle('show_tile'))
        event_bus.subscribe('hud_toggle_health',   lambda _: self._toggle('show_health'))

    def _toggle(self, attr: str) -> None:
        """
        Toggle a boolean HUD visibility attribute.

        Args:
            attr: Attribute name string
        """
        setattr(self, attr, not getattr(self, attr))

    def update(
        self,
        mode: str = "Play",
        sub_mode: str = "",
        selected_tile: str = "floor",
        world_name: str = "",
        player_pos: Tuple[int, int] = (0, 0),
        player_health: int = 100,
        player_max_health: int = 100,
    ) -> None:
        """
        Update HUD state values.

        Args:
            mode: Current game mode string
            sub_mode: Current sub-mode string
            selected_tile: Selected tile type name
            world_name: Current world name
            player_pos: Player grid coordinates
            player_health: Current player HP
            player_max_health: Maximum player HP
        """
        self.mode = mode
        self.sub_mode = sub_mode
        self.selected_tile = selected_tile
        self.world_name = world_name
        self.player_pos = player_pos
        self.player_health = player_health
        self.player_max_health = player_max_health

    def render(self) -> None:
        """Render all visible HUD elements to screen."""
        if not self.font:
            return

        # --- Top-left info panel ---
        panel_w = int(self.sw * 0.22)
        panel_h = int(self.sh * 0.18)
        panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel_surf.fill((20, 20, 30, 200))
        self.screen.blit(panel_surf, (10, 10))

        y = 16
        line_h = 22

        if self.show_mode:
            mode_text = f"Mode: {self.mode}"
            if self.sub_mode:
                mode_text += f" [{self.sub_mode}]"
            self._draw_text(mode_text, 18, y, self.font)
            y += line_h

        if self.show_tile and self.mode == "Build":
            self._draw_text(f"Tile: {self.selected_tile}", 18, y, self.font_small)
            y += line_h

        self._draw_text(f"World: {self.world_name}", 18, y, self.font_small)
        y += line_h

        if self.show_position:
            self._draw_text(
                f"Pos: ({self.player_pos[0]}, {self.player_pos[1]})",
                18, y, self.font_small
            )
            y += line_h

        # --- Health bar (bottom-left) ---
        if self.show_health and settings.GAME_RULES.get('health_system', True):
            self._render_health_bar()

    def _draw_text(
        self,
        text: str,
        x: int,
        y: int,
        font: Optional[pygame.font.Font],
    ) -> None:
        """
        Draw white text at absolute screen position.

        Args:
            text: String to render
            x: Screen x
            y: Screen y
            font: Font to use
        """
        if font is None:
            return
        surf = font.render(text, True, settings.COLORS['white'])
        self.screen.blit(surf, (x, y))

    def _render_health_bar(self) -> None:
        """Render player health bar at bottom-left of screen."""
        bar_w = int(self.sw * 0.15)
        bar_h = 14
        bar_x = 10
        bar_y = self.sh - 30

        # Background
        pygame.draw.rect(
            self.screen,
            settings.COLORS['health_bar_bg'],
            pygame.Rect(bar_x, bar_y, bar_w, bar_h)
        )

        # Fill proportion
        if self.player_max_health > 0:
            ratio = max(0.0, min(1.0, self.player_health / self.player_max_health))
            fill_w = int(bar_w * ratio)
            if fill_w > 0:
                pygame.draw.rect(
                    self.screen,
                    settings.COLORS['health_bar'],
                    pygame.Rect(bar_x, bar_y, fill_w, bar_h)
                )

        pygame.draw.rect(
            self.screen,
            settings.COLORS['white'],
            pygame.Rect(bar_x, bar_y, bar_w, bar_h),
            1
        )

        # Label
        if self.font_small:
            label = self.font_small.render(
                f"HP {self.player_health}/{self.player_max_health}",
                True,
                settings.COLORS['white']
            )
            self.screen.blit(label, (bar_x + bar_w + 6, bar_y))
