# =============================================================================
# File: sandbox_game/ui/help_panel.py
# =============================================================================
"""
Help panel with API reference, code templates, tutorial links, and keybindings.
"""

import pygame
import pygame_gui
from typing import Optional
import settings


class HelpPanel:
    """
    In-game help panel with tabbed sections and search.
    """

    # Full API reference text
    _API_REFERENCE = """<font face='monospace' size=3>
<b>SCRIPTING API REFERENCE</b><br><br>
<b>move_toward(entity, target, speed)</b><br>
  Move entity toward target (entity or (x,y)) at speed px/s.<br><br>
<b>distance(entity_a, entity_b)</b><br>
  Returns pixel distance between two entities.<br><br>
<b>deal_damage(target, amount)</b><br>
  Deal integer damage to target entity.<br><br>
<b>heal(target, amount)</b><br>
  Heal target entity by amount (capped at max_health).<br><br>
<b>get_player()</b><br>
  Returns the player entity.<br><br>
<b>spawn_entity(entity_type, x, y)</b><br>
  Spawn 'npc' or 'enemy' at grid tile (x, y). Returns entity.<br><br>
<b>destroy_entity(entity)</b><br>
  Remove entity from the world immediately.<br><br>
<b>open_dialogue(text)</b><br>
  Display a dialogue string on screen for 3 seconds.<br><br>
<b>play_animation(entity, animation_name)</b><br>
  Play named animation on entity (Phase 4+).<br><br>
<b>set_tile(x, y, tile_type)</b><br>
  Set grid tile at (x,y) to tile_type string.<br><br>
<b>get_tile(x, y)</b><br>
  Returns Tile object at grid (x,y) or None.<br><br>
<b>log(message)</b><br>
  Print message to developer console in cyan.<br><br>
<b>give_item(player, item_id, quantity)</b><br>
  Add item_id x quantity to player inventory.<br><br>
<b>remove_item(player, item_id, quantity)</b><br>
  Remove item_id x quantity from player inventory.<br><br>
<b>has_item(player, item_id, quantity)</b><br>
  Returns True if player has at least quantity of item_id.<br><br>
<b>get_inventory(player)</b><br>
  Returns the player Inventory object.<br><br>
<b>set_world_background(image_path)</b><br>
  Set world background image (Phase 4+).<br><br>
<b>set_player_sprite(image_path)</b><br>
  Set player sprite image (Phase 4+).<br><br>
<b>get_world_setting(key)</b><br>
  Get value from world metadata dict.<br><br>
<b>set_world_setting(key, value)</b><br>
  Set value in world metadata dict.<br>
</font>"""

    _TEMPLATES = """<font face='monospace' size=3>
<b>BASIC CHASE ENEMY</b><br>
def on_update(self, dt):<br>
&nbsp;&nbsp;player = get_player()<br>
&nbsp;&nbsp;if player and distance(self, player) &lt; 300:<br>
&nbsp;&nbsp;&nbsp;&nbsp;move_toward(self, player, 80)<br><br>

<b>ZOMBIE (chase + damage on contact + 3-hit death)</b><br>
def on_spawn(self):<br>
&nbsp;&nbsp;self.hits = 0<br>
def on_update(self, dt):<br>
&nbsp;&nbsp;player = get_player()<br>
&nbsp;&nbsp;if not player: return<br>
&nbsp;&nbsp;move_toward(self, player, 60)<br>
&nbsp;&nbsp;if distance(self, player) &lt; 40:<br>
&nbsp;&nbsp;&nbsp;&nbsp;deal_damage(player, 1)<br>
def on_death(self):<br>
&nbsp;&nbsp;log("Zombie slain!")<br><br>

<b>SHOPKEEPER NPC</b><br>
def on_interact(self, player):<br>
&nbsp;&nbsp;if has_item(player, 'stone', 3):<br>
&nbsp;&nbsp;&nbsp;&nbsp;remove_item(player, 'stone', 3)<br>
&nbsp;&nbsp;&nbsp;&nbsp;give_item(player, 'key', 1)<br>
&nbsp;&nbsp;&nbsp;&nbsp;open_dialogue("Here is your key!")<br>
&nbsp;&nbsp;else:<br>
&nbsp;&nbsp;&nbsp;&nbsp;open_dialogue("Bring me 3 stones for a key.")<br><br>

<b>PATROLLING GUARD</b><br>
def on_spawn(self):<br>
&nbsp;&nbsp;self.target_x = self.position[0] + 128<br>
&nbsp;&nbsp;self.dir = 1<br>
def on_update(self, dt):<br>
&nbsp;&nbsp;self.position[0] += 60 * self.dir * dt<br>
&nbsp;&nbsp;if abs(self.position[0] - self.target_x) &lt; 4:<br>
&nbsp;&nbsp;&nbsp;&nbsp;self.dir *= -1<br><br>

<b>COLLECTIBLE ITEM</b><br>
def on_use(self, player):<br>
&nbsp;&nbsp;give_item(player, 'stick', 1)<br>
&nbsp;&nbsp;log("Collected a stick!")<br><br>

<b>DOOR WITH KEY</b><br>
def on_interact(self, entity):<br>
&nbsp;&nbsp;player = get_player()<br>
&nbsp;&nbsp;if has_item(player, 'key', 1):<br>
&nbsp;&nbsp;&nbsp;&nbsp;remove_item(player, 'key', 1)<br>
&nbsp;&nbsp;&nbsp;&nbsp;set_tile(int(self.position[0]//64),<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;int(self.position[1]//64), 'floor')<br>
&nbsp;&nbsp;&nbsp;&nbsp;open_dialogue("Door unlocked!")<br>
&nbsp;&nbsp;else:<br>
&nbsp;&nbsp;&nbsp;&nbsp;open_dialogue("You need a key.")<br><br>

<b>LAVA TILE</b><br>
def on_walk(self, entity):<br>
&nbsp;&nbsp;deal_damage(entity, 1)<br><br>

<b>HEAL TILE</b><br>
def on_walk(self, entity):<br>
&nbsp;&nbsp;heal(entity, 1)<br><br>

<b>TELEPORT TILE</b><br>
def on_enter(self, entity):<br>
&nbsp;&nbsp;entity.position[0] = 5 * 64<br>
&nbsp;&nbsp;entity.position[1] = 5 * 64<br>
</font>"""

    _TUTORIAL_TAB = """<font size=3>
<b>TUTORIAL MODE</b><br><br>
Access the full 15-step hands-on tutorial from:<br>
  Main Menu → Tutorial<br>
  or this panel → Tutorial tab<br><br>
<b>Quick start:</b><br>
1. WASD to move<br>
2. B to enter build mode<br>
3. Click to place tiles<br>
4. E to spawn entities<br>
5. F near NPC to talk<br>
6. Tab for inventory<br>
7. Backtick for console<br>
8. H for this help panel<br>
9. ESC for game menu<br>
</font>"""

    _SHORTCUTS = """<font face='monospace' size=3>
<b>KEYBOARD SHORTCUTS</b><br><br>
<b>Movement</b><br>
  WASD          Move player<br><br>
<b>Modes</b><br>
  B             Toggle build mode<br>
  E             Entity editor (in build mode)<br>
  Tab           Open / close inventory<br>
  Backtick (`)  Toggle developer console<br>
  H             Toggle help panel<br>
  ESC           Game menu / back<br><br>
<b>Build Mode</b><br>
  1             Place tile sub-mode<br>
  2             Delete tile sub-mode<br>
  3             Inspect tile sub-mode<br>
  4             Select tile sub-mode<br>
  Left Click    Act on tile (place/delete/inspect)<br><br>
<b>Code Editor</b><br>
  Ctrl+S        Save script<br>
  Ctrl+Z        Undo<br>
  Ctrl+Y        Redo<br>
  Enter         New line<br>
  Up / Down     Navigate lines<br><br>
<b>Interaction</b><br>
  F             Interact with nearby NPC<br>
</font>"""

    def __init__(self, ui_manager: pygame_gui.UIManager):
        """
        Initialize help panel.

        Args:
            ui_manager: pygame_gui UIManager instance
        """
        self.ui_manager = ui_manager
        self.active = False
        self._current_tab = "api"

        sw = settings.SCREEN_WIDTH
        sh = settings.SCREEN_HEIGHT

        pw = int(sw * 0.78)
        ph = int(sh * 0.82)
        px = (sw - pw) // 2
        py = (sh - ph) // 2

        self.panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(px, py, pw, ph),
            manager=ui_manager,
            starting_layer_height=18
        )
        self.panel.hide()

        # Title
        self.title_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 8, pw - 20, 28),
            text="Help & Reference",
            manager=ui_manager,
            container=self.panel
        )

        # Tab buttons
        tab_w = 130
        gap = 8
        tabs = [
            ("api",       "API Reference"),
            ("templates", "Code Templates"),
            ("tutorial",  "Tutorial"),
            ("shortcuts", "Shortcuts"),
        ]
        for i, (tab_id, label) in enumerate(tabs):
            btn = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(10 + i * (tab_w + gap), 44, tab_w, 32),
                text=label,
                manager=ui_manager,
                container=self.panel
            )
            setattr(self, f"_tab_btn_{tab_id}", btn)

        # Search bar
        self.search_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(10 + len(tabs) * (tab_w + gap), 44, pw - 10 - len(tabs) * (tab_w + gap) - 10, 32),
            manager=ui_manager,
            container=self.panel
        )
        self.search_entry.set_text("")

        # Content box
        content_y = 86
        content_h = ph - content_y - 50

        self.content_box = pygame_gui.elements.UITextBox(
            html_text=self._API_REFERENCE,
            relative_rect=pygame.Rect(10, content_y, pw - 20, content_h),
            manager=ui_manager,
            container=self.panel
        )

        # Close button
        self.close_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(pw - 110, ph - 44, 100, 36),
            text="Close",
            manager=ui_manager,
            container=self.panel
        )

    # ------------------------------------------------------------------
    # Show / hide
    # ------------------------------------------------------------------

    def show(self, tab: str = "api") -> None:
        """
        Show the help panel.

        Args:
            tab: Which tab to open initially
        """
        self.active = True
        self._switch_tab(tab)
        self.panel.show()

    def hide(self) -> None:
        """Hide the help panel."""
        self.active = False
        self.panel.hide()

    def toggle(self, tab: str = "api") -> None:
        """Toggle help panel visibility."""
        if self.active:
            self.hide()
        else:
            self.show(tab)

    # ------------------------------------------------------------------
    # Tab switching
    # ------------------------------------------------------------------

    def _switch_tab(self, tab: str) -> None:
        """
        Switch displayed content to the given tab.

        Args:
            tab: Tab identifier string
        """
        self._current_tab = tab

        content_map = {
            "api":       self._API_REFERENCE,
            "templates": self._TEMPLATES,
            "tutorial":  self._TUTORIAL_TAB,
            "shortcuts": self._SHORTCUTS,
        }

        html = content_map.get(tab, self._API_REFERENCE)
        self._rebuild_content(html)

    def _rebuild_content(self, html: str) -> None:
        """
        Rebuild the content text box with new HTML.

        Args:
            html: HTML content string
        """
        try:
            self.content_box.kill()
            pw = int(settings.SCREEN_WIDTH * 0.78)
            ph = int(settings.SCREEN_HEIGHT * 0.82)
            content_h = ph - 86 - 50

            self.content_box = pygame_gui.elements.UITextBox(
                html_text=html,
                relative_rect=pygame.Rect(10, 86, pw - 20, content_h),
                manager=self.ui_manager,
                container=self.panel
            )
        except Exception as e:
            print(f"Help panel content rebuild error: {e}")

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def _apply_search(self, query: str) -> None:
        """
        Filter current tab content by search query.

        Args:
            query: Search string
        """
        if not query.strip():
            self._switch_tab(self._current_tab)
            return

        content_map = {
            "api":       self._API_REFERENCE,
            "templates": self._TEMPLATES,
            "tutorial":  self._TUTORIAL_TAB,
            "shortcuts": self._SHORTCUTS,
        }

        # Search all tabs, collect matching lines
        query_lower = query.lower()
        matched_lines = []

        for tab_id, content in content_map.items():
            # Strip HTML tags roughly for searching
            import re
            plain = re.sub(r'<[^>]+>', '', content)
            for line in plain.splitlines():
                if query_lower in line.lower() and line.strip():
                    matched_lines.append(line.strip())

        if matched_lines:
            safe_lines = [
                l.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                for l in matched_lines
            ]
            html = (
                "<font face='monospace' size=3>"
                + f"<b>Search results for '{query}':</b><br><br>"
                + "<br>".join(safe_lines)
                + "</font>"
            )
        else:
            html = f"<font size=3>No results found for '{query}'.</font>"

        self._rebuild_content(html)

    # ------------------------------------------------------------------
    # Event handling
    # ------------------------------------------------------------------

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle UI events.

        Args:
            event: pygame event

        Returns:
            True if event was consumed
        """
        if not self.active:
            return False

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.close_button:
                self.hide()
                return True

            for tab_id in ("api", "templates", "tutorial", "shortcuts"):
                btn = getattr(self, f"_tab_btn_{tab_id}", None)
                if btn and event.ui_element == btn:
                    self._switch_tab(tab_id)
                    return True

        if event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
            if event.ui_element == self.search_entry:
                self._apply_search(event.text)
                return True

        return False
