# =============================================================================
# File: sandbox_game/editor/tile_editor.py
# =============================================================================
"""
Tile editor for placing, deleting, inspecting, and selecting tiles.
"""

import pygame
import pygame_gui
from typing import Optional, Tuple
from world.tile_map import TileMap
from world.tile import Tile
from core.input_handler import InputHandler
import settings


class TileEditor:
    """
    Tile editing system with Place, Delete, Inspect, and Select sub-modes.
    """
    
    def __init__(self, ui_manager: pygame_gui.UIManager):
        """
        Initialize tile editor.
        
        Args:
            ui_manager: pygame_gui UIManager instance
        """
        self.ui_manager = ui_manager
        self.active = False
        self.sub_mode = "Place"  # Place, Delete, Inspect, Select
        self.selected_tile_type = "floor"
        self.tile_palette_visible = False
        
        # Create tile palette panel
        screen_width = settings.SCREEN_WIDTH
        screen_height = settings.SCREEN_HEIGHT
        
        palette_width = int(screen_width * 0.15)
        palette_height = int(screen_height * 0.4)
        palette_x = screen_width - palette_width - 10
        palette_y = int(screen_height * 0.3)
        
        self.palette_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(palette_x, palette_y, palette_width, palette_height),
            manager=ui_manager,
            starting_layer_height=5
        )
        self.palette_panel.hide()
        
        # Tile type buttons
        button_height = 40
        button_spacing = 10
        y_offset = 10
        
        tile_types = list(settings.DEFAULT_TILE_TYPES.keys())
        self.tile_buttons = {}
        
        for tile_type in tile_types:
            button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(10, y_offset, palette_width - 20, button_height),
                text=tile_type.capitalize(),
                manager=ui_manager,
                container=self.palette_panel
            )
            self.tile_buttons[tile_type] = button
            y_offset += button_height + button_spacing
    
    def activate(self) -> None:
        """Activate build mode."""
        self.active = True
        self.tile_palette_visible = True
        self.palette_panel.show()
    
    def deactivate(self) -> None:
        """Deactivate build mode."""
        self.active = False
        self.tile_palette_visible = False
        self.palette_panel.hide()
    
    def toggle(self) -> None:
        """Toggle build mode."""
        if self.active:
            self.deactivate()
        else:
            self.activate()
    
    def set_sub_mode(self, mode: str) -> None:
        """
        Set current sub-mode.
        
        Args:
            mode: Sub-mode name (Place, Delete, Inspect, Select)
        """
        # If switching to Inspect, exit Select
        if mode == "Inspect" and self.sub_mode == "Select":
            self.sub_mode = mode
        # If switching to Select, exit Inspect
        elif mode == "Select" and self.sub_mode == "Inspect":
            self.sub_mode = mode
        else:
            self.sub_mode = mode
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle UI events.
        
        Args:
            event: pygame event
            
        Returns:
            True if event was handled, False otherwise
        """
        if not self.active:
            return False
        
        # Handle tile palette button clicks
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            for tile_type, button in self.tile_buttons.items():
                if event.ui_element == button:
                    self.selected_tile_type = tile_type
                    return True
        
        return False
    
    def update(
        self,
        input_handler: InputHandler,
        tile_map: TileMap,
        camera_offset: Tuple[float, float]
    ) -> None:
        """
        Update tile editor (handles mouse clicks for placing/deleting tiles).
        
        Args:
            input_handler: InputHandler instance
            tile_map: TileMap to edit
            camera_offset: Current camera offset
        """
        if not self.active:
            return
        
        # Handle mouse clicks
        if input_handler.is_mouse_button_just_pressed(0):  # Left click
            mouse_pos = input_handler.get_mouse_pos()
            
            # Convert screen to world coordinates
            world_x = mouse_pos[0] + camera_offset[0]
            world_y = mouse_pos[1] + camera_offset[1]
            
            # Convert to grid coordinates
            grid_x, grid_y = tile_map.world_to_grid(world_x, world_y)
            
            # Place or delete tile based on sub-mode
            if self.sub_mode == "Place":
                self._place_tile(tile_map, grid_x, grid_y)
            elif self.sub_mode == "Delete":
                self._delete_tile(tile_map, grid_x, grid_y)
            elif self.sub_mode == "Inspect":
                self._inspect_tile(tile_map, grid_x, grid_y)
    
    def _place_tile(self, tile_map: TileMap, x: int, y: int) -> None:
        """
        Place a tile at grid coordinates.
        
        Args:
            tile_map: TileMap to modify
            x: Grid x coordinate
            y: Grid y coordinate
        """
        tile_data = settings.DEFAULT_TILE_TYPES.get(self.selected_tile_type)
        if tile_data:
            new_tile = Tile(
                tile_type=self.selected_tile_type,
                is_solid=tile_data['is_solid'],
                movement_modifier=tile_data['movement_modifier'],
                color=tile_data['color']
            )
            tile_map.set_tile(x, y, new_tile)
    
    def _delete_tile(self, tile_map: TileMap, x: int, y: int) -> None:
        """
        Delete a tile (replace with floor).
        
        Args:
            tile_map: TileMap to modify
            x: Grid x coordinate
            y: Grid y coordinate
        """
        tile_data = settings.DEFAULT_TILE_TYPES['floor']
        floor_tile = Tile(
            tile_type='floor',
            is_solid=tile_data['is_solid'],
            movement_modifier=tile_data['movement_modifier'],
            color=tile_data['color']
        )
        tile_map.set_tile(x, y, floor_tile)
    
    def _inspect_tile(self, tile_map: TileMap, x: int, y: int) -> None:
        """
        Inspect a tile (placeholder for Phase 3).
        
        Args:
            tile_map: TileMap to inspect
            x: Grid x coordinate
            y: Grid y coordinate
        """
        tile = tile_map.get_tile(x, y)
        if tile:
            print(f"Tile at ({x}, {y}): Type={tile.tile_type}, Solid={tile.is_solid}, Modifier={tile.movement_modifier}")
