# =============================================================================
# File: sandbox_game/editor/entity_editor.py
# =============================================================================
"""
Entity editor for spawning and configuring entities.
"""

import pygame
import pygame_gui
from typing import Optional, Tuple
from core.input_handler import InputHandler
from world.tile_map import TileMap
from entities.npc import NPC
from entities.enemy import Enemy
import settings


class EntityEditor:
    """
    Entity spawning and editing system.
    """
    
    def __init__(self, ui_manager: pygame_gui.UIManager):
        """
        Initialize entity editor.
        
        Args:
            ui_manager: pygame_gui UIManager instance
        """
        self.ui_manager = ui_manager
        self.active = False
        self.selected_entity_type = "npc"
        self.spawn_menu_visible = False
        
        # Create spawn menu
        screen_width = settings.SCREEN_WIDTH
        screen_height = settings.SCREEN_HEIGHT
        
        menu_width = int(screen_width * 0.15)
        menu_height = int(screen_height * 0.3)
        menu_x = screen_width - menu_width - 10
        menu_y = int(screen_height * 0.1)
        
        self.spawn_menu = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(menu_x, menu_y, menu_width, menu_height),
            manager=ui_manager,
            starting_layer_height=5
        )
        self.spawn_menu.hide()
        
        # Entity type buttons
        button_height = 40
        button_spacing = 10
        y_offset = 10
        
        self.npc_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, y_offset, menu_width - 20, button_height),
            text="NPC",
            manager=ui_manager,
            container=self.spawn_menu
        )
        y_offset += button_height + button_spacing
        
        self.enemy_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, y_offset, menu_width - 20, button_height),
            text="Enemy",
            manager=ui_manager,
            container=self.spawn_menu
        )
    
    def activate(self) -> None:
        """Activate entity editor."""
        self.active = True
        self.spawn_menu_visible = True
        self.spawn_menu.show()
    
    def deactivate(self) -> None:
        """Deactivate entity editor."""
        self.active = False
        self.spawn_menu_visible = False
        self.spawn_menu.hide()
    
    def toggle(self) -> None:
        """Toggle entity editor."""
        if self.active:
            self.deactivate()
        else:
            self.activate()
    
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
            if event.ui_element == self.npc_button:
                self.selected_entity_type = "npc"
                return True
            
            elif event.ui_element == self.enemy_button:
                self.selected_entity_type = "enemy"
                return True
        
        return False
    
    def update(
        self,
        input_handler: InputHandler,
        tile_map: TileMap,
        camera_offset: Tuple[float, float],
        entities: list
    ) -> None:
        """
        Update entity editor (handles spawning).
        
        Args:
            input_handler: InputHandler instance
            tile_map: TileMap reference
            camera_offset: Current camera offset
            entities: List of entities to add to
        """
        if not self.active:
            return
        
        # Spawn entity on left click
        if input_handler.is_mouse_button_just_pressed(0):
            mouse_pos = input_handler.get_mouse_pos()
            
            # Convert screen to world coordinates
            world_x = mouse_pos[0] + camera_offset[0]
            world_y = mouse_pos[1] + camera_offset[1]
            
            # Convert to grid coordinates
            grid_x, grid_y = tile_map.world_to_grid(world_x, world_y)
            
            # Spawn entity at grid position
            spawn_x, spawn_y = tile_map.grid_to_world(grid_x, grid_y)
            
            if self.selected_entity_type == "npc":
                entity = NPC(position=(spawn_x, spawn_y))
                entities.append(entity)
            
            elif self.selected_entity_type == "enemy":
                entity = Enemy(position=(spawn_x, spawn_y))
                entities.append(entity)
