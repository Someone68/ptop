import threading
from time import sleep

import psutil

ATTRS = [
    "pid",
    "name",
    "exe",
    "username",
    "memory_info",
    "cpu_percent",
    "threads",
]


class Processes:
    def __init__(self) -> None:
        self.procs: list[dict] | None = None
        self.lock = threading.Lock()
        self._stop = threading.Event()

    def poll(self):
        while True:
            proc_iter = psutil.process_iter(ATTRS)

            proclst = []
            for proc in proc_iter:
                proclst.append(proc.info)

            with self.lock:
                self.procs = proclst
            self._stop.wait(2)

    def get_procs(self):
        with self.lock:
            return self.procs
