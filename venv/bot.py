import valueMatrix


class Bot:
    def __init__(self, board_grid):
        self.matrix = valueMatrix.ValueMatrix()
        self.board = board_grid

    def test_move(self, x, y, piece):
        current_value = self.matrix.valueMatrix[self.matrix.Figures[piece.name], piece.row, piece.col]
        new_value = 0
        if self.board.grid[x][y].color == piece.color.opposite():
            new_value = self.board.grid[x][y].value_in_hand
        new_value += self.matrix.valueMatrix[self.matrix.Figures[piece.name], x, y]
        return new_value - current_value
    # Testing more moves TBA
