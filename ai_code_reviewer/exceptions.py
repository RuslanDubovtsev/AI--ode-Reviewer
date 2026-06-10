"""
Custom exceptions for the AI Code Reviewer.
Allows callers to handle errors gracefully instead of sys.exit().
"""

from typing import Any, Dict, Optional


class ConfigError(Exception):
    """Raised when configuration (API key, etc.) is missing or invalid."""
    pass


class FileReadError(Exception):
    """Raised when a file cannot be read or is invalid."""
    pass


class FileTooLargeError(FileReadError):
    """Raised when the file exceeds the maximum allowed size."""
    pass


class ApiError(Exception):
    """Raised when the AI API returns an error or is unreachable."""
    pass


class ApiTimeoutError(ApiError):
    """Raised when the API request times out."""
    pass


class ApiConnectionError(ApiError):
    """Raised when a network connection to the API cannot be established."""
    pass


class ApiResponseError(ApiError):
    """
    Raised when the API returns an unexpected or invalid response.

    Attributes:
        raw_response: The parsed JSON response body, if available.
        raw_text: The raw text response body, if available.
    """

    def __init__(
        self,
        message: str,
        raw_response: Optional[Dict[str, Any]] = None,
        raw_text: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.raw_response = raw_response
        self.raw_text = raw_text


class CliUsageError(Exception):
    """Raised when CLI arguments are invalid."""
    pass
