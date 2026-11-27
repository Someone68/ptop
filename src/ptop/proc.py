import threading
from time import sleep
from typing import Any

import psutil

ATTRS = [
    "pid",
    "name",
    "exe",
    "username",
    "memory_usage",
    "cpu_percent",
    "num_threads",
]

ATTRS_MAP = {
    "net_connections": "Network",
    "cpu_affinity": "CPU Affinity",
    "cpu_num": "CPU Core",
    "cpu_percent": "CPU%",
    "cwd": "CWD",
    "environ": "Environment",
    "exe": "Command",
    "gids": "Group IDs",
    "io_counters": "I/O",
    "memory_percent": "MEM%",
    "memory_usage": "MemB",
    "name": "Name",
    "num_ctx_switches": "# CTX Switches",
    "num_threads": "#Threads",
    "open_files": "Open Files",
    "pid": "PID",
    "ppid": "PPID",
    "status": "Status",
    "terminal": "Terminal",
    "uids": "UIDs",
    "username": "User",
}

DERIVED = {"memory_usage": "memory_info"}


def fetch_attrs(keys) -> list[str]:
    needed = {DERIVED.get(k, k) for k in keys}
    return [a for a in needed if a is not None and hasattr(psutil.Process, a)]


def fmt(key, val):
    if val is None:
        return "-"
    if key == "memory_usage":
        return f"{val.rss / 1024**2:.1f}M"
    if key in ("cpu_percent", "memory_percent"):
        return f"{val:.1f}"
    if key == "environ":
        return f"{len(val)} vars"
    if key in ("open_files", "net_connections"):
        return str(len(val))
    if key == "cpu_affinity":
        return ",".join(map(str, val))
    if key in ("uids", "gids"):
        return str(val.real)
    if key == "num_ctx_switches":
        return str(val.voluntary + val.involuntary)
    if key == "io_counters":
        return f"r{val.read_bytes // 1024**2}M w{val.write_bytes // 1024**2}M"
    if key == "exe":
        return val[-40:]
    return str(val)


def get_table(keys, procs):
    attrs = fetch_attrs(keys)
    shown = [k for k in keys if DERIVED.get(k, k) in attrs]
    headers = [ATTRS_MAP[k] for k in shown]
    rows = [[fmt(k, info.get(DERIVED.get(k, k))) for k in shown] for info in procs]
    return headers, rows


class Processes:
    def __init__(self) -> None:
        self.procs: list[dict[str, Any]] | None = None
        self.lock = threading.Lock()
        self._stop = threading.Event()

    def poll(self):
        while True:
            proc_iter = psutil.process_iter(fetch_attrs(ATTRS))

            proclst = []
            for proc in proc_iter:
                proclst.append(proc.info)

            proclst.sort(key=lambda i: i.get("cpu_percent") or 0, reverse=True)
            with self.lock:
                self.procs = proclst
            self._stop.wait(1)

    def get_procs(self):
        with self.lock:
            return self.procs
