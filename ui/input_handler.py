# =============================================================================
# File: sandbox_game/core/input_handler.py
# =============================================================================
"""
Input handling abstraction for keyboard, mouse, and virtual mobile controls.
Mobile controls inject synthetic state here — no duplicate logic in callers.
"""

import pygame
from typing import Tuple, Dict, Set


class InputHandler:
    """
    Centralized input handling with state tracking and virtual input injection.
    Mobile controls call inject_* methods; game logic reads is_key_pressed etc.
    """

    def __init__(self):
        """Initialize all input state containers."""
        self.keys_pressed: Set[int] = set()
        self.keys_just_pressed: Set[int] = set()
        self.keys_just_released: Set[int] = set()

        self.mouse_pos: Tuple[int, int] = (0, 0)
        self.mouse_buttons = [False, False, False]
        self.mouse_just_pressed = [False, False, False]
        self.mouse_just_released = [False, False, False]

        # Virtual injections from mobile controls (reset each frame)
        self._virtual_keys: Set[int] = set()
        self._virtual_mouse_buttons = [False, False, False]
        self._virtual_mouse_pos: Tuple[int, int] = (0, 0)
        self._use_virtual_mouse = False

    # ------------------------------------------------------------------
    # Frame update
    # ------------------------------------------------------------------

    def update(self, events: list) -> None:
        """
        Update input state from pygame events and merge virtual input.

        Args:
            events: List of pygame events from current frame
        """
        # Clear just-pressed / released each frame
        self.keys_just_pressed.clear()
        self.keys_just_released.clear()
        self.mouse_just_pressed = [False, False, False]
        self.mouse_just_released = [False, False, False]
        self._use_virtual_mouse = False

        for event in events:
            if event.type == pygame.KEYDOWN:
                self.keys_pressed.add(event.key)
                self.keys_just_pressed.add(event.key)

            elif event.type == pygame.KEYUP:
                self.keys_pressed.discard(event.key)
                self.keys_just_released.add(event.key)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if 1 <= event.button <= 3:
                    self.mouse_buttons[event.button - 1] = True
                    self.mouse_just_pressed[event.button - 1] = True

            elif event.type == pygame.MOUSEBUTTONUP:
                if 1 <= event.button <= 3:
                    self.mouse_buttons[event.button - 1] = False
                    self.mouse_just_released[event.button - 1] = True

        self.mouse_pos = pygame.mouse.get_pos()

        # Merge virtual keys (held from mobile controls)
        for vk in self._virtual_keys:
            if vk not in self.keys_pressed:
                self.keys_just_pressed.add(vk)
            self.keys_pressed.add(vk)

        # Merge virtual mouse if injected this frame
        if self._use_virtual_mouse:
            self.mouse_pos = self._virtual_mouse_pos
            for i in range(3):
                if self._virtual_mouse_buttons[i] and not self.mouse_buttons[i]:
                    self.mouse_just_pressed[i] = True
                self.mouse_buttons[i] = (
                    self.mouse_buttons[i] or self._virtual_mouse_buttons[i]
                )

    # ------------------------------------------------------------------
    # Virtual injection API (called by MobileControls)
    # ------------------------------------------------------------------

    def inject_key(self, key: int, held: bool) -> None:
        """
        Inject a virtual key press from mobile controls.

        Args:
            key: pygame key constant
            held: True = key is held this frame
        """
        if held:
            self._virtual_keys.add(key)
        else:
            self._virtual_keys.discard(key)

    def inject_mouse_button(self, button: int, pressed: bool) -> None:
        """
        Inject a virtual mouse button state.

        Args:
            button: 0=left, 1=middle, 2=right
            pressed: Whether the button is pressed
        """
        if 0 <= button <= 2:
            self._virtual_mouse_buttons[button] = pressed
            self._use_virtual_mouse = True

    def inject_mouse_pos(self, pos: Tuple[int, int]) -> None:
        """
        Inject a virtual mouse position.

        Args:
            pos: (x, y) screen coordinates
        """
        self._virtual_mouse_pos = pos
        self._use_virtual_mouse = True

    def clear_virtual(self) -> None:
        """Clear all virtual injections (call at end of mobile update)."""
        self._virtual_keys.clear()
        self._virtual_mouse_buttons = [False, False, False]
        self._use_virtual_mouse = False

    # ------------------------------------------------------------------
    # Query API
    # ------------------------------------------------------------------

    def is_key_pressed(self, key: int) -> bool:
        """Return True if key is currently held down."""
        return key in self.keys_pressed

    def is_key_just_pressed(self, key: int) -> bool:
        """Return True if key was pressed this frame."""
        return key in self.keys_just_pressed

    def is_key_just_released(self, key: int) -> bool:
        """Return True if key was released this frame."""
        return key in self.keys_just_released

    def get_mouse_pos(self) -> Tuple[int, int]:
        """Return current (possibly virtual) mouse position."""
        return self.mouse_pos

    def is_mouse_button_pressed(self, button: int) -> bool:
        """Return True if mouse button is held (0=left,1=mid,2=right)."""
        if 0 <= button <= 2:
            return self.mouse_buttons[button]
        return False

    def is_mouse_button_just_pressed(self, button: int) -> bool:
        """Return True if mouse button was just pressed this frame."""
        if 0 <= button <= 2:
            return self.mouse_just_pressed[button]
        return False
