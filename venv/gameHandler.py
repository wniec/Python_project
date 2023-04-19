import pygame
import pygame.freetype
import numpy as np
import math
import time
import board
from pieces import COLOR
from sprite import Sprite

PATH = "rsrc/sprites/"
FONT_PATH = "rsrc/fonts/"


class Renderer:
    def __init__(self, screen):
        self.screen = screen

        self.pieces = {
            name: (
                Sprite(np.load(PATH + name + "0.npy"), 100),
                Sprite(np.load(PATH + name + "1.npy"), 100),
            )
            for name in ("P", "L", "N", "S", "G", "B", "R", "K")
        }
        self.board = None
        self.clock = [None, None]
        self.bg_color = (0, 0, 0)
        self.quittxt = None
        self.quitmenu = None

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

    def draw_quitmenu(self, pos):
        self.screen.blit(self.quitmenu, pos)


class Handler:
    def __init__(self, window, window_size, who_starts, max_time):
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

        self.active_piece = None
        self.active_pos = None
        self.available_squares = None
        self.dragging = False

        self.clk_event = pygame.USEREVENT + 1
        self.clk_started = False
        self.first_moved = False

        self.paused = False

        self.renderer = Renderer(window)

        self.setup()

    def setup(self):
        self.board = board.Board(max_time=self.max_time)
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
        self.renderer.render_quitmenu(self.square_size)


def handle(event, h: Handler, draw=False):
    def snap_to_grid(position):
        x, y = position
        x = (
            h.board_pos[0]
            + max(min(math.floor((x - h.board_pos[0]) / h.square_size), 8), 0)
            * h.square_size
        )
        y = (
            h.board_pos[1]
            + max(min(math.floor((y - h.board_pos[1]) / h.square_size), 8), 0)
            * h.square_size
        )
        return (x, y)

    def get_position(row, col):
        x = h.board_pos[0] + col * h.square_size
        y = h.board_pos[1] + row * h.square_size
        return (x, y)

    def get_rowcol(x, y):
        col = max(min(math.floor((x - h.board_pos[0]) / h.square_size), 8), 0)
        row = max(min(math.floor((y - h.board_pos[1]) / h.square_size), 8), 0)
        return (row, col)

    def in_board(x, y):
        p = h.board_pos[0] <= x <= h.board_pos[0] + h.board.size * h.square_size
        q = h.board_pos[1] <= y <= h.board_pos[1] + h.board.size * h.square_size
        return p and q

    if draw:
        r = h.renderer

        # Clear the window
        r.draw_bg()

        # Draw the squares of the chessboard
        r.draw_board(h.board_pos)

        # Draw clocks
        r.draw_clock(
            (
                h.board_pos[0]
                + h.board.size * h.square_size
                - r.clock[0].get_size()[0],
                h.board_pos[1]
                + h.board.size * h.square_size
                + 0.15 * r.clock[0].get_size()[1],
            ),
            (h.board_pos[0], h.board_pos[1] - 1.15 * r.clock[1].get_size()[1]),
        )

        # Draw Quit text
        r.draw_quittxt(
            (
                h.board_pos[0],
                h.board_pos[1]
                + h.board.size * h.square_size
                + 0.15 * r.quittxt.get_size()[1],
            ),
        )

        # If dragging a piece draw available squares
        if h.dragging:
            for x, y in h.available_squares - {
                (h.active_piece.row, h.active_piece.col)
            }:
                r.draw_hint(get_position(x, y), h.square_size)
            r.draw_hint(
                get_position(h.active_piece.row, h.active_piece.col),
                h.square_size,
                sqr_color=(169, 169, 169),
            )

        # Draw the pieces
        for row in range(h.board.size):
            for col in range(h.board.size):
                if (
                    h.board.grid[row][col] != None
                    and h.board.grid[row][col] != h.active_piece
                ):
                    piece = h.board.grid[row][col]
                    r.draw_piece(piece.name, piece.color, get_position(row, col))

        # Draw active piece
        if h.dragging:
            r.draw_piece(h.active_piece.name, h.active_piece.color, h.active_pos)

        # If pause draw pause menu
        if h.paused:
            r.draw_quitmenu(
                (
                    (h.window_size[0] - r.quitmenu.get_size()[0]) // 2,
                    (h.window_size[1] - r.quitmenu.get_size()[1]) // 2,
                )
            )

    elif event.type == pygame.QUIT:
        pygame.quit()
        exit()

    elif event.type == h.clk_event:
        r = h.renderer
        r.render_clock(
            time.strftime("%H:%M:%S", time.gmtime(h.board.clock.get_time(COLOR.BLACK))),
            h.square_size,
            COLOR.BLACK,
        )
        r.render_clock(
            time.strftime("%H:%M:%S", time.gmtime(h.board.clock.get_time(COLOR.WHITE))),
            h.square_size,
            COLOR.WHITE,
        )

    elif event.type == pygame.VIDEORESIZE:
        # Resize the window
        h.window_size = pygame.display.get_surface().get_size()

        # Update dimensions
        h.board_width, h.board_height = (
            0.8 * min(event.w, event.h),
            0.8 * min(event.w, event.h),
        )
        h.square_size = h.board_width // 9
        h.board_pos = (
            (h.window.get_width() - h.board_width) // 2,
            (h.window.get_height() - h.board_height) // 2,
        )

        # Rerender surfaces
        r = h.renderer
        r.render_pieces(h.square_size)
        r.render_board(h.square_size)
        r.render_clock(
            time.strftime("%H:%M:%S", time.gmtime(h.board.clock.get_time(COLOR.BLACK))),
            h.square_size,
            COLOR.BLACK,
        )
        r.render_clock(
            time.strftime("%H:%M:%S", time.gmtime(h.board.clock.get_time(COLOR.WHITE))),
            h.square_size,
            COLOR.WHITE,
        )
        r.render_quittxt(h.square_size)
        r.render_quitmenu(h.square_size)

    elif event.type == pygame.MOUSEBUTTONDOWN and not h.paused:
        # Check if the piece is clicked
        if in_board(event.pos[0], event.pos[1]):
            row, col = get_rowcol(event.pos[0], event.pos[1])

            if h.board.grid[row][col] != None:
                # Piece in hand
                h.dragging = True
                h.active_piece = h.board.grid[row][col]
                h.active_pos = get_position(h.active_piece.row, h.active_piece.col)
                h.available_squares = h.board.get_available(h.active_piece) | {
                    (h.active_piece.row, h.active_piece.col)
                }

                h.mouse_offset = (
                    h.active_pos[0] - event.pos[0],
                    h.active_pos[1] - event.pos[1],
                )

    elif event.type == pygame.MOUSEBUTTONUP and not h.paused:
        # Release the piece and snap it to the nearest grid square
        if (
            h.dragging
            and get_rowcol(event.pos[0], event.pos[1])
            in h.available_squares - {(h.active_piece.row, h.active_piece.col)}
            and in_board(event.pos[0], event.pos[1])
        ):
            if not h.first_moved:
                h.first_moved = True

            h.dragging = False
            h.active_pos = snap_to_grid(event.pos)
            h.board.move(h.active_piece, get_rowcol(h.active_pos[0], h.active_pos[1]))

            h.active_piece = None
            h.active_pos = None
            h.available_squares = None

            h.board.end_turn()

            # ==============================================
            print("Captured by WHITE", h.board.captured[COLOR.WHITE.value].keys())
            print("Captured by BLACK", h.board.captured[COLOR.BLACK.value].keys())
            # ==============================================

        elif h.dragging:
            h.dragging = False
            h.active_piece = None
            h.active_pos = None
            h.available_squares = None

    elif event.type == pygame.MOUSEMOTION and not h.paused:
        # Move the piece with the mouse
        if h.dragging:
            h.active_pos = (
                event.pos[0] + h.mouse_offset[0],
                event.pos[1] + h.mouse_offset[1],
            )

    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_q and not h.paused:
            h.paused = True
            h.dragging = False
            h.active_piece = None
            h.active_pos = None
            h.available_squares = None
        elif event.key == pygame.K_n and h.paused:
            h.paused = False
        elif event.key == pygame.K_y and h.paused:
            return "Menu"
