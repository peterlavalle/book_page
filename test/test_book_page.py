from pathlib import Path

import pytest

from book_page import CSVBook, XLSXBook

data = Path(__file__).parent / "data" / __name__

import textwrap


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
def test_read_data(kind, path):

    book = kind(path)

    assert "data_3x4" in book
    assert "data_3x6" in book

    assert book.max_rows("data_3x4") == 4
    assert book.max_columns("data_3x4") == 4
    expected = iter(
        [
            ["id", "name", "age", "score"],
            ["1", "Alice", "28", "87.5"],
            ["2", "Bob", "34", "92.1"],
            ["3", "Carol", "22", "78.3"],
        ]
    )
    for obtained in book["data_3x4"]:
        assert obtained == next(expected)

    assert book.max_rows("data_3x6") == 4
    assert book.max_columns("data_3x6") == 6
    expected = iter(
        [
            ["id", "name", "age", "score", "city", "active"],
            ["1", "Alice", "28", "87.5", "London", "True"],
            ["2", "Bob", "34", "92.1", "Paris", "False"],
            ["3", "Carol", "22", "78.3", "Tokyo", "True"],
        ]
    )
    for obtained in book["data_3x6"]:
        assert obtained == next(expected)
