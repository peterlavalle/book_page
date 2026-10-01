from pathlib import Path

from .book import Page
from .csv_book import CSVBook
from .xlsx_book import XLSXBook

# use this or-type instead of the "real" base class since we only have/support these two
Book = CSVBook | XLSXBook


def book_open(src: str | Path | list[Path]) -> Book:
    if isinstance(src, str):
        src = Path(str)

    if isinstance(src, Path) and src.name.endswith(".xlsx"):
        return XLSXBook(src)
    else:
        return CSVBook(src)


def book_copy(src: str | Path | list[Path], out: str | Path) -> Book:
    if isinstance(src, str):
        src = Path(str)

    if isinstance(src, Path) and src.name.endswith(".xlsx"):
        return XLSXBook.copy(src, out)
    else:
        return CSVBook.copy(src, out)


__all__ = [  # noqa: PLE0604
    Book,
    Page,
    book_open,
    book_copy,
]
