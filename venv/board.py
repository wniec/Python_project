import time
import pieces

from bot import Bot
from pieces import COLOR


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

    def pretty_time(self, task):
        return time.strftime("%H:%M:%S", time.gmtime(self.get_time(task)))


class Board:
    def __init__(self, size=9, max_time=600, is_pvp=True, who_starts=COLOR.BLACK):
        """Initializes `Board` object.

        Args:
            size (int, optional): size of the board i.e. board will be a grid with size x size squares. Defaults to 9.

            max_time (int, optional): max time of game in seconds. Defaults to 600.

            is_pvp (bool, optional): Defaults to True.

            who_starts (_type_, optional): Defaults to COLOR.BLACK.
        """

        self.size = size
        self.grid = [[None for _ in range(size)] for _ in range(size)]
        self.clock = Clock(max_time)

        # first black, second white
        self.active = ({}, {})
        self.captured = ({}, {})
        self.kings = [None, None]

        self.bot = Bot(self, 3, 4)
        self.turn_color = who_starts
        self.is_pvp = is_pvp

        self.__setup()

    def __setup(self):
        """Places pieces on the board. Note that white pieces are placed at the top."""

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

            self.active[color.value]["L1" + str(color.value)] = lance_l
            self.active[color.value]["L2" + str(color.value)] = lance_r
            self.active[color.value]["N1" + str(color.value)] = knight_l
            self.active[color.value]["N2" + str(color.value)] = knight_r
            self.active[color.value]["S1" + str(color.value)] = silver_l
            self.active[color.value]["S2" + str(color.value)] = silver_r
            self.active[color.value]["G1" + str(color.value)] = gold_l
            self.active[color.value]["G2" + str(color.value)] = gold_r
            self.active[color.value]["K" + str(color.value)] = king

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

            self.active[color.value]["B" + str(color.value)] = bishop
            self.active[color.value]["R" + str(color.value)] = rook

        # Set third ranks
        for row in (2, self.size - 3):
            color = COLOR.WHITE if row == 2 else COLOR.BLACK

            for col in range(self.size):
                piece = pieces.Pawn(pos=(row, col), color=color)
                self.grid[row][col] = piece
                self.active[color.value]["P{}".format(col) + str(color.value)] = piece

    def __get_path(self, pos1, pos2) -> list:
        """Returns diagonal, horizontal or vertical path if such exists between two squares at
        positions `pos1` and `pos2`.

        Args:
            pos1 (int, int): position of first square

            pos2 (int, int): position of second square

        Returns:
            list: list of squares forming a path betwwen pos1 and pos2
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
        """Checks whether `piece` has a line of sight to square at position `pos`.

        Args:
            pos (int, int): position of a square

            piece (pieces.Piece): piece

        Returns:
            bool: True if is blocked else False
        """

        path = self.__get_path((piece.row, piece.col), pos)

        for row, col in path:
            if self.grid[row][col] is not None:
                return True

        return False

    def get_available(self, piece: pieces.Piece, is_bot=False) -> set:
        """Returns available squares to which `piece` can move. Getting moves of opposite color is inevitable for checking opposite moves in bot

        Args:
            piece (pieces.Piece): piece

            is_bot (bool, optional): Defaults to False.

        Returns:
            set: set of available moves
        """

        if piece.color != self.turn_color and not is_bot:
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

        return available_pos

    def get_attacking(self, pos: tuple[int, int], attacking_color: COLOR) -> list:
        """Returns set of all `attacking_color` pieces which attack square at pos `position`
        Args:
            pos (tuple[int, int]): color of attacking pieces
            attacking_color (COLOR): position of square
        Returns:
            list:
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

    def move(self, piece: pieces.Piece, new_position: tuple[int, int]) -> None:
        """Moves piece to new position i.e. changes its internal position `(piece.x, piece.y)` and
        changes piece's position on the board stored in structures `self.grid` and `self.active`.

        Args:
            piece (pieces.Piece): piece

            new_position (tuple[int, int]): a pair of integers specifying new position
        """

        if (
                self.grid[new_position[0]][new_position[1]] is not None
                and self.grid[new_position[0]][new_position[1]].color
                == piece.color.opposite()
        ):
            self.capture(self.grid[new_position[0]][new_position[1]])

        self.grid[piece.row][piece.col] = None
        self.grid[new_position[0]][new_position[1]] = piece
        piece.place(new_position)

    def capture(self, captured_piece: pieces.Piece):
        """Deletes piece `captured_piece` from board (i.e. from structures `Board.grid` and
        `Board.active`) and adds it to structure `Board.captured`.

        Args:
            captured_piece (pieces.Piece): piece
        """

        capture_key = None
        for key, piece in self.active[captured_piece.color.value].items():
            if piece == captured_piece:
                capture_key = key

        color = captured_piece.color
        self.captured[color.opposite().value][capture_key] = captured_piece
        captured_piece.degrade()
        captured_piece.row = None
        captured_piece.col = None

        del self.active[color.value][capture_key]

    def end_turn(self):
        self.clock.switch_to(self.turn_color.opposite())
        self.turn_color = self.turn_color.opposite()

    def revert_move(
            self,
            piece: pieces.Piece,
            captured: pieces.Piece,
            old_position: tuple[int, int],
            was_promoted: bool,
    ):
        if captured is not None:
            if captured.color == piece.color:
                raise ValueError
            if was_promoted:
                captured.promote()
            captured.place(piece.pos())
            captured_key = None
            for key, val in self.captured[piece.color.value].items():
                if val is captured:
                    captured_key = key
            self.active[piece.color.opposite().value][captured_key] = captured
            del self.captured[piece.color.value][captured_key]
            captured.color = piece.color.opposite()
        self.grid[piece.row][piece.col] = captured
        self.grid[old_position[0]][old_position[1]] = piece
        piece.place(old_position)

    def revert_drop(self, piece: pieces.Piece) -> None:
        x, y = piece.pos()
        self.grid[x][y] = None
        undrop_key = None
        for key, val in self.active[piece.color.value].items():
            if val is piece:
                undrop_key = key
        self.captured[piece.color.value][undrop_key] = piece
        del self.active[piece.color.value][undrop_key]
        piece.color = piece.color.opposite()

    def drop(self, piece: pieces.Piece, new_position) -> None:
        """
        Drops piece to new position i.e. changes its internal position `(piece.x, piece.y)` and
        changes piece's position on the board stored in structures `self.grid` and `self.active`.
        :param piece:
        :param new_position:
        """
        piece.degrade()
        piece.place(new_position)
        piece.color = piece.color.opposite()
        if self.grid[new_position[0]][new_position[1]] is not None:
            print(self.grid[new_position[0]][new_position[1]])
            raise ValueError
        drop_key = None
        for key, val in self.captured[piece.color.value].items():
            if val is piece:
                drop_key = key
        self.active[piece.color.value][drop_key] = self.captured[piece.color.value][
            drop_key
        ]
        del self.captured[piece.color.value][drop_key]
        self.grid[new_position[0]][new_position[1]] = piece

    def get_available_drops(self, piece, is_bot=False):
        """returns all free positions on which player or bot can drop their piece on"""
        color = piece.color.opposite()
        if color != self.turn_color and not is_bot:
            return set()
        free = set()
        possible_rows = {i for i in range(9)}
        if color == COLOR.BLACK:
            match piece.name:
                case "P" | "L":
                    possible_rows = {i for i in range(1, 9)}
                case "N":
                    possible_rows = {i for i in range(2, 9)}
        else:
            match piece.name:
                case "P" | "L":
                    possible_rows = {i for i in range(8)}
                case "N":
                    possible_rows = {i for i in range(7)}
        possible_cols = set(i for i in range(9))
        impossible_cols = set()
        if piece.name == "P":
            for key, val in self.active[color.value].items():
                if val.name == "P":
                    impossible_cols.add(val.col)
        possible_cols.difference_update(impossible_cols)
        king_x, king_y = self.kings[color.opposite().value].pos()
        for x in possible_rows:
            for y in possible_cols:
                if self.grid[x][y] is None and not (
                        king_x == x + color.value * 2 - 1 and king_y == y
                ):
                    free.add((x, y))
        return free

    def is_checkmate(self, color):
        king = self.kings[color.value]

        attackers = self.get_attacking((king.row, king.col), king.color.opposite())

        # Check if king was captured
        if "K" + str(color.value) in self.captured[color.opposite().value]:
            return True

        # Check if the king is attacked
        if len(attackers) == 0:
            return False

        # Check if the king can escape or capture the attacking piece
        for pos in self.get_available(king):
            attack_pieces = []

            for piece_type in self.active[color.opposite().value].keys():
                attack_piece = self.active[color.opposite().value][piece_type]
                positions = set()

                for move in attack_piece.moves:
                    if attack_piece.color == COLOR.WHITE:
                        row, col = attack_piece.row + move[0], attack_piece.col + move[1]
                    else:
                        row, col = attack_piece.row - move[0], attack_piece.col - move[1]

                    if row != attack_piece.row or col != attack_piece.col:
                        positions.add((row, col))
                king_is_blocked = False
                path = self.__get_path(attack_piece.pos(), pos)

                for row, col in path:
                    if self.grid[row][col] is not None and self.grid[row][col] is not king:
                        king_is_blocked = True
                        break
                if pos in positions and not king_is_blocked:
                    attack_pieces.append(attack_piece)
            if len(attack_pieces) == 0:
                return False

        # Check if any piece can block the attack
        if len(attackers) == 1:
            attacker = attackers[0]
            path = set(
                self.__get_path((king.row, king.col), (attacker.row, attacker.col))
            )

            for piece_type in self.active[king.color.value].keys():
                defender = self.active[king.color.value][piece_type]

                for move in self.get_available(defender):
                    if move in path:
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

    def is_check(self, color: pieces.COLOR):
        king = self.kings[color.value]
        attackers = self.get_attacking(king.pos(), color.opposite())
        return len(attackers) > 0

    def show(self):
        import os
        import platform

        if platform.system() == "Windows":
            os.system("cls")
        else:
            os.system("clear")
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
        print("\n")
