"""Injectable wall-clock timestamps. Tests do not have to sleep."""

import threading
import time


class SystemClock:
    def __call__(self):
        return time.time()


class ManualClock:
    def __init__(self, value=1000.0):
        self._value = float(value)
        self._lock = threading.Lock()

    def __call__(self):
        with self._lock:
            return self._value

    def advance(self, seconds):
        if seconds < 0:
            raise ValueError("clock cannot move backwards")
        with self._lock:
            self._value += seconds
            return self._value
