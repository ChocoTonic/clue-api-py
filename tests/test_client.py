from __future__ import annotations

import httpx
import pytest

from clue_api import AuthenticationError, ClueClient, InvalidResponseError, ResourceNotFoundError


def test_initialize_uses_token_scheme_and_current_path() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/v1/initialize"
        assert request.headers["authorization"] == "Token secret"
        assert request.headers["clue-time-zone"] == "America/Los_Angeles"
        return httpx.Response(200, json={"user": {}})

    with ClueClient(
        "Token secret",
        time_zone="America/Los_Angeles",
        transport=httpx.MockTransport(handler),
    ) as client:
        assert client.initialize() == {"user": {}}


def test_cycle_history_serializes_pagination() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert dict(request.url.params) == {"limit": "10", "cursor": "next-page"}
        return httpx.Response(200, json={"cycles": [], "nextCursor": None})

    with ClueClient("secret", transport=httpx.MockTransport(handler)) as client:
        client.cycle_history(limit=10, cursor="next-page")


def test_measurements_uses_observed_query_names() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert dict(request.url.params) == {
            "start": "2026-01-01",
            "end": "2026-01-31",
            "measurementType": "period",
        }
        return httpx.Response(200, json={"measurements": [], "nextCursor": None})

    with ClueClient("secret", transport=httpx.MockTransport(handler)) as client:
        client.measurements(
            start="2026-01-01",
            end="2026-01-31",
            measurement_type="period",
        )


def test_login_matches_current_apk_contract() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/access-tokens"
        assert request.read() == b'{"email":"person@example.com","password":"password"}'
        return httpx.Response(201, json={"access_token": "issued-token", "user": {}})

    with ClueClient.from_credentials(
        "person@example.com",
        "password",
        transport=httpx.MockTransport(handler),
    ) as client:
        assert "issued-token" not in repr(client)


def test_authentication_error_does_not_include_response_body() -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(401, json={"error": "sensitive server detail"})
    )
    with (
        ClueClient("expired", transport=transport) as client,
        pytest.raises(AuthenticationError, match="rejected") as caught,
    ):
        client.initialize()
    assert "sensitive" not in str(caught.value)


def test_invalid_json_is_wrapped() -> None:
    transport = httpx.MockTransport(lambda request: httpx.Response(200, text="not-json"))
    with (
        ClueClient("secret", transport=transport) as client,
        pytest.raises(InvalidResponseError, match="invalid JSON"),
    ):
        client.initialize()


def test_not_found_has_a_specific_safe_error() -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(404, json={"error": "private detail"})
    )
    with (
        ClueClient("secret", transport=transport) as client,
        pytest.raises(ResourceNotFoundError, match="unavailable") as caught,
    ):
        client.pregnancy()
    assert "private detail" not in str(caught.value)
