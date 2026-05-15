# =============================================================================
# File: sandbox_game/entities/entity.py
# =============================================================================
"""
Base entity class for all game objects.
"""

import pygame
import uuid
from typing import Tuple, Dict


class Entity:
    """
    Base class for all entities in the game world.
    Entities are movable, drawable objects with unique IDs.
    """
    
    def __init__(
        self,
        position: Tuple[float, float] = (0, 0),
        size: Tuple[int, int] = (48, 48),
        color: Tuple[int, int, int] = (255, 255, 255),
        name: str = "Entity"
    ):
        """
        Initialize an entity.
        
        Args:
            position: (x, y) world position in pixels
            size: (width, height) in pixels
            color: RGB color tuple
            name: Display name for the entity
        """
        self.id = str(uuid.uuid4())
        self.position = list(position)  # [x, y] for mutability
        self.size = size
        self.color = color
        self.name = name
    
    def update(self, dt: float) -> None:
        """
        Update entity state.
        
        Args:
            dt: Delta time in seconds since last frame
        """
        pass
    
    def draw(self, surface: pygame.Surface, camera_offset: Tuple[float, float]) -> None:
        """
        Draw entity to surface with camera offset.
        
        Args:
            surface: Pygame surface to draw on
            camera_offset: (x, y) camera offset in pixels
        """
        screen_x = self.position[0] - camera_offset[0]
        screen_y = self.position[1] - camera_offset[1]
        
        rect = pygame.Rect(screen_x, screen_y, self.size[0], self.size[1])
        pygame.draw.rect(surface, self.color, rect)
    
    def get_rect(self) -> pygame.Rect:
        """Get pygame Rect for collision detection."""
        return pygame.Rect(self.position[0], self.position[1], self.size[0], self.size[1])
    
    def to_dict(self) -> Dict:
        """Serialize entity to dictionary."""
        return {
            'id': self.id,
            'position': self.position,
            'size': self.size,
            'color': self.color,
            'name': self.name,
            'type': self.__class__.__name__
        }
