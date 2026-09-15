"""Public typing helpers for Clue's evolving API."""

from __future__ import annotations

from datetime import date
from typing import Any, Literal, TypedDict

JsonObject = dict[str, Any]
DateLike = date | str

Evidence = Literal["live", "state-dependent", "apk-only"]
PainType = Literal[
    "period_cramps",
    "lower_back",
    "breast_tenderness",
    "headache",
    "migraine",
    "migraine_with_aura",
    "leg",
    "joint",
    "vulvar",
]
PredictionType = Literal[
    "cramps",
    "headache",
    "lower_back",
    "breast_tenderness",
    "migraine",
    "migraine_with_aura",
    "leg",
    "joint",
    "vulvar",
]


class CursorPage(TypedDict, total=False):
    """Common shape used by current paginated endpoints."""

    nextCursor: str | None
