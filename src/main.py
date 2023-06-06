import pygame
import gui.gameHandler as gameHandler
import gui.menuHandler as menuHandler
import gui.statsHandler as statsHandler

from gui.saveController import SaveController

pygame.init()
pygame.display.set_caption("Shogi")

WINDOW_SIZE = (1024, 768)
CLK = pygame.time.Clock()

window = pygame.display.set_mode(WINDOW_SIZE, pygame.RESIZABLE)
handler = menuHandler.Handler(window)

while True:
    # Handle events
    for event in pygame.event.get():
        res = handler.handle(event)
        try:
            change_scene_to, args = res
        except:
            change_scene_to = res

        match change_scene_to:
            case "Game":
                handler = gameHandler.Handler(window, **args)

            case "Menu":
                handler = menuHandler.Handler(window)

            case "Stats":
                handler = statsHandler.Handler(window)

            case _:
                pass

    # Draw scene
    handler.handle(None, draw=True)

    # Update the display
    pygame.display.update()

    CLK.tick(120)
