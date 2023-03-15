import vector_comparision


class Figure:
    steps = []

    def __init__(self, color, position, promoted=False):
        self.color = color
        self.position = position
        self.promoted = promoted

    def move(self, step):
        self.position = vector_comparision.add(step,self.position)

    def promote(self):
        pass

    def to_str(self):
        return ""


class King(Figure):
    steps = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]

    def promote(self):
        return self

    def to_str(self):
        return "K"


class Rook(Figure):
    steps = [(i, 0) for i in range(8)] + [(-i, 0) for i in range(8)] + [(0, i) for i in range(8)] + [(0, -i) for i in
                                                                                                     range(8)]

    def promote(self):
        return Dragon(self.color, self.position, True)

    def to_str(self):
        return "R"


class Dragon(Figure):
    steps = [(i, 0) for i in range(8)] + [(-i, 0) for i in range(8)] + [(0, i) for i in range(8)] + [(0, -i) for i in
                                                                                                     range(8)] + \
            [(1, 1), (-1, 1), (-1, -1), (-1, -1)]

    def to_str(self):
        return "D"


class Bishop(Figure):
    steps = [(i, i) for i in range(8)] + [(-i, -i) for i in range(8)] + [(-i, i) for i in range(8)] + [(i, -i) for i in
                                                                                                       range(8)]

    def promote(self):
        return Horse(self.color, self.position, True)

    def to_str(self):
        return "B"


class Horse(Figure):
    steps = [(i, i) for i in range(8)] + [(-i, -i) for i in range(8)] + [(-i, i) for i in range(8)] + [(i, -i) for i in
                                                                                                       range(8)] + \
            [(1, 0), (0, 1), (-1, 0), (0, -1)]

    def to_str(self):
        return "H"


class Gold(Figure):
    steps = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (0, -1)]

    def to_str(self):
        return "G"


class Silver(Figure):
    steps = [(1, 1), (0, 1), (-1, 1), (-1, -1), (1, -1)]

    def promote(self):
        return Gold(self.color, self.position, True)

    def to_str(self):
        return "S"


class Knight(Figure):
    steps = [(1, 2), (-1, 2)]

    def promote(self):
        return Gold(self.color, self.position, True)

    def to_str(self):
        return "N"


class Lance(Figure):
    steps = [(0, i) for i in range(8)]

    def promote(self):
        return Gold(self.color, self.position, True)

    def to_str(self):
        return "L"


class Pawn(Figure):
    steps = [(0, 1)]

    def promote(self):
        return Gold(self.color, self.position, True)

    def to_str(self):
        return "p"


def create_frigures_dicts(color_down, color_up):
    down_dict = dict()
    up_dict = dict()
    for i in range(9):
        down_dict[(i, 2)] = Pawn(color_down, (i, 2))
        up_dict[(i, 6)] = (Pawn(color_up, (i, 6)))
    down_dict[(1, 1)] = (Bishop(color_down, (1, 1)))
    up_dict[(7, 7)] = (Bishop(color_down, (7, 7)))
    down_dict[(7, 1)] = (Rook(color_down, (7, 1)))
    up_dict[(1, 7)] = (Rook(color_down, (1, 7)))
    down_dict[(4, 0)] = (King(color_down, (4, 0)))
    up_dict[(4, 8)] = (King(color_down, (4, 8)))
    other_figures = [Lance, Knight, Silver, Gold]
    for i, figure in enumerate(other_figures):
        down_dict[(i, 0)] = (figure(color_down, (i, 0)))
        down_dict[(8 - i, 0)] = (figure(color_down, (8 - i, 0)))
        up_dict[(i, 0)] = (figure(color_down, (i, 8)))
        up_dict[(8 - i, 0)] = (figure(color_down, (8 - i, 8)))
    return down_dict, up_dict
