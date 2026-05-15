# =============================================================================
# File: sandbox_game/core/renderer.py
# =============================================================================
"""
Centralized rendering system handling all draw calls.
"""

import pygame
from typing import Tuple
from world.tile_map import TileMap
from entities.entity import Entity
import settings


class Renderer:
    """
    Handles all rendering operations for the game.
    Separates rendering logic from game logic.
    """
    
    def __init__(self, screen: pygame.Surface):
        """
        Initialize renderer.
        
        Args:
            screen: Main pygame display surface
        """
        self.screen = screen
        self.screen_width = settings.SCREEN_WIDTH
        self.screen_height = settings.SCREEN_HEIGHT
    
    def clear(self) -> None:
        """Clear screen with background color."""
        self.screen.fill(settings.COLORS['background'])
    
    def render_tile_map(self, tile_map: TileMap, camera_offset: Tuple[float, float]) -> None:
        """
        Render the tile map.
        
        Args:
            tile_map: TileMap instance to render
            camera_offset: (x, y) camera offset in pixels
        """
        tile_map.render(self.screen, camera_offset)
    
    def render_entity(self, entity: Entity, camera_offset: Tuple[float, float]) -> None:
        """
        Render a single entity.
        
        Args:
            entity: Entity to render
            camera_offset: (x, y) camera offset in pixels
        """
        entity.draw(self.screen, camera_offset)
    
    def render_entities(self, entities: list, camera_offset: Tuple[float, float]) -> None:
        """
        Render a list of entities.
        
        Args:
            entities: List of Entity instances
            camera_offset: (x, y) camera offset in pixels
        """
        for entity in entities:
            self.render_entity(entity, camera_offset)
    
    def present(self) -> None:
        """Present the rendered frame to the screen."""
        pygame.display.flip()
