# =============================================================================
# File: sandbox_game/entities/enemy.py
# =============================================================================
"""
Enemy entity with health and behavior scripting.
"""

from typing import Optional, Dict
from entities.entity import Entity
import settings


class Enemy(Entity):
    """
    Enemy entity with health, damage, and scriptable behavior.
    """
    
    def __init__(
        self,
        position: tuple = (0, 0),
        name: str = "Enemy",
        health: int = 10,
        max_health: int = 10,
        damage: int = 1,
        behavior_script: Optional[str] = None,
        color: tuple = (200, 50, 50)
    ):
        """
        Initialize enemy.
        
        Args:
            position: (x, y) world position in pixels
            name: Enemy display name
            health: Current health
            max_health: Maximum health
            damage: Damage dealt to player
            behavior_script: Path to behavior script file
            color: RGB color tuple
        """
        super().__init__(
            position=position,
            size=(settings.PLAYER_SIZE, settings.PLAYER_SIZE),
            color=color,
            name=name
        )
        
        self.health = health
        self.max_health = max_health
        self.damage = damage
        self.behavior_script = behavior_script
        self.behavior_module = None
        self.is_dead = False
    
    def take_damage(self, amount: int) -> None:
        """
        Deal damage to enemy.
        
        Args:
            amount: Damage amount
        """
        self.health = max(0, self.health - amount)
        
        if self.health <= 0 and not self.is_dead:
            self.is_dead = True
            self.on_death()
    
    def on_death(self) -> None:
        """Called when enemy dies."""
        # Execute script hook if available
        if self.behavior_module and hasattr(self.behavior_module, 'on_death'):
            try:
                self.behavior_module.on_death(self)
            except Exception as e:
                print(f"Error in Enemy behavior on_death: {e}")
    
    def update(self, dt: float) -> None:
        """
        Update enemy state.
        
        Args:
            dt: Delta time in seconds
        """
        if self.is_dead:
            return
        
        # Execute script hook if available
        if self.behavior_module and hasattr(self.behavior_module, 'on_update'):
            try:
                self.behavior_module.on_update(self, dt)
            except Exception as e:
                print(f"Error in Enemy behavior on_update: {e}")
    
    def to_dict(self) -> Dict:
        """Serialize enemy to dictionary."""
        data = super().to_dict()
        data.update({
            'health': self.health,
            'max_health': self.max_health,
            'damage': self.damage,
            'behavior_script': self.behavior_script,
            'is_dead': self.is_dead
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Enemy':
        """Deserialize enemy from dictionary."""
        enemy = cls(
            position=tuple(data.get('position', [0, 0])),
            name=data.get('name', 'Enemy'),
            health=data.get('health', 10),
            max_health=data.get('max_health', 10),
            damage=data.get('damage', 1),
            behavior_script=data.get('behavior_script'),
            color=tuple(data.get('color', [200, 50, 50]))
        )
        enemy.id = data.get('id', enemy.id)
        enemy.is_dead = data.get('is_dead', False)
        return enemy
