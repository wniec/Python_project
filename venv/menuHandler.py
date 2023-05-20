import pygame
import pygame.freetype
import numpy as np

from sprite import Sprite
from abstractHandler import (
    TextBox,
    Button,
    AbstractRenderer,
    AbstractHandler,
    SPRITE_PATH,
    RGB_BLACK,
    RGB_WHITE,
)


class Renderer(AbstractRenderer):
    def __init__(self, screen):
        self.screen = screen
        self.bg_color = RGB_BLACK
        self.nbg_color = RGB_WHITE
        self.bg = Sprite(np.load(SPRITE_PATH + "bg" ".npy"), 100)

        self.start_button = None
        self.start_button_hover = None

    def render_bg(self, size):
        self.bg.render(size)

    def render_start_button(self, width, height):
        self.start_button = TextBox(
            "New Game",
            font_size=height / 2,
            font_color=RGB_WHITE,
            bg_color=RGB_BLACK,
            width=width,
            height=height,
            border=True,
        ).render_text()

        self.start_button_hover = TextBox(
            "New Game",
            font_size=height / 2,
            font_color=RGB_BLACK,
            bg_color=RGB_WHITE,
            width=width,
            height=height,
            border=True,
        ).render_text()

    def draw_bg(self, pos):
        self.screen.fill(self.bg_color)
        self.screen.blit(self.bg.surface, pos)

    def draw_start_button(self, pos, hover=False):
        if hover:
            self.screen.blit(self.start_button_hover, pos)
        else:
            self.screen.blit(self.start_button, pos)


class Handler(AbstractHandler):
    def __init__(self, window, window_size) -> None:
        self.window = window
        self.window_size = window_size
        self.frame_size = 0.95 * min(window_size)
        self.base_size = 0.1 * self.frame_size
        self.frame_pos = (
            (window_size[0] - self.frame_size) // 2,
            (window_size[1] - self.frame_size) // 2,
        )

        self.start_button = Button(
            (
                self.frame_pos[0] + self.frame_size / 2 - 3 * self.base_size / 2,
                self.frame_pos[1] + self.frame_size / 1.3,
                3 * self.base_size,
                self.base_size,
            )
        )

        self.renderer = Renderer(self.window)
        self.renderer.render_bg(self.frame_size)
        self.renderer.render_start_button(
            self.start_button.rect[2], self.start_button.rect[3]
        )

    def handle(self, event, draw=False):
        if draw:
            r = self.renderer
            r.draw_bg(self.frame_pos)
            r.draw_start_button(
                (self.start_button.rect[0], self.start_button.rect[1]),
                self.start_button.hover,
            )

        elif event.type == pygame.MOUSEMOTION:
            if self.start_button.inbounds((event.pos[0], event.pos[1])):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                self.start_button.hover = True

            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                self.start_button.hover = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.start_button.inbounds((event.pos[0], event.pos[1])):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                return "Game"

        elif event.type == pygame.VIDEORESIZE:
            # Resize the window
            self.window_size = pygame.display.get_surface().get_size()

            # Update dimensions
            self.frame_size = 0.95 * min(event.w, event.h)
            self.base_size = 0.1 * self.frame_size
            self.frame_pos = (
                (self.window.get_width() - self.frame_size) // 2,
                (self.window.get_height() - self.frame_size) // 2,
            )
            self.start_button.rect = (
                self.frame_pos[0] + self.frame_size / 2 - 3 * self.base_size / 2,
                self.frame_pos[1] + self.frame_size / 1.3,
                3 * self.base_size,
                self.base_size,
            )

            # Rerender surfaces
            r = self.renderer
            r.render_bg(self.frame_size)
            r.render_start_button(self.start_button.rect[2], self.start_button.rect[3])

        elif event.type == pygame.QUIT:
            pygame.quit()
            exit()
