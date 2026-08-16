import os
from collections import deque
from time import time

# Conservative cap so the app stays within free-tier search usage even if Google changes quotas.
SEARCH_CALLS_PER_DAY = int(os.getenv("GEMINI_SEARCH_CALLS_PER_DAY", "400"))
_calls = deque()

def allow_search() -> bool:
    now=time()
    while _calls and now-_calls[0] > 86400: _calls.popleft()
    if len(_calls) >= SEARCH_CALLS_PER_DAY: return False
    _calls.append(now); return True
