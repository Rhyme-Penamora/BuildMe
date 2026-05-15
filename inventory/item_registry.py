# =============================================================================
# File: sandbox_game/inventory/item_registry.py
# =============================================================================
"""
Global registry of all item type definitions.
"""

import json
import os
from typing import Dict, Optional
from inventory.item import Item


class ItemRegistry:
    """
    Global registry managing all item type definitions.
    """
    
    def __init__(self):
        """Initialize item registry."""
        self.item_types: Dict[str, Dict] = {}
        self._load_default_items()
    
    def _load_default_items(self) -> None:
        """Load default item types."""
        # Define some default items
        self.register_item_type('stick', {
            'name': 'Stick',
            'description': 'A wooden stick',
            'stackable': True,
            'max_stack': 99
        })
        
        self.register_item_type('stone', {
            'name': 'Stone',
            'description': 'A piece of stone',
            'stackable': True,
            'max_stack': 99
        })
        
        self.register_item_type('key', {
            'name': 'Key',
            'description': 'A mysterious key',
            'stackable': False,
            'max_stack': 1
        })
    
    def register_item_type(self, item_id: str, properties: Dict) -> None:
        """
        Register a new item type.
        
        Args:
            item_id: Unique item identifier
            properties: Item properties dictionary
        """
        self.item_types[item_id] = properties
    
    def get_item_type(self, item_id: str) -> Optional[Dict]:
        """
        Get item type properties.
        
        Args:
            item_id: Item identifier
            
        Returns:
            Item properties dictionary or None
        """
        return self.item_types.get(item_id)
    
    def create_item(self, item_id: str, quantity: int = 1) -> Optional[Item]:
        """
        Create an item instance from registry.
        
        Args:
            item_id: Item type identifier
            quantity: Item quantity
            
        Returns:
            Item instance or None if type not found
        """
        item_type = self.get_item_type(item_id)
        if not item_type:
            return None
        
        return Item(
            item_id=item_id,
            name=item_type.get('name', 'Unknown'),
            description=item_type.get('description', ''),
            sprite=item_type.get('sprite'),
            stackable=item_type.get('stackable', True),
            max_stack=item_type.get('max_stack', 99),
            quantity=quantity,
            custom_properties=item_type.get('custom_properties', {}),
            behavior_script=item_type.get('behavior_script')
        )
    
    def load_from_json(self, filepath: str) -> bool:
        """
        Load item types from JSON file.
        
        Args:
            filepath: Path to JSON file
            
        Returns:
            True if loaded successfully
        """
        try:
            if not os.path.exists(filepath):
                return False
            
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            for item_id, properties in data.items():
                self.register_item_type(item_id, properties)
            
            return True
        except Exception as e:
            print(f"Error loading item registry from {filepath}: {e}")
            return False
    
    def save_to_json(self, filepath: str) -> bool:
        """
        Save item types to JSON file.
        
        Args:
            filepath: Path to JSON file
            
        Returns:
            True if saved successfully
        """
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w') as f:
                json.dump(self.item_types, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving item registry to {filepath}: {e}")
            return False


# Global item registry instance
item_registry = ItemRegistry()
