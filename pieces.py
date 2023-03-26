from enum import Enum
from pygame.image import load


class COLOR(Enum):
    BLACK = 0
    WHITE = 1

    def opposite(self):
        if self.value == 0:
            return COLOR.WHITE
        return COLOR.BLACK


class Piece:
    def __init__(self, pos, color, promoted=False):
        self.row = pos[0]
        self.col = pos[1]
        self.color = color
        self.promoted = promoted

    def place(self, new_position):
        self.row = new_position[0]
        self.col = new_position[1]

    def promote(self):
        pass


class Pawn(Piece):
    def __init__(self, pos, color, promoted=False):
        super().__init__(pos, color, promoted)
        # self.img = "P"
        self.img = load("imgs/piece.png")
        self.moves = [(1, 0)]

    def promote(self):
        return Gold((self.row, self.col), self.color, True)


class King(Piece):
    def __init__(self, pos, color, promoted=False):
        super().__init__(pos, color, promoted)
        # self.img = "K"
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


class Rook(Piece):
    def __init__(self, pos, color, promoted=False):
        super().__init__(pos, color, promoted)
        # self.img = "R"
        self.img = load("imgs/piece.png")
        self.moves = (
            [(i, 0) for i in range(8)]
            + [(-i, 0) for i in range(8)]
            + [(0, i) for i in range(8)]
            + [(0, -i) for i in range(8)]
        )

    def promote(self):
        return Dragon((self.row, self.col), self.color, True)


class Dragon(Piece):
    def __init__(self, pos, color, promoted=False):
        super().__init__(pos, color, promoted)
        # self.img = "D"
        self.img = load("imgs/piece.png")
        self.moves = (
            [(i, 0) for i in range(8)]
            + [(-i, 0) for i in range(8)]
            + [(0, i) for i in range(8)]
            + [(0, -i) for i in range(8)]
            + [(1, 1), (-1, 1), (-1, -1), (-1, -1)]
        )


class Bishop(Piece):
    def __init__(self, pos, color, promoted=False):
        super().__init__(pos, color, promoted)
        # self.img = "B"
        self.img = load("imgs/piece.png")
        self.moves = (
            [(i, i) for i in range(8)]
            + [(-i, -i) for i in range(8)]
            + [(-i, i) for i in range(8)]
            + [(i, -i) for i in range(8)]
        )

    def promote(self):
        return Horse((self.row, self.col), self.color, True)


class Horse(Piece):
    def __init__(self, pos, color, promoted=False):
        super().__init__(pos, color, promoted)
        # self.img = "H"
        self.img = load("imgs/piece.png")
        self.moves = (
            [(i, i) for i in range(8)]
            + [(-i, -i) for i in range(8)]
            + [(-i, i) for i in range(8)]
            + [(i, -i) for i in range(8)]
            + [(1, 0), (0, 1), (-1, 0), (0, -1)]
        )


class Gold(Piece):
    def __init__(self, pos, color, promoted=False):
        super().__init__(pos, color, promoted)
        # self.img = "G"
        self.img = load("imgs/piece.png")
        self.moves = [(1, 0), (1, 1), (1, -1), (0, 1), (0, -1), (-1, 0)]


class Silver(Piece):
    def __init__(self, pos, color, promoted=False):
        super().__init__(pos, color, promoted)
        # self.img = "S"
        self.img = load("imgs/piece.png")
        self.moves = [(1, 0), (1, 1), (1, -1), (-1, 1), (-1, 1)]

    def promote(self):
        return Gold((self.row, self.col), self.color, True)


class Knight(Piece):
    def __init__(self, pos, color, promoted=False):
        super().__init__(pos, color, promoted)
        # self.img = "N"
        self.img = load("imgs/piece.png")
        self.moves = [(2, 1), (2, -1)]

    def promote(self):
        return Gold((self.row, self.col), self.color, True)


class Lance(Piece):
    def __init__(self, pos, color, promoted=False):
        super().__init__(pos, color, promoted)
        # self.img = "L"
        self.img = load("imgs/piece.png")
        self.moves = [(i, 0) for i in range(8)]

    def promote(self):
        return Gold((self.row, self.col), self.color, True)
