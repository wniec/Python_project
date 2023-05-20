import queue
from pieces import COLOR
import pieces
from pieces import pieces_dict
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

    def __test_move(self, piece, x, y, depth):
        old_pos = piece.pos()
        captured = self.board.grid[x][y]
        was_promoted = None
        if captured:
            was_promoted = captured.promoted
        self.board.move(piece, (x, y))
        move_result = self.__evaluate(piece.color, depth)
        self.board.revert_move(piece, captured, old_pos, was_promoted)
        return move_result

    def __test_drop(self, piece, x, y, depth):
        self.board.drop(piece, (x, y))
        drop_result = self.__evaluate(piece.color, depth)
        self.board.revert_drop(piece)
        return drop_result

    def __evaluate(self, color: COLOR, depth: int):
        if self.board.get_attacking(
            self.board.kings[color.value].pos(), color.opposite()
        ):
            return -depth * 10_000
        side_0 = sum(piece.value for piece in self.board.captured[color.value].values())
        side_0 += sum(piece.value for piece in self.board.active[color.value].values())
        side_1 = sum(
            piece.value
            for piece in self.board.captured[color.opposite().value].values()
        )
        side_1 += sum(
            piece.value for piece in self.board.active[color.opposite().value].values()
        )
        side_0 += sum(
            self.matrix[pieces_dict[piece.name]][matrix_position(piece.pos(), color)]
            for key, piece in self.board.active[color.value].items()
        )
        side_1 += sum(
            self.matrix[pieces_dict[piece.name]][
                matrix_position(piece.pos(), piece.color)
            ]
            for key, piece in self.board.active[color.opposite().value].items()
        )
        return side_0 - side_1

    def __add_move(self, best_queue, color: COLOR, piece_sign: str):
        piece = self.board.active[color.value][piece_sign]
        possible = self.board.get_available(piece, True)
        for x, y in possible:
            if piece.can_promote(x):
                piece.promote()
                best_queue.put(
                    (-self.__test_move(piece, x, y, 1), x, y, piece, False, True)
                )
                piece.degrade()
            best_queue.put(
                (-self.__test_move(piece, x, y, 1), x, y, piece, False, False)
            )

    def __add_drop(self, best_queue, color: COLOR, piece_sign: str):
        piece = self.board.captured[color.value][piece_sign]
        possible = self.board.get_available_drops(piece, True)
        for x, y in possible:
            best_queue.put(
                (-self.__test_drop(piece, x, y, 1), x, y, piece, True, False)
            )

    def __test_best_moves_depth1(self, color: pieces.COLOR) -> list[tuple]:
        best = queue.PriorityQueue()
        result = []

        for piece_sign in list(self.board.active[color.value]):
            self.__add_move(best, color, piece_sign)

        for piece_sign in list(self.board.captured[color.value]):
            self.__add_drop(best, color, piece_sign)

        i = 0
        while i < self.width and not best.empty():
            move = best.get()
            negative_value, x, y, piece, dropped, promoted = move
            result.append((-negative_value, x, y, piece, dropped, promoted))
            i += 1
        # returns up to n best moves
        # checking all would take too long
        return result

    def best_move(self, color: COLOR, depth: int = None):
        """
        function, that returns the best move for given depth
        tests width moves for depth, for each calculating an opposite move with depth -1
        :param color:
        :param depth: depth: current depth of search
        """
        if depth is None:
            depth = self.depth
        if depth == 1:
            result = self.__test_best_moves_depth1(color)
            if result and result[0][0] > -10_000:
                return result[0]

        else:
            potential_moves = self.__test_best_moves_depth1(color)
            best_move = None
            worst_move_val = float("inf")
            for move in potential_moves:
                value, x, y, piece, dropped, promoted = move
                old_pos = piece.pos()
                captured = self.board.grid[x][y]
                was_promoted = None
                if captured:
                    was_promoted = captured.promoted
                if dropped:
                    self.board.drop(piece, (x, y))
                else:
                    self.board.move(piece, (x, y))
                opposite_move = self.best_move(color.opposite(), depth - 1)
                if dropped:
                    self.board.revert_drop(piece)
                else:
                    self.board.revert_move(piece, captured, old_pos, was_promoted)
                if (
                    opposite_move is not None
                    and opposite_move[0] - 0.1 * value < worst_move_val
                ):
                    best_move = (
                        -opposite_move[0] + 0.1 * value,
                        x,
                        y,
                        piece,
                        dropped,
                        promoted,
                    )
                    worst_move_val = opposite_move[0]
            return best_move

    def play_against_bot(self, bot):
        """
        function for testing bot
        A bot vs bot game: returns COLOR of winner
        :param bot: another bot to play with
        """
        i = 0
        while i < 200:
            color = self.board.turn_color
            if self.board.is_checkmate(color):
                print("mat")
                return color.opposite()
            move = self.best_move(color)
            if move is None:
                print("pat")
                return None
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
            # print(self.__evaluate(COLOR.WHITE, 1))
            i += 1
        result = self.__evaluate(COLOR.WHITE, 1)
        return COLOR.WHITE if result > 0 else COLOR.BLACK
