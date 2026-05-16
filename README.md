# BuildMe

A top-down 2D sandbox building game written in Python using `pygame-ce` and `pygame_gui`.

BuildMe focuses on:
- tile-based world building
- editable sandbox worlds
- entity spawning
- world saving/loading
- build mode editing
- customizable tile systems
- expandable maps
- live in-game editing foundations

---

# Features

## Current Working Features

### World System
- Create worlds from the main menu
- Load existing worlds
- Delete saved worlds
- Automatic JSON world persistence
- Auto-save support
- Expandable tile maps

### Tile System
- Grid-based tile placement
- Multiple tile types
- Tile deletion
- Tile inspection
- Tile selection mode
- Solid and non-solid tiles
- Movement modifiers
- Tile map expansion

### Build Mode
Press `B` to enter build mode.

Available editor modes:
- Place
- Delete
- Inspect
- Select

### Entity System
- Spawn NPCs
- Spawn enemies
- Entity serialization
- Basic entity editing
- Collision support
- Player movement

### UI System
- Main menu
- World list
- In-game HUD
- Popup dialogs
- Build UI
- Tile palette
- Basic pygame_gui integration

### Rendering
- Camera movement
- Tile rendering
- Grid rendering
- Entity rendering
- Basic culling optimization

### File Structure
- Modular engine architecture
- Separate systems for world, UI, entities, editor, and rendering

---

# Requirements

- Python 3.9+
- pygame-ce
- pygame_gui

Install dependencies:

```bash
pip install -r requirements.txt
```

Or manually:

```bash
pip install pygame-ce pygame_gui
```

---

# Running The Game

```bash
cd BuildMe
python3 main.py
```

---

# Controls

## Movement

| Key | Action |
|------|--------|
| W A S D | Move player |

## General

| Key | Action |
|------|--------|
| B | Toggle build mode |
| ESC | Exit menus / quit |

## Build Mode

| Key | Action |
|------|--------|
| 1 | Place mode |
| 2 | Delete mode |
| 3 | Inspect mode |
| 4 | Select mode |
| E | Entity editor |
| Left Click | Use active tool |

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
│   └── renderer.py
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
│   └── entity_editor.py
│
├── ui/
│   └── main_menu.py
│
└── worlds/
```

---

# Current Limitations

These systems are still incomplete or planned:

- fully responsive window resizing
- inventory UI
- hotbar/block selection navigation
- advanced scripting tools
- multiplayer
- optimized chunk rendering
- animation system
- crafting system
- audio system
- mobile support

---

# Known Issues

## Linux ALSA Warnings

Some Linux systems display ALSA warnings when launching pygame:

```text
ALSA lib ...
```

These warnings are harmless and do not affect gameplay.

## Window Resize Behavior

The game window is marked resizable, but dynamic UI/layout resizing is still under development.

---

# Development Goals

Planned future systems:

- inventory and hotbar
- drag-and-drop blocks
- scripting API
- in-game code editor
- advanced entity AI
- procedural generation
- custom sprites
- chunk streaming
- lighting system
- crafting and resources
- multiplayer support

---

# License

This project is currently experimental and under active development.
