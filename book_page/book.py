from abc import abstractmethod


def normalize_cell(cell):
    if cell is not None:
        cell = str(cell)
        if cell:
            return cell


class Book:
    def __contains__(self, name):
        return name in self.keys()

    @abstractmethod
    def __getitem__(self, name): ...

    @abstractmethod
    def keys(self): ...

    def __iter__(self):
        for name in self.keys():
            with self[name] as page:
                yield page


class Page:
    def __init__(self, page: object):
        self._page = page
        self._changed = False

    @abstractmethod
    def cell_get(self, r: int, c: int): ...

    @abstractmethod
    def cell_set(self, r: int, c: int, v: any): ...

    @abstractmethod
    def get_rows(self) -> int: ...

    @abstractmethod
    def get_columns(self) -> int: ...

    @property
    def rows(self) -> int:
        return self.get_rows()

    @property
    def columns(self) -> int:
        return self.get_columns()

    def __getitem__(self, rc: tuple[int, int]):
        (r, c) = rc
        assert 0 <= r < self.rows
        assert 0 <= c < self.columns

        return Cell(self, r, c)


class Cell:
    def __init__(self, page: Page, row: int, col: int):
        self._page = page
        self._row = row
        self._col = col
        self._got = {}

    @property
    def value(self):
        return normalize_cell(self._page.cell_get(self._row, self._col))

    @value.setter
    def value(self, val):
        self._page._changed = True
        return self._page.cell_set(self._row, self._col, normalize_cell(val))
