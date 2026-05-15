# =============================================================================
# File: sandbox_game/scripting/api.py
# =============================================================================
"""
Scripting API providing safe functions for behavior scripts.
"""

import math
from typing import Optional, Any


class ScriptingAPI:
    """
    Safe API for behavior scripts.
    All functions are implemented and safe to use.
    """
    
    def __init__(self, game_instance):
        """
        Initialize API with game instance reference.
        
        Args:
            game_instance: Reference to main Game instance
        """
        self.game = game_instance
    
    def move_toward(self, entity, target, speed: float) -> None:
        """
        Move entity toward target position.
        
        Args:
            entity: Entity to move
            target: Target entity or (x, y) position
            speed: Movement speed in pixels per second
        """
        # Get target position
        if hasattr(target, 'position'):
            target_x, target_y = target.position[0], target.position[1]
        else:
            target_x, target_y = target
        
        # Calculate direction
        dx = target_x - entity.position[0]
        dy = target_y - entity.position[1]
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > 0:
            # Normalize and apply speed
            dx = (dx / distance) * speed * self.game.dt
            dy = (dy / distance) * speed * self.game.dt
            
            entity.position[0] += dx
            entity.position[1] += dy
    
    def distance(self, entity_a, entity_b) -> float:
        """
        Calculate distance between two entities.
        
        Args:
            entity_a: First entity
            entity_b: Second entity
            
        Returns:
            Distance in pixels
        """
        dx = entity_b.position[0] - entity_a.position[0]
        dy = entity_b.position[1] - entity_a.position[1]
        return math.sqrt(dx * dx + dy * dy)
    
    def deal_damage(self, target, amount: int) -> None:
        """
        Deal damage to a target entity.
        
        Args:
            target: Target entity (must have take_damage method)
            amount: Damage amount
        """
        if hasattr(target, 'take_damage'):
            target.take_damage(amount)
    
    def heal(self, target, amount: int) -> None:
        """
        Heal a target entity.
        
        Args:
            target: Target entity (must have health attribute)
            amount: Heal amount
        """
        if hasattr(target, 'health') and hasattr(target, 'max_health'):
            target.health = min(target.max_health, target.health + amount)
    
    def get_player(self):
        """
        Get the player entity.
        
        Returns:
            Player entity or None
        """
        return self.game.player
    
    def spawn_entity(self, entity_type: str, x: int, y: int):
        """
        Spawn an entity at grid coordinates.
        
        Args:
            entity_type: Type of entity ('npc' or 'enemy')
            x: Grid x coordinate
            y: Grid y coordinate
            
        Returns:
            Spawned entity or None
        """
        if not self.game.current_world:
            return None
        
        # Convert grid to world coordinates
        world_x, world_y = self.game.current_world.tile_map.grid_to_world(x, y)
        
        # Create entity based on type
        from entities.npc import NPC
        from entities.enemy import Enemy
        
        entity = None
        if entity_type.lower() == 'npc':
            entity = NPC(position=(world_x, world_y))
        elif entity_type.lower() == 'enemy':
            entity = Enemy(position=(world_x, world_y))
        
        if entity:
            self.game.current_world.entities.append(entity)
        
        return entity
    
    def destroy_entity(self, entity) -> None:
        """
        Remove an entity from the world.
        
        Args:
            entity: Entity to remove
        """
        if self.game.current_world and entity in self.game.current_world.entities:
            self.game.current_world.entities.remove(entity)
    
    def open_dialogue(self, text: str) -> None:
        """
        Display dialogue text to player.
        
        Args:
            text: Dialogue text to display
        """
        if self.game.console:
            self.game.console.log(f"[DIALOGUE] {text}", "#FFFF00")
    
    def play_animation(self, entity, animation_name: str) -> None:
        """
        Play an animation on an entity (placeholder for Phase 4).
        
        Args:
            entity: Entity to animate
            animation_name: Name of animation
        """
        # Placeholder - full implementation in Phase 4
        pass
    
    def set_tile(self, x: int, y: int, tile_type: str) -> bool:
        """
        Set tile at grid coordinates.
        
        Args:
            x: Grid x coordinate
            y: Grid y coordinate
            tile_type: Tile type name
            
        Returns:
            True if successful
        """
        if not self.game.current_world:
            return False
        
        from world.tile import Tile
        import settings
        
        tile_data = settings.DEFAULT_TILE_TYPES.get(tile_type)
        if not tile_data:
            return False
        
        new_tile = Tile(
            tile_type=tile_type,
            is_solid=tile_data['is_solid'],
            movement_modifier=tile_data['movement_modifier'],
            color=tile_data['color']
        )
        
        return self.game.current_world.tile_map.set_tile(x, y, new_tile)
    
    def get_tile(self, x: int, y: int):
        """
        Get tile at grid coordinates.
        
        Args:
            x: Grid x coordinate
            y: Grid y coordinate
            
        Returns:
            Tile or None
        """
        if not self.game.current_world:
            return None
        
        return self.game.current_world.tile_map.get_tile(x, y)
    
    def log(self, message: str) -> None:
        """
        Log a message to the console.
        
        Args:
            message: Message to log
        """
        if self.game.console:
            self.game.console.log(f"[SCRIPT] {message}", "#00FFFF")
    
    def give_item(self, player, item_id: str, quantity: int = 1) -> bool:
        """
        Give item to player inventory.
        
        Args:
            player: Player entity
            item_id: Item type ID
            quantity: Quantity to give
            
        Returns:
            True if added successfully
        """
        if not hasattr(player, 'inventory'):
            return False
        
        from inventory.item_registry import item_registry
        item = item_registry.create_item(item_id, quantity)
        
        if item:
            return player.inventory.add_item(item)
        
        return False
    
    def remove_item(self, player, item_id: str, quantity: int = 1) -> bool:
        """
        Remove item from player inventory.
        
        Args:
            player: Player entity
            item_id: Item type ID
            quantity: Quantity to remove
            
        Returns:
            True if removed successfully
        """
        if not hasattr(player, 'inventory'):
            return False
        
        return player.inventory.remove_item(item_id, quantity)
    
    def has_item(self, player, item_id: str, quantity: int = 1) -> bool:
        """
        Check if player has item.
        
        Args:
            player: Player entity
            item_id: Item type ID
            quantity: Quantity to check
            
        Returns:
            True if player has item
        """
        if not hasattr(player, 'inventory'):
            return False
        
        return player.inventory.has_item(item_id, quantity)
    
    def get_inventory(self, player):
        """
        Get player's inventory.
        
        Args:
            player: Player entity
            
        Returns:
            Inventory or None
        """
        return getattr(player, 'inventory', None)
    
    def set_world_background(self, image_path: str) -> bool:
        """
        Set world background image (placeholder for Phase 4).
        
        Args:
            image_path: Path to background image
            
        Returns:
            True if successful
        """
        # Placeholder - full implementation in Phase 4
        return False
    
    def set_player_sprite(self, image_path: str) -> bool:
        """
        Set player sprite (placeholder for Phase 4).
        
        Args:
            image_path: Path to sprite image
            
        Returns:
            True if successful
        """
        # Placeholder - full implementation in Phase 4
        return False
    
    def get_world_setting(self, key: str) -> Any:
        """
        Get world setting value.
        
        Args:
            key: Setting key
            
        Returns:
            Setting value or None
        """
        if self.game.current_world:
            return self.game.current_world.metadata.get(key)
        return None
    
    def set_world_setting(self, key: str, value: Any) -> None:
        """
        Set world setting value.
        
        Args:
            key: Setting key
            value: Setting value
        """
        if self.game.current_world:
            self.game.current_world.metadata[key] = value
