# =============================================================================
# File: sandbox_game/core/game.py
# =============================================================================
"""
Main game loop — all systems wired, all issues fixed.
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

        # NPC panel state
        self._npc_panel: Optional[pygame_gui.elements.UIWindow] = None
        self._npc_panel_target: Optional[NPC] = None
        self._npc_name_entry = None
        self._npc_dialogue_entry = None
        self._npc_apply_btn = None
        self._npc_edit_script_btn = None

        # Expansion popup reference
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

        # Track which overlay panel is currently open so we can
        # close it automatically when another one is opened.
        self._active_overlay: Optional[str] = None

        self._wire_callbacks()
        self._register_console_commands()
        self._subscribe_fab_events()

        try:
            self.dialogue_font = pygame.font.Font(None, 28)
        except Exception:
            self.dialogue_font = None

    # ------------------------------------------------------------------
    # Overlay / panel exclusivity
    # ------------------------------------------------------------------

    # Map of overlay name → (show callable, hide callable, active property getter)
    # We build this lazily in _get_overlay_map so all objects are initialised first.
    def _get_overlay_map(self) -> dict:
        """
        Return a mapping of overlay_name → (show_fn, hide_fn, is_active_fn).
        Used by _open_exclusive_overlay to enforce single-panel-at-a-time behaviour.
        """
        return {
            'settings':        (self.settings_menu.show,
                                self.settings_menu.hide,
                                lambda: self.settings_menu.active),

            'help':            (self.help_panel.toggle,
                                self.help_panel.toggle,
                                lambda: self.help_panel.active),

            'file_editor':     (self.file_editor.toggle,
                                self.file_editor.toggle,
                                lambda: self.file_editor.active),

            # in _get_overlay_map(), replace the 'inventory' entry:

            'inventory': (lambda: self.inventory_editor.open(self.player.inventory)
                          if self.player else None,
                          self.inventory_editor.close,          # was .hide  ← the crash
                          lambda: self.inventory_editor.active,),

            'player_customize': (lambda: self.player_customize.show(self.player)
                                 if self.player else None,
                                 self.player_customize.hide,
                                 lambda: self.player_customize.active),

            'tile_type_manager': (self.tile_type_manager.show,
                                  self.tile_type_manager.hide,
                                  lambda: self.tile_type_manager.active),

            'item_type_manager': (self.item_type_manager.show,
                                  self.item_type_manager.hide,
                                  lambda: self.item_type_manager.active),

            'sprite_editor':   (lambda: self.sprite_editor.show(
                                    target=self.player, category='sprites'),
                                self.sprite_editor.hide,
                                lambda: self.sprite_editor.active),

            'code_editor':     (None,          # opened with specific args
                                self.code_editor.close,
                                lambda: self.code_editor.active),

            'tutorial':        (lambda: self._start_tutorial(),
                                lambda: None,
                                lambda: self.tutorial.active),

            'game_menu':       (self.game_menu.toggle,
                                self.game_menu.toggle,
                                lambda: self.game_menu.active),
        }

    def _close_active_overlay(self) -> None:
        """
        Close whatever overlay is currently open.
        Calls the registered hide callable for self._active_overlay.
        """
        if self._active_overlay is None:
            return

        overlay_map = self._get_overlay_map()
        entry = overlay_map.get(self._active_overlay)
        if entry is None:
            self._active_overlay = None
            return

        _show_fn, hide_fn, is_active_fn = entry

        # Only call hide if the panel reports itself as active.
        try:
            if is_active_fn():
                hide_fn()
        except Exception as e:
            print(f"[overlay] Could not close '{self._active_overlay}': {e}")

        self._active_overlay = None

    def _open_exclusive_overlay(self, name: str, show_fn=None) -> None:
        """
        Close any currently open overlay then open the requested one.

        Args:
            name:    Key in the overlay map (e.g. 'settings', 'help').
            show_fn: Optional override callable to open the panel.
                     If None the registered show callable is used.
        """
        # If the same overlay is already open, just close it (toggle behaviour).
        if self._active_overlay == name:
            self._close_active_overlay()
            return

        # Close whatever was open before.
        self._close_active_overlay()

        # Open the new overlay.
        overlay_map = self._get_overlay_map()
        entry = overlay_map.get(name)

        opener = show_fn
        if opener is None and entry is not None:
            opener = entry[0]   # registered show callable

        if opener is not None:
            try:
                opener()
            except Exception as e:
                print(f"[overlay] Could not open '{name}': {e}")

        self._active_overlay = name

    # ------------------------------------------------------------------
    # Sprite editor helpers (public API for external callers)
    # ------------------------------------------------------------------

    def open_sprite_editor(
        self,
        target=None,
        category: str = 'sprites',
        world_name: str = ""
    ) -> None:
        """
        Open the sprite editor for *target* exclusively
        (closes any other open overlay first).

        Args:
            target:     Object that will receive the assigned sprite
                        (e.g. player, an entity, or None).
            category:   Asset sub-folder category ('sprites', 'tiles', etc.).
            world_name: Optional world name used when saving assets.
                        Defaults to the current world name when omitted.
        """
        resolved_world = world_name or (
            self.current_world.name if self.current_world else ""
        )

        def _open():
            self.sprite_editor.show(target=target, category=category)
            # Store world name so handle_event passes it automatically.
            self.sprite_editor._current_world_name = resolved_world

        self._open_exclusive_overlay('sprite_editor', show_fn=_open)

    # ------------------------------------------------------------------
    # Wiring
    # ------------------------------------------------------------------

    def _wire_callbacks(self) -> None:
        self.code_editor.on_save = self._on_script_saved
        self.game_menu.on_save = self._save_world
        self.game_menu.on_exit_to_menu = self._exit_to_main_menu

        # Route every game-menu action through the exclusive-overlay system.
        self.game_menu.on_settings       = lambda: self._open_exclusive_overlay('settings')
        self.game_menu.on_help           = lambda: self._open_exclusive_overlay('help')
        self.game_menu.on_file_editor    = lambda: self._open_exclusive_overlay('file_editor')
        self.game_menu.on_tutorial       = lambda: self._open_exclusive_overlay('tutorial')
        self.game_menu.on_customize_player = lambda: self._open_exclusive_overlay('player_customize')

        self.settings_menu.on_apply = self._on_settings_applied
        self.tutorial.on_exit = lambda: None

        self.player_customize.on_open_sprite_editor = (
            lambda p: self.open_sprite_editor(target=p, category='sprites')
        )

    def _subscribe_fab_events(self) -> None:
        event_bus.subscribe('fab_save',
                            lambda _: self._save_world())
        event_bus.subscribe('fab_help',
                            lambda _: self._open_exclusive_overlay('help'))
        event_bus.subscribe('fab_settings',
                            lambda _: self._open_exclusive_overlay('settings'))
        event_bus.subscribe('fab_file_editor',
                            lambda _: self._open_exclusive_overlay('file_editor'))
        event_bus.subscribe('fab_exit_menu',
                            lambda _: self._exit_to_main_menu())

    # ------------------------------------------------------------------
    # World loading
    # ------------------------------------------------------------------

    def load_world(self, world: World) -> None:
        self.current_world = world
        self.world_manager.current_world = world

        world_dir = os.path.join(
            "worlds", self.world_manager._sanitize_filename(world.name)
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

        cx = world.tile_map.width  * world.tile_map.tile_size / 2 - settings.PLAYER_SIZE / 2
        cy = world.tile_map.height * world.tile_map.tile_size / 2 - settings.PLAYER_SIZE / 2
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
                surf, (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
            )
        except Exception as e:
            print(f"Background error: {e}")
            self._background_surface = None

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def run(self) -> None:
        while self.running:
            self.dt = self.clock.tick(
                settings.GLOBAL_SETTINGS.get('target_fps', settings.FPS)
            ) / 1000.0
            events = pygame.event.get()

            for event in events:
                if event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode(
                        (event.w, event.h), pygame.RESIZABLE
                    )

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
        for event in events:
            self.ui_manager.process_events(event)

            if event.type == pygame.QUIT:
                self._save_world()
                self.running = False
                continue

            if event.type == pygame.VIDEORESIZE:
                continue

            # Expansion popup — highest priority after quit/resize.
            if self._expansion_popup is not None:
                consumed = self._expansion_popup.handle_event(event)
                if self._expansion_popup is not None and not self._expansion_popup.active:
                    self._expansion_popup = None
                if consumed:
                    continue

            # Priority overlays (only the first active one consumes the event)
            priority_systems = [
                self.settings_menu,
                self.player_customize,
                self.tile_type_manager,
                self.item_type_manager,
                self.file_editor,
                self.code_editor,
            ]
            consumed_by_priority = False
            for system in priority_systems:
                if system.active:
                    if system.handle_event(event):
                        consumed_by_priority = True
                        break
            if consumed_by_priority:
                continue

            if self.sprite_editor.active:
                # Pass stored world name so SpriteEditor can save assets correctly.
                wn = getattr(self.sprite_editor, '_current_world_name', None)
                if wn is None:
                    wn = self.current_world.name if self.current_world else ""
                if self.sprite_editor.handle_event(event, wn):
                    continue

            if self.help_panel.active:
                if self.help_panel.handle_event(event):
                    continue

            if self.tutorial.active:
                if self.tutorial.handle_event(event):
                    continue

            if self.inventory_editor.active:
                if self.inventory_editor.handle_event(event):
                    continue

            if self.game_menu.active:
                if self.game_menu.handle_event(event):
                    continue

            if self._npc_panel is not None:
                if self._handle_npc_panel_event(event):
                    continue

            # Console toggle key
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

            # Right-click NPC
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                self._try_open_npc_panel(event.pos)

            if self.tile_editor.active and not self.console.active:
                self.tile_editor.handle_event(event)

            if self.entity_editor.active and not self.console.active:
                self.entity_editor.handle_event(event)

        self.input_handler.update(events)

    def _handle_keydown(self, event: pygame.event.Event) -> None:
        """Route keyboard shortcuts."""
        if self.game_menu.active or self.console.active or self.code_editor.active:
            return

        kb = settings.KEYBINDINGS

        if event.key == kb.get('menu', pygame.K_ESCAPE):
            # Pressing Escape closes any open overlay first; if none, toggles menu.
            if self._active_overlay and self._active_overlay != 'game_menu':
                self._close_active_overlay()
            else:
                self._open_exclusive_overlay('game_menu')
            return

        if event.key == kb.get('inventory', pygame.K_TAB):
            if self.player and settings.GAME_RULES.get('inventory_system', True):
                self._open_exclusive_overlay('inventory')
            return

        if event.key == kb.get('help', pygame.K_h):
            self._open_exclusive_overlay('help')
            return

        if event.key == kb.get('build_mode', pygame.K_b):
            if settings.GAME_RULES.get('build_mode', True):
                self._toggle_build_mode()
            return

        if event.key == kb.get('interact', pygame.K_f):
            self._interact_with_nearby_entity()
            return

        if event.key == kb.get('entity_editor', pygame.K_e):
            if (self.game_mode == "build" and
                    settings.GAME_RULES.get('entity_spawning', True)):
                self._toggle_entity_editor()
            return

        # Sub-mode keys — active in build mode regardless of entity editor
        if self.game_mode == "build":
            sub_map = {
                kb.get('sub_place',   pygame.K_1): "Place",
                kb.get('sub_delete',  pygame.K_2): "Delete",
                kb.get('sub_inspect', pygame.K_3): "Inspect",
                kb.get('sub_select',  pygame.K_4): "Select",
            }
            new_mode = sub_map.get(event.key)
            if new_mode is not None:
                self.tile_editor.set_sub_mode(new_mode)
                self.entity_editor.deactivate()
                self.tile_editor.activate()
                return

    # ------------------------------------------------------------------
    # NPC right-click panel
    # ------------------------------------------------------------------

    def _try_open_npc_panel(self, screen_pos: Tuple[int, int]) -> None:
        if not self.current_world:
            return
        wx = screen_pos[0] + self.camera_offset[0]
        wy = screen_pos[1] + self.camera_offset[1]

        for entity in self.current_world.entities:
            if not isinstance(entity, NPC):
                continue
            ex, ey = entity.position[0], entity.position[1]
            ew, eh = entity.size[0], entity.size[1]
            if ex <= wx <= ex + ew and ey <= wy <= ey + eh:
                self._open_npc_panel(entity)
                return

    def _open_npc_panel(self, npc: NPC) -> None:
        if self._npc_panel is not None:
            try:
                self._npc_panel.kill()
            except Exception:
                pass

        self._npc_panel_target = npc
        sw, sh = settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT
        pw, ph = 370, 220
        px = (sw - pw) // 2
        py = (sh - ph) // 2

        self._npc_panel = pygame_gui.elements.UIWindow(
            rect=pygame.Rect(px, py, pw, ph),
            manager=self.ui_manager,
            window_display_title=f"NPC Properties: {npc.name}"
        )

        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 10, pw - 30, 22),
            text="Name:",
            manager=self.ui_manager,
            container=self._npc_panel
        )
        self._npc_name_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(10, 36, pw - 30, 32),
            manager=self.ui_manager,
            container=self._npc_panel
        )
        self._npc_name_entry.set_text(npc.name)

        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 76, pw - 30, 22),
            text="Dialogue:",
            manager=self.ui_manager,
            container=self._npc_panel
        )
        self._npc_dialogue_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(10, 102, pw - 30, 32),
            manager=self.ui_manager,
            container=self._npc_panel
        )
        self._npc_dialogue_entry.set_text(
            npc.dialogue[0] if npc.dialogue else ""
        )

        self._npc_apply_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, 146, 120, 34),
            text="Apply",
            manager=self.ui_manager,
            container=self._npc_panel
        )
        self._npc_edit_script_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(140, 146, 160, 34),
            text="Edit Behavior",
            manager=self.ui_manager,
            container=self._npc_panel
        )

    def _handle_npc_panel_event(self, event: pygame.event.Event) -> bool:
        if self._npc_panel is None:
            return False

        if event.type == pygame_gui.UI_WINDOW_CLOSE:
            if event.ui_element == self._npc_panel:
                self._npc_panel = None
                self._npc_panel_target = None
                return True

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self._npc_apply_btn:
                if self._npc_panel_target:
                    name = self._npc_name_entry.get_text().strip()
                    if name:
                        self._npc_panel_target.name = name
                    dlg = self._npc_dialogue_entry.get_text().strip()
                    if dlg:
                        self._npc_panel_target.dialogue = [dlg]
                return True

            if event.ui_element == self._npc_edit_script_btn:
                if self._npc_panel_target and self.current_world:
                    npc = self._npc_panel_target
                    world_dir = os.path.join(
                        "worlds",
                        self.world_manager._sanitize_filename(
                            self.current_world.name
                        )
                    )
                    script_path = os.path.join(
                        world_dir, "behaviors", "entities", f"{npc.id[:8]}.py"
                    )
                    # Opening code editor closes any other overlay first.
                    self._close_active_overlay()
                    self.code_editor.open(
                        script_path,
                        self.code_editor.get_template("entity", npc.name)
                    )
                    self._active_overlay = 'code_editor'
                    npc.behavior_script = script_path
                return True

        return False

    # ------------------------------------------------------------------
    # World expansion
    # ------------------------------------------------------------------

    def _handle_world_expansion(self, direction: str) -> None:
        if not self.current_world:
            return

        if self._expansion_popup is not None and self._expansion_popup.active:
            return

        def confirm_expand():
            tm = self.current_world.tile_map
            ok = tm.expand(direction, amount=10)
            if ok:
                shift = 10 * settings.TILE_SIZE
                if direction == 'north':
                    self.player.position[1] += shift
                    self.camera_offset[1]   += shift
                elif direction == 'west':
                    self.player.position[0] += shift
                    self.camera_offset[0]   += shift
                self.console.log(
                    f"Expanded {direction}. Size: "
                    f"{tm.width}x{tm.height}", "#00FF00"
                )
            else:
                self.console.log("Expansion failed.", "#FF0000")
            self._expansion_popup = None

        def cancel_expand():
            self._expansion_popup = None

        self._expansion_popup = Popup(
            self.ui_manager,
            "Expand World?",
            f"Expand world {direction} by 10 tiles?",
            on_confirm=confirm_expand,
            on_cancel=cancel_expand,
            confirm_text="Expand"
        )

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def _update(self, dt: float) -> None:
        self.ui_manager.update(dt)

        if self.sprite_editor.active:
            self.sprite_editor.update(dt)
        if self.tutorial.active:
            self.tutorial.update(dt)

        if (self.game_menu.active or self.code_editor.active or
                self.inventory_editor.active or self.settings_menu.active):
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
        if not self.player:
            return
        tx = self.player.position[0] + self.player.size[0]/2 - settings.SCREEN_WIDTH/2
        ty = self.player.position[1] + self.player.size[1]/2 - settings.SCREEN_HEIGHT/2
        t = min(1.0, settings.CAMERA_LERP_SPEED * dt)
        self.camera_offset[0] += (tx - self.camera_offset[0]) * t
        self.camera_offset[1] += (ty - self.camera_offset[1]) * t

    def _update_camera_immediate(self) -> None:
        if not self.player:
            return
        self.camera_offset[0] = (
            self.player.position[0] + self.player.size[0]/2 - settings.SCREEN_WIDTH/2
        )
        self.camera_offset[1] = (
            self.player.position[1] + self.player.size[1]/2 - settings.SCREEN_HEIGHT/2
        )

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def _get_mouse_grid(self) -> Optional[Tuple[int, int]]:
        if not self.current_world:
            return None
        mx, my = pygame.mouse.get_pos()
        wx = mx + self.camera_offset[0]
        wy = my + self.camera_offset[1]
        return self.current_world.tile_map.world_to_grid(wx, wy)

    def _render(self) -> None:
        if self._background_surface:
            self.screen.blit(self._background_surface, (0, 0))
        else:
            self.renderer.clear()

        if self.current_world and self.player:
            mouse_grid = (
                self._get_mouse_grid() if self.tile_editor.active else None
            )

            self.renderer.render_tile_map(
                self.current_world.tile_map,
                tuple(self.camera_offset),
                selected_tile_type=self.tile_editor.selected_tile_type,
                sub_mode=self.tile_editor.sub_mode if self.tile_editor.active else "",
                mouse_grid=mouse_grid,
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

        if self.mobile_controls.enabled:
            self.mobile_controls.render(self.screen)

        self.ui_manager.draw_ui(self.screen)
        self.renderer.present()

    def _render_entity_labels(self) -> None:
        if not self.current_world:
            return
        try:
            font = pygame.font.Font(None, 20)
        except Exception:
            return
        for entity in self.current_world.entities:
            sx = entity.position[0] - self.camera_offset[0]
            sy = entity.position[1] - self.camera_offset[1] - 18
            if (-60 <= sx <= settings.SCREEN_WIDTH + 60 and
                    -60 <= sy <= settings.SCREEN_HEIGHT + 60):
                lbl = font.render(entity.name, True, settings.COLORS['white'])
                self.screen.blit(lbl, (int(sx), int(sy)))

    def _render_dialogue(self, text: str) -> None:
        if not self.dialogue_font:
            return
        bw = int(settings.SCREEN_WIDTH * 0.6)
        bh = 70
        bx = (settings.SCREEN_WIDTH - bw) // 2
        by = settings.SCREEN_HEIGHT - bh - 20
        s = pygame.Surface((bw, bh))
        s.set_alpha(220)
        s.fill((20, 20, 40))
        self.screen.blit(s, (bx, by))
        pygame.draw.rect(self.screen, settings.COLORS['white'],
                         pygame.Rect(bx, by, bw, bh), 2)
        t = self.dialogue_font.render(text, True, settings.COLORS['white'])
        self.screen.blit(t, (bx + 15, by + (bh - t.get_height()) // 2))

    # ------------------------------------------------------------------
    # HUD
    # ------------------------------------------------------------------

    def _update_hud(self) -> None:
        if not self.current_world or not self.player:
            return
        gx, gy = self.current_world.tile_map.world_to_grid(
            self.player.position[0] + self.player.size[0] / 2,
            self.player.position[1] + self.player.size[1] / 2
        )
        sub = ""
        if self.game_mode == "build":
            sub = (f"Entity({self.entity_editor.selected_entity_type})"
                   if self.entity_editor.active
                   else self.tile_editor.sub_mode)

        self.hud.update(
            mode="Build" if self.game_mode == "build" else "Play",
            sub_mode=sub,
            selected_tile=self.tile_editor.selected_tile_type,
            world_name=self.current_world.name,
            player_pos=(gx, gy),
            player_health=getattr(self.player, 'health', 100),
            player_max_health=getattr(self.player, 'max_health', 100),
        )

    # ------------------------------------------------------------------
    # Build mode
    # ------------------------------------------------------------------

    def _toggle_build_mode(self) -> None:
        if self.game_mode == "play":
            self.game_mode = "build"
            self.tile_editor.activate()
            self.console.log(
                "Build mode ON  —  1:Place  2:Delete  3:Inspect  4:Select  E:Entities",
                "#FFFF00"
            )
        else:
            self.game_mode = "play"
            self.tile_editor.deactivate()
            self.entity_editor.deactivate()
            self.console.log("Build mode OFF", "#FFFF00")

    def _toggle_entity_editor(self) -> None:
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
        if not self.current_world or not self.player:
            return
        interact_range = settings.TILE_SIZE * 1.5
        closest, closest_dist = None, float('inf')

        for entity in self.current_world.entities:
            if isinstance(entity, NPC):
                dx = entity.position[0] - self.player.position[0]
                dy = entity.position[1] - self.player.position[1]
                dist = (dx*dx + dy*dy)**0.5
                if dist < interact_range and dist < closest_dist:
                    closest_dist = dist
                    closest = entity

        if closest:
            dialogue = closest.on_interact(self.player)
            if dialogue:
                self.show_dialogue(dialogue)

    def show_dialogue(self, text: str) -> None:
        self.dialogue_text = text
        self.dialogue_timer = self.dialogue_duration

    # ------------------------------------------------------------------
    # Tutorial
    # ------------------------------------------------------------------

    def _start_tutorial(self) -> None:
        step = self.tutorial.load_progress()
        self.tutorial.start(self, from_step=step)

    # ------------------------------------------------------------------
    # Settings
    # ------------------------------------------------------------------

    def _open_settings(self) -> None:
        self._open_exclusive_overlay('settings')

    def _on_settings_applied(self, kb, rules, glb) -> None:
        if glb.get('mobile_controls'):
            self.mobile_controls.keybindings = kb
            self.mobile_controls.set_dpad_size(glb.get('dpad_size', 80))
            self.mobile_controls.set_action_btn_size(glb.get('action_btn_size', 64))
            self.mobile_controls.enable()
        else:
            self.mobile_controls.disable()

        flags = pygame.RESIZABLE
        if glb.get('fullscreen'):
            flags = pygame.FULLSCREEN
        pygame.display.set_mode(
            (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), flags
        )

    def _open_player_customize(self) -> None:
        if self.player:
            self._open_exclusive_overlay('player_customize')

    # ------------------------------------------------------------------
    # Hot reload
    # ------------------------------------------------------------------

    def _on_behavior_file_changed(self, filepath: str) -> None:
        if not self.current_world:
            return
        for entity in self.current_world.entities:
            if getattr(entity, 'behavior_script', None):
                if (os.path.normpath(entity.behavior_script) ==
                        os.path.normpath(filepath)):
                    self._reload_entity_script(entity)
                    self.console.log(f"Hot reloaded: {entity.name}", "#00FFFF")

    def _reload_entity_script(self, entity) -> None:
        if not entity.behavior_script:
            return
        ok, module, error = self.hot_reload_manager.reload_script(
            entity.behavior_script, self.sandbox.get_safe_globals()
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
        if not self.current_world:
            return
        for entity in self.current_world.entities:
            if getattr(entity, 'behavior_script', None):
                ok, module, error = self.hot_reload_manager.load_script(
                    entity.behavior_script, self.sandbox.get_safe_globals()
                )
                if ok:
                    entity.behavior_module = module
                else:
                    print(f"Script load error {entity.name}: {error}")

    def _on_script_saved(self, filepath: str) -> None:
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
        self.console.log(
            f"{'Hot reloaded' if reloaded else 'Saved'}: "
            f"{os.path.basename(filepath)}",
            "#00FFFF" if reloaded else "#00FF00"
        )

    # ------------------------------------------------------------------
    # Save / exit
    # ------------------------------------------------------------------

    def _save_world(self) -> None:
        if self.current_world:
            ok = self.world_manager.save_world(self.current_world)
            self.console.log(
                "World saved." if ok else "Save failed.",
                "#00FF00" if ok else "#FF0000"
            )

    def _exit_to_main_menu(self) -> None:
        self._save_world()
        self.running = False

    # ------------------------------------------------------------------
    # Console commands
    # ------------------------------------------------------------------

    def _register_console_commands(self) -> None:

        def cmd_spawn(args):
            if len(args) < 3:
                self.console.log("Usage: spawn [type] [x] [y]", "#FFFF00")
                return
            etype = args[0].lower()
            if etype not in ('npc', 'enemy'):
                self.console.log(f"Unknown type '{etype}'.", "#FF0000")
                return
            try:
                x, y = int(args[1]), int(args[2])
            except ValueError:
                self.console.log("Coordinates must be integers.", "#FF0000")
                return
            if not self.current_world:
                self.console.log("No world loaded.", "#FF0000")
                return
            entity = self.api.spawn_entity(etype, x, y)
            if entity:
                self.console.log(f"Spawned {etype} id={entity.id[:8]}", "#00FF00")
            else:
                self.console.log("Spawn failed.", "#FF0000")

        def cmd_settile(args):
            if len(args) < 3:
                self.console.log(
                    f"Usage: settile [x] [y] [type]  Types: "
                    f"{', '.join(settings.DEFAULT_TILE_TYPES)}", "#FFFF00"
                )
                return
            try:
                x, y = int(args[0]), int(args[1])
            except ValueError:
                self.console.log("Coordinates must be integers.", "#FF0000")
                return
            ttype = args[2].lower()
            if ttype not in settings.DEFAULT_TILE_TYPES:
                self.console.log(f"Unknown type '{ttype}'.", "#FF0000")
                return
            if not self.current_world:
                self.console.log("No world loaded.", "#FF0000")
                return

            tm = self.current_world.tile_map
            if not tm.is_in_bounds(x, y):
                direction = tm.get_expansion_direction(x, y)
                if direction:
                    needed = max(10, abs(x) if direction in ('west',) else
                                 abs(y) if direction in ('north',) else
                                 x - tm.width + 1 if direction == 'east' else
                                 y - tm.height + 1)
                    tm.expand(direction, needed)
                    if direction == 'north':
                        self.player.position[1] += needed * settings.TILE_SIZE
                        self.camera_offset[1]   += needed * settings.TILE_SIZE
                    elif direction == 'west':
                        self.player.position[0] += needed * settings.TILE_SIZE
                        self.camera_offset[0]   += needed * settings.TILE_SIZE
                    self.console.log(f"Auto-expanded {direction}.", "#FFFF00")

            td = settings.DEFAULT_TILE_TYPES[ttype]
            ok = tm.set_tile(x, y, Tile(
                ttype, td['is_solid'], td['movement_modifier'], td['color']
            ))
            self.console.log(
                f"Set ({x},{y}) → {ttype}." if ok else "Still out of bounds.",
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
                self.console.log("No player.", "#FF0000")
                return
            wx, wy = self.current_world.tile_map.grid_to_world(x, y)
            self.player.position[0] = wx
            self.player.position[1] = wy
            self._update_camera_immediate()
            self.console.log(f"Teleported to ({x},{y}).", "#00FF00")

        def cmd_listentities(args):
            if not self.current_world:
                self.console.log("No world.", "#FF0000")
                return
            if not self.current_world.entities:
                self.console.log("No entities.", "#FFFF00")
                return
            for e in self.current_world.entities:
                gx, gy = self.current_world.tile_map.world_to_grid(
                    e.position[0], e.position[1]
                )
                self.console.log(
                    f"  [{e.__class__.__name__}] {e.name} "
                    f"id={e.id[:8]} pos=({gx},{gy})", "#FFFFFF"
                )

        def cmd_reload(args):
            if not args:
                self.console.log("Usage: reload [entity_id]", "#FFFF00")
                return
            if not self.current_world:
                self.console.log("No world.", "#FF0000")
                return
            m = next(
                (e for e in self.current_world.entities
                 if e.id.lower().startswith(args[0].lower())), None
            )
            if not m:
                self.console.log(f"No entity '{args[0]}'.", "#FF0000")
                return
            if not getattr(m, 'behavior_script', None):
                self.console.log(f"No script on '{m.name}'.", "#FFFF00")
                return
            self._reload_entity_script(m)
            self.console.log(f"Reloaded '{m.name}'.", "#00FF00")

        def cmd_save(args):
            self._save_world()

        def cmd_clear(args):
            self.console.clear_log()

        def cmd_listworlds(args):
            worlds = self.world_manager.list_worlds()
            if not worlds:
                self.console.log("No worlds.", "#FFFF00")
                return
            for w in worlds:
                import time as _t
                lp = _t.strftime("%Y-%m-%d", _t.localtime(w.get('last_played', 0)))
                self.console.log(f"  {w['name']}  last:{lp}", "#FFFFFF")

        def cmd_listcmds(args):
            rows = [
                ("spawn [type] [x] [y]",      "Spawn entity"),
                ("settile [x] [y] [type]",    "Set tile (auto-expands)"),
                ("tp [x] [y]",                "Teleport player"),
                ("listentities",              "List entities"),
                ("reload [id]",               "Reload entity script"),
                ("save",                      "Save world"),
                ("clear",                     "Clear console"),
                ("listworlds",                "List worlds"),
                ("listcmds",                  "List commands"),
                ("listitems",                 "List inventory"),
                ("giveitem [id] [qty]",       "Give item"),
                ("settilecode [x] [y]",       "Edit tile script"),
                ("setworldbg [path]",         "Set background"),
                ("setplayersprite [path]",    "Set player sprite"),
                ("opentilemanager",           "Tile type manager"),
                ("openitemmanager",           "Item type manager"),
                ("opencustomize",             "Player customize"),
                ("opensettings",              "Settings menu"),
                ("openspriteeditor",          "Open sprite editor"),
                ("help [command]",            "Help for command"),
            ]
            for name, desc in rows:
                self.console.log(f"  {name:<34} {desc}", "#FFFFFF")
            self.tutorial.notify_task_complete("run_listcmds")

        def cmd_listitems(args):
            if not self.player:
                self.console.log("No player.", "#FF0000")
                return
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
                self.console.log("Usage: giveitem [id] [qty]", "#FFFF00")
                return
            item_id = args[0]
            qty = int(args[1]) if len(args) > 1 else 1
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
                self.console.log("No world.", "#FF0000")
                return
            tile = self.current_world.tile_map.get_tile(x, y)
            if not tile:
                self.console.log(f"No tile at ({x},{y}).", "#FF0000")
                return
            world_dir = os.path.join(
                "worlds",
                self.world_manager._sanitize_filename(self.current_world.name)
            )
            sp = os.path.join(
                world_dir, "behaviors", "tiles", f"tile_{x}_{y}.py"
            )
            self._close_active_overlay()
            self.code_editor.open(
                sp, self.code_editor.get_template(
                    "tile", f"{tile.tile_type}_{x}_{y}"
                )
            )
            self._active_overlay = 'code_editor'
            tile.behavior_script = sp
            self.console.log(f"Opened tile editor ({x},{y}).", "#00FF00")
            self.tutorial.notify_task_complete("open_code_editor")

        def cmd_setworldbg(args):
            if not args:
                self.console.log("Usage: setworldbg [path]", "#FFFF00")
                return
            path = " ".join(args)
            if not os.path.exists(path):
                self.console.log(f"Not found: {path}", "#FF0000")
                return
            if self.current_world:
                self.current_world.metadata['background_image'] = path
                self._load_background(path)
                self.console.log("Background set.", "#00FF00")

        def cmd_setplayersprite(args):
            if not args:
                self.console.log("Usage: setplayersprite [path]", "#FFFF00")
                return
            path = " ".join(args)
            if not os.path.exists(path):
                self.console.log(f"Not found: {path}", "#FF0000")
                return
            if self.player:
                try:
                    self.player.sprite_surface = (
                        pygame.image.load(path).convert_alpha()
                    )
                    self.player.sprite_path = path
                    self.console.log("Sprite set.", "#00FF00")
                except Exception as e:
                    self.console.log(f"Error: {e}", "#FF0000")

        def cmd_opentilemanager(args):
            self._open_exclusive_overlay('tile_type_manager')
            self.console.log("Tile manager opened.", "#00FF00")

        def cmd_openitemmanager(args):
            self._open_exclusive_overlay('item_type_manager')
            self.console.log("Item manager opened.", "#00FF00")

        def cmd_opencustomize(args):
            self._open_player_customize()
            self.console.log("Player customize opened.", "#00FF00")

        def cmd_opensettings(args):
            self._open_exclusive_overlay('settings')
            self.console.log("Settings opened.", "#00FF00")

        def cmd_openspriteeditor(args):
            """Open the sprite editor for the player from the console."""
            self.open_sprite_editor(
                target=self.player,
                category='sprites'
            )
            self.console.log("Sprite editor opened.", "#00FF00")

        def cmd_help(args):
            if not args:
                cmd_listcmds([])
                return
            help_map = {
                'spawn':            "spawn [type] [x] [y]  Types: npc, enemy",
                'settile':          (
                    f"settile [x] [y] [type]  Auto-expands world. "
                    f"Types: {', '.join(settings.DEFAULT_TILE_TYPES)}"
                ),
                'tp':               "tp [x] [y]  Teleport player to tile coords",
                'listentities':     "List all entities with id and position",
                'reload':           "reload [id]  Force reload behavior script",
                'save':             "Force save world to disk",
                'clear':            "Clear console log",
                'listworlds':       "List all saved worlds",
                'listcmds':         "List all commands",
                'listitems':        "List player inventory",
                'giveitem':         "giveitem [id] [qty]  Add item to inventory",
                'settilecode':      "settilecode [x] [y]  Open tile script editor",
                'setworldbg':       "setworldbg [path]  Set world background PNG/JPG",
                'setplayersprite':  "setplayersprite [path]  Set player sprite",
                'opentilemanager':  "Open in-game tile type manager",
                'openitemmanager':  "Open in-game item type manager",
                'opencustomize':    "Open player customization panel",
                'opensettings':     "Open settings menu",
                'openspriteeditor': (
                    "Open the sprite editor for the player. "
                    "Closes any other open panel first."
                ),
                'help':             "help [command]  Show help for command",
            }
            name = args[0].lower()
            if name in help_map:
                self.console.log(help_map[name], "#00FF00")
            else:
                self.console.log(f"No help for '{name}'.", "#FF0000")

        cmds = {
            'spawn':            cmd_spawn,
            'settile':          cmd_settile,
            'tp':               cmd_tp,
            'listentities':     cmd_listentities,
            'reload':           cmd_reload,
            'save':             cmd_save,
            'clear':            cmd_clear,
            'listworlds':       cmd_listworlds,
            'listcmds':         cmd_listcmds,
            'listitems':        cmd_listitems,
            'giveitem':         cmd_giveitem,
            'settilecode':      cmd_settilecode,
            'setworldbg':       cmd_setworldbg,
            'setplayersprite':  cmd_setplayersprite,
            'opentilemanager':  cmd_opentilemanager,
            'openitemmanager':  cmd_openitemmanager,
            'opencustomize':    cmd_opencustomize,
            'opensettings':     cmd_opensettings,
            'openspriteeditor': cmd_openspriteeditor,
            'help':             cmd_help,
        }
        for name, fn in cmds.items():
            self.console.register_command(name, fn)
