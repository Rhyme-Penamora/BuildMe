# =============================================================================
# File: BuildMe/core/game.py
# =============================================================================
"""
Main game loop — all systems wired, runtime resize support improved.
"""

import pygame
import pygame_gui
import os
import json
from typing import Optional, Tuple

from core.renderer import Renderer
from core.input_handler import InputHandler
from core.event_bus import event_bus
from core.hot_reload import HotReloadManager

from world.tile_map import TileMap
from world.world_manager import WorldManager
from world.world import World
from world.tile import Tile

from entities.player import Player
from entities.npc import NPC
from entities.enemy import Enemy

from editor.tile_editor import TileEditor
from editor.entity_editor import EntityEditor
from editor.code_editor import CodeEditor
from editor.inventory_editor import InventoryEditor
from editor.sprite_editor import SpriteEditor
from editor.file_editor import FileEditor

from ui.hud import HUD
from ui.game_menu import GameMenu
from ui.developer_console import DeveloperConsole
from ui.help_panel import HelpPanel
from ui.tutorial import TutorialMode
from ui.settings_menu import SettingsMenu
from ui.mobile_controls import MobileControls
from ui.player_customize import PlayerCustomizePanel
from ui.type_managers import TileTypeManager, ItemTypeManager
from ui.popup import Popup

from scripting.api import ScriptingAPI
from scripting.sandbox import ScriptSandbox
from scripting.validator import ScriptValidator

from inventory.item_registry import item_registry

import settings


class Game:
    """Main game class — all systems integrated."""

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0.0

        self.ui_manager = pygame_gui.UIManager(
            (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
        )

        self.renderer = Renderer(screen)
        self.input_handler = InputHandler()
        self.world_manager = WorldManager()
        self.hot_reload_manager = HotReloadManager()

        self.current_world: Optional[World] = None
        self.player: Optional[Player] = None
        self.camera_offset = [0.0, 0.0]
        self.game_mode = "play"

        self.dialogue_text: Optional[str] = None
        self.dialogue_timer = 0.0
        self.dialogue_duration = 3.0
        self._background_surface: Optional[pygame.Surface] = None

        self._npc_panel: Optional[pygame_gui.elements.UIWindow] = None
        self._npc_panel_target: Optional[NPC] = None
        self._npc_name_entry = None
        self._npc_dialogue_entry = None
        self._npc_apply_btn = None
        self._npc_edit_script_btn = None

        self._expansion_popup: Optional[Popup] = None

        self.api = ScriptingAPI(self)
        self.sandbox = ScriptSandbox(self.api)
        self.validator = ScriptValidator()

        self.tile_editor = TileEditor(self.ui_manager)
        self.entity_editor = EntityEditor(self.ui_manager)
        self.code_editor = CodeEditor(self.ui_manager)
        self.inventory_editor = InventoryEditor(self.ui_manager)
        self.sprite_editor = SpriteEditor(self.ui_manager)
        self.file_editor = FileEditor(self.ui_manager)

        self.hud = HUD(screen)
        self.game_menu = GameMenu(self.ui_manager)
        self.console = DeveloperConsole(self.ui_manager)
        self.help_panel = HelpPanel(self.ui_manager)
        self.tutorial = TutorialMode(self.ui_manager)

        self.settings_menu = SettingsMenu(self.ui_manager)
        self.mobile_controls = MobileControls(
            self.input_handler, settings.KEYBINDINGS
        )
        self.player_customize = PlayerCustomizePanel(self.ui_manager)
        self.tile_type_manager = TileTypeManager(self.ui_manager)
        self.item_type_manager = ItemTypeManager(self.ui_manager)

        self.settings_menu.load_global()

        if settings.GLOBAL_SETTINGS.get('mobile_controls'):
            self.mobile_controls.enable()

        self.tile_editor.on_expansion_needed = self._handle_world_expansion

        self._wire_callbacks()
        self._register_console_commands()
        self._subscribe_fab_events()

        try:
            self.dialogue_font = pygame.font.Font(None, 28)
        except Exception:
            self.dialogue_font = None

    def _handle_resize(self, width: int, height: int) -> None:
        """Centralized runtime resize handling."""

        width = max(800, width)
        height = max(600, height)

        settings.SCREEN_WIDTH = width
        settings.SCREEN_HEIGHT = height

        self.screen = pygame.display.set_mode(
            (width, height),
            pygame.RESIZABLE
        )

        self.renderer.screen = self.screen
        self.hud.screen = self.screen

        self.ui_manager.set_window_resolution((width, height))

        if self._background_surface is not None:
            try:
                self._background_surface = pygame.transform.scale(
                    self._background_surface,
                    (width, height)
                )
            except Exception:
                pass

        print(f"[WINDOW] Resized to {width}x{height}")

    def _wire_callbacks(self) -> None:
        self.code_editor.on_save = self._on_script_saved
        self.game_menu.on_save = self._save_world
        self.game_menu.on_exit_to_menu = self._exit_to_main_menu
        self.game_menu.on_settings = self._open_settings
        self.game_menu.on_help = lambda: self.help_panel.toggle()
        self.game_menu.on_file_editor = lambda: self.file_editor.toggle()
        self.game_menu.on_tutorial = self._start_tutorial
        self.game_menu.on_customize_player = self._open_player_customize
        self.settings_menu.on_apply = self._on_settings_applied
        self.tutorial.on_exit = lambda: None
        self.player_customize.on_open_sprite_editor = (
            lambda p: self.sprite_editor.show(target=p, category='sprites')
        )

    def _subscribe_fab_events(self) -> None:
        event_bus.subscribe('fab_save', lambda _: self._save_world())
        event_bus.subscribe('fab_help', lambda _: self.help_panel.toggle())
        event_bus.subscribe('fab_settings', lambda _: self._open_settings())
        event_bus.subscribe('fab_file_editor', lambda _: self.file_editor.toggle())
        event_bus.subscribe('fab_exit_menu', lambda _: self._exit_to_main_menu())

    def load_world(self, world: World) -> None:
        self.current_world = world
        self.world_manager.current_world = world

        world_dir = os.path.join(
            "worlds",
            self.world_manager._sanitize_filename(world.name)
        )

        os.makedirs(os.path.join(world_dir, "behaviors"), exist_ok=True)

        self.hot_reload_manager.start_watching(
            os.path.join(world_dir, "behaviors"),
            self._on_behavior_file_changed
        )

        item_registry.load_from_json(
            os.path.join(world_dir, "items", "items.json")
        )

        self._load_world_settings(world_dir)
        self._reload_all_entity_scripts()

        bg = world.metadata.get('background_image')

        if bg and os.path.exists(bg):
            self._load_background(bg)

        cx = (
            world.tile_map.width * world.tile_map.tile_size / 2 -
            settings.PLAYER_SIZE / 2
        )

        cy = (
            world.tile_map.height * world.tile_map.tile_size / 2 -
            settings.PLAYER_SIZE / 2
        )

        self.player = Player(position=(cx, cy))

        self._update_camera_immediate()
        self._update_hud()

    def _load_world_settings(self, world_dir: str) -> None:
        path = os.path.join(world_dir, "settings.json")

        if not os.path.exists(path):
            return

        try:
            with open(path) as f:
                data = json.load(f)

            iv = data.get('auto_save_interval')

            if iv:
                self.world_manager.auto_save_interval = float(iv)

        except Exception as e:
            print(f"World settings load error: {e}")

    def _load_background(self, path: str) -> None:
        try:
            surf = pygame.image.load(path).convert()

            self._background_surface = pygame.transform.scale(
                surf,
                (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
            )

        except Exception as e:
            print(f"Background error: {e}")
            self._background_surface = None

    def run(self) -> None:
        while self.running:
            self.dt = self.clock.tick(
                settings.GLOBAL_SETTINGS.get('target_fps', settings.FPS)
            ) / 1000.0

            events = pygame.event.get()

            for event in events:
                if event.type == pygame.VIDEORESIZE:
                    self._handle_resize(event.w, event.h)

            if self.mobile_controls.enabled:
                self.mobile_controls.update(events)

            self._handle_events(events)
            self._update(self.dt)
            self._render()

        self.hot_reload_manager.stop_watching()
