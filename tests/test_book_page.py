import textwrap
from pathlib import Path

import pytest

from book_page import CSVBook, XLSXBook, Book, book_open, book_copy

data = Path(__file__).parent / "data" / __name__


data_3x4 = [
    ["id", "name", "age", "score"],
    ["1", "Alice", "28", "87.5"],
    ["2", "Bob", "34", "92.1"],
    ["3", "Carol", "22", "78.3"],
]
data_3x6 = [
    ["id", "name", "age", "score", "city", "active"],
    ["1", "Alice", "28", "87.5", "London", "True"],
    ["2", "Bob", "34", "92.1", "Paris", "False"],
    ["3", "Carol", "22", "78.3", "Tokyo", "True"],
]


def test_csv_name_collision():
    with pytest.raises(ValueError) as error:
        CSVBook([data / "data_3x4.csv", data / "data_3x4.tsv"])
    assert (
        textwrap.dedent(
            f"""
            the following csv files have name collisions
                data_3x4
                    {data}/data_3x4.csv
                data_3x4
                    {data}/data_3x4.tsv
            """
        ).strip()
        == str(error.value).strip()
    )


@pytest.mark.parametrize(
    "kind, path",
    [
        (CSVBook, data),
        (XLSXBook, data / "data.xlsx"),
    ],
)
@pytest.mark.parametrize(
    "to_str",
    [False, True],
)
@pytest.mark.parametrize(
    "generic",
    [False, True],
)
@pytest.mark.parametrize(
    "name, data",
    [
        ("data_3x4", data_3x4),
        ("data_3x6", data_3x6),
    ],
)
def test_read_data(kind, path, to_str: bool, generic: bool, name, data):

    # arrange
    book: Book

    # act
    if generic:
        book = book_open(str(path) if to_str else path)
    else:
        book = kind(str(path) if to_str else path)

    # assert
    assert isinstance(book, kind)
    assert name in book
    with book[name] as page:
        page_check(page, name, data)


@pytest.mark.parametrize(
    "kind, path",
    [
        (CSVBook, data),
        (XLSXBook, data / "data.xlsx"),
    ],
)
@pytest.mark.parametrize(
    "src_str",
    [False, True],
)
@pytest.mark.parametrize(
    "out_str",
    [False, True],
)
@pytest.mark.parametrize(
    "end_str",
    [False, True],
)
@pytest.mark.parametrize(
    "generic_copy",
    [False, True],
)
@pytest.mark.parametrize(
    "generic_open",
    [False, True],
)
@pytest.mark.parametrize(
    "name, data",
    [
        ("data_3x4", data_3x4),
        ("data_3x6", data_3x6),
    ],
)
def test_copy_book(
    src_str: bool,
    out_str: bool,
    end_str: bool,
    kind,
    path,
    tmp_path: Path,
    generic_copy: bool,
    generic_open: bool,
    name,
    data,
):
    # arrange
    copy_book: Book
    changed_data = [
        [f"edit[{r},{c}]{data[r][c]}" for c in range(len(data[0]))]
        for r in range(len(data))
    ]
    src = str(path) if src_str else path
    out = str(tmp_path) if out_str else tmp_path
    end: str | Path = (tmp_path / path.name) if path.is_file() else tmp_path
    if end_str:
        end = str(end)

    # act
    if generic_copy:
        copy_book = book_copy(src, out)
    else:
        copy_book = kind.copy(src, out)
    for page in copy_book:
        for r in range(page.rows):
            for c in range(page.columns):
                page[r, c].value = f"edit[{r},{c}]{page[r, c].value}"
    changed_book: Book
    if generic_open:
        changed_book = book_open(end)
    else:
        changed_book = kind(end)

    assert name in copy_book
    assert name in changed_book
    assert isinstance(copy_book, kind)
    assert isinstance(changed_book, kind)

    with changed_book[name] as page:
        page_check(page, name, changed_data)


def page_check(page, name, data):
    assert page.name == name
    assert page.rows == len(data)
    assert page.columns == len(data[0])
    e = data[0][0]
    o = page[0, 0].value
    assert e == o, f"mismatch\n\t{e=}\n\t{o=}"
    for r in range(page.rows):
        for c in range(page.columns):
            assert page[r, c].value == data[r][c]


def test_non_file(tmp_path: Path):
    with pytest.raises(RuntimeError) as error:
        XLSXBook(tmp_path / "foo.xlsx")
    assert f"xlsx file not found {tmp_path}/foo.xlsx" == str(error.value)
    with pytest.raises(RuntimeError) as error:
        XLSXBook.copy(tmp_path / "bar.xlsx", tmp_path / "foo.xlsx")
    assert f"xlsx file not found {tmp_path}/bar.xlsx" == str(error.value)


def test_csv_file():
    path = data / "data.xlsx"

    with pytest.raises(RuntimeError) as error:
        CSVBook(path)
    assert f"need a dir or list of files, but, got a file {path=}" == str(error.value)


def test_xlsx_multi_page():
    book = XLSXBook(data / "data.xlsx")
    with (
        pytest.raises(RuntimeError) as error,
        book["data_3x4"] as page1,
        book["data_3x6"] as page2,
    ):
        pytest.fail("shouldn't work" + page1 + page2)
    assert (
        "only one page can be open at a time self._open='data_3x4' name='data_3x6'"
        == str(error.value)
    )


def test_xlsx_name_cap():
    book = XLSXBook(data / "data.xlsx")
    long_name = "name which exceeds 31 characters"
    with (
        pytest.raises(RuntimeError) as error,
        book[long_name] as page,
    ):
        raise RuntimeError(f"{long_name=} should have failed {page.name=}")
    assert "excel limits you to 31 character page names" == str(error.value)


def test_csv_multi_page():
    book = CSVBook(data)
    with (
        pytest.raises(RuntimeError) as error,
        book["data_3x4"] as page1,
        book["data_3x4"] as page2,
    ):
        pytest.fail("shouldn't work" + page1 + page2)
    assert "only one copy of a page can be open at once name='data_3x4'" == str(
        error.value
    )
