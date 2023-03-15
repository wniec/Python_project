import figure
import vector_comparision


def is_on_board(position):
    return vector_comparision.follows(position, (0, 0)) and vector_comparision.precedes(position, (8, 8))


class Board:
    figures = dict()

    def can_move_to(self, position):
        return is_on_board(position) and not self.figures.get(position)

    def possible_moves(self, fig):
        steps = fig.steps
        position = fig.position
        moves = [vector_comparision.add(step, position) for step in steps]
        return list(filter(lambda x: self.can_move_to(x), moves))
