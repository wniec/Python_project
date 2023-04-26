import queue
from pieces import COLOR
import pieces
from pieces import pieces_dict
from board import Board
import numpy as np
import json
import os
import time


def matrix_index(x: int, y: int, color: COLOR):
    if color == COLOR.WHITE:
        return x, y
    return 8 - x, 8 - y


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

    def test_move(self, x: int, y: int, piece: pieces.Piece) -> int:
        matrix_x, matrix_y = matrix_index(x, y, piece.color)
        new_mx, new_my = matrix_index(piece.row, piece.col, piece.color)
        current_value = self.matrix[pieces_dict[piece.name], new_mx, new_my]
        piece_value = 0
        king_pos = self.board.kings[piece.color.value].pos()
        if piece.name == 'K':
            king_pos = (x, y)
        if len(self.board.get_attacking(king_pos, piece.color.opposite())) > 0:
            return None
        if self.board.grid[x][y] is not None and self.board.grid[x][y].color == piece.color.opposite():
            captured = self.board.grid[x][y]
            piece_value = captured.value_in_hand + captured.value + self.matrix[
                pieces_dict[captured.name], 8 - matrix_x, 8 - matrix_y]
        new_value = self.matrix[pieces_dict[piece.name], matrix_x, matrix_y]
        return new_value - current_value + piece_value

    def test_drop(self, x: int, y: int, piece: pieces.Piece) -> int:
        matrix_x, matrix_y = matrix_index(x, y, piece.color)
        current_value = piece.value_in_hand
        new_value = self.matrix[pieces_dict[piece.name], matrix_x, matrix_y] + piece.value
        return new_value - current_value

    def test_best_moves_depth1(self, color: pieces.COLOR) -> list[tuple]:
        # side is 0 or 1 -depending on whose moves are we testing
        best = queue.PriorityQueue()
        result = []
        for piece_sign in self.board.active[color.value]:
            piece = self.board.active[color.value][piece_sign]
            possible = self.board.get_available(piece, True)
            for x, y in possible:
                move_result = self.test_move(x, y, piece)
                if move_result:
                    best.put((-move_result, x, y, piece, False))
        for piece_sign in self.board.captured[color.value]:
            piece = self.board.captured[color.value][piece_sign]
            possible = self.board.get_available_drops(piece, True)
            for x, y in possible:
                drop_result = self.test_drop(x, y, piece)
                best.put((-drop_result, x, y, piece, True))
        i = 0
        while i < self.width and not best.empty():
            move = best.get()
            negative_value, x, y, piece, dropped = move
            result.append((-negative_value, x, y, piece, dropped))
            i += 1
        # returns up to n best moves
        # checking all would take too long
        return result

    def test_best_moves(self, color, depth) -> (int, int, int, pieces.Piece, list[list]):
        # function, that returns the best move for given depth
        # tests @width moves for depth 1, for each calculating an opposite move with @depth -1
        if depth == 1:
            result = self.test_best_moves_depth1(color)
            if result:
                return result[0]
            return None
        else:
            potential_moves = self.test_best_moves_depth1(color)
            best_move = None
            best_move_val = -float("inf")
            for move in potential_moves:
                value, x, y, piece, dropped = move
                old_pos = piece.pos()
                captured = self.board.grid[x][y]
                self.board.move(piece, (x, y))
                opposite_move = self.test_best_moves(color.opposite(), depth - 1)
                if not dropped:
                    self.board.revert_move(piece, captured, old_pos)
                else:
                    self.board.revert_drop(piece)
                if opposite_move is not None and value - opposite_move[0] > best_move_val:
                    best_move = (best_move_val, x, y, piece, dropped)
            return best_move

    def play_against_bot(self, bot) -> pieces.COLOR:
        # function for testing bot
        # A bot vs bot game: returns COLOR of winner
        i = 0
        while i < 200:
            move = self.test_best_moves(COLOR.WHITE, self.depth)
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
            time.sleep(0.2)
            move = bot.test_best_moves(COLOR.BLACK, bot.depth)
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
            time.sleep(0.2)
            i += 1
        side1, side2 = self.board.evaluate()
        return COLOR.WHITE if side1 < side2 else COLOR.BLACK


b = Board(9)
b.setup()
b.who_starts(option="White")
b1 = Bot(b, 2, 4)
b2 = Bot(b, 5, 4)
b1.play_against_bot(b2)
