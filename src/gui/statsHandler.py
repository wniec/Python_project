import pygame
import pygame.freetype
import numpy as np

from gui.sprite import Sprite
from gui.saveController import SaveController
from gui.abstractHandler import (
    TextBox,
    Button,
    AbstractRenderer,
    AbstractHandler,
    SPRITE_PATH,
    FONT_PATH,
    RGB_BLACK,
    RGB_WHITE,
)


class Renderer(AbstractRenderer):
    def __init__(self, screen):
        self.screen = screen
        self.bg_color = RGB_BLACK
        self.stat_text = None
        self.return_button = None
        self.return_button_hover = None

    def render_stats(self, data, width, height):
        self.stat_text = TextBox(
            f"Games played: {data['Total games']}\nGames won: {data['Won games']}\nLast 10 games\n{data['Last 10 games']}",
            font_size=height // 8,
            font_color=RGB_WHITE,
            bg_color=RGB_BLACK,
            width=width,
            height=height,
            border=True,
        ).render_text()

    def render_stat_button(self, width, height):
        self.return_button = TextBox(
            "<",
            font_size=height / 2,
            font_color=RGB_WHITE,
            bg_color=RGB_BLACK,
            width=width,
            height=height,
            border=True,
        ).render_text()

        self.return_button_hover = TextBox(
            "<",
            font_size=height / 2,
            font_color=RGB_BLACK,
            bg_color=RGB_WHITE,
            width=width,
            height=height,
            border=True,
        ).render_text()

    def draw_bg(self):
        self.screen.fill(self.bg_color)

    def draw_stats(self, pos):
        self.screen.blit(self.stat_text, pos)

    def draw_stat_button(self, pos, hover=False):
        if hover:
            self.screen.blit(self.return_button_hover, pos)
        else:
            self.screen.blit(self.return_button, pos)


class Handler(AbstractHandler):
    def __init__(self, window) -> None:
        self.window = window
        self.window_size = (0, 0)
        self.base_size = 0
        self.textbox_size = (0, 0)
        self.textbox_pos = (0, 0)

        self.return_button = Button((0, 0, 0, 0))
        self.data = SaveController().get_data()

        self.renderer = Renderer(self.window)
        self._update_dims()
        self._render_all()

    def _update_dims(self):
        self.window_size = pygame.display.get_surface().get_size()
        self.base_size = 0.1 * min(self.window_size)
        self.textbox_size = (0.6 * self.window_size[0], 0.6 * self.window_size[1])
        self.textbox_pos = (
            (self.window_size[0] - self.textbox_size[0]) / 2,
            (self.window_size[1] - self.textbox_size[1]) / 2,
        )
        self.return_button.rect = (
            (self.window_size[0] - self.textbox_size[0]) / 2,
            (self.window_size[1] - self.textbox_size[1]) / 2 - self.base_size,
            self.base_size,
            self.base_size,
        )

    def _render_all(self):
        self.renderer.render_stats(
            self.data, self.textbox_size[0], self.textbox_size[1]
        )
        self.renderer.render_stat_button(self.base_size, self.base_size)

    def handle(self, event, draw=False):
        if draw:
            r = self.renderer
            r.draw_bg()
            r.draw_stats(self.textbox_pos)
            r.draw_stat_button(
                (self.return_button.rect[0], self.return_button.rect[1]),
                self.return_button.hover,
            )

        elif event.type == pygame.MOUSEMOTION:
            if self.return_button.inbounds((event.pos[0], event.pos[1])):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                self.return_button.hover = True
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                self.return_button.hover = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.return_button.inbounds((event.pos[0], event.pos[1])):
                return "Menu"

        elif event.type == pygame.VIDEORESIZE:
            self._update_dims()
            self._render_all()

        elif event.type == pygame.QUIT:
            pygame.quit()
            exit()
