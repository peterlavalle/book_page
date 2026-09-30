import textwrap
from pathlib import Path

import pytest

from book_page import CSVBook, XLSXBook

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
def test_read_data(kind, path, to_str: bool):

    book = kind(str(path) if to_str else path)

    assert "data_3x4" in book
    assert "data_3x6" in book

    with book["data_3x4"] as page:
        page_check(page, data_3x4)

    with book["data_3x6"] as page:
        page_check(page, data_3x6)


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
    "tmp_str",
    [False, True],
)
def test_copy_book(
    src_str: bool, out_str: bool, tmp_str: bool, kind, path, tmp_path: Path
):
    book = kind.copy(
        str(path) if src_str else path, str(tmp_path) if out_str else tmp_path
    )

    for page in book:
        for r in range(page.rows):
            for c in range(page.columns):
                page[r, c].value = f"edit[{r},{c}]{page[r, c].value}"

    out_path = (tmp_path / path.name) if path.is_file() else tmp_path
    book = kind(str(out_path) if tmp_str else out_path)

    assert "data_3x4" in book
    assert "data_3x6" in book

    with book["data_3x4"] as page:
        page_check(
            page,
            [
                [f"edit[{r},{c}]{data_3x4[r][c]}" for c in range(len(data_3x4[0]))]
                for r in range(len(data_3x4))
            ],
        )

    with book["data_3x6"] as page:
        page_check(
            page,
            [
                [f"edit[{r},{c}]{data_3x6[r][c]}" for c in range(len(data_3x6[0]))]
                for r in range(len(data_3x6))
            ],
        )


def page_check(page, data):
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
