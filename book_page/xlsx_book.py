import contextlib
import shutil
from pathlib import Path

import openpyxl

from .book import Book, Page


class XLSXBook(Book):
    @classmethod
    def copy(cls, src: str | Path, out: str | Path):
        if isinstance(src, str):
            src = Path(src)
        if isinstance(out, str):
            out = Path(out)
        if not src.is_file():
            raise RuntimeError(f"xlsx file not found {src}")

        if out.is_dir():
            out = out / src.name

        shutil.copy2(src, out)

        return XLSXBook(out, False)

    def __init__(self, file: str | Path, read_only=True):
        if isinstance(file, str):
            file = Path(file)
        if not file.is_file():
            raise RuntimeError(f"xlsx file not found {file}")
        self._file = file
        self._book = openpyxl.load_workbook(file, read_only=read_only)
        self._open = None

    def keys(self):
        return [page.title for page in self._book.worksheets]

    @contextlib.contextmanager
    def __getitem__(self, name):

        if self._open is not None:
            raise RuntimeError(
                f"only one page can be open at a time {self._open=} {name=}"
            )

        class XLSXPage(Page):
            def cell_get(self, r: int, c: int):
                return self._page.cell(r + 1, c + 1).value

            def cell_set(self, r: int, c: int, v: any):
                self._page.cell(r + 1, c + 1).value = v

            def get_rows(self) -> int:
                return self._page.max_row

            def get_columns(self) -> int:
                return self._page.max_column

        self._open = name
        page = XLSXPage(self._book[name])
        yield page
        if page._changed:
            self._book.save(self._file)
        self._open = None
