from ciphers import CaesarCipher
from dictionary import dictionary_popular

class GridResult:
    word: str
    x: int
    y: int
    orientation: str
    rot: int
    reversed: bool

    def __init__(self, word: str, x: int, y: int, orientation: str, rot: int, reversed: bool):
        self.word = word
        self.x = x
        self.y = y
        self.orientation = orientation
        self.rot = rot
        self.reversed = reversed


def find_rotated_grid_words(grid: str, rotate: bool, reverse: bool) -> list[GridResult]:
    if rotate:
        return [res for rot in range(0, 25) for res in __find_grid_words(rotate_grid(grid, rot), rot, reverse)]  # python is a terrible language
    else:
        return __find_grid_words(grid, 0, reverse)

def rotate_grid(grid: str, rot: int) -> str:
    return CaesarCipher().encode(grid.encode("utf-8"), str(rot))

def __find_grid_words(grid: str, rot_hint: int, reverse: bool) -> list[GridResult]:
    rows = [row for row in grid.split() if row != ""]
    if any([len(row) != len(rows[0]) for row in rows]):
        return [GridResult("Not a grid", -1, -1, "", -1, False)]

    cols = ["".join([row[col_i] for row in rows]) for col_i in range(len(rows[0]))]

    res = []

    for i, row in enumerate(rows):
        for match in search_string_for_submatches(row, reverse):
            res.append(GridResult(match[0], match[1], i, "horizontal", rot_hint, match[2]))
    for i, col in enumerate(cols):
        for match in search_string_for_submatches(col, reverse):
            res.append(GridResult(match[0], i, match[1], "vertical", rot_hint, match[2]))

    return res

def search_string_for_submatches(s: str, reverse: bool) -> list[tuple[str, int, bool]]:
    matches = []

    print("searching", s)

    for start in range(len(s) - 1):
        for end in range(start + 1 + 3, len(s)+1):  # min length: 3
            if s[start:end] in dictionary_popular:
                matches.append((s[start:end], start, False))
            if reverse and s[start:end][::-1] in dictionary_popular:
                matches.append((s[start:end][::-1], start, True))

    return matches

