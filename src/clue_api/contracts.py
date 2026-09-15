"""Evidence-backed endpoint inventory and OpenAPI document builder."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from ._version import __version__
from .types import Evidence

ParameterLocation = Literal["path", "query", "header"]
ResponseKind = Literal["object", "array", "binary"]


@dataclass(frozen=True, slots=True)
class Parameter:
    name: str
    location: ParameterLocation = "query"
    required: bool = False
    schema: str = "string"
    enum: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class EndpointContract:
    path: str
    operation_id: str
    summary: str
    evidence: Evidence
    response_fields: tuple[str, ...] = ()
    parameters: tuple[Parameter, ...] = ()
    response_kind: ResponseKind = "object"


P = Parameter
PAIN_TYPES = (
    "period_cramps",
    "lower_back",
    "breast_tenderness",
    "headache",
    "migraine",
    "migraine_with_aura",
    "leg",
    "joint",
    "vulvar",
)
PREDICTION_TYPES = (
    "cramps",
    "headache",
    "lower_back",
    "breast_tenderness",
    "migraine",
    "migraine_with_aura",
    "leg",
    "joint",
    "vulvar",
)

READ_ENDPOINTS: tuple[EndpointContract, ...] = (
    EndpointContract(
        "/v1/initialize",
        "initialize",
        "Get account bootstrap state",
        "live",
        ("actions", "consent", "consent_v2", "features", "productTier", "subscription", "user"),
    ),
    EndpointContract(
        "/v1/authentication-methods",
        "getAuthenticationMethods",
        "Get enabled authentication methods",
        "live",
        ("authentication",),
    ),
    EndpointContract(
        "/v1/user",
        "getCurrentUser",
        "Get the current user",
        "live",
        ("analyticsId", "email", "emailVerified", "firstName", "lastName", "mode"),
    ),
    EndpointContract(
        "/users/{user_id}",
        "getUserById",
        "Get the current user's legacy user envelope",
        "live",
        ("user",),
        (P("user_id", "path", True),),
    ),
    EndpointContract(
        "/v1/consents",
        "getConsents",
        "Get consent settings",
        "live",
        ("consents", "opt_out_types"),
    ),
    EndpointContract(
        "/v1/notifications",
        "getNotifications",
        "Get notification settings",
        "live",
    ),
    EndpointContract(
        "/v1/tracking/preferences",
        "getTrackingPreferences",
        "Get tracking preferences",
        "live",
        ("tags",),
    ),
    EndpointContract(
        "/v1/birth-control/settings",
        "getBirthControlSettings",
        "Get birth-control settings",
        "live",
        ("settings",),
    ),
    EndpointContract(
        "/v1/birth-control/spec",
        "getBirthControlSpec",
        "Get birth-control option metadata",
        "live",
        ("typeOptions",),
    ),
    EndpointContract(
        "/v1/wearables",
        "getWearables",
        "List wearable integrations",
        "live",
        ("wearables",),
    ),
    EndpointContract(
        "/v1/wearables/{provider}",
        "getWearable",
        "Get a wearable integration",
        "live",
        ("connection_status", "integration_provider", "provider", "supported_measurement_types"),
        (P("provider", "path", True),),
    ),
    EndpointContract(
        "/v1/connections",
        "getConnections",
        "List sharing connections",
        "live",
        ("connections",),
    ),
    EndpointContract(
        "/v1/calendar/connections/{code}",
        "getConnectionCalendar",
        "Get a shared calendar by connection code",
        "apk-only",
        parameters=(
            P("code", "path", True),
            P("startDate", required=True, schema="date"),
            P("endDate", required=True, schema="date"),
        ),
    ),
    EndpointContract(
        "/v1/community/me",
        "getCommunityProfile",
        "Get the community profile",
        "live",
        ("id", "nickname", "picture_url"),
    ),
    EndpointContract(
        "/v1/cycles/current",
        "getCurrentCycle",
        "Get the current cycle",
        "live",
        (
            "analysis",
            "availablePredictions",
            "birthControlMethod",
            "cycle",
            "dailyCategoryGroups",
            "periodConfirmation",
        ),
        (P("include-ovarian-phases", schema="boolean"),),
    ),
    EndpointContract(
        "/v1/cycles/history",
        "getCycleHistory",
        "Get paginated cycle history",
        "live",
        ("cycles", "nextCursor"),
        (P("limit", schema="integer"), P("cursor")),
    ),
    EndpointContract(
        "/v1/cycles/settings",
        "getCycleSettings",
        "Get cycle prediction settings",
        "live",
        (
            "cycleLengthSettings",
            "fertilePhaseEnabled",
            "ovulationPhaseEnabled",
            "periodLengthSettings",
        ),
    ),
    EndpointContract(
        "/v1/cycles/analysis",
        "getCycleAnalysis",
        "Get cycle analysis",
        "live",
        (
            "cycleLength",
            "cycleLengthDetails",
            "cycleVariation",
            "cycleVariationDetails",
            "lastCycleLength",
            "pastCycleLengths",
            "periodLength",
            "periodStats",
        ),
    ),
    EndpointContract(
        "/v1/cycles/analysis/diff",
        "getCycleAnalysisDiff",
        "Get cycle-analysis changes",
        "state-dependent",
    ),
    EndpointContract(
        "/v1/cycles/feelings-analysis",
        "getFeelingsAnalysis",
        "Get cycle feelings analysis",
        "live",
        ("correlations", "feelingsHeatMap", "ovarianFeelings"),
    ),
    EndpointContract(
        "/v1/cycles/pain-analysis/{pain_type}",
        "getPainAnalysis",
        "Get analysis for a pain type",
        "live",
        ("painHistory", "painStatistics"),
        (P("pain_type", "path", True, enum=PAIN_TYPES),),
    ),
    EndpointContract(
        "/v1/cycles/symptom-predictions/{prediction_type}",
        "getSymptomPredictions",
        "Get symptom predictions",
        "state-dependent",
        parameters=(P("prediction_type", "path", True, enum=PREDICTION_TYPES),),
    ),
    EndpointContract(
        "/v1/analysis/bbt",
        "getBbtAnalysis",
        "Get basal-body-temperature analysis",
        "live",
        ("cycles", "nextCursor"),
    ),
    EndpointContract(
        "/v1/analysis/body-metrics",
        "getBodyMetrics",
        "Get body metrics",
        "live",
        ("bmi", "height", "weightMeasurement"),
    ),
    EndpointContract(
        "/v1/analysis/resting-heart-rate",
        "getRestingHeartRateAnalysis",
        "Get resting-heart-rate analysis",
        "live",
        ("cycles", "nextCursor"),
        (P("source"),),
    ),
    EndpointContract(
        "/v1/analysis/delta-temperature",
        "getDeltaTemperatureAnalysis",
        "Get delta-temperature analysis",
        "live",
        ("cycles", "nextCursor"),
        (P("source"),),
    ),
    EndpointContract(
        "/v1/analysis/heart-rate-variability",
        "getHeartRateVariabilityAnalysis",
        "Get heart-rate-variability analysis",
        "live",
        ("cycles", "nextCursor"),
        (P("source"),),
    ),
    EndpointContract(
        "/v1/analysis/skin-temperature",
        "getSkinTemperatureAnalysis",
        "Get skin-temperature analysis",
        "live",
        ("cycles", "nextCursor"),
        (P("source"),),
    ),
    EndpointContract(
        "/v1/analysis/sleep-duration",
        "getSleepDurationAnalysis",
        "Get sleep-duration analysis",
        "live",
        ("cycles", "nextCursor"),
        (P("source"),),
    ),
    EndpointContract(
        "/v1/analysis/weight",
        "getWeightAnalysis",
        "Get paginated weight analysis",
        "live",
        ("cycles", "nextCursor"),
        (P("limit", schema="integer"), P("cursor"), P("source")),
    ),
    EndpointContract(
        "/v1/measurements",
        "getMeasurements",
        "Get measurements in a date range",
        "live",
        ("measurements", "nextCursor"),
        (
            P("start", required=True, schema="date"),
            P("end", required=True, schema="date"),
            P("measurementType"),
        ),
    ),
    EndpointContract(
        "/v1/calendar",
        "getCalendar",
        "Get calendar days in a date range",
        "live",
        ("days", "maxCalendarDate", "periodConfirmation"),
        (P("startDate", required=True, schema="date"), P("endDate", required=True, schema="date")),
    ),
    EndpointContract(
        "/v1/pregnancy",
        "getPregnancy",
        "Get current pregnancy data",
        "state-dependent",
    ),
    EndpointContract(
        "/v1/medical-records",
        "getMedicalRecords",
        "Get medical-record options",
        "live",
        ("options", "version"),
    ),
    EndpointContract(
        "/v1/doctor-reports",
        "getDoctorReports",
        "List doctor reports and eligibility",
        "live",
        ("doctorReports", "eligibility"),
    ),
    EndpointContract(
        "/v1/doctor-reports/user-details",
        "getDoctorReportUserDetails",
        "Get user details used in doctor reports",
        "live",
        ("age", "birthControl", "healthConditions", "medication", "name"),
    ),
    EndpointContract(
        "/v1/doctor-reports/{report_id}/download",
        "downloadDoctorReport",
        "Download a doctor report",
        "apk-only",
        parameters=(P("report_id", "path", True),),
        response_kind="binary",
    ),
    EndpointContract(
        "/v1/study/enrolled",
        "getEnrolledStudies",
        "List enrolled studies",
        "live",
        ("enrolledStudies",),
    ),
    EndpointContract(
        "/v1/study/{study_id}",
        "getStudy",
        "Get a study",
        "apk-only",
        parameters=(P("study_id", "path", True),),
    ),
    EndpointContract(
        "/v1/takeout",
        "getTakeout",
        "Get data-takeout credentials",
        "live",
        ("email", "expiresAt", "password", "userId"),
    ),
    EndpointContract(
        "/v1/chatbot",
        "getChatbotHistory",
        "Get chatbot history",
        "live",
        response_kind="array",
    ),
    EndpointContract(
        "/v1/paywall",
        "getPaywall",
        "Get products and entitlement state",
        "live",
        ("availableProducts", "entitlements", "productTier", "products"),
        (P("option"),),
    ),
)


def build_openapi() -> dict[str, Any]:
    """Build the deterministic OpenAPI 3.1 contract shipped with the project."""
    paths: dict[str, Any] = {
        "/access-tokens": {
            "post": {
                "operationId": "createAccessToken",
                "summary": "Log in with email and password",
                "x-clue-evidence": {
                    "level": "apk-only",
                    "androidAppVersion": "269.1",
                    "historicalDocumentation": True,
                },
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/LoginRequest"}
                        }
                    },
                },
                "responses": {
                    "201": {
                        "description": "Access token created",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/LoginResponse"}
                            }
                        },
                    },
                    "401": {"$ref": "#/components/responses/AuthenticationError"},
                },
            }
        }
    }
    for endpoint in READ_ENDPOINTS:
        evidence: dict[str, Any] = {
            "level": endpoint.evidence,
            "androidAppVersion": "269.1",
        }
        if endpoint.evidence == "live":
            evidence.update({"observedStatus": 200, "observedOn": "2026-09-15"})
        operation: dict[str, Any] = {
            "operationId": endpoint.operation_id,
            "summary": endpoint.summary,
            "security": [{"tokenAuth": []}],
            "x-clue-evidence": evidence,
            "responses": {
                "200": {
                    "description": "Successful response",
                    "content": _response_content(endpoint),
                },
                "401": {"$ref": "#/components/responses/AuthenticationError"},
                "404": {"$ref": "#/components/responses/NotFoundError"},
            },
        }
        if endpoint.parameters:
            operation["parameters"] = [
                _parameter_schema(parameter) for parameter in endpoint.parameters
            ]
        paths[endpoint.path] = {"get": operation}
    return {
        "openapi": "3.1.0",
        "info": {
            "title": "Unofficial Clue Period Tracker API",
            "version": __version__,
            "description": (
                "Evidence-backed contract for the undocumented Clue API. "
                "The x-clue-evidence extension distinguishes live observations "
                "from state-dependent and APK-only declarations."
            ),
        },
        "servers": [{"url": "https://api.helloclue.com"}],
        "paths": paths,
        "components": {
            "securitySchemes": {
                "tokenAuth": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "Authorization",
                    "description": "Prefix the access token with `Token `.",
                }
            },
            "schemas": {
                "LoginRequest": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["email", "password"],
                    "properties": {
                        "email": {"type": "string", "format": "email"},
                        "password": {"type": "string", "format": "password", "writeOnly": True},
                    },
                },
                "LoginResponse": {
                    "type": "object",
                    "required": ["access_token", "user"],
                    "properties": {
                        "access_token": {"type": "string", "readOnly": True},
                        "analytics_id": {"type": "string"},
                        "user": {"type": "object", "additionalProperties": True},
                    },
                    "additionalProperties": True,
                },
                "Error": {
                    "type": "object",
                    "properties": {
                        "error": {"type": "string"},
                        "path": {"type": "string"},
                        "status": {"type": "integer"},
                        "timestamp": {"type": "string"},
                    },
                    "additionalProperties": True,
                },
            },
            "responses": {
                "AuthenticationError": {
                    "description": "Credentials or token rejected",
                    "content": {
                        "application/json": {"schema": {"$ref": "#/components/schemas/Error"}}
                    },
                },
                "NotFoundError": {
                    "description": "Resource or state-dependent endpoint unavailable",
                    "content": {
                        "application/json": {"schema": {"$ref": "#/components/schemas/Error"}}
                    },
                },
            },
        },
    }


def _parameter_schema(parameter: Parameter) -> dict[str, Any]:
    schema: dict[str, Any]
    if parameter.schema == "date":
        schema = {"type": "string", "format": "date"}
    else:
        schema = {"type": parameter.schema}
    if parameter.enum:
        schema["enum"] = list(parameter.enum)
    return {
        "name": parameter.name,
        "in": parameter.location,
        "required": parameter.required or parameter.location == "path",
        "schema": schema,
    }


def _response_content(endpoint: EndpointContract) -> dict[str, Any]:
    if endpoint.response_kind == "binary":
        return {"application/pdf": {"schema": {"type": "string", "format": "binary"}}}
    if endpoint.response_kind == "array":
        schema: dict[str, Any] = {"type": "array", "items": {}}
    else:
        schema = {
            "type": "object",
            "properties": {field: {} for field in endpoint.response_fields},
            "additionalProperties": True,
        }
    return {"application/json": {"schema": schema}}
