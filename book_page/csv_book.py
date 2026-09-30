import csv
from pathlib import Path

from book_page.book import Book, normalize_cell


class CSVBook(Book):
    def __init__(self, data: Path | list[Path]):

        # get it to a list
        if isinstance(data, Path):
            data = sorted(
                list(data.glob("*.csv")) + list(data.glob("*.tsv")),
                key=lambda file: file.stem.lower(),
            )

        # compute dupes
        collisions = sorted(
            [
                page
                for page in data
                if len(
                    [them for them in data if them.stem.lower() == page.stem.lower()]
                )
                != 1
            ],
            key=lambda file: file.name.lower(),
        )
        # raise error if there are dupes
        if collisions:
            raise ValueError(
                f"the following csv files have name collisions\n    {
                    '\n    '.join(
                        [
                            (file.stem.lower() + '\n        ' + str(file))
                            for file in collisions
                        ]
                    )
                }"
            )

        self._page_files = {page.stem.lower(): page for page in data}

    def __contains__(self, name):
        assert isinstance(name, str)
        return name in self._page_files

    def __getitem__(self, name):

        file = self._page_files[name]
        for line in csv.reader(
            file.open(), delimiter="\t" if file.name.endswith(".tsv") else ","
        ):
            yield [normalize_cell(cell) for cell in line]
