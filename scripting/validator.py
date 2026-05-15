# =============================================================================
# File: sandbox_game/scripting/validator.py
# =============================================================================
"""
Script validation using AST parsing for safe execution.
"""

import ast
from typing import Tuple, Optional


class ScriptValidator:
    """
    Validates behavior scripts before execution using AST parsing.
    Prevents dangerous operations from running inside the sandbox.
    """

    # Disallowed node types — ast.Exec was Python 2 only, not present in 3.9+
    DISALLOWED_NODES = {
        ast.Import,
        ast.ImportFrom,
        ast.Global,
        ast.Nonlocal,
    }

    # Disallowed function names that could escape the sandbox
    DISALLOWED_CALLS = {
        'eval', 'exec', 'compile', '__import__',
        'open', 'input', 'memoryview', 'breakpoint'
    }

    def __init__(self):
        """Initialize validator."""
        pass

    def validate(self, script_code: str) -> Tuple[bool, Optional[str]]:
        """
        Validate script code via AST parsing before execution.

        Args:
            script_code: Python source code string

        Returns:
            Tuple of (is_valid, error_message_or_None)
        """
        if not script_code or not script_code.strip():
            return True, None

        try:
            tree = ast.parse(script_code)
        except SyntaxError as e:
            return False, f"Syntax error on line {e.lineno}: {e.msg}"
        except Exception as e:
            return False, f"Parse error: {str(e)}"

        # Walk every node in the AST
        for node in ast.walk(tree):
            # Disallowed statement types
            if type(node) in self.DISALLOWED_NODES:
                return False, f"Disallowed operation: {type(node).__name__}"

            # Disallowed function calls
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in self.DISALLOWED_CALLS:
                        return False, f"Disallowed function call: {node.func.id}()"
                # Disallow dunder attribute access like obj.__class__
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr.startswith('__'):
                        return False, f"Disallowed dunder access: {node.func.attr}"

            # Disallow dunder attribute access on any node
            if isinstance(node, ast.Attribute):
                if node.attr.startswith('__'):
                    return False, f"Disallowed dunder attribute: {node.attr}"

        return True, None

    def get_human_readable_error(self, error_message: str) -> str:
        """
        Convert a technical error string into a user-friendly message.

        Args:
            error_message: Raw error string

        Returns:
            Human-readable error string
        """
        if not error_message:
            return "Unknown error."

        if "Syntax error" in error_message:
            return f"{error_message}\nCheck for missing colons, quotes, or incorrect indentation."

        if "Disallowed operation: Import" in error_message:
            return "Import statements are not allowed in behavior scripts.\nUse the built-in API functions instead."

        if "Disallowed function call" in error_message:
            return f"{error_message}\nThis function is not available in the script sandbox."

        if "Disallowed dunder" in error_message:
            return f"{error_message}\nDirect access to double-underscore attributes is not permitted."

        return error_message
