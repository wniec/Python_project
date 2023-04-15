import json
from json import JSONEncoder
import numpy as np
from pieces import COLOR
from pieces import pieces_dict


# matrix for evaluating real values of Pieces in given configuration


class ValueMatrix:

    def __init__(self):
        self.valueMatrix = None
        self.generate_random()

    def generate_random(self):
        self.valueMatrix = np.random.random((10, 9, 9))

    # saving current configuration will be helpful for reinforcement learning

    def save_matrix(self):
        numpy_data = {"valueMatrix": self.valueMatrix}
        with open("values.json", "w") as write_file:
            json.dump(numpy_data, write_file, cls=NpArrayEncoder)

    def read(self):
        with open("values.json", "r") as read_file:
            decoded_array = json.load(read_file)
            self.valueMatrix = np.asarray(decoded_array["valueMatrix"])

    def evaluate_score(self, active, captured, color):
        score = 0
        for a in active:
            if color == COLOR.BLACK:
                x, y = a.row, a.col
            else:
                x, y = 8 - a.row, 8 - a.col
            name = a.name
            score += self.valueMatrix[pieces_dict[name], x, y]
        for c in captured:
            score += c.value_in_hand
        return score
    # Changing matrices according to bot performance TBA


class NpArrayEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)
