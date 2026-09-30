def normalize_cell(cell):
    if cell is not None:
        cell = str(cell)
        if cell:
            return cell


class Book:
    def __contains__(self, name):
        raise NotImplementedError()

    def __getitem__(self, name):
        raise NotImplementedError()

    def max_rows(self, page: str) -> int:
        count = 0
        for _ in self[page]:
            count += 1
        return count

    def max_columns(self, page: str) -> int:
        count = 0
        for row in self[page]:
            count = max(count, len(row))
        return count
