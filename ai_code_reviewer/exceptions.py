"""
Custom exceptions for the AI Code Reviewer.
Allows callers to handle errors gracefully instead of sys.exit().
"""


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
    """Raised when the API returns an unexpected or invalid response."""
    pass


class CliUsageError(Exception):
    """Raised when CLI arguments are invalid."""
    pass
