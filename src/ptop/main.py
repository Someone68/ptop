from prompt_toolkit import Application
from prompt_toolkit.data_structures import Point
from prompt_toolkit.formatted_text import StyleAndTextTuples
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit, Window, VSplit
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout
import threading

from ptop.cpu import Cpu
from ptop.proc import ATTRS, Processes, get_table
from ptop.table import render_table

cpu = Cpu()
proc = Processes()


class ProcessView:
    def __init__(self) -> None:
        self.selected_pid = None
        self._idx = 0
        self._procs = None
        self._header: list[str] = []
        self._body: list[str] = []
        self._pids: list[int] = []

    def _update(self):
        procs = proc.get_procs() or []
        if procs is self._procs:
            return
        self._procs = procs
        rendered = render_table(*get_table(ATTRS, procs))
        self._header = rendered[0]
        self._body = rendered[1]
        self._pids = [p["pid"] for p in procs]

    def idx(self) -> int:
        self._update()
        if not self._pids:
            return 0
        if self.selected_pid in self._pids:
            self._idx = self._pids.index(self.selected_pid)
            return self._idx
        self._idx = min(self._idx, len(self._pids) - 1)
        self.selected_pid = self._pids[self._idx]
        return self._idx

    def move(self, d):
        if not self._pids:
            return
        i = max(0, min(self.idx() + d, len(self._pids) - 1))
        self._idx = i
        self.selected_pid = self._pids[i]

    def render_header(self):
        self._update()
        return "\n".join(self._header)

    def render_body(self) -> StyleAndTextTuples:
        idx = self.idx()
        return [
            ("reverse" if n == idx else "", line + "\n")
            for n, line in enumerate(self._body)
        ]


view = ProcessView()
body_window = Window(
    always_hide_cursor=True,
    content=FormattedTextControl(
        text=view.render_body,
        focusable=True,
        get_cursor_position=lambda: Point(0, view.idx()),
    ),
)

root_container = HSplit(
    [
        Window(
            always_hide_cursor=True,
            content=FormattedTextControl(
                text=lambda: f"CPU: {cpu.used_percentage:.1f}% {cpu.temperature}°C"
            ),
        ),
        Window(height=1, char="─"),
        Window(content=FormattedTextControl(text=view.render_header)),
        body_window,
    ]
)

layout = Layout(root_container)
kb = KeyBindings()


@kb.add("q")
@kb.add("c-c")
def exit_(e):
    e.app.exit()


@kb.add("up")
@kb.add("k")
def _(e):
    view.move(-1)


@kb.add("down")
@kb.add("j")
def _(e):
    view.move(1)


app = Application(key_bindings=kb, layout=layout, full_screen=True, refresh_interval=1)


def main():
    threading.Thread(target=cpu.poll, daemon=True).start()
    threading.Thread(target=proc.poll, daemon=True).start()
    app.run()


if __name__ == "__main__":
    main()
