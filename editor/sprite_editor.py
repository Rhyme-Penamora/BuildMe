# =============================================================================
# File: sandbox_game/editor/sprite_editor.py
# =============================================================================
"""
Sprite editor for uploading and assigning custom sprites and animations.
"""

import os
import shutil
import pygame
import pygame_gui
from typing import Optional, Dict, List
import settings


class SpriteEditor:
    """
    In-game sprite editor panel — file browse, spritesheet, animations, preview.
    """

    def __init__(self, ui_manager: pygame_gui.UIManager):
        """
        Initialize sprite editor.

        Args:
            ui_manager: pygame_gui UIManager instance
        """
        self.ui_manager = ui_manager
        self.active = False

        self.assign_target = None
        self.assign_category = ""

        self.loaded_image_path: Optional[str] = None
        self.loaded_surface: Optional[pygame.Surface] = None

        self.animations: Dict[str, Dict] = {}

        self._preview_anim_name: Optional[str] = None
        self._preview_frame_index = 0
        self._preview_timer = 0.0

        sw = settings.SCREEN_WIDTH
        sh = settings.SCREEN_HEIGHT

        pw = int(sw * 0.75)
        ph = int(sh * 0.8)
        px = (sw - pw) // 2
        py = (sh - ph) // 2

        self.panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(px, py, pw, ph),
            manager=ui_manager
        )
        self.panel.hide()

        self.title_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 8, pw - 20, 28),
            text="Sprite Editor",
            manager=ui_manager,
            container=self.panel
        )

        self.path_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(10, 46, pw - 160, 36),
            manager=ui_manager,
            container=self.panel
        )
        self.path_entry.set_text("Enter image path here...")

        self.browse_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(pw - 145, 46, 130, 36),
            text="Load Image",
            manager=ui_manager,
            container=self.panel
        )

        self.status_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 90, pw - 20, 24),
            text="No image loaded.",
            manager=ui_manager,
            container=self.panel
        )

        self.cols_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 122, 100, 24),
            text="Columns:",
            manager=ui_manager,
            container=self.panel
        )
        self.cols_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(115, 122, 60, 28),
            manager=ui_manager,
            container=self.panel
        )
        self.cols_entry.set_text("1")

        self.rows_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(185, 122, 100, 24),
            text="Rows:",
            manager=ui_manager,
            container=self.panel
        )
        self.rows_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(285, 122, 60, 28),
            manager=ui_manager,
            container=self.panel
        )
        self.rows_entry.set_text("1")

        self.grid_apply_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(355, 122, 120, 28),
            text="Apply Grid",
            manager=ui_manager,
            container=self.panel
        )

        self.anim_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 160, pw - 20, 24),
            text="Animation — Name | Frames (0,1,2) | FPS | Loop",
            manager=ui_manager,
            container=self.panel
        )

        self.anim_name_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(10, 190, 120, 32),
            manager=ui_manager,
            container=self.panel
        )
        self.anim_name_entry.set_text("idle")

        self.anim_frames_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(140, 190, 160, 32),
            manager=ui_manager,
            container=self.panel
        )
        self.anim_frames_entry.set_text("0")

        self.anim_fps_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(310, 190, 70, 32),
            manager=ui_manager,
            container=self.panel
        )
        self.anim_fps_entry.set_text("8")

        self.anim_loop_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(390, 190, 90, 32),
            text="Loop: ON",
            manager=ui_manager,
            container=self.panel
        )
        self._anim_loop = True

        self.add_anim_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(490, 190, 120, 32),
            text="Add Animation",
            manager=ui_manager,
            container=self.panel
        )

        self.anim_list = pygame_gui.elements.UITextBox(
            html_text="<font size=3>No animations defined.</font>",
            relative_rect=pygame.Rect(10, 232, pw - 20, 80),
            manager=ui_manager,
            container=self.panel
        )

        self.assign_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 322, 120, 28),
            text="Assign to:",
            manager=ui_manager,
            container=self.panel
        )
        self.assign_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=["Player", "Entity", "Tile", "Item", "Background"],
            starting_option="Player",
            relative_rect=pygame.Rect(135, 322, 160, 32),
            manager=ui_manager,
            container=self.panel
        )
        self.assign_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(305, 322, 120, 32),
            text="Assign Sprite",
            manager=ui_manager,
            container=self.panel
        )

        self.close_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(pw - 110, ph - 50, 100, 36),
            text="Close",
            manager=ui_manager,
            container=self.panel
        )

    def show(self, target=None, category: str = "sprites") -> None:
        """
        Show the sprite editor.

        Args:
            target: Object to assign sprite to
            category: Asset category folder name
        """
        self.assign_target = target
        self.assign_category = category
        self.active = True
        self.panel.show()

    def hide(self) -> None:
        """Hide the sprite editor."""
        self.active = False
        self.panel.hide()

    def _load_image(self, path: str) -> None:
        """
        Validate and load an image file.

        Args:
            path: Filesystem path to the image
        """
        path = path.strip()

        if not os.path.exists(path):
            self.status_label.set_text(f"File not found: {path}")
            return

        ext = os.path.splitext(path)[1].lower()
        if ext not in ('.png', '.jpg', '.jpeg'):
            self.status_label.set_text("Unsupported format. Use PNG or JPG.")
            return

        try:
            surface = pygame.image.load(path).convert_alpha()
            self.loaded_surface = surface
            self.loaded_image_path = path
            w, h = surface.get_size()
            self.status_label.set_text(
                f"Loaded: {os.path.basename(path)}  ({w}x{h} px)"
            )
        except pygame.error as e:
            self.status_label.set_text(f"Failed to load image: {e}")

    def _toggle_loop(self) -> None:
        """Toggle loop flag on the animation loop button."""
        self._anim_loop = not self._anim_loop
        self.anim_loop_button.set_text(
            "Loop: ON" if self._anim_loop else "Loop: OFF"
        )

    def _add_animation(self) -> None:
        """Read animation fields and register a new animation definition."""
        name = self.anim_name_entry.get_text().strip()
        frames_text = self.anim_frames_entry.get_text().strip()
        fps_text = self.anim_fps_entry.get_text().strip()

        if not name:
            self.status_label.set_text("Animation name cannot be empty.")
            return

        try:
            frames = [int(f.strip()) for f in frames_text.split(",") if f.strip()]
        except ValueError:
            self.status_label.set_text("Frames must be comma-separated integers.")
            return

        try:
            fps = max(1, int(fps_text))
        except ValueError:
            self.status_label.set_text("FPS must be a positive integer.")
            return

        self.animations[name] = {
            'frames': frames,
            'fps': fps,
            'loop': self._anim_loop
        }
        self._refresh_anim_list()
        self.status_label.set_text(f"Animation '{name}' added.")

    def _refresh_anim_list(self) -> None:
        """Rebuild the animation list display."""
        if not self.animations:
            html = "<font size=3>No animations defined.</font>"
        else:
            lines = []
            for name, data in self.animations.items():
                frames_str = ",".join(str(f) for f in data['frames'])
                loop_str = "loop" if data['loop'] else "once"
                lines.append(
                    f"<b>{name}</b>: frames [{frames_str}] "
                    f"@ {data['fps']}fps — {loop_str}"
                )
            html = "<font size=3>" + "<br>".join(lines) + "</font>"

        try:
            self.anim_list.kill()
            pw = int(settings.SCREEN_WIDTH * 0.75)
            self.anim_list = pygame_gui.elements.UITextBox(
                html_text=html,
                relative_rect=pygame.Rect(10, 232, pw - 20, 80),
                manager=self.ui_manager,
                container=self.panel
            )
        except Exception as e:
            print(f"Anim list refresh error: {e}")

    def _assign_sprite(self, world_name: str) -> None:
        """
        Copy image into world assets and assign to target.

        Args:
            world_name: Current world name for directory resolution
        """
        if not self.loaded_image_path or not self.loaded_surface:
            self.status_label.set_text("No image loaded.")
            return

        world_dir = os.path.join("worlds", world_name)
        dest_dir = os.path.join(world_dir, "assets", self.assign_category)
        os.makedirs(dest_dir, exist_ok=True)

        filename = os.path.basename(self.loaded_image_path)
        dest_path = os.path.join(dest_dir, filename)

        try:
            shutil.copy2(self.loaded_image_path, dest_path)
        except Exception as e:
            self.status_label.set_text(f"Copy error: {e}")
            return

        if self.assign_target is not None:
            self.assign_target.sprite_path = dest_path
            self.assign_target.sprite_surface = self.loaded_surface.copy()
            if self.animations:
                self.assign_target.animations = dict(self.animations)
            self.status_label.set_text(f"Sprite assigned: {filename}")
        else:
            self.status_label.set_text(f"Sprite saved (no target): {filename}")

    def update(self, dt: float) -> None:
        """
        Update preview animation timer.

        Args:
            dt: Delta time in seconds
        """
        if not self.active or not self._preview_anim_name:
            return

        anim = self.animations.get(self._preview_anim_name)
        if not anim or not anim['frames']:
            return

        frame_duration = 1.0 / max(1, anim['fps'])
        self._preview_timer += dt

        if self._preview_timer >= frame_duration:
            self._preview_timer = 0.0
            self._preview_frame_index += 1
            if self._preview_frame_index >= len(anim['frames']):
                if anim['loop']:
                    self._preview_frame_index = 0
                else:
                    self._preview_frame_index = len(anim['frames']) - 1

    def render_preview(self, screen: pygame.Surface) -> None:
        """
        Draw sprite preview onto screen.

        Args:
            screen: pygame display surface
        """
        if not self.active or not self.loaded_surface:
            return

        sw = settings.SCREEN_WIDTH
        sh = settings.SCREEN_HEIGHT
        pw = int(sw * 0.75)
        ph = int(sh * 0.8)
        px = (sw - pw) // 2
        py = (sh - ph) // 2

        preview_size = 96
        preview_x = px + pw - preview_size - 10
        preview_y = py + ph - preview_size - 60

        pygame.draw.rect(
            screen, settings.COLORS['white'],
            pygame.Rect(preview_x - 2, preview_y - 2,
                        preview_size + 4, preview_size + 4),
            2
        )

        preview_surf = pygame.transform.scale(
            self.loaded_surface, (preview_size, preview_size)
        )
        screen.blit(preview_surf, (preview_x, preview_y))

    def handle_event(self, event: pygame.event.Event, world_name: str = "") -> bool:
        """
        Handle UI events.

        Args:
            event: pygame event
            world_name: Current world name for asset saving

        Returns:
            True if event was consumed
        """
        if not self.active:
            return False

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.close_button:
                self.hide()
                return True

            if event.ui_element == self.browse_button:
                self._load_image(self.path_entry.get_text())
                return True

            if event.ui_element == self.grid_apply_button:
                try:
                    cols = int(self.cols_entry.get_text())
                    rows = int(self.rows_entry.get_text())
                    if self.loaded_surface:
                        w, h = self.loaded_surface.get_size()
                        fw = w // max(1, cols)
                        fh = h // max(1, rows)
                        self.status_label.set_text(
                            f"Grid: {cols}x{rows}, frame {fw}x{fh}px"
                        )
                except ValueError:
                    self.status_label.set_text("Columns and rows must be integers.")
                return True

            if event.ui_element == self.anim_loop_button:
                self._toggle_loop()
                return True

            if event.ui_element == self.add_anim_button:
                self._add_animation()
                return True

            if event.ui_element == self.assign_button:
                self._assign_sprite(world_name)
                return True

        return False
