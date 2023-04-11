import pieces
from pieces import COLOR
from itertools import product


class Board:
    def __init__(self, size: int) -> None:
        """
        Initializes `Board` object.
        @param int `size`: size of the board i.e. board will be a grid with size x size squares.
        """

        self.size = size
        self.grid = [[None for _ in range(size)] for _ in range(size)]
        self.active = ({}, {})
        self.captured = ({}, {})
        self.kings = [None, None]
        # first black, second white

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
        positions pos1 and pos2.
        @param (int,int) pos1: position of first square
        @param (int,int) pos2: position of second square
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
        @param (int,int) `pos`: position of a square
        @param Piece `piece`:
        """

        path = self.get_path((piece.row, piece.col), pos)

        for row, col in path:
            if self.grid[row][col] is not None:
                return True

        return False

    def get_available(self, piece: pieces.Piece) -> set:
        """
        Returns available squares to which `piece` can move.
        param Piece `piece`:
        """

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

    def move(self, piece: pieces.Piece, new_position) -> None:
        """
        Moves piece to new position i.e. changes its internal position `(piece.x, piece.y)` and
        changes piece's position on the board stored in structures `self.grid` and `self.active`.
        @param Piece `piece`:
        @param (int, int) `new_position`: pair of integers specifing new position
        """
        if (
                self.grid[new_position[0]][new_position[1]] != None
                and self.grid[new_position[0]][new_position[1]].color
                == piece.color.opposite()
        ):
            self.capture(self.grid[new_position[0]][new_position[1]])

        self.grid[piece.row][piece.col] = None
        self.grid[new_position[0]][new_position[1]] = piece
        piece.place(new_position)
    def get_attacking(self, pos, attacking_color: COLOR) -> list:
        """
        Returns set of all `attacking_color` pieces which attack square at pos `position`.
        @param (int,int) `pos`: position of square
        @param COLOR `attacking_color`: color of attacking pieces
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
                positions.add((row, col))

            if pos in positions and not self.is_blocked(pos, attack_piece):
                attack_pieces.append(attack_piece)

        return attack_pieces

    def capture(self, capture_piece: pieces.Piece):
        """
        Deletes piece `capture_piece` from board (i.e. from structures `Board.grid` and
        `Board.active`), degrades and adds it to structure `Board.captured`.
        @param Piece `piece`:
        """

        capture_key = None
        for key, piece in self.active[capture_piece.color.value].items():
            if piece == capture_piece:
                capture_key = key

        self.captured[capture_piece.color.opposite().value][capture_key] = self.active[
            capture_piece.color.value
        ][capture_key].degrade()

        del self.active[capture_piece.color.value][capture_key]

    # Fix
    def is_checkmate(self, king):
        attackers = self.get_attacking((king.row, king.col), king.color.opposite())

        # Check if the king is attacked
        if len(attackers) == 0:
            return False

        # Check if the king can escape or capture the attacking piece
        moves = self.get_moves(king)
        for pos in [(king.x + move[0], king.y + move[1]) for move in moves]:
            if not self.is_attacked(pos, king.color.opposite()):
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
                    defender.add((row, col))

                    if (row, col) in path:
                        return False

        # Check if any piece can capture the attacking piece
        if len(attackers) == 1:
            attacker = attackers[0]
            defenders = self.get_attacking((attacker.row, attacker.col), king.color)
            if len(defenders) > 0:
                return False

        return True

    def get_available_drops(self, piece):
        """

        returns all free positions on which player or bot can drop their piece on
        """
        free = set()
        match piece.name:
            case 'P' | 'L':
                possible_rows = {i for i in range(8)}
            case 'N':
                possible_rows = {i for i in range(7)}
            case _:
                possible_rows = {i for i in range(9)}
        possible_cols = set(i for i in range(9))
        if piece.name == 'P':
            possible_cols.difference_update({pawn.col for pawn in self.active[piece.color] if not pawn.promoted})
        for x, in possible_rows:
            for y in possible_cols:
                if self.grid[x][y] is not None and not self.is_checkmate(self.kings[piece.color.opposite()]):
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
                if self.grid[row][col] != None:
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

# os.system("cls")

# board = Board(9)
# board.setup()
# board.show()

# print(board.is_checkmate(board.active[COLOR.WHITE.value]["K"][0]))
# print(board.is_attacked((0, 1), COLOR.WHITE))
# print(board.get_available(board.active[COLOR.BLACK.value]["K"]))
# print(board.get_attacking((7, 4), COLOR.BLACK))
# print(board.is_blocked(board.active[COLOR.WHITE.value]["B"][0], (4, 4)))
