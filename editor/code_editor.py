# =============================================================================
# File: sandbox_game/editor/code_editor.py
# =============================================================================
"""
In-game code editor with multi-line editing, syntax highlighting, and error display.
"""

import os
import pygame
import pygame_gui
from typing import Optional, Callable, List
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
import settings


class CodeEditor:
    """
    In-game popup code editor.
    Uses a pygame_gui UITextBox for display and a UITextEntryLine for the
    current-line input, together with an internal line buffer for multi-line editing.
    Ctrl+S saves; errors shown in a red bar at the bottom.
    """

    def __init__(self, ui_manager: pygame_gui.UIManager):
        """
        Initialize code editor.

        Args:
            ui_manager: pygame_gui UIManager instance
        """
        self.ui_manager = ui_manager
        self.active = False
        self.current_file: Optional[str] = None
        self.on_save: Optional[Callable] = None
        self.error_message: Optional[str] = None

        # Internal line buffer
        self._lines: List[str] = [""]
        self._cursor_line = 0

        # Undo / redo stacks — each entry is a snapshot of self._lines
        self._undo_stack: List[List[str]] = []
        self._redo_stack: List[List[str]] = []

        self.screen_width = settings.SCREEN_WIDTH
        self.screen_height = settings.SCREEN_HEIGHT

        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        """Build all pygame_gui elements for the editor panel."""
        pw = int(self.screen_width * 0.82)
        ph = int(self.screen_height * 0.85)
        px = (self.screen_width - pw) // 2
        py = (self.screen_height - ph) // 2

        self.panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(px, py, pw, ph),
            manager=self.ui_manager,
            starting_layer_height=20
        )
        self.panel.hide()

        # Title
        self.title_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 8, pw - 20, 28),
            text="Code Editor",
            manager=self.ui_manager,
            container=self.panel
        )

        # Code display (read-only HTMLTextBox with syntax highlighting)
        display_h = ph - 170
        self.display_box = pygame_gui.elements.UITextBox(
            html_text="<font face='monospace' size=3></font>",
            relative_rect=pygame.Rect(10, 44, pw - 20, display_h),
            manager=self.ui_manager,
            container=self.panel
        )

        # Current-line entry
        entry_y = 44 + display_h + 6
        self.line_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(10, entry_y, pw - 20, 36),
            manager=self.ui_manager,
            container=self.panel
        )

        # Buttons row
        btn_y = entry_y + 44
        btn_w = 130
        gap = 10

        self.save_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, btn_y, btn_w, 36),
            text="Save (Ctrl+S)",
            manager=self.ui_manager,
            container=self.panel
        )
        self.close_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10 + btn_w + gap, btn_y, btn_w, 36),
            text="Close",
            manager=self.ui_manager,
            container=self.panel
        )
        self.undo_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10 + (btn_w + gap) * 2, btn_y, 80, 36),
            text="Undo",
            manager=self.ui_manager,
            container=self.panel
        )
        self.redo_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10 + (btn_w + gap) * 2 + 90, btn_y, 80, 36),
            text="Redo",
            manager=self.ui_manager,
            container=self.panel
        )

        # Error bar
        error_y = btn_y + 44
        self.error_box = pygame_gui.elements.UITextBox(
            html_text="<font face='monospace' size=2 color='#00FF00'>No errors.</font>",
            relative_rect=pygame.Rect(10, error_y, pw - 20, 28),
            manager=self.ui_manager,
            container=self.panel
        )

    # ------------------------------------------------------------------
    # Open / close
    # ------------------------------------------------------------------

    def open(self, filepath: str, template: str = "") -> None:
        """
        Open a file in the editor.

        Args:
            filepath: Path to .py or .json file
            template: Pre-fill template if file does not exist
        """
        self.current_file = filepath
        self.active = True
        self.error_message = None
        self._undo_stack.clear()
        self._redo_stack.clear()

        # Load content
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                content = f"# Error loading file: {e}\n{template}"
        else:
            content = template

        self._lines = content.splitlines()
        if not self._lines:
            self._lines = [""]
        self._cursor_line = len(self._lines) - 1

        # Show current line in entry
        self.line_entry.set_text(self._lines[self._cursor_line])

        # Update title
        self.title_label.set_text(f"Code Editor — {os.path.basename(filepath)}")

        self._refresh_display()
        self._update_error_bar()
        self.panel.show()

    def close(self) -> None:
        """Close the editor."""
        self.active = False
        self.current_file = None
        self.panel.hide()

    # ------------------------------------------------------------------
    # Save
    # ------------------------------------------------------------------

    def save(self) -> bool:
        """
        Validate and save the current buffer to disk.

        Returns:
            True if saved successfully
        """
        if not self.current_file:
            return False

        # Commit current entry line into buffer
        self._commit_current_line()

        content = "\n".join(self._lines)

        # Only validate .py files
        if self.current_file.endswith('.py'):
            from scripting.validator import ScriptValidator
            validator = ScriptValidator()
            is_valid, error = validator.validate(content)
            if not is_valid:
                self.error_message = validator.get_human_readable_error(error)
                self._update_error_bar()
                return False

        try:
            os.makedirs(os.path.dirname(self.current_file), exist_ok=True)
            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(content)

            self.error_message = None
            self._update_error_bar()

            if self.on_save:
                self.on_save(self.current_file)

            return True

        except Exception as e:
            self.error_message = f"Save error: {e}"
            self._update_error_bar()
            return False

    # ------------------------------------------------------------------
    # Undo / Redo
    # ------------------------------------------------------------------

    def _push_undo(self) -> None:
        """Push current lines onto undo stack."""
        self._undo_stack.append(list(self._lines))
        self._redo_stack.clear()

    def undo(self) -> None:
        """Undo last change."""
        if self._undo_stack:
            self._redo_stack.append(list(self._lines))
            self._lines = self._undo_stack.pop()
            self._cursor_line = min(self._cursor_line, len(self._lines) - 1)
            self.line_entry.set_text(self._lines[self._cursor_line])
            self._refresh_display()

    def redo(self) -> None:
        """Redo last undone change."""
        if self._redo_stack:
            self._undo_stack.append(list(self._lines))
            self._lines = self._redo_stack.pop()
            self._cursor_line = min(self._cursor_line, len(self._lines) - 1)
            self.line_entry.set_text(self._lines[self._cursor_line])
            self._refresh_display()

    # ------------------------------------------------------------------
    # Display refresh
    # ------------------------------------------------------------------

    def _commit_current_line(self) -> None:
        """Write the entry widget's text back into the line buffer."""
        text = self.line_entry.get_text()
        if self._cursor_line < len(self._lines):
            self._lines[self._cursor_line] = text

    def _refresh_display(self) -> None:
        """Re-render the code display box with syntax-highlighted content."""
        content = "\n".join(self._lines)

        try:
            # Pygments HTML highlighting
            formatter = HtmlFormatter(
                nowrap=True,
                style='monokai',
                noclasses=True
            )
            highlighted = highlight(content, PythonLexer(), formatter)

            # Wrap in monospace font tag
            html = f"<font face='monospace' size=3>{highlighted}</font>"
        except Exception:
            # Fallback: plain text
            safe = content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            html = f"<font face='monospace' size=3>{safe}</font>"

        try:
            self.display_box.kill()
            display_h = int(self.screen_height * 0.85) - 170
            pw = int(self.screen_width * 0.82)
            self.display_box = pygame_gui.elements.UITextBox(
                html_text=html,
                relative_rect=pygame.Rect(10, 44, pw - 20, display_h),
                manager=self.ui_manager,
                container=self.panel
            )
        except Exception as e:
            print(f"Code editor display refresh error: {e}")

    def _update_error_bar(self) -> None:
        """Update the error bar with current error state."""
        if self.error_message:
            safe = (
                self.error_message
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )
            html = f"<font face='monospace' size=2 color='#FF4444'>{safe}</font>"
        else:
            html = "<font face='monospace' size=2 color='#00FF00'>No errors.</font>"

        try:
            self.error_box.kill()
            pw = int(self.screen_width * 0.82)
            ph = int(self.screen_height * 0.85)
            display_h = ph - 170
            entry_y = 44 + display_h + 6
            btn_y = entry_y + 44
            error_y = btn_y + 44

            self.error_box = pygame_gui.elements.UITextBox(
                html_text=html,
                relative_rect=pygame.Rect(10, error_y, pw - 20, 28),
                manager=self.ui_manager,
                container=self.panel
            )
        except Exception as e:
            print(f"Error bar update error: {e}")

    # ------------------------------------------------------------------
    # Event handling
    # ------------------------------------------------------------------

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle events for the code editor.

        Args:
            event: pygame event

        Returns:
            True if event was consumed
        """
        if not self.active:
            return False

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.save_button:
                self.save()
                return True
            if event.ui_element == self.close_button:
                self.close()
                return True
            if event.ui_element == self.undo_button:
                self.undo()
                return True
            if event.ui_element == self.redo_button:
                self.redo()
                return True

        if event.type == pygame.KEYDOWN:
            mods = pygame.key.get_mods()

            # Ctrl+S — save
            if event.key == pygame.K_s and (mods & pygame.KMOD_CTRL):
                self.save()
                return True

            # Ctrl+Z — undo
            if event.key == pygame.K_z and (mods & pygame.KMOD_CTRL):
                self.undo()
                return True

            # Ctrl+Y — redo
            if event.key == pygame.K_y and (mods & pygame.KMOD_CTRL):
                self.redo()
                return True

            # Enter — commit line, move to new line
            if event.key == pygame.K_RETURN:
                self._push_undo()
                self._commit_current_line()
                self._cursor_line += 1
                self._lines.insert(self._cursor_line, "")
                self.line_entry.set_text("")
                self._refresh_display()
                return True

            # Up arrow — move to previous line
            if event.key == pygame.K_UP:
                if self._cursor_line > 0:
                    self._commit_current_line()
                    self._cursor_line -= 1
                    self.line_entry.set_text(self._lines[self._cursor_line])
                    self._refresh_display()
                return True

            # Down arrow — move to next line
            if event.key == pygame.K_DOWN:
                if self._cursor_line < len(self._lines) - 1:
                    self._commit_current_line()
                    self._cursor_line += 1
                    self.line_entry.set_text(self._lines[self._cursor_line])
                    self._refresh_display()
                return True

            # Backspace on empty line — delete line
            if event.key == pygame.K_BACKSPACE:
                current_text = self.line_entry.get_text()
                if current_text == "" and len(self._lines) > 1:
                    self._push_undo()
                    self._lines.pop(self._cursor_line)
                    self._cursor_line = max(0, self._cursor_line - 1)
                    self.line_entry.set_text(self._lines[self._cursor_line])
                    self._refresh_display()
                    return True

        return False

    # ------------------------------------------------------------------
    # Template generation
    # ------------------------------------------------------------------

    def get_template(self, context: str, name: str = "") -> str:
        """
        Return a starter code template for the given context.

        Args:
            context: 'entity', 'tile', or 'item'
            name: Name to embed in the template header

        Returns:
            Template source code string
        """
        if context == "entity":
            return (
                f"# Behavior script for: {name}\n"
                "# Type: Entity\n"
                "# Press H in-game to see all available API functions\n\n"
                "def on_spawn(self):\n"
                "    pass\n\n"
                "def on_update(self, dt):\n"
                "    pass\n\n"
                "def on_interact(self, player):\n"
                "    pass\n\n"
                "def on_death(self):\n"
                "    pass\n"
            )

        if context == "tile":
            return (
                f"# Behavior script for tile type: {name}\n"
                "# Press H in-game to see all available API functions\n\n"
                "def on_walk(self, entity):\n"
                "    pass\n\n"
                "def on_enter(self, entity):\n"
                "    pass\n\n"
                "def on_exit(self, entity):\n"
                "    pass\n\n"
                "def on_interact(self, entity):\n"
                "    pass\n\n"
                "def on_tick(self, dt):\n"
                "    pass\n\n"
                "def on_place(self):\n"
                "    pass\n\n"
                "def on_destroy(self):\n"
                "    pass\n"
            )

        if context == "item":
            return (
                f"# Behavior script for item: {name}\n"
                "# Press H in-game to see all available API functions\n\n"
                "def on_pickup(self, player):\n"
                "    pass\n\n"
                "def on_drop(self, player):\n"
                "    pass\n\n"
                "def on_use(self, player):\n"
                "    pass\n\n"
                "def on_equip(self, player):\n"
                "    pass\n\n"
                "def on_tick(self, player, dt):\n"
                "    pass\n"
            )

        return "# New script\n"
