import time


class RateLimiter:
    def __init__(self, min_interval: float = 2.0) -> None:
        self._min_interval = min_interval
        self._last_request: float = 0.0

    def wait(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_request
        if elapsed < self._min_interval:
            time.sleep(self._min_interval - elapsed)
        self._last_request = time.monotonic()
