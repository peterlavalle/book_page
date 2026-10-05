import contextlib
import csv
import shutil
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
        self._page_cache = {}

    def keys(self):
        return self._page_files.keys()

    @contextlib.contextmanager
    def __getitem__(self, name):
        if name in self._page_cache:
            raise RuntimeError(f"only one copy of a page can be open at once {name=}")

        file = self._page_files[name]

        self._page_cache[name] = [
            line
            for line in csv.reader(
                file.open(), delimiter="\t" if file.name.endswith(".tsv") else ","
            )
        ]

        class CSVPage(Page):
            def cell_get(self, r: int, c: int):
                return self._page[r][c]

            def cell_set(self, r: int, c: int, v: any):
                self._page[r][c] = v

            def get_rows(self) -> int:
                return len(self._page)

            def get_columns(self) -> int:
                return max([len(row) for row in self._page])

        page = CSVPage(name, self._page_cache[name])
        yield page
        if page._changed:
            with file.open("w") as stream:
                csv.writer(
                    stream, delimiter="\t" if file.name.endswith(".tsv") else ","
                ).writerows(self._page_cache[name])
        self._page_cache.pop(name)

    def stream_rows(self, want: None | list[str] = None):
        raise NotImplementedError('move this to Page')
        if want:
            missing = [i for i in want if i not in self._page_files]
            if missing:
                raise ValueError(f"{missing=}")
        for name, file in self._page_files.items():
            if want is None or name in want:
                with file.open() as source:
                    reader = csv.reader(
                        source,
                        delimiter="\t" if file.name.endswith(".tsv") else ",",
                    )
                    for row in reader:
                        yield (name, row)

    def stream_copy(self, into: Path):
        if into.is_file():
            raise RuntimeError(f"can't write csvs to {into} because it's a file")

        open_file = None
        open_name = None
        writer = None

        for name, row in self.stream_rows():
            # if the page name has changed -> open a new stream
            if open_name != name:
                if open_file:
                    open_file.close()
                into.mkdir(parents=True, exist_ok=True)
                open_name = name
                open_file = (into / self._page_files[name].name).open("w")
                writer = csv.writer(
                    open_file,
                    delimiter="\t" if open_file.name.endswith(".tsv") else ",",
                )
            yield (name, row)
            writer.writerow(row)
        if open_file:
            open_file.close()


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
