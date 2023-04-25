import pieces
from pieces import COLOR
from itertools import product
from random import randint
import time


class Clock:
    def __init__(self, max_time) -> None:
        self.current_task = None
        self.timers = {}
        self.reftime = time.monotonic()
        self.max_time = max_time

    def elapsed(self, reset=False):
        old_reftime = self.reftime
        new_reftime = time.monotonic()
        if reset:
            self.reftime = new_reftime

        return new_reftime - old_reftime

    def switch_to(self, newtask):
        task = self.current_task
        elapsed = self.elapsed(True)
        if task is not None:
            self.timers[task] -= elapsed

        self.current_task = newtask
        if newtask is not None and newtask not in self.timers:
            self.timers[newtask] = self.max_time

    def get_time(self, task):
        if task not in self.timers:
            return self.max_time

        val = self.timers[task]
        if task == self.current_task:
            val -= self.elapsed()

        return int(max(0, val))


class Board:
    def __init__(self, size: int = 9, max_time=600, is_pvp=True) -> None:
        """
        Initializes `Board` object.
        :param int `size`: size of the board i.e. board will be a grid with size x size squares
        :param int `max_time`: max time of game in seconds
        """

        self.size = size
        self.grid = [[None for _ in range(size)] for _ in range(size)]
        self.clock = Clock(max_time)

        # first black, second white
        self.active = ({}, {})
        self.captured = ({}, {})
        self.kings = [None, None]

        self.turn_color = None
        self.is_pvp = is_pvp

    def who_starts(self, option="Black"):
        match option:
            case "Black":
                self.turn_color = COLOR.BLACK
            case "White":
                self.turn_color = COLOR.WHITE
            case "Random":
                rand = randint(0, 1)
                self.turn_color = COLOR.BLACK if rand == 0 else COLOR.WHITE

    def end_turn(self):
        self.clock.switch_to(self.turn_color.opposite())
        self.turn_color = self.turn_color.opposite()

    def setup(self) -> None:
        """
        Places pieces on the board. Note that white pieces are placed at the top.
        """

        # Set first ranks
        for row in (0, self.size - 1):
            color = COLOR.WHITE if row == 0 else COLOR.BLACK

            lance_l = pieces.Lance(pos=(row, 0), color=color)
            knight_l = pieces.Knight(pos=(row, 1), color=color)
            silver_l = pieces.Silver(pos=(row, 2), color=color)
            gold_l = pieces.Gold(pos=(row, 3), color=color)
            king = pieces.King(pos=(row, 4), color=color)
            gold_r = pieces.Gold(pos=(row, 5), color=color)
            silver_r = pieces.Silver(pos=(row, 6), color=color)
            knight_r = pieces.Knight(pos=(row, 7), color=color)
            lance_r = pieces.Lance(pos=(row, 8), color=color)

            self.grid[row][0] = lance_l
            self.grid[row][1] = knight_l
            self.grid[row][2] = silver_l
            self.grid[row][3] = gold_l
            self.grid[row][4] = king
            self.grid[row][5] = gold_r
            self.grid[row][6] = silver_r
            self.grid[row][7] = knight_r
            self.grid[row][8] = lance_r

            self.active[color.value]["L1"] = lance_l
            self.active[color.value]["L2"] = lance_r
            self.active[color.value]["N1"] = knight_l
            self.active[color.value]["N2"] = knight_r
            self.active[color.value]["S1"] = silver_l
            self.active[color.value]["S2"] = silver_r
            self.active[color.value]["G1"] = gold_l
            self.active[color.value]["G2"] = gold_r
            self.active[color.value]["K"] = king

            self.kings[color.value] = king

        # Set second ranks
        for row in (1, self.size - 2):
            color = COLOR.WHITE if row == 1 else COLOR.BLACK

            bishop = pieces.Bishop(
                pos=(row, 1 if color == COLOR.BLACK else 7), color=color
            )
            rook = pieces.Rook(pos=(row, 7 if color == COLOR.BLACK else 1), color=color)

            self.grid[row][bishop.col] = bishop
            self.grid[row][rook.col] = rook

            self.active[color.value]["B"] = bishop
            self.active[color.value]["R"] = rook

        # Set third ranks
        for row in (2, self.size - 3):
            color = COLOR.WHITE if row == 2 else COLOR.BLACK

            for col in range(self.size):
                piece = pieces.Pawn(pos=(row, col), color=color)
                self.grid[row][col] = piece
                self.active[color.value]["P{}".format(col)] = piece

    def get_path(self, pos1, pos2) -> list:
        """
        Returns diagonal, horizontal or vertical path if such exists between two squares at
        positions `pos1` and `pos2`.
        :param (int,int) `pos1`: position of first square
        :param (int,int) `pos2`: position of second square
        """

        row_diff = pos2[0] - pos1[0]
        col_diff = pos2[1] - pos1[1]
        path = []

        if abs(row_diff) == abs(col_diff):  # Path is diagonal
            row_step = 1 if row_diff > 0 else -1
            col_step = 1 if col_diff > 0 else -1
            for i in range(1, abs(row_diff)):
                path.append((pos1[0] + i * row_step, pos1[1] + i * col_step))
            return path

        elif row_diff == 0:  # Path is horizontal
            path = []
            col_step = 1 if col_diff > 0 else -1
            for i in range(1, abs(col_diff)):
                path.append((pos1[0], pos1[1] + i * col_step))
            return path

        elif col_diff == 0:  # Path is vertical
            path = []
            row_step = 1 if row_diff > 0 else -1
            for i in range(1, abs(row_diff)):
                path.append((pos1[0] + i * row_step, pos1[1]))
            return path

        return path

    def is_blocked(self, pos, piece: pieces.Piece) -> bool:
        """
        Checks whether `piece` has a line of sight to square at position `pos`.
        :param (int,int) `pos`: position of a square
        :param Piece `piece`:
        """

        path = self.get_path((piece.row, piece.col), pos)

        for row, col in path:
            if self.grid[row][col] is not None:
                return True

        return False

    def get_available(self, piece: pieces.Piece) -> set:
        """
        Returns available squares to which `piece` can move.
        :param Piece `piece`:
        """
        if piece.color != self.turn_color or (
            not self.is_pvp and piece.color == COLOR.WHITE
        ):
            return set()


        inbounds = lambda row, col: 0 <= row < self.size and 0 <= col < self.size
        available_pos = set()

        for move in piece.moves:
            if piece.color == COLOR.WHITE:
                row, col = piece.row + move[0], piece.col + move[1]
            else:
                row, col = piece.row - move[0], piece.col - move[1]

            if (
                inbounds(row, col)
                and not self.is_blocked((row, col), piece)
                and (
                    self.grid[row][col] is None
                    or self.grid[row][col].color != piece.color
                )
            ):
                available_pos.add((row, col))

        if self.is_check(piece.color):
            available_pos_new = set()
            king = self.kings[piece.color.value]
            attackers = self.get_attacking((king.row, king.col), king.color.opposite())

            if piece == king:
                for pos in available_pos:
                    if len(self.get_attacking(pos, piece.color.opposite())) == 0:
                        available_pos_new.add(pos)
                return available_pos_new

            if len(attackers) > 1:
                return set()
            else:
                attacker = attackers[0]
                for pos in available_pos:
                    if pos == (attacker.row, attacker.col) or pos in self.get_path(
                        (attacker.row, attacker.col), (king.row, king.col)
                    ):
                        available_pos_new.add(pos)
                return available_pos_new

        return available_pos

    def get_attacking(self, pos, attacking_color: COLOR) -> list:
        """
        Returns set of all `attacking_color` pieces which attack square at pos `position`.
        :param (int,int) `pos`: position of square
        :param COLOR `attacking_color`: color of attacking pieces
        """

        attack_pieces = []

        for piece_type in self.active[attacking_color.value].keys():
            attack_piece = self.active[attacking_color.value][piece_type]
            positions = set()

            for move in attack_piece.moves:
                if attack_piece.color == COLOR.WHITE:
                    row, col = attack_piece.row + move[0], attack_piece.col + move[1]
                else:
                    row, col = attack_piece.row - move[0], attack_piece.col - move[1]

                if row != attack_piece.row or col != attack_piece.col:
                    positions.add((row, col))

            if pos in positions and not self.is_blocked(pos, attack_piece):
                attack_pieces.append(attack_piece)

        return attack_pieces

    def move(self, piece: pieces.Piece, new_position) -> None:
        """
        Moves piece to new position i.e. changes its internal position `(piece.x, piece.y)` and
        changes piece's position on the board stored in structures `self.grid` and `self.active`.
        :param Piece `piece`:
        :param (int, int) `new_position`: pair of integers specifing new position
        """

        for key, val in self.captured[piece.color.value].items():
            if val == piece:
                self.drop(piece, new_position)
                return
        if (
            self.grid[new_position[0]][new_position[1]] is not None
            and self.grid[new_position[0]][new_position[1]].color
            == piece.color.opposite()
        ):
            self.capture(self.grid[new_position[0]][new_position[1]])

        self.grid[piece.row][piece.col] = None
        self.grid[new_position[0]][new_position[1]] = piece
        piece.place(new_position)

    def drop(self, piece: pieces.Piece, new_position) -> None:
        """
        Drops piece to new position i.e. changes its internal position `(piece.x, piece.y)` and
        changes piece's position on the board stored in structures `self.grid` and `self.active`.
        :param piece:
        :param new_position:
        """
        self.grid[new_position[0]][new_position[1]] = piece
        piece.place(new_position)
        drop_key = None
        for key, val in self.captured[piece.color.value].items():
            if val == piece:
                drop_key = key

        self.active[piece.color.opposite().value][drop_key] = self.captured[
            piece.color.value
        ][drop_key]
        del self.captured[piece.color.value][drop_key]

    def capture(self, captured_piece: pieces.Piece):
        """
        Deletes piece `captured_piece` from board (i.e. from structures `Board.grid` and
        `Board.active`) and adds it to structure `Board.captured`.
        :param `captured_piece`:
        """

        capture_key = None
        for key, piece in self.active[captured_piece.color.value].items():
            if piece == captured_piece:
                capture_key = key

        color = captured_piece.color
        self.captured[color.opposite().value][capture_key] = captured_piece

        del self.active[color.value][capture_key]

    # Fix handle check in get_available()

    def is_check(self, color):
        king = self.kings[color.value]
        attackers = self.get_attacking((king.row, king.col), king.color.opposite())
        if len(attackers) == 0:
            return False
        return True

    def is_checkmate(self, color):
        king = self.kings[color.value]
        attackers = self.get_attacking((king.row, king.col), king.color.opposite())

        # Check if the king is attacked
        if len(attackers) == 0:
            return False

        # Check if the king can escape or capture the attacking piece
        for pos in self.get_available(king):
            if len(self.get_attacking(pos, king.color.opposite())) == 0:
                return False

        # Check if any piece can block the attack
        if len(attackers) == 1:
            attacker = attackers[0]
            path = set(
                self.get_path((king.row, king.col), (attacker.row, attacker.col))
            )

            for piece_type in self.active[king.color.value].keys():
                defender = self.active[king.color.value][piece_type]

                for move in self.get_available(defender):
                    if defender.color == COLOR.WHITE:
                        row, col = defender.row + move[0], defender.col + move[1]
                    else:
                        row, col = defender.row - move[0], defender.col - move[1]

                    if (row, col) in path:
                        return False

        # Check if any piece can capture the attacking piece
        if len(attackers) == 1:
            attacker = attackers[0]
            defenders = set(
                self.get_attacking((attacker.row, attacker.col), king.color)
            ) - {king}

            if len(defenders) > 0:
                return False

        return True

    def get_available_drops(self, piece):
        """

        returns all free positions on which player or bot can drop their piece on
        """
        free = set()
        match piece.name:
            case "P" | "L":
                possible_rows = {i for i in range(8)}
            case "N":
                possible_rows = {i for i in range(7)}
            case _:
                possible_rows = {i for i in range(9)}
        possible_cols = set(i for i in range(9))
        impossible_cols = set()
        if piece.name == "P":
            for piece_id in self.active[piece.color.value]:
                if piece_id[0] == "P":
                    impossible_cols.add(self.active[piece.color.value][piece_id].col)
        possible_cols.difference_update(impossible_cols)
        king_x, king_y = self.kings[piece.color.opposite().value].pos()
        for x in possible_rows:
            for y in possible_cols:
                if self.grid[x][y] is not None and not (
                    king_x == x + piece.color.value * 2 - 1 and king_y == y
                ):
                    free.add((x, y))
        return free

    def show(self):
        print("   ", end="")
        for col in range(self.size):
            print(col, " ", end="")
        print()

        for row in range(self.size):
            print(row, " ", end="")
            for col in range(self.size):
                if self.grid[row][col] is not None:
                    if self.grid[row][col].color == COLOR.BLACK:
                        print(
                            "\033[91m{}\033[0m".format(self.grid[row][col].name),
                            " ",
                            end="",
                        )
                    else:
                        print("\033[0m{}".format(self.grid[row][col].name), " ", end="")
                else:
                    print("·", " ", end="")
            print()

    def evaluate(self):
        side_0 = sum([self.captured[0][piece].value for piece in self.captured[0]])
        side_0 += sum([self.active[0][piece].value for piece in self.active[0]])
        side_1 = sum([self.captured[1][piece].value for piece in self.captured[1]])
        side_1 += sum([self.active[1][piece].value for piece in self.active[1]])
        return side_0, side_1
