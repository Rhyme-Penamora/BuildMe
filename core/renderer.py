# =============================================================================
# File: BuildMe/core/renderer.py
# =============================================================================
"""
All draw calls — tile map with hover highlight, entities, background.
Dynamically adapts to resized windows.
"""

import pygame
from typing import Tuple, Optional
import settings


class Renderer:
    """Handles all rendering with tile selection highlight."""

    def __init__(self, screen: pygame.Surface):
        self.screen = screen

    def _get_screen_size(self) -> Tuple[int, int]:
        """Fetch live screen size after resize events."""

        self.screen = pygame.display.get_surface()

        if not self.screen:
            return settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT

        return self.screen.get_size()

    def clear(self) -> None:
        self.screen = pygame.display.get_surface()

        if self.screen:
            self.screen.fill(settings.COLORS['background'])

    def render_tile_map(
        self,
        tile_map,
        camera_offset: Tuple[float, float],
        selected_tile_type: Optional[str] = None,
        sub_mode: str = "",
        mouse_grid: Optional[Tuple[int, int]] = None,
    ) -> None:
        """Draw tile map with grid lines and hover highlight."""

        screen_w, screen_h = self._get_screen_size()

        ts = tile_map.tile_size
        cx, cy = camera_offset

        for y in range(tile_map.height):
            for x in range(tile_map.width):
                tile = tile_map.get_tile(x, y)

                if tile is None:
                    continue

                sx = int(x * ts - cx)
                sy = int(y * ts - cy)

                if (
                    sx + ts < 0 or
                    sx > screen_w or
                    sy + ts < 0 or
                    sy > screen_h
                ):
                    continue

                rect = pygame.Rect(sx, sy, ts, ts)

                pygame.draw.rect(self.screen, tile.color, rect)

                pygame.draw.rect(
                    self.screen,
                    settings.COLORS['grid_line'],
                    rect,
                    1
                )

        # Hover highlight
        if mouse_grid and sub_mode in ("Place", "Delete", "Inspect"):
            gx, gy = mouse_grid

            sx = int(gx * ts - cx)
            sy = int(gy * ts - cy)

            hover = pygame.Surface((ts, ts), pygame.SRCALPHA)
            rect = pygame.Rect(sx, sy, ts, ts)

            if sub_mode == "Place" and selected_tile_type:
                td = settings.DEFAULT_TILE_TYPES.get(
                    selected_tile_type,
                    {}
                )

                base = td.get('color', (200, 200, 200))

                hover.fill((*base, 160))
                self.screen.blit(hover, (sx, sy))

                pygame.draw.rect(
                    self.screen,
                    settings.COLORS['white'],
                    rect,
                    3
                )

            elif sub_mode == "Delete":
                hover.fill((255, 60, 60, 130))
                self.screen.blit(hover, (sx, sy))

                pygame.draw.rect(
                    self.screen,
                    settings.COLORS['red'],
                    rect,
                    3
                )

            elif sub_mode == "Inspect":
                hover.fill((60, 210, 255, 110))
                self.screen.blit(hover, (sx, sy))

                pygame.draw.rect(
                    self.screen,
                    settings.COLORS['yellow'],
                    rect,
                    3
                )

    def render_entity(
        self,
        entity,
        camera_offset: Tuple[float, float]
    ) -> None:
        """Render single entity with resize-safe culling."""

        screen_w, screen_h = self._get_screen_size()

        sx = int(entity.position[0] - camera_offset[0])
        sy = int(entity.position[1] - camera_offset[1])

        w = int(entity.size[0])
        h = int(entity.size[1])

        if (
            sx + w < 0 or
            sx > screen_w or
            sy + h < 0 or
            sy > screen_h
        ):
            return

        sprite = getattr(entity, 'sprite_surface', None)

        if sprite:
            scaled = pygame.transform.scale(sprite, (w, h))
            self.screen.blit(scaled, (sx, sy))

        else:
            pygame.draw.rect(
                self.screen,
                entity.color,
                pygame.Rect(sx, sy, w, h)
            )

        pygame.draw.rect(
            self.screen,
            settings.COLORS['white'],
            pygame.Rect(sx, sy, w, h),
            1
        )

    def render_entities(
        self,
        entities: list,
        camera_offset: Tuple[float, float]
    ) -> None:
        for entity in entities:
            self.render_entity(entity, camera_offset)

    def present(self) -> None:
        pygame.display.flip()
