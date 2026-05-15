# =============================================================================
# File: sandbox_game/main.py
# =============================================================================
"""
Entry point for Build Me — handles main menu loop and world loading.
"""

import sys
import pygame
import pygame_gui

from core.game import Game
from ui.main_menu import MainMenu
from world.world_manager import WorldManager
from world.world import World
import settings


def run_main_menu(screen: pygame.Surface) -> str:
    """
    Run the main menu and return the selected world name.

    Args:
        screen: pygame display surface

    Returns:
        World name string or empty string if user quit
    """
    ui_manager = pygame_gui.UIManager((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
    world_manager = WorldManager()
    main_menu = MainMenu(screen, ui_manager)
    main_menu.populate_world_list(world_manager.list_worlds())

    clock = pygame.time.Clock()
    selected_world_name = ""
    running = True

    def on_world_selected(name: str):
        nonlocal selected_world_name, running
        selected_world_name = name
        running = False

    def on_new_world(name: str):
        world = world_manager.create_world(name)
        world_manager.save_world(world)
        main_menu.populate_world_list(world_manager.list_worlds())

    def on_delete_world(name: str):
        world_manager.delete_world(name)
        main_menu.populate_world_list(world_manager.list_worlds())

    main_menu.on_world_selected = on_world_selected
    main_menu.on_new_world = on_new_world
    main_menu.on_delete_world = on_delete_world

    while running and main_menu.active:
        dt = clock.tick(settings.FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)

            ui_manager.process_events(event)
            main_menu.handle_event(event)

        ui_manager.update(dt)
        screen.fill(settings.COLORS['background'])
        ui_manager.draw_ui(screen)
        pygame.display.flip()

    main_menu.cleanup()
    return selected_world_name


def main() -> int:
    """
    Initialize pygame, run main menu, load world, run game loop.

    Returns:
        Exit code (0 = success, 1 = error)
    """
    try:
        pygame.init()
        screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        pygame.display.set_caption(settings.GAME_TITLE)

        world_name = run_main_menu(screen)

        if not world_name:
            return 0

        # Load selected world
        world_manager = WorldManager()
        world = world_manager.load_world(world_name)

        if world is None:
            print(f"Failed to load '{world_name}', creating fresh world.")
            world = world_manager.create_world(world_name)

        # Run game
        game = Game(screen)
        game.load_world(world)
        game.run()

        return 0

    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        pygame.quit()


if __name__ == "__main__":
    sys.exit(main())
