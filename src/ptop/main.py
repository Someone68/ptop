import time
from rich import box, print
from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.control import Control
from rich.text import Text
from ptop.console import console, term
from psutil import cpu_percent
import threading

from ptop.cpu import Cpu
from ptop.proc import ATTRS, Processes


class Ptop:
    def __init__(self, cpu: Cpu, proc: Processes) -> None:
        self.cpu: Cpu = cpu
        self.proc: Processes = proc
        self.bindings: dict = {"q": self.quit}
        self.running = True

    def quit(self):
        self.running = False

    def __rich__(self):
        with self.cpu.lock:
            pct, temp = self.cpu.used_percentage, self.cpu.temperature
        text = f"CPU: {pct}% {temp if temp else 'N/A'}deg"
        proctable = Table(box=box.SIMPLE)
        for attr in ATTRS:
            proctable.add_column(attr)
        procs = self.proc.get_procs()
        if procs is not None:
            for process in procs:
                proctable.add_row(*(str(process[attr]) for attr in ATTRS))
        return Group(
            Panel(Text(text), title="CPU"), Panel(proctable, title="Processes")
        )


def main():
    cpu = Cpu()
    threading.Thread(target=cpu.poll, daemon=True).start()

    proc = Processes()
    threading.Thread(target=proc.poll, daemon=True).start()

    ptop = Ptop(cpu, proc)
    with Live(ptop, refresh_per_second=4, screen=True), term.cbreak():
        while ptop.running:
            key = term.inkey(timeout=0.1)
            if not key:
                continue

            action = ptop.bindings.get(key.name or str(key))
            if action:
                action()


if __name__ == "__main__":
    main()
