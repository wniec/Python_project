import pygame
import pygame.freetype

from abc import ABC, abstractmethod
from config.defs import SRC_DIR

SPRITE_PATH = SRC_DIR + "/resources/sprites/"
FONT_PATH = SRC_DIR + "/resources/fonts/"

RGB_BLACK = (0, 0, 0)
RGB_WHITE = (255, 255, 255)


class TextBox:
    def __init__(
        self,
        text,
        font_size=16,
        font_color=RGB_WHITE,
        bg_color=RGB_BLACK,
        width=400,
        height=200,
        border=False,
    ):
        self.text = text
        self.font_size = font_size
        self.font_color = font_color
        self.bg_color = bg_color
        self.width = width
        self.height = height
        self.font = pygame.freetype.Font(FONT_PATH + "LGGothic.ttf", size=font_size)
        self.border = border

    def render_text(self):
        lines = self.text.split("\n")
        surface = pygame.Surface((self.width, self.height))

        surface.fill(self.bg_color)
        if self.border:
            pygame.draw.rect(
                surface,
                color=self.font_color,
                rect=(0, 0, self.width, self.height),
                width=int(self.font_size / 12.5),
            )

        delta = self.height / len(lines)
        y = 0

        for line in lines:
            rendered_text, _ = self.font.render(
                line, self.font_color, size=self.font_size
            )
            surface.blit(
                rendered_text,
                (
                    self.width / 2 - rendered_text.get_width() / 2,
                    (y + (y + delta)) / 2 - rendered_text.get_height() / 2,
                ),
            )
            y += delta

        return surface


class Button:
    def __init__(self, rect):
        self.hover = False
        self.rect = rect

    def inbounds(self, pos):
        x, y = pos
        x0, y0, w, h = self.rect
        return x0 <= x <= x0 + w and y0 <= y <= y0 + h


class AbstractRenderer(ABC):
    pass


class AbstractHandler(ABC):
    @abstractmethod
    def _render_all(self):
        pass

    @abstractmethod
    def _update_dims(self):
        pass

    @abstractmethod
    def handle(self, event, draw=False):
        pass
