# =============================================================================
# File: sandbox_game/world/world_manager.py
# =============================================================================
"""
World manager for creating, loading, saving, and deleting worlds.
"""

import os
import json
from typing import List, Optional, Dict
from world.world import World
from world.tile_map import TileMap
from world.tile import Tile
from entities.npc import NPC
from entities.enemy import Enemy
import settings


class WorldManager:
    """
    Manages world persistence and lifecycle.
    """
    
    def __init__(self):
        """Initialize world manager and ensure worlds directory exists."""
        self.worlds_dir = "worlds"
        self.current_world: Optional[World] = None
        self.auto_save_timer = 0.0
        self.auto_save_interval = 60.0  # Auto-save every 60 seconds
        
        # Ensure worlds directory exists
        try:
            os.makedirs(self.worlds_dir, exist_ok=True)
        except OSError as e:
            print(f"Error creating worlds directory: {e}")
    
    def create_world(self, name: str, width: int = settings.DEFAULT_GRID_WIDTH, height: int = settings.DEFAULT_GRID_HEIGHT) -> World:
        """
        Create a new world.
        
        Args:
            name: World name
            width: Tile map width
            height: Tile map height
            
        Returns:
            Newly created World instance
        """
        tile_map = TileMap(width, height)
        world = World(name=name, tile_map=tile_map)
        return world
    
    def save_world(self, world: World) -> bool:
        """
        Save a world to disk.
        
        Args:
            world: World instance to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create world directory
            world_dir = os.path.join(self.worlds_dir, self._sanitize_filename(world.name))
            os.makedirs(world_dir, exist_ok=True)
            
            # Create subdirectories
            os.makedirs(os.path.join(world_dir, "behaviors", "entities"), exist_ok=True)
            os.makedirs(os.path.join(world_dir, "behaviors", "tiles"), exist_ok=True)
            os.makedirs(os.path.join(world_dir, "items"), exist_ok=True)
            os.makedirs(os.path.join(world_dir, "assets", "sprites"), exist_ok=True)
            os.makedirs(os.path.join(world_dir, "assets", "tiles"), exist_ok=True)
            os.makedirs(os.path.join(world_dir, "assets", "backgrounds"), exist_ok=True)
            os.makedirs(os.path.join(world_dir, "assets", "ui"), exist_ok=True)
            
            # Save world data
            world_file = os.path.join(world_dir, "world.json")
            with open(world_file, 'w') as f:
                json.dump(world.to_dict(), f, indent=2)
            
            # Save settings
            settings_file = os.path.join(world_dir, "settings.json")
            settings_data = {
                'auto_save_interval': self.auto_save_interval
            }
            with open(settings_file, 'w') as f:
                json.dump(settings_data, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error saving world '{world.name}': {e}")
            return False
    
    def load_world(self, name: str) -> Optional[World]:
        """
        Load a world from disk.
        
        Args:
            name: World name to load
            
        Returns:
            Loaded World instance or None if failed
        """
        try:
            world_dir = os.path.join(self.worlds_dir, self._sanitize_filename(name))
            world_file = os.path.join(world_dir, "world.json")
            
            if not os.path.exists(world_file):
                print(f"World file not found: {world_file}")
                return None
            
            with open(world_file, 'r') as f:
                data = json.load(f)
            
            # Reconstruct tile map
            tile_map_data = data.get('tile_map', {})
            width = tile_map_data.get('width', settings.DEFAULT_GRID_WIDTH)
            height = tile_map_data.get('height', settings.DEFAULT_GRID_HEIGHT)
            tile_map = TileMap(width, height)
            
            # Load tiles
            tiles_data = tile_map_data.get('tiles', [])
            for y, row in enumerate(tiles_data):
                for x, tile_data in enumerate(row):
                    if tile_data:
                        tile = Tile.from_dict(tile_data)
                        tile_map.set_tile(x, y, tile)
            
            # Load entities
            entities = []
            entities_data = data.get('entities', [])
            for entity_data in entities_data:
                entity_type = entity_data.get('type', 'Entity')
                
                if entity_type == 'NPC':
                    entity = NPC.from_dict(entity_data)
                    entities.append(entity)
                elif entity_type == 'Enemy':
                    entity = Enemy.from_dict(entity_data)
                    entities.append(entity)
            
            # Create world
            world = World(
                name=data.get('name', name),
                tile_map=tile_map,
                entities=entities,
                metadata=data.get('metadata', {})
            )
            
            return world
            
        except Exception as e:
            print(f"Error loading world '{name}': {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def delete_world(self, name: str) -> bool:
        """
        Delete a world from disk.
        
        Args:
            name: World name to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import shutil
            world_dir = os.path.join(self.worlds_dir, self._sanitize_filename(name))
            
            if os.path.exists(world_dir):
                shutil.rmtree(world_dir)
                return True
            else:
                print(f"World directory not found: {world_dir}")
                return False
                
        except Exception as e:
            print(f"Error deleting world '{name}': {e}")
            return False
    
    def list_worlds(self) -> List[Dict[str, str]]:
        """
        List all available worlds.
        
        Returns:
            List of dictionaries with world metadata
        """
        worlds = []
        
        try:
            if not os.path.exists(self.worlds_dir):
                return worlds
            
            for item in os.listdir(self.worlds_dir):
                world_dir = os.path.join(self.worlds_dir, item)
                world_file = os.path.join(world_dir, "world.json")
                
                if os.path.isdir(world_dir) and os.path.exists(world_file):
                    try:
                        with open(world_file, 'r') as f:
                            data = json.load(f)
                        
                        worlds.append({
                            'name': data.get('name', item),
                            'created': data.get('metadata', {}).get('created', 0),
                            'last_played': data.get('metadata', {}).get('last_played', 0),
                            'play_time': data.get('metadata', {}).get('play_time', 0)
                        })
                    except Exception as e:
                        print(f"Error reading world metadata for '{item}': {e}")
                        
        except Exception as e:
            print(f"Error listing worlds: {e}")
        
        return worlds
    
    def update(self, dt: float) -> None:
        """
        Update world manager (handles auto-save).
        
        Args:
            dt: Delta time in seconds
        """
        if self.current_world:
            self.current_world.update_play_time(dt)
            
            # Auto-save timer
            self.auto_save_timer += dt
            if self.auto_save_timer >= self.auto_save_interval:
                self.auto_save_timer = 0.0
                self.save_world(self.current_world)
    
    def _sanitize_filename(self, name: str) -> str:
        """
        Sanitize world name for use as filename.
        
        Args:
            name: World name
            
        Returns:
            Sanitized filename
        """
        # Replace invalid characters with underscores
        invalid_chars = '<>:"/\\|?*'
        sanitized = ''.join('_' if c in invalid_chars else c for c in name)
        return sanitized.strip()
