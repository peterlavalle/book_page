from pathlib import Path

from book_page import CSVBook

test_data = Path(__file__).parent / "data" / __name__


def test_bom_is_removed():
    book = CSVBook([test_data / "page-desc.csv"])

    obtained = []
    with book["page-desc"] as page:
        for idx, row in page.stream_rows():
            assert idx == len(obtained)
            obtained.append(row.copy())

    expected = [
        ["foo", "pid", "glitter"],
        ["bar", "nuh71", "road"],
        [
            "shoe",
            "nuh06",
            "can't recall the date but on 12/11/2001 they had an itchy tummy",
        ],
        ["agreed on 21st jul 2017", "nuh23", "grip"],
        ["farm", "nuh67", "grim"],
        ["cake", "nuh27", "cheese"],
        ["glip", "nuh65", "jkl"],
    ]
    assert obtained == expected
