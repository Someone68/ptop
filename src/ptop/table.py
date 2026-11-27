from typing import Any


def render_table(cols: list[str], rows: list[list[Any]]):
    cells = [[str(c) for c in row] for row in [cols, *rows]]
    widths = [max(len(r[i]) for r in cells) for i in range(len(cols))]

    def line(row):
        return " │ ".join(c.ljust(w) for c, w in zip(row, widths))

    header = [line(cells[0]), "─┼─".join("─" * w for w in widths)]
    body = [line(r) for r in cells[1:]]

    return header, body
