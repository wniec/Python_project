import queue
from pieces import COLOR
import pieces
from pieces import pieces_dict
from board import Board
import numpy as np
import json
import time


def read_matrix():
    with open("values.json", "r") as read_file:
        decoded_array = json.load(read_file)
        matrix = np.asarray(decoded_array["valueMatrix"])
        return matrix


def matrix_position(position, color: COLOR):
    x, y = position
    if color == COLOR.WHITE:
        return x, y
    return 8 - x, 8 - y


class Bot:
    def __init__(self, board, depth, width):
        self.matrix = read_matrix()
        self.board = board
        self.depth = depth
        self.width = width

    def test_move(self, piece, x, y):
        old_pos = piece.pos()
        captured = self.board.grid[x][y]
        self.board.move(piece, (x, y))
        move_result = self.evaluate(piece.color)
        self.board.revert_move(piece, captured, old_pos)
        return move_result

    def test_drop(self, piece, x, y):
        self.board.drop(piece, (x, y))
        drop_result = self.evaluate(piece.color)
        self.board.revert_drop(piece)
        return drop_result

    def evaluate(self, color: COLOR):
        if self.board.get_attacking(self.board.kings[color.value].pos(), color.opposite()):
            return -float("inf")
        side_0 = sum(piece.value for piece in self.board.captured[color.value].values())
        side_0 += sum(piece.value for piece in self.board.active[color.value].values())
        side_1 = sum(piece.value for piece in self.board.captured[color.opposite().value].values())
        side_1 += sum(piece.value for piece in self.board.active[color.opposite().value].values())
        side_0 += sum(self.matrix[pieces_dict[piece.name]][matrix_position(piece.pos(), color)] for key, piece in
                      self.board.active[color.value].items())
        side_1 += sum(self.matrix[pieces_dict[piece.name]][matrix_position(piece.pos(), piece.color)] for key, piece in
                      self.board.active[color.opposite().value].items())
        return side_0 - side_1

    def test_best_moves_depth1(self, color: pieces.COLOR) -> list[tuple]:
        best = queue.PriorityQueue()
        result = []

        for piece_sign in list(self.board.active[color.value]):
            piece = self.board.active[color.value][piece_sign]
            possible = self.board.get_available(piece, True)
            for x, y in possible:
                if piece.can_promote(x):
                    piece.promote()
                    best.put((-self.test_move(piece, x, y), x, y, piece, False, True))
                    piece.degrade()
                best.put((-self.test_move(piece, x, y), x, y, piece, False, False))

        for piece_sign in list(self.board.captured[color.value]):
            piece = self.board.captured[color.value][piece_sign]
            possible = self.board.get_available_drops(piece, True)
            for x, y in possible:
                best.put((-self.test_drop(piece, x, y), x, y, piece, True, False))
        i = 0
        while i < self.width and not best.empty():
            move = best.get()
            negative_value, x, y, piece, dropped, promoted = move
            if negative_value is not float("inf"):
                result.append((-negative_value, x, y, piece, dropped, promoted))
            i += 1
        # returns up to n best moves
        # checking all would take too long
        return result

    def test_best_moves(self, color, depth) -> (int, int, int, pieces.Piece, list[list]):
        """
        function, that returns the best move for given depth
        tests width moves for :param depth 1, for each calculating an opposite move with depth -1
        """
        if depth == 1:
            result = self.test_best_moves_depth1(color)
            if result and result[0][0] is not -float("inf"):
                return result[0]

        else:
            potential_moves = self.test_best_moves_depth1(color)
            best_move = None
            worst_move_val = -float("inf")
            for move in potential_moves:
                value, x, y, piece, dropped, promoted = move
                old_pos = piece.pos()
                captured = self.board.grid[x][y]
                if dropped:
                    self.board.drop(piece, (x, y))
                else:
                    self.board.move(piece, (x, y))
                opposite_move = self.test_best_moves(color.opposite(), depth - 1)
                if dropped:
                    self.board.revert_drop(piece)
                else:
                    self.board.revert_move(piece, captured, old_pos)
                if opposite_move is not None and -opposite_move[0] > worst_move_val:
                    best_move = (-opposite_move[0], x, y, piece, dropped, promoted)
                    worst_move_val = -opposite_move[0]
            return best_move

    def play_against_bot(self, bot) -> pieces.COLOR:
        # function for testing bot
        # A bot vs bot game: returns COLOR of winner
        i = 0
        while i < 200:
            move = self.test_best_moves(COLOR.WHITE, self.depth)
            if move is None or self.board.is_checkmate(COLOR.WHITE):
                return COLOR.BLACK
            _, x, y, piece, dropped, promoted = move
            if promoted:
                piece.promote()
            if dropped:
                self.board.drop(piece, (x, y))
            else:
                self.board.move(piece, (x, y))
            self.board.end_turn()
            self.board.show()
            time.sleep(0.2)
            move = bot.test_best_moves(COLOR.BLACK, bot.depth)
            if move is None or self.board.is_checkmate(COLOR.BLACK):
                return COLOR.WHITE
            _, x, y, piece, dropped, promoted = move
            if promoted:
                piece.promote()
            if dropped:
                self.board.drop(piece, (x, y))
            else:
                self.board.move(piece, (x, y))
            self.board.end_turn()
            self.board.show()
            time.sleep(0.2)
            i += 1
        result = self.evaluate(COLOR.WHITE)
        return COLOR.WHITE if result > 0 else COLOR.BLACK


b = Board(9)
b.setup()
b.who_starts(option="White")
b1 = Bot(b, 2, 4)
b2 = Bot(b, 3, 4)
b1.play_against_bot(b2)
