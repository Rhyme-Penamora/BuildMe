# =============================================================================
# File: sandbox_game/ui/tutorial.py
# =============================================================================
"""
15-step hands-on tutorial mode running in an isolated world.
"""

import os
import json
import pygame
import pygame_gui
from typing import Optional, Callable, List, Dict
import settings


# ---------------------------------------------------------------------------
# Tutorial step definitions
# ---------------------------------------------------------------------------

TUTORIAL_STEPS: List[Dict] = [
    {
        "id": 1,
        "title": "Welcome to Build Me!",
        "instruction": (
            "Welcome! This game is a blank canvas — you are the designer.\n"
            "Everything here can be built, scripted, and customized by you.\n\n"
            "This tutorial will guide you through all the core features.\n"
            "Click 'Next' when you're ready to begin."
        ),
        "task": "click_next",
        "highlight": None,
    },
    {
        "id": 2,
        "title": "Movement",
        "instruction": (
            "Use W A S D to move the player.\n\n"
            "Task: Move your character to any different tile on the map."
        ),
        "task": "move",
        "highlight": "player",
    },
    {
        "id": 3,
        "title": "Build Mode",
        "instruction": (
            "Press B to enter Build Mode.\n\n"
            "Task: Press B now to enter Build Mode."
        ),
        "task": "enter_build_mode",
        "highlight": "hud",
    },
    {
        "id": 4,
        "title": "Placing Tiles",
        "instruction": (
            "In Build Mode, left-click any tile to place the selected type.\n"
            "The tile palette is on the right.\n\n"
            "Task: Place at least one WALL tile on the map."
        ),
        "task": "place_wall",
        "highlight": "tile_palette",
    },
    {
        "id": 5,
        "title": "Deleting Tiles",
        "instruction": (
            "Press 2 to switch to Delete sub-mode.\n"
            "Left-click a tile to replace it with floor.\n\n"
            "Task: Delete a tile by clicking it in Delete mode."
        ),
        "task": "delete_tile",
        "highlight": "hud",
    },
    {
        "id": 6,
        "title": "Tile Types",
        "instruction": (
            "The tile palette shows all tile types:\n"
            "  Floor — walkable, normal speed\n"
            "  Wall  — solid, blocks movement\n"
            "  Water — walkable, 50% speed\n"
            "  Void  — solid, dark\n\n"
            "Task: Place one Water tile."
        ),
        "task": "place_water",
        "highlight": "tile_palette",
    },
    {
        "id": 7,
        "title": "Inspecting Tiles",
        "instruction": (
            "Press 3 to switch to Inspect sub-mode.\n"
            "Click any tile to view its properties.\n\n"
            "Task: Inspect any tile."
        ),
        "task": "inspect_tile",
        "highlight": "hud",
    },
    {
        "id": 8,
        "title": "Spawning Entities",
        "instruction": (
            "Press E in Build Mode to open the entity spawn menu.\n"
            "Select NPC or Enemy, then click a tile to place it.\n\n"
            "Task: Spawn one NPC on the map."
        ),
        "task": "spawn_npc",
        "highlight": "entity_menu",
    },
    {
        "id": 9,
        "title": "Talking to an NPC",
        "instruction": (
            "Press B to exit build mode, then walk near an NPC.\n"
            "Press F to interact with it.\n\n"
            "Task: Talk to the NPC you just placed."
        ),
        "task": "interact_npc",
        "highlight": "player",
    },
    {
        "id": 10,
        "title": "Writing a Behavior Script",
        "instruction": (
            "Open the console (backtick `) and type:\n"
            "  settilecode 5 5\n\n"
            "This opens the code editor for that tile.\n"
            "Task: Open the code editor via settilecode command."
        ),
        "task": "open_code_editor",
        "highlight": "console",
    },
    {
        "id": 11,
        "title": "Hot Reload",
        "instruction": (
            "When you save a script with Ctrl+S,\n"
            "the game reloads it immediately — no restart needed!\n\n"
            "Task: Save the currently open script with Ctrl+S."
        ),
        "task": "save_script",
        "highlight": "code_editor",
    },
    {
        "id": 12,
        "title": "Inventory",
        "instruction": (
            "Press Tab to open your inventory.\n"
            "Items you pick up or are given will appear here.\n\n"
            "Task: Open the inventory with Tab."
        ),
        "task": "open_inventory",
        "highlight": "inventory",
    },
    {
        "id": 13,
        "title": "Giving Yourself Items",
        "instruction": (
            "Open the console (backtick `) and type:\n"
            "  giveitem stick 5\n\n"
            "Then type: listitems\n\n"
            "Task: Give yourself a stick using the console."
        ),
        "task": "give_item_stick",
        "highlight": "console",
    },
    {
        "id": 14,
        "title": "Console Commands",
        "instruction": (
            "The developer console supports many commands.\n"
            "Type: listcmds to see them all.\n"
            "Type: help [command] for details on any command.\n\n"
            "Task: Type 'listcmds' in the console."
        ),
        "task": "run_listcmds",
        "highlight": "console",
    },
    {
        "id": 15,
        "title": "You're Ready!",
        "instruction": (
            "Congratulations — you've completed the tutorial!\n\n"
            "You now know:\n"
            "  ✓ Movement and tile building\n"
            "  ✓ Entity spawning and interaction\n"
            "  ✓ Behavior scripting and hot reload\n"
            "  ✓ Inventory and item commands\n"
            "  ✓ Developer console\n\n"
            "Press H anytime for the full API reference.\n"
            "Go build something amazing!"
        ),
        "task": "click_next",
        "highlight": None,
    },
]


PROGRESS_FILE = "tutorial_progress.json"


class TutorialMode:
    """
    Manages the 15-step tutorial mode running in an isolated tutorial world.
    """

    def __init__(self, ui_manager: pygame_gui.UIManager):
        """
        Initialize tutorial mode.

        Args:
            ui_manager: pygame_gui UIManager instance
        """
        self.ui_manager = ui_manager
        self.active = False
        self.current_step_index = 0
        self.on_exit: Optional[Callable] = None

        # Task completion flags per step
        self._task_flags: Dict[str, bool] = {}

        # Callbacks the game loop injects so tutorial can detect task completion
        self.game_ref = None

        sw = settings.SCREEN_WIDTH
        sh = settings.SCREEN_HEIGHT

        # Instruction panel (right side, 28% width, 70% height)
        pw = int(sw * 0.28)
        ph = int(sh * 0.70)
        px = sw - pw - 10
        py = int(sh * 0.15)

        self.panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(px, py, pw, ph),
            manager=ui_manager,
            starting_layer_height=25
        )
        self.panel.hide()

        # Step number
        self.step_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 8, pw - 20, 24),
            text="Step 1 / 15",
            manager=ui_manager,
            container=self.panel
        )

        # Title
        self.title_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 38, pw - 20, 28),
            text="Welcome!",
            manager=ui_manager,
            container=self.panel
        )

        # Instruction text
        instruction_h = ph - 180
        self.instruction_box = pygame_gui.elements.UITextBox(
            html_text="<font size=3></font>",
            relative_rect=pygame.Rect(10, 74, pw - 20, instruction_h),
            manager=ui_manager,
            container=self.panel
        )

        # Buttons
        btn_y = ph - 96
        btn_w = (pw - 30) // 2

        self.next_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, btn_y, btn_w, 36),
            text="Next →",
            manager=ui_manager,
            container=self.panel
        )

        self.skip_step_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10 + btn_w + 10, btn_y, btn_w, 36),
            text="Skip Step",
            manager=ui_manager,
            container=self.panel
        )

        self.skip_tutorial_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, btn_y + 44, pw - 20, 32),
            text="Skip Tutorial",
            manager=ui_manager,
            container=self.panel
        )

    # ------------------------------------------------------------------
    # Start / stop
    # ------------------------------------------------------------------

    def start(self, game_ref, from_step: int = 0) -> None:
        """
        Start or resume the tutorial.

        Args:
            game_ref: Reference to Game instance
            from_step: Step index to start from (0-based)
        """
        self.game_ref = game_ref
        self.active = True
        self.current_step_index = from_step
        self._task_flags = {}
        self._show_current_step()
        self.panel.show()

    def stop(self) -> None:
        """Stop the tutorial and save progress."""
        self.active = False
        self.panel.hide()
        self._save_progress()
        if self.on_exit:
            self.on_exit()

    # ------------------------------------------------------------------
    # Step display
    # ------------------------------------------------------------------

    def _show_current_step(self) -> None:
        """Render the current tutorial step into the panel."""
        if self.current_step_index >= len(TUTORIAL_STEPS):
            self.stop()
            return

        step = TUTORIAL_STEPS[self.current_step_index]
        total = len(TUTORIAL_STEPS)

        self.step_label.set_text(f"Step {step['id']} / {total}")
        self.title_label.set_text(step['title'])

        safe_text = (
            step['instruction']
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("\n", "<br>")
        )
        html = f"<font size=3>{safe_text}</font>"

        try:
            self.instruction_box.kill()
            pw = int(settings.SCREEN_WIDTH * 0.28)
            ph = int(settings.SCREEN_HEIGHT * 0.70)
            instruction_h = ph - 180

            self.instruction_box = pygame_gui.elements.UITextBox(
                html_text=html,
                relative_rect=pygame.Rect(10, 74, pw - 20, instruction_h),
                manager=self.ui_manager,
                container=self.panel
            )
        except Exception as e:
            print(f"Tutorial instruction box error: {e}")

        # Next button only enabled when task is "click_next" or task completed
        task = step.get('task', 'click_next')
        can_advance = (task == 'click_next') or self._task_flags.get(task, False)
        if can_advance:
            self.next_button.enable()
        else:
            self.next_button.disable()

    def _advance_step(self) -> None:
        """Move to the next tutorial step."""
        self._save_progress()
        self.current_step_index += 1
        self._task_flags = {}

        if self.current_step_index >= len(TUTORIAL_STEPS):
            self.stop()
        else:
            self._show_current_step()

    # ------------------------------------------------------------------
    # Task completion detection
    # ------------------------------------------------------------------

    def notify_task_complete(self, task: str) -> None:
        """
        Called by the game when a task is detected as complete.

        Args:
            task: Task identifier string matching TUTORIAL_STEPS[n]['task']
        """
        if not self.active:
            return

        step = TUTORIAL_STEPS[self.current_step_index]
        if step.get('task') == task:
            self._task_flags[task] = True
            # Re-enable the Next button
            self.next_button.enable()

    # ------------------------------------------------------------------
    # Progress persistence
    # ------------------------------------------------------------------

    def _save_progress(self) -> None:
        """Save tutorial progress to file."""
        try:
            data = {
                'current_step': self.current_step_index,
                'completed_steps': list(self._task_flags.keys())
            }
            with open(PROGRESS_FILE, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving tutorial progress: {e}")

    def load_progress(self) -> int:
        """
        Load tutorial progress from file.

        Returns:
            Step index to resume from (0 if no progress)
        """
        try:
            if os.path.exists(PROGRESS_FILE):
                with open(PROGRESS_FILE, 'r') as f:
                    data = json.load(f)
                return int(data.get('current_step', 0))
        except Exception as e:
            print(f"Error loading tutorial progress: {e}")
        return 0

    def reset_progress(self) -> None:
        """Reset tutorial progress to the beginning."""
        try:
            if os.path.exists(PROGRESS_FILE):
                os.remove(PROGRESS_FILE)
        except Exception as e:
            print(f"Error resetting tutorial progress: {e}")
        self.current_step_index = 0
        self._task_flags = {}

    # ------------------------------------------------------------------
    # Event handling
    # ------------------------------------------------------------------

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle UI events.

        Args:
            event: pygame event

        Returns:
            True if event was consumed
        """
        if not self.active:
            return False

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.next_button:
                self._advance_step()
                return True

            if event.ui_element == self.skip_step_button:
                self._advance_step()
                return True

            if event.ui_element == self.skip_tutorial_button:
                self.stop()
                return True

        return False

    # ------------------------------------------------------------------
    # Per-frame update (task detection)
    # ------------------------------------------------------------------

    def update(self, dt: float) -> None:
        """
        Check per-frame task completion conditions.

        Args:
            dt: Delta time in seconds
        """
        if not self.active or not self.game_ref:
            return

        step = TUTORIAL_STEPS[self.current_step_index]
        task = step.get('task', 'click_next')

        if self._task_flags.get(task):
            return  # Already completed

        game = self.game_ref

        # Detect movement
        if task == "move":
            if game.player:
                center_x = game.current_world.tile_map.width * settings.TILE_SIZE / 2
                center_y = game.current_world.tile_map.height * settings.TILE_SIZE / 2
                dx = abs(game.player.position[0] - center_x)
                dy = abs(game.player.position[1] - center_y)
                if dx > settings.TILE_SIZE or dy > settings.TILE_SIZE:
                    self.notify_task_complete("move")

        elif task == "enter_build_mode":
            if game.game_mode == "build":
                self.notify_task_complete("enter_build_mode")

        elif task == "place_wall":
            if game.current_world:
                for row in game.current_world.tile_map.tiles:
                    for tile in row:
                        if tile and tile.tile_type == "wall":
                            self.notify_task_complete("place_wall")
                            return

        elif task == "delete_tile":
            if game.tile_editor.sub_mode == "Delete":
                self.notify_task_complete("delete_tile")

        elif task == "place_water":
            if game.current_world:
                for row in game.current_world.tile_map.tiles:
                    for tile in row:
                        if tile and tile.tile_type == "water":
                            self.notify_task_complete("place_water")
                            return

        elif task == "inspect_tile":
            if game.tile_editor.sub_mode == "Inspect":
                self.notify_task_complete("inspect_tile")

        elif task == "spawn_npc":
            if game.current_world:
                from entities.npc import NPC
                for entity in game.current_world.entities:
                    if isinstance(entity, NPC):
                        self.notify_task_complete("spawn_npc")
                        return

        elif task == "interact_npc":
            if game.dialogue_text:
                self.notify_task_complete("interact_npc")

        elif task == "open_code_editor":
            if game.code_editor.active:
                self.notify_task_complete("open_code_editor")

        elif task == "save_script":
            # Detected via external call from game._on_script_saved
            pass

        elif task == "open_inventory":
            if game.inventory_editor.active:
                self.notify_task_complete("open_inventory")

        elif task == "give_item_stick":
            if game.player and game.player.inventory.has_item("stick"):
                self.notify_task_complete("give_item_stick")

        elif task == "run_listcmds":
            # Detected via external call
            pass
