# =============================================================================
# File: sandbox_game/world/tile.py
# =============================================================================
"""
Tile class representing a single tile in the game world.
"""

from typing import Dict, Tuple, Optional


class Tile:
    """
    Represents a single tile in the game world.
    Tiles have type, physics properties, visuals, and optional behavior scripts.
    """
    
    def __init__(
        self,
        tile_type: str = 'floor',
        is_solid: bool = False,
        movement_modifier: float = 1.0,
        color: Tuple[int, int, int] = (100, 100, 100),
        custom_properties: Optional[Dict] = None,
        behavior_script: Optional[str] = None
    ):
        """
        Initialize a tile.
        
        Args:
            tile_type: The type identifier for this tile
            is_solid: Whether entities can pass through this tile
            movement_modifier: Speed multiplier when moving on this tile (0.0 to 1.0)
            color: RGB color tuple for rendering
            custom_properties: Dictionary of custom properties for scripting
            behavior_script: Path to behavior script file (optional)
        """
        self.tile_type = tile_type
        self.is_solid = is_solid
        self.movement_modifier = max(0.0, min(1.0, movement_modifier))
        self.color = color
        self.custom_properties = custom_properties if custom_properties is not None else {}
        self.behavior_script = behavior_script
    
    def to_dict(self) -> Dict:
        """Serialize tile to dictionary for saving."""
        return {
            'tile_type': self.tile_type,
            'is_solid': self.is_solid,
            'movement_modifier': self.movement_modifier,
            'color': self.color,
            'custom_properties': self.custom_properties,
            'behavior_script': self.behavior_script
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Tile':
        """Deserialize tile from dictionary."""
        return cls(
            tile_type=data.get('tile_type', 'floor'),
            is_solid=data.get('is_solid', False),
            movement_modifier=data.get('movement_modifier', 1.0),
            color=tuple(data.get('color', [100, 100, 100])),
            custom_properties=data.get('custom_properties', {}),
            behavior_script=data.get('behavior_script')
        )
    
    def copy(self) -> 'Tile':
        """Create a deep copy of this tile."""
        return Tile(
            tile_type=self.tile_type,
            is_solid=self.is_solid,
            movement_modifier=self.movement_modifier,
            color=self.color,
            custom_properties=self.custom_properties.copy(),
            behavior_script=self.behavior_script
        )
