# =============================================================================
# File: sandbox_game/editor/file_editor.py
# =============================================================================
"""
In-game source file browser and editor with backup system.
"""

import os
import shutil
import datetime
import pygame
import pygame_gui
from typing import Optional, List
from editor.code_editor import CodeEditor
import settings

RESTART_REQUIRED = {"main.py", "settings.py"}
EXCLUDED = {"__pycache__", ".git", "backups"}


class FileEditor:
    """
    In-game file browser and editor for all project source files.
    Creates timestamped backups before every save.
    """

    def __init__(self, ui_manager: pygame_gui.UIManager):
        """
        Initialize file editor.

        Args:
            ui_manager: pygame_gui UIManager instance
        """
        self.ui_manager = ui_manager
        self.active = False
        self.current_file: Optional[str] = None
        self._file_tree: List[str] = []

        self.code_editor = CodeEditor(ui_manager)
        self.code_editor.on_save = self._on_code_saved

        sw = settings.SCREEN_WIDTH
        sh = settings.SCREEN_HEIGHT

        pw = int(sw * 0.88)
        ph = int(sh * 0.86)
        px = (sw - pw) // 2
        py = (sh - ph) // 2

        self.panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(px, py, pw, ph),
            manager=ui_manager
        )
        self.panel.hide()

        self.title_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 8, pw - 20, 28),
            text="File Editor — Project Source Browser",
            manager=ui_manager,
            container=self.panel
        )

        self.warning_box = pygame_gui.elements.UITextBox(
            html_text=(
                "<font size=3 color='#FFD700'>"
                "⚠  Editing source files can break the game. "
                "A backup is created in backups/ before every save."
                "</font>"
            ),
            relative_rect=pygame.Rect(10, 44, pw - 20, 32),
            manager=ui_manager,
            container=self.panel
        )

        tree_w = int(pw * 0.28)
        tree_h = ph - 130

        self.file_list = pygame_gui.elements.UISelectionList(
            relative_rect=pygame.Rect(10, 84, tree_w, tree_h),
            item_list=[],
            manager=ui_manager,
            container=self.panel
        )

        self.open_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, 84 + tree_h + 6, tree_w, 32),
            text="Open Selected",
            manager=ui_manager,
            container=self.panel
        )

        self.restore_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, 84 + tree_h + 44, tree_w, 32),
            text="Restore Backup",
            manager=ui_manager,
            container=self.panel
        )

        self.close_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(pw - 110, ph - 44, 100, 36),
            text="Close",
            manager=ui_manager,
            container=self.panel
        )

        backup_x = tree_w + 20
        self.backup_list = pygame_gui.elements.UISelectionList(
            relative_rect=pygame.Rect(backup_x, 84, pw - backup_x - 10, tree_h),
            item_list=[],
            manager=ui_manager,
            container=self.panel
        )
        self.backup_list.hide()

        self.restore_confirm_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(backup_x, 84 + tree_h + 6, 160, 32),
            text="Restore Selected",
            manager=ui_manager,
            container=self.panel
        )
        self.restore_confirm_button.hide()

        self.backup_cancel_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(backup_x + 170, 84 + tree_h + 6, 120, 32),
            text="Cancel",
            manager=ui_manager,
            container=self.panel
        )
        self.backup_cancel_button.hide()

        self._showing_backups = False

    def show(self) -> None:
        """Show the file editor and populate the file tree."""
        self.active = True
        self._populate_file_tree()
        self.panel.show()

    def hide(self) -> None:
        """Hide the file editor and close any open code editor."""
        self.active = False
        self.panel.hide()
        if self.code_editor.active:
            self.code_editor.close()

    def toggle(self) -> None:
        """Toggle file editor visibility."""
        if self.active:
            self.hide()
        else:
            self.show()

    def _populate_file_tree(self) -> None:
        """Walk the project directory and build the file list."""
        root = os.path.abspath(".")
        self._file_tree = []

        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [
                d for d in dirnames
                if d not in EXCLUDED and not d.startswith('.')
            ]
            rel_dir = os.path.relpath(dirpath, root)

            for filename in sorted(filenames):
                if not filename.endswith(('.py', '.json', '.txt', '.md')):
                    continue
                if filename.startswith('.'):
                    continue
                rel_path = os.path.join(rel_dir, filename)
                self._file_tree.append(rel_path)

        self.file_list.set_item_list(self._file_tree)

    def _open_selected_file(self) -> None:
        """Open the currently selected file in the code editor."""
        selected = self.file_list.get_single_selection()
        if not selected:
            return

        abs_path = os.path.abspath(selected)
        self.current_file = abs_path

        self.panel.hide()
        self.code_editor.open(abs_path)

        filename = os.path.basename(abs_path)
        if filename in RESTART_REQUIRED:
            self.code_editor.error_message = (
                f"Warning: '{filename}' requires a game restart to take effect."
            )
            self.code_editor._update_error_bar()

    def _create_backup(self, filepath: str) -> Optional[str]:
        """
        Create a timestamped backup of a file.

        Args:
            filepath: Absolute path of file to back up

        Returns:
            Backup path or None if backup failed
        """
        try:
            backup_dir = os.path.join(os.path.abspath("."), "backups")
            os.makedirs(backup_dir, exist_ok=True)

            filename = os.path.basename(filepath)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{filename}.{timestamp}.bak"
            backup_path = os.path.join(backup_dir, backup_name)

            shutil.copy2(filepath, backup_path)
            return backup_path

        except Exception as e:
            print(f"Backup creation error: {e}")
            return None

    def _show_backup_list(self) -> None:
        """Show available backups for the current file."""
        if not self.current_file:
            return

        filename = os.path.basename(self.current_file)
        backup_dir = os.path.join(os.path.abspath("."), "backups")

        backups = []
        if os.path.exists(backup_dir):
            for f in sorted(os.listdir(backup_dir), reverse=True):
                if f.startswith(filename) and f.endswith('.bak'):
                    backups.append(f)

        if not backups:
            backups = ["No backups found for this file."]

        self.backup_list.set_item_list(backups)
        self._showing_backups = True
        self.backup_list.show()
        self.restore_confirm_button.show()
        self.backup_cancel_button.show()

    def _restore_selected_backup(self) -> None:
        """Restore the selected backup over the current file."""
        selected = self.backup_list.get_single_selection()
        if not selected or selected == "No backups found for this file.":
            return

        backup_path = os.path.join(os.path.abspath("."), "backups", selected)
        if not os.path.exists(backup_path):
            return

        try:
            shutil.copy2(backup_path, self.current_file)
            self._hide_backup_list()
            self.code_editor.open(self.current_file)
        except Exception as e:
            print(f"Restore error: {e}")

    def _hide_backup_list(self) -> None:
        """Hide the backup list panel."""
        self._showing_backups = False
        self.backup_list.hide()
        self.restore_confirm_button.hide()
        self.backup_cancel_button.hide()

    def _on_code_saved(self, filepath: str) -> None:
        """
        Called by embedded code editor when Ctrl+S is pressed.

        Args:
            filepath: Path that was saved
        """
        self._create_backup(filepath)
        print(f"[FileEditor] Saved and backed up: {filepath}")
        self.panel.show()

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle UI events.

        Args:
            event: pygame event

        Returns:
            True if event was consumed
        """
        if self.code_editor.active:
            return self.code_editor.handle_event(event)

        if not self.active:
            return False

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.close_button:
                self.hide()
                return True
            if event.ui_element == self.open_button:
                self._open_selected_file()
                return True
            if event.ui_element == self.restore_button:
                self._show_backup_list()
                return True
            if event.ui_element == self.restore_confirm_button:
                self._restore_selected_backup()
                return True
            if event.ui_element == self.backup_cancel_button:
                self._hide_backup_list()
                return True

        if event.type == pygame_gui.UI_SELECTION_LIST_DOUBLE_CLICKED_SELECTION:
            if event.ui_element == self.file_list:
                self._open_selected_file()
                return True

        return False

    def update(self, dt: float) -> None:
        """Update embedded code editor."""
        pass
