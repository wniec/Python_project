import json
from config.defs import SRC_DIR

SAVE_PATH = SRC_DIR + "/resources/saves/data.json"


class SaveController:
    def __init__(self) -> None:
        self.data = {"Total games": 0, "Won games": 0, "Last 10 games": ""}

    def __load(self):
        with open(SAVE_PATH, "r") as savefile:
            self.data = json.load(savefile)

    def __save(self):
        with open(SAVE_PATH, "w") as savefile:
            json.dump(self.data, savefile)

    def update(self, result):
        self.__load()
        self.data["Total games"] += 1
        res = self.data["Last 10 games"]

        match result:
            case "Win":
                self.data["Won games"] += 1
                res = res[1:] + "W " if len(res) >= 10 else res + "W "

            case "Loss":
                res = res[1:] + "L " if len(res) >= 10 else res + "L "

        self.data["Last 10 games"] = res
        self.__save()

    def get_data(self):
        self.__load()
        return self.data
