"""Thread-aware colored logging for the OSM bot."""

import threading
from datetime import datetime

from termcolor import colored

from core.config import REDIRECTION

_THREAD_COLORS: dict[str, str] = {
    "Hilo 1": "red",
    "Hilo 2": "green",
    "Hilo 3": "blue",
    "Hilo 4": "yellow",
}


def log(msg: str, color: str = "white") -> None:
    """Thread-safe colored log; also appends to REDIRECTION file."""
    line = f"{threading.current_thread().name}-> {msg}"
    print(colored(line, color))
    REDIRECTION.parent.mkdir(parents=True, exist_ok=True)
    with REDIRECTION.open("a") as fh:
        fh.write(line + "\n")


def tlog(msg: str) -> None:
    """Log using the current thread's canonical color."""
    log(msg, _THREAD_COLORS.get(threading.current_thread().name, "white"))
