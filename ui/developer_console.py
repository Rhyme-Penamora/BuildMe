# =============================================================================
# File: sandbox_game/ui/developer_console.py
# =============================================================================
"""
Developer console with command execution and scrollable log.
"""

import pygame
import pygame_gui
from typing import Callable, Dict, List, Optional
import settings


class DeveloperConsole:
    """
    In-game developer console with command history and colored output.
    """

    def __init__(self, ui_manager: pygame_gui.UIManager):
        self.ui_manager = ui_manager
        self.active = False
        self.commands: Dict[str, Callable] = {}
        self.log_lines: List[str] = []
        self.command_history: List[str] = []
        self.history_index = -1

        sw = settings.SCREEN_WIDTH
        sh = settings.SCREEN_HEIGHT

        pw = int(sw * 0.7)
        ph = int(sh * 0.5)
        px = (sw - pw) // 2
        py = sh - ph - 10

        self.panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(px, py, pw, ph),
            manager=ui_manager
        )
        self.panel.hide()

        self.title_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 8, pw - 20, 24),
            text="Developer Console",
            manager=ui_manager,
            container=self.panel
        )

        log_h = ph - 100
        self.log_box = pygame_gui.elements.UITextBox(
            html_text="<font face='monospace' size=3 color='#00FF00'>Console ready. Type 'listcmds' for all commands.</font>",
            relative_rect=pygame.Rect(10, 40, pw - 20, log_h),
            manager=ui_manager,
            container=self.panel
        )

        entry_y = 40 + log_h + 6
        self.input_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(10, entry_y, pw - 20, 32),
            manager=ui_manager,
            container=self.panel
        )

        self.log_lines.append(
            "<font face='monospace' size=3 color='#00FF00'>Console ready. Type 'listcmds' for all commands.</font>"
        )

    def toggle(self) -> None:
        if self.active:
            self.active = False
            self.panel.hide()
        else:
            self.active = True
            self.panel.show()

    def register_command(self, name: str, callback: Callable) -> None:
        self.commands[name] = callback

    def execute(self, command_line: str) -> None:
        if not command_line.strip():
            return

        self.command_history.append(command_line)
        self.history_index = len(self.command_history)

        parts = command_line.split()
        cmd = parts[0].lower()
        args = parts[1:]

        self.log(f"> {command_line}", "#FFFF00")

        if cmd in self.commands:
            try:
                self.commands[cmd](args)
            except Exception as e:
                self.log(f"Error: {e}", "#FF0000")
        else:
            self.log(f"Unknown command '{cmd}'. Type 'listcmds' for help.", "#FF0000")

    def log(self, message: str, color: str = "#FFFFFF") -> None:
        safe = message.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        self.log_lines.append(f"<font face='monospace' size=3 color='{color}'>{safe}</font>")
        if len(self.log_lines) > 200:
            self.log_lines = self.log_lines[-200:]
        self._refresh_log()

    def clear_log(self) -> None:
        self.log_lines.clear()
        self.log_lines.append(
            "<font face='monospace' size=3 color='#00FF00'>Console cleared.</font>"
        )
        self._refresh_log()

    def _refresh_log(self) -> None:
        html = "<br>".join(self.log_lines)
        try:
            self.log_box.kill()
            pw = int(settings.SCREEN_WIDTH * 0.7)
            ph = int(settings.SCREEN_HEIGHT * 0.5)
            log_h = ph - 100
            self.log_box = pygame_gui.elements.UITextBox(
                html_text=html,
                relative_rect=pygame.Rect(10, 40, pw - 20, log_h),
                manager=self.ui_manager,
                container=self.panel
            )
        except Exception as e:
            print(f"Console log refresh error: {e}")

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.active:
            return False

        if event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
            if event.ui_element == self.input_entry:
                cmd = self.input_entry.get_text()
                self.input_entry.set_text("")
                self.execute(cmd)
                return True

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                if self.command_history and self.history_index > 0:
                    self.history_index -= 1
                    self.input_entry.set_text(self.command_history[self.history_index])
                return True
            if event.key == pygame.K_DOWN:
                if self.command_history:
                    if self.history_index < len(self.command_history) - 1:
                        self.history_index += 1
                        self.input_entry.set_text(self.command_history[self.history_index])
                    else:
                        self.history_index = len(self.command_history)
                        self.input_entry.set_text("")
                return True

        return False
