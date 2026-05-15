# =============================================================================
# File: sandbox_game/core/input_handler.py
# =============================================================================
"""
Input handling abstraction for keyboard and mouse.
Future mobile touch input will integrate here.
"""

import pygame
from typing import Tuple


class InputHandler:
    """
    Centralized input handling with state tracking.
    Abstracts input so touch controls can be added without changing game logic.
    """
    
    def __init__(self):
        self.keys_pressed = set()
        self.keys_just_pressed = set()
        self.keys_just_released = set()
        self.mouse_pos = (0, 0)
        self.mouse_buttons = [False, False, False]  # left, middle, right
        self.mouse_just_pressed = [False, False, False]
        self.mouse_just_released = [False, False, False]
    
    def update(self, events: list) -> None:
        """
        Update input state from pygame events.
        
        Args:
            events: List of pygame events from current frame
        """
        # Clear just-pressed/released states
        self.keys_just_pressed.clear()
        self.keys_just_released.clear()
        self.mouse_just_pressed = [False, False, False]
        self.mouse_just_released = [False, False, False]
        
        # Process events
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
        
        # Update mouse position
        self.mouse_pos = pygame.mouse.get_pos()
    
    def is_key_pressed(self, key: int) -> bool:
        """Check if key is currently held down."""
        return key in self.keys_pressed
    
    def is_key_just_pressed(self, key: int) -> bool:
        """Check if key was just pressed this frame."""
        return key in self.keys_just_pressed
    
    def is_key_just_released(self, key: int) -> bool:
        """Check if key was just released this frame."""
        return key in self.keys_just_released
    
    def get_mouse_pos(self) -> Tuple[int, int]:
        """Get current mouse position."""
        return self.mouse_pos
    
    def is_mouse_button_pressed(self, button: int) -> bool:
        """Check if mouse button is held (0=left, 1=middle, 2=right)."""
        if 0 <= button <= 2:
            return self.mouse_buttons[button]
        return False
    
    def is_mouse_button_just_pressed(self, button: int) -> bool:
        """Check if mouse button was just pressed (0=left, 1=middle, 2=right)."""
        if 0 <= button <= 2:
            return self.mouse_just_pressed[button]
        return False
