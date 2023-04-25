import pygame
import numpy as np


class Sprite:
    def __init__(self, array: np.array, size: float):
        self.rgb_array: np.array = array
        self.surface: pygame.Surface = None
        self.size: float = None

        self.render(size)

    def render(self, size: float):
        """
        Only supports square rendering i.e. self.rgb_array is a square matrix
        """
        n = len(self.rgb_array)
        pxl_size = size // n
        padding = (abs((size / n) - pxl_size) * n) / 2
        surface = pygame.Surface((size, size), pygame.SRCALPHA)

        for row in range(n):
            for col in range(n):
                if self.rgb_array[row][col][3] != 0:
                    pygame.draw.rect(
                        surface,
                        self.rgb_array[row][col][:3],
                        (
                            padding + col * pxl_size,
                            padding + row * pxl_size,
                            pxl_size,
                            pxl_size,
                        ),
                    )

        self.surface = surface
        self.size = size
