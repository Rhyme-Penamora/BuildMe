# =============================================================================
# File: sandbox_game/ui/type_managers.py
# =============================================================================
"""
In-game type manager panels for tiles, entities, and items.
All accessible from within the game — no external file editing needed.
"""

import os
import json
import pygame
import pygame_gui
from typing import Optional, Dict, Any, List
import settings
from inventory.item_registry import item_registry


class TileTypeManager:
    """
    View, add, edit, and delete custom tile types without leaving the game.
    """

    def __init__(self, ui_manager: pygame_gui.UIManager):
        """
        Initialize tile type manager.

        Args:
            ui_manager: pygame_gui UIManager instance
        """
        self.ui_manager = ui_manager
        self.active = False

        sw = settings.SCREEN_WIDTH
        sh = settings.SCREEN_HEIGHT

        pw = int(sw * 0.55)
        ph = int(sh * 0.74)
        px = (sw - pw) // 2
        py = (sh - ph) // 2

        self.panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(px, py, pw, ph),
            manager=ui_manager,
            starting_layer_height=14
        )
        self.panel.hide()

        self.title = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 8, pw - 20, 28),
            text="Tile Type Manager",
            manager=ui_manager,
            container=self.panel
        )

        # Tile list (left)
        list_w = int(pw * 0.38)
        list_h = ph - 100
        self.tile_list = pygame_gui.elements.UISelectionList(
            relative_rect=pygame.Rect(10, 44, list_w, list_h),
            item_list=list(settings.DEFAULT_TILE_TYPES.keys()),
            manager=ui_manager,
            container=self.panel
        )

        # Detail area (right)
        dx = list_w + 20
        dw = pw - dx - 10
        row_h = 30
        row_gap = 8
        y = 44

        def lbl(text: str) -> None:
            nonlocal y
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(dx, y, dw, row_h),
                text=text,
                manager=ui_manager,
                container=self.panel
            )

        lbl("Name:")
        self._name_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(dx, y + row_h, dw, 30),
            manager=ui_manager,
            container=self.panel
        )
        y += row_h + 30 + row_gap

        lbl("Solid (yes/no):")
        self._solid_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(dx, y + row_h, dw, 30),
            manager=ui_manager,
            container=self.panel
        )
        y += row_h + 30 + row_gap

        lbl("Movement modifier (0.0 - 1.0):")
        self._mod_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(dx, y + row_h, dw, 30),
            manager=ui_manager,
            container=self.panel
        )
        y += row_h + 30 + row_gap

        lbl("Color R,G,B (e.g. 100,100,100):")
        self._color_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(dx, y + row_h, dw, 30),
            manager=ui_manager,
            container=self.panel
        )
        y += row_h + 30 + row_gap

        self._add_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(dx, y, 90, 30),
            text="Add/Update",
            manager=ui_manager,
            container=self.panel
        )
        self._delete_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(dx + 100, y, 80, 30),
            text="Delete",
            manager=ui_manager,
            container=self.panel
        )

        self._status = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, ph - 42, pw - 20, 28),
            text="",
            manager=ui_manager,
            container=self.panel
        )

        self._close_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(pw - 110, ph - 42, 100, 32),
            text="Close",
            manager=ui_manager,
            container=self.panel
        )

    def show(self) -> None:
        """Show tile type manager."""
        self.active = True
        self._refresh_list()
        self.panel.show()

    def hide(self) -> None:
        """Hide tile type manager."""
        self.active = False
        self.panel.hide()

    def _refresh_list(self) -> None:
        """Refresh tile list from settings."""
        self.tile_list.set_item_list(list(settings.DEFAULT_TILE_TYPES.keys()))

    def _populate_fields(self, tile_type: str) -> None:
        """
        Fill detail fields with data for a selected tile type.

        Args:
            tile_type: Tile type name string
        """
        data = settings.DEFAULT_TILE_TYPES.get(tile_type, {})
        self._name_entry.set_text(tile_type)
        self._solid_entry.set_text("yes" if data.get('is_solid') else "no")
        self._mod_entry.set_text(str(data.get('movement_modifier', 1.0)))
        color = data.get('color', (100, 100, 100))
        self._color_entry.set_text(f"{color[0]},{color[1]},{color[2]}")

    def _add_or_update(self) -> None:
        """Read fields and add/update a tile type in settings."""
        try:
            name = self._name_entry.get_text().strip().lower()
            if not name:
                self._status.set_text("Name cannot be empty.")
                return
            is_solid = self._solid_entry.get_text().strip().lower() in ('yes', 'true', '1')
            mod = float(self._mod_entry.get_text().strip())
            parts = [int(p.strip()) for p in self._color_entry.get_text().split(',')]
            color = (
                max(0, min(255, parts[0])),
                max(0, min(255, parts[1])),
                max(0, min(255, parts[2])),
            )
            settings.DEFAULT_TILE_TYPES[name] = {
                'is_solid': is_solid,
                'movement_modifier': max(0.0, min(1.0, mod)),
                'color': color,
            }
            self._refresh_list()
            self._status.set_text(f"Tile type '{name}' saved.")
        except (ValueError, IndexError) as e:
            self._status.set_text(f"Input error: {e}")

    def _delete_selected(self) -> None:
        """Delete selected custom tile type (built-ins protected)."""
        selected = self.tile_list.get_single_selection()
        if not selected:
            self._status.set_text("Select a tile type to delete.")
            return
        built_ins = {'floor', 'wall', 'water', 'void'}
        if selected in built_ins:
            self._status.set_text("Cannot delete built-in tile types.")
            return
        settings.DEFAULT_TILE_TYPES.pop(selected, None)
        self._refresh_list()
        self._status.set_text(f"Deleted '{selected}'.")

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle UI events.

        Args:
            event: pygame event

        Returns:
            True if consumed
        """
        if not self.active:
            return False

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self._close_btn:
                self.hide()
                return True
            if event.ui_element == self._add_btn:
                self._add_or_update()
                return True
            if event.ui_element == self._delete_btn:
                self._delete_selected()
                return True

        if event.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
            if event.ui_element == self.tile_list:
                self._populate_fields(event.text)
                return True

        return False


class ItemTypeManager:
    """
    View, add, edit, and delete item types from the global item registry.
    """

    def __init__(self, ui_manager: pygame_gui.UIManager):
        """
        Initialize item type manager.

        Args:
            ui_manager: pygame_gui UIManager instance
        """
        self.ui_manager = ui_manager
        self.active = False

        sw = settings.SCREEN_WIDTH
        sh = settings.SCREEN_HEIGHT

        pw = int(sw * 0.55)
        ph = int(sh * 0.72)
        px = (sw - pw) // 2
        py = (sh - ph) // 2

        self.panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(px, py, pw, ph),
            manager=ui_manager,
            starting_layer_height=14
        )
        self.panel.hide()

        self.title = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 8, pw - 20, 28),
            text="Item Type Manager",
            manager=ui_manager,
            container=self.panel
        )

        list_w = int(pw * 0.36)
        list_h = ph - 100

        self.item_list = pygame_gui.elements.UISelectionList(
            relative_rect=pygame.Rect(10, 44, list_w, list_h),
            item_list=[],
            manager=ui_manager,
            container=self.panel
        )

        dx = list_w + 20
        dw = pw - dx - 10
        y = 44

        fields = [
            ("ID:", '_id_entry', "stick"),
            ("Name:", '_name_entry', "Stick"),
            ("Description:", '_desc_entry', "A plain stick."),
            ("Stackable (yes/no):", '_stack_entry', "yes"),
            ("Max Stack:", '_maxstack_entry', "64"),
        ]
        for label_text, attr, default in fields:
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(dx, y, dw, 26),
                text=label_text,
                manager=ui_manager,
                container=self.panel
            )
            entry = pygame_gui.elements.UITextEntryLine(
                relative_rect=pygame.Rect(dx, y + 26, dw, 28),
                manager=ui_manager,
                container=self.panel
            )
            entry.set_text(default)
            setattr(self, attr, entry)
            y += 62

        self._add_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(dx, y, 110, 30),
            text="Add/Update",
            manager=ui_manager,
            container=self.panel
        )
        self._delete_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(dx + 120, y, 80, 30),
            text="Delete",
            manager=ui_manager,
            container=self.panel
        )

        self._status = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, ph - 42, pw - 120, 28),
            text="",
            manager=ui_manager,
            container=self.panel
        )
        self._close_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(pw - 110, ph - 42, 100, 32),
            text="Close",
            manager=ui_manager,
            container=self.panel
        )

    def show(self) -> None:
        """Show item type manager and refresh list."""
        self.active = True
        self._refresh_list()
        self.panel.show()

    def hide(self) -> None:
        """Hide item type manager."""
        self.active = False
        self.panel.hide()

    def _refresh_list(self) -> None:
        """Refresh item list from registry."""
        self.item_list.set_item_list(list(item_registry._registry.keys()))

    def _populate_fields(self, item_id: str) -> None:
        """
        Fill fields with item type data.

        Args:
            item_id: Item type ID string
        """
        data = item_registry.get_item_type(item_id)
        if not data:
            return
        self._id_entry.set_text(item_id)
        self._name_entry.set_text(data.get('name', ''))
        self._desc_entry.set_text(data.get('description', ''))
        self._stack_entry.set_text("yes" if data.get('stackable', True) else "no")
        self._maxstack_entry.set_text(str(data.get('max_stack', 64)))

    def _add_or_update(self) -> None:
        """Read fields and register/update item type."""
        try:
            item_id = self._id_entry.get_text().strip()
            name = self._name_entry.get_text().strip()
            if not item_id or not name:
                self._status.set_text("ID and Name are required.")
                return
            desc = self._desc_entry.get_text().strip()
            stackable = self._stack_entry.get_text().strip().lower() in ('yes', 'true', '1')
            max_stack = max(1, int(self._maxstack_entry.get_text().strip()))

            item_registry.register_item(item_id, {
                'name': name,
                'description': desc,
                'stackable': stackable,
                'max_stack': max_stack,
                'sprite': None,
                'behavior_script': None,
                'custom_properties': {},
            })
            self._refresh_list()
            self._status.set_text(f"Item '{item_id}' saved.")
        except ValueError as e:
            self._status.set_text(f"Input error: {e}")

    def _delete_selected(self) -> None:
        """Delete selected item type from registry."""
        selected = self.item_list.get_single_selection()
        if not selected:
            self._status.set_text("Select an item to delete.")
            return
        item_registry._registry.pop(selected, None)
        self._refresh_list()
        self._status.set_text(f"Deleted '{selected}'.")

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle UI events.

        Args:
            event: pygame event

        Returns:
            True if consumed
        """
        if not self.active:
            return False

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self._close_btn:
                self.hide()
                return True
            if event.ui_element == self._add_btn:
                self._add_or_update()
                return True
            if event.ui_element == self._delete_btn:
                self._delete_selected()
                return True

        if event.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
            if event.ui_element == self.item_list:
                self._populate_fields(event.text)
                return True

        return False
