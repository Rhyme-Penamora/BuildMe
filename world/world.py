# =============================================================================
# File: sandbox_game/world/world.py
# =============================================================================
"""
World class combining tile map, entities, items, and metadata.
"""

from typing import List, Dict, Optional
from world.tile_map import TileMap
from entities.entity import Entity
import time


class World:
    """
    Represents a complete game world with tiles, entities, items, and metadata.
    """
    
    def __init__(
        self,
        name: str = "New World",
        tile_map: Optional[TileMap] = None,
        entities: Optional[List[Entity]] = None,
        metadata: Optional[Dict] = None
    ):
        """
        Initialize a world.
        
        Args:
            name: World display name
            tile_map: TileMap instance (creates default if None)
            entities: List of entities (empty list if None)
            metadata: Dictionary of world metadata
        """
        self.name = name
        self.tile_map = tile_map if tile_map is not None else TileMap()
        self.entities = entities if entities is not None else []
        self.metadata = metadata if metadata is not None else {}
        
        # Set default metadata
        if 'created' not in self.metadata:
            self.metadata['created'] = time.time()
        if 'last_played' not in self.metadata:
            self.metadata['last_played'] = time.time()
        if 'play_time' not in self.metadata:
            self.metadata['play_time'] = 0.0
    
    def update_play_time(self, dt: float) -> None:
        """
        Update total play time.
        
        Args:
            dt: Delta time in seconds
        """
        self.metadata['play_time'] += dt
        self.metadata['last_played'] = time.time()
    
    def to_dict(self) -> Dict:
        """Serialize world to dictionary for saving."""
        # Serialize tile map
        tiles_data = []
        for y in range(self.tile_map.height):
            row = []
            for x in range(self.tile_map.width):
                tile = self.tile_map.get_tile(x, y)
                row.append(tile.to_dict() if tile else None)
            tiles_data.append(row)
        
        # Serialize entities
        entities_data = [entity.to_dict() for entity in self.entities]
        
        return {
            'name': self.name,
            'tile_map': {
                'width': self.tile_map.width,
                'height': self.tile_map.height,
                'tiles': tiles_data
            },
            'entities': entities_data,
            'metadata': self.metadata
        }
