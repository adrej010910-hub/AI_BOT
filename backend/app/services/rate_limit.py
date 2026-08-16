import time
from collections import deque

class DailyLimiter:
    def __init__(self, limit: int = 500):
        self.limit = limit
        self.calls = deque()
    def allow(self) -> bool:
        now = time.time()
        while self.calls and now - self.calls[0] > 86400:
            self.calls.popleft()
        if len(self.calls) >= self.limit:
            return False
        self.calls.append(now)
        return True

GEMINI_SEARCH_LIMITER = DailyLimiter(500)
