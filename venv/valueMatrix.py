import numpy as np
from pieces import COLOR


# matrix for evaluating real values of Pieces in given configuration

class ValueMatrix:
    Figures = {'P': 0, 'L': 1, 'N': 2, 'S': 3, 'G': 4, 'B': 5, 'R': 6, 'D': 7, 'H': 8, 'K': 9}

    def __init__(self):
        self.valueMatrix = self.read_values()

    def generate_random(self):
        self.valueMatrix = np.random.random((10, 9, 9))
    # saving current configuration will be helpful for reinforcement learning
    def save_matrix(self):
        with open("values.txt", "w") as valuesFile:
            for i in range(10):
                for j in range(9):
                    for k in range(9):
                        valuesFile.write(str(self.valueMatrix[i, j, k]) + " ")

    def read_values(self):
        with open("values.txt", "r") as valuesFile:
            values = np.array([float(i) for i in valuesFile.read().split()]).reshape(10, 9, 9)
        return values

    def evaluate_score(self, active, captured, color):
        score = 0
        for a in active:
            if color == COLOR.BLACK:
                x, y = a.row, a.col
            else:
                x, y = 8 - a.row, 8 - a.col
            name = a.name
            score += self.valueMatrix[self.Figures[name], x, y]
        for c in captured:
            score += c.value_in_hand
        return score
    #Changing matrices according to bot performance TBA
