import pygame
import pygame.freetype
import numpy as np

from gui.sprite import Sprite
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


class OptionBox:
    def __init__(
        self,
        options,
        arguments,
    ):
        self.options = options
        self.arguments = arguments
        self.selected_option = 0
        self.selected_argument = 0
        self.selected_args = {option: 0 for option in range(len(self.options))}

    def render(
        self,
        font_size=16,
        font_color=RGB_WHITE,
        bg_color=RGB_BLACK,
        width=400,
        height=200,
        border=False,
    ):
        font = pygame.freetype.Font(FONT_PATH + "LGGothic.ttf", size=font_size)
        surface = pygame.Surface((width, height))
        surface.fill(bg_color)
        if border:
            pygame.draw.rect(
                surface,
                color=font_color,
                rect=(0, 0, width, height),
                width=int(font_size / 12.5),
            )

        delta = height / 2
        y = 0

        option_text, _ = font.render(
            self.options[self.selected_option],
            fgcolor=font_color,
            size=font_size,
        )
        surface.blit(
            option_text,
            (
                width / 2 - option_text.get_width() / 2,
                (y + (y + delta)) / 2 - option_text.get_height() / 2,
            ),
        )

        y += delta

        argument_text, _ = font.render(
            str(self.arguments[self.selected_option][self.selected_argument]),
            fgcolor=font_color,
            size=font_size,
        )

        surface.blit(
            argument_text,
            (
                width / 2 - argument_text.get_width() / 2,
                (y + (y + delta)) / 2 - argument_text.get_height() / 2,
            ),
        )

        return surface

    def change_option(self, increment):
        self.selected_option = (self.selected_option + increment) % len(self.options)
        self.selected_argument = self.selected_args[self.selected_option]

    def change_argument(self, increment):
        arguments = self.arguments[self.selected_option]
        self.selected_argument = (self.selected_argument + increment) % len(arguments)
        self.selected_args[self.selected_option] = self.selected_argument

    def get_selected_args(self):
        args = {"who_starts": 0, "max_time": 0, "is_pvp": 0}
        match self.selected_args[0]:
            case 0:
                args["is_pvp"] = True
            case 1:
                args["is_pvp"] = False

        args["max_time"] = self.arguments[1][self.selected_args[1]] * 60

        match self.selected_args[2]:
            case 0:
                args["who_starts"] = "Black"
            case 1:
                args["who_starts"] = "White"
            case 2:
                args["who_starts"] = "Random"

        return args


class Renderer(AbstractRenderer):
    def __init__(self, screen):
        self.screen = screen
        self.bg_color = RGB_BLACK
        self.bg = Sprite(np.load(SPRITE_PATH + "bg" ".npy"), 100)

        self.newgame_button = None
        self.newgame_hover = None

        self.stat_button = None
        self.stat_button_hover = None

        self.option_box_bg = None
        self.option_box = None
        self.next_option_button = None
        self.next_option_button_hover = None
        self.next_value_button = None
        self.next_value_button_hover = None

        self.start_button = None
        self.start_button_hover = None

        self.X_button = None
        self.X_button_hover = None

    def render_bg(self, size):
        self.bg.render(size)

    def render_newgame_button(self, width, height):
        self.newgame_button = TextBox(
            "New Game",
            font_size=height / 2,
            font_color=RGB_WHITE,
            bg_color=RGB_BLACK,
            width=width,
            height=height,
            border=True,
        ).render_text()

        self.newgame_hover = TextBox(
            "New Game",
            font_size=height / 2,
            font_color=RGB_BLACK,
            bg_color=RGB_WHITE,
            width=width,
            height=height,
            border=True,
        ).render_text()

    def render_stat_button(self, width, height):
        self.stat_button = TextBox(
            "Stats",
            font_size=height / 2,
            font_color=RGB_WHITE,
            bg_color=RGB_BLACK,
            width=width,
            height=height,
            border=True,
        ).render_text()

        self.stat_button_hover = TextBox(
            "Stats",
            font_size=height / 2,
            font_color=RGB_BLACK,
            bg_color=RGB_WHITE,
            width=width,
            height=height,
            border=True,
        ).render_text()

    def render_option_box_bg(self, width, height):
        self.option_box_bg = TextBox(
            "",
            font_size=height / 2,
            font_color=RGB_BLACK,
            bg_color=RGB_WHITE,
            width=width,
            height=height,
            border=False,
        ).render_text()

    def render_option_box(self, option_box: OptionBox, width, height):
        self.option_box = option_box.render(
            font_size=height / 4,
            font_color=RGB_BLACK,
            bg_color=RGB_WHITE,
            width=width,
            height=height,
            border=False,
        )

    def render_option_button(self, width, height):
        self.next_option_button_hover = TextBox(
            ">",
            font_size=height / 2,
            font_color=RGB_BLACK,
            bg_color=RGB_WHITE,
            width=width,
            height=height,
            border=False,
        ).render_text()

        self.next_option_button = TextBox(
            ">",
            font_size=height / 2,
            font_color=RGB_WHITE,
            bg_color=RGB_BLACK,
            width=width,
            height=height,
            border=False,
        ).render_text()

        self.next_value_button_hover = TextBox(
            ">",
            font_size=height / 2,
            font_color=RGB_BLACK,
            bg_color=RGB_WHITE,
            width=width,
            height=height,
            border=False,
        ).render_text()

        self.next_value_button = TextBox(
            ">",
            font_size=height / 2,
            font_color=RGB_WHITE,
            bg_color=RGB_BLACK,
            width=width,
            height=height,
            border=False,
        ).render_text()

    def render_start_button(self, width, height):
        self.start_button_hover = TextBox(
            "Start",
            font_size=height / 2,
            font_color=RGB_BLACK,
            bg_color=RGB_WHITE,
            width=width,
            height=height,
            border=False,
        ).render_text()

        self.start_button = TextBox(
            "Start",
            font_size=height / 2,
            font_color=RGB_WHITE,
            bg_color=RGB_BLACK,
            width=width,
            height=height,
            border=False,
        ).render_text()

    def render_X_button(self, width, height):
        self.X_button = TextBox(
            "X",
            font_size=height / 2,
            font_color=RGB_WHITE,
            bg_color=RGB_BLACK,
            width=width,
            height=height,
            border=False,
        ).render_text()

        self.X_button_hover = TextBox(
            "X",
            font_size=height / 2,
            font_color=RGB_BLACK,
            bg_color=RGB_WHITE,
            width=width,
            height=height,
            border=False,
        ).render_text()

    def draw_bg(self, pos):
        self.screen.fill(self.bg_color)
        self.screen.blit(self.bg.surface, pos)

    def draw_newgame_button(self, pos, hover=False):
        if hover:
            self.screen.blit(self.newgame_hover, pos)
        else:
            self.screen.blit(self.newgame_button, pos)

    def draw_stat_button(self, pos, hover=False):
        if hover:
            self.screen.blit(self.stat_button_hover, pos)
        else:
            self.screen.blit(self.stat_button, pos)

    def draw_option_box_bg(self, pos):
        self.screen.blit(self.option_box_bg, pos)

    def draw_option_box(self, pos):
        self.screen.blit(self.option_box, pos)

    def draw_option_button(self, pos1, pos2, hover1=False, hover2=False):
        if hover1:
            self.screen.blit(self.next_option_button_hover, pos1)
        else:
            self.screen.blit(self.next_option_button, pos1)

        if hover2:
            self.screen.blit(self.next_value_button_hover, pos2)
        else:
            self.screen.blit(self.next_value_button, pos2)

    def draw_start_button(self, pos, hover=False):
        if hover:
            self.screen.blit(self.start_button_hover, pos)
        else:
            self.screen.blit(self.start_button, pos)

    def draw_X_button(self, pos, hover=False):
        if hover:
            self.screen.blit(self.X_button_hover, pos)
        else:
            self.screen.blit(self.X_button, pos)


class Handler(AbstractHandler):
    def __init__(self, window):
        self.window = window
        self.window_size = 0
        self.frame_size = 0
        self.base_size = 0
        self.frame_pos = (0, 0)

        self.option_box = OptionBox(
            ["Opponent?", "Time [min]?", "Who starts?"],
            [
                ("Player", "Bot"),
                (5, 10, 30, 60, 720),
                ("Player 1", "Player 2", "Random"),
            ],
        )
        self.option_box_enabled = False

        self.newgame_button = Button((0, 0, 0, 0))
        self.stat_button = Button((0, 0, 0, 0))
        self.next_option_button = Button((0, 0, 0, 0))
        self.next_value_button = Button((0, 0, 0, 0))
        self.start_button = Button((0, 0, 0, 0))
        self.X_button = Button((0, 0, 0, 0))

        self.renderer = Renderer(self.window)
        self._update_dims()
        self._render_all()

    def _update_dims(self):
        self.window_size = pygame.display.get_surface().get_size()
        self.frame_size = 0.95 * min(self.window_size)
        self.base_size = 0.1 * self.frame_size
        self.frame_pos = (
            (self.window.get_width() - self.frame_size) // 2,
            (self.window.get_height() - self.frame_size) // 2,
        )
        self.newgame_button.rect = (
            self.frame_pos[0] + self.frame_size / 4 - 3 * self.base_size / 2,
            self.frame_pos[1] + self.frame_size / 1.3,
            3 * self.base_size,
            self.base_size,
        )
        self.stat_button.rect = (
            self.frame_pos[0] + 3 * self.frame_size / 4 - 3 * self.base_size / 2,
            self.frame_pos[1] + self.frame_size / 1.3,
            3 * self.base_size,
            self.base_size,
        )
        self.next_option_button.rect = (
            self.frame_pos[0] + self.frame_size / 2 + self.base_size,
            self.frame_pos[1] + self.frame_size / 2 - self.base_size,
            self.base_size,
            self.base_size,
        )
        self.next_value_button.rect = (
            self.frame_pos[0] + self.frame_size / 2 + self.base_size,
            self.frame_pos[1] + self.frame_size / 2,
            self.base_size,
            self.base_size,
        )
        self.start_button.rect = (
            self.frame_pos[0] + self.frame_size / 2 - 2 * self.base_size,
            self.frame_pos[1] + self.frame_size / 2 + self.base_size,
            3 * self.base_size,
            self.base_size,
        )
        self.X_button.rect = (
            self.frame_pos[0] + self.frame_size / 2 + self.base_size,
            self.frame_pos[1] + self.frame_size / 2 + self.base_size,
            self.base_size,
            self.base_size,
        )

    def _render_all(self):
        self.renderer.render_bg(self.frame_size)
        self.renderer.render_newgame_button(
            self.newgame_button.rect[2], self.newgame_button.rect[3]
        )
        self.renderer.render_stat_button(
            self.stat_button.rect[2], self.stat_button.rect[3]
        )

        self.renderer.render_option_box_bg(4 * self.base_size, 3 * self.base_size)
        self.renderer.render_option_box(
            self.option_box, 3 * self.base_size, 2 * self.base_size
        )
        self.renderer.render_option_button(self.base_size, self.base_size)
        self.renderer.render_start_button(3 * self.base_size, self.base_size)
        self.renderer.render_X_button(self.base_size, self.base_size)

    def handle(self, event, draw=False):
        if draw:
            r = self.renderer
            r.draw_bg(self.frame_pos)
            r.draw_newgame_button(
                (self.newgame_button.rect[0], self.newgame_button.rect[1]),
                self.newgame_button.hover,
            )
            r.draw_stat_button(
                (self.stat_button.rect[0], self.stat_button.rect[1]),
                self.stat_button.hover,
            )

            if self.option_box_enabled:
                r.draw_option_box_bg(
                    (
                        self.frame_pos[0] + self.frame_size / 2 - 2 * self.base_size,
                        self.frame_pos[1] + self.frame_size / 2 - self.base_size,
                    )
                )
                r.draw_option_box(
                    (
                        self.frame_pos[0] + self.frame_size / 2 - 2 * self.base_size,
                        self.frame_pos[1] + self.frame_size / 2 - self.base_size,
                    )
                )
                r.draw_option_button(
                    (self.next_option_button.rect[0], self.next_option_button.rect[1]),
                    (self.next_value_button.rect[0], self.next_value_button.rect[1]),
                    self.next_option_button.hover,
                    self.next_value_button.hover,
                )
                r.draw_start_button(
                    (self.start_button.rect[0], self.start_button.rect[1]),
                    self.start_button.hover,
                )
                r.draw_X_button(
                    (self.X_button.rect[0], self.X_button.rect[1]), self.X_button.hover
                )

        elif event.type == pygame.MOUSEMOTION:
            if self.newgame_button.inbounds((event.pos[0], event.pos[1])):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                self.newgame_button.hover = True

            elif self.stat_button.inbounds((event.pos[0], event.pos[1])):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                self.stat_button.hover = True

            elif self.option_box_enabled and self.next_option_button.inbounds(
                (event.pos[0], event.pos[1])
            ):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                self.next_option_button.hover = True
                self.next_value_button.hover = False
                self.start_button.hover = False
                self.X_button.hover = False

            elif self.option_box_enabled and self.next_value_button.inbounds(
                (event.pos[0], event.pos[1])
            ):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                self.next_value_button.hover = True
                self.next_option_button.hover = False
                self.start_button.hover = False
                self.X_button.hover = False

            elif self.option_box_enabled and self.X_button.inbounds(
                (event.pos[0], event.pos[1])
            ):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                self.next_value_button.hover = False
                self.next_option_button.hover = False
                self.start_button.hover = False
                self.X_button.hover = True

            elif self.option_box_enabled and self.start_button.inbounds(
                (event.pos[0], event.pos[1])
            ):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                self.next_value_button.hover = False
                self.next_option_button.hover = False
                self.start_button.hover = True
                self.X_button.hover = False

            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                self.newgame_button.hover = False
                self.stat_button.hover = False
                self.next_value_button.hover = False
                self.next_option_button.hover = False
                self.start_button.hover = False
                self.X_button.hover = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.newgame_button.inbounds((event.pos[0], event.pos[1])):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                self.option_box_enabled = True

            elif self.option_box_enabled and self.next_value_button.inbounds(
                (event.pos[0], event.pos[1])
            ):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                self.option_box.change_argument(1)
                self.renderer.render_option_box(
                    self.option_box, 3 * self.base_size, 2 * self.base_size
                )

            elif self.option_box_enabled and self.next_option_button.inbounds(
                (event.pos[0], event.pos[1])
            ):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                self.option_box.change_option(1)
                self.renderer.render_option_box(
                    self.option_box, 3 * self.base_size, 2 * self.base_size
                )

            elif self.option_box_enabled and self.X_button.inbounds(
                (event.pos[0], event.pos[1])
            ):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                self.option_box_enabled = False

            elif self.option_box_enabled and self.start_button.inbounds(
                (event.pos[0], event.pos[1])
            ):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                return "Game", self.option_box.get_selected_args()

            elif self.stat_button.inbounds((event.pos[0], event.pos[1])):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                return "Stats"

        elif event.type == pygame.VIDEORESIZE:
            self._update_dims()
            self._render_all()

        elif event.type == pygame.QUIT:
            pygame.quit()
            exit()
