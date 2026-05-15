# =============================================================================
# File: sandbox_game/core/hot_reload.py
# =============================================================================
"""
Hot reload system using watchdog to monitor behavior script changes.
"""

import os
import importlib.util
from typing import Dict, Optional, Callable, Tuple

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class ScriptReloader(FileSystemEventHandler):
    """
    File system event handler for hot reloading scripts.
    """

    def __init__(self, on_script_changed: Callable):
        """
        Initialize script reloader.

        Args:
            on_script_changed: Callback when script changes (receives filepath)
        """
        super().__init__()
        self.on_script_changed = on_script_changed

    def on_modified(self, event):
        """Called by watchdog when a file is modified."""
        if not event.is_directory and event.src_path.endswith('.py'):
            self.on_script_changed(event.src_path)


class HotReloadManager:
    """
    Manages hot reloading of behavior scripts via watchdog file watching.
    """

    def __init__(self):
        """Initialize hot reload manager."""
        self.observer: Optional[Observer] = None
        self.watched_paths: set = set()
        self.loaded_modules: Dict[str, object] = {}

    def start_watching(self, path: str, on_script_changed: Callable) -> None:
        """
        Start watching a directory for script changes.

        Args:
            path: Directory path to watch
            on_script_changed: Callback when script changes
        """
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)

        if path in self.watched_paths:
            return

        if self.observer is None:
            self.observer = Observer()
            self.observer.start()

        event_handler = ScriptReloader(on_script_changed)
        self.observer.schedule(event_handler, path, recursive=True)
        self.watched_paths.add(path)

    def stop_watching(self) -> None:
        """Stop all watchdog observers cleanly."""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
        self.watched_paths.clear()

    def load_script(
        self,
        filepath: str,
        safe_globals: Dict
    ) -> Tuple[bool, Optional[object], Optional[str]]:
        """
        Load a Python script file and return its module object.

        Args:
            filepath: Absolute or relative path to .py script
            safe_globals: Dictionary of allowed globals for exec

        Returns:
            Tuple of (success, module_object, error_message)
        """
        try:
            if not os.path.exists(filepath):
                return False, None, f"Script file not found: {filepath}"

            with open(filepath, 'r') as f:
                script_code = f.read()

            # Validate before executing
            from scripting.validator import ScriptValidator
            validator = ScriptValidator()
            is_valid, error = validator.validate(script_code)

            if not is_valid:
                return False, None, validator.get_human_readable_error(error)

            # Build a fresh module namespace
            module_namespace: Dict = {}

            # Execute script into namespace using safe globals as globals
            exec(compile(script_code, filepath, 'exec'), safe_globals, module_namespace)

            # Wrap namespace in a simple object so callers use attribute access
            class _Module:
                pass

            module = _Module()
            for key, value in module_namespace.items():
                setattr(module, key, value)

            self.loaded_modules[filepath] = module
            return True, module, None

        except Exception as e:
            return False, None, f"Error loading script '{filepath}': {str(e)}"

    def reload_script(
        self,
        filepath: str,
        safe_globals: Dict
    ) -> Tuple[bool, Optional[object], Optional[str]]:
        """
        Reload a previously loaded script file.

        Args:
            filepath: Path to script file
            safe_globals: Dictionary of allowed globals

        Returns:
            Tuple of (success, module_object, error_message)
        """
        # Evict from cache so load_script starts fresh
        if filepath in self.loaded_modules:
            del self.loaded_modules[filepath]

        return self.load_script(filepath, safe_globals)
