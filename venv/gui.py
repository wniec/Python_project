import gameHandler
import menuHandler
import pygame

pygame.init()
pygame.display.set_caption("Shogi Appl")

WINDOW_SIZE = (800, 600)
CLK = pygame.time.Clock()
window = pygame.display.set_mode(WINDOW_SIZE, pygame.RESIZABLE)


handle = menuHandler.handle
h = menuHandler.Handler(window, WINDOW_SIZE)

while True:
    # Handle events
    for event in pygame.event.get():
        change_scene_to = handle(event, h)
        match change_scene_to:
            case "Game":
                handle = gameHandler.handle
                h = gameHandler.Handler(window, window.get_size(), "Black", 600)

            case "Menu":
                handle = menuHandler.handle
                h = menuHandler.Handler(window, window.get_size())

            case _:
                pass

    # Draw scene
    handle(None, h, draw=True)

    # Update the display
    pygame.display.update()

    CLK.tick(60)
