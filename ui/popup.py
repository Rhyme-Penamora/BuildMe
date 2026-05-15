# =============================================================================
# File: sandbox_game/ui/popup.py
# =============================================================================
"""
Reusable modal popup dialog.
"""

import pygame
import pygame_gui
from typing import Optional, Callable


class Popup:
    """
    Modal popup dialog with title, message, and confirm/cancel buttons.
    """

    def __init__(
        self,
        ui_manager: pygame_gui.UIManager,
        title: str,
        message: str,
        on_confirm: Optional[Callable] = None,
        on_cancel: Optional[Callable] = None,
        confirm_text: str = "OK",
        cancel_text: str = "Cancel",
        show_cancel: bool = True
    ):
        """
        Initialize popup.

        Args:
            ui_manager: pygame_gui UIManager instance
            title: Popup title
            message: Popup message text
            on_confirm: Callback when confirm button is clicked
            on_cancel: Callback when cancel button is clicked
            confirm_text: Text for confirm button
            cancel_text: Text for cancel button
            show_cancel: Whether to show cancel button
        """
        self.ui_manager = ui_manager
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel
        self.active = True

        screen_width, screen_height = ui_manager.get_root_container().get_size()

        popup_width = int(screen_width * 0.35)
        popup_height = 220
        popup_x = (screen_width - popup_width) // 2
        popup_y = (screen_height - popup_height) // 2

        self.dialog = pygame_gui.windows.UIConfirmationDialog(
            rect=pygame.Rect(popup_x, popup_y, popup_width, popup_height),
            manager=ui_manager,
            window_title=title,
            action_long_desc=message,
            action_short_name=confirm_text,
            blocking=True
        )

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle UI events for this popup.

        Args:
            event: pygame event

        Returns:
            True if event was consumed
        """
        if event.type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
            if event.ui_element == self.dialog:
                self.active = False
                if self.on_confirm:
                    self.on_confirm()
                return True

        if event.type == pygame_gui.UI_WINDOW_CLOSE:
            if event.ui_element == self.dialog:
                self.active = False
                if self.on_cancel:
                    self.on_cancel()
                return True

        return False
