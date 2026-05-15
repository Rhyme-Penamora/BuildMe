# =============================================================================
# File: sandbox_game/inventory/item.py
# =============================================================================
"""
Item class representing items in the game.
"""

from typing import Dict, Optional


class Item:
    """
    Represents an item in the game with properties and behavior.
    """
    
    def __init__(
        self,
        item_id: str,
        name: str,
        description: str = "",
        sprite: Optional[str] = None,
        stackable: bool = True,
        max_stack: int = 99,
        quantity: int = 1,
        custom_properties: Optional[Dict] = None,
        behavior_script: Optional[str] = None
    ):
        """
        Initialize an item.
        
        Args:
            item_id: Unique identifier for this item type
            name: Display name
            description: Item description
            sprite: Path to sprite image
            stackable: Whether this item can stack
            max_stack: Maximum stack size
            quantity: Current quantity
            custom_properties: Dictionary of custom properties
            behavior_script: Path to behavior script file
        """
        self.item_id = item_id
        self.name = name
        self.description = description
        self.sprite = sprite
        self.stackable = stackable
        self.max_stack = max_stack
        self.quantity = quantity
        self.custom_properties = custom_properties if custom_properties is not None else {}
        self.behavior_script = behavior_script
        self.behavior_module = None
    
    def to_dict(self) -> Dict:
        """Serialize item to dictionary."""
        return {
            'item_id': self.item_id,
            'name': self.name,
            'description': self.description,
            'sprite': self.sprite,
            'stackable': self.stackable,
            'max_stack': self.max_stack,
            'quantity': self.quantity,
            'custom_properties': self.custom_properties,
            'behavior_script': self.behavior_script
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Item':
        """Deserialize item from dictionary."""
        return cls(
            item_id=data.get('item_id', 'unknown'),
            name=data.get('name', 'Unknown Item'),
            description=data.get('description', ''),
            sprite=data.get('sprite'),
            stackable=data.get('stackable', True),
            max_stack=data.get('max_stack', 99),
            quantity=data.get('quantity', 1),
            custom_properties=data.get('custom_properties', {}),
            behavior_script=data.get('behavior_script')
        )
    
    def copy(self) -> 'Item':
        """Create a copy of this item."""
        return Item(
            item_id=self.item_id,
            name=self.name,
            description=self.description,
            sprite=self.sprite,
            stackable=self.stackable,
            max_stack=self.max_stack,
            quantity=self.quantity,
            custom_properties=self.custom_properties.copy(),
            behavior_script=self.behavior_script
        )
