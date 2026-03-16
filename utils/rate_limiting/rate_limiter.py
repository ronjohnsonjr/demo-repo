"""Rate limiter that respects GitHub API rate-limit headers."""

import logging
import time
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# GitHub rate-limit response headers
HEADER_LIMIT = "X-RateLimit-Limit"
HEADER_REMAINING = "X-RateLimit-Remaining"
HEADER_RESET = "X-RateLimit-Reset"
HEADER_USED = "X-RateLimit-Used"


@dataclass
class RateLimitState:
    """Current snapshot of rate-limit counters."""

    limit: int = 60  # default unauthenticated
    remaining: int = 60
    reset_at: float = 0.0
    used: int = 0


class RateLimiter:
    """Pause requests when approaching the GitHub rate limit.

    Reads ``X-RateLimit-*`` headers from every response and sleeps
    automatically when the remaining quota drops below ``buffer``.
    """

    def __init__(self, buffer: int = 5) -> None:
        self.buffer = buffer
        self.state = RateLimitState()
        self._request_count: int = 0

    def update_from_headers(self, headers: dict) -> None:
        """Update internal state from GitHub response headers."""
        if HEADER_REMAINING in headers:
            self.state.remaining = int(headers[HEADER_REMAINING])
        if HEADER_LIMIT in headers:
            self.state.limit = int(headers[HEADER_LIMIT])
        if HEADER_RESET in headers:
            self.state.reset_at = float(headers[HEADER_RESET])
        if HEADER_USED in headers:
            self.state.used = int(headers[HEADER_USED])
        self._request_count += 1

    def wait_if_needed(self) -> None:
        """Sleep until the rate-limit window resets if quota is low."""
        if self.state.remaining <= self.buffer:
            sleep_seconds = max(0, self.state.reset_at - time.time()) + 1
            if sleep_seconds > 0:
                logger.warning(
                    "Rate limit nearly exhausted (%d/%d remaining). "
                    "Sleeping %.1fs until reset.",
                    self.state.remaining,
                    self.state.limit,
                    sleep_seconds,
                )
                time.sleep(sleep_seconds)

    @property
    def total_requests(self) -> int:
        """Total number of requests tracked by this limiter."""
        return self._request_count
