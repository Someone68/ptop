import time
from rich import print
from rich.table import Table
from rich.live import Live
from rich.control import Control
from rich.text import Text
from ptop.console import console, term
from psutil import cpu_percent
import threading

from ptop.cpu import Cpu


class Ptop:
    def __init__(self, cpu: Cpu) -> None:
        self.cpu: Cpu = cpu
        self.bindings: dict = {"q": self.quit}
        self.running = True

    def quit(self):
        self.running = False

    def __rich__(self):
        with self.cpu.lock:
            pct, temp = self.cpu.used_percentage, self.cpu.temperature
        text = f"CPU: {pct}% {temp if temp else 'N/A'}deg"
        return Text(text)


def main():
    cpu = Cpu()
    threading.Thread(target=cpu.poll, daemon=True).start()

    ptop = Ptop(cpu)
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
