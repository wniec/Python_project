import pygame


class Sprite:
    def __init__(self, array, size):
        self.rgb_array = array
        self.surface = None
        self.size = None

        self.render(size)

    def render(self, size):
        """
        Only supports square rendering i.e. self.rgb_array is a square matrix, size: float
        """
        n_row, n_col = len(self.rgb_array), len(self.rgb_array[0])
        pxl_size = size // n_row
        padding = (abs((size / n_row) - size // n_row) * n_row) / 2
        surface = pygame.Surface((size, size), pygame.SRCALPHA)

        for row in range(n_row):
            for col in range(n_col):
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
