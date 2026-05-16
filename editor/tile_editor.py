# =============================================================================
# File: sandbox_game/editor/tile_editor.py
# =============================================================================
"""
Tile editor — Place/Delete/Inspect/Select with expansion support.
"""

import pygame
import pygame_gui
from typing import Optional, Tuple, Callable
from world.tile_map import TileMap
from world.tile import Tile
from core.input_handler import InputHandler
import settings


class TileEditor:
    """Tile editing with sub-modes and world expansion."""

    def __init__(self, ui_manager: pygame_gui.UIManager):
        self.ui_manager = ui_manager
        self.active = False
        self.sub_mode = "Place"
        self.selected_tile_type = "floor"
        self.tile_palette_visible = False
        self.on_expansion_needed: Optional[Callable[[str], None]] = None

        sw = settings.SCREEN_WIDTH
        sh = settings.SCREEN_HEIGHT

        pw = int(sw * 0.13)
        ph = int(sh * 0.5)
        px = sw - pw - 8
        py = int(sh * 0.25)

        self.palette_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(px, py, pw, ph),
            manager=ui_manager
        )
        self.palette_panel.hide()

        # Header label
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(4, 4, pw - 8, 22),
            text="TILES",
            manager=ui_manager,
            container=self.palette_panel
        )

        btn_h = 38
        gap = 6
        y = 30

        self.tile_buttons = {}
        for tile_type in settings.DEFAULT_TILE_TYPES:
            td = settings.DEFAULT_TILE_TYPES[tile_type]
            btn = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(6, y, pw - 12, btn_h),
                text=tile_type.capitalize(),
                manager=ui_manager,
                container=self.palette_panel
            )
            self.tile_buttons[tile_type] = btn
            y += btn_h + gap

        # Sub-mode buttons
        sub_label_y = y + 6
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(4, sub_label_y, pw - 8, 20),
            text="MODE",
            manager=ui_manager,
            container=self.palette_panel
        )
        y = sub_label_y + 24

        self._sub_buttons = {}
        for key, label in [("Place","1:Place"),("Delete","2:Delete"),
                            ("Inspect","3:Inspect"),("Select","4:Select")]:
            btn = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(6, y, pw - 12, 32),
                text=label,
                manager=ui_manager,
                container=self.palette_panel
            )
            self._sub_buttons[key] = btn
            y += 32 + 4

    def activate(self) -> None:
        self.active = True
        self.palette_panel.show()

    def deactivate(self) -> None:
        self.active = False
        self.palette_panel.hide()

    def toggle(self) -> None:
        if self.active:
            self.deactivate()
        else:
            self.activate()

    def set_sub_mode(self, mode: str) -> None:
        self.sub_mode = mode

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.active:
            return False
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            for tile_type, btn in self.tile_buttons.items():
                if event.ui_element == btn:
                    self.selected_tile_type = tile_type
                    return True
            for mode, btn in self._sub_buttons.items():
                if event.ui_element == btn:
                    self.sub_mode = mode
                    return True
        return False

    def update(
        self,
        input_handler: InputHandler,
        tile_map: TileMap,
        camera_offset: Tuple[float, float]
    ) -> None:
        if not self.active:
            return
        if input_handler.is_mouse_button_just_pressed(0):
            mx, my = input_handler.get_mouse_pos()

            # Don't act if clicking inside palette panel
            pw = int(settings.SCREEN_WIDTH * 0.13)
            ph = int(settings.SCREEN_HEIGHT * 0.5)
            px = settings.SCREEN_WIDTH - pw - 8
            py = int(settings.SCREEN_HEIGHT * 0.25)
            if pygame.Rect(px, py, pw, ph).collidepoint(mx, my):
                return

            world_x = mx + camera_offset[0]
            world_y = my + camera_offset[1]
            gx, gy = tile_map.world_to_grid(world_x, world_y)

            if self.sub_mode == "Place":
                self._place_tile(tile_map, gx, gy)
            elif self.sub_mode == "Delete":
                self._delete_tile(tile_map, gx, gy)
            elif self.sub_mode == "Inspect":
                self._inspect_tile(tile_map, gx, gy)

    def _place_tile(self, tile_map: TileMap, x: int, y: int) -> None:
        """Place tile, trigger expansion if at/outside edge."""
        if not tile_map.is_in_bounds(x, y):
            direction = tile_map.get_expansion_direction(x, y)
            if direction and self.on_expansion_needed:
                self.on_expansion_needed(direction)
            return

        # Also trigger expansion prompt when placing on exact edge
        if tile_map.is_at_edge(x, y) and self.on_expansion_needed:
            direction = tile_map.get_expansion_direction(
                x - 1 if x == 0 else (x + 1 if x == tile_map.width - 1 else x),
                y - 1 if y == 0 else (y + 1 if y == tile_map.height - 1 else y)
            )
            if direction:
                self.on_expansion_needed(direction)

        td = settings.DEFAULT_TILE_TYPES.get(self.selected_tile_type)
        if td:
            tile_map.set_tile(x, y, Tile(
                self.selected_tile_type,
                td['is_solid'],
                td['movement_modifier'],
                td['color']
            ))

    def _delete_tile(self, tile_map: TileMap, x: int, y: int) -> None:
        if not tile_map.is_in_bounds(x, y):
            return
        td = settings.DEFAULT_TILE_TYPES['floor']
        tile_map.set_tile(x, y, Tile(
            'floor', td['is_solid'], td['movement_modifier'], td['color']
        ))

    def _inspect_tile(self, tile_map: TileMap, x: int, y: int) -> None:
        tile = tile_map.get_tile(x, y)
        if tile:
            print(
                f"Tile ({x},{y}): type={tile.tile_type} "
                f"solid={tile.is_solid} mod={tile.movement_modifier}"
            )
