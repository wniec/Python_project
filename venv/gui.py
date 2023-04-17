"""
This code is only a prototype and needs massive refactoring
"""

import pygame
import math
import board
import io
import os
import time
from pygame import gfxdraw
from pieces import COLOR

pygame.init()

BG_COLOR = (40, 40, 40)
SQR_COLOR_1 = (235, 234, 221)
SQR_COLOR_2 = (63, 90, 54)
SQR_COLOR_HINT = (124, 252, 0)
WINDOW_SIZE = (600, 600)
BOARD_SIZE = (550, 550)

window = pygame.display.set_mode(WINDOW_SIZE, pygame.RESIZABLE)
pygame.display.set_caption("Shogi Appl")

# Initialize the board
board_pos = (
    (WINDOW_SIZE[0] - BOARD_SIZE[0]) // 2,
    (WINDOW_SIZE[1] - BOARD_SIZE[1]) // 2,
)
board_width, board_height = BOARD_SIZE
square_size = board_width // 9

board = board.Board()
board.setup()
board.who_starts("Black")


def load_and_scale_svg(filename, scale):
    svg_string = open(filename, "rt").read()
    start = svg_string.find("<svg")
    if start > 0:
        svg_string = (
            svg_string[: start + 4]
            + f' transform="scale({scale})"'
            + svg_string[start + 4 :]
        )
    return pygame.image.load(io.BytesIO(svg_string.encode()))


INIT_SCALE = 1.67
INIT_SIZE = square_size
prefix = "resources/international/"
IMG_PATH_DICT = {
    "P": (prefix + "0FU.svg", prefix + "1FU.svg"),
    "L": (prefix + "0KY.svg", prefix + "1KY.svg"),
    "N": (prefix + "0KE.svg", prefix + "1KE.svg"),
    "S": (prefix + "0GI.svg", prefix + "1GI.svg"),
    "G": (prefix + "0KI.svg", prefix + "1KI.svg"),
    "B": (prefix + "0KA.svg", prefix + "1KA.svg"),
    "R": (prefix + "0HI.svg", prefix + "1HI.svg"),
    "D": (prefix + "0RY.svg", prefix + "1RY.svg"),
    "H": (prefix + "0FU.svg", prefix + "1FU.svg"),
    "K": (prefix + "0OU.svg", prefix + "1OU.svg"),
}
IMGS = {}


def update_imgs():
    for key in IMG_PATH_DICT.keys():
        IMGS[key] = (
            load_and_scale_svg(
                IMG_PATH_DICT[key][COLOR.BLACK.value],
                INIT_SCALE * square_size / INIT_SIZE,
            ),
            load_and_scale_svg(
                IMG_PATH_DICT[key][COLOR.WHITE.value],
                INIT_SCALE * square_size / INIT_SIZE,
            ),
        )


update_imgs()


def snap_to_grid(position):
    x, y = position
    x = (
        board_pos[0]
        + max(min(math.floor((x - board_pos[0]) / square_size), 8), 0) * square_size
    )
    y = (
        board_pos[1]
        + max(min(math.floor((y - board_pos[1]) / square_size), 8), 0) * square_size
    )
    return (x, y)


def get_position(row, col):
    x = board_pos[0] + col * square_size
    y = board_pos[1] + row * square_size
    return (x, y)


def get_rowcol(x, y):
    col = max(min(math.floor((x - board_pos[0]) / square_size), 8), 0)
    row = max(min(math.floor((y - board_pos[1]) / square_size), 8), 0)
    return (row, col)


ACTIVE_PIECE = None
ACTIVE_PIECE_POS = None
AVAILABLE_SQRS = None
DRAGGING = False

CLK_STARTED = False
FIRST_MOVED = False
CLK_EVENT, DELTA_T = pygame.USEREVENT + 1, 1000
pygame.time.set_timer(CLK_EVENT, DELTA_T)

while True:
    if not CLK_STARTED and FIRST_MOVED:
        board.clock.switch_to(board.turn_color)
        CLK_STARTED = True

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        elif event.type == CLK_EVENT:
            os.system("cls")
            print("*" * 42)
            print(
                "Black time:",
                time.strftime(
                    "%H:%M:%S", time.gmtime(board.clock.get_time(COLOR.BLACK))
                ),
            )
            print(
                "White time:",
                time.strftime(
                    "%H:%M:%S", time.gmtime(board.clock.get_time(COLOR.WHITE))
                ),
            )
            print("*" * 42)

        elif event.type == pygame.VIDEORESIZE:
            # Resize the window and recalculate the square size
            window = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            board_width, board_height = (
                min(event.w, event.h) - 50,
                min(event.w, event.h) - 50,
            )
            square_size = board_width // 9
            board_pos = (
                (window.get_width() - board_width) // 2,
                (window.get_height() - board_height) // 2,
            )

            update_imgs()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Check if the piece is clicked
            if (
                board_pos[0] <= event.pos[0] <= board_pos[0] + board.size * square_size
                and board_pos[1]
                <= event.pos[1]
                <= board_pos[1] + board.size * square_size
            ):
                row, col = get_rowcol(event.pos[0], event.pos[1])
                if board.grid[row][col] != None:
                    DRAGGING = True

                    ACTIVE_PIECE = board.grid[row][col]
                    x, y = get_position(ACTIVE_PIECE.row, ACTIVE_PIECE.col)
                    ACTIVE_PIECE_POS = (x, y)
                    AVAILABLE_SQRS = board.get_available(ACTIVE_PIECE) | {
                        (ACTIVE_PIECE.row, ACTIVE_PIECE.col)
                    }

                    mouse_offset = (
                        ACTIVE_PIECE_POS[0] - event.pos[0],
                        ACTIVE_PIECE_POS[1] - event.pos[1],
                    )

        elif event.type == pygame.MOUSEBUTTONUP:
            # Release the piece and snap it to the nearest grid square
            if (
                DRAGGING
                and get_rowcol(event.pos[0], event.pos[1])
                in AVAILABLE_SQRS - {(ACTIVE_PIECE.row, ACTIVE_PIECE.col)}
                and board_pos[0]
                <= event.pos[0]
                <= board_pos[0] + board.size * square_size
                and board_pos[1]
                <= event.pos[1]
                <= board_pos[1] + board.size * square_size
            ):
                if not FIRST_MOVED:
                    FIRST_MOVED = True
                DRAGGING = False
                ACTIVE_PIECE_POS = snap_to_grid(event.pos)
                board.move(
                    ACTIVE_PIECE, get_rowcol(ACTIVE_PIECE_POS[0], ACTIVE_PIECE_POS[1])
                )
                ACTIVE_PIECE = None
                ACTIVE_PIECE_POS = None

                board.end_turn()

                # ==============================================
                # print("Captured by WHITE", board.captured[COLOR.WHITE.value].keys())
                # print("Captured by BLACK", board.captured[COLOR.BLACK.value].keys())
                # ==============================================

            elif DRAGGING:
                DRAGGING = False
                ACTIVE_PIECE_POS = snap_to_grid(event.pos)
                ACTIVE_PIECE = None
                ACTIVE_PIECE_POS = None

        elif event.type == pygame.MOUSEMOTION:
            if (
                board_pos[0] <= event.pos[0] <= board_pos[0] + board.size * square_size
                and board_pos[1]
                <= event.pos[1]
                <= board_pos[1] + board.size * square_size
            ):
                row, col = get_rowcol(event.pos[0], event.pos[1])

            # Move the piece with the mouse
            if DRAGGING:
                ACTIVE_PIECE_POS = (
                    event.pos[0] + mouse_offset[0],
                    event.pos[1] + mouse_offset[1],
                )

    # Clear the window
    window.fill(BG_COLOR)

    # Draw the squares of the chessboard
    for x in range(9):
        for y in range(9):
            square_color = SQR_COLOR_1 if (x + y) % 2 == 0 else SQR_COLOR_2
            pygame.draw.rect(
                window,
                square_color,
                (
                    board_pos[0] + x * square_size,
                    board_pos[1] + y * square_size,
                    square_size,
                    square_size,
                ),
            )

    # If dragging a piece draw available squares
    if DRAGGING:
        for x, y in AVAILABLE_SQRS:
            transparent_square = pygame.Surface(
                (square_size, square_size), pygame.SRCALPHA
            )
            transparent_square.set_alpha(128)

            if board.grid[x][y] != None:
                transparent_square.fill(SQR_COLOR_HINT)
            else:
                gfxdraw.aacircle(
                    transparent_square,
                    square_size // 2,
                    square_size // 2,
                    square_size // 7,
                    SQR_COLOR_HINT,
                )
                gfxdraw.filled_circle(
                    transparent_square,
                    square_size // 2,
                    square_size // 2,
                    square_size // 7,
                    SQR_COLOR_HINT,
                )

            window.blit(
                transparent_square,
                (
                    board_pos[0] + y * square_size,
                    board_pos[1] + x * square_size,
                ),
            )

    # Draw the pieces
    for row in range(board.size):
        for col in range(board.size):
            if board.grid[row][col] != None and board.grid[row][col] != ACTIVE_PIECE:
                piece = board.grid[row][col]
                window.blit(IMGS[piece.name][piece.color.value], get_position(row, col))

    # Draw active piece
    if DRAGGING:
        window.blit(IMGS[ACTIVE_PIECE.name][ACTIVE_PIECE.color.value], ACTIVE_PIECE_POS)

    # Update the display
    pygame.display.update()
