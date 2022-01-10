from pathlib import Path
from typing import Callable


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


class Day3:
    def __init__(self) -> None:
        self.day = 3

    @staticmethod
    def parser(line: str) -> list[int]:
        line = line.strip()
        return [int(char) for char in line]

    def lines(self) -> list[int]:
        return _get_lines(day=self.day, parser=self.parser)

    def most_least(self, lines) -> tuple[str, str]:
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

    def filter(self, lines:list[list[int]], idx:int, predicate:Callable) -> list[list[int]]:
        pattern = predicate(lines)
        lines = list(filter(lambda l: l[idx] == int(pattern[idx]), lines))
        return lines

    def filter_loop(self, lines:list[list[int]], predicate:Callable) -> list[int]:
        width = len(lines[0])
        for idx in range(width):
            lines = self.filter(lines, idx, predicate)
            if len(lines) == 1:
                result = lines[0]
                break
            elif len(lines) == 0:
                raise RuntimeError('Run out of lines!')
        else:
            raise RuntimeError('Ran out of width?')
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

    def sol(self) -> None:
        print("Day {0}".format(self.day))
        print("part 1: {0}".format(self.part1()))
        print("part 2: {0}".format(self.part2()))


if __name__ == "__main__":
    days = (Day1(), Day2(), Day3())
    for d in days:
        d.sol()
