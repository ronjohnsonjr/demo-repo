"""Unit tests for utils/rate_limiting/rate_limiter.py.

Validates header parsing, buffer threshold sleep behavior, and
request counting in RateLimiter.
"""

import time
import unittest.mock
from unittest.mock import patch

import pytest

from data.constants import RATE_LIMIT_BUFFER
from utils.rate_limiting.rate_limiter import (
    HEADER_LIMIT,
    HEADER_REMAINING,
    HEADER_RESET,
    HEADER_USED,
    RateLimitState,
    RateLimiter,
)


@pytest.mark.test_rate_limiting
class TestRateLimitState:
    """Unit tests for RateLimitState dataclass defaults."""

    def test_default_limit_is_60(self):
        """Verify unauthenticated default limit is 60.

        Setup: Instantiate RateLimitState with no arguments.
        Action: Read the limit attribute.
        Assertions: Limit equals 60 (unauthenticated GitHub rate limit).
        """
        # Action
        state = RateLimitState()

        # Assertions
        assert state.limit == 60

    def test_default_remaining_is_60(self):
        """Verify remaining starts at 60 (full quota).

        Setup: Instantiate RateLimitState with no arguments.
        Action: Read the remaining attribute.
        Assertions: Remaining equals 60.
        """
        # Action
        state = RateLimitState()

        # Assertions
        assert state.remaining == 60

    def test_default_reset_at_is_zero(self):
        """Verify reset_at initializes to 0.0.

        Setup: Instantiate RateLimitState with no arguments.
        Action: Read the reset_at attribute.
        Assertions: reset_at equals 0.0.
        """
        # Action
        state = RateLimitState()

        # Assertions
        assert state.reset_at == 0.0

    def test_default_used_is_zero(self):
        """Verify used counter initializes to 0.

        Setup: Instantiate RateLimitState with no arguments.
        Action: Read the used attribute.
        Assertions: used equals 0.
        """
        # Action
        state = RateLimitState()

        # Assertions
        assert state.used == 0


@pytest.mark.test_rate_limiting
class TestRateLimiterInit:
    """Unit tests for RateLimiter initialization."""

    def test_default_buffer_is_5(self):
        """Verify the default buffer threshold is 5.

        Setup: Instantiate RateLimiter with no arguments.
        Action: Read the buffer attribute.
        Assertions: Buffer equals RATE_LIMIT_BUFFER (5).
        """
        # Action
        limiter = RateLimiter()

        # Assertions
        assert limiter.buffer == RATE_LIMIT_BUFFER

    def test_custom_buffer(self):
        """Verify a custom buffer value is respected.

        Setup: Instantiate RateLimiter with buffer=10.
        Action: Read the buffer attribute.
        Assertions: Buffer equals 10.
        """
        # Action
        limiter = RateLimiter(buffer=10)

        # Assertions
        assert limiter.buffer == 10

    def test_initial_request_count_is_zero(self):
        """Verify total_requests starts at zero.

        Setup: Instantiate a fresh RateLimiter.
        Action: Read total_requests property.
        Assertions: total_requests equals 0.
        """
        # Action
        limiter = RateLimiter()

        # Assertions
        assert limiter.total_requests == 0


@pytest.mark.test_rate_limiting
class TestUpdateFromHeaders:
    """Unit tests for RateLimiter.update_from_headers."""

    def test_parses_remaining_header(self):
        """Verify X-RateLimit-Remaining is parsed correctly.

        Setup: Headers dict with X-RateLimit-Remaining=4999.
        Action: Call update_from_headers.
        Assertions: state.remaining equals 4999.
        """
        # Setup
        limiter = RateLimiter()
        headers = {HEADER_REMAINING: "4999"}

        # Action
        limiter.update_from_headers(headers)

        # Assertions
        assert limiter.state.remaining == 4999

    def test_parses_limit_header(self):
        """Verify X-RateLimit-Limit is parsed correctly.

        Setup: Headers dict with X-RateLimit-Limit=5000.
        Action: Call update_from_headers.
        Assertions: state.limit equals 5000.
        """
        # Setup
        limiter = RateLimiter()
        headers = {HEADER_LIMIT: "5000"}

        # Action
        limiter.update_from_headers(headers)

        # Assertions
        assert limiter.state.limit == 5000

    def test_parses_reset_header(self):
        """Verify X-RateLimit-Reset is parsed as a float timestamp.

        Setup: Headers dict with a Unix timestamp for X-RateLimit-Reset.
        Action: Call update_from_headers.
        Assertions: state.reset_at matches the expected float value.
        """
        # Setup
        limiter = RateLimiter()
        reset_ts = str(int(time.time()) + 3600)
        headers = {HEADER_RESET: reset_ts}

        # Action
        limiter.update_from_headers(headers)

        # Assertions
        assert limiter.state.reset_at == float(reset_ts)

    def test_parses_used_header(self):
        """Verify X-RateLimit-Used is parsed correctly.

        Setup: Headers dict with X-RateLimit-Used=50.
        Action: Call update_from_headers.
        Assertions: state.used equals 50.
        """
        # Setup
        limiter = RateLimiter()
        headers = {HEADER_USED: "50"}

        # Action
        limiter.update_from_headers(headers)

        # Assertions
        assert limiter.state.used == 50

    def test_parses_all_headers_together(self):
        """Verify all four rate-limit headers are parsed in a single call.

        Setup: Headers dict containing all four X-RateLimit-* fields.
        Action: Call update_from_headers.
        Assertions: All state fields match the header values.
        """
        # Setup
        limiter = RateLimiter()
        reset_ts = str(int(time.time()) + 3600)
        headers = {
            HEADER_REMAINING: "4950",
            HEADER_LIMIT: "5000",
            HEADER_RESET: reset_ts,
            HEADER_USED: "50",
        }

        # Action
        limiter.update_from_headers(headers)

        # Assertions
        assert limiter.state.remaining == 4950
        assert limiter.state.limit == 5000
        assert limiter.state.reset_at == float(reset_ts)
        assert limiter.state.used == 50

    def test_ignores_missing_headers(self):
        """Verify state is unchanged when headers dict is empty.

        Setup: Empty headers dict, default state.
        Action: Call update_from_headers with empty dict.
        Assertions: State remains at defaults.
        """
        # Setup
        limiter = RateLimiter()

        # Action
        limiter.update_from_headers({})

        # Assertions
        assert limiter.state.remaining == 60
        assert limiter.state.limit == 60

    def test_increments_request_count(self):
        """Verify _request_count increments on each update_from_headers call.

        Setup: A fresh RateLimiter.
        Action: Call update_from_headers three times.
        Assertions: total_requests equals 3.
        """
        # Setup
        limiter = RateLimiter()

        # Action
        limiter.update_from_headers({})
        limiter.update_from_headers({})
        limiter.update_from_headers({})

        # Assertions
        assert limiter.total_requests == 3


@pytest.mark.test_rate_limiting
class TestWaitIfNeeded:
    """Unit tests for RateLimiter.wait_if_needed."""

    def test_no_sleep_when_remaining_above_buffer(self):
        """Verify no sleep occurs when remaining quota is above the buffer.

        Setup: RateLimiter with remaining=100, buffer=5.
        Action: Call wait_if_needed.
        Assertions: time.sleep is never called.
        """
        # Setup
        limiter = RateLimiter(buffer=5)
        limiter.state.remaining = 100

        # Action / Assertions
        with patch("time.sleep") as mock_sleep:
            limiter.wait_if_needed()
            mock_sleep.assert_not_called()

    def test_no_sleep_when_remaining_equals_buffer_plus_one(self):
        """Verify no sleep when remaining is exactly one above buffer.

        Setup: RateLimiter with remaining=6, buffer=5.
        Action: Call wait_if_needed.
        Assertions: time.sleep is never called.
        """
        # Setup
        limiter = RateLimiter(buffer=5)
        limiter.state.remaining = 6

        # Action / Assertions
        with patch("time.sleep") as mock_sleep:
            limiter.wait_if_needed()
            mock_sleep.assert_not_called()

    def test_sleeps_when_remaining_equals_buffer(self):
        """Verify sleep occurs when remaining equals the buffer threshold.

        Setup: RateLimiter with remaining=5 (equals buffer=5), future reset_at.
        Action: Call wait_if_needed.
        Assertions: time.sleep is called with a positive duration.
        """
        # Setup
        limiter = RateLimiter(buffer=5)
        limiter.state.remaining = 5
        limiter.state.reset_at = time.time() + 60  # 60 seconds in the future

        # Action / Assertions
        with patch("time.sleep") as mock_sleep:
            limiter.wait_if_needed()
            mock_sleep.assert_called_once()
            sleep_duration = mock_sleep.call_args[0][0]
            assert sleep_duration > 0

    def test_sleeps_when_remaining_below_buffer(self):
        """Verify sleep occurs when remaining drops below the buffer.

        Setup: RateLimiter with remaining=2 (below buffer=5), future reset_at.
        Action: Call wait_if_needed.
        Assertions: time.sleep is called once with a positive duration.
        """
        # Setup
        limiter = RateLimiter(buffer=5)
        limiter.state.remaining = 2
        limiter.state.reset_at = time.time() + 30

        # Action / Assertions
        with patch("time.sleep") as mock_sleep:
            limiter.wait_if_needed()
            mock_sleep.assert_called_once()

    def test_sleep_duration_includes_one_second_padding(self):
        """Verify sleep duration adds 1 second of padding beyond the reset window.

        Setup: RateLimiter with remaining=0, reset_at 10 seconds from now.
        Action: Call wait_if_needed.
        Assertions: Sleep duration is approximately 11 seconds (10 + 1 padding).
        """
        # Setup
        limiter = RateLimiter(buffer=5)
        limiter.state.remaining = 0
        future_reset = time.time() + 10
        limiter.state.reset_at = future_reset

        # Action
        with patch("time.sleep") as mock_sleep:
            limiter.wait_if_needed()
            sleep_duration = mock_sleep.call_args[0][0]

        # Assertions -- allow 1 second of tolerance for execution time
        assert 10 <= sleep_duration <= 12
