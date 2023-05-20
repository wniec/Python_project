import pygame
import pygame.freetype
import numpy as np
import math
import board
import pieces

from pieces import COLOR
from sprite import Sprite
from random import randint
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
        self.screen: pygame.surface = screen

        self.pieces = {
            name: (
                Sprite(np.load(SPRITE_PATH + name + "0.npy"), 100),
                Sprite(np.load(SPRITE_PATH + name + "1.npy"), 100),
            )
            for name in pieces.pieces_dict
        }
        self.board = None
        self.clock = [None, None]
        self.bg_color = RGB_BLACK
        self.drop_menu = [None, None]

        self.player_text = [None, None]
        self.end_text = None

        self.quit_button = None
        self.quit_button_hover = None

        self.drop_button = [None, None]
        self.drop_button_hover = [None, None]

    def render_pieces(self, size):
        for key in self.pieces.keys():
            sprite1, sprite2 = self.pieces[key]
            sprite1.render(size)
            sprite2.render(size)

    def render_board(self, square_size, n_squares=9):
        BOARD_COLOR = (234, 158, 34)

        surface = pygame.Surface((n_squares * square_size, n_squares * square_size))
        surface.fill(BOARD_COLOR)

        for x in range(n_squares):
            for y in range(n_squares):
                pygame.draw.rect(
                    surface,
                    RGB_BLACK,
                    (x * square_size, y * square_size, square_size, square_size),
                    width=int(square_size / 25),
                )

        self.board = surface

    def render_drop_menu(self, square_size):
        self.drop_menu = []
        for _ in range(2):
            surface = pygame.Surface((6 * square_size, 7 * square_size))
            surface.fill((153, 78, 0, 255))
            pygame.draw.rect(
                surface,
                RGB_BLACK,
                (0, 0, 6 * square_size, 7 * square_size),
                width=int(square_size / 12.5),
            )
            self.drop_menu.append(surface)

    def render_clock(self, time, square_size, color):
        self.clock[color.value] = TextBox(
            time,
            font_size=square_size / 2,
            font_color=RGB_BLACK,
            bg_color=RGB_WHITE,
            width=3 * square_size,
            height=square_size / 2,
            border=True,
        ).render_text()

    def render_quit_button(self, square_size):
        self.quit_button = TextBox(
            "Q",
            font_size=square_size / 2,
            font_color=RGB_WHITE,
            bg_color=RGB_BLACK,
            width=square_size,
            height=square_size,
            border=True,
        ).render_text()

        self.quit_button_hover = TextBox(
            "Q",
            font_size=square_size / 2,
            font_color=RGB_BLACK,
            bg_color=RGB_WHITE,
            width=square_size,
            height=square_size,
            border=True,
        ).render_text()

    def render_drop_button(self, square_size):
        self.drop_button = []
        self.drop_button_hover = []
        for _ in range(2):
            self.drop_button.append(
                TextBox(
                    "D",
                    font_size=square_size / 2,
                    font_color=RGB_WHITE,
                    bg_color=RGB_BLACK,
                    width=square_size,
                    height=square_size,
                    border=True,
                ).render_text()
            )

            self.drop_button_hover.append(
                TextBox(
                    "D",
                    font_size=square_size / 2,
                    font_color=RGB_BLACK,
                    bg_color=RGB_WHITE,
                    width=square_size,
                    height=square_size,
                    border=True,
                ).render_text()
            )

    def render_player_text(self, square_size):
        self.player_text = []
        for player in (1, 2):
            self.player_text.append(
                TextBox(
                    "Player " + str(player),
                    font_size=square_size / 2,
                    font_color=RGB_WHITE,
                    bg_color=RGB_BLACK,
                    width=3 * square_size,
                    height=square_size / 2,
                    border=False,
                ).render_text()
            )

    def render_end_text(self, square_size, who_won):
        self.end_text = TextBox(
            who_won + " wins!",
            font_size=square_size / 2,
            font_color=RGB_BLACK,
            bg_color=RGB_WHITE,
            width=4 * square_size,
            height=1.2 * square_size,
            border=False,
        ).render_text()

    def draw_bg(self):
        self.screen.fill(self.bg_color)

    def draw_piece(self, piece_name, piece_color, pos):
        self.screen.blit(self.pieces[piece_name][piece_color.value].surface, pos)

    def draw_board(self, pos):
        self.screen.blit(self.board, pos)

    def draw_drop_menu(self, pos, color: COLOR):
        self.screen.blit(self.drop_menu[color.value], pos)

    def draw_clock(self, pos0, pos1):
        self.screen.blit(self.clock[0], pos0)
        self.screen.blit(self.clock[1], pos1)

    def draw_hint(self, pos, square_size, sqr_color=(124, 252, 0)):
        transparent_square = pygame.Surface((square_size, square_size), pygame.SRCALPHA)
        transparent_square.set_alpha(128)
        transparent_square.fill(sqr_color, (0, 0, square_size, square_size))
        self.screen.blit(transparent_square, pos)

    def draw_quit_button(self, pos, hover=False):
        if hover:
            self.screen.blit(self.quit_button_hover, pos)
        else:
            self.screen.blit(self.quit_button, pos)

    def draw_drop_button(self, pos1, pos2, hover1=False, hover2=False):
        if hover1:
            self.screen.blit(self.drop_button_hover[0], pos1)
        else:
            self.screen.blit(self.drop_button[0], pos1)

        if hover2:
            self.screen.blit(self.drop_button_hover[1], pos2)
        else:
            self.screen.blit(self.drop_button[1], pos2)

    def draw_player_text(self, pos1, pos2):
        self.screen.blit(self.player_text[0], pos1)
        self.screen.blit(self.player_text[1], pos2)

    def draw_end_text(self, pos):
        self.screen.blit(self.end_text, pos)


class Handler(AbstractHandler):
    def __init__(self, window, who_starts, max_time, is_pvp):
        # Window attributes
        self.window = window
        self.window_size = 0
        self.board_width = 0
        self.board_height = 0
        self.board_pos = (0, 0)
        self.square_size = 0
        self.drop_menu_1_pos = (0, 0)
        self.drop_menu_2_pos = (0, 0)

        # Board attributes
        self.board = None
        self.who_starts = who_starts
        self.max_time = max_time
        self.is_pvp = is_pvp

        # Active piece attributes
        self.active_piece: pieces.Piece = None
        self.active_pos = None
        self.available_squares = None
        self.dragging = False
        self.mouse_offset = None

        # Logic attributes
        self.clk_event = pygame.USEREVENT + 1

        self.ended = False
        self.who_won: str = ""

        self.drop_menu_enabled_1 = False
        self.drop_menu_enabled_2 = False

        self.quit_button = None
        self.drop_button_1 = None
        self.drop_button_2 = None

        # Renderer
        self.renderer = Renderer(window)

        # Set field values
        self.__setup()

    def __setup(self):
        # Setup board
        if self.who_starts == "White":
            who_starts = COLOR.WHITE
        elif self.who_starts == "Black":
            who_starts = COLOR.BLACK
        else:
            who_starts = COLOR.WHITE if randint(0, 1) == 0 else COLOR.BLACK

        who_starts = who_starts if self.is_pvp else COLOR.BLACK
        self.board = board.Board(
            max_time=self.max_time, is_pvp=self.is_pvp, who_starts=who_starts
        )

        # Setup logic
        pygame.time.set_timer(self.clk_event, 1000)

        self.quit_button = Button((0, 0, 0, 0))
        self.drop_button_1 = Button((0, 0, 0, 0))
        self.drop_button_2 = Button((0, 0, 0, 0))

        # Setup dimensions and renders
        self._update_dims()
        self._render_all()

    def _update_dims(self):
        self.window_size = pygame.display.get_surface().get_size()
        self.board_width = 0.8 * min(self.window_size)
        self.board_height = 0.8 * min(self.window_size)
        self.board_pos = (
            (self.window_size[0] - self.board_width) / 2,
            (self.window_size[1] - self.board_height) / 2,
        )
        self.square_size = self.board_width // 9
        self.drop_menu_1_pos = (
            self.board_pos[0] - 0.75 * self.square_size,
            self.board_pos[1] + 1.5 * self.square_size,
        )
        self.drop_menu_2_pos = (
            self.board_pos[0] - 0.75 * self.square_size,
            self.board_pos[1] + 0.5 * self.square_size,
        )
        self.quit_button.rect = (
            self.board_pos[0]
            + self.square_size * self.board.size
            + 0.15 * self.square_size / 2,
            self.board_pos[1] + self.square_size * (self.board.size // 2),
            self.square_size,
            self.square_size,
        )
        self.drop_button_1.rect = (
            self.board_pos[0]
            + self.square_size * self.board.size
            + 0.15 * self.square_size / 2,
            self.board_pos[1] + self.square_size * self.board.size - self.square_size,
            self.square_size,
            self.square_size,
        )
        self.drop_button_2.rect = (
            self.board_pos[0]
            + self.square_size * self.board.size
            + 0.15 * self.square_size / 2,
            self.board_pos[1],
            self.square_size,
            self.square_size,
        )

    def _render_all(self):
        self.renderer.render_pieces(self.square_size)
        self.renderer.render_board(self.square_size)
        self.renderer.render_clock(
            self.board.clock.pretty_time(COLOR.BLACK),
            self.square_size,
            COLOR.BLACK,
        )
        self.renderer.render_clock(
            self.board.clock.pretty_time(COLOR.WHITE),
            self.square_size,
            COLOR.WHITE,
        )
        self.renderer.render_quit_button(self.square_size)
        self.renderer.render_drop_button(self.square_size)
        self.renderer.render_player_text(self.square_size)
        self.renderer.render_end_text(self.square_size, self.who_won)
        self.renderer.render_drop_menu(self.square_size)

    def __end_game(self):
        self.ended = True
        self.who_won = (
            "Player 1" if self.board.turn_color == COLOR.WHITE else "Player 2"
        )

        self.drop_menu_enabled_1 = False
        self.drop_menu_enabled_2 = False

        self.active_piece = None
        self.active_pos = None
        self.available_squares = None
        self.dragging = False

        self.renderer.render_end_text(self.square_size, self.who_won)

    def handle(self, event, draw=False):
        def __get_position_on_board(row, col):
            x = self.board_pos[0] + col * self.square_size
            y = self.board_pos[1] + row * self.square_size
            return (x, y)

        def __get_rowcol_on_board(x, y):
            col = max(min(math.floor((x - self.board_pos[0]) / self.square_size), 8), 0)
            row = max(min(math.floor((y - self.board_pos[1]) / self.square_size), 8), 0)
            return (row, col)

        def __in_board(x, y):
            p = (
                self.board_pos[0]
                <= x
                <= self.board_pos[0] + self.board.size * self.square_size
            )
            q = (
                self.board_pos[1]
                <= y
                <= self.board_pos[1] + self.board.size * self.square_size
            )
            return p and q

        def __get_position_in_dropmenu(color: COLOR, key):
            d = 3 if int(key[-1]) == color.value else 0
            match key[0]:
                case "P":
                    x, y = int(key[1]) // 3, int(key[1]) % 3
                case "R":
                    x, y = 3, 0

                case "B":
                    x, y = 3, 1

                case "L":
                    if key[1] == "1":
                        x, y = 3, 2
                    else:
                        x, y = 4, 0

                case "N":
                    if key[1] == "1":
                        x, y = 4, 1
                    else:
                        x, y = 4, 2

                case "S":
                    if key[1] == "1":
                        x, y = 5, 0
                    else:
                        x, y = 5, 1

                case "G":
                    if key[1] == "1":
                        x, y = 5, 2
                    else:
                        x, y = 6, 0
            y += d
            if color == COLOR.WHITE:
                return (
                    self.drop_menu_2_pos[0] + y * self.square_size,
                    self.drop_menu_2_pos[1] + x * self.square_size,
                )
            return (
                self.drop_menu_1_pos[0] + y * self.square_size,
                self.drop_menu_1_pos[1] + x * self.square_size,
            )

        def __get_piece_from_dropmenu(color: COLOR, x, y):
            if color == COLOR.WHITE:
                col = math.floor((x - self.drop_menu_2_pos[0]) / self.square_size)
                row = math.floor((y - self.drop_menu_2_pos[1]) / self.square_size)
            else:
                col = math.floor((x - self.drop_menu_1_pos[0]) / self.square_size)
                row = math.floor((y - self.drop_menu_1_pos[1]) / self.square_size)

            key = ""
            match (row, col):
                case (0, 0) | (0, 3):
                    key = "P0"
                case (0, 1) | (0, 4):
                    key = "P1"
                case (0, 2) | (0, 5):
                    key = "P2"
                case (1, 0) | (1, 3):
                    key = "P3"
                case (1, 1) | (1, 4):
                    key = "P4"
                case (1, 2) | (1, 5):
                    key = "P5"
                case (2, 0) | (2, 3):
                    key = "P6"
                case (2, 1) | (2, 4):
                    key = "P7"
                case (2, 2) | (2, 5):
                    key = "P8"
                case (3, 0) | (3, 3):
                    key = "R"
                case (3, 1) | (3, 4):
                    key = "B"
                case (3, 2) | (3, 5):
                    key = "L1"
                case (4, 0) | (4, 3):
                    key = "L2"
                case (4, 1) | (4, 4):
                    key = "N1"
                case (4, 2) | (4, 5):
                    key = "N2"
                case (5, 0) | (5, 3):
                    key = "S1"
                case (5, 1) | (5, 4):
                    key = "S2"
                case (5, 2) | (5, 5):
                    key = "G1"
                case (6, 0) | (6, 3):
                    key = "G2"

            if col >= 3:
                key += str(color.value)
            else:
                key += str(color.opposite().value)

            if key in self.board.captured[color.value]:
                return key, self.board.captured[color.value][key]

            return key, None

        def __in_dropmenu(color: COLOR, x, y):
            if color == COLOR.BLACK:
                return (
                    self.drop_menu_1_pos[0]
                    <= x
                    <= self.drop_menu_1_pos[0] + 6 * self.square_size
                    and self.drop_menu_1_pos[1]
                    <= y
                    <= self.drop_menu_1_pos[1] + 7 * self.square_size
                )

            return (
                self.drop_menu_2_pos[0]
                <= x
                <= self.drop_menu_2_pos[0] + 6 * self.square_size
                and self.drop_menu_2_pos[1]
                <= y
                <= self.drop_menu_2_pos[1] + 7 * self.square_size
            )

        if draw:
            r = self.renderer

            # Draw base
            r.draw_bg()
            r.draw_board(self.board_pos)
            r.draw_clock(
                (
                    self.board_pos[0]
                    + self.board.size * self.square_size
                    - r.clock[0].get_size()[0],
                    self.board_pos[1]
                    + self.board.size * self.square_size
                    + 0.15 * r.clock[0].get_size()[1],
                ),
                (
                    self.board_pos[0]
                    + self.board.size * self.square_size
                    - r.clock[1].get_size()[0],
                    self.board_pos[1] - 1.15 * r.clock[1].get_size()[1],
                ),
            )
            r.draw_quit_button(
                (self.quit_button.rect[0], self.quit_button.rect[1]),
                self.quit_button.hover,
            )
            r.draw_drop_button(
                (self.drop_button_1.rect[0], self.drop_button_1.rect[1]),
                (self.drop_button_2.rect[0], self.drop_button_2.rect[1]),
                self.drop_button_1.hover,
                self.drop_button_2.hover,
            )
            r.draw_player_text(
                (
                    self.board_pos[0],
                    self.board_pos[1]
                    + self.board.size * self.square_size
                    + 0.15 * r.player_text[0].get_size()[1],
                ),
                (
                    self.board_pos[0],
                    self.board_pos[1] - 1.15 * r.player_text[1].get_size()[1],
                ),
            )

            # If dragging a piece draw available squares
            if not self.ended and self.dragging:
                for x, y in self.available_squares - {
                    (self.active_piece.row, self.active_piece.col)
                }:
                    r.draw_hint(__get_position_on_board(x, y), self.square_size)

                if not self.drop_menu_enabled_1 and not self.drop_menu_enabled_2:
                    r.draw_hint(
                        __get_position_on_board(
                            self.active_piece.row, self.active_piece.col
                        ),
                        self.square_size,
                        sqr_color=(169, 169, 169),
                    )

            # Draw the pieces
            for row in range(self.board.size):
                for col in range(self.board.size):
                    if (
                        self.board.grid[row][col] != None
                        and self.board.grid[row][col] != self.active_piece
                    ):
                        piece = self.board.grid[row][col]
                        r.draw_piece(
                            piece.name, piece.color, __get_position_on_board(row, col)
                        )

            # If ended draw end text
            if self.ended:
                r.draw_end_text(
                    (
                        self.board_pos[0]
                        + (self.board_width - r.end_text.get_size()[0]) // 2,
                        self.board_pos[1] + self.square_size * (self.board.size // 2),
                    )
                )

            # If dragging draw piece in hand
            elif self.dragging:
                r.draw_piece(
                    self.active_piece.name, self.active_piece.color, self.active_pos
                )

            # If enabled draw dropmenu
            elif self.drop_menu_enabled_1:
                r.draw_drop_menu(self.drop_menu_1_pos, COLOR.BLACK)

                for key, piece in self.board.captured[COLOR.BLACK.value].items():
                    pos = __get_position_in_dropmenu(COLOR.BLACK, key)
                    r.draw_piece(piece.name, COLOR.BLACK, pos)

            elif self.drop_menu_enabled_2:
                r.draw_drop_menu(self.drop_menu_2_pos, COLOR.WHITE)

                for key, piece in self.board.captured[COLOR.WHITE.value].items():
                    pos = __get_position_in_dropmenu(COLOR.WHITE, key)
                    r.draw_piece(piece.name, COLOR.WHITE, pos)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Check if the piece is clicked
            if (
                not self.ended
                and not self.drop_menu_enabled_1
                and not self.drop_menu_enabled_2
                and __in_board(event.pos[0], event.pos[1])
            ):
                row, col = __get_rowcol_on_board(event.pos[0], event.pos[1])

                if self.board.grid[row][col] != None:
                    # Piece in hand

                    self.dragging = True
                    self.active_piece = self.board.grid[row][col]
                    self.active_pos = __get_position_on_board(
                        self.active_piece.row, self.active_piece.col
                    )

                    self.available_squares = self.board.get_available(
                        self.active_piece
                    ) | {(self.active_piece.row, self.active_piece.col)}

                    self.mouse_offset = (
                        self.active_pos[0] - event.pos[0],
                        self.active_pos[1] - event.pos[1],
                    )

            # Drop button logic
            elif (
                not self.ended
                and not self.drop_menu_enabled_2
                and self.drop_button_1.inbounds((event.pos[0], event.pos[1]))
            ):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                self.drop_menu_enabled_1 = not self.drop_menu_enabled_1

            # Drop button logic
            elif (
                not self.ended
                and not self.drop_menu_enabled_1
                and self.drop_button_2.inbounds((event.pos[0], event.pos[1]))
            ):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                self.drop_menu_enabled_2 = not self.drop_menu_enabled_2

            # Drop menu logic
            elif (
                not self.ended
                and self.drop_menu_enabled_1
                and __in_dropmenu(COLOR.BLACK, event.pos[0], event.pos[1])
            ):
                key, piece = __get_piece_from_dropmenu(
                    COLOR.BLACK, event.pos[0], event.pos[1]
                )
                if piece != None:
                    # Piece in hand
                    self.dragging = True
                    self.active_piece = piece
                    self.active_pos = __get_position_in_dropmenu(COLOR.BLACK, key)
                    self.available_squares = self.board.get_available_drops(piece)
                    self.mouse_offset = (
                        self.active_pos[0] - event.pos[0],
                        self.active_pos[1] - event.pos[1],
                    )

            # Drop menu logic
            elif (
                not self.ended
                and self.drop_menu_enabled_2
                and __in_dropmenu(COLOR.WHITE, event.pos[0], event.pos[1])
            ):
                key, piece = __get_piece_from_dropmenu(
                    COLOR.WHITE, event.pos[0], event.pos[1]
                )
                if piece != None:
                    # Piece in hand
                    self.dragging = True
                    self.active_piece = piece
                    self.active_pos = __get_position_in_dropmenu(COLOR.WHITE, key)
                    self.available_squares = self.board.get_available_drops(piece)
                    self.mouse_offset = (
                        self.active_pos[0] - event.pos[0],
                        self.active_pos[1] - event.pos[1],
                    )

            # Quit button logic
            elif self.quit_button.inbounds((event.pos[0], event.pos[1])):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                return "Menu"

        elif event.type == pygame.MOUSEBUTTONUP and not self.ended:
            # If dragging release the piece and snap it to the nearest grid square
            if (
                not self.ended
                and self.dragging
                and __get_rowcol_on_board(event.pos[0], event.pos[1])
                in self.available_squares
                - {(self.active_piece.row, self.active_piece.col)}
                and __in_board(event.pos[0], event.pos[1])
            ):
                self.dragging = False
                self.active_pos = (event.pos[0], event.pos[1])

                # Handle dropping a piece from drop menu
                if self.drop_menu_enabled_1 or self.drop_menu_enabled_2:
                    self.drop_menu_enabled_1 = False
                    self.drop_menu_enabled_2 = False

                    self.board.drop(
                        self.active_piece,
                        __get_rowcol_on_board(self.active_pos[0], self.active_pos[1]),
                    )

                # Handle moving a piece on the board
                else:
                    self.board.move(
                        self.active_piece,
                        __get_rowcol_on_board(self.active_pos[0], self.active_pos[1]),
                    )

                if self.active_piece.can_promote(self.active_piece.row):
                    self.active_piece.promote()

                self.active_piece = None
                self.active_pos = None
                self.available_squares = None

                self.board.end_turn()

                if self.board.is_checkmate(self.board.turn_color):
                    self.__end_game()

                # Handle bot move
                if not self.ended and not self.board.is_pvp:
                    _, x, y, piece, dropped, promoted = self.board.bot.best_move(
                        self.board.turn_color
                    )
                    if dropped:
                        self.board.drop(piece, (x, y))
                    else:
                        self.board.move(piece, (x, y))

                    self.board.end_turn()

                    if self.board.is_checkmate(self.board.turn_color):
                        self.__end_game()

            # If incorrect release position stop dragging the piece
            elif self.dragging:
                self.dragging = False
                self.active_piece = None
                self.active_pos = None
                self.available_squares = None

        elif event.type == self.clk_event and not self.ended:
            r = self.renderer
            r.render_clock(
                self.board.clock.pretty_time(COLOR.BLACK),
                self.square_size,
                COLOR.BLACK,
            )
            r.render_clock(
                self.board.clock.pretty_time(COLOR.WHITE),
                self.square_size,
                COLOR.WHITE,
            )

            if self.board.clock.get_time(self.board.turn_color) == 0:
                self.__end_game()

        elif event.type == pygame.MOUSEMOTION:
            # Move the piece with the mouse
            if not self.ended and self.dragging:
                self.active_pos = (
                    event.pos[0] + self.mouse_offset[0],
                    event.pos[1] + self.mouse_offset[1],
                )

            # Hover logic
            elif (
                not self.ended
                and not self.drop_menu_enabled_2
                and self.drop_button_1.inbounds((event.pos[0], event.pos[1]))
            ):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                self.drop_button_1.hover = True

            # Hover logic
            elif (
                not self.ended
                and not self.drop_menu_enabled_1
                and self.drop_button_2.inbounds((event.pos[0], event.pos[1]))
            ):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                self.drop_button_2.hover = True

            # Hover logic
            elif self.quit_button.inbounds((event.pos[0], event.pos[1])):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                self.quit_button.hover = True

            # Hover logic
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

                if not self.drop_menu_enabled_1:
                    self.drop_button_1.hover = False

                if not self.drop_menu_enabled_2:
                    self.drop_button_2.hover = False

                self.quit_button.hover = False

        elif event.type == pygame.VIDEORESIZE:
            self._update_dims()
            self._render_all()

        elif event.type == pygame.QUIT:
            pygame.quit()
            exit()
