import time
from collections import defaultdict
from typing import Dict, List, Tuple
from security.config import security_config


class RateLimiter:
    """Sliding-window in-memory rate limiter per client key."""

    def __init__(self, limit: int = 120, window_seconds: int = 60):
        self.limit = limit
        self.window_seconds = window_seconds
        self.requests: Dict[str, List[float]] = defaultdict(list)

    def is_allowed(self, client_key: str, cost: int = 1) -> Tuple[bool, int]:
        """
        Returns (is_allowed, retry_after_seconds).
        """
        if not security_config.RATE_LIMIT_ENABLED:
            return True, 0

        now = time.time()
        window_start = now - self.window_seconds

        # Clean timestamps older than the sliding window
        valid_timestamps = [ts for ts in self.requests[client_key] if ts > window_start]
        self.requests[client_key] = valid_timestamps

        if len(valid_timestamps) + cost > self.limit:
            oldest = valid_timestamps[0] if valid_timestamps else now
            retry_after = max(1, int(self.window_seconds - (now - oldest)))
            return False, retry_after

        # Record this request
        for _ in range(cost):
            self.requests[client_key].append(now)

        return True, 0

    def reset(self):
        """Reset rate limiter state (useful for tests)."""
        self.requests.clear()


rate_limiter = RateLimiter(
    limit=security_config.RATE_LIMIT,
    window_seconds=security_config.RATE_LIMIT_WINDOW,
)
