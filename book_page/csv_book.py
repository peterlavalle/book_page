import contextlib
import csv
import shutil
from pathlib import Path
from collections.abc import Generator as gen
from pathlib import Path

from book_page.book import Book, Page


class CSVBook(Book):
    @classmethod
    def copy(cls, src: str | Path | list[Path], out: str | Path):
        src = csv_files(src)

        if isinstance(out, str):
            out = Path(out)

        for s in src:
            shutil.copy2(s, out / s.name)

        return CSVBook([out / s.name for s in src])

    def __init__(self, path: str | Path | list[Path]):
        self._page_files = {page.stem.lower(): page for page in csv_files(path)}

    def keys(self):
        return self._page_files.keys()

    @contextlib.contextmanager
    def __getitem__(self, name):

        class CSVPage(Page):
            def stream_rows(self) -> gen[tuple[int, list[str]]]:
                assert isinstance(self._page, Path)
                with self._page.open() as file:
                    for row, line in enumerate(
                        csv.reader(
                            file,
                            delimiter="\t" if file.name.endswith(".tsv") else ",",
                        )
                    ):
                        # normalize and yield the row

                        yield (
                            row,
                            [
                                cell if cell else None
                                for cell in [
                                    cell.strip() if isinstance(cell, str) else cell
                                    for cell in line
                                ]
                            ],
                        )

        assert isinstance(self._page_files[name], Path)
        yield CSVPage(name, self._page_files[name])

    def stream_copy(self, into: Path):
        if into.is_file():
            raise RuntimeError(f"can't write csvs to {into} because it's a file")

        into.mkdir(parents=True, exist_ok=True)

        for page in self:
            name = page.name
            file = self._page_files[name].name
            with (into / file).open("w") as data:
                writer = csv.writer(
                    data, delimiter="\t" if file.endswith(".tsv") else ","
                )

                for row, cell in page.stream_rows():
                    yield name, row, cell
                    writer.writerow(cell)


def csv_files(path: str | Path | list[Path]):
    if isinstance(path, str):
        path = Path(path)

    # get it to a list
    if isinstance(path, Path):
        if path.is_file():
            raise RuntimeError(f"need a dir or list of files, but, got a file {path=}")
        path = sorted(
            list(path.glob("*.csv")) + list(path.glob("*.tsv")),
            key=lambda file: file.stem.lower(),
        )

    # compute dupes
    collisions = sorted(
        [
            page
            for page in path
            if len([them for them in path if them.stem.lower() == page.stem.lower()])
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

    return path
