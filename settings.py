# =============================================================================
# File: sandbox_game/settings.py
# =============================================================================
"""
Global settings and constants for the sandbox game.
All values are defined here to prevent hardcoding throughout the project.
"""

# Screen settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
GAME_TITLE = "Build Me - Programmable Sandbox Game"

# Tile settings
TILE_SIZE = 64
DEFAULT_GRID_WIDTH = 10
DEFAULT_GRID_HEIGHT = 10

# Player settings
PLAYER_SIZE = 48
PLAYER_SPEED = 200  # pixels per second
PLAYER_COLOR = (0, 150, 255)

# Camera settings
CAMERA_LERP_SPEED = 5.0

# Colors
COLORS = {
    'background': (30, 30, 40),
    'grid_line': (60, 60, 70),
    'floor': (100, 100, 100),
    'wall': (80, 50, 30),
    'water': (50, 100, 200),
    'void': (20, 20, 30),
    'player': (0, 150, 255),
    'white': (255, 255, 255),
    'black': (0, 0, 0),
    'red': (255, 50, 50),
    'green': (50, 255, 50),
    'blue': (50, 50, 255),
    'yellow': (255, 255, 50),
    'hud_bg': (20, 20, 30),
    'health_bar': (200, 50, 50),
    'health_bar_bg': (60, 20, 20),
}

# Default tile types
DEFAULT_TILE_TYPES = {
    'floor': {
        'is_solid': False,
        'movement_modifier': 1.0,
        'color': (100, 100, 100),
    },
    'wall': {
        'is_solid': True,
        'movement_modifier': 0.0,
        'color': (80, 50, 30),
    },
    'water': {
        'is_solid': False,
        'movement_modifier': 0.5,
        'color': (50, 100, 200),
    },
    'void': {
        'is_solid': True,
        'movement_modifier': 0.0,
        'color': (20, 20, 30),
    },
}

# -------------------------------------------------------------------------
# Keybindings — action: pygame key constant (int)
# These are the defaults. Runtime overrides are saved to settings.json.
# -------------------------------------------------------------------------
import pygame

KEYBINDINGS = {
    'move_up':      pygame.K_w,
    'move_down':    pygame.K_s,
    'move_left':    pygame.K_a,
    'move_right':   pygame.K_d,
    'build_mode':   pygame.K_b,
    'interact':     pygame.K_f,
    'inventory':    pygame.K_TAB,
    'console':      pygame.K_BACKQUOTE,
    'help':         pygame.K_h,
    'menu':         pygame.K_ESCAPE,
    'entity_editor':pygame.K_e,
    'sub_place':    pygame.K_1,
    'sub_delete':   pygame.K_2,
    'sub_inspect':  pygame.K_3,
    'sub_select':   pygame.K_4,
}

# -------------------------------------------------------------------------
# Global game-rule toggles (saved to global settings.json)
# -------------------------------------------------------------------------
GAME_RULES = {
    'health_system':    True,
    'inventory_system': True,
    'build_mode':       True,
    'entity_spawning':  True,
}

# -------------------------------------------------------------------------
# Global display / audio defaults
# -------------------------------------------------------------------------
GLOBAL_SETTINGS = {
    'fullscreen':        False,
    'target_fps':        60,
    'mobile_controls':   False,
    'dpad_size':         80,
    'action_btn_size':   64,
    'volume':            1.0,
    'font_scale':        1.0,
    'ui_theme':          'default',
}
