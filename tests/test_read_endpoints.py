from __future__ import annotations

import httpx
import pytest

from clue_api import ClueClient


def test_read_only_surface_routes_to_observed_paths() -> None:
    seen: list[tuple[str, str]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        raw_path = request.url.raw_path.decode().split("?", 1)[0]
        seen.append((request.method, raw_path))
        if request.url.path == "/v1/chatbot":
            return httpx.Response(200, json=[])
        if request.url.path.endswith("/download"):
            return httpx.Response(200, content=b"pdf")
        return httpx.Response(200, json={})

    with ClueClient("secret", transport=httpx.MockTransport(handler)) as client:
        client.initialize()
        client.authentication_methods()
        client.account()
        client.user("user/id")
        client.consents()
        client.notifications()
        client.tracking_preferences()
        client.birth_control_settings()
        client.birth_control_spec()
        client.wearables()
        client.wearable("fitbit")
        client.connections()
        client.connection_calendar("share/code", start="2026-01-01", end="2026-01-02")
        client.community_profile()
        client.current_cycle()
        client.cycle_history()
        client.cycle_settings()
        client.cycle_analysis()
        client.cycle_analysis_diff()
        client.feelings_analysis()
        client.pain_analysis("period_cramps")
        client.symptom_predictions("cramps")
        client.bbt_analysis()
        client.body_metrics()
        client.resting_heart_rate_analysis()
        client.delta_temperature_analysis()
        client.heart_rate_variability_analysis()
        client.skin_temperature_analysis()
        client.sleep_duration_analysis()
        client.weight_analysis()
        client.measurements(start="2026-01-01", end="2026-01-02")
        client.calendar(start="2026-01-01", end="2026-01-02")
        client.pregnancy()
        client.medical_records()
        client.doctor_reports()
        client.doctor_report_user_details()
        assert client.download_doctor_report("report/id") == b"pdf"
        client.enrolled_studies()
        client.study("study/id")
        client.takeout()
        client.chatbot_history()
        client.paywall()

    assert all(method == "GET" for method, _ in seen)
    assert ("GET", "/users/user%2Fid") in seen
    assert ("GET", "/v1/calendar/connections/share%2Fcode") in seen
    assert ("GET", "/v1/doctor-reports/report%2Fid/download") in seen


def test_date_ranges_are_validated_before_request() -> None:
    transport = httpx.MockTransport(lambda request: httpx.Response(200, json={}))
    with (
        ClueClient("secret", transport=transport) as client,
        pytest.raises(ValueError, match="start must be"),
    ):
        client.measurements(start="2026-02-01", end="2026-01-01")


def test_invalid_date_is_rejected_before_request() -> None:
    transport = httpx.MockTransport(lambda request: httpx.Response(200, json={}))
    with (
        ClueClient("secret", transport=transport) as client,
        pytest.raises(ValueError),
    ):
        client.calendar(start="not-a-date", end="2026-01-01")
