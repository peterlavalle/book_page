from pathlib import Path

import openpyxl

from .book import Book, normalize_cell


class XLSXBook(Book):
    def __init__(self, data: Path):
        assert data.is_file(), f"not found {data=}"
        self._book = openpyxl.load_workbook(data, read_only=True)

    def __contains__(self, name):
        return name in [page.title for page in self._book.worksheets]

    def __getitem__(self, name):
        page = self._book[name]
        for row in range(page.max_row):
            yield [
                normalize_cell(page.cell(row + 1, col + 1).value)
                for col in range(page.max_column)
            ]
