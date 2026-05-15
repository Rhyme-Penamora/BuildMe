# =============================================================================
# File: sandbox_game/ui/developer_console.py
# =============================================================================
"""
Developer console for executing game commands at runtime.
"""

import pygame
import pygame_gui
from typing import List, Callable, Optional, Dict
import settings


class DeveloperConsole:
    """
    In-game developer console with command execution, history, and colored log output.
    """

    def __init__(self, ui_manager: pygame_gui.UIManager):
        """
        Initialize developer console.

        Args:
            ui_manager: pygame_gui UIManager instance
        """
        self.ui_manager = ui_manager
        self.active = False
        self.command_history: List[str] = []
        self.history_index = 0
        self.commands: Dict[str, Callable] = {}

        screen_width = settings.SCREEN_WIDTH
        screen_height = settings.SCREEN_HEIGHT

        console_height = int(screen_height * 0.4)
        console_y = screen_height - console_height

        self.panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(0, console_y, screen_width, console_height),
            manager=ui_manager,
            starting_layer_height=15
        )
        self.panel.hide()

        log_height = console_height - 60

        # UITextBox supports append_html_text in pygame_gui 0.6.x
        self.log_box = pygame_gui.elements.UITextBox(
            html_text=(
                "<font face='monospace' size=3 color='#AAAAAA'>"
                "Developer Console ready. Type 'listcmds' for commands."
                "</font>"
            ),
            relative_rect=pygame.Rect(5, 5, screen_width - 10, log_height),
            manager=ui_manager,
            container=self.panel
        )

        self.input_field = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(5, log_height + 10, screen_width - 10, 40),
            manager=ui_manager,
            container=self.panel
        )

    def register_command(self, name: str, callback: Callable) -> None:
        """
        Register a named command with its callback.

        Args:
            name: Command name (case-insensitive match applied at call time)
            callback: Function(args: list) to invoke
        """
        self.commands[name.lower()] = callback

    def toggle(self) -> None:
        """Toggle console visibility."""
        if self.active:
            self.hide()
        else:
            self.show()

    def show(self) -> None:
        """Show the console and focus the input field."""
        self.active = True
        self.panel.show()
        self.input_field.focus()

    def hide(self) -> None:
        """Hide the console."""
        self.active = False
        self.panel.hide()

    def log(self, message: str, color: str = "#FFFFFF") -> None:
        """
        Append a line to the console log with a given color.

        Args:
            message: Text to append
            color: HTML hex color string e.g. '#FF0000'
        """
        # Escape any HTML-significant characters in the message
        safe_message = (
            message
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
        html_line = f"<font face='monospace' size=3 color='{color}'>{safe_message}</font><br>"

        try:
            self.log_box.append_html_text(html_line)
        except Exception as e:
            print(f"Console log error: {e}")

    def execute_command(self, command_str: str) -> None:
        """
        Parse and execute a command string.

        Args:
            command_str: Raw command string typed by user
        """
        command_str = command_str.strip()
        if not command_str:
            return

        self.command_history.append(command_str)
        self.history_index = len(self.command_history)

        self.log(f"> {command_str}", "#00FF00")

        parts = command_str.split()
        cmd_name = parts[0].lower()
        args = parts[1:]

        if cmd_name in self.commands:
            try:
                self.commands[cmd_name](args)
            except Exception as e:
                self.log(f"Error executing '{cmd_name}': {e}", "#FF0000")
        else:
            self.log(
                f"Unknown command: '{cmd_name}'. Type 'listcmds' for all commands.",
                "#FF0000"
            )

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle events relevant to the console.

        Args:
            event: pygame event

        Returns:
            True if event was consumed
        """
        if not self.active:
            return False

        if event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
            if event.ui_element == self.input_field:
                self.execute_command(event.text)
                self.input_field.set_text("")
                return True

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                if self.history_index > 0:
                    self.history_index -= 1
                    self.input_field.set_text(
                        self.command_history[self.history_index]
                    )
                return True

            if event.key == pygame.K_DOWN:
                if self.history_index < len(self.command_history) - 1:
                    self.history_index += 1
                    self.input_field.set_text(
                        self.command_history[self.history_index]
                    )
                else:
                    self.history_index = len(self.command_history)
                    self.input_field.set_text("")
                return True

        return False

    def clear_log(self) -> None:
        """Clear the console log display."""
        try:
            self.log_box.kill()
            screen_width = settings.SCREEN_WIDTH
            console_height = int(settings.SCREEN_HEIGHT * 0.4)
            log_height = console_height - 60

            self.log_box = pygame_gui.elements.UITextBox(
                html_text="<font face='monospace' size=3 color='#AAAAAA'>Console cleared.</font>",
                relative_rect=pygame.Rect(5, 5, screen_width - 10, log_height),
                manager=self.ui_manager,
                container=self.panel
            )
        except Exception as e:
            print(f"Error clearing console log: {e}")
