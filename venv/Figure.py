from Vector2D import Vector2D


class Figure:
    steps = []

    def __init__(self, color, position, promoted=False):
        self.color = color
        self.position = position
        self.promoted = promoted

    def move(self, step):
        self.position = self.position.add(step)

    def promote(self):
        pass


class King(Figure):
    steps = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]

    def promote(self):
        return self


class Rook(Figure):
    steps = [(i, 0) for i in range(8)] + [(-i, 0) for i in range(8)] + [(0, i) for i in range(8)] + [(0, -i) for i in
                                                                                                     range(8)]

    def promote(self):
        return Dragon(self.color, self.position, True)


class Dragon(Figure):
    steps = [(i, 0) for i in range(8)] + [(-i, 0) for i in range(8)] + [(0, i) for i in range(8)] + [(0, -i) for i in
                                                                                                     range(8)] + \
            [(1, 1), (-1, 1), (-1, -1), (-1, -1)]


class Bishop(Figure):
    steps = [(i, i) for i in range(8)] + [(-i, -i) for i in range(8)] + [(-i, i) for i in range(8)] + [(i, -i) for i in
                                                                                                       range(8)]

    def promote(self):
        return Horse(self.color, self.position, True)


class Horse(Figure):
    steps = [(i, i) for i in range(8)] + [(-i, -i) for i in range(8)] + [(-i, i) for i in range(8)] + [(i, -i) for i in
                                                                                                       range(8)] + \
            [(1, 0), (0, 1), (-1, 0), (0, -1)]


class Gold(Figure):
    steps = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (0, -1)]


class Silver(Figure):
    steps = [(1, 1), (0, 1), (-1, 1), (-1, -1), (1, -1)]

    def promote(self):
        return Gold(self.color, self.position, True)


class Knight(Figure):
    steps = [(1, 2), (-1, 2)]

    def promote(self):
        return Gold(self.color, self.position, True)


class Lance(Figure):
    steps = [(0, i) for i in range(8)]

    def promote(self):
        return Gold(self.color, self.position, True)


class Pawn(Figure):
    steps = [(0, 1)]

    def promote(self):
        return Gold(self.color, self.position, True)


def create_frigures_dicts(color_down, color_up):
    down_dict = dict()
    up_dict = dict()
    for i in range(9):
        down_dict.add(Pawn(color_down, Vector2D(i, 2)))
        up_dict.add(Pawn(color_up, Vector2D(i, 2)))
    # Pozostałe figury TBA
