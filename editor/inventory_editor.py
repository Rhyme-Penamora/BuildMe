# =============================================================================
# File: sandbox_game/editor/inventory_editor.py
# =============================================================================
"""
Inventory editor for creating and managing items.
"""

import pygame
import pygame_gui
from typing import Optional
from inventory.inventory import Inventory
import settings


class InventoryEditor:
    """
    In-game inventory UI with item management.
    """
    
    def __init__(self, ui_manager: pygame_gui.UIManager):
        """
        Initialize inventory editor.
        
        Args:
            ui_manager: pygame_gui UIManager instance
        """
        self.ui_manager = ui_manager
        self.active = False
        self.inventory: Optional[Inventory] = None
        
        # Create inventory panel
        screen_width = settings.SCREEN_WIDTH
        screen_height = settings.SCREEN_HEIGHT
        
        panel_width = int(screen_width * 0.4)
        panel_height = int(screen_height * 0.6)
        panel_x = (screen_width - panel_width) // 2
        panel_y = (screen_height - panel_height) // 2
        
        self.panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(panel_x, panel_y, panel_width, panel_height),
            manager=ui_manager,
            starting_layer_height=10
        )
        self.panel.hide()
        
        # Title
        self.title_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 10, panel_width - 20, 30),
            text="Inventory",
            manager=ui_manager,
            container=self.panel
        )
        
        # Item list
        list_height = panel_height - 100
        self.item_list = pygame_gui.elements.UITextBox(
            html_text="<font face='monospace' size=3>Empty inventory</font>",
            relative_rect=pygame.Rect(10, 50, panel_width - 20, list_height),
            manager=ui_manager,
            container=self.panel
        )
        
        # Close button
        self.close_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, panel_height - 50, 100, 40),
            text="Close",
            manager=ui_manager,
            container=self.panel
        )
    
    def open(self, inventory: Inventory) -> None:
        """
        Open inventory editor.
        
        Args:
            inventory: Inventory instance to display
        """
        self.inventory = inventory
        self.active = True
        self.panel.show()
        self._update_display()
    
    def close(self) -> None:
        """Close inventory editor."""
        self.active = False
        self.panel.hide()
        self.inventory = None
    
    def toggle(self, inventory: Optional[Inventory] = None) -> None:
        """
        Toggle inventory editor.
        
        Args:
            inventory: Inventory to display (if opening)
        """
        if self.active:
            self.close()
        else:
            if inventory:
                self.open(inventory)
    
    def _update_display(self) -> None:
        """Update inventory display."""
        if not self.inventory:
            return
        
        # Build HTML for item list
        html_lines = []
        html_lines.append("<font face='monospace' size=3>")
        
        has_items = False
        for i, item in enumerate(self.inventory.slots):
            if item:
                has_items = True
                html_lines.append(f"[{i}] {item.name} x{item.quantity}<br>")
        
        if not has_items:
            html_lines.append("Empty inventory")
        
        html_lines.append("</font>")
        
        self.item_list.html_text = "".join(html_lines)
        self.item_list.rebuild()
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle UI events.
        
        Args:
            event: pygame event
            
        Returns:
            True if event was handled
        """
        if not self.active:
            return False
        
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.close_button:
                self.close()
                return True
        
        return False
