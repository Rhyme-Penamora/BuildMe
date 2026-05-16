# BuildMe

BuildMe is a 2D sandbox building game written in Python using `pygame-ce` and `pygame_gui`.

The project combines:
- tile-based world editing
- sandbox world management
- entity spawning
- in-game editors
- UI tools
- scripting-related systems
- modular game architecture

The repository is currently under active development.

---

# Overview

BuildMe starts from a main menu where worlds can be created, loaded, and deleted.

Inside a world, the player can:
- move around the map
- enter build mode
- place and delete tiles
- inspect map tiles
- spawn entities
- open various editor panels
- interact with sandbox systems

The project is structured around separate systems for rendering, world management, UI, entities, editing tools, and scripting.

---

# Requirements

## Python

- Python 3.9 or newer

## Dependencies

Install dependencies with:

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install pygame-ce pygame_gui
```

---

# Running The Game

From the repository root:

```bash
cd BuildMe
python3 main.py
```

On some Linux systems, ALSA warnings may appear during startup:

```text
ALSA lib ...
```

These warnings are common with pygame audio initialization and do not necessarily indicate a fatal problem.

---

# Main Menu

The main menu is responsible for world management.

Current functionality includes:
- creating worlds
- loading worlds
- deleting worlds
- displaying saved world lists

World data is stored inside the `worlds/` directory.

---

# Gameplay

## Player Movement

The player moves in a top-down environment.

### Controls

| Key | Action |
|------|--------|
| W | Move Up |
| A | Move Left |
| S | Move Down |
| D | Move Right |

The camera follows the player position.

---

# Build Mode

Build mode allows direct editing of the tile map.

Press:

```text
B
```

to toggle build mode.

When active, the tile editor UI becomes available.

## Build Mode Controls

| Key | Action |
|------|--------|
| 1 | Place Mode |
| 2 | Delete Mode |
| 3 | Inspect Mode |
| 4 | Select Mode |
| Left Click | Use Current Tool |
| Mouse Wheel | Cycle Tile Types |
| [ | Previous Tile |
| ] | Next Tile |
| E | Open Entity Editor |

---

# Tile Editing

The tile editor supports:
- tile placement
- tile deletion
- tile inspection
- tile selection
- tile palette UI
- tile map expansion hooks

The editor reads tile definitions from `settings.DEFAULT_TILE_TYPES`.

Tile data includes:
- tile type
- collision state
- movement modifiers
- color data

## Place Mode

Places the currently selected tile.

## Delete Mode

Replaces tiles with the default floor tile.

## Inspect Mode

Prints tile information to the terminal.

## Tile Cycling

Available tile types can be cycled using:
- mouse wheel
- `[` key
- `]` key

The selected tile is displayed through build mode feedback.

---

# Entity Editor

The entity editor is used for spawning entities into the world.

Press:

```text
E
```

while in build mode to open the entity editor.

## Current Entity Types

The repository currently includes:
- NPC entities
- Enemy entities
- Player entity

## Entity Editor Controls

| Key | Action |
|------|--------|
| Mouse Wheel | Cycle Entity Types |
| [ | Previous Entity |
| ] | Next Entity |
| Left Click | Spawn Selected Entity |

Entity spawning currently supports:
- NPC spawning
- Enemy spawning
- grid-aligned placement
- world bounds checking

---

# HUD

The game contains an in-game HUD system.

Current HUD functionality includes:
- mode display
- world display
- player position display
- health display
- selected tile display
- control hints

The HUD dynamically updates during gameplay.

---

# UI Systems

The repository contains multiple UI systems and editor panels.

Existing UI-related modules include:

- Main Menu
- HUD
- Game Menu
- Settings Menu
- Developer Console
- Help Panel
- Tutorial System
- Popup System
- Player Customization Panel
- Tile Type Manager
- Item Type Manager
- Mobile Controls

Some systems may still be incomplete or experimental.

---

# Scripting Systems

The repository contains scripting-related modules.

Included scripting systems:
- scripting API
- sandbox module
- validator module
- hot reload manager

The README only documents their presence in the repository and does not assume all scripting features are fully implemented.

---

# Inventory And Item Systems

The repository includes:
- inventory editor modules
- item registry systems
- item type management systems

Implementation completeness may vary between systems.

---

# World System

The world system includes:
- world loading
- world saving
- auto-save support
- world metadata
- tile map management
- entity persistence

World-related modules include:
- `world.py`
- `tile.py`
- `tile_map.py`
- `world_manager.py`

---

# Rendering System

The rendering system handles:
- tile rendering
- entity rendering
- grid rendering
- camera offset rendering
- tile hover highlighting
- resize-aware culling

The renderer dynamically reads the active window size.

---

# Window Resizing

The game window is configured as resizable.

Current resize-related functionality includes:
- runtime resize handling
- dynamic HUD scaling
- dynamic renderer updates
- UI manager resolution updates

Some UI layouts may still require additional polish.

---

# Project Structure

```text
BuildMe/
├── main.py
├── settings.py
├── requirements.txt
│
├── core/
│   ├── game.py
│   ├── renderer.py
│   ├── input_handler.py
│   ├── event_bus.py
│   └── hot_reload.py
│
├── world/
│   ├── world.py
│   ├── tile.py
│   ├── tile_map.py
│   └── world_manager.py
│
├── entities/
│   ├── entity.py
│   ├── player.py
│   ├── npc.py
│   └── enemy.py
│
├── editor/
│   ├── tile_editor.py
│   ├── entity_editor.py
│   ├── code_editor.py
│   ├── inventory_editor.py
│   ├── sprite_editor.py
│   └── file_editor.py
│
├── ui/
│   ├── hud.py
│   ├── main_menu.py
│   ├── game_menu.py
│   ├── settings_menu.py
│   ├── developer_console.py
│   ├── help_panel.py
│   ├── tutorial.py
│   ├── popup.py
│   └── player_customize.py
│
├── scripting/
├── inventory/
└── worlds/
```

---

# Current State Of The Project

BuildMe is still actively evolving.

Some systems are functional and playable, while others appear to be partially implemented, experimental, or under development.

This README intentionally avoids claiming features that could not be verified directly from the repository structure and accessible source files.

---

# License

This project is currently experimental and under active development.
