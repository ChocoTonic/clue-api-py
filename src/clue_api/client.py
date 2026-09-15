"""Synchronous, read-oriented client for the current Clue Android API."""

from __future__ import annotations

import os
from collections.abc import Mapping
from datetime import date
from pathlib import Path
from types import TracebackType
from typing import Self, cast
from urllib.parse import quote

import httpx

from ._version import __version__
from .errors import AuthenticationError, ClueApiError, InvalidResponseError, ResourceNotFoundError
from .types import DateLike, JsonObject, PainType, PredictionType


class ClueClient:
    """Access Clue data with a token issued to the account owner.

    This uses an undocumented API. Callers should expect endpoint and
    response changes. Public methods are read-only except ``from_credentials``,
    which creates an access token using Clue's login endpoint.
    """

    DEFAULT_BASE_URL = "https://api.helloclue.com"

    def __init__(
        self,
        access_token: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 20.0,
        time_zone: str | None = None,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        token = self._normalize_token(access_token)
        self._client = httpx.Client(
            base_url=base_url,
            headers={
                "Accept": "application/json",
                "Authorization": f"Token {token}",
                "Clue-Time-Zone": time_zone or self._local_time_zone(),
                "User-Agent": f"clue-api-py/{__version__}",
            },
            timeout=httpx.Timeout(timeout),
            transport=transport,
        )

    @classmethod
    def from_credentials(
        cls,
        email: str,
        password: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 20.0,
        time_zone: str | None = None,
        transport: httpx.BaseTransport | None = None,
    ) -> Self:
        """Log in with email/password and return an authenticated client.

        The endpoint and request fields are present in the current Android APK
        and match the historical public reverse-engineering notes. Passwords
        are used only for this request and are not retained by the client.
        """
        if not email.strip() or not password:
            raise ValueError("email and password are required")
        try:
            with httpx.Client(
                base_url=base_url,
                headers={
                    "Accept": "application/json",
                    "User-Agent": f"clue-api-py/{__version__}",
                },
                timeout=httpx.Timeout(timeout),
                transport=transport,
            ) as login_client:
                response = login_client.post(
                    "/access-tokens",
                    json={"email": email.strip(), "password": password},
                )
        except httpx.HTTPError as error:
            raise ClueApiError("Clue login request failed") from error
        cls._raise_for_status(response)
        payload = cls._json_object(response)
        token = payload.get("access_token")
        if not isinstance(token, str) or not token:
            raise InvalidResponseError("Clue login response did not include an access token")
        return cls(
            token,
            base_url=base_url,
            timeout=timeout,
            time_zone=time_zone,
            transport=transport,
        )

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()

    def __repr__(self) -> str:
        return f"{type(self).__name__}(access_token=<redacted>)"

    def close(self) -> None:
        self._client.close()

    def initialize(self) -> JsonObject:
        return self._get("/v1/initialize")

    def notifications(self) -> JsonObject:
        return self._get("/v1/notifications")

    def authentication_methods(self) -> JsonObject:
        return self._get("/v1/authentication-methods")

    def account(self) -> JsonObject:
        return self._get("/v1/user")

    def consents(self) -> JsonObject:
        return self._get("/v1/consents")

    def tracking_preferences(self) -> JsonObject:
        return self._get("/v1/tracking/preferences")

    def wearables(self) -> JsonObject:
        return self._get("/v1/wearables")

    def wearable(self, provider: str) -> JsonObject:
        return self._get(f"/v1/wearables/{self._path_segment(provider, 'provider')}")

    def birth_control_settings(self) -> JsonObject:
        return self._get("/v1/birth-control/settings")

    def birth_control_spec(self) -> JsonObject:
        return self._get("/v1/birth-control/spec")

    def connections(self) -> JsonObject:
        return self._get("/v1/connections")

    def connection_calendar(
        self,
        code: str,
        *,
        start: DateLike,
        end: DateLike,
    ) -> JsonObject:
        return self._get(
            f"/v1/calendar/connections/{self._path_segment(code, 'code')}",
            params=self._date_range_params(start, end, start_name="startDate", end_name="endDate"),
        )

    def community_profile(self) -> JsonObject:
        return self._get("/v1/community/me")

    def current_cycle(self, *, include_ovarian_phases: bool = True) -> JsonObject:
        return self._get(
            "/v1/cycles/current",
            params={"include-ovarian-phases": str(include_ovarian_phases).lower()},
        )

    def cycle_history(self, *, limit: int = 20, cursor: str | None = None) -> JsonObject:
        if limit < 1:
            raise ValueError("limit must be positive")
        return self._get(
            "/v1/cycles/history",
            params=self._pagination_params(limit=limit, cursor=cursor),
        )

    def cycle_settings(self) -> JsonObject:
        return self._get("/v1/cycles/settings")

    def cycle_analysis(self) -> JsonObject:
        return self._get("/v1/cycles/analysis")

    def cycle_analysis_diff(self) -> JsonObject:
        """Get analysis changes; this returned 404 for the observed account."""
        return self._get("/v1/cycles/analysis/diff")

    def feelings_analysis(self) -> JsonObject:
        return self._get("/v1/cycles/feelings-analysis")

    def pain_analysis(self, pain_type: PainType) -> JsonObject:
        return self._get(f"/v1/cycles/pain-analysis/{quote(pain_type, safe='')}")

    def symptom_predictions(self, prediction_type: PredictionType) -> JsonObject:
        """Get symptom predictions; availability depends on account state."""
        return self._get(f"/v1/cycles/symptom-predictions/{quote(prediction_type, safe='')}")

    def bbt_analysis(self) -> JsonObject:
        return self._get("/v1/analysis/bbt")

    def body_metrics(self) -> JsonObject:
        return self._get("/v1/analysis/body-metrics")

    def resting_heart_rate_analysis(self, *, source: str | None = None) -> JsonObject:
        return self._analysis_by_source("resting-heart-rate", source)

    def delta_temperature_analysis(self, *, source: str | None = None) -> JsonObject:
        return self._analysis_by_source("delta-temperature", source)

    def heart_rate_variability_analysis(self, *, source: str | None = None) -> JsonObject:
        return self._analysis_by_source("heart-rate-variability", source)

    def skin_temperature_analysis(self, *, source: str | None = None) -> JsonObject:
        return self._analysis_by_source("skin-temperature", source)

    def sleep_duration_analysis(self, *, source: str | None = None) -> JsonObject:
        return self._analysis_by_source("sleep-duration", source)

    def weight_analysis(
        self,
        *,
        limit: int = 20,
        cursor: str | None = None,
        source: str | None = None,
    ) -> JsonObject:
        if limit < 1:
            raise ValueError("limit must be positive")
        params = self._pagination_params(limit=limit, cursor=cursor)
        if source:
            params["source"] = source
        return self._get("/v1/analysis/weight", params=params)

    def measurements(
        self,
        *,
        start: DateLike,
        end: DateLike,
        measurement_type: str | None = None,
    ) -> JsonObject:
        params = self._date_range_params(start, end, start_name="start", end_name="end")
        if measurement_type:
            params["measurementType"] = measurement_type
        return self._get("/v1/measurements", params=params)

    def calendar(self, *, start: DateLike, end: DateLike) -> JsonObject:
        return self._get(
            "/v1/calendar",
            params=self._date_range_params(start, end, start_name="startDate", end_name="endDate"),
        )

    def pregnancy(self) -> JsonObject:
        """Get pregnancy data; non-pregnancy accounts normally receive 404."""
        return self._get("/v1/pregnancy")

    def medical_records(self) -> JsonObject:
        return self._get("/v1/medical-records")

    def doctor_reports(self) -> JsonObject:
        return self._get("/v1/doctor-reports")

    def doctor_report_user_details(self) -> JsonObject:
        return self._get("/v1/doctor-reports/user-details")

    def download_doctor_report(self, report_id: str) -> bytes:
        return self._get_bytes(
            f"/v1/doctor-reports/{self._path_segment(report_id, 'report_id')}/download"
        )

    def enrolled_studies(self) -> JsonObject:
        return self._get("/v1/study/enrolled")

    def study(self, study_id: str) -> JsonObject:
        return self._get(f"/v1/study/{self._path_segment(study_id, 'study_id')}")

    def takeout(self) -> JsonObject:
        """Return data-takeout credentials; treat the response as a secret."""
        return self._get("/v1/takeout")

    def chatbot_history(self) -> list[JsonObject]:
        return self._get_array("/v1/chatbot")

    def paywall(self, *, option: str | None = None) -> JsonObject:
        return self._get("/v1/paywall", params=self._optional_param("option", option))

    def user(self, user_id: str) -> JsonObject:
        return self._get(f"/users/{self._path_segment(user_id, 'user_id')}")

    def _get(
        self,
        path: str,
        *,
        params: Mapping[str, str | int] | None = None,
    ) -> JsonObject:
        return self._json_object(self._request_get(path, params=params))

    def _get_array(
        self,
        path: str,
        *,
        params: Mapping[str, str | int] | None = None,
    ) -> list[JsonObject]:
        response = self._request_get(path, params=params)
        try:
            payload = response.json()
        except ValueError as error:
            raise InvalidResponseError(
                "Clue returned invalid JSON",
                status_code=response.status_code,
            ) from error
        if not isinstance(payload, list) or not all(isinstance(item, dict) for item in payload):
            raise InvalidResponseError(
                "Clue returned JSON that was not an array of objects",
                status_code=response.status_code,
            )
        return cast(list[JsonObject], payload)

    def _get_bytes(self, path: str) -> bytes:
        return self._request_get(path).content

    def _request_get(
        self,
        path: str,
        *,
        params: Mapping[str, str | int] | None = None,
    ) -> httpx.Response:
        try:
            response = self._client.get(path, params=params)
        except httpx.HTTPError as error:
            raise ClueApiError(f"Clue request failed for GET {path}") from error
        self._raise_for_status(response)
        return response

    def _analysis_by_source(self, name: str, source: str | None) -> JsonObject:
        return self._get(
            f"/v1/analysis/{name}",
            params=self._optional_param("source", source),
        )

    @staticmethod
    def _raise_for_status(response: httpx.Response) -> None:
        if response.status_code in {401, 403}:
            raise AuthenticationError(
                "Clue rejected the credentials or access token",
                status_code=response.status_code,
            )
        if response.status_code == 404:
            raise ResourceNotFoundError(
                "Clue resource is unavailable for this account or identifier",
                status_code=response.status_code,
            )
        if response.is_error:
            raise ClueApiError(
                f"Clue returned HTTP {response.status_code}",
                status_code=response.status_code,
            )

    @staticmethod
    def _json_object(response: httpx.Response) -> JsonObject:
        try:
            payload = response.json()
        except ValueError as error:
            raise InvalidResponseError(
                "Clue returned invalid JSON",
                status_code=response.status_code,
            ) from error
        if not isinstance(payload, dict):
            raise InvalidResponseError(
                "Clue returned JSON that was not an object",
                status_code=response.status_code,
            )
        return payload

    @staticmethod
    def _normalize_token(access_token: str) -> str:
        token = access_token.strip()
        if token.lower().startswith("token "):
            token = token[6:].strip()
        if not token:
            raise ValueError("access_token is required")
        return token

    @staticmethod
    def _date_value(value: DateLike) -> str:
        if isinstance(value, date):
            return value.isoformat()
        date.fromisoformat(value)
        return value

    @classmethod
    def _date_range_params(
        cls,
        start: DateLike,
        end: DateLike,
        *,
        start_name: str,
        end_name: str,
    ) -> dict[str, str]:
        start_value = cls._date_value(start)
        end_value = cls._date_value(end)
        if start_value > end_value:
            raise ValueError("start must be on or before end")
        return {start_name: start_value, end_name: end_value}

    @staticmethod
    def _pagination_params(*, limit: int, cursor: str | None) -> dict[str, str | int]:
        params: dict[str, str | int] = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        return params

    @staticmethod
    def _optional_param(name: str, value: str | None) -> dict[str, str] | None:
        return {name: value} if value else None

    @staticmethod
    def _path_segment(value: str, name: str) -> str:
        if not value:
            raise ValueError(f"{name} is required")
        return quote(value, safe="")

    @staticmethod
    def _local_time_zone() -> str:
        if configured := os.environ.get("TZ"):
            return configured
        try:
            resolved = str(Path("/etc/localtime").resolve())
            marker = "zoneinfo/"
            if marker in resolved:
                return resolved.split(marker, 1)[1]
        except OSError:
            pass
        return "UTC"
