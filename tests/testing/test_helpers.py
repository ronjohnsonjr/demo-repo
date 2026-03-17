"""Unit tests for utils/testing/helpers.py.

Validates all shared test helper functions in isolation.
"""

import time
import unittest
import unittest.mock
from unittest.mock import MagicMock, patch

import pytest
import requests

from data.constants import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND, HTTP_429_RATE_LIMITED
from utils.testing.helpers import (
    assert_json_keys,
    assert_pagination_headers,
    assert_status_code,
    generate_unique_suffix,
    hash_response,
    retry_on_rate_limit,
)


@pytest.mark.test_testing
class TestGenerateUniqueSuffix:
    """Unit tests for generate_unique_suffix."""

    def test_returns_string(self):
        """Verify the function returns a string.

        Setup: No setup required.
        Action: Call generate_unique_suffix().
        Assertions: The result is a string of length 8.
        """
        # Setup
        # (none)

        # Action
        result = generate_unique_suffix()

        # Assertions
        assert isinstance(result, str)
        assert len(result) == 8

    def test_returns_unique_values(self):
        """Verify consecutive calls produce distinct values.

        Setup: No setup required.
        Action: Call generate_unique_suffix() twice.
        Assertions: Both values are different from each other.
        """
        # Action
        first = generate_unique_suffix()
        second = generate_unique_suffix()

        # Assertions
        assert first != second

    def test_returns_hex_characters(self):
        """Verify the suffix contains only hex characters.

        Setup: No setup required.
        Action: Call generate_unique_suffix().
        Assertions: All characters are valid hexadecimal digits.
        """
        # Action
        result = generate_unique_suffix()

        # Assertions
        assert all(c in "0123456789abcdef" for c in result)


@pytest.mark.test_testing
class TestAssertStatusCode:
    """Unit tests for assert_status_code."""

    def test_passes_when_codes_match(self):
        """Verify no assertion is raised when status code matches expected.

        Setup: A mock response with status_code=200.
        Action: Call assert_status_code with expected=200.
        Assertions: No exception is raised.
        """
        # Setup
        mock_response = MagicMock()
        mock_response.status_code = HTTP_200_OK
        mock_response.url = "https://api.github.com/test"
        mock_response.text = "{}"

        # Action / Assertions (no exception expected)
        assert_status_code(mock_response, HTTP_200_OK)

    def test_raises_on_mismatch(self):
        """Verify AssertionError is raised when status code does not match.

        Setup: A mock response with status_code=404.
        Action: Call assert_status_code with expected=200.
        Assertions: AssertionError is raised with informative message.
        """
        # Setup
        mock_response = MagicMock()
        mock_response.status_code = HTTP_404_NOT_FOUND
        mock_response.url = "https://api.github.com/repos/nonexistent/repo"
        mock_response.text = '{"message": "Not Found"}'

        # Action / Assertions
        with pytest.raises(AssertionError) as exc_info:
            assert_status_code(mock_response, HTTP_200_OK)

        assert "200" in str(exc_info.value)
        assert "404" in str(exc_info.value)

    def test_error_message_includes_url(self):
        """Verify the assertion message includes the request URL.

        Setup: A mock response with a specific URL.
        Action: Trigger an assertion error.
        Assertions: The URL appears in the error message.
        """
        # Setup
        mock_response = MagicMock()
        mock_response.status_code = HTTP_401_UNAUTHORIZED
        mock_response.url = "https://api.github.com/user"
        mock_response.text = '{"message": "Unauthorized"}'

        # Action / Assertions
        with pytest.raises(AssertionError) as exc_info:
            assert_status_code(mock_response, HTTP_200_OK)

        assert "https://api.github.com/user" in str(exc_info.value)


@pytest.mark.test_testing
class TestAssertJsonKeys:
    """Unit tests for assert_json_keys."""

    def test_passes_when_all_keys_present(self):
        """Verify no assertion when all required keys exist.

        Setup: A dict with keys a, b, c.
        Action: Assert that keys a, b are present.
        Assertions: No exception is raised.
        """
        # Setup
        data = {"id": 1, "name": "test", "url": "https://example.com"}

        # Action / Assertions (no exception expected)
        assert_json_keys(data, ["id", "name", "url"])

    def test_raises_when_key_missing(self):
        """Verify AssertionError when a required key is absent.

        Setup: A dict missing the 'email' key.
        Action: Assert that 'email' is required.
        Assertions: AssertionError lists the missing key.
        """
        # Setup
        data = {"id": 1, "name": "test"}

        # Action / Assertions
        with pytest.raises(AssertionError) as exc_info:
            assert_json_keys(data, ["id", "name", "email"])

        assert "email" in str(exc_info.value)

    def test_raises_with_multiple_missing_keys(self):
        """Verify error lists all missing keys when several are absent.

        Setup: A dict with only 'id'.
        Action: Require 'id', 'name', 'url'.
        Assertions: Both 'name' and 'url' appear in the error.
        """
        # Setup
        data = {"id": 1}

        # Action / Assertions
        with pytest.raises(AssertionError) as exc_info:
            assert_json_keys(data, ["id", "name", "url"])

        assert "name" in str(exc_info.value)
        assert "url" in str(exc_info.value)

    def test_passes_with_empty_required_list(self):
        """Verify empty required_keys list always passes.

        Setup: Any dict.
        Action: Assert no required keys.
        Assertions: No exception is raised.
        """
        # Action / Assertions (no exception expected)
        assert_json_keys({"id": 1}, [])


@pytest.mark.test_testing
class TestAssertPaginationHeaders:
    """Unit tests for assert_pagination_headers."""

    def test_passes_with_link_header(self):
        """Verify no exception when Link header is present.

        Setup: A headers dict containing the Link key.
        Action: Call assert_pagination_headers.
        Assertions: No exception is raised.
        """
        # Setup
        headers = {"Link": '<https://api.github.com/repos?page=2>; rel="next"'}

        # Action / Assertions (no exception expected)
        assert_pagination_headers(headers)

    def test_passes_without_link_header(self):
        """Verify no exception when Link header is absent (non-paginated response).

        Setup: A headers dict with no Link key.
        Action: Call assert_pagination_headers.
        Assertions: No exception is raised (the assert has an or-True guard).
        """
        # Setup
        headers = {"Content-Type": "application/json"}

        # Action / Assertions (no exception expected)
        assert_pagination_headers(headers)


@pytest.mark.test_testing
class TestHashResponse:
    """Unit tests for hash_response."""

    def test_returns_string(self):
        """Verify hash_response returns a hex string.

        Setup: A simple dict payload.
        Action: Call hash_response.
        Assertions: Result is a 64-character hex string (SHA-256).
        """
        # Setup
        data = {"id": 1, "name": "octocat"}

        # Action
        result = hash_response(data)

        # Assertions
        assert isinstance(result, str)
        assert len(result) == 64
        assert all(c in "0123456789abcdef" for c in result)

    def test_same_data_same_hash(self):
        """Verify identical data produces identical hash.

        Setup: Two identical dicts (same key order).
        Action: Hash both.
        Assertions: Both hashes are equal.
        """
        # Setup
        data1 = {"id": 1, "name": "octocat", "type": "User"}
        data2 = {"id": 1, "name": "octocat", "type": "User"}

        # Action
        hash1 = hash_response(data1)
        hash2 = hash_response(data2)

        # Assertions
        assert hash1 == hash2

    def test_different_data_different_hash(self):
        """Verify different data produces different hashes.

        Setup: Two dicts with different values.
        Action: Hash both.
        Assertions: Hashes differ.
        """
        # Setup
        data1 = {"id": 1, "name": "octocat"}
        data2 = {"id": 2, "name": "torvalds"}

        # Action
        hash1 = hash_response(data1)
        hash2 = hash_response(data2)

        # Assertions
        assert hash1 != hash2

    def test_key_order_does_not_affect_hash(self):
        """Verify key order does not affect the hash (sort_keys=True).

        Setup: Same dict with keys in different orders.
        Action: Hash both.
        Assertions: Hashes are equal.
        """
        # Setup
        data1 = {"name": "octocat", "id": 1}
        data2 = {"id": 1, "name": "octocat"}

        # Action
        hash1 = hash_response(data1)
        hash2 = hash_response(data2)

        # Assertions
        assert hash1 == hash2

    def test_works_with_list(self):
        """Verify hash_response handles list payloads.

        Setup: A list of dicts.
        Action: Call hash_response.
        Assertions: Returns a valid 64-character hash.
        """
        # Setup
        data = [{"id": 1}, {"id": 2}]

        # Action
        result = hash_response(data)

        # Assertions
        assert len(result) == 64


@pytest.mark.test_testing
class TestRetryOnRateLimit:
    """Unit tests for retry_on_rate_limit."""

    def test_returns_on_first_success(self):
        """Verify the result is returned immediately when the function succeeds.

        Setup: A mock function that returns 42.
        Action: Wrap it with retry_on_rate_limit.
        Assertions: Returns 42 and the function was called once.
        """
        # Setup
        mock_func = MagicMock(return_value=42)

        # Action
        result = retry_on_rate_limit(mock_func)

        # Assertions
        assert result == 42
        mock_func.assert_called_once()

    def test_retries_on_403(self):
        """Verify the wrapper retries after a 403 HTTPError.

        Setup: A mock function that raises 403 once then returns 'ok'.
        Action: Call retry_on_rate_limit with max_retries=2.
        Assertions: Final result is 'ok' and function was called twice.
        """
        # Setup
        mock_response = MagicMock()
        mock_response.status_code = 403

        error = requests.exceptions.HTTPError(response=mock_response)
        mock_func = MagicMock(side_effect=[error, "ok"])

        # Action
        with patch("time.sleep"):
            result = retry_on_rate_limit(mock_func, max_retries=2)

        # Assertions
        assert result == "ok"
        assert mock_func.call_count == 2

    def test_retries_on_429(self):
        """Verify the wrapper retries after a 429 HTTPError.

        Setup: A mock function that raises 429 once then returns 'ok'.
        Action: Call retry_on_rate_limit with max_retries=2.
        Assertions: Final result is 'ok'.
        """
        # Setup
        mock_response = MagicMock()
        mock_response.status_code = 429

        error = requests.exceptions.HTTPError(response=mock_response)
        mock_func = MagicMock(side_effect=[error, "ok"])

        # Action
        with patch("time.sleep"):
            result = retry_on_rate_limit(mock_func, max_retries=2)

        # Assertions
        assert result == "ok"

    def test_raises_non_rate_limit_errors(self):
        """Verify non-rate-limit HTTPErrors are re-raised immediately.

        Setup: A function that raises a 404 HTTPError.
        Action: Call retry_on_rate_limit.
        Assertions: The 404 error propagates without retry.
        """
        # Setup
        mock_response = MagicMock()
        mock_response.status_code = HTTP_404_NOT_FOUND

        error = requests.exceptions.HTTPError(response=mock_response)
        mock_func = MagicMock(side_effect=error)

        # Action / Assertions
        with pytest.raises(requests.exceptions.HTTPError):
            retry_on_rate_limit(mock_func, max_retries=3)

        mock_func.assert_called_once()

    def test_passes_args_and_kwargs(self):
        """Verify positional and keyword arguments are forwarded to the function.

        Setup: A mock function that captures its arguments.
        Action: Call retry_on_rate_limit with args and kwargs.
        Assertions: The underlying function received the correct arguments.
        """
        # Setup
        mock_func = MagicMock(return_value="result")

        # Action
        result = retry_on_rate_limit(mock_func, "arg1", key="val")

        # Assertions
        mock_func.assert_called_once_with("arg1", key="val")
        assert result == "result"

    def test_final_attempt_after_exhausted_retries(self):
        """Verify the function is called one final time after all retries are rate-limited.

        Setup: A mock that raises 429 exactly max_retries times, then returns 'final'.
        Action: Call retry_on_rate_limit with max_retries=2.
        Assertions: Returns 'final' and function is called max_retries+1 times total.
        """
        # Setup
        mock_response = MagicMock()
        mock_response.status_code = HTTP_429_RATE_LIMITED

        error_429 = requests.exceptions.HTTPError(response=mock_response)
        # Raises 429 twice (exhaust the loop), then returns on the final call
        mock_func = MagicMock(side_effect=[error_429, error_429, "final"])

        # Action
        with patch("time.sleep"):
            result = retry_on_rate_limit(mock_func, max_retries=2)

        # Assertions -- line 56 (final return) is executed
        assert result == "final"
        assert mock_func.call_count == 3  # 2 retries in loop + 1 final call
