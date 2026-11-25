import time
import platform
from rich import print
from rich.table import Table
from rich.live import Live
from rich.control import Control
from rich.text import Text
from ptop.console import console, term
from psutil import cpu_percent, sensors_temperatures
import threading


def cpu_temp_linux() -> float | None:
    temps = sensors_temperatures()
    for name in ("coretemp", "k10temp", "zenpower", "cpu_thermal", "acpitz"):
        if name in temps and temps[name]:
            entries = temps[name]
            for e in entries:
                if e.label in ("Package id 0", "Tctl", "Tdie"):
                    return e.current
            return entries[0].current
    return None


class Cpu:
    def __init__(self) -> None:
        self.used_percentage: float = cpu_percent(interval=None)
        self.temperature: float | None = None
        self.lock = threading.Lock()
        self._stop = threading.Event()

    def poll(self):
        while True:
            percent = cpu_percent(interval=None)
            temp = cpu_temp_linux()
            with self.lock:
                self.used_percentage = percent
                self.temperature = temp
            self._stop.wait(1)
