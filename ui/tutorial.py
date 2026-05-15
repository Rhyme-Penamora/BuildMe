# =============================================================================
# File: sandbox_game/ui/tutorial.py
# =============================================================================
"""
Tutorial mode — isolated world, 15 guided steps.
"""

import pygame
import pygame_gui
from typing import Optional, Callable
import settings


class TutorialMode:
    """
    Tutorial mode with step-by-step guided tasks.
    """

    def __init__(self, ui_manager: pygame_gui.UIManager):
        self.ui_manager = ui_manager
        self.active = False
        self.on_exit: Optional[Callable] = None

    def show(self) -> None:
        self.active = True

    def hide(self) -> None:
        self.active = False

    def notify_task_complete(self, task: str) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def handle_event(self, event: pygame.event.Event) -> bool:
        return False
