import gameHandler
import menuHandler
import pygame

pygame.init()
pygame.display.set_caption("Shogi Appl")

WINDOW_SIZE = (854, 480)
CLK = pygame.time.Clock()
window = pygame.display.set_mode(WINDOW_SIZE, pygame.RESIZABLE)


handler = menuHandler.Handler(window, WINDOW_SIZE)

while True:
    # Handle events
    for event in pygame.event.get():
        change_scene_to = handler.handle(event)
        match change_scene_to:
            case "Game":
                handler = gameHandler.Handler(
                    window, window.get_size(), "Random", 60, is_pvp=True
                )

            case "Menu":
                handler = menuHandler.Handler(window, window.get_size())

            case _:
                pass

    # Draw scene
    handler.handle(None, draw=True)

    # Update the display
    pygame.display.update()

    CLK.tick(60)
