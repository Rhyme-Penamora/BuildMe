# =============================================================================
# File: sandbox_game/core/game.py
# =============================================================================
"""
Main game loop and state management — Phase 5 full integration.
"""

import pygame
import pygame_gui
import os
import json
from typing import Optional

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

from scripting.api import ScriptingAPI
from scripting.sandbox import ScriptSandbox
from scripting.validator import ScriptValidator

from inventory.item_registry import item_registry

import settings


class Game:
    """
    Main game class — Phase 5 complete with mobile, settings, type managers,
    player customization, HUD toggles, and event bus wiring.
    """

    def __init__(self, screen: pygame.Surface):
        """
        Initialize all game systems.

        Args:
            screen: Main pygame display surface
        """
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0.0

        self.ui_manager = pygame_gui.UIManager(
            (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
        )

        # Core systems
        self.renderer = Renderer(screen)
        self.input_handler = InputHandler()
        self.world_manager = WorldManager()
        self.hot_reload_manager = HotReloadManager()

        # World / player
        self.current_world: Optional[World] = None
        self.player: Optional[Player] = None
        self.camera_offset = [0.0, 0.0]

        # Game mode
        self.game_mode = "play"

        # Dialogue
        self.dialogue_text: Optional[str] = None
        self.dialogue_timer = 0.0
        self.dialogue_duration = 3.0

        # Background
        self._background_surface: Optional[pygame.Surface] = None

        # Scripting
        self.api = ScriptingAPI(self)
        self.sandbox = ScriptSandbox(self.api)
        self.validator = ScriptValidator()

        # Editors
        self.tile_editor = TileEditor(self.ui_manager)
        self.entity_editor = EntityEditor(self.ui_manager)
        self.code_editor = CodeEditor(self.ui_manager)
        self.inventory_editor = InventoryEditor(self.ui_manager)
        self.sprite_editor = SpriteEditor(self.ui_manager)
        self.file_editor = FileEditor(self.ui_manager)

        # UI panels
        self.hud = HUD(screen)
        self.game_menu = GameMenu(self.ui_manager)
        self.console = DeveloperConsole(self.ui_manager)
        self.help_panel = HelpPanel(self.ui_manager)
        self.tutorial = TutorialMode(self.ui_manager)

        # Phase 5 additions
        self.settings_menu = SettingsMenu(self.ui_manager)
        self.mobile_controls = MobileControls(self.input_handler, settings.KEYBINDINGS)
        self.player_customize = PlayerCustomizePanel(self.ui_manager)
        self.tile_type_manager = TileTypeManager(self.ui_manager)
        self.item_type_manager = ItemTypeManager(self.ui_manager)

        # Load persisted global settings before anything runs
        self.settings_menu.load_global()

        # Enable mobile controls if saved setting says so
        if settings.GLOBAL_SETTINGS.get('mobile_controls'):
            self.mobile_controls.enable()

        # Wire all callbacks
        self._wire_callbacks()

        # Register console commands
        self._register_console_commands()

        # Subscribe to FAB events
        self._subscribe_fab_events()

        # Dialogue font
        try:
            self.dialogue_font = pygame.font.Font(None, 28)
        except Exception:
            self.dialogue_font = None

    # ------------------------------------------------------------------
    # Callback wiring
    # ------------------------------------------------------------------

    def _wire_callbacks(self) -> None:
        """Connect all inter-system callbacks."""
        self.code_editor.on_save = self._on_script_saved
        self.game_menu.on_save = self._save_world
        self.game_menu.on_exit_to_menu = self._exit_to_main_menu
        self.game_menu.on_settings = self._open_settings
        self.game_menu.on_help = lambda: self.help_panel.toggle()
        self.game_menu.on_file_editor = lambda: self.file_editor.toggle()
        self.game_menu.on_tutorial = lambda: self.tutorial.show() if hasattr(self.tutorial, 'show') else None
        self.game_menu.on_customize_player = self._open_player_customize

        self.settings_menu.on_apply = self._on_settings_applied
        self.settings_menu.on_close = lambda: None

        self.tutorial.on_exit = lambda: None

        self.player_customize.on_open_sprite_editor = (
            lambda p: self.sprite_editor.show(target=p, category='sprites')
        )

    # ------------------------------------------------------------------
    # FAB event bus subscriptions
    # ------------------------------------------------------------------

    def _subscribe_fab_events(self) -> None:
        """Subscribe to FAB menu events from mobile controls."""
        event_bus.subscribe('fab_save',        lambda _: self._save_world())
        event_bus.subscribe('fab_help',        lambda _: self.help_panel.toggle())
        event_bus.subscribe('fab_settings',    lambda _: self._open_settings())
        event_bus.subscribe('fab_file_editor', lambda _: self.file_editor.toggle())
        event_bus.subscribe('fab_exit_menu',   lambda _: self._exit_to_main_menu())

    # ------------------------------------------------------------------
    # World loading
    # ------------------------------------------------------------------

    def load_world(self, world: World) -> None:
        """
        Load a world and initialize all world-specific systems.

        Args:
            world: World instance to load
        """
        self.current_world = world
        self.world_manager.current_world = world

        world_dir = os.path.join(
            "worlds", self.world_manager._sanitize_filename(world.name)
        )
        behaviors_dir = os.path.join(world_dir, "behaviors")
        os.makedirs(behaviors_dir, exist_ok=True)

        self.hot_reload_manager.start_watching(
            behaviors_dir, self._on_behavior_file_changed
        )

        item_registry.load_from_json(
            os.path.join(world_dir, "items", "items.json")
        )

        # Load world-specific settings
        self._load_world_settings(world_dir)

        self._reload_all_entity_scripts()

        bg_path = world.metadata.get('background_image')
        if bg_path and os.path.exists(bg_path):
            self._load_background(bg_path)

        center_x = (
            world.tile_map.width * world.tile_map.tile_size / 2
            - settings.PLAYER_SIZE / 2
        )
        center_y = (
            world.tile_map.height * world.tile_map.tile_size / 2
            - settings.PLAYER_SIZE / 2
        )
        self.player = Player(position=(center_x, center_y))

        self._update_camera_immediate()
        self._update_hud()

    def _load_world_settings(self, world_dir: str) -> None:
        """
        Load per-world settings from settings.json in world folder.

        Args:
            world_dir: Absolute path to world directory
        """
        settings_path = os.path.join(world_dir, "settings.json")
        if not os.path.exists(settings_path):
            return
        try:
            with open(settings_path, 'r') as f:
                data = json.load(f)
            interval = data.get('auto_save_interval')
            if interval:
                self.world_manager.auto_save_interval = float(interval)
        except Exception as e:
            print(f"World settings load error: {e}")

    # ------------------------------------------------------------------
    # Background
    # ------------------------------------------------------------------

    def _load_background(self, path: str) -> None:
        """
        Load and scale world background image.

        Args:
            path: Path to image file
        """
        try:
            surf = pygame.image.load(path).convert()
            self._background_surface = pygame.transform.scale(
                surf, (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
            )
        except Exception as e:
            print(f"Background load error: {e}")
            self._background_surface = None

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def run(self) -> None:
        """Main game loop."""
        while self.running:
            self.dt = self.clock.tick(settings.GLOBAL_SETTINGS.get('target_fps', settings.FPS)) / 1000.0
            events = pygame.event.get()

            # Mobile controls process first (injects virtual input)
            if self.mobile_controls.enabled:
                self.mobile_controls.update(events)

            self._handle_events(events)
            self._update(self.dt)
            self._render()

        self.hot_reload_manager.stop_watching()

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------

    def _handle_events(self, events: list) -> None:
        """
        Dispatch all pygame events to correct subsystems.

        Args:
            events: List of pygame events
        """
        for event in events:
            self.ui_manager.process_events(event)

            if event.type == pygame.QUIT:
                self._save_world()
                self.running = False
                continue

            # Settings menu (highest priority overlay)
            if self.settings_menu.active:
                if self.settings_menu.handle_event(event):
                    continue

            # Player customize panel
            if self.player_customize.active:
                if self.player_customize.handle_event(event):
                    continue

            # Type managers
            if self.tile_type_manager.active:
                if self.tile_type_manager.handle_event(event):
                    continue
            if self.item_type_manager.active:
                if self.item_type_manager.handle_event(event):
                    continue

            # File editor
            if self.file_editor.active:
                if self.file_editor.handle_event(event):
                    continue

            # Code editor
            if self.code_editor.active:
                if self.code_editor.handle_event(event):
                    continue

            # Sprite editor
            if self.sprite_editor.active:
                world_name = self.current_world.name if self.current_world else ""
                if self.sprite_editor.handle_event(event, world_name):
                    continue

            # Help panel
            if self.help_panel.active:
                if self.help_panel.handle_event(event):
                    continue

            # Tutorial
            if self.tutorial.active:
                if self.tutorial.handle_event(event):
                    continue

            # Inventory editor
            if self.inventory_editor.active:
                if self.inventory_editor.handle_event(event):
                    continue

            # Game menu
            if self.game_menu.active:
                if self.game_menu.handle_event(event):
                    continue

            # Console toggle
            if event.type == pygame.KEYDOWN:
                kb = settings.KEYBINDINGS
                if event.key == kb.get('console', pygame.K_BACKQUOTE):
                    self.console.toggle()
                    continue

            if self.console.active:
                if self.console.handle_event(event):
                    continue

            if event.type == pygame.KEYDOWN:
                self._handle_keydown(event)

            if self.tile_editor.active:
                self.tile_editor.handle_event(event)

            if self.entity_editor.active:
                self.entity_editor.handle_event(event)

        self.input_handler.update(events)

    def _handle_keydown(self, event: pygame.event.Event) -> None:
        """
        Handle keyboard shortcuts using current keybindings.

        Args:
            event: KEYDOWN pygame event
        """
        if self.game_menu.active or self.console.active or self.code_editor.active:
            return

        kb = settings.KEYBINDINGS

        if event.key == kb.get('menu', pygame.K_ESCAPE):
            self.game_menu.toggle()

        elif event.key == kb.get('inventory', pygame.K_TAB):
            if self.player and settings.GAME_RULES.get('inventory_system', True):
                self.inventory_editor.toggle(self.player.inventory)

        elif event.key == kb.get('help', pygame.K_h):
            self.help_panel.toggle()

        elif event.key == kb.get('build_mode', pygame.K_b):
            if settings.GAME_RULES.get('build_mode', True):
                self._toggle_build_mode()

        elif event.key == kb.get('entity_editor', pygame.K_e):
            if (self.game_mode == "build" and
                    settings.GAME_RULES.get('entity_spawning', True)):
                self._toggle_entity_editor()

        elif event.key == kb.get('interact', pygame.K_f):
            self._interact_with_nearby_entity()

        elif self.game_mode == "build":
            if event.key == kb.get('sub_place', pygame.K_1):
                self.tile_editor.set_sub_mode("Place")
                self.entity_editor.deactivate()
                self.tile_editor.activate()
            elif event.key == kb.get('sub_delete', pygame.K_2):
                self.tile_editor.set_sub_mode("Delete")
                self.entity_editor.deactivate()
                self.tile_editor.activate()
            elif event.key == kb.get('sub_inspect', pygame.K_3):
                self.tile_editor.set_sub_mode("Inspect")
                self.entity_editor.deactivate()
                self.tile_editor.activate()
            elif event.key == kb.get('sub_select', pygame.K_4):
                self.tile_editor.set_sub_mode("Select")
                self.entity_editor.deactivate()
                self.tile_editor.activate()

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def _update(self, dt: float) -> None:
        """
        Update all game systems.

        Args:
            dt: Delta time in seconds
        """
        self.ui_manager.update(dt)

        if self.sprite_editor.active:
            self.sprite_editor.update(dt)

        if self.tutorial.active:
            self.tutorial.update(dt)

        if (self.game_menu.active or
                self.code_editor.active or
                self.inventory_editor.active or
                self.settings_menu.active):
            return

        self.world_manager.update(dt)

        if not self.current_world or not self.player:
            return

        if not self.console.active:
            self.player.update(dt, self.input_handler, self.current_world.tile_map)

        for entity in list(self.current_world.entities):
            entity.update(dt)

        self.current_world.entities = [
            e for e in self.current_world.entities
            if not (isinstance(e, Enemy) and e.is_dead)
        ]

        self._update_camera(dt)

        if self.tile_editor.active and not self.console.active:
            self.tile_editor.update(
                self.input_handler,
                self.current_world.tile_map,
                tuple(self.camera_offset)
            )

        if self.entity_editor.active and not self.console.active:
            self.entity_editor.update(
                self.input_handler,
                self.current_world.tile_map,
                tuple(self.camera_offset),
                self.current_world.entities
            )

        if self.dialogue_text:
            self.dialogue_timer -= dt
            if self.dialogue_timer <= 0:
                self.dialogue_text = None

        self._update_hud()

    # ------------------------------------------------------------------
    # Camera
    # ------------------------------------------------------------------

    def _update_camera(self, dt: float) -> None:
        """Smooth lerp camera to player position."""
        if not self.player:
            return
        target_x = (
            self.player.position[0] + self.player.size[0] / 2
            - settings.SCREEN_WIDTH / 2
        )
        target_y = (
            self.player.position[1] + self.player.size[1] / 2
            - settings.SCREEN_HEIGHT / 2
        )
        lerp = min(1.0, settings.CAMERA_LERP_SPEED * dt)
        self.camera_offset[0] += (target_x - self.camera_offset[0]) * lerp
        self.camera_offset[1] += (target_y - self.camera_offset[1]) * lerp

    def _update_camera_immediate(self) -> None:
        """Snap camera directly to player."""
        if not self.player:
            return
        self.camera_offset[0] = (
            self.player.position[0] + self.player.size[0] / 2
            - settings.SCREEN_WIDTH / 2
        )
        self.camera_offset[1] = (
            self.player.position[1] + self.player.size[1] / 2
            - settings.SCREEN_HEIGHT / 2
        )

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def _render(self) -> None:
        """Render all layers in order."""
        if self._background_surface:
            self.screen.blit(self._background_surface, (0, 0))
        else:
            self.renderer.clear()

        if self.current_world and self.player:
            self.renderer.render_tile_map(
                self.current_world.tile_map, tuple(self.camera_offset)
            )
            self.renderer.render_entities(
                self.current_world.entities, tuple(self.camera_offset)
            )
            self.renderer.render_entity(self.player, tuple(self.camera_offset))
            self._render_entity_labels()

            if self.dialogue_text:
                self._render_dialogue(self.dialogue_text)

            self.hud.render()

        if self.sprite_editor.active:
            self.sprite_editor.render_preview(self.screen)

        # Mobile controls drawn last (always on top)
        if self.mobile_controls.enabled:
            self.mobile_controls.render(self.screen)

        self.ui_manager.draw_ui(self.screen)
        self.renderer.present()

    def _render_entity_labels(self) -> None:
        """Render name labels above every entity in view."""
        if not self.current_world:
            return
        try:
            font = pygame.font.Font(None, 20)
        except Exception:
            return

        for entity in self.current_world.entities:
            sx = entity.position[0] - self.camera_offset[0]
            sy = entity.position[1] - self.camera_offset[1] - 18
            if (-100 <= sx <= settings.SCREEN_WIDTH + 100 and
                    -100 <= sy <= settings.SCREEN_HEIGHT + 100):
                label = font.render(entity.name, True, settings.COLORS['white'])
                self.screen.blit(label, (int(sx), int(sy)))

    def _render_dialogue(self, text: str) -> None:
        """
        Render dialogue box at screen bottom.

        Args:
            text: Dialogue string
        """
        if not self.dialogue_font:
            return
        box_w = int(settings.SCREEN_WIDTH * 0.6)
        box_h = 70
        box_x = (settings.SCREEN_WIDTH - box_w) // 2
        box_y = settings.SCREEN_HEIGHT - box_h - 20

        box_surf = pygame.Surface((box_w, box_h))
        box_surf.set_alpha(220)
        box_surf.fill((20, 20, 40))
        self.screen.blit(box_surf, (box_x, box_y))

        pygame.draw.rect(
            self.screen, settings.COLORS['white'],
            pygame.Rect(box_x, box_y, box_w, box_h), 2
        )
        txt = self.dialogue_font.render(text, True, settings.COLORS['white'])
        self.screen.blit(
            txt,
            (box_x + 15, box_y + (box_h - txt.get_height()) // 2)
        )

    # ------------------------------------------------------------------
    # HUD
    # ------------------------------------------------------------------

    def _update_hud(self) -> None:
        """Sync HUD values with current game state."""
        if not self.current_world or not self.player:
            return

        gx, gy = self.current_world.tile_map.world_to_grid(
            self.player.position[0] + self.player.size[0] / 2,
            self.player.position[1] + self.player.size[1] / 2
        )

        sub_mode = ""
        if self.game_mode == "build":
            if self.entity_editor.active:
                sub_mode = f"Entity ({self.entity_editor.selected_entity_type})"
            else:
                sub_mode = self.tile_editor.sub_mode

        hp = getattr(self.player, 'health', 100)
        max_hp = getattr(self.player, 'max_health', 100)

        self.hud.update(
            mode="Build" if self.game_mode == "build" else "Play",
            sub_mode=sub_mode,
            selected_tile=self.tile_editor.selected_tile_type,
            world_name=self.current_world.name,
            player_pos=(gx, gy),
            player_health=hp,
            player_max_health=max_hp,
        )

    # ------------------------------------------------------------------
    # Build mode helpers
    # ------------------------------------------------------------------

    def _toggle_build_mode(self) -> None:
        """Toggle between play and build modes."""
        if self.game_mode == "play":
            self.game_mode = "build"
            self.tile_editor.activate()
        else:
            self.game_mode = "play"
            self.tile_editor.deactivate()
            self.entity_editor.deactivate()

    def _toggle_entity_editor(self) -> None:
        """Toggle entity editor within build mode."""
        if self.entity_editor.active:
            self.entity_editor.deactivate()
            self.tile_editor.activate()
        else:
            self.entity_editor.activate()
            self.tile_editor.deactivate()

    # ------------------------------------------------------------------
    # Interaction
    # ------------------------------------------------------------------

    def _interact_with_nearby_entity(self) -> None:
        """Find nearest NPC within range and trigger dialogue."""
        if not self.current_world or not self.player:
            return
        interact_range = settings.TILE_SIZE * 1.5
        closest = None
        closest_dist = float('inf')

        for entity in self.current_world.entities:
            if isinstance(entity, NPC):
                dx = entity.position[0] - self.player.position[0]
                dy = entity.position[1] - self.player.position[1]
                dist = (dx * dx + dy * dy) ** 0.5
                if dist < interact_range and dist < closest_dist:
                    closest_dist = dist
                    closest = entity

        if closest:
            dialogue = closest.on_interact(self.player)
            if dialogue:
                self.show_dialogue(dialogue)

    def show_dialogue(self, text: str) -> None:
        """
        Display dialogue text for dialogue_duration seconds.

        Args:
            text: String to display
        """
        self.dialogue_text = text
        self.dialogue_timer = self.dialogue_duration

    # ------------------------------------------------------------------
    # Settings callbacks
    # ------------------------------------------------------------------

    def _open_settings(self) -> None:
        """Open the settings menu."""
        self.settings_menu.show()

    def _on_settings_applied(
        self,
        keybindings: dict,
        game_rules: dict,
        global_cfg: dict,
    ) -> None:
        """
        React to settings changes applied by the user.

        Args:
            keybindings: Updated keybinding dict
            game_rules:  Updated game rules dict
            global_cfg:  Updated global settings dict
        """
        # Update mobile controls
        if global_cfg.get('mobile_controls'):
            self.mobile_controls.keybindings = keybindings
            self.mobile_controls.set_dpad_size(global_cfg.get('dpad_size', 80))
            self.mobile_controls.set_action_btn_size(global_cfg.get('action_btn_size', 64))
            self.mobile_controls.enable()
        else:
            self.mobile_controls.disable()

        # Fullscreen toggle
        if global_cfg.get('fullscreen'):
            pygame.display.set_mode(
                (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT),
                pygame.FULLSCREEN
            )
        else:
            pygame.display.set_mode(
                (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
            )

    # ------------------------------------------------------------------
    # Player customization
    # ------------------------------------------------------------------

    def _open_player_customize(self) -> None:
        """Open the player customization panel."""
        if self.player:
            self.player_customize.show(self.player)

    # ------------------------------------------------------------------
    # Hot reload
    # ------------------------------------------------------------------

    def _on_behavior_file_changed(self, filepath: str) -> None:
        """
        Watchdog callback — reload entity scripts when files change.

        Args:
            filepath: Changed file path
        """
        if not self.current_world:
            return
        for entity in self.current_world.entities:
            if getattr(entity, 'behavior_script', None):
                if (os.path.normpath(entity.behavior_script) ==
                        os.path.normpath(filepath)):
                    self._reload_entity_script(entity)
                    self.console.log(f"Hot reloaded: {entity.name}", "#00FFFF")

    def _reload_entity_script(self, entity) -> None:
        """
        Reload and attach behavior module to an entity.

        Args:
            entity: Entity to reload
        """
        if not entity.behavior_script:
            return
        safe_globals = self.sandbox.get_safe_globals()
        ok, module, error = self.hot_reload_manager.reload_script(
            entity.behavior_script, safe_globals
        )
        if ok:
            entity.behavior_module = module
            if hasattr(module, 'on_spawn'):
                try:
                    module.on_spawn(entity)
                except Exception as e:
                    print(f"on_spawn error: {e}")
        else:
            self.console.log(f"Reload error: {error}", "#FF0000")

    def _reload_all_entity_scripts(self) -> None:
        """Load behavior scripts for every entity in current world."""
        if not self.current_world:
            return
        safe_globals = self.sandbox.get_safe_globals()
        for entity in self.current_world.entities:
            if getattr(entity, 'behavior_script', None):
                ok, module, error = self.hot_reload_manager.load_script(
                    entity.behavior_script, safe_globals
                )
                if ok:
                    entity.behavior_module = module
                else:
                    print(f"Script load error for {entity.name}: {error}")

    def _on_script_saved(self, filepath: str) -> None:
        """
        Code editor save callback — hot reload matching entity scripts.

        Args:
            filepath: Saved script file path
        """
        if not self.current_world:
            return
        reloaded = False
        for entity in self.current_world.entities:
            if getattr(entity, 'behavior_script', None):
                if (os.path.normpath(entity.behavior_script) ==
                        os.path.normpath(filepath)):
                    self._reload_entity_script(entity)
                    reloaded = True

        self.tutorial.notify_task_complete("save_script")
        msg = (
            f"Hot reloaded: {os.path.basename(filepath)}"
            if reloaded
            else f"Saved: {os.path.basename(filepath)}"
        )
        self.console.log(msg, "#00FFFF" if reloaded else "#00FF00")

    # ------------------------------------------------------------------
    # Save / exit
    # ------------------------------------------------------------------

    def _save_world(self) -> None:
        """Save current world to disk."""
        if self.current_world:
            ok = self.world_manager.save_world(self.current_world)
            self.console.log(
                "World saved." if ok else "Save failed.",
                "#00FF00" if ok else "#FF0000"
            )

    def _exit_to_main_menu(self) -> None:
        """Save world and stop game loop."""
        self._save_world()
        self.running = False

    # ------------------------------------------------------------------
    # Console commands (Phase 5 additions + full set)
    # ------------------------------------------------------------------

    def _register_console_commands(self) -> None:
        """Register all developer console commands."""

        # ---- helpers already defined in Phase 2/3 game.py ----
        # Re-registering here so they all exist in one place.

        def cmd_spawn(args):
            if len(args) < 3:
                self.console.log("Usage: spawn [type] [x] [y]", "#FFFF00")
                return
            entity_type = args[0].lower()
            if entity_type not in ('npc', 'enemy'):
                self.console.log(f"Unknown type '{entity_type}'.", "#FF0000")
                return
            try:
                x, y = int(args[1]), int(args[2])
            except ValueError:
                self.console.log("Coordinates must be integers.", "#FF0000")
                return
            if not self.current_world:
                self.console.log("No world loaded.", "#FF0000")
                return
            entity = self.api.spawn_entity(entity_type, x, y)
            if entity:
                self.console.log(
                    f"Spawned {entity_type} id={entity.id[:8]}", "#00FF00"
                )
            else:
                self.console.log("Spawn failed.", "#FF0000")

        def cmd_settile(args):
            if len(args) < 3:
                self.console.log(
                    f"Usage: settile [x] [y] [type]  Types: {', '.join(settings.DEFAULT_TILE_TYPES)}",
                    "#FFFF00"
                )
                return
            try:
                x, y = int(args[0]), int(args[1])
            except ValueError:
                self.console.log("Coordinates must be integers.", "#FF0000")
                return
            tile_type = args[2].lower()
            if tile_type not in settings.DEFAULT_TILE_TYPES:
                self.console.log(f"Unknown tile type '{tile_type}'.", "#FF0000")
                return
            if not self.current_world:
                self.console.log("No world loaded.", "#FF0000")
                return
            td = settings.DEFAULT_TILE_TYPES[tile_type]
            ok = self.current_world.tile_map.set_tile(
                x, y, Tile(tile_type, td['is_solid'], td['movement_modifier'], td['color'])
            )
            self.console.log(
                f"Set ({x},{y}) → {tile_type}." if ok else f"({x},{y}) out of bounds.",
                "#00FF00" if ok else "#FF0000"
            )

        def cmd_tp(args):
            if len(args) < 2:
                self.console.log("Usage: tp [x] [y]", "#FFFF00")
                return
            try:
                x, y = int(args[0]), int(args[1])
            except ValueError:
                self.console.log("Coordinates must be integers.", "#FF0000")
                return
            if not self.player or not self.current_world:
                self.console.log("No player loaded.", "#FF0000")
                return
            wx, wy = self.current_world.tile_map.grid_to_world(x, y)
            self.player.position[0] = wx
            self.player.position[1] = wy
            self._update_camera_immediate()
            self.console.log(f"Teleported to ({x},{y}).", "#00FF00")

        def cmd_listentities(args):
            if not self.current_world:
                self.console.log("No world loaded.", "#FF0000")
                return
            if not self.current_world.entities:
                self.console.log("No entities.", "#FFFF00")
                return
            self.console.log(
                f"Entities ({len(self.current_world.entities)}):", "#00FF00"
            )
            for e in self.current_world.entities:
                gx, gy = self.current_world.tile_map.world_to_grid(
                    e.position[0], e.position[1]
                )
                self.console.log(
                    f"  [{e.__class__.__name__}] {e.name} id={e.id[:8]} pos=({gx},{gy})",
                    "#FFFFFF"
                )

        def cmd_reload(args):
            if not args:
                self.console.log("Usage: reload [entity_id]", "#FFFF00")
                return
            prefix = args[0].lower()
            if not self.current_world:
                self.console.log("No world loaded.", "#FF0000")
                return
            matched = next(
                (e for e in self.current_world.entities
                 if e.id.lower().startswith(prefix)),
                None
            )
            if not matched:
                self.console.log(f"No entity id starts with '{prefix}'.", "#FF0000")
                return
            if not getattr(matched, 'behavior_script', None):
                self.console.log(f"'{matched.name}' has no script.", "#FFFF00")
                return
            self._reload_entity_script(matched)
            self.console.log(f"Reloaded '{matched.name}'.", "#00FF00")

        def cmd_save(args):
            self._save_world()

        def cmd_clear(args):
            self.console.clear_log()

        def cmd_listworlds(args):
            worlds = self.world_manager.list_worlds()
            if not worlds:
                self.console.log("No worlds.", "#FFFF00")
                return
            self.console.log(f"Worlds ({len(worlds)}):", "#00FF00")
            for w in worlds:
                import time as _t
                lp = _t.strftime("%Y-%m-%d", _t.localtime(w.get('last_played', 0)))
                self.console.log(f"  - {w['name']}  last:{lp}", "#FFFFFF")

        def cmd_listcmds(args):
            rows = [
                ("spawn [type] [x] [y]",       "Spawn entity at tile coords"),
                ("settile [x] [y] [type]",      "Set tile at coords"),
                ("tp [x] [y]",                  "Teleport player"),
                ("listentities",                "List all entities"),
                ("reload [entity_id]",          "Reload entity script"),
                ("save",                        "Force save world"),
                ("clear",                       "Clear console"),
                ("listworlds",                  "List worlds"),
                ("listcmds",                    "List commands"),
                ("listitems",                   "List inventory"),
                ("giveitem [id] [qty]",         "Give item to player"),
                ("settilecode [x] [y]",         "Edit tile behavior script"),
                ("setworldbg [path]",           "Set world background"),
                ("setplayersprite [path]",      "Set player sprite"),
                ("opentilemanager",             "Open tile type manager"),
                ("openitemmanager",             "Open item type manager"),
                ("opencustomize",               "Open player customize panel"),
                ("opensettings",                "Open settings menu"),
                ("help [command]",              "Help for command"),
            ]
            self.console.log("Commands:", "#00FF00")
            for name, desc in rows:
                self.console.log(f"  {name:<36} {desc}", "#FFFFFF")
            self.tutorial.notify_task_complete("run_listcmds")

        def cmd_listitems(args):
            if not self.player:
                self.console.log("No player.", "#FF0000")
                return
            self.console.log("Inventory:", "#00FF00")
            has = False
            for i, item in enumerate(self.player.inventory.slots):
                if item:
                    has = True
                    self.console.log(
                        f"  [{i}] {item.name} x{item.quantity} ({item.item_id})",
                        "#FFFFFF"
                    )
            if not has:
                self.console.log("  Empty.", "#FFFF00")

        def cmd_giveitem(args):
            if not args:
                self.console.log("Usage: giveitem [item_id] [quantity]", "#FFFF00")
                return
            item_id = args[0]
            qty = 1
            if len(args) >= 2:
                try:
                    qty = max(1, int(args[1]))
                except ValueError:
                    self.console.log("Quantity must be integer.", "#FF0000")
                    return
            if not self.player:
                self.console.log("No player.", "#FF0000")
                return
            if not item_registry.get_item_type(item_id):
                self.console.log(f"Unknown item '{item_id}'.", "#FF0000")
                return
            ok = self.api.give_item(self.player, item_id, qty)
            name = item_registry.get_item_type(item_id)['name']
            self.console.log(
                f"Gave {qty}x {name}." if ok else "Inventory full.",
                "#00FF00" if ok else "#FF0000"
            )

        def cmd_settilecode(args):
            if len(args) < 2:
                self.console.log("Usage: settilecode [x] [y]", "#FFFF00")
                return
            try:
                x, y = int(args[0]), int(args[1])
            except ValueError:
                self.console.log("Coordinates must be integers.", "#FF0000")
                return
            if not self.current_world:
                self.console.log("No world loaded.", "#FF0000")
                return
            tile = self.current_world.tile_map.get_tile(x, y)
            if not tile:
                self.console.log(f"No tile at ({x},{y}).", "#FF0000")
                return
            world_dir = os.path.join(
                "worlds",
                self.world_manager._sanitize_filename(self.current_world.name)
            )
            script_path = os.path.join(
                world_dir, "behaviors", "tiles", f"tile_{x}_{y}.py"
            )
            template = self.code_editor.get_template(
                "tile", f"{tile.tile_type}_{x}_{y}"
            )
            self.code_editor.open(script_path, template)
            tile.behavior_script = script_path
            self.console.log(f"Opened tile editor ({x},{y}).", "#00FF00")
            self.tutorial.notify_task_complete("open_code_editor")

        def cmd_setworldbg(args):
            if not args:
                self.console.log("Usage: setworldbg [image_path]", "#FFFF00")
                return
            path = " ".join(args)
            if not os.path.exists(path):
                self.console.log(f"File not found: {path}", "#FF0000")
                return
            if not path.lower().endswith(('.png', '.jpg', '.jpeg')):
                self.console.log("Use PNG or JPG.", "#FF0000")
                return
            if self.current_world:
                self.current_world.metadata['background_image'] = path
                self._load_background(path)
                self.console.log(f"Background set.", "#00FF00")
            else:
                self.console.log("No world loaded.", "#FF0000")

        def cmd_setplayersprite(args):
            if not args:
                self.console.log("Usage: setplayersprite [image_path]", "#FFFF00")
                return
            path = " ".join(args)
            if not os.path.exists(path):
                self.console.log(f"File not found: {path}", "#FF0000")
                return
            if not path.lower().endswith(('.png', '.jpg', '.jpeg')):
                self.console.log("Use PNG or JPG.", "#FF0000")
                return
            if self.player:
                self.player.sprite_path = path
                try:
                    self.player.sprite_surface = pygame.image.load(path).convert_alpha()
                    self.console.log("Player sprite set.", "#00FF00")
                except Exception as e:
                    self.console.log(f"Sprite error: {e}", "#FF0000")
            else:
                self.console.log("No player.", "#FF0000")

        # --- Phase 5 new console commands ---

        def cmd_opentilemanager(args):
            """Open tile type manager panel from console."""
            self.tile_type_manager.show()
            self.console.log("Tile type manager opened.", "#00FF00")

        def cmd_openitemmanager(args):
            """Open item type manager panel from console."""
            self.item_type_manager.show()
            self.console.log("Item type manager opened.", "#00FF00")

        def cmd_opencustomize(args):
            """Open player customization panel from console."""
            self._open_player_customize()
            self.console.log("Player customization opened.", "#00FF00")

        def cmd_opensettings(args):
            """Open settings menu from console."""
            self._open_settings()
            self.console.log("Settings opened.", "#00FF00")

        def cmd_help(args):
            if not args:
                cmd_listcmds([])
                return
            name = args[0].lower()
            help_map = {
                'spawn':            "spawn [type] [x] [y]\nTypes: npc, enemy",
                'settile':          f"settile [x] [y] [type]\nTypes: {', '.join(settings.DEFAULT_TILE_TYPES)}",
                'tp':               "tp [x] [y]  — teleport player to tile coords",
                'listentities':     "listentities — list all entities",
                'reload':           "reload [entity_id] — reload behavior script",
                'save':             "save — force save world",
                'clear':            "clear — clear console log",
                'listworlds':       "listworlds — list saved worlds",
                'listcmds':         "listcmds — list all commands",
                'listitems':        "listitems — list inventory",
                'giveitem':         "giveitem [id] [qty] — add item",
                'settilecode':      "settilecode [x] [y] — open tile script editor",
                'setworldbg':       "setworldbg [path] — set background image",
                'setplayersprite':  "setplayersprite [path] — set player sprite",
                'opentilemanager':  "opentilemanager — open tile type manager",
                'openitemmanager':  "openitemmanager — open item type manager",
                'opencustomize':    "opencustomize — open player customization",
                'opensettings':     "opensettings — open settings menu",
                'help':             "help [command] — show help",
            }
            if name in help_map:
                for line in help_map[name].split('\n'):
                    self.console.log(line, "#00FF00")
            else:
                self.console.log(f"No help for '{name}'.", "#FF0000")

        # Register everything
        cmds = {
            'spawn':           cmd_spawn,
            'settile':         cmd_settile,
            'tp':              cmd_tp,
            'listentities':    cmd_listentities,
            'reload':          cmd_reload,
            'save':            cmd_save,
            'clear':           cmd_clear,
            'listworlds':      cmd_listworlds,
            'listcmds':        cmd_listcmds,
            'listitems':       cmd_listitems,
            'giveitem':        cmd_giveitem,
            'settilecode':     cmd_settilecode,
            'setworldbg':      cmd_setworldbg,
            'setplayersprite': cmd_setplayersprite,
            'opentilemanager': cmd_opentilemanager,
            'openitemmanager': cmd_openitemmanager,
            'opencustomize':   cmd_opencustomize,
            'opensettings':    cmd_opensettings,
            'help':            cmd_help,
        }
        for name, fn in cmds.items():
            self.console.register_command(name, fn)
