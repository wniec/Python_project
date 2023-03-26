"""
This code is only a prototype (aka HOT GARBAGE) and needs massive refactoring
"""

import pygame
import math
import board
from pieces import COLOR
from pygame import gfxdraw

pygame.init()

BLACK = (0, 0, 0)
BG_COLOR = (0, 102, 102)
SQR_COLOR_1 = (194, 178, 128)
SQR_COLOR_2 = (150, 111, 51)
SQR_COLOR_3 = (124, 252, 0)

WINDOW_SIZE = (600, 600)
BOARD_SIZE = (550, 550)

window = pygame.display.set_mode(WINDOW_SIZE, pygame.RESIZABLE)
pygame.display.set_caption("Shogi App")

# Initialize the board
board_pos = (
    (WINDOW_SIZE[0] - BOARD_SIZE[0]) // 2,
    (WINDOW_SIZE[1] - BOARD_SIZE[1]) // 2,
)
board_width, board_height = BOARD_SIZE
square_size = board_width // 9

board = board.Board(9)
board.setup()

for color in (COLOR.WHITE, COLOR.BLACK):
    for piece_type in board.active[color.value].keys():
        piece = board.active[color.value][piece_type]
        piece.img = pygame.transform.smoothscale(piece.img, (square_size, square_size))

dragging = False


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


active_piece = None
active_piece_pos = None
available_squares = None

while True:

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

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

        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Check if the piece is clicked
            row, col = get_rowcol(event.pos[0], event.pos[1])
            if board.grid[row][col] != None:
                dragging = True

                active_piece = board.grid[row][col]
                x, y = get_position(active_piece.row, active_piece.col)
                active_piece_pos = (x, y)
                available_squares = board.get_available(active_piece) | {
                    (active_piece.row, active_piece.col)
                }

                mouse_offset = (
                    active_piece_pos[0] - event.pos[0],
                    active_piece_pos[1] - event.pos[1],
                )

        elif event.type == pygame.MOUSEBUTTONUP:
            # Release the piece and snap it to the nearest grid square
            if dragging and get_rowcol(event.pos[0], event.pos[1]) in available_squares:
                dragging = False
                active_piece_pos = snap_to_grid(event.pos)
                board.move(
                    active_piece, get_rowcol(active_piece_pos[0], active_piece_pos[1])
                )
                active_piece = None
                active_piece_pos = None

                # ==============================================
                print("Captured by WHITE", board.captured[COLOR.WHITE.value].keys())
                print("Captured by BLACK", board.captured[COLOR.BLACK.value].keys())
                # ==============================================

            elif dragging:
                dragging = False
                active_piece_pos = snap_to_grid(event.pos)
                active_piece = None
                active_piece_pos = None

        elif event.type == pygame.MOUSEMOTION and dragging:
            # Move the piece with the mouse
            active_piece_pos = (
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
    if dragging:
        for x, y in available_squares:
            transparent_square = pygame.Surface((square_size, square_size))
            transparent_square.set_alpha(128)
            transparent_square.fill(SQR_COLOR_3)
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
            if board.grid[row][col] != None and board.grid[row][col] != active_piece:
                piece = board.grid[row][col]
                piece.img = pygame.transform.smoothscale(
                    piece.img, (square_size, square_size)
                )
                window.blit(piece.img, get_position(piece.row, piece.col))

    if dragging:
        active_piece.img = pygame.transform.smoothscale(
            active_piece.img, (square_size, square_size)
        )
        window.blit(active_piece.img, active_piece_pos)

    # Update the display
    pygame.display.update()
