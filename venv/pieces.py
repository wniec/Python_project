from enum import Enum
from pygame.image import load


class COLOR(Enum):
    BLACK = 0
    WHITE = 1

    def opposite(self):
        if self.value == 0:
            return COLOR.WHITE
        return COLOR.BLACK


pieces_dict = {'P': 0, 'L': 1, 'N': 2, 'S': 3, 'G': 4, 'B': 5, 'R': 6, 'D': 7, 'H': 8, 'K': 9}


class Piece:
    def __init__(self, pos, color, promoted=False):
        self.value_in_hand = None
        self.value = None
        self.name = None
        self.row = pos[0]
        self.col = pos[1]
        self.color = color
        self.promoted = promoted

    def place(self, new_position):
        self.row = new_position[0]
        self.col = new_position[1]

    def promote(self):
        pass

    def degrade(self):
        return Piece((self.row, self.col), self.color)

    def pos(self):
        return self.row, self.col

    def __lt__(self, other):
        return self.value < other.value


class Pawn(Piece):
    def __init__(self, pos, color, promoted=False):
        super().__init__(pos, color, promoted)
        # self.img = "P"
        self.name = 'P'
        self.img = load("imgs/piece.png")
        self.moves = [(1, 0)]
        self.value = 1.0
        self.value_in_hand = 1.15

    def promote(self):
        self.moves = GoldenGeneral.moves
        self.img = GoldenGeneral.img
        self.value = 4.20
        self.promoted = True


class King(Piece):
    def __init__(self, pos, color, promoted=False):
        super().__init__(pos, color, promoted)
        # self.img = "K"
        self.name = 'K'
        self.img = load("imgs/piece.png")
        self.moves = [
            (0, 1),
            (1, 0),
            (0, -1),
            (-1, 0),
            (1, 1),
            (-1, -1),
            (1, -1),
            (-1, 1),
        ]
        self.value = 1000.00
        self.value_in_hand = -1000.00



class Rook(Piece):
    def __init__(self, pos, color, promoted=False):
        super().__init__(pos, color, promoted)
        # self.img = "R"
        self.name = 'R'
        self.img = load("imgs/piece.png")
        self.moves = (
                [(i, 0) for i in range(8)]
                + [(-i, 0) for i in range(8)]
                + [(0, i) for i in range(8)]
                + [(0, -i) for i in range(8)]
        )
        self.value = 10.40
        self.value_in_hand = 12.70

    def promote(self):
        self.moves = Dragon.moves
        self.img = Dragon.img
        self.value = 13.00
        self.promoted = True
        self.name = 'D'


class Bishop(Piece):
    def __init__(self, pos, color, promoted=False):
        super().__init__(pos, color, promoted)
        # self.img = "B"
        self.name = 'B'
        self.img = load("imgs/piece.png")
        self.moves = (
                [(i, i) for i in range(8)]
                + [(-i, -i) for i in range(8)]
                + [(-i, i) for i in range(8)]
                + [(i, -i) for i in range(8)]
        )
        self.value = 8.90
        self.value_in_hand = 11.10

    def promote(self):
        self.moves = Horse.moves
        self.img = Horse.img
        self.value = 11.50
        self.promoted = True
        self.name = 'H'


class Gold(Piece):
    def __init__(self, pos, color, promoted=False):
        super().__init__(pos, color, promoted)
        # self.img = "G"
        self.name = 'G'
        self.img = load("imgs/piece.png")
        self.moves = [(1, 0), (1, 1), (1, -1), (0, 1), (0, -1), (-1, 0)]
        self.value = 6.90
        self.value_in_hand = 7.80


class Silver(Piece):
    def __init__(self, pos, color, promoted=False):
        super().__init__(pos, color, promoted)
        # self.img = "S"
        self.name = 'S'
        self.img = load("imgs/piece.png")
        self.moves = [(1, 0), (1, 1), (1, -1), (-1, 1), (-1, 1)]
        self.value = 6.40
        self.value_in_hand = 7.20

    def promote(self):
        self.moves = GoldenGeneral.moves
        self.img = GoldenGeneral.img
        self.value = 6.70
        self.promoted = True


class Knight(Piece):
    def __init__(self, pos, color, promoted=False):
        super().__init__(pos, color, promoted)
        # self.img = "N"
        self.name = 'N'
        self.img = load("imgs/piece.png")
        self.moves = [(2, 1), (2, -1)]
        self.value = 4.50
        self.value_in_hand = 5.10

    def promote(self):
        self.moves = GoldenGeneral.moves
        self.img = GoldenGeneral.img
        self.value = 6.40
        self.promoted = True


class Lance(Piece):
    def __init__(self, pos, color, promoted=False):
        super().__init__(pos, color, promoted)
        # self.img = "L"
        self.name = 'L'
        self.img = load("imgs/piece.png")
        self.moves = [(i, 0) for i in range(8)]
        self.value = 4.30
        self.value_in_hand = 4.80

    def promote(self):
        self.moves = GoldenGeneral.moves
        self.img = GoldenGeneral.img
        self.value = 6.30
        self.promoted = True


class Dragon:
    img = load("imgs/piece.png")
    moves = (
            [(i, 0) for i in range(8)]
            + [(-i, 0) for i in range(8)]
            + [(0, i) for i in range(8)]
            + [(0, -i) for i in range(8)]
            + [(1, 1), (-1, 1), (-1, -1), (-1, -1)]
    )


class Horse:
    img = load("imgs/piece.png")
    moves = (
            [(i, i) for i in range(8)]
            + [(-i, -i) for i in range(8)]
            + [(-i, i) for i in range(8)]
            + [(i, -i) for i in range(8)]
            + [(1, 0), (0, 1), (-1, 0), (0, -1)]
    )


class GoldenGeneral:
    img = load("imgs/piece.png")
    moves = (
            [(i, i) for i in range(8)]
            + [(-i, -i) for i in range(8)]
            + [(-i, i) for i in range(8)]
            + [(i, -i) for i in range(8)]
            + [(1, 0), (0, 1), (-1, 0), (0, -1)]
    )
