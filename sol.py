from pathlib import Path
from typing import Callable, Union


def _get_lines(day: int, parser: Callable = str) -> list[int]:
    input1 = Path(__file__).parent / "input" / f"day{day}.txt"

    with open(input1, "rt") as openf:
        lines = openf.readlines()

    return [parser(line) for line in lines]


def _count_incs(lines: list[int]) -> int:
    """Count the number of increaesd increments"""
    increases = 0
    previous = None

    for line in lines:
        current = line
        if previous is not None:
            if current > previous:
                increases += 1
        previous = current

    return increases


def _build_windows(lines: list[int], size: int = 3) -> list[list[int]]:
    """Build the appropriate windows from the original line set.
    Basically creating a bunch of duplicated slices of the list.
    """
    windows = []

    for index in range(len(lines)):
        try:
            # windows.append(lines[index:index+size])
            # cannot merely slice because it's happy to slice beyond the
            # end of the list. Use indexing instead as it'll throw an error
            # when accessing beyond end of the list...
            windows.append([lines[index + x] for x in range(size)])
        except IndexError:  # get towards end can run over end of list
            break
    return windows


def _compact_windows(windows: list[list[int]]) -> list[int]:
    """Convert every list in windows into a single value"""
    return [sum(list_i) for list_i in windows]


class Day:
    def __init__(self, day: int) -> None:
        self.day = day

    def part1(self) -> None:
        return None

    def part2(self) -> None:
        return None

    def sol(self) -> None:
        print("Day {0}".format(self.day))
        print("part 1: {0}".format(self.part1()))
        print("part 2: {0}".format(self.part2()))


class Day1(Day):
    """Scanning the descending depth of the ocean floor"""

    def __init__(self) -> None:
        self.day = 1

    def part1(self) -> int:
        return _count_incs(lines=_get_lines(day=self.day, parser=int))

    def part2(self) -> int:
        lines = _get_lines(day=self.day, parser=int)
        lines = _compact_windows(windows=_build_windows(lines))
        return _count_incs(lines=lines)


class Day2(Day):
    """Tracking the descend of the submarine"""

    def __init__(self) -> None:
        self.day = 2
        self.moves: list[tuple[str, int]] = []
        self.aims: list[int] = []
        self.positions: list[tuple[int, int]] = []

    @staticmethod
    def parser(line: str) -> tuple[str, int]:
        line = line.strip()
        tokes = line.split(" ")
        return tokes[0], int(tokes[1])

    @staticmethod
    def move_v1(move: tuple[str, int], x: int, y: int) -> tuple[int, int]:
        if move[0] == "forward":
            x += move[1]
        elif move[0] == "up":
            y += move[1]
        elif move[0] == "down":
            y -= move[1]
        return x, y

    def move_v2(
        self, move: tuple[str, int], x: int, y: int, aim: int
    ) -> tuple[int, int]:
        """down X increases your aim by X units.
        up X decreases your aim by X units.
        forward X does two things:
        increases your horizontal position by X units.
        increases your depth by your aim multiplied by X.
        """
        self.aims.append(aim)
        if move[0] == "forward":
            x += move[1]
            y -= move[1] * aim
        elif move[0] == "up":
            aim -= move[1]
        elif move[0] == "down":
            aim += move[1]
        return x, y, aim

    def process_moves(
        self,
        moves: list[tuple[str, int]],
        x: int = 0,
        y: int = 0,
        aim: int = None,
        move_fnc: Callable = None,
    ) -> tuple[int, int]:
        """Iterate through a list of moves starting from an x and y
        Returns final x,y position and logs all positions on self.x/y
        """
        if move_fnc is None:
            move_fnc = self.move_v1
        for move in moves:
            self.positions.append((x, y))
            if aim is not None:
                x, y, aim = move_fnc(move=move, x=x, y=y, aim=aim)
            else:
                x, y = move_fnc(move=move, x=x, y=y)
        return x, y

    def load_moves(self) -> None:
        self.moves = _get_lines(day=self.day, parser=self.parser)

    def finalise(self, x: int, y: int) -> int:
        """multiply your final horizontal position by your final depth"""
        return x * (-y)

    def part1(self) -> int:
        self.load_moves()
        x, y = self.process_moves(moves=self.moves)
        return self.finalise(x, y)

    def part2(self) -> int:
        self.load_moves()
        x, y = self.process_moves(moves=self.moves, move_fnc=self.move_v2, aim=0)
        return self.finalise(x, y)


class Day3(Day):
    def __init__(self) -> None:
        self.day = 3

    @staticmethod
    def parser(line: str) -> list[int]:
        # norvig chooses not to parse as ints keeps them as strs which
        # probably helps him a bit, less conversion code
        line = line.strip()
        return [int(char) for char in line]

    def lines(self) -> list[int]:
        return _get_lines(day=self.day, parser=self.parser)

    def most_least(self, lines) -> tuple[str, str]:
        # norvig uses pythons str.count inbuilt to do a neater job of
        # this function...
        most_common = ""
        least_common = ""
        for col in range(len(lines[0])):
            tot = sum([row[col] for row in lines])
            if tot > len(lines) // 2:
                most_common += "1"
                least_common += "0"
            elif tot < len(lines) // 2:
                most_common += "0"
                least_common += "1"
            else:
                raise RuntimeError("unexpected total")
        return most_common, least_common

    def part1(self) -> int:
        lines = self.lines()
        most_common, least_common = self.most_least(lines=lines)
        gamma = int(most_common, 2)
        epsilon = int(least_common, 2)
        power = gamma * epsilon
        return power

    def part2_common(self, lines):
        most_common = ""
        least_common = ""
        for col in range(len(lines[0])):
            tot = sum([row[col] for row in lines])
            if tot > len(lines) / 2:
                most_common += "1"
                least_common += "0"
            elif tot < len(lines) / 2:
                most_common += "0"
                least_common += "1"
            else:
                most_common += "1"
                least_common += "0"
        return most_common, least_common

    def filter(
        self, lines: list[list[int]], idx: int, predicate: Callable
    ) -> list[list[int]]:
        pattern = predicate(lines)
        lines = list(filter(lambda l: l[idx] == int(pattern[idx]), lines))
        return lines

    def filter_loop(self, lines: list[list[int]], predicate: Callable) -> list[int]:
        # norvig makes this a recursive loop, with index being fed into
        # the recursive call each time with += 1
        width = len(lines[0])
        for idx in range(width):
            lines = self.filter(lines, idx, predicate)
            if len(lines) == 1:
                result = lines[0]
                break
            elif len(lines) == 0:
                raise RuntimeError("Run out of lines!")
        else:
            raise RuntimeError("Ran out of width?")
        return result

    def part2(self) -> int:
        lines = _get_lines(day=self.day, parser=self.parser)

        def most_common(lines):
            return self.part2_common(lines)[0]

        def least_common(lines):
            return self.part2_common(lines)[1]

        o2 = self.filter_loop(lines, most_common)
        co2 = self.filter_loop(lines, least_common)
        # rejoin to ints, still binary
        o2 = "".join(map(str, o2))
        co2 = "".join(map(str, co2))
        return int(o2, 2) * int(co2, 2)


class BingoBoard:
    def __init__(self, board: list[list[int]], width=5, height=5, num: int = 0) -> None:
        self.num = num
        assert len(board) == height
        for col in board:
            assert len(col) == width
        self.board = board  # grid of bingo numbers
        self.marks = []  # grid of marks for each square in the bingo board
        for row in board:
            self.marks.append([False for _ in range(width)])

    def mark(self, number: int) -> None:
        for row_idx, row in enumerate(self.board):
            for col_idx, col in enumerate(row):
                if col == number:
                    self.marks[row_idx][col_idx] = True

    def indexs(self) -> list[tuple[int, int]]:
        indxs = []
        for row_idx, row in enumerate(self.board):
            for col_idx, col in enumerate(row):
                indxs.append((row_idx, col_idx))
        return indxs

    def numbers(self) -> list:
        numbers = []
        for row_idx, col_idx in self.indexs():
            numbers.append(
                [
                    row_idx,
                    col_idx,
                    self.board[row_idx][col_idx],
                    self.marks[row_idx][col_idx],
                ]
            )
        return numbers

    def __str__(self):
        out = ""
        last_row_idx = 0
        for row_idx, col_idx, num, marked in self.numbers():
            if row_idx > last_row_idx:
                last_row_idx = row_idx
                out += "\n"  # newline
            out += "{0:2},{1}|".format(num, "X" if marked else "_")
        return out

    def row_bingo(self) -> Union[None, int]:
        for row_idx, row in enumerate(self.marks):
            if all(col for col in row):
                return row_idx
        else:
            return None

    def col_bingo(self) -> Union[None, int]:
        for col_idx in range(len(self.board[0])):  # width
            # len(self.board) == height
            if all(
                [self.marks[row_idx][col_idx] for row_idx in range(len(self.board))]
            ):
                return col_idx
        else:
            return None

    def bingo(self) -> Union[None, int]:
        return self.col_bingo() is not None or self.row_bingo() is not None


class Day4(Day):
    def __init__(self):
        # self.day = '4_example'
        self.day = 4

    def get_marks(self) -> list[int]:
        lines = _get_lines(day=self.day, parser=str)
        marks = lines[0].split(",")
        return [int(m) for m in marks]

    def get_boards(self) -> list[BingoBoard]:
        lines = _get_lines(day=self.day, parser=str)
        end = len(lines)
        i = 1  # discard first line
        boards = []
        while i < end:
            board_lines = lines[i + 1 : i + 6]  # first line is empty
            rows = []
            for line in board_lines:
                tokes = line.split(" ")
                tokes = filter(lambda x: x.strip(), tokes)
                row = [int(toke) for toke in tokes]
                rows.append(row)
            boards.append(BingoBoard(board=rows, num=len(boards)))
            i += 6

        return boards

    def part1(self):
        marks, boards = self.get_marks(), self.get_boards()
        for mark in marks:
            # print("=======Marking {0}========".format(mark))
            for b in boards:
                b.mark(mark)
                # print(b)
                # print("-" * 20)
                if b.bingo():
                    print("******Winner Board {0}********".format(b.num))
                    unmarked = [n[2] for n in b.numbers() if not n[3]]
                    return sum(unmarked) * mark
        else:
            return "no bingo"

    def part2(self):
        marks, boards = self.get_marks(), self.get_boards()
        board_order = []
        for mark in marks:
            # print("=======Marking {0}========".format(mark))
            for b in boards:
                b.mark(mark)
                # print(b)
                # print("-" * 20)
                if b.bingo() and b.num not in board_order:
                    board_order.append(b.num)
                    # print("~~Bingo on Board {0}~~".format(b.num))
            if len(board_order) == len(boards):
                last_board = boards[board_order[-1]]
                print("******Last Board {0}******".format(last_board.num))
                unmarked = [n[2] for n in last_board.numbers() if not n[3]]
                return sum(unmarked) * mark
        else:
            return "No bingo or len(board_order) < len(boards)"


if __name__ == "__main__":
    days = (Day1(), Day2(), Day3(), Day4())
    for d in days:
        d.sol()
