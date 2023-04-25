import queue
from pieces import COLOR
import pieces
from pieces import pieces_dict
from board import Board
import numpy as np
import json
import os
import time


def change_grid(x, y, piece, grid, drop):
    # changing grid according to move
    piece_before = grid[x][y]
    if not drop:
        grid[piece.row][piece.col] = None
    grid[x][y] = piece
    return piece_before


def revert_change_grid(old_x, old_y, piece, piece_before, grid):
    # changing grid according to move
    x, y = piece.pos()
    grid[x][y] = piece_before
    grid[old_x][old_y] = piece


def read_matrix():
    with open("values.json", "r") as read_file:
        decoded_array = json.load(read_file)
        matrix = np.asarray(decoded_array["valueMatrix"])
        return matrix


class Bot:
    def __init__(self, board, depth, width):
        self.matrix = read_matrix()
        self.board = board
        self.depth = depth
        self.width = width

    def test_move(self, x: int, y: int, piece: pieces.Piece, grid: [[]]) -> int:
        current_value = self.matrix[pieces_dict[piece.name], piece.row, piece.col]
        piece_value = 0
        if grid[x][y] is not None and grid[x][y].color == piece.color.opposite():
            captured = grid[x][y]
            piece_value = captured.value_in_hand + captured.value + self.matrix[
                pieces_dict[captured.name], 8 - x, 8 - y]
        new_value = self.matrix[pieces_dict[piece.name], x, y]
        return new_value - current_value + piece_value

    def test_drop(self, x: int, y: int, piece: pieces.Piece) -> int:
        current_value = piece.value_in_hand
        new_value = self.matrix[pieces_dict[piece.name], x, y] + piece.value
        return new_value - current_value

    def test_best_moves_depth1(self, color: pieces.COLOR, grid: list[list]) -> list[tuple]:
        # side is 0 or 1 -depending on whose moves are we testing
        best = queue.PriorityQueue()
        result = []
        for piece_sign in self.board.active[color.value]:
            piece = self.board.active[color.value][piece_sign]
            possible = self.board.get_available(piece, True)
            for x, y in possible:
                move_result = self.test_move(x, y, piece, grid)
                best.put((-move_result, x, y, piece, False))
        for piece_sign in self.board.captured[color.value]:
            piece = self.board.captured[color.value][piece_sign]
            possible = self.board.get_available_drops(piece, True)
            for x, y in possible:
                move_result = self.test_drop(x, y, piece)
                best.put((-move_result, x, y, piece, True))
        i = 0
        while i < self.width and not best.empty():
            move = best.get()
            negative_value, x, y, piece, dropped = move
            result.append((-negative_value, x, y, piece, dropped))
            i += 1
        # returns up to n best moves
        # checking all would take too long
        return result

    def test_best_moves(self, color, depth, grid) -> (int, int, int, pieces.Piece, list[list]):
        # function, that returns the best move for given depth
        # tests @width moves for depth 1, for each calculating an opposite move with @depth -1
        if depth == 1:
            return self.test_best_moves_depth1(color, grid)[0]
        else:
            potential_moves = self.test_best_moves_depth1(color, grid)
            best_move = None
            best_move_val = -float("inf")
            for move in potential_moves:
                value, x, y, piece, dropped = move
                old_x, old_y = piece.pos()
                piece_before = change_grid(x, y, piece, grid, dropped)
                opposite_move = self.test_best_moves(color.opposite(), depth - 1, grid)
                revert_change_grid(old_x, old_y, piece, piece_before, grid)
                if opposite_move is not None and value - opposite_move[0] > best_move_val:
                    best_move = (best_move_val, x, y, piece, dropped)
            return best_move

    def play_against_bot(self, bot) -> pieces.COLOR:
        # function for testing bot
        # A bot vs bot game: returns COLOR of winner
        i = 0
        while i < 200:
            grid = [row[:] for row in self.board.grid]
            move = self.test_best_moves(COLOR.WHITE, self.depth, grid)
            if move is None or self.board.is_checkmate(COLOR.WHITE):
                return COLOR.BLACK
            _, x, y, piece, dropped = move
            if dropped:
                self.board.drop(piece, (x, y))
            else:
                self.board.move(piece, (x, y))
            self.board.end_turn()
            os.system('cls')
            self.board.show()
            time.sleep(1)
            grid = [row[:] for row in self.board.grid]
            move = bot.test_best_moves(COLOR.BLACK, bot.depth, grid)
            if move is None or self.board.is_checkmate(COLOR.BLACK):
                return COLOR.WHITE
            _, x, y, piece, dropped = move
            if dropped:
                self.board.drop(piece, (x, y))
            else:
                self.board.move(piece, (x, y))
            self.board.end_turn()
            os.system('cls')
            self.board.show()
            time.sleep(1)
            i += 1
        side1, side2 = self.board.evaluate()
        return COLOR.WHITE if side1 < side2 else COLOR.BLACK


b = Board(9)
b.setup()
b.who_starts(option="White")
b1 = Bot(b, 2, 4)
b2 = Bot(b, 4, 8)
b1.play_against_bot(b2)
