"""Exceptions raised by the Clue API client."""

from __future__ import annotations


class ClueApiError(RuntimeError):
    """Base error for API and transport failures."""

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class AuthenticationError(ClueApiError):
    """Authentication failed or the access token is no longer valid."""


class ResourceNotFoundError(ClueApiError):
    """A resource or account-state-dependent endpoint is unavailable."""


class InvalidResponseError(ClueApiError):
    """The server returned a response the client could not interpret."""
