# =============================================================================
# File: sandbox_game/entities/npc.py
# =============================================================================
"""
NPC entity with dialogue and behavior scripting.
"""

from typing import List, Optional, Dict
from entities.entity import Entity
import settings


class NPC(Entity):
    """
    Non-player character with dialogue and scriptable behavior.
    """
    
    def __init__(
        self,
        position: tuple = (0, 0),
        name: str = "NPC",
        dialogue: Optional[List[str]] = None,
        behavior_script: Optional[str] = None,
        color: tuple = (100, 200, 100)
    ):
        """
        Initialize NPC.
        
        Args:
            position: (x, y) world position in pixels
            name: NPC display name
            dialogue: List of dialogue strings
            behavior_script: Path to behavior script file
            color: RGB color tuple
        """
        super().__init__(
            position=position,
            size=(settings.PLAYER_SIZE, settings.PLAYER_SIZE),
            color=color,
            name=name
        )
        
        self.dialogue = dialogue if dialogue is not None else ["Hello, traveler!"]
        self.behavior_script = behavior_script
        self.current_dialogue_index = 0
        self.behavior_module = None
    
    def on_interact(self, player) -> str:
        """
        Called when player interacts with NPC.
        
        Args:
            player: Player entity that interacted
            
        Returns:
            Current dialogue line
        """
        # Execute script hook if available
        if self.behavior_module and hasattr(self.behavior_module, 'on_interact'):
            try:
                self.behavior_module.on_interact(self, player)
            except Exception as e:
                print(f"Error in NPC behavior on_interact: {e}")
        
        # Get current dialogue
        if self.dialogue:
            dialogue_line = self.dialogue[self.current_dialogue_index]
            self.current_dialogue_index = (self.current_dialogue_index + 1) % len(self.dialogue)
            return dialogue_line
        
        return ""
    
    def update(self, dt: float) -> None:
        """
        Update NPC state.
        
        Args:
            dt: Delta time in seconds
        """
        # Execute script hook if available
        if self.behavior_module and hasattr(self.behavior_module, 'on_update'):
            try:
                self.behavior_module.on_update(self, dt)
            except Exception as e:
                print(f"Error in NPC behavior on_update: {e}")
    
    def to_dict(self) -> Dict:
        """Serialize NPC to dictionary."""
        data = super().to_dict()
        data.update({
            'dialogue': self.dialogue,
            'behavior_script': self.behavior_script,
            'current_dialogue_index': self.current_dialogue_index
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'NPC':
        """Deserialize NPC from dictionary."""
        npc = cls(
            position=tuple(data.get('position', [0, 0])),
            name=data.get('name', 'NPC'),
            dialogue=data.get('dialogue', ["Hello!"]),
            behavior_script=data.get('behavior_script'),
            color=tuple(data.get('color', [100, 200, 100]))
        )
        npc.id = data.get('id', npc.id)
        npc.current_dialogue_index = data.get('current_dialogue_index', 0)
        return npc
