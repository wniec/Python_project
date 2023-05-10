import pygame
import pygame.freetype
import numpy as np
import math
import time
import board
from pieces import COLOR
from sprite import Sprite

SPRITE_PATH = "rsrc/sprites/"
FONT_PATH = "rsrc/fonts/"


class Renderer:
    def __init__(self, screen):
        self.screen = screen

        self.pieces = {
            name: (
                Sprite(np.load(SPRITE_PATH + name + "0.npy"), 100),
                Sprite(np.load(SPRITE_PATH + name + "1.npy"), 100),
            )
            for name in ("P", "L", "N", "S", "G", "B", "R", "K")
        }
        self.board = None
        self.clock = [None, None]
        self.bg_color = (0, 0, 0)
        self.quittxt = None
        self.playertxt = [None, None]
        self.quitmenu = None
        self.endmenu = None

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
                    (0, 0, 0),
                    (x * square_size, y * square_size, square_size, square_size),
                    width=int(square_size / 25),
                )

        self.board = surface

    def render_clock(self, time, square_size, color):
        FONT = pygame.freetype.Font(FONT_PATH + "LGGothic.ttf", size=10)
        surface, _ = FONT.render(time, (255, 255, 255), size=square_size / 2)
        self.clock[color.value] = surface

    def render_quittxt(self, square_size):
        FONT = pygame.freetype.Font(FONT_PATH + "LGGothic.ttf", size=10)
        surface, _ = FONT.render("Quit [Q]", (255, 255, 255), size=square_size / 2)
        self.quittxt = surface

    def render_playertxt(self, square_size):
        FONT = pygame.freetype.Font(FONT_PATH + "LGGothic.ttf", size=10)
        surface1, _ = FONT.render("Player 1", (255, 255, 255), size=square_size / 2)
        surface2, _ = FONT.render("Player 2", (255, 255, 255), size=square_size / 2)
        self.playertxt = [surface1, surface2]

    def render_quitmenu(self, square_size):
        FONT = pygame.freetype.Font(FONT_PATH + "LGGothic.ttf", size=10)
        text1, _ = FONT.render("Quit?", (0, 0, 0), size=square_size / 2)
        text2, _ = FONT.render("YES [Y]    NO [N]", (0, 0, 0), size=square_size / 2)
        width, height = 1.15 * max(
            text1.get_size()[0], text2.get_size()[0]
        ), 1.6 * 2 * max(text1.get_size()[1], text2.get_size()[1])
        surface = pygame.Surface((width, height))

        surface.fill((255, 255, 255), (0, 0, width, height))
        pygame.draw.rect(
            surface, (0, 0, 0), (0, 0, width, height), width=int(square_size / 12.5)
        )

        surface.blit(text1, ((width - text1.get_size()[0]) // 2, 0.1 * height))
        surface.blit(
            text2,
            ((width - text2.get_size()[0]) // 2, 0.3 * height + text1.get_size()[1]),
        )

        self.quitmenu = surface

    def render_endmenu(self, square_size, who_won):
        FONT = pygame.freetype.Font(FONT_PATH + "LGGothic.ttf", size=10)
        text, _ = FONT.render(who_won + " wins!", (0, 0, 0), size=square_size / 2)
        width, height = 1.5 * text.get_size()[0], 2 * text.get_size()[1]
        surface = pygame.Surface((width, height))

        surface.fill((255, 255, 255), (0, 0, width, height))
        pygame.draw.rect(
            surface, (0, 0, 0), (0, 0, width, height), width=int(square_size / 12.5)
        )

        surface.blit(
            text,
            ((width - text.get_size()[0]) // 2, (height - text.get_size()[1]) // 2),
        )

        self.endmenu = surface

    def draw_piece(self, piece_name, piece_color, pos):
        self.screen.blit(self.pieces[piece_name][piece_color.value].surface, pos)

    def draw_board(self, pos):
        self.screen.blit(self.board, pos)

    def draw_clock(self, pos0, pos1):
        self.screen.blit(self.clock[0], pos0)
        self.screen.blit(self.clock[1], pos1)

    def draw_bg(self):
        self.screen.fill(self.bg_color)

    def draw_hint(self, pos, square_size, sqr_color=(124, 252, 0)):
        transparent_square = pygame.Surface((square_size, square_size), pygame.SRCALPHA)
        transparent_square.set_alpha(128)
        transparent_square.fill(sqr_color, (0, 0, square_size, square_size))
        self.screen.blit(transparent_square, pos)

    def draw_quittxt(self, pos):
        self.screen.blit(self.quittxt, pos)

    def draw_playertxt(self, pos1, pos2):
        self.screen.blit(self.playertxt[0], pos1)
        self.screen.blit(self.playertxt[1], pos2)

    def draw_quitmenu(self, pos):
        self.screen.blit(self.quitmenu, pos)

    def draw_endmenu(self, pos):
        self.screen.blit(self.endmenu, pos)


class Handler:
    def __init__(self, window, window_size, who_starts, max_time, is_pvp):
        self.window = window
        self.window_size = window_size
        self.board_width = 0.8 * min(window_size)
        self.board_height = 0.8 * min(window_size)
        self.board_pos = (
            (window_size[0] - self.board_width) // 2,
            (window_size[1] - self.board_height) // 2,
        )
        self.square_size = self.board_width // 9
        self.mouse_offset = None

        self.board = None
        self.who_starts = who_starts
        self.max_time = max_time
        self.is_pvp = is_pvp

        self.active_piece = None
        self.active_pos = None
        self.available_squares = None
        self.dragging = False

        self.clk_event = pygame.USEREVENT + 1
        self.clk_started = False
        self.first_moved = False

        self.paused = False
        self.ended = False
        self.who_won: str = ""

        self.renderer = Renderer(window)

        self.setup()

    def setup(self):
        self.board = board.Board(max_time=self.max_time, is_pvp=self.is_pvp)
        self.board.setup()
        self.board.who_starts(self.who_starts)

        pygame.time.set_timer(self.clk_event, 1000)

        self.renderer.render_pieces(self.square_size)
        self.renderer.render_board(self.square_size)
        self.renderer.render_clock(
            time.strftime(
                "%H:%M:%S", time.gmtime(self.board.clock.get_time(COLOR.BLACK))
            ),
            self.square_size,
            COLOR.BLACK,
        )
        self.renderer.render_clock(
            time.strftime(
                "%H:%M:%S", time.gmtime(self.board.clock.get_time(COLOR.WHITE))
            ),
            self.square_size,
            COLOR.WHITE,
        )
        self.renderer.render_quittxt(self.square_size)
        self.renderer.render_playertxt(self.square_size)
        self.renderer.render_quitmenu(self.square_size)

    def handle(self, event, draw=False):
        def snap_to_grid(position):
            x, y = position
            x = (
                self.board_pos[0]
                + max(min(math.floor((x - self.board_pos[0]) / self.square_size), 8), 0)
                * self.square_size
            )
            y = (
                self.board_pos[1]
                + max(min(math.floor((y - self.board_pos[1]) / self.square_size), 8), 0)
                * self.square_size
            )
            return (x, y)

        def get_position(row, col):
            x = self.board_pos[0] + col * self.square_size
            y = self.board_pos[1] + row * self.square_size
            return (x, y)

        def get_rowcol(x, y):
            col = max(min(math.floor((x - self.board_pos[0]) / self.square_size), 8), 0)
            row = max(min(math.floor((y - self.board_pos[1]) / self.square_size), 8), 0)
            return (row, col)

        def in_board(x, y):
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

        if draw:
            r = self.renderer
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
                    self.board_pos[0],
                    self.board_pos[1] - 1.15 * r.clock[1].get_size()[1],
                ),
            )
            r.draw_quittxt(
                (
                    self.board_pos[0],
                    self.board_pos[1]
                    + self.board.size * self.square_size
                    + 0.15 * r.quittxt.get_size()[1],
                ),
            )
            r.draw_playertxt(
                (
                    self.board_pos[0]
                    + (self.board_width - r.playertxt[0].get_size()[0]) // 2,
                    self.board_pos[1]
                    + self.board.size * self.square_size
                    + 0.15 * r.playertxt[0].get_size()[1],
                ),
                (
                    self.board_pos[0]
                    + (self.board_width - r.playertxt[1].get_size()[0]) // 2,
                    self.board_pos[1] - 1.15 * r.playertxt[1].get_size()[1],
                ),
            )

            # If dragging a piece draw available squares
            if self.dragging:
                for x, y in self.available_squares - {
                    (self.active_piece.row, self.active_piece.col)
                }:
                    r.draw_hint(get_position(x, y), self.square_size)
                r.draw_hint(
                    get_position(self.active_piece.row, self.active_piece.col),
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
                        r.draw_piece(piece.name, piece.color, get_position(row, col))

            # Draw active piece
            if self.dragging:
                r.draw_piece(
                    self.active_piece.name, self.active_piece.color, self.active_pos
                )

            # If pause draw pause menu
            if self.paused:
                r.draw_quitmenu(
                    (
                        (self.window_size[0] - r.quitmenu.get_size()[0]) // 2,
                        (self.window_size[1] - r.quitmenu.get_size()[1]) // 2,
                    )
                )

            if self.ended:
                r.draw_endmenu(
                    (
                        (self.window_size[0] - r.endmenu.get_size()[0]) // 2,
                        (self.window_size[1] - r.endmenu.get_size()[1]) // 2,
                    )
                )

        elif event.type == pygame.QUIT:
            pygame.quit()
            exit()

        elif event.type == self.clk_event and not self.ended:
            r = self.renderer
            r.render_clock(
                time.strftime(
                    "%H:%M:%S", time.gmtime(self.board.clock.get_time(COLOR.BLACK))
                ),
                self.square_size,
                COLOR.BLACK,
            )
            r.render_clock(
                time.strftime(
                    "%H:%M:%S", time.gmtime(self.board.clock.get_time(COLOR.WHITE))
                ),
                self.square_size,
                COLOR.WHITE,
            )

            if self.board.clock.get_time(self.board.turn_color) == 0:
                self.ended = True
                self.paused = False
                self.active_piece = None
                self.active_pos = None
                self.available_squares = None
                self.who_won = (
                    "Player 1" if self.board.turn_color == COLOR.WHITE else "Player 2"
                )
                r.render_endmenu(
                    self.square_size,
                    self.who_won,
                )

        elif event.type == pygame.VIDEORESIZE:
            # Resize the window
            self.window_size = pygame.display.get_surface().get_size()

            # Update dimensions
            self.board_width, self.board_height = (
                0.8 * min(event.w, event.h),
                0.8 * min(event.w, event.h),
            )
            self.square_size = self.board_width // 9
            self.board_pos = (
                (self.window.get_width() - self.board_width) // 2,
                (self.window.get_height() - self.board_height) // 2,
            )

            # Rerender surfaces
            r = self.renderer
            r.render_pieces(self.square_size)
            r.render_board(self.square_size)
            r.render_clock(
                time.strftime(
                    "%H:%M:%S", time.gmtime(self.board.clock.get_time(COLOR.BLACK))
                ),
                self.square_size,
                COLOR.BLACK,
            )
            r.render_clock(
                time.strftime(
                    "%H:%M:%S", time.gmtime(self.board.clock.get_time(COLOR.WHITE))
                ),
                self.square_size,
                COLOR.WHITE,
            )
            r.render_quittxt(self.square_size)
            r.render_playertxt(self.square_size)
            r.render_quitmenu(self.square_size)
            if self.ended:
                r.render_endmenu(self.square_size, self.who_won)

        elif (
            event.type == pygame.MOUSEBUTTONDOWN and not self.paused and not self.ended
        ):
            # Check if the piece is clicked
            if in_board(event.pos[0], event.pos[1]):
                row, col = get_rowcol(event.pos[0], event.pos[1])

                if self.board.grid[row][col] != None:
                    # Piece in hand
                    self.dragging = True
                    self.active_piece = self.board.grid[row][col]
                    self.active_pos = get_position(
                        self.active_piece.row, self.active_piece.col
                    )
                    self.available_squares = self.board.get_available(
                        self.active_piece
                    ) | {(self.active_piece.row, self.active_piece.col)}

                    self.mouse_offset = (
                        self.active_pos[0] - event.pos[0],
                        self.active_pos[1] - event.pos[1],
                    )

        elif event.type == pygame.MOUSEBUTTONUP and not self.paused and not self.ended:
            # Release the piece and snap it to the nearest grid square
            if (
                self.dragging
                and get_rowcol(event.pos[0], event.pos[1])
                in self.available_squares
                - {(self.active_piece.row, self.active_piece.col)}
                and in_board(event.pos[0], event.pos[1])
            ):
                if not self.first_moved:
                    self.first_moved = True

                self.dragging = False
                self.active_pos = snap_to_grid(event.pos)
                self.board.move(
                    self.active_piece,
                    get_rowcol(self.active_pos[0], self.active_pos[1]),
                )

                self.active_piece = None
                self.active_pos = None
                self.available_squares = None

                self.board.end_turn()

                if self.board.is_checkmate(self.board.turn_color):
                    self.ended = True
                    self.paused = False
                    self.active_piece = None
                    self.active_pos = None
                    self.available_squares = None
                    self.who_won = (
                        "Player 1"
                        if self.board.turn_color == COLOR.WHITE
                        else "Player 2"
                    )
                    self.renderer.render_endmenu(self.square_size, self.who_won)
                if not self.board.is_pvp:
                    _, x, y, piece, dropped, promoted = self.board.bot.best_move(self.board.turn_color)
                    if dropped:
                        self.board.drop(piece, (x, y))
                    else:
                        self.board.move(piece, (x, y))
                    self.board.end_turn()
                # ==============================================
                print(
                    "Captured by WHITE", self.board.captured[COLOR.WHITE.value].keys()
                )
                print(
                    "Captured by BLACK", self.board.captured[COLOR.BLACK.value].keys()
                )
                # ==============================================

            elif self.dragging:
                self.dragging = False
                self.active_piece = None
                self.active_pos = None
                self.available_squares = None

        elif event.type == pygame.MOUSEMOTION and not self.paused and not self.ended:
            # Move the piece with the mouse
            if self.dragging:
                self.active_pos = (
                    event.pos[0] + self.mouse_offset[0],
                    event.pos[1] + self.mouse_offset[1],
                )

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q and not self.paused and not self.ended:
                self.paused = True
                self.dragging = False
                self.active_piece = None
                self.active_pos = None
                self.available_squares = None

            elif event.key == pygame.K_q and self.ended:
                return "Menu"

            elif event.key == pygame.K_n and self.paused:
                self.paused = False

            elif event.key == pygame.K_y and self.paused:
                return "Menu"
