# =============================================================================
# File: sandbox_game/ui/hud.py
# =============================================================================
"""
HUD — mode, position, health bar, selected tile with color swatch.
All positions are screen-relative. No hardcoded pixels.
"""

import pygame
from typing import Tuple, Optional
import settings
from core.event_bus import event_bus


class HUD:
    """In-game HUD with health bar and tile selection swatch."""

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.sw = settings.SCREEN_WIDTH
        self.sh = settings.SCREEN_HEIGHT

        try:
            self.font      = pygame.font.Font(None, 22)
            self.font_bold = pygame.font.SysFont(None, 24, bold=True)
            self.font_sm   = pygame.font.Font(None, 18)
        except Exception:
            self.font = self.font_bold = self.font_sm = None

        self.mode = "Play"
        self.sub_mode = ""
        self.selected_tile = "floor"
        self.world_name = ""
        self.player_pos: Tuple[int, int] = (0, 0)
        self.player_health = 100
        self.player_max_health = 100

        self.show_mode     = True
        self.show_position = True
        self.show_tile     = True
        self.show_health   = True

        event_bus.subscribe('hud_toggle_mode',     lambda _: self._toggle('show_mode'))
        event_bus.subscribe('hud_toggle_position', lambda _: self._toggle('show_position'))
        event_bus.subscribe('hud_toggle_tile',     lambda _: self._toggle('show_tile'))
        event_bus.subscribe('hud_toggle_health',   lambda _: self._toggle('show_health'))

    def _toggle(self, attr: str) -> None:
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
        self.mode = mode
        self.sub_mode = sub_mode
        self.selected_tile = selected_tile
        self.world_name = world_name
        self.player_pos = player_pos
        self.player_health = player_health
        self.player_max_health = player_max_health

    def render(self) -> None:
        if not self.font:
            return

        # ---- Top-left info panel ----
        lines = []
        if self.show_mode:
            mode_str = self.mode
            if self.sub_mode:
                mode_str += f"  [{self.sub_mode}]"
            lines.append(("MODE: " + mode_str, settings.COLORS['yellow']))

        lines.append(("WORLD: " + self.world_name, settings.COLORS['white']))

        if self.show_position:
            lines.append((
                f"POS: ({self.player_pos[0]}, {self.player_pos[1]})",
                settings.COLORS['white']
            ))

        panel_w = int(self.sw * 0.20)
        line_h = 22
        panel_h = len(lines) * line_h + 16

        panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel_surf.fill((10, 10, 20, 210))
        pygame.draw.rect(panel_surf, (60, 60, 100, 180),
                         panel_surf.get_rect(), 1)
        self.screen.blit(panel_surf, (8, 8))

        y = 14
        for text, color in lines:
            surf = self.font.render(text, True, color)
            self.screen.blit(surf, (16, y))
            y += line_h

        # ---- Build mode tile swatch (top-center) ----
        if self.show_tile and self.mode == "Build":
            tile_data = settings.DEFAULT_TILE_TYPES.get(self.selected_tile, {})
            tile_color = tile_data.get('color', (100, 100, 100))
            swatch_size = 28
            cx = self.sw // 2
            sx = cx - 80
            sy = 10

            label = self.font.render("TILE:", True, settings.COLORS['white'])
            self.screen.blit(label, (sx, sy + 6))

            pygame.draw.rect(self.screen, tile_color,
                             pygame.Rect(sx + 52, sy, swatch_size, swatch_size))
            pygame.draw.rect(self.screen, settings.COLORS['white'],
                             pygame.Rect(sx + 52, sy, swatch_size, swatch_size), 2)

            name_surf = self.font_bold.render(
                self.selected_tile.upper(), True, settings.COLORS['white']
            )
            self.screen.blit(name_surf, (sx + 88, sy + 6))

            # Sub-mode key hints
            hints = "  1:Place  2:Delete  3:Inspect  4:Select  E:Entities"
            hint_surf = self.font_sm.render(hints, True, (160, 160, 200))
            self.screen.blit(hint_surf, (8, panel_h + 14))

        # ---- Health bar (bottom-left) ----
        if self.show_health and settings.GAME_RULES.get('health_system', True):
            bar_w = int(self.sw * 0.16)
            bar_h = 16
            bar_x = 8
            bar_y = self.sh - 30

            pygame.draw.rect(self.screen, (50, 15, 15),
                             pygame.Rect(bar_x, bar_y, bar_w, bar_h))

            if self.player_max_health > 0:
                ratio = max(0.0, min(1.0,
                    self.player_health / self.player_max_health))
                fill_w = int(bar_w * ratio)
                fill_color = (
                    (50, 200, 50) if ratio > 0.5 else
                    (220, 180, 0) if ratio > 0.25 else
                    (200, 40, 40)
                )
                if fill_w > 0:
                    pygame.draw.rect(self.screen, fill_color,
                                     pygame.Rect(bar_x, bar_y, fill_w, bar_h))

            pygame.draw.rect(self.screen, settings.COLORS['white'],
                             pygame.Rect(bar_x, bar_y, bar_w, bar_h), 1)

            if self.font_sm:
                lbl = self.font_sm.render(
                    f"HP {self.player_health}/{self.player_max_health}",
                    True, settings.COLORS['white']
                )
                self.screen.blit(lbl, (bar_x + bar_w + 8, bar_y))

        # ---- Controls reminder (bottom-right, play mode) ----
        if self.mode == "Play" and self.font_sm:
            hints = [
                "B — Build Mode",
                "F — Interact",
                "Tab — Inventory",
                "` — Console",
                "H — Help",
                "ESC — Menu",
            ]
            rx = self.sw - 140
            ry = self.sh - len(hints) * 18 - 8
            bg = pygame.Surface((132, len(hints) * 18 + 8), pygame.SRCALPHA)
            bg.fill((10, 10, 20, 180))
            self.screen.blit(bg, (rx - 4, ry - 4))
            for i, hint in enumerate(hints):
                s = self.font_sm.render(hint, True, (160, 160, 200))
                self.screen.blit(s, (rx, ry + i * 18))
