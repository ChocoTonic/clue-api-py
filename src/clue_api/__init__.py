"""Unofficial Python client for the Clue period tracker API."""

from ._version import __version__
from .client import ClueClient
from .contracts import READ_ENDPOINTS, build_openapi
from .errors import AuthenticationError, ClueApiError, InvalidResponseError, ResourceNotFoundError
from .types import CursorPage, JsonObject, PainType, PredictionType

__all__ = [
    "AuthenticationError",
    "ClueApiError",
    "ClueClient",
    "CursorPage",
    "InvalidResponseError",
    "JsonObject",
    "PainType",
    "PredictionType",
    "READ_ENDPOINTS",
    "ResourceNotFoundError",
    "__version__",
    "build_openapi",
]
