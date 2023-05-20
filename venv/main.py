import pygame
import gameHandler
import menuHandler

pygame.init()
pygame.display.set_caption("Shogi App")

WINDOW_SIZE = (1024, 768)
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
                    window, window.get_size(), "White", 300, is_pvp=False
                )

            case "Menu":
                handler = menuHandler.Handler(window, window.get_size())

            case _:
                pass

    # Draw scene
    handler.handle(None, draw=True)

    # Update the display
    pygame.display.update()

    CLK.tick(120)
