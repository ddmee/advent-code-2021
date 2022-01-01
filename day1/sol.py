from pathlib import Path


def _get_lines() -> list[int]:
    input1 = Path(__file__).parent / 'input1'

    with open(input1, 'rt') as openf:
        lines = openf.readlines()

    return [int(line) for line in lines]


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
            windows.append([lines[index+x] for x in range(size)])
        except IndexError:  # get towards end can run over end of list
            break
    return windows


def _compact_windows(windows: list[list[int]]) -> list[int]:
    """Convert every list in windows into a single value"""
    return [sum(list_i) for list_i in windows]


def sol1() -> int:
    return _count_incs(lines=_get_lines())


def sol2() -> int:
    lines = _compact_windows(windows=_build_windows(lines=_get_lines()))
    return _count_incs(lines=lines)


if __name__ == '__main__':
    print('solution 1: {0}'.format(sol1()))
    print('solution 2: {0}'.format(sol2()))
