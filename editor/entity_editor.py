# =============================================================================
# File: BuildMe/editor/entity_editor.py
# =============================================================================
"""
Entity editor for spawning and configuring entities.
"""

import pygame
import pygame_gui
from typing import Tuple
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
        """Initialize entity editor."""

        self.ui_manager = ui_manager
        self.active = False
        self.selected_entity_type = "npc"
        self.spawn_menu_visible = False

        self.entity_types = ["npc", "enemy"]
        self.selected_entity_index = 0

        screen_width = settings.SCREEN_WIDTH
        screen_height = settings.SCREEN_HEIGHT

        menu_width = int(screen_width * 0.15)
        menu_height = int(screen_height * 0.3)
        menu_x = screen_width - menu_width - 10
        menu_y = int(screen_height * 0.1)

        self.spawn_menu = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(
                menu_x,
                menu_y,
                menu_width,
                menu_height
            ),
            manager=ui_manager
        )

        self.spawn_menu.hide()

        title = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(
                10,
                5,
                menu_width - 20,
                25
            ),
            text="ENTITIES",
            manager=ui_manager,
            container=self.spawn_menu
        )

        button_height = 40
        button_spacing = 10
        y_offset = 40

        self.npc_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(
                10,
                y_offset,
                menu_width - 20,
                button_height
            ),
            text="NPC",
            manager=ui_manager,
            container=self.spawn_menu
        )

        y_offset += button_height + button_spacing

        self.enemy_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(
                10,
                y_offset,
                menu_width - 20,
                button_height
            ),
            text="Enemy",
            manager=ui_manager,
            container=self.spawn_menu
        )

    def activate(self) -> None:
        """Activate entity editor."""

        self.active = True
        self.spawn_menu_visible = True
        self.spawn_menu.show()

        print(
            f"[ENTITY EDITOR] Active | Selected entity: {self.selected_entity_type}"
        )

    def deactivate(self) -> None:
        """Deactivate entity editor."""

        self.active = False
        self.spawn_menu_visible = False
        self.spawn_menu.hide()

        print("[ENTITY EDITOR] Closed")

    def toggle(self) -> None:
        """Toggle entity editor."""

        if self.active:
            self.deactivate()
        else:
            self.activate()

    def _cycle_entity_selection(self, direction: int) -> None:
        """Cycle between available entity types."""

        self.selected_entity_index = (
            self.selected_entity_index + direction
        ) % len(self.entity_types)

        self.selected_entity_type = self.entity_types[
            self.selected_entity_index
        ]

        print(
            f"[ENTITY EDITOR] Selected entity: {self.selected_entity_type}"
        )

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle UI events."""

        if not self.active:
            return False

        if event.type == pygame.MOUSEWHEEL:
            self._cycle_entity_selection(-event.y)
            return True

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFTBRACKET:
                self._cycle_entity_selection(-1)
                return True

            if event.key == pygame.K_RIGHTBRACKET:
                self._cycle_entity_selection(1)
                return True

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.npc_button:
                self.selected_entity_type = "npc"
                self.selected_entity_index = 0

                print("[ENTITY EDITOR] Selected entity: npc")
                return True

            elif event.ui_element == self.enemy_button:
                self.selected_entity_type = "enemy"
                self.selected_entity_index = 1

                print("[ENTITY EDITOR] Selected entity: enemy")
                return True

        return False

    def update(
        self,
        input_handler: InputHandler,
        tile_map: TileMap,
        camera_offset: Tuple[float, float],
        entities: list
    ) -> None:
        """Update entity editor — spawn on left click."""

        if not self.active:
            return

        if input_handler.is_mouse_button_just_pressed(0):
            mouse_pos = input_handler.get_mouse_pos()

            menu_rect = self.spawn_menu.get_relative_rect()

            if menu_rect.collidepoint(mouse_pos):
                return

            world_x = mouse_pos[0] + camera_offset[0]
            world_y = mouse_pos[1] + camera_offset[1]

            grid_x, grid_y = tile_map.world_to_grid(world_x, world_y)

            if not tile_map.is_in_bounds(grid_x, grid_y):
                print("[ENTITY EDITOR] Cannot spawn outside map bounds")
                return

            spawn_x, spawn_y = tile_map.grid_to_world(grid_x, grid_y)

            if self.selected_entity_type == "npc":
                entity = NPC(position=(spawn_x, spawn_y))
                entities.append(entity)

            elif self.selected_entity_type == "enemy":
                entity = Enemy(position=(spawn_x, spawn_y))
                entities.append(entity)

            print(
                f"[ENTITY EDITOR] Spawned {self.selected_entity_type} "
                f"at ({grid_x}, {grid_y})"
            )
