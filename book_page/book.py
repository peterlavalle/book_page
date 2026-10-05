from abc import ABC, abstractmethod
from collections.abc import Generator as gen
from functools import cached_property
from pathlib import Path


class Book(ABC):
    def __contains__(self, name):
        return name in self.keys()

    @abstractmethod
    def __getitem__(self, name): ...

    @abstractmethod
    def keys(self): ...

    @abstractmethod
    def stream_copy(self, into: Path) -> gen[tuple[str, int, list[str]]]: ...

    def __iter__(self):
        for name in self.keys():
            with self[name] as page:
                yield page


class Page(ABC):
    def __init__(self, name: str, page: object):
        self._name = name
        self._page = page
        self._changed = False

    @abstractmethod
    def stream_rows(self) -> gen[tuple[int, list[str]]]: ...

    @cached_property
    def name(self) -> str:
        return self._name
