# =============================================================================
# File: sandbox_game/ui/mobile_controls.py
# =============================================================================
"""
Mobile virtual controls: D-pad, action buttons, FAB menu.
All controls inject into InputHandler — zero duplicate game logic.
"""

import pygame
import pygame_gui
from typing import Optional, List, Tuple, Dict
from core.input_handler import InputHandler
import settings


# Minimum tap target size in pixels (accessibility standard)
MIN_BTN = 48


class _VirtualButton:
    """A single circular/square virtual button drawn on screen."""

    def __init__(
        self,
        label: str,
        center: Tuple[int, int],
        size: int,
        color: Tuple[int, int, int],
        alpha: int = 160,
    ):
        """
        Initialize virtual button.

        Args:
            label: Text shown on button
            center: (cx, cy) screen position
            size: Diameter in pixels
            color: RGB fill color
            alpha: Transparency 0-255
        """
        self.label = label
        self.center = center
        self.size = max(MIN_BTN, size)
        self.color = color
        self.alpha = alpha
        self.pressed = False
        self._font: Optional[pygame.font.Font] = None

    def get_rect(self) -> pygame.Rect:
        """Return bounding rect for hit testing."""
        half = self.size // 2
        return pygame.Rect(
            self.center[0] - half,
            self.center[1] - half,
            self.size,
            self.size,
        )

    def contains(self, pos: Tuple[int, int]) -> bool:
        """Return True if pos is inside this button."""
        return self.get_rect().collidepoint(pos)

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the button onto surface.

        Args:
            surface: Target pygame surface
        """
        if self._font is None:
            try:
                self._font = pygame.font.Font(None, 22)
            except Exception:
                self._font = None

        rect = self.get_rect()

        # Semi-transparent fill
        btn_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        fill_color = (*self.color, self.alpha) if not self.pressed else (
            min(255, self.color[0] + 60),
            min(255, self.color[1] + 60),
            min(255, self.color[2] + 60),
            self.alpha,
        )
        pygame.draw.ellipse(btn_surf, fill_color, btn_surf.get_rect())
        pygame.draw.ellipse(
            btn_surf,
            (255, 255, 255, 180),
            btn_surf.get_rect(),
            2,
        )
        surface.blit(btn_surf, rect.topleft)

        # Label
        if self._font:
            txt = self._font.render(self.label, True, (255, 255, 255))
            tx = rect.centerx - txt.get_width() // 2
            ty = rect.centery - txt.get_height() // 2
            surface.blit(txt, (tx, ty))


class MobileControls:
    """
    Full mobile control layer.

    D-pad bottom-left, action buttons bottom-right, FAB top-right.
    All button presses are translated to InputHandler virtual key injections.
    """

    def __init__(self, input_handler: InputHandler, keybindings: Dict[str, int]):
        """
        Initialize mobile controls.

        Args:
            input_handler: Game InputHandler to inject into
            keybindings: Current keybinding dict (action -> key constant)
        """
        self.input_handler = input_handler
        self.keybindings = keybindings
        self.enabled = False

        self._dpad_size = settings.GLOBAL_SETTINGS.get('dpad_size', 80)
        self._btn_size = settings.GLOBAL_SETTINGS.get('action_btn_size', 64)

        self._fab_expanded = False
        self._buttons: List[_VirtualButton] = []
        self._fab_menu_buttons: List[_VirtualButton] = []

        # Track which action buttons are held between frames
        self._held_actions: Dict[str, bool] = {}

        self._build_layout()

    # ------------------------------------------------------------------
    # Layout construction
    # ------------------------------------------------------------------

    def _build_layout(self) -> None:
        """Build all virtual button positions relative to screen size."""
        sw = settings.SCREEN_WIDTH
        sh = settings.SCREEN_HEIGHT
        ds = self._dpad_size
        bs = self._btn_size

        self._buttons.clear()
        self._fab_menu_buttons.clear()
        self._held_actions.clear()

        # --- D-pad (bottom-left) ---
        pad_cx = int(sw * 0.12)
        pad_cy = int(sh * 0.82)

        self._dpad_up = _VirtualButton("▲", (pad_cx, pad_cy - ds), ds, (70, 70, 120))
        self._dpad_down = _VirtualButton("▼", (pad_cx, pad_cy + ds), ds, (70, 70, 120))
        self._dpad_left = _VirtualButton("◀", (pad_cx - ds, pad_cy), ds, (70, 70, 120))
        self._dpad_right = _VirtualButton("▶", (pad_cx + ds, pad_cy), ds, (70, 70, 120))

        self._buttons += [
            self._dpad_up, self._dpad_down,
            self._dpad_left, self._dpad_right,
        ]

        # --- Action buttons (bottom-right) ---
        act_cx = int(sw * 0.88)
        act_cy = int(sh * 0.82)
        gap = bs + 10

        self._btn_interact = _VirtualButton("F", (act_cx, act_cy - gap), bs, (80, 140, 80))
        self._btn_build = _VirtualButton("B", (act_cx - gap, act_cy), bs, (140, 100, 40))
        self._btn_inventory = _VirtualButton("Tab", (act_cx + gap, act_cy), bs, (100, 60, 140))
        self._btn_attack = _VirtualButton("ATK", (act_cx, act_cy + gap), bs, (160, 50, 50))

        self._buttons += [
            self._btn_interact, self._btn_build,
            self._btn_inventory, self._btn_attack,
        ]

        # --- FAB (top-right) ---
        self._fab_btn = _VirtualButton("☰", (int(sw * 0.96), int(sh * 0.05)), bs, (60, 60, 100))
        self._buttons.append(self._fab_btn)

        # FAB expanded menu items (stacked vertically below FAB)
        fab_labels = ["Save", "Help", "Settings", "File Editor", "Exit Menu"]
        fab_x = int(sw * 0.96)
        fab_start_y = int(sh * 0.12)
        for i, label in enumerate(fab_labels):
            fb = _VirtualButton(label, (fab_x, fab_start_y + i * (bs + 8)), bs, (50, 50, 90))
            self._fab_menu_buttons.append(fb)

        # Map action buttons to keybinding actions
        self._action_map: Dict[_VirtualButton, str] = {
            self._dpad_up:       'move_up',
            self._dpad_down:     'move_down',
            self._dpad_left:     'move_left',
            self._dpad_right:    'move_right',
            self._btn_interact:  'interact',
            self._btn_build:     'build_mode',
            self._btn_inventory: 'inventory',
        }

    # ------------------------------------------------------------------
    # Enable / disable
    # ------------------------------------------------------------------

    def enable(self) -> None:
        """Enable mobile controls."""
        self.enabled = True

    def disable(self) -> None:
        """Disable mobile controls and clear all injected state."""
        self.enabled = False
        self._fab_expanded = False
        self.input_handler.clear_virtual()

    def set_dpad_size(self, size: int) -> None:
        """
        Change D-pad button size and rebuild layout.

        Args:
            size: New size in pixels
        """
        self._dpad_size = max(MIN_BTN, size)
        self._build_layout()

    def set_action_btn_size(self, size: int) -> None:
        """
        Change action button size and rebuild layout.

        Args:
            size: New size in pixels
        """
        self._btn_size = max(MIN_BTN, size)
        self._build_layout()

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(self, events: list) -> None:
        """
        Process touch/mouse events and inject into InputHandler.

        Args:
            events: pygame event list from current frame
        """
        if not self.enabled:
            return

        # Reset all virtual held keys before processing this frame
        for btn, action in self._action_map.items():
            key = self.keybindings.get(action)
            if key is not None:
                self.input_handler.inject_key(key, False)

        mouse_pos = pygame.mouse.get_pos()
        mouse_down = pygame.mouse.get_pressed()[0]

        # Check each action button hold state
        for btn, action in self._action_map.items():
            key = self.keybindings.get(action)
            if key is None:
                continue
            held = mouse_down and btn.contains(mouse_pos)
            btn.pressed = held
            self.input_handler.inject_key(key, held)

        # Handle one-shot events (MOUSEBUTTONDOWN) for toggle buttons
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos

                # FAB toggle
                if self._fab_btn.contains(pos):
                    self._fab_expanded = not self._fab_expanded
                    continue

                # FAB menu items (one-shot injections via key press)
                if self._fab_expanded:
                    for i, fb in enumerate(self._fab_menu_buttons):
                        if fb.contains(pos):
                            self._handle_fab_item(i)
                            self._fab_expanded = False
                            break

    def _handle_fab_item(self, index: int) -> None:
        """
        Handle FAB menu item press by injecting appropriate key.

        Args:
            index: Index in fab_labels list
        """
        # FAB items: Save, Help, Settings, File Editor, Exit Menu
        fab_keys = [
            None,                                    # Save — handled by event bus
            self.keybindings.get('help'),            # Help
            self.keybindings.get('menu'),            # Settings/menu
            None,                                    # File Editor
            self.keybindings.get('menu'),            # Exit (same as menu)
        ]
        key = fab_keys[index] if index < len(fab_keys) else None
        if key is not None:
            # Momentary press — inject then schedule release next frame
            self.input_handler.inject_key(key, True)

        # Publish FAB-specific events via event bus for Save/File Editor
        from core.event_bus import event_bus
        fab_events = ['fab_save', 'fab_help', 'fab_settings', 'fab_file_editor', 'fab_exit_menu']
        if index < len(fab_events):
            event_bus.publish(fab_events[index])

    # ------------------------------------------------------------------
    # Render
    # ------------------------------------------------------------------

    def render(self, screen: pygame.Surface) -> None:
        """
        Draw all virtual controls onto screen.

        Args:
            screen: pygame display surface
        """
        if not self.enabled:
            return

        for btn in self._buttons:
            btn.draw(screen)

        if self._fab_expanded:
            for fb in self._fab_menu_buttons:
                fb.draw(screen)
