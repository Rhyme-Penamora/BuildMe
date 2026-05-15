# =============================================================================
# File: sandbox_game/entities/player.py
# =============================================================================
"""
Player entity with movement and collision.
"""

import pygame
from typing import Tuple
from entities.entity import Entity
from world.tile_map import TileMap
from core.input_handler import InputHandler
from inventory.inventory import Inventory
import settings


class Player(Entity):
    """
    Player-controlled entity with WASD movement and tile collision.
    """
    
    def __init__(self, position: Tuple[float, float] = (0, 0)):
        """
        Initialize player.
        
        Args:
            position: Starting (x, y) world position in pixels
        """
        super().__init__(
            position=position,
            size=(settings.PLAYER_SIZE, settings.PLAYER_SIZE),
            color=settings.PLAYER_COLOR,
            name="Player"
        )
        self.speed = settings.PLAYER_SPEED
        
        # Add inventory
        self.inventory = Inventory(size=20)
    
    def update(self, dt: float, input_handler: InputHandler, tile_map: TileMap) -> None:
        """
        Update player with input and collision.
        
        Args:
            dt: Delta time in seconds
            input_handler: InputHandler instance for reading controls
            tile_map: TileMap instance for collision checks
        """
        # Get movement input
        move_x = 0
        move_y = 0
        
        if input_handler.is_key_pressed(pygame.K_w):
            move_y -= 1
        if input_handler.is_key_pressed(pygame.K_s):
            move_y += 1
        if input_handler.is_key_pressed(pygame.K_a):
            move_x -= 1
        if input_handler.is_key_pressed(pygame.K_d):
            move_x += 1
        
        # Normalize diagonal movement
        if move_x != 0 and move_y != 0:
            move_x *= 0.7071  # 1/sqrt(2)
            move_y *= 0.7071
        
        # Get current tile for movement modifier
        grid_x, grid_y = tile_map.world_to_grid(
            self.position[0] + self.size[0] / 2,
            self.position[1] + self.size[1] / 2
        )
        current_tile = tile_map.get_tile(grid_x, grid_y)
        movement_modifier = current_tile.movement_modifier if current_tile else 1.0
        
        # Apply movement with tile modifier
        effective_speed = self.speed * movement_modifier
        velocity_x = move_x * effective_speed * dt
        velocity_y = move_y * effective_speed * dt
        
        # Move and check collision on X axis
        self.position[0] += velocity_x
        if self._check_collision(tile_map):
            self.position[0] -= velocity_x
        
        # Move and check collision on Y axis
        self.position[1] += velocity_y
        if self._check_collision(tile_map):
            self.position[1] -= velocity_y
    
    def _check_collision(self, tile_map: TileMap) -> bool:
        """
        Check if player is colliding with any solid tiles.
        
        Args:
            tile_map: TileMap to check against
            
        Returns:
            True if colliding with solid tile, False otherwise
        """
        player_rect = self.get_rect()
        
        # Get tile coordinates the player overlaps
        left_tile = int(player_rect.left // tile_map.tile_size)
        right_tile = int(player_rect.right // tile_map.tile_size)
        top_tile = int(player_rect.top // tile_map.tile_size)
        bottom_tile = int(player_rect.bottom // tile_map.tile_size)
        
        # Check all overlapping tiles
        for y in range(top_tile, bottom_tile + 1):
            for x in range(left_tile, right_tile + 1):
                tile = tile_map.get_tile(x, y)
                if tile and tile.is_solid:
                    return True
        
        return False
