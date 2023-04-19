from sprite import Sprite
import numpy as np
import pygame
import pygame.freetype

PATH = "rsrc/sprites/"
FONT_PATH = "rsrc/fonts/"


class Renderer:
    def __init__(self, screen):
        self.screen = screen
        self.bg_color = (0, 0, 0)
        self.frames = [
            Sprite(np.load(PATH + "frame" + str(i) + ".npy"), 100) for i in range(4)
        ]
        self.starttxt = None
        self.statstxt = None

    def render_frames(self, size):
        for frame in self.frames:
            frame.render(size)

    def render_starttxt(self, size):
        FONT = pygame.freetype.Font(FONT_PATH + "LGGothic.ttf", size=10)
        surface, _ = FONT.render("New game [N]", (255, 255, 255), size=size)
        self.starttxt = surface

    def render_statstxt(self, size):
        FONT = pygame.freetype.Font(FONT_PATH + "LGGothic.ttf", size=10)
        surface, _ = FONT.render("Statistics [S]", (255, 255, 255), size=size)
        self.statstxt = surface

    def draw_bg(self):
        self.screen.fill(self.bg_color)

    def draw_frame(self, i_frame, pos):
        self.screen.blit(self.frames[i_frame].surface, pos)

    def draw_starttxt(self, pos):
        self.screen.blit(self.starttxt, pos)

    def draw_statstxt(self, pos):
        self.screen.blit(self.statstxt, pos)


class Handler:
    def __init__(self, window, window_size) -> None:
        self.window = window
        self.window_size = window_size
        self.frame_size = 0.9 * min(window_size)
        self.frame_pos = (
            (window_size[0] - self.frame_size) // 2,
            (window_size[1] - self.frame_size) // 2,
        )
        self.i_frame = 0
        self.renderer = Renderer(self.window)

        self.clk_event = pygame.USEREVENT + 1

        self.setup()

    def setup(self):
        self.renderer.render_frames(self.frame_size)
        self.renderer.render_starttxt(self.frame_size / 15)
        self.renderer.render_statstxt(self.frame_size / 15)

        pygame.time.set_timer(self.clk_event, 200)


def handle(event, h: Handler, draw=False):
    if draw:
        r = h.renderer
        # Clear the window
        r.draw_bg()

        # Draw frames
        r.draw_frame(h.i_frame, h.frame_pos)

        # Draw text
        r.draw_starttxt(
            (
                (h.window_size[0] - r.starttxt.get_size()[0]) // 2,
                (h.window_size[1] - r.starttxt.get_size()[1]) // 2
                + r.starttxt.get_size()[1],
            )
        )

        r.draw_statstxt(
            (
                (h.window_size[0] - r.statstxt.get_size()[0]) // 2,
                (h.window_size[1] - r.statstxt.get_size()[1]) // 2
                + 2.5 * r.starttxt.get_size()[1],
            )
        )

    elif event.type == pygame.QUIT:
        pygame.quit()
        exit()

    elif event.type == h.clk_event:
        h.i_frame = (h.i_frame + 1) % 4

    elif event.type == pygame.VIDEORESIZE:
        # Resize the window
        h.window_size = pygame.display.get_surface().get_size()

        # Update dimensions
        h.frame_size = 0.9 * min(event.w, event.h)
        h.frame_pos = (
            (h.window.get_width() - h.frame_size) // 2,
            (h.window.get_height() - h.frame_size) // 2,
        )

        # Rerender surfaces
        r = h.renderer
        r.render_frames(h.frame_size)
        r.render_starttxt(h.frame_size / 15)
        r.render_statstxt(h.frame_size / 15)

    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_n:
            return "Game"
