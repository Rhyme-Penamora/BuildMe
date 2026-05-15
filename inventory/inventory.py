# =============================================================================
# File: sandbox_game/inventory/inventory.py
# =============================================================================
"""
Inventory class managing a grid of item slots.
"""

from typing import List, Optional, Dict
from inventory.item import Item


class Inventory:
    """
    Inventory with fixed grid of slots for storing items.
    """
    
    def __init__(self, size: int = 20):
        """
        Initialize inventory.
        
        Args:
            size: Number of inventory slots
        """
        self.size = size
        self.slots: List[Optional[Item]] = [None] * size
    
    def add_item(self, item: Item) -> bool:
        """
        Add an item to inventory.
        
        Args:
            item: Item to add
            
        Returns:
            True if item was added, False if inventory is full
        """
        # Try to stack with existing items first
        if item.stackable:
            for i, slot_item in enumerate(self.slots):
                if slot_item and slot_item.item_id == item.item_id:
                    # Can stack here
                    space_available = slot_item.max_stack - slot_item.quantity
                    if space_available > 0:
                        amount_to_add = min(space_available, item.quantity)
                        slot_item.quantity += amount_to_add
                        item.quantity -= amount_to_add
                        
                        if item.quantity <= 0:
                            return True
        
        # Find empty slot
        for i, slot_item in enumerate(self.slots):
            if slot_item is None:
                self.slots[i] = item
                return True
        
        # Inventory full
        return False
    
    def remove_item(self, item_id: str, quantity: int = 1) -> bool:
        """
        Remove item(s) from inventory.
        
        Args:
            item_id: ID of item to remove
            quantity: Amount to remove
            
        Returns:
            True if removed successfully, False if not enough items
        """
        # Check if we have enough
        total = self.count_item(item_id)
        if total < quantity:
            return False
        
        # Remove items
        remaining = quantity
        for i, slot_item in enumerate(self.slots):
            if slot_item and slot_item.item_id == item_id:
                if slot_item.quantity <= remaining:
                    remaining -= slot_item.quantity
                    self.slots[i] = None
                else:
                    slot_item.quantity -= remaining
                    remaining = 0
                
                if remaining <= 0:
                    break
        
        return True
    
    def has_item(self, item_id: str, quantity: int = 1) -> bool:
        """
        Check if inventory has item.
        
        Args:
            item_id: ID of item to check
            quantity: Amount to check for
            
        Returns:
            True if inventory has at least quantity of item
        """
        return self.count_item(item_id) >= quantity
    
    def count_item(self, item_id: str) -> int:
        """
        Count total quantity of an item.
        
        Args:
            item_id: ID of item to count
            
        Returns:
            Total quantity
        """
        total = 0
        for slot_item in self.slots:
            if slot_item and slot_item.item_id == item_id:
                total += slot_item.quantity
        return total
    
    def get_item(self, slot: int) -> Optional[Item]:
        """
        Get item in slot.
        
        Args:
            slot: Slot index
            
        Returns:
            Item or None
        """
        if 0 <= slot < self.size:
            return self.slots[slot]
        return None
    
    def swap_slots(self, slot_a: int, slot_b: int) -> bool:
        """
        Swap items in two slots.
        
        Args:
            slot_a: First slot index
            slot_b: Second slot index
            
        Returns:
            True if swapped successfully
        """
        if 0 <= slot_a < self.size and 0 <= slot_b < self.size:
            self.slots[slot_a], self.slots[slot_b] = self.slots[slot_b], self.slots[slot_a]
            return True
        return False
    
    def to_dict(self) -> Dict:
        """Serialize inventory to dictionary."""
        slots_data = []
        for slot_item in self.slots:
            if slot_item:
                slots_data.append(slot_item.to_dict())
            else:
                slots_data.append(None)
        
        return {
            'size': self.size,
            'slots': slots_data
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Inventory':
        """Deserialize inventory from dictionary."""
        inventory = cls(size=data.get('size', 20))
        
        slots_data = data.get('slots', [])
        for i, slot_data in enumerate(slots_data):
            if i < inventory.size and slot_data:
                inventory.slots[i] = Item.from_dict(slot_data)
        
        return inventory
