import json
import string
from json import JSONEncoder
from pieces import pieces_dict
import numpy as np

from board import Board
from pieces import COLOR


class NpArrayEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)


class Game:
    def __init__(self):
        self.kifu = None

    def read(self):
        with open("games.json", "r") as read_file:
            self.kifu = json.load(read_file)


def read_move(move: string, board: Board, color: COLOR):
    i = 0
    promoted = False
    if move[i] == '+':
        promoted = True
        i += 1
    piece_name = pieces_dict[move[i]]
    if move[i + 1] != '\'':
        x_before = int(move[i + 1]) - 1
        y_before = ord(move[i + 2].lower()) - 97
        piece = board.grid[x_before][y_before]
        if piece is None or piece.name != piece_name or promoted != piece.promoted:
            return None
        x = int(move[i + 4]) - 1
        y = ord(move[i + 5].lower()) - 97
        return piece, (x, y)
    else:
        x = int(move[i + 2]) - 1
        y = ord(move[i + 3].lower()) - 97
        for p in board.captured[color.value]:
            if p.name == piece_name:
                return p, (x, y)
        return None
