# =============================================================================
# File: sandbox_game/world/tile_map.py
# =============================================================================
"""
TileMap class managing the 2D grid of tiles.
"""

import pygame
from typing import List, Tuple, Optional
from world.tile import Tile
import settings


class TileMap:
    """
    Manages a 2D grid of tiles with rendering and expansion capabilities.
    """
    
    def __init__(self, width: int = settings.DEFAULT_GRID_WIDTH, height: int = settings.DEFAULT_GRID_HEIGHT):
        """
        Initialize tile map with given dimensions.
        
        Args:
            width: Number of tiles horizontally
            height: Number of tiles vertically
        """
        self.width = width
        self.height = height
        self.tile_size = settings.TILE_SIZE
        
        # Create grid with default floor tiles
        self.tiles: List[List[Tile]] = []
        for y in range(height):
            row = []
            for x in range(width):
                # Create floor tiles by default
                tile_data = settings.DEFAULT_TILE_TYPES['floor']
                row.append(Tile(
                    tile_type='floor',
                    is_solid=tile_data['is_solid'],
                    movement_modifier=tile_data['movement_modifier'],
                    color=tile_data['color']
                ))
            self.tiles.append(row)
    
    def get_tile(self, x: int, y: int) -> Optional[Tile]:
        """
        Get tile at grid coordinates.
        
        Args:
            x: Grid x coordinate
            y: Grid y coordinate
            
        Returns:
            Tile at position or None if out of bounds
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        return None
    
    def set_tile(self, x: int, y: int, tile: Tile) -> bool:
        """
        Set tile at grid coordinates.
        
        Args:
            x: Grid x coordinate
            y: Grid y coordinate
            tile: Tile to place
            
        Returns:
            True if successful, False if out of bounds
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            self.tiles[y][x] = tile
            return True
        return False
    
    def world_to_grid(self, world_x: float, world_y: float) -> Tuple[int, int]:
        """
        Convert world pixel coordinates to grid coordinates.
        
        Args:
            world_x: World x position in pixels
            world_y: World y position in pixels
            
        Returns:
            Tuple of (grid_x, grid_y)
        """
        grid_x = int(world_x // self.tile_size)
        grid_y = int(world_y // self.tile_size)
        return (grid_x, grid_y)
    
    def grid_to_world(self, grid_x: int, grid_y: int) -> Tuple[float, float]:
        """
        Convert grid coordinates to world pixel coordinates (top-left of tile).
        
        Args:
            grid_x: Grid x coordinate
            grid_y: Grid y coordinate
            
        Returns:
            Tuple of (world_x, world_y)
        """
        world_x = grid_x * self.tile_size
        world_y = grid_y * self.tile_size
        return (world_x, world_y)
    
    def expand(self, direction: str, amount: int) -> None:
        """
        Expand the tile map in a given direction.
        
        Args:
            direction: 'north', 'south', 'east', or 'west'
            amount: Number of tiles to add
        """
        tile_data = settings.DEFAULT_TILE_TYPES['floor']
        
        if direction == 'north':
            for _ in range(amount):
                new_row = [
                    Tile(
                        tile_type='floor',
                        is_solid=tile_data['is_solid'],
                        movement_modifier=tile_data['movement_modifier'],
                        color=tile_data['color']
                    ) for _ in range(self.width)
                ]
                self.tiles.insert(0, new_row)
            self.height += amount
        
        elif direction == 'south':
            for _ in range(amount):
                new_row = [
                    Tile(
                        tile_type='floor',
                        is_solid=tile_data['is_solid'],
                        movement_modifier=tile_data['movement_modifier'],
                        color=tile_data['color']
                    ) for _ in range(self.width)
                ]
                self.tiles.append(new_row)
            self.height += amount
        
        elif direction == 'east':
            for row in self.tiles:
                for _ in range(amount):
                    row.append(Tile(
                        tile_type='floor',
                        is_solid=tile_data['is_solid'],
                        movement_modifier=tile_data['movement_modifier'],
                        color=tile_data['color']
                    ))
            self.width += amount
        
        elif direction == 'west':
            for row in self.tiles:
                for _ in range(amount):
                    row.insert(0, Tile(
                        tile_type='floor',
                        is_solid=tile_data['is_solid'],
                        movement_modifier=tile_data['movement_modifier'],
                        color=tile_data['color']
                    ))
            self.width += amount
    
    def render(self, surface: pygame.Surface, camera_offset: Tuple[float, float]) -> None:
        """
        Render the tile map to a surface with camera offset.
        
        Args:
            surface: Pygame surface to draw on
            camera_offset: (x, y) camera offset in pixels
        """
        for y in range(self.height):
            for x in range(self.width):
                tile = self.tiles[y][x]
                world_x, world_y = self.grid_to_world(x, y)
                
                # Apply camera offset
                screen_x = world_x - camera_offset[0]
                screen_y = world_y - camera_offset[1]
                
                # Only draw if on screen (simple culling)
                if (-self.tile_size <= screen_x <= settings.SCREEN_WIDTH and
                    -self.tile_size <= screen_y <= settings.SCREEN_HEIGHT):
                    
                    # Draw tile
                    rect = pygame.Rect(screen_x, screen_y, self.tile_size, self.tile_size)
                    pygame.draw.rect(surface, tile.color, rect)
                    
                    # Draw grid lines
                    pygame.draw.rect(surface, settings.COLORS['grid_line'], rect, 1)
