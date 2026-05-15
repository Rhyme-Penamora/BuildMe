`
# =============================================================================
# File: sandbox_game/README.md
# =============================================================================

# Build Me — Programmable Sandbox Game Engine

> **"You are not just playing a game. You are building one."**

Build Me is a top-down 2D programmable sandbox game written entirely in Python.
It ships as a blank canvas. Every tile, entity, item, behavior, sprite, UI element,
and even the engine's own source code can be customized and scripted from inside
the game itself — in real time, with no external tools required.

Think Minecraft worlds meets Roblox Studio meets a live Python IDE, all running
inside a single Python application.

---

## Table of Contents

1. [What Is This?](#what-is-this)
2. [Requirements](#requirements)
3. [Installation](#installation)
4. [How To Run](#how-to-run)
5. [Project Structure](#project-structure)
6. [Core Concepts](#core-concepts)
7. [Controls Reference](#controls-reference)
8. [Game Modes](#game-modes)
9. [Build Mode](#build-mode)
10. [Entity System](#entity-system)
11. [Inventory System](#inventory-system)
12. [Scripting System](#scripting-system)
13. [Full Scripting API Reference](#full-scripting-api-reference)
14. [Behavior Script Hooks](#behavior-script-hooks)
15. [Code Editor](#code-editor)
16. [Hot Reload](#hot-reload)
17. [Tile System](#tile-system)
18. [Sprite Customization](#sprite-customization)
19. [World System](#world-system)
20. [Developer Console](#developer-console)
21. [Settings Menu](#settings-menu)
22. [Mobile Controls](#mobile-controls)
23. [Help Panel](#help-panel)
24. [File Editor](#file-editor)
25. [Tutorial Mode](#tutorial-mode)
26. [Player Customization](#player-customization)
27. [Type Managers](#type-managers)
28. [HUD Customization](#hud-customization)
29. [UI Theming](#ui-theming)
30. [Keybinding Remapping](#keybinding-remapping)
31. [Code Templates](#code-templates)
32. [Troubleshooting](#troubleshooting)
33. [Architecture Overview](#architecture-overview)
34. [License](#license)

---

## What Is This?

Build Me is a game engine and sandbox game simultaneously. When you launch it,
you see a blank grid world. From there, you have total control:

- **Place tiles** — floor, wall, water, void, or any custom tile type you define
- **Spawn entities** — NPCs, enemies, or custom entity types you create
- **Script behaviors** — write Python scripts that control how everything acts
- **Edit in real time** — save a script and it reloads in the running game instantly
- **Customize everything** — player stats, sprites, item types, tile types, world settings
- **Edit the engine itself** — open any source `.py` file from inside the game,
  edit it, and hot-reload it (with automatic backup)

There is no separation between "player" and "developer". Every tool is available
at all times from within the game.

---

## Requirements

| Requirement | Version |
|-------------|---------|
| Python | 3.9 or higher |
| pygame-ce | 2.3.2 or higher |
| pygame_gui | 0.6.9 or higher |
| pygments | 2.16.1 or higher |
| watchdog | 3.0.0 or higher |

**Operating Systems:** Windows, macOS, Linux (any OS that runs Python 3.9+)

**Hardware:** Any machine capable of running Python desktop applications.
No GPU required. Runs comfortably on low-end hardware.

---

## Installation

### Step 1 — Install Python 3.9+

Download from https://www.python.org/downloads/
Make sure to check "Add Python to PATH" during installation on Windows.

Verify your installation:
```bash
python --version
```
Expected output: `Python 3.9.x` or higher.

### Step 2 — Install dependencies

```bash
pip install pygame-ce pygame_gui pygments watchdog
```

Or install from the included requirements file:

```bash
pip install -r requirements.txt
```

### Step 3 — Verify installation

```bash
python -c "import pygame; import pygame_gui; import pygments; import watchdog; print('All OK')"
```

Expected output: `All OK`

---

## How To Run

```bash
cd sandbox_game
python main.py
```

That is it. No build step. No compilation. No configuration files required.

On first launch:
1. The main menu appears showing your saved worlds (empty on first run)
2. Click **New World** and enter a name
3. Click **Load World** or double-click the world name
4. The game loads with a blank 10x10 grid

To exit cleanly at any time: press **ESC → Exit to Main Menu**, or close the window.
The world is auto-saved every 60 seconds and on every clean exit.

---

## Project Structure

```
sandbox_game/
│
├── main.py                    # Entry point — menu loop and world loading
├── settings.py                # All global constants, keybindings, game rules
├── requirements.txt           # pip dependencies
├── README.md                  # This file
├── settings.json              # Auto-generated — persisted global settings
│
├── core/
│   ├── game.py                # Main game loop, all system wiring
│   ├── renderer.py            # All draw calls — no game logic here
│   ├── input_handler.py       # Keyboard, mouse, and virtual mobile input
│   ├── hot_reload.py          # watchdog file watcher + importlib reloader
│   └── event_bus.py           # Pub/sub event system for decoupled communication
│
├── world/
│   ├── world.py               # World: tile map + entities + items + metadata
│   ├── tile.py                # Tile class with type, solid, modifier, color, script
│   ├── tile_map.py            # TileMap grid, expand, get/set tile, coordinate conversion
│   └── world_manager.py       # Create, save, load, delete worlds. Auto-save
│
├── entities/
│   ├── entity.py              # Base Entity: id, position, size, color, name
│   ├── player.py              # Player: WASD movement, collision, tile modifiers
│   ├── npc.py                 # NPC: dialogue, on_interact
│   └── enemy.py               # Enemy: health, damage, is_dead, on_update
│
├── editor/
│   ├── code_editor.py         # In-game Python editor: syntax highlight, undo/redo
│   ├── tile_editor.py         # Tile placement, deletion, inspection, selection
│   ├── entity_editor.py       # Entity spawning and configuration
│   ├── sprite_editor.py       # Sprite upload, spritesheet, animations, preview
│   ├── file_editor.py         # Full project file browser + editor + backup system
│   └── inventory_editor.py    # Inventory grid UI, item management
│
├── ui/
│   ├── main_menu.py           # World selection screen
│   ├── hud.py                 # In-game HUD with health bar and toggle support
│   ├── popup.py               # Reusable confirmation dialog
│   ├── help_panel.py          # Tabbed help: API, templates, tutorial, shortcuts
│   ├── game_menu.py           # ESC menu with all options
│   ├── settings_menu.py       # 7-tab settings: display, controls, mobile, rules...
│   ├── mobile_controls.py     # Virtual D-pad, action buttons, FAB menu
│   ├── player_customize.py    # Player name/speed/health/size/sprite editor
│   └── type_managers.py       # Tile type manager + Item type manager
│
├── scripting/
│   ├── api.py                 # Full scripting API implementation
│   ├── sandbox.py             # Restricted execution globals (no os/sys/exec)
│   └── validator.py           # ast.parse() pre-validation with human errors
│
├── inventory/
│   ├── inventory.py           # Inventory: configurable slots, add/remove/swap
│   ├── item.py                # Item: id, name, desc, sprite, stackable, script
│   └── item_registry.py       # Global item type registry, load/save JSON
│
├── worlds/
│   └── [world_name]/
│       ├── world.json         # Tile map + entity list + metadata
│       ├── settings.json      # Per-world settings (auto-save interval etc.)
│       ├── behaviors/
│       │   ├── entities/      # Entity behavior .py scripts
│       │   └── tiles/         # Tile behavior .py scripts
│       ├── items/
│       │   └── items.json     # Item type definitions for this world
│       └── assets/
│           ├── sprites/       # Entity/player sprites
│           ├── tiles/         # Tile sprites
│           ├── backgrounds/   # World background images
│           └── ui/            # UI element images
│
├── assets/
│   └── default/               # Default built-in assets
│
└── backups/                   # Auto-created timestamped backups of source files
```

---

## Core Concepts

### Everything is scriptable

Every entity (NPC, enemy), every tile type, and every item type can have a Python
behavior script attached. Scripts are plain `.py` files stored in the world folder.
They use a safe restricted API — no access to `os`, `sys`, `subprocess`, `open`,
`eval`, or `exec`. Only the scripting API and safe builtins are available.

### Hot reload

When you save a behavior script (via the in-game code editor with `Ctrl+S`),
the `watchdog` file watcher detects the change and reloads the script
immediately — without stopping the game or restarting. The entity continues
running, now with the new behavior.

### Everything persists to JSON

Worlds are saved as JSON files. Tile maps, entities, item definitions, and world
metadata are all serialized to `worlds/[name]/world.json`. Nothing is stored in
memory only.

### Event bus

All systems communicate through a centralized publish/subscribe event bus
(`core/event_bus.py`). Systems subscribe to named events and publish data without
holding direct references to each other. This means systems can be replaced or
extended without breaking others.

---

## Controls Reference

### Movement

| Key | Action |
|-----|--------|
| W | Move up |
| A | Move left |
| S | Move down |
| D | Move right |

Movement speed is modified by the tile you are standing on.
Water tiles slow you to 50% speed. Custom tiles can have any modifier.

### Mode Switching

| Key | Action |
|-----|--------|
| B | Toggle build mode on/off |
| ESC | Open/close game menu |
| Tab | Open/close inventory |
| ` (backtick) | Toggle developer console |
| H | Toggle help panel |

### Build Mode Keys

 | Action |
|-----|--------|
| 1 | Switch to Place sub-mode |
| 2 | Switch to Delete sub-mode |
| 3 | Switch to Inspect sub-mode |
| 4 | Switch to Select sub-mode |
| E | Toggle entity editor |
| Left Click | Act on tile (place/delete/inspect depending on mode) |

### Interaction

| Key | Action |
|-----|--------|
| F | Interact with nearest NPC (within 1.5 tiles) |

### Code Editor (when open)

| Key | Action |
|-----|--------|
| Ctrl+S | Save script and hot-reload |
| Ctrl+Z | Undo |
| Ctrl+Y | Redo |
| Enter | New line |
| Up Arrow | Move to previous line |
| Down Arrow | Move to next line |
| Backspace (on empty line) | Delete line |

All keybindings (except code editor keys) are remappable in Settings → Controls.

---

## Game Modes

### Play Mode (default)

- Player moves with WASD
- Tile movement modifiers apply (water slows, etc.)
- Solid tiles block movement (walls, void)
- Entities run their behavior scripts
- Press F near an NPC to trigger dialogue
- Dialogue appears at bottom of screen for 3 seconds

### Build Mode (press B)

- Tile palette appears on the right side
- Click tiles to place/delete/inspect
- Entity editor available with E
- Sub-modes shown in HUD
- Camera still follows player

Inspect mode and Select mode are mutually exclusive.
Switching to Inspect automatically exits Select and vice versa.

---

## Build Mode

### Sub-modes

**Place** — Left click on any grid cell to place the currently selected tile type.
Select a tile type from the palette panel (right side of screen).

**Delete** — Left click replaces any tile with a floor tile (the default empty tile).

**Inspect** — Left click shows the tile's properties: type, solid flag, movement
modifier, behavior script path (if assigned). From inspect, you can open the
behavior script editor for that tile.

**Select** — Left click begins selection. Drag to select a region.
(Foundation for copy/paste operations in future updates.)

### Tile Palette

The tile palette appears on the right when build mode is active. It shows all
available tile types as clickable buttons. Click to select. The HUD shows the
currently selected tile type at all times.

### Edge Expansion

If you place a tile at the grid boundary, you will be prompted to expand the world
in that direction. The world grows by adding new rows or columns of floor tiles.
The expansion amount is configurable in Settings → World.

---

## Entity System

### Spawning Entities

1. Enter build mode (B)
2. Press E to open the entity editor
3. Select NPC or Enemy from the spawn menu (right side)
4. Left click any tile to spawn the entity at that position

### NPC

- Has a `name` and a `dialogue` list
- Press F near an NPC to trigger `on_interact` — shows first dialogue entry
- Dialogue can be customized via behavior script
- Right-click an NPC in build mode to edit properties

### Enemy

- Has `name`, `health`, `max_health`, `damage`
- `is_dead` flag — dead enemies are removed from the world automatically
- Behavior script's `on_update(self, dt)` runs every frame
- Can use `move_toward`, `deal_damage`, `distance` API calls

### Behavior Scripts

Every entity has an optional `behavior_script` path. This `.py` file is loaded
and hot-reloaded. Functions defined in the script are called by the engine at
the appropriate times. See [Behavior Script Hooks](#behavior-script-hooks).

---

## Inventory System

### Opening Inventory

Press **Tab** to open the inventory grid.
Inventory can be disabled in Settings → Game Rules → Inventory System.

### Default Slots

The default inventory has 20 slots. Slot count is configurable in
Settings → World → Inventory Slot Count.

### Item Operations

- Items added via `giveitem` console command or via scripting API `give_item()`
- Items can be dragged and dropped within the grid
- Items with `stackable: true` stack up to their `max_stack` count
- Removing items via scripting: `remove_item(player, item_id, quantity)`

### Item Properties

Each item type has:

| Property | Type | Description |
|----------|------|-------------|
| id | string | Unique identifier (e.g. "stick") |
| name | string | Display name (e.g. "Stick") |
| description | string | Tooltip text |
| sprite | path or None | Image file path |
| stackable | bool | Whether items of this type stack |
| max_stack | int | Maximum stack size (default 64) |
| custom_properties | dict | Any extra data you want |
| behavior_script | path or None | Script file path |

### Creating Items

Use the console command `openitemmanager` or open the Item Type Manager
from the console. Fill in the fields and click Add/Update.
Items are saved to `worlds/[name]/items/items.json`.

---

## Scripting System

### How It Works

1. In build mode, inspect a tile or entity and click "Edit Behavior"
2. The in-game code editor opens with a template
3. Write your Python behavior using the scripting API
4. Press Ctrl+S to save
5. The script hot-reloads immediately — no restart needed

### Safety Restrictions

Scripts run in a sandboxed environment. The following are **blocked**:

- `import os`
- `import sys`
- `import subprocess`
- `open()` (file access)
- `eval()` and `exec()`
- Any access to the filesystem or network outside the API

The following are **allowed**:

- All scripting API functions (see below)
- Safe builtins: `print`, `len`, `range`, `int`, `float`, `str`, `bool`,
  `list`, `dict`, `tuple`, `abs`, `min`, `max`, `round`, `isinstance`
- Standard math operations

### Validation

Before any script is executed, it is passed through `ast.parse()` for syntax
checking. If the syntax is invalid, a human-readable error is shown in the
red error bar at the bottom of the code editor. The game never crashes
from a script error.

---

## Full Scripting API Reference

All of these functions are available inside any behavior script automatically.
No imports needed.

---

### Entity Movement

```python
move_toward(entity, target, speed)
```
Move `entity` toward `target` at `speed` pixels per second.
`target` can be another entity or a `(x, y)` pixel coordinate tuple.

```python
distance(entity_a, entity_b)
```
Return the pixel distance between two entities as a float.

---

### Combat

```python
deal_damage(target, amount)
```
Deal `amount` integer damage to `target` entity.
Reduces `target.health` by `amount`. Triggers `on_death` if health reaches 0.

```python
heal(target, amount)
```
Heal `target` entity by `amount`. Capped at `target.max_health`.

---

### World Access

```python
get_player()
```
Return the player entity. Returns `None` if no player is loaded.

```python
spawn_entity(entity_type, x, y)
```
Spawn an entity of type `'npc'` or `'enemy'` at grid tile coordinates `(x, y)`.
Returns the newly created entity, or `None` if spawning failed.

```python
destroy_entity(entity)
```
Remove `entity` from the world immediately.

```python
set_tile(x, y, tile_type)
```
Set the tile at grid coordinates `(x, y)` to `tile_type` string.
`tile_type` must be a key in `DEFAULT_TILE_TYPES` (e.g. `'floor'`, `'wall'`).

```python
get_tile(x, y)
```
Return the `Tile` object at grid coordinates `(x, y)`, or `None` if out of bounds.

---

### Dialogue & UI

```python
open_dialogue(text)
```
Display `text` in the dialogue box at the bottom of the screen for 3 seconds.

```python
play_animation(entity, animation_name)
```
Set `entity`'s current animation to `animation_name`.
The animation must be defined in the entity's sprite animation definitions.

```python
log(message)
```
Print `message` to the developer console in cyan. Useful for debugging scripts.

---

### Inventory

```python
give_item(player, item_id, quantity)
```
Add `quantity` of `item_id` to `player`'s inventory.
Returns `True` if successful, `False` if inventory is full or item id unknown.

```python
remove_item(player, item_id, quantity)
```
Remove `quantity` of `item_id` from `player`'s inventory.
Returns `True` if successful, `False` if player does not have enough.

```python
has_item(player, item_id, quantity)
```
Return `True` if `player` has at least `quantity` of `item_id`. Otherwise `False`.

```python
get_inventory(player)
```
Return the player's `Inventory` object for direct slot inspection.

---

### World Settings

```python
get_world_setting(key)
```
Return the value of `key` from the current world's metadata dictionary.

```python
set_world_setting(key, value)
```
Set `key` to `value` in the current world's metadata. Persists on next save.

---

### Visual

```python
set_world_background(image_path)
```
Set the world background to the image at `image_path`. PNG and JPG supported.

```python
set_player_sprite(image_path)
```
Set the player's sprite to the image at `image_path`. PNG and JPG supported.

---

## Behavior Script Hooks

### Entity Hooks

Define any of these functions in an entity behavior script:

```python
def on_spawn(self):
    # Called once when the entity first appears in the world
    pass

def on_update(self, dt):
    # Called every frame. dt = delta time in seconds
    pass

def on_interact(self, player):
    # Called when player presses F near this entity
    pass

def on_death(self):
    # Called when entity health reaches 0
    pass
```

### Tile Hooks

Define any of these functions in a tile behavior script:

```python
def on_walk(self, entity):
    # Called every frame any entity is standing on this tile
    pass

def on_enter(self, entity):
    # Called once when an entity first steps onto this tile
    pass

def on_exit(self, entity):
    # Called once when an entity leaves this tile
    pass

def on_interact(self, entity):
    # Called when player presses F while on this tile
    pass

def on_tick(self, dt):
    # Called every frame regardless of entities (continuous updates)
    pass

def on_place(self):
    # Called when this tile is placed in the world
    pass

def on_destroy(self):
    # Called when this tile is deleted
    pass
```

### Item Hooks

Define any of these functions in an item behavior script:

```python
def on_pickup(self, player):
    # Called when item enters player inventory
    pass

def on_drop(self, player):
    # Called when item is dropped from inventory
    pass

def on_use(self, player):
    # Called when player uses/activates the item
    pass

def on_equip(self, player):
    # Called when item is placed in equipment slot
    pass

def on_tick(self, player, dt):
    # Called every frame while item is in inventory
    pass
```

---

## Code Editor

The in-game code editor is available whenever you open a behavior script,
click "Edit Behavior" in build mode, or open a file from the File Editor.

### Features

- **Syntax highlighting** via Pygments (Monokai color scheme)
- **Line numbers** shown in display
- **Multi-line editing** — navigate with Up/Down arrow keys
- **Undo / Redo** — Ctrl+Z and Ctrl+Y, unlimited history
- **Error bar** — red bar at bottom shows syntax errors before saving
- **Auto-validate** — scripts are parsed with `ast.parse()` before saving
- **Template pre-fill** — new scripts open with the appropriate hook template
  (entity, tile, or item) so you never start from a blank file

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Ctrl+S | Validate, save, and hot-reload |
| Ctrl+Z | Undo last change |
| Ctrl+Y | Redo last undone change |
| Enter | Create new line |
| Up | Go to previous line |
| Down | Go to next line |
| Backspace (empty line) | Delete current line |

### Error Handling

If your script has a syntax error, the error bar shows the exact line number
and error message. The file is NOT saved until errors are fixed.
Runtime errors (logic errors that happen during execution) are caught by the
engine and printed to the console — they never crash the game.

---

## Hot Reload

Hot reload is one of the core features of Build Me.

### How It Works

1. The `watchdog` library watches the `worlds/[name]/behaviors/` directory
2. When any `.py` file changes (saved from code editor or external editor),
   `watchdog` fires a callback immediately
3. The engine uses `importlib` to reload the changed module
4. The new behavior is attached to the matching entity or tile
5. The game continues running — no pause, no restart

### What Gets Reloaded

- Entity behavior scripts (`worlds/[name]/behaviors/entities/`)
- Tile behavior scripts (`worlds/[name]/behaviors/tiles/`)
- Game source files (via File Editor — with restart warning for `main.py`)

### What Does Not Hot-Reload

- `main.py` — requires restart (warning shown in File Editor)
- `settings.py` — requires restart for most changes
- The tile map or entity list — these are data, not scripts

### Triggering Hot Reload

- **From code editor:** Ctrl+S always triggers hot reload on save
- **From external editor:** Save the `.py` file in your OS — watchdog detects it
- **From console:** `reload [entity_id]` forces a reload for a specific entity

---

## Tile System

### Built-in Tile Types

| Type | Solid | Movement | Color |
|------|-------|----------|-------|
| floor | No | 1.0 (full speed) | Gray |
| wall | Yes | 0.0 (blocked) | Brown |
| water | No | 0.5 (half speed) | Blue |
| void | Yes | 0.0 (blocked) | Dark |

### Built-in Tile Behaviors

These behaviors are pre-implemented and can be assigned to any tile:

**damage_on_walk** — Deals configurable damage per second to any entity on tile.
Used for lava. Configure damage amount via tile's `custom_properties`.

**heal_on_walk** — Heals entity while standing on tile.

**slow_on_walk** — Reduces entity movement speed beyond the movement modifier.

**teleport_on_walk** — Teleports entity to a configured destination tile coordinate.

**trigger_on_walk** — Fires a custom event name when walked on.

### Custom Tile Types

Open the Tile Type Manager (console command `opentilemanager`) to:
- View all existing tile types
- Add new custom tile types with any name, solid flag, movement modifier, and color
- Edit existing custom tile types
- Delete custom tile types (built-ins cannot be deleted)

Custom tile types are available immediately in the tile palette and
via the `settile` console command.

### Tile Behavior Scripting

1. In build mode, switch to Inspect (key 3)
2. Click a tile
3. In the inspector popup, click "Edit Behavior"
4. The code editor opens with the tile behavior template
5. Write your script using tile hooks
6. Ctrl+S to save and hot-reload

Or use the console: `settilecode [x] [y]`

---

## Sprite Customization

Every visual element in the game can be replaced with a custom image.

### What Can Be Customized

- Player sprite
- NPC sprites
- Enemy sprites
- Tile appearance (per tile type)
- Item icons
- World background image
- UI elements

### How To Upload a Sprite

1. Open the Sprite Editor from the game menu → Customize Player → Change Sprite,
   or from the entity inspector → Edit Sprite
2. Enter the full path to your PNG or JPG file in the path field
3. Click "Load Image"
4. The image is validated — unsupported formats show a clear error
5. Optionally configure spritesheet grid (columns × rows)
6. Define named animations (name, frame list, FPS, loop on/off)
7. Select what to assign to (Player, Entity, Tile, Item, Background)
8. Click "Assign Sprite"

The image is copied into `worlds/[name]/assets/[category]/` and the path
is stored in the entity or tile data. It persists on world save.

### Spritesheet Setup

If your image is a spritesheet with multiple frames:
1. Enter the number of columns and rows
2. Click "Apply Grid" — frame size is calculated automatically
3. Define animations:
   - **Name:** e.g. "idle", "walk", "attack"
   - **Frames:** comma-separated frame indices e.g. `0,1,2,3`
   - **FPS:** frames per second e.g. `8`
   - **Loop:** ON or OFF
4. Click "Add Animation" for each animation
5. The live preview in the bottom-right shows the animation playing

### Supported Formats

PNG and JPG/JPEG. Other formats are rejected with a clear error message.

### Setting World Background

Via console:
```
setworldbg C:/images/background.png
```

Via sprite editor: assign category "Background".

The background scales to fill the screen. Fallback is the solid background color
defined in `settings.py`.

---

## World System

### Creating a World

On the main menu, click **New World**, enter a name, click **Create**.
The world is saved immediately with a default 10×10 floor grid.

### Loading a World

Click a world in the list and click **Load World**, or double-click the world name.

### Saving a World

- **Auto-save:** every 60 seconds (configurable in Settings → World)
- **Manual save:** ESC → Save World, or console command `save`
- **On exit:** world is saved automatically when you exit to main menu or close window

### Deleting a World

On the main menu, select a world and click **Delete World**.
A confirmation dialog appears. Deletion removes the entire world folder from disk.
This cannot be undone.

### World Data Location

```
worlds/
└── [world_name]/
    ├── world.json         # All tile and entity data
    ├── settings.json      # World-specific settings
    ├── behaviors/         # Behavior scripts
    ├── items/             # Item type definitions
    └── assets/            # Sprites and backgrounds
```

### World Metadata

Each world stores metadata including creation time, last played time,
total play time, background image path, and any custom properties
set via `set_world_setting()` in scripts.

---

## Developer Console

Open and close with the **backtick key** (`` ` ``).

The console shows a scrollable log of messages, errors, and command output.
Type commands in the bottom input field. Press Enter to execute.
Use **Up/Down arrow** keys to navigate command history.

### Full Command Reference

| Command | Description |
|---------|-------------|
| `spawn [type] [x] [y]` | Spawn entity at tile coordinates. Types: npc, enemy |
| `settile [x] [y] [type]` | Set tile type at grid coordinates |
| `tp [x] [y]` | Teleport player to grid coordinates |
| `listentities` | List all entities: type, name, ID, position |
| `reload [entity_id]` | Force reload behavior script for entity (use first chars of ID) |
| `save` | Force save world to disk immediately |
| `clear` | Clear console log |
| `listworlds` | List all saved worlds with last-played date |
| `listcmds` | List all available commands |
| `listitems` | List all items in player inventory |
| `giveitem [id] [qty]` | Add item to player inventory |
| `settilecode [x] [y]` | Open behavior script editor for tile at coordinates |
| `setworldbg [path]` | Set world background image |
| `setplayersprite [path]` | Set player sprite image |
| `opentilemanager` | Open tile type manager panel |
| `openitemmanager` | Open item type manager panel |
| `opencustomize` | Open player customization panel |
| `opensettings` | Open settings menu |
| `help [command]` | Show detailed help for a specific command |

### Command Examples

```
spawn npc 5 5
spawn enemy 3 7
settile 0 0 wall
settile 4 4 water
tp 5 5
listentities
reload ab12ef
giveitem stick 10
settilecode 3 3
setworldbg C:/images/grass.png
setplayersprite C:/images/hero.png
help spawn
```

### Console Colors

| Color | Meaning |
|-------|---------|
| Green | Success |
| Red | Error |
| Yellow | Warning / usage hint |
| Cyan | Hot reload notification |
| White | Information |

---

## Settings Menu

Open from **ESC → Settings** or console command `opensettings`.

### Display Tab

- **Fullscreen toggle** — switches between windowed and fullscreen
- **Target FPS** — change frame rate cap (default 60)
- Resolution is fixed at 1280×720 (scaling support in future update)

### Controls Tab

- Shows all remappable actions with their current key binding
- Click any action button
- Press the new key you want to assign
- The binding updates immediately
- All bindings save to `settings.json` and persist between sessions

### Mobile Tab

- **Toggle virtual controls** — enable/disable the on-screen D-pad and buttons
- **D-pad size** — size in pixels (minimum 48px)
- **Action button size** — size in pixels (minimum 48px)
- Changes apply after clicking Apply

### Game Rules Tab

Toggle each rule on or off. Changes apply immediately to the running game:

- **Health System** — if OFF, player health bar is hidden and damage is disabled
- **Inventory System** — if OFF, Tab key does nothing and inventory is inaccessible
- **Build Mode** — if OFF, B key does nothing and no building is possible
- **Entity Spawning** — if OFF, E key does nothing in build mode

### World Tab (per-world settings)

- **Auto-save interval** — seconds between auto-saves (default 60)
- **World expansion limit** — max tiles the world can grow to in any direction
- **Entity spawn limit** — maximum number of entities allowed in the world
- **Inventory slot count** — number of inventory slots

### Audio Tab

- **Master Volume** slider — prepared for future audio system
- Slider is functional; no audio plays yet

### UI Tab

- **Font scale** — scale factor for all text (0.5 to 3.0)
- **HUD element toggles** — show/hide each HUD element individually
- Theme configuration via `ui_theme.json` (see UI Theming)

---

## Mobile Controls

Enable from **Settings → Mobile → Toggle Mobile Controls** or console `opensettings`.

When enabled, three control groups appear on screen:

### D-pad (bottom-left)

Four directional buttons arranged in a cross:
- ▲ = move up (maps to W key)
- ▼ = move down (maps to S key)
- ◀ = move left (maps to A key)
- ▶ = move right (maps to D key)

Hold any D-pad button for continuous movement.

### Action Buttons (bottom-right)

| Button | Action |
|--------|--------|
| F | Interact with NPC |
| B | Toggle build mode |
| Tab | Open/close inventory |
| ATK | Attack (reserved) |

### FAB Menu (top-right)

The ☰ button expands to a vertical menu:
- **Save** — save world
- **Help** — open help panel
- **Settings** — open settings menu
- **File Editor** — open file editor
- **Exit Menu** — exit to main menu

### Technical Note

All mobile button presses are injected into the same `InputHandler` used by
keyboard input. There is zero duplicate game logic. If you remap a key in settings,
the mobile control for that action automatically uses the new mapping.

### PC Testing

Mobile controls work on PC too. Enable them in settings to test the mobile layout
without needing a touch device.

---

## Help Panel

Press **H** to open the help panel at any time.

### Tab 1: API Reference

Complete reference for every scripting API function:
- Function signature
- Description
- Parameter types
- Return value
- Example usage

### Tab 2: Code Templates

Pre-written, insertable scripts for common patterns:
- Basic Chase Enemy
- Zombie (chase + damage on contact + 3-hit death)
- Shopkeeper NPC (dialogue with item trade)
- Patrolling Guard (walks between two points)
- Collectible Item (disappears on pickup)
- Door with Key (checks inventory for key item)
- Lava Tile (damage on walk)
- Heal Tile (heal on walk)
- Teleport Tile (teleports entity to destination)

Click any template to insert it into the currently open code editor.

### Tab 3: Tutorial

Links to Tutorial Mode and shows a quick-start guide for absolute beginners.

### Tab 4: Keyboard Shortcuts

All keybindings listed. Updates live when you remap keys in settings.

### Search

The search bar at the top filters content across all tabs simultaneously.
Type any word to find matching functions, templates, or shortcuts.

---

## File Editor

Open from **ESC → File Editor** or console command `opensettings` → File Editor.

The File Editor lets you browse and edit the actual Python source files of the
engine itself, from inside the running game.

### Features

- **Full project file tree** on the left panel
- Click any `.py`, `.json`, `.txt`, or `.md` file to open it
- Same code editor as behavior scripts — syntax highlighting, undo/redo, Ctrl+S
- **Automatic backup** — before every save, a timestamped `.bak` copy is created in `backups/`
- **Restore Backup** button — lists all backups for the current file, click to restore
- **Warning banner** always visible — "Editing source files can break the game"
- Files that require a restart show an additional warning when opened

### Backup System

Every time you save a file through the File Editor:
1. A backup is created at `backups/[filename].[YYYYMMDD_HHMMSS].bak`
2. The new content is written to the original file
3. The backup list is always accessible via "Restore Backup"

### Files That Require Restart

| File | Reason |
|------|--------|
| `main.py` | Entry point — cannot hot-reload |
| `settings.py` | Constants loaded at startup |

All other `.py` files can be hot-reloaded after saving.

### Safety

Even if you save a broken file, the backup lets you restore to the last working state.
The game catches import errors from reloaded modules and reports them to the console
rather than crashing.

---

## Tutorial Mode

Access from **Main Menu → Tutorial** or **Help Panel → Tutorial tab**.

Tutorial mode runs in its own isolated world that resets every time you start it.
Changes made in tutorial mode do not affect your saved worlds.

### 15 Tutorial Steps

| Step | Topic |
|------|-------|
| 1 | Welcome — what the game is, what you can do |
| 2 | Movement — WASD / D-pad |
| 3 | Build Mode — entering, placing, deleting tiles |
| 4 | Tile Types — switching types, wall/water/floor/void |
| 5 | Inspecting Tiles — tile inspector, viewing properties |
| 6 | Tile Behavior — opening behavior editor, lava example |
| 7 | Spawning Entities — placing NPC and enemy |
| 8 | Entity Properties — name, stats, dialogue |
| 9 | Writing a Behavior — guided first script: chase player |
| 10 | Hot Reload — saving script updates game instantly |
| 11 | Inventory — open, create item, script it |
| 12 | Sprites — upload custom sprite, assign it |
| 13 | Console — opening console, running basic commands |
| 14 | File Editor — open and edit source files safely |
| 15 | You're Ready — summary and links to full help |

### Each Step Includes

- Highlighted instruction panel that cannot be dismissed until the task is done
- Arrow or highlight pointing to the relevant UI element
- **Skip Step** button (with warning about knowledge gaps)
- **Skip Tutorial** button to exit tutorial mode entirely

### Progress Saving

Tutorial progress saves to `tutorial_progress.json`. If you close the game
mid-tutorial, it resumes from where you left off.

---

## Player Customization

Open from **ESC → Customize Player** or console command `opencustomize`.

### Customizable Properties

| Property | Description |
|----------|-------------|
| Player Name | Display name shown above player |
| Move Speed | Pixels per second (default 200) |
| Max Health | Maximum HP value (default 100) |
| Width | Player hitbox/sprite width in pixels |
| Height | Player hitbox/sprite height in pixels |
| Sprite | Custom image assigned via Sprite Editor |

### How To Customize

1. Open Customize Player panel
2. Edit any field
3. Click **Apply** to apply immediately — changes take effect in real time
4. Click **Change Sprite…** to open the Sprite Editor for the player

Changes persist to the current world on next save.

---

## Type Managers

### Tile Type Manager

Open with console command `opentilemanager`.

- Lists all current tile types (built-in + custom)
- Select any tile to populate the detail fields
- Edit name, solid flag, movement modifier, and color
- Click **Add/Update** to save changes
- Click **Delete** to remove custom tiles (built-ins are protected)
- New tile types appear immediately in the build mode tile palette
- Changes to tile types apply immediately to newly placed tiles

### Item Type Manager

Open with console command `openitemmanager`.

- Lists all registered item types
- Select any item to populate fields
- Edit ID, name, description, stackable, max stack
- Click **Add/Update** to register or update
- Click **Delete** to remove an item type
- New items are available via `giveitem` console command immediately

---

## HUD Customization

The HUD (heads-up display) shows game state information in the top-left corner
and a health bar at the bottom-left.

### HUD Elements

| Element | Description |
|---------|-------------|
| Mode | Current mode (Play/Build) and sub-mode |
| Tile | Currently selected tile type (build mode only) |
| World | Current world name |
| Position | Player grid coordinates |
| Health Bar | Current / max HP with color fill |

### Toggling Elements

Open **Settings → UI** and click the HUD toggle buttons:
- HUD: show mode
- HUD: show position
- HUD: show tile
- HUD: show health

Each click toggles that element on or off. Changes apply immediately.
HUD visibility state is saved with the game settings.

### Health System

If the Health System game rule is OFF (Settings → Game Rules),
the health bar is hidden regardless of the HUD toggle setting.

---

## UI Theming

The pygame_gui library supports full theme customization via JSON theme files.

### Theme File Location

```
worlds/[world_name]/assets/ui/ui_theme.json
```

### What Can Be Themed

- Button colors, hover colors, pressed colors
- Panel background colors
- Text colors and font sizes
- Border colors and widths
- Scrollbar colors
- Any pygame_gui element property

### Applying a Theme

Place a valid `ui_theme.json` in the world's `assets/ui/` folder.
The theme is loaded when the world loads.

Refer to the pygame_gui documentation for the full theme specification:
https://pygame-gui.readthedocs.io/en/latest/theme_reference/

---

## Keybinding Remapping

All gameplay keybindings can be remapped without editing any files.

### How To Remap

1. Open Settings (ESC → Settings)
2. Click the **Controls** tab
3. Click the button for the action you want to remap
   (the button changes to show "[ press any key ]")
4. Press the new key
5. The binding updates immediately and the button shows the new key name
6. Click **Apply** to save

### Remappable Actions

| Action | Default |
|--------|---------|
| Move Up | W |
| Move Down | S |
| Move Left | A |
| Move Right | D |
| Build Mode | B |
| Interact | F |
| Inventory | Tab |
| Console | ` (backtick) |
| Help | H |
| Menu | Escape |
| Entity Editor | E |
| Sub-mode Place | 1 |
| Sub-mode Delete | 2 |
| Sub-mode Inspect | 3 |
| Sub-mode Select | 4 |

Remapped keys are saved to `settings.json` and loaded on next launch.

---

## Code Templates

These ready-to-use templates are available in the Help Panel → Code Templates tab
and can be inserted directly into the open code editor.

### Basic Chase Enemy
```python
def on_update(self, dt):
    player = get_player()
    if player and distance(self, player) < 300:
        move_toward(self, player, 80)
```

### Zombie (Chase + Damage + 3-hit Death)
```python
def on_spawn(self):
    self.hits = 0

def on_update(self, dt):
    player = get_player()
    if not player:
        return
    move_toward(self, player, 60)
    if distance(self, player) < 40:
        deal_damage(player, 1)

def on_death(self):
    log("Zombie slain!")
```

### Shopkeeper NPC
```python
def on_interact(self, player):
    if has_item(player, 'stone', 3):
        remove_item(player, 'stone', 3)
        give_item(player, 'key', 1)
        open_dialogue("Here is your key!")
    else:
        open_dialogue("Bring me 3 stones for a key.")
```

### Patrolling Guard
```python
def on_spawn(self):
    self.target_x = self.position[0] + 128
    self.dir = 1

def on_update(self, dt):
    self.position[0] += 60 * self.dir * dt
    if abs(self.position[0] - self.target_x) < 4:
        self.dir *= -1
```

### Collectible Item
```python
def on_use(self, player):
    give_item(player, 'stick', 1)
    log("Collected a stick!")
```

### Door with Key
```python
def on_interact(self, entity):
    player = get_player()
    if has_item(player, 'key', 1):
        remove_item(player, 'key', 1)
        set_tile(int(self.position[0]//64),
                 int(self.position[1]//64), 'floor')
        open_dialogue("Door unlocked!")
    else:
        open_dialogue("You need a key.")
```

### Lava Tile
```python
def on_walk(self, entity):
    deal_damage(entity, 1)
```

### Heal Tile
```python
def on_walk(self, entity):
    heal(entity, 1)
```

### Teleport Tile
```python
def on_enter(self, entity):
    entity.position[0] = 5 * 64
    entity.position[1] = 5 * 64
```

---

## Troubleshooting

### Game does not launch

**Check Python version:**
```bash
python --version
```
Must be 3.9 or higher.

**Check dependencies:**
```bash
pip install pygame-ce pygame_gui pygments watchdog
```

**Check for import errors:**
```bash
python -c "import pygame; import pygame_gui; import pygments; import watchdog"
```

---

### "ModuleNotFoundError: No module named 'pygame'"

You installed `pygame` instead of `pygame-ce`. Run:
```bash
pip uninstall pygame
pip install pygame-ce
```

---

### Black screen on launch

This can happen if pygame cannot initialize the display.
Try running from a terminal (not an IDE) and check for error output.

---

### World fails to load

Check the console output for the specific error.
Common causes:
- Corrupted `world.json` (edit or delete it)
- Missing behavior script file (script path stored but file deleted)
- Permission error on worlds directory

---

### Script syntax error in code editor

The red error bar at the bottom of the code editor shows the exact line and error.
Fix the syntax before saving. The file will not be saved with errors.

---

### Hot reload not working

- Make sure `watchdog` is installed: `pip install watchdog`
- The behavior script path must be inside `worlds/[name]/behaviors/`
- Check the console for reload error messages in red

---

### Settings not saving

Check that the game has write permission to the `sandbox_game/` directory.
`settings.json` is created in the same folder as `main.py`.

---

### Mobile controls not appearing

Enable them in **Settings → Mobile → Toggle Mobile Controls**, then click **Apply**.

---

### Backup files filling up disk

Backups are stored in `sandbox_game/backups/`.
You can safely delete old `.bak` files manually at any time.
Backup creation can be reduced by saving source files less frequently.

---

## Architecture Overview

```
main.py
  └── run_main_menu()       WorldManager.list_worlds()
  └── Game(screen)
        ├── InputHandler    ← keyboard + mouse + virtual mobile input
        ├── Renderer        ← all drawing, no game logic
        ├── EventBus        ← pub/sub for cross-system events
        ├── HotReloadManager← watchdog watcher + importlib reloader
        ├── WorldManager    ← save/load/delete worlds (JSON)
        │
        ├── World           ← TileMap + entities list + metadata
        │     ├── TileMap   ← 2D grid of Tile objects
        │     └── [Entity]  ← NPC, Enemy (behavior_module attached)
        │
        ├── Player          ← WASD movement, collision, tile modifiers
        │
        ├── ScriptingAPI    ← all API functions (move_toward, deal_damage...)
        ├── ScriptSandbox   ← restricted globals for safe execution
        ├── ScriptValidator ← ast.parse() pre-validation
        │
        ├── TileEditor      ← place/delete/inspect/select sub-modes
        ├── EntityEditor    ← spawn NPC/enemy on click
        ├── CodeEditor      ← syntax highlight, undo/redo, Ctrl+S hot-reload
        ├── InventoryEditor ← inventory grid UI
        ├── SpriteEditor    ← upload, spritesheet, animations, preview
        ├── FileEditor      ← project file browser + backup system
        │
        ├── HUD             ← mode, position, health, toggleable elements
        ├── GameMenu        ← ESC menu, all options
        ├── SettingsMenu    ← 7-tab settings, keybind remap, game rules
        ├── MobileControls  ← D-pad + action buttons + FAB, injects InputHandler
        ├── PlayerCustomize ← name/speed/health/size/sprite
        ├── TileTypeManager ← add/edit/delete tile types
        ├── ItemTypeManager ← add/edit/delete item types
        ├── HelpPanel       ← API ref, templates, shortcuts, search
        ├── TutorialMode    ← 15-step isolated hands-on tutorial
        └── DeveloperConsole← toggle, history, all commands registered
```

### Event Bus Events

| Event Name | Published By | Consumed By |
|------------|-------------|-------------|
| `hud_toggle_mode` | SettingsMenu | HUD |
| `hud_toggle_position` | SettingsMenu | HUD |
| `hud_toggle_tile` | SettingsMenu | HUD |
| `hud_toggle_health` | SettingsMenu | HUD |
| `fab_save` | MobileControls | Game |
| `fab_help` | MobileControls | Game |
| `fab_settings` | MobileControls | Game |
| `fab_file_editor` | MobileControls | Game |
| `fab_exit_menu` | MobileControls | Game |

---

## License

This project is provided as-is for personal and educational use.
All code was written as part of the Build Me project.

---

*Build Me — version 1.0 — Python 3.9+ — pygame-ce — Build anything.*
```
