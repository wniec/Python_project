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
    pass


class Handler(AbstractHandler):
    def _render_all(self):
        return super()._render_all()

    def _update_dims(self):
        return super()._update_dims()

    def handle(self, event, draw=False):
        return super().handle(event, draw)
