# =============================================================================
# File: sandbox_game/scripting/sandbox.py
# =============================================================================
"""
Sandboxed execution environment for behavior scripts.
"""

from typing import Dict, Any


class ScriptSandbox:
    """
    Provides restricted globals for safe script execution.
    """
    
    def __init__(self, api):
        """
        Initialize sandbox with API.
        
        Args:
            api: ScriptingAPI instance
        """
        self.api = api
    
    def get_safe_globals(self) -> Dict[str, Any]:
        """
        Get dictionary of safe globals for script execution.
        
        Returns:
            Dictionary of allowed globals
        """
        # Safe built-ins
        safe_builtins = {
            'abs': abs,
            'all': all,
            'any': any,
            'bool': bool,
            'dict': dict,
            'enumerate': enumerate,
            'float': float,
            'int': int,
            'len': len,
            'list': list,
            'max': max,
            'min': min,
            'print': print,
            'range': range,
            'round': round,
            'sorted': sorted,
            'str': str,
            'sum': sum,
            'tuple': tuple,
            'zip': zip,
            'True': True,
            'False': False,
            'None': None,
        }
        
        # API functions
        api_functions = {
            'move_toward': self.api.move_toward,
            'distance': self.api.distance,
            'deal_damage': self.api.deal_damage,
            'heal': self.api.heal,
            'get_player': self.api.get_player,
            'spawn_entity': self.api.spawn_entity,
            'destroy_entity': self.api.destroy_entity,
            'open_dialogue': self.api.open_dialogue,
            'play_animation': self.api.play_animation,
            'set_tile': self.api.set_tile,
            'get_tile': self.api.get_tile,
            'log': self.api.log,
            'give_item': self.api.give_item,
            'remove_item': self.api.remove_item,
            'has_item': self.api.has_item,
            'get_inventory': self.api.get_inventory,
            'set_world_background': self.api.set_world_background,
            'set_player_sprite': self.api.set_player_sprite,
            'get_world_setting': self.api.get_world_setting,
            'set_world_setting': self.api.set_world_setting,
        }
        
        # Combine safe builtins and API
        safe_globals = {**safe_builtins, **api_functions}
        
        # Add __builtins__ as empty dict to prevent access to dangerous functions
        safe_globals['__builtins__'] = {}
        
        return safe_globals
