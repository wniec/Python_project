import Figure
import Vector2D


def is_on_board(position):
    return position.follows(Vector2D(0, 0)) and position.precedes(Vector2D(8, 8))


class Board:
    figures = dict()

    def can_move_to(self, position):
        return is_on_board(position) and not self.figures.get(position)

